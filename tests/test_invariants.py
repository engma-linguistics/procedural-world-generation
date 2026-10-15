"""Things that must hold whatever the tuning: determinism, bookkeeping,
physically sane values, storage that doesn't clip, module interfaces."""

import numpy as np
import pytest

from planet import climate, store as S, timeline as T, zoom
from planet.grid import build_grid
from planet.surface import ROCKS
from planet.tectonics import MAX_KM, Params, Simulation

from helpers import continental_volume, run_sim


def test_deterministic(sim4_60):
    """Same seed and params -> identical history (runs are stored as a cache;
    slicing replays from t=0 and relies on this)."""
    a, b = sim4_60, run_sim(myr=60)
    for k in ("w_elev", "w_thick", "w_cover", "w_age", "owner", "precip", "temp"):
        assert np.array_equal(getattr(a, k), getattr(b, k)), k
    assert [e.as_dict() for e in a.events] == [e.as_dict() for e in b.events]


def test_seed_changes_world():
    a, b = run_sim(myr=20), run_sim(myr=20, seed=2)
    assert not np.array_equal(a.w_elev, b.w_elev)


def test_crust_budget_closes():
    """Every change in continental crust volume is booked to a process in
    Simulation.budget; unbooked changes mean a leak (or a silent source)."""
    sim = Simulation(build_grid(4), 3, Params(), 2.0)
    v0 = continental_volume(sim)
    sim.run(120)
    booked = sum(sim.budget.values())
    change = continental_volume(sim) - v0
    assert abs(change - booked) < 0.01 * v0, (change, booked, sim.budget)


def test_values_sane(sim4):
    s = sim4
    land = s.w_elev > 0
    for k in ("w_elev", "w_thick", "w_cover", "w_age", "precip", "temp", "t_warm", "t_cold", "ice"):
        assert np.isfinite(getattr(s, k)).all(), k
    assert -12000 < s.w_elev.min() and s.w_elev.max() < 10000
    assert s.w_thick.min() >= 1.0 and s.w_thick.max() <= MAX_KM
    assert (s.w_cover >= 0).all() and (s.w_cover <= s.w_thick + 1e-9).all()
    assert (s.precip >= 0).all() and s.precip.max() < 10000
    assert -95 < s.t_cold.min() and s.t_warm.max() < 60
    assert (s.t_warm >= s.temp - 1e-6).all() and (s.t_cold <= s.temp + 1e-6).all()
    assert (s.w_rock < len(ROCKS)).all()
    snap = s.snapshot()
    assert (snap.koppen[land] != climate.SEA_CLASS).all()
    assert (snap.koppen[~land] == climate.SEA_CLASS).all()


def test_layers_round_trip(sim4):
    """What a run stores reads back without silent clipping for values the
    model actually produces (sediment cover once clipped at 25.5 km)."""
    snap = sim4.snapshot()
    big = {"sediment_cover": 60.0, "crust_thickness": MAX_KM, "precipitation": 9000, "ice": 3000,
           "elevation": -12000, "flow": 5000.0}
    for k, v in big.items():
        spec = S.LAYERS[k]
        back = S.decode(S.encode(np.array([v]), spec), spec)[0]
        assert abs(back - v) <= max(spec["scale"], 0.05 * v if spec["transform"] else 0), k
    vecs = T.vec_layers(sim4.grid, "wind", snap.wind) + T.vec_layers(sim4.grid, "jet", T.jet_of(sim4.grid, snap))
    for name, arr in vecs:
        assert np.abs(S.encode(arr, S.LAYERS[name])).max() < 127, name  # not saturating the int8


def test_climate_compute_interface(grid4):
    g = grid4
    rng = np.random.default_rng(0)
    elev = np.where(rng.random(g.n) < 0.3, rng.uniform(0, 3000, g.n), -3000.0)
    c = climate.compute(g, elev, dT=0.0, tilt=23.4)
    for k in ("temp", "t_warm", "t_cold", "precip", "p_jul", "p_jan", "koppen", "sst"):
        assert c[k].shape == (g.n,), k
        assert np.isfinite(c[k]).all(), k
    for k in ("wind_jul", "wind_jan", "current", "jet_jul", "jet_jan"):
        assert c[k].shape == (g.n, 3), k
        assert np.isfinite(c[k]).all(), k
    # global mean rain is anchored (see TUNE['mean_mm'])
    assert 700 < c["precip"].mean() < 1300


def test_climate_same_on_any_thread_count(grid4):
    """The parallel climate kernels add up in a fixed order, so the
    results are bit-identical whatever the number of threads."""
    numba = pytest.importorskip("numba")
    g = grid4
    rng = np.random.default_rng(1)
    elev = np.where(rng.random(g.n) < 0.3, rng.uniform(0, 3000, g.n), -3000.0)
    before = numba.get_num_threads()
    try:
        numba.set_num_threads(1)
        one = climate.compute(g, elev)
        numba.set_num_threads(min(3, numba.config.NUMBA_NUM_THREADS))
        many = climate.compute(g, elev)
    finally:
        numba.set_num_threads(before)
    def same(a, b):
        if isinstance(a, dict):
            return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
        if isinstance(a, list):
            return a == b
        return np.array_equal(a, b)

    for k in one:
        assert same(one[k], many[k]), k


def test_coarse_smooth_matches_fine():
    """A wide blur is done on a coarser grid (climate.smooth); it should
    match the all-fine-grid blur to well under 1% of the blurred field's
    spread, and its gradient (what the winds follow) to a few %: no lattice
    of the coarse cells in it (PW-211)."""
    g = build_grid(6)
    rng = np.random.default_rng(0)
    f = np.sin(3 * np.radians(g.lat)) + np.cos(2 * np.radians(g.lon)) + rng.standard_normal(g.n)
    G = climate._geom(g)
    for km in (600.0, 900.0, 2000.0):
        fine = climate._smooth(f, g.nbr_off, g.nbr_idx, G["sk"], int(round(4 * (km / G["h"]) ** 2)))
        coarse = climate.smooth(g, f, km)
        assert np.sqrt(((coarse - fine) ** 2).mean()) < 0.01 * fine.std(), km
        gf, gc = climate.gradient(g, fine), climate.gradient(g, coarse)
        assert np.sqrt(((gc - gf) ** 2).sum(1).mean() / (gf**2).sum(1).mean()) < 0.04, km


def test_no_icosphere_seams():
    """The icosphere's cells are up to ~9% larger or smaller along the
    seams of the icosahedron it was built from. The gradient of a smooth
    field, a blur of it, and the rain's transport in a wind blowing the same
    way everywhere must not show them (they made straight lines in the
    winds and rain; PW-211)."""
    g = build_grid(6)
    G = climate._geom(g)
    a = np.array([0.3, -0.5, 0.8])
    f = (g.centers @ a) ** 2 * 30
    rough = []  # the gradient's small-scale wiggle, relative to its size (the field's own curvature at 0 km)
    for km in (0.0, 250.0, 900.0):
        s = climate.smooth(g, f, km) if km else f
        gm = np.linalg.norm(climate.gradient(g, s), axis=1)
        rough.append((gm - climate._smooth(gm, g.nbr_off, g.nbr_idx, G["sk"], 30)).std() / gm.mean())
    assert max(rough[1:]) < 1.3 * rough[0], rough  # (a plain neighbour average: ~3x)
    w = climate.inflow_weights(g, G["east"] + 0.5 * G["north"])
    inflow = np.bincount(G["dst"][G["in_e"]], w, g.n)
    # (near the equator this wind blows nearly the same way everywhere; further poleward east and north
    # turn, a real convergence; the plain shares of the outflow are up to ~25% off)
    assert np.abs(inflow - 1)[np.abs(g.lat) < 30].max() < 0.02


def test_gyres_and_jet():
    """One ocean between two coasts (a pole-to-pole continent 60 deg wide):
    the subtropical gyre's return flow runs poleward in a narrow fast
    current along the ocean's western side and drifts slowly equatorward
    across the rest (western intensification). The jet aloft blows from the
    west in mid-latitudes, tens of m/s, strongest in the winter hemisphere."""
    g = build_grid(5)
    elev = np.where(np.abs(g.lon) < 30, 300.0, -4000.0)
    c = climate.compute(g, elev)
    G = climate._geom(g)
    vn = (c["current"] * G["north"]).sum(1)
    sub = (g.lat > 18) & (g.lat < 35) & (elev <= 0)
    west = sub & (g.lon > 30) & (g.lon < 40)  # just off the continent's east coast
    inner = sub & (np.abs(g.lon) > 60) & (np.abs(g.lon) < 160)
    assert vn[west].mean() > 0 > vn[inner].mean()
    assert vn[west].mean() > 4 * abs(vn[inner].mean())
    for k, winter in (("jet_jan", g.lat > 0), ("jet_jul", g.lat < 0)):
        ue = (c[k] * G["east"]).sum(1)
        mid = (np.abs(g.lat) > 30) & (np.abs(g.lat) < 55)
        assert ue[mid].mean() > 5, k
        assert 15 < ue[mid & winter].mean() < 80, k


def test_climate_responds_to_dT(grid4):
    g = grid4
    elev = np.where(np.abs(g.lat) < 40, 200.0, -3000.0)
    cold, warm = climate.compute(g, elev, dT=-5), climate.compute(g, elev, dT=5)
    assert warm["temp"].mean() > cold["temp"].mean() + 5
    assert warm["precip"].mean() > cold["precip"].mean()


def test_world_and_zoom(sim4):
    """sim -> full world in memory -> regional zoom, without touching disk."""
    w = T.world_from_sim(sim4)
    L = w["layers"]
    for k in ("elevation", "precipitation", "biome", "rock", "climate", "flow", "downstream"):
        assert len(L[k]) == sim4.grid.n, k
    land = np.flatnonzero(np.asarray(L["elevation"]) > 200)
    i = land[len(land) // 2]
    lat, lon = float(sim4.grid.lat[i]), float(sim4.grid.lon[i])
    z = zoom.build(w, lat, lon, size_km=400, res_km=8, iterations=3, log=lambda *a: None)
    e = z["layers"]["elevation"]
    assert np.isfinite(e).all() and e.max() > 0


def test_params_from_old_run():
    """run.json from older code: removed params are dropped (with a warning),
    missing ones take today's defaults."""
    stored = {"n_plates": 9, "some_removed_param": 1.0}
    with pytest.warns(UserWarning, match="some_removed_param"):
        p = Params.from_stored(stored)
    assert p.n_plates == 9 and p.tilt == Params().tilt


def test_simulate_slice_provenance(data_root):
    """simulate stamps the code into run.json; slicing at a keyframe must
    reproduce it, and refuses to save a world when it doesn't (unless forced).
    Runs without the stamp (older runs) still slice."""
    import json
    out = T.simulate(1, 4, 8.0, 2.0, 4.0, "t", Params())
    run = json.loads((out / "run.json").read_text())
    assert run["meta"]["code"]["planet_src_sha"]
    world = json.loads(T.slice_world(out, 8.0).read_text())
    assert world["meta"]["replay_matches_keyframe"] is True

    # an older run: no code stamp, plus a param this code no longer has
    del run["meta"]["code"]
    run["meta"]["params"]["long_gone_param"] = 1
    (out / "run.json").write_text(json.dumps(run))
    with pytest.warns(UserWarning):
        T.slice_world(out, 4.0)

    # the stored keyframe no longer matches what the code computes
    spec = run["layers"]["elevation"]
    elev = np.memmap(out / spec["file"], spec["dtype"], "r+", shape=tuple(spec["shape"]))
    elev[-1] += 1
    elev.flush()
    del elev
    with pytest.warns(UserWarning), pytest.raises(T.ReplayMismatch):
        T.slice_world(out, 8.0)
    with pytest.warns(UserWarning):
        world = json.loads(T.slice_world(out, 8.0, force=True).read_text())
    assert world["meta"]["replay_matches_keyframe"] is False


def test_climate_fits_ground_after_events():
    """The climate is computed after the step's events (sutures, slivers,
    rifts), so at every climate step the Koppen sea class agrees with the
    ground the step leaves (PW-109). Cells within 200 m of the sea are
    skipped: land ice moves the sea a little after the climate is computed."""
    sim = Simulation(build_grid(4), 5, Params(), 2.0)
    bad = []

    def check(s):
        if s.climate_t == s.t:
            sure = np.abs(s.w_elev) > 200
            sea = s.koppen == climate.SEA_CLASS
            bad.extend((s.t, int(i)) for i in np.flatnonzero(sure & (sea != (s.w_elev <= 0))))

    sim.run(300, on_step=check)
    assert not bad, bad[:10]
