"""Waves, tides and delta types (planet/coast.py, and the deltas in
planet/zoom.py) on small synthetic worlds."""

import numpy as np
import pytest

from planet import coast, zoom
from planet.geo import R_KM, xyz
from planet.grid import build_grid

from test_zoom_water import _dist_km, water_world  # noqa: F401  (fixture)


def _cell(g, lat, lon):
    return int(np.argmax(g.centers @ xyz(np.radians(lat), np.radians(lon))))


def _coastal(g, elev, lat, lon):
    """The sea cell touching land nearest to (lat, lon)."""
    sea = elev <= 0
    src = np.repeat(np.arange(g.n), np.diff(g.nbr_off))
    touch = sea & (np.bincount(src, ~sea[g.nbr_idx], g.n) > 0)
    d = np.where(touch, -(g.centers @ xyz(np.radians(lat), np.radians(lon))), np.inf)
    return int(np.argmin(d))


def _east(g):
    e = np.cross([0.0, 0.0, 1.0], g.centers)
    return e / np.linalg.norm(e, axis=1, keepdims=True)


@pytest.fixture(scope="module")
def g5():
    return build_grid(5)


def test_wave_fetch_exposed_vs_sheltered(g5, monkeypatch):
    """A steady westerly over an ocean with a continent in it: its west
    coast faces thousands of km of open water upwind and gets big waves; a
    narrow bay opening to the north (across the wind) and the lee (east)
    coast get little. (Long storms, so fetch, not duration, limits the sea.)"""
    monkeypatch.setattr(coast, "T_STORM", 72.0)
    g = g5
    lat, lon = g.lat, g.lon
    land = (lon > 0) & (lon < 60) & (np.abs(lat) < 50)
    bay = (lon > 26.5) & (lon < 29.5) & (lat > 10) & (lat < 50)  # a long narrow bay, open to the north
    elev = np.where(land & ~bay, 300.0, -4000.0)
    assert elev[_cell(g, 25, 28)] < 0
    U = np.full((2, g.n), 12.0)
    D = np.repeat(_east(g)[None], 2, 0)  # blowing toward the east
    wp = coast.wave_power_winds(g, elev, U, D, np.zeros((2, g.n), bool))
    assert np.all(wp[elev > 0] == 0)
    exposed = wp[_coastal(g, elev, 20, -1)]
    sheltered = wp[_coastal(g, elev, 25, 28)]
    lee = wp[_coastal(g, elev, 20, 61)]
    assert exposed > 20, exposed
    assert sheltered < 0.3 * exposed, (sheltered, exposed)
    assert lee < 0.3 * exposed, (lee, exposed)
    # the open ocean far from land: a fully developed sea for the wind, roughly
    assert 0.3 * coast._wsat(12.0) < wp[_cell(g, 0, -120)] < 1.5 * coast._wsat(12.0)


def test_wave_frozen_sea_blocks(g5):
    """Sea ice upwind stops the waves like land."""
    g = g5
    elev = np.where((g.lon > 0) & (g.lon < 60) & (np.abs(g.lat) < 50), 300.0, -4000.0)
    U, D = np.full((2, g.n), 12.0), np.repeat(_east(g)[None], 2, 0)
    open_ = coast.wave_power_winds(g, elev, U, D, np.zeros((2, g.n), bool))
    i = _coastal(g, elev, 20, -1)
    icy = np.repeat(((g.lon < g.lon[i] - 1.0) & (elev <= 0))[None], 2, 0)  # frozen beyond the coastal cell
    frozen = coast.wave_power_winds(g, elev, U, D, icy)
    assert frozen[i] < 0.5 * open_[i]


@pytest.fixture(scope="module")
def tide_world(g5):
    """A continent in a deep ocean. Its west coast has a wide, shallow shelf
    (80 m deep, ~330 km wide) south of the equator and drops straight to the
    deep sea north of it; inside it lies an enclosed sea (~1300 km across)
    joined to the ocean by a one-cell, shallow strait."""
    g = g5
    lat, lon = g.lat, g.lon
    land = (lon > 0) & (lon < 70) & (np.abs(lat) < 55)
    elev = np.where(land, 300.0, -4000.0)
    shelf = (lon > -3.5) & (lon <= 0) & (lat < -5) & (lat > -50)
    elev = np.where(shelf, -80.0, elev)
    inland = _dist_km(g, 20.0, 40.0) < 650
    elev = np.where(inland, -1500.0, elev)
    # the strait: a line of cells from the sea's east end to the open ocean at lon 70
    for lo in np.arange(46, 72, 1.0):
        elev[_cell(g, 20.0, lo)] = -30.0
    return g, elev


def test_tide_wide_shelf_vs_narrow(tide_world):
    g, elev = tide_world
    tr, det = coast.tide_range(g, elev, detail=True)
    assert np.all(tr[elev > 0] == 0)
    iw, iN = _coastal(g, elev, -25, -1), _coastal(g, elev, 25, -1)
    wide, narrow = tr[iw], tr[iN]
    assert det["shelf_km"][iw] > 150
    assert wide > 1.5 * narrow, (wide, narrow)
    assert 0.5 < narrow < 3.0  # an open-ocean coast: ~1-2 m


def test_tide_enclosed_sea_is_small(tide_world):
    g, elev = tide_world
    tr = coast.tide_range(g, elev)
    enclosed = tr[_coastal(g, elev, 20, 34)]
    open_coast = tr[_coastal(g, elev, 25, -1)]
    assert enclosed < 0.3 * open_coast, (enclosed, open_coast)
    # cut off entirely, a sea that size raises only a tiny tide of its own
    shut = elev.copy()
    for lo in np.arange(46, 72, 1.0):
        shut[_cell(g, 20.0, lo)] = 300.0
    shut[(_dist_km(g, 20.0, 40.0) >= 650) & (shut < 0) & (g.lon > 0) & (g.lon < 70) & (np.abs(g.lat) < 55)] = 300.0
    assert coast.tide_range(g, shut)[_coastal(g, shut, 20, 34)] < 0.15


def test_galloway_weights():
    big_river = coast.galloway(20000.0, 15000.0, 1.0, 0.3, 200.0)
    assert big_river["type"] == "river-dominated"
    assert coast.galloway(500.0, 3000.0, 60.0, 0.3, 100.0)["type"] == "wave-dominated"
    assert coast.galloway(2000.0, 3000.0, 1.0, 6.0, 100.0)["type"] == "tide-dominated"
    w = coast.galloway(3000.0, 5000.0, 20.0, 2.0, 120.0)["weights"]
    assert abs(sum(w.values()) - 1) < 1e-2
    hs, te = coast.hs_te(50.0)  # P = 0.49 Hs^2 Te
    assert abs(0.49 * hs * hs * te - 50.0) < 2.0


# ---------------------------------------------------------------------------
# Deltas in the zoom: the same river into three different seas
# ---------------------------------------------------------------------------
SEAS = {"river": (0.5, 0.2), "wave": (60.0, 0.3), "tide": (1.0, 8.0)}  # wave kW/m, tide m


@pytest.fixture(scope="module")
def three_deltas(water_world):  # noqa: F811
    g, L = water_world["grid"], water_world["layers"]
    down, flow, elev = L["downstream"], L["flow"], L["elevation"]
    mouths = np.flatnonzero((elev > 0) & (down >= 0))
    mouths = mouths[elev[down[mouths]] <= 0]
    i = mouths[np.argmax(flow[mouths])]
    p = g.centers[i] + g.centers[down[i]]
    lat, lon = np.degrees(np.arcsin(p[2] / np.linalg.norm(p))), np.degrees(np.arctan2(p[1], p[0]))
    out = {}
    for name, (wave, tide) in SEAS.items():
        Lw = {**L, "wave_power": np.where(elev > 0, 0.0, wave), "tide_range": np.where(elev > 0, 0.0, tide)}
        out[name] = zoom.build({**water_world, "layers": Lw}, float(lat), float(lon), size_km=300, res_km=2,
                               iterations=8, log=lambda *a: None)
    return out


def _measures(z):
    """Within the delta plain (radius R) of the zoom's main delta: coast
    length per R (roughness), how far land reaches seaward beyond the coast
    at the mouth (protrusion, in R), and the sea's share in a band just
    inside the coast vs further inland (channels widening seaward)."""
    d = z["stats"]["deltas"][0]
    n, res = z["nx"], z["res"]
    xs = (np.arange(n) + 0.5 - n / 2) * res
    X, Y = np.meshgrid(xs, -xs)
    dx, dy = X - d["mouth_km"][0], Y - d["mouth_km"][1]
    R = d["plain_radius_km"]
    u = np.array(d["seaward"])
    a, b = dx * u[0] + dy * u[1], dx * -u[1] + dy * u[0]
    land = z["layers"]["water"] != 1
    sea = ~land
    coast = land & zoom._dilate(sea, 1)
    disc = np.hypot(dx, dy) < R
    rough = coast[disc].sum() * res / R
    beam = np.abs(b) < 0.7 * R
    reach = a[land & beam].max() / R
    # the coast at the mouth: the median seaward reach of land across the beam
    cols = [a[land & beam & (np.abs(b - c) < res)].max() for c in np.arange(-0.6 * R, 0.6 * R, 2 * res)
            if (land & beam & (np.abs(b - c) < res)).any()]
    s0 = float(np.median(cols))
    near = beam & (a > s0 - 0.15 * R) & (a < s0 - 0.02 * R)
    inland = beam & (a > s0 - 0.45 * R) & (a < s0 - 0.3 * R)
    return {"rough": rough, "reach": reach - s0 / R, "sea_near": sea[near].mean(), "sea_inland": sea[inland].mean(),
            "mouths": d["mouths"], "type": d["type"], "weights": d["weights"]}


def test_delta_types_differ(three_deltas):
    m = {k: _measures(z) for k, z in three_deltas.items()}
    for k in SEAS:
        assert m[k]["type"] == f"{k}-dominated", (k, m[k])
    # river: land reaches furthest out to sea (the bird's foot)
    assert m["river"]["reach"] > m["wave"]["reach"] + 0.1, m
    assert m["river"]["reach"] > m["tide"]["reach"] + 0.1, m
    # waves: the smoothest coast, and one or two mouths
    assert m["wave"]["rough"] < m["river"]["rough"], m
    assert m["wave"]["rough"] < m["tide"]["rough"], m
    assert m["wave"]["mouths"] <= 2, m
    # tides: the most ragged coast, sea channels cut into the plain that
    # widen seaward
    assert m["tide"]["rough"] > 1.3 * m["wave"]["rough"], m
    assert m["tide"]["sea_near"] > 0.15, m
    assert m["tide"]["sea_near"] > 1.5 * m["tide"]["sea_inland"], m
    assert m["tide"]["mouths"] >= 3 and m["tide"]["mouths"] >= m["wave"]["mouths"] + 2, m


def test_delta_tidal_flats(three_deltas):
    """Tide-dominated: a band of sea floor above low tide offshore (tidal flats)."""
    def flats(z):
        Lr = z["layers"]
        return ((Lr["water"] == 1) & (Lr["elevation"] > -0.5 * Lr["tide_range"]) & (Lr["tide_range"] > 0.8)).sum()
    assert flats(three_deltas["tide"]) > 50
    assert flats(three_deltas["river"]) == 0  # (a 0.2 m tide)


def test_sea_ice_share():
    # a warm sea, a sea frozen all year, and an Arctic one open ~3 months in its (northern) summer
    from types import SimpleNamespace
    g = SimpleNamespace(lat=np.array([10.0, 80.0, 72.0, 72.0]))
    c = {"t_warm": np.array([28.0, -10.0, 8.0, 8.0]), "t_cold": np.array([20.0, -40.0, -30.0, -30.0])}
    elev = np.array([-100.0, -100.0, -100.0, 50.0])
    s = coast.sea_ice_share(g, elev, c)
    assert s[:, 0].max() == 0 and s[:, 1].min() == 1 and s[:, 3].max() == 0  # land: 0
    assert 0.3 < s[0, 2] < 0.7 and s[1, 2] == 1  # July half partly open, January frozen
    assert 0.6 < s[:, 2].mean() < 0.85  # ~3-4 months open a year
