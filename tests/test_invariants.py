"""Things that must hold whatever the tuning: determinism, bookkeeping,
physically sane values, storage that doesn't clip, module interfaces."""

import numpy as np
import pytest

from planet import climate, timeline as T, world as W, zoom
from planet.grid import build_grid
from planet.surface import ROCKS
from planet.tectonics import MAX_KM, Params, Simulation

from conftest import continental_volume, run_sim


def test_deterministic():
    """Same seed and params -> identical history (runs are stored as a cache;
    slicing replays from t=0 and relies on this)."""
    a, b = run_sim(myr=60), run_sim(myr=60)
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
    big = {"cover": 60.0 * 10, "thickness": MAX_KM, "precip": 9000, "ice": 3000 / 20}
    for k, v in big.items():
        info = np.iinfo(np.dtype(T.LAYERS[k]))
        assert info.max >= v, k
    assert np.iinfo(np.dtype(T.LAYERS["elevation"])).min <= -12000
    for name, arr in T.vec_layers(sim4.grid, "wind", snap.wind):
        assert np.abs(arr).max() < 127, name  # not saturating the int8
    for name, arr in T.vec_layers(sim4.grid, "jet", T.jet_of(sim4.grid, snap), 1.0):
        assert np.abs(arr).max() < 127, name


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
    e = z["elevation"] if "elevation" in z else z["layers"]["elevation"]
    assert np.isfinite(e).all() and e.max() > 0
