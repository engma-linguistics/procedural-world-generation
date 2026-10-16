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
    # (PW-226, PW-276: an ice sheet's surface rises from the bed at its edge, so a cap on a high range is thin)
    assert -95 < s.t_cold.min() and s.t_warm.max() < 60
    assert (s.t_warm >= s.temp - 1e-6).all() and (s.t_cold <= s.temp + 1e-6).all()
    assert (s.w_rock < len(ROCKS)).all()
    snap = s.snapshot()
    land = s.land()  # (frames' land: the bed under an ice load can be below the sea, PW-309)
    assert (snap.koppen[land] != climate.SEA_CLASS).all()
    assert (snap.koppen[~land] == climate.SEA_CLASS).all()


def test_ice_surface_rises_from_the_edge(sim4):
    """PW-276: a sheet's (Nye) surface rises from the bed at its edge, so
    raising the bed inside a sheet thins the ice there (it doesn't lift the
    surface by the bed's rise): over ground 3 km higher the ice is at most
    a margin's, or what stood above it before."""
    from planet.tectonics import earth
    from planet.tectonics.isostasy import land_view
    s, g = sim4, sim4.grid
    e, ice0, _ = land_view(s.w_elev - s.ice_sink, np.where(s.w_elev > 0, s.ice, 0.0))
    land = e > 0
    c = climate.compute(g, e, s.dT - 12.0, s.params.tilt, np.where(land, ice0, 0.0))  # (colder: bigger sheets)
    a = earth.ice_sheets(s, land, e, c["ground"], ice0)
    iced = a > 0
    inner = iced & (np.add.reduceat(~iced[g.nbr_idx], g.nbr_off[:-1]) == 0)
    margin = 1.15 * earth.ICE_EDGE_M
    assert inner.sum() >= 3 and (a[inner] > margin).any()
    b = earth.ice_sheets(s, land, e + 3000.0 * inner, c["ground"], ice0)
    assert np.array_equal(b > 0, iced)  # (the extent doesn't depend on the bed's height here)
    assert (b <= a + 1e-6).all()
    # (where ICE_MAX capped the first sheet, its thickness wasn't set by the margins, so the
    # raised bed can keep more than a - 3000 of what the margins allow)
    free = inner & (a < earth.ICE_MAX - 1e-6)
    assert free.sum() >= 3
    assert (b[free] <= np.maximum(a[free] - 3000.0, margin) + 1e-6).all()


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


def test_vegetation_feedbacks_nudge():
    """The vegetation's feedbacks on the climate are nudges (PW-203): a
    forested continent recycles more rain than a bare one, (through Budyko's w,
    which stays within Fu's range), and the albedo moves each half-year by at
    most albedo_cap."""
    from planet import vegetation
    g = build_grid(4)
    elev = np.where(np.abs(g.lon) < 60, 300.0, -4000.0)
    land = elev > 0
    n = g.n
    forest = dict(woody=np.ones(n), deep=np.ones(n), lai=np.full(n, 6.0), albedo=np.full(n, 0.11),
                  mask=np.full(n, 0.75))
    bare = vegetation.bare(n)
    T = climate.TUNE
    for v in (forest, bare):
        f = climate.vegetation_feedbacks(land, v, T)
        assert np.all((f["w"] >= 1.5) & (f["w"] <= 4.0))
    cf, cb = climate.compute(g, elev, veg=forest), climate.compute(g, elev, veg=bare)
    assert cf["precip"][land].mean() > cb["precip"][land].mean()
    assert cf["aet"][land].sum() > cb["aet"][land].sum()  # forests give more back to the air
    c0 = climate.compute(g, elev)
    d = climate.albedo_warming(g.lat, 23.4, c0["temp"], c0["t_warm"], c0["t_cold"], c0["p_jul"], c0["p_jan"], bare, T)
    assert max(np.abs(d[0]).max(), np.abs(d[1]).max()) <= T["albedo_cap"] + 1e-9


def test_sediment_budget_closes(monkeypatch):
    """surface.erode moves rock, it doesn't make or lose it: each step's
    deposits (land, lakes, sea) add up to what it removed, and none is
    negative (PW-283). And a closed basin keeps only what fits: no cell
    where rivers end is filled above the basin's spill point (PW-280)."""
    from planet import kernels, surface
    steps, real = [], surface.erode

    def wrapped(grid, elev, *a, **kw):
        out = real(grid, elev, *a, **kw)
        spill = kernels.priority_flood(elev.astype(float), grid.nbr_off, grid.nbr_idx, 0.01)[0]
        top = elev + out[4] * a[-1]  # (a[-1]: iso_dep, m per km deposited)
        steps.append((out[3].copy(), out[4].copy(), out[7]["sink"] & (top > spill + 1.0), out[7]["sink"].sum()))
        return out

    monkeypatch.setattr(surface, "erode", wrapped)
    run_sim(myr=100)
    assert len(steps) >= 40
    assert sum(s[3] for s in steps) > 50  # (closed basins to test)
    for removed, dep, over, _ in steps:
        assert removed.sum() > 0
        assert dep.sum() == pytest.approx(removed.sum(), rel=1e-9)
        assert dep.min() >= -1e-12
        assert not over.any()


def test_hillslope_wear_level_consistent():
    """The run's hillslope term is a slope law, so the same terrain wears
    down the same at any grid level (PW-282: drop / spacing^2 doubled per level)."""
    from planet import surface
    from planet.geo import R_KM
    rng = np.random.default_rng(3)
    waves = [(v / np.linalg.norm(v), rng.uniform(0, 2 * np.pi), rng.uniform(1500, 4000))
             for v in rng.normal(size=(12, 3))]
    wear = []
    for level in (4, 5):
        g = build_grid(level)
        h = sum(np.sin(g.centers @ v * R_KM * 2 * np.pi / lam + ph) for v, ph, lam in waves) / np.sqrt(12)
        e = np.where(h > 0.3, 300 + 2500 * (h - 0.3), -3000.0)
        n, land = g.n, e > 0
        out = surface.erode(g, e, np.full(n, 35.0), np.zeros(n), np.zeros((n, len(surface.MIX_ROCKS))),
                            np.full(n, surface.CRATON, np.uint8), land, np.full(n, 800.0), np.full(n, 300.0),
                            np.full(n, 500.0), np.full(n, 1000.0), 2.0, Params().hillslope, 1e30, 2000.0, 0.0,
                            2.0 ** (level - 4), np.full(n, 170.0))
        wear.append(out[3][land].mean())
    assert wear[1] == pytest.approx(wear[0], rel=0.15), wear


def test_kernel_budyko_matches_and_stays_finite():
    """The rain kernel's scalar Budyko (PW-266) is water_balance's, and stays
    finite for a trace of rain under a big potential evaporation."""
    for p, pet, w in [(800.0, 400.0, 2.6), (300.0, 1500.0, 1.5), (50.0, 2000.0, 4.0), (2000.0, 100.0, 2.6)]:
        assert climate._budyko1(p, pet, w) == pytest.approx(float(climate.budyko(np.array(p), np.array(pet), w)),
                                                             rel=1e-9)
    for p in (1e-300, 5e-324, 1e-12, 0.0):
        e = climate._budyko1(p, 2000.0, 2.6)
        assert np.isfinite(e) and 0.0 <= e <= p
