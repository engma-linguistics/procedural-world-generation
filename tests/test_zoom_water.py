"""Zoom lakes and deltas on a small synthetic world: a domed continent with
a basin that fills into an open lake, and radial rivers to the sea."""

import numpy as np
import pytest

from planet import hydrology, zoom
from planet.geo import R_KM, latlon, xyz
from planet.grid import build_grid

LAKE_AT = (5.0, 8.0)  # lat, lon of the basin


def _dist_km(g, lat, lon):
    c = xyz(np.radians(lat), np.radians(lon))
    return np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM


@pytest.fixture(scope="module")
def water_world():
    g = build_grid(5)
    d0 = _dist_km(g, 0.0, 0.0)
    elev = np.where(d0 < 2500, 60 + 0.3 * (2500 - d0), -3000.0)
    elev = elev - np.where(d0 < 2300, 500 * np.exp(-(_dist_km(g, *LAKE_AT) / 500) ** 2), 0)
    precip = np.full(g.n, 1200.0)
    # wet enough that the basin overflows: an open lake
    c = {"runoff": 0.5 * precip, "aet": 0.5 * precip, "lake_evap": np.full(g.n, 300.0)}
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c)
    lake = lk["wet"]
    land = elev > 0
    layers = {
        "elevation": np.round(elev), "precipitation": precip, "temperature": np.full(g.n, 22.0),
        "warm_month": np.full(g.n, 26.0), "flow": flow, "downstream": down, "lake": lake.astype(int),
        "lake_level": np.maximum(np.round(lk["level"]), np.round(elev)), "lake_kind": lk["kind"].astype(int),
        "runoff": c["runoff"],
        "rock": np.zeros(g.n, int), "surface_rock": np.zeros(g.n, int), "climate": np.full(g.n, 2),
        "ice": np.zeros(g.n), "sediment_cover": np.where(land, 0.5, 6.0),
    }
    assert lake.sum() >= 3, "the synthetic basin should hold a coarse lake"
    return {"grid": g, "layers": layers, "meta": {"level": 5}}


@pytest.fixture(scope="module")
def lake_zoom(water_world):
    return zoom.build(water_world, *LAKE_AT, size_km=1600, res_km=8, iterations=6, log=lambda *a: None)


def test_lake_passes_its_water_on(lake_zoom):
    lk = lake_zoom["stats"]["largest_lakes"][0]
    assert lk["outlet"] is not None
    assert lk["inflow_m3s"] > 0
    assert lk["inflow_m3s"] <= lk["outflow_m3s"] < 1.1 * lk["inflow_m3s"]


def test_lake_rim_holds_the_water(lake_zoom):
    Lr = lake_zoom["layers"]
    water, h = Lr["water"], Lr["elevation"].astype(float)
    surf = np.where(water == 2, h + Lr["lake_depth"], -np.inf)
    level = np.full(surf.shape, -np.inf)  # highest lake surface next to each pixel
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            level = np.maximum(level, zoom._shift(surf, dr, dc, -np.inf))
    low = (water == 0) & np.isfinite(level) & (h < level - 0.01)
    edge = np.zeros_like(low)
    edge[[0, -1], :] = edge[:, [0, -1]] = True
    orow, ocol = lake_zoom["stats"]["largest_lakes"][0]["outlet"]
    rr, cc = np.nonzero(low & ~edge)
    # only the outlet channel may sit below the water
    assert np.all(np.maximum(np.abs(rr - orow), np.abs(cc - ocol)) <= 2), list(zip(rr, cc))


def test_lake_depth_varies(lake_zoom):
    d = lake_zoom["layers"]["lake_depth"][lake_zoom["layers"]["water"] == 2]
    assert len(d) > 50
    assert d.std() > 0.25 * d.mean()
    assert d.max() > 1.5 * np.median(d)


def test_delta_plain_and_distributaries(water_world):
    g, L = water_world["grid"], water_world["layers"]
    down, flow, elev = L["downstream"], L["flow"], L["elevation"]
    mouths = np.flatnonzero((elev > 0) & (down >= 0))
    mouths = mouths[elev[down[mouths]] <= 0]
    i = mouths[np.argmax(flow[mouths])]
    p = g.centers[i] + g.centers[down[i]]
    lat, lon = np.degrees(np.arcsin(p[2] / np.linalg.norm(p))), np.degrees(np.arctan2(p[1], p[0]))
    z = zoom.build(water_world, float(lat), float(lon), size_km=1600, res_km=8, iterations=6, log=lambda *a: None)
    dl = z["stats"]["deltas"][0]
    assert dl["discharge_m3s"] >= zoom.DELTA_MIN_Q
    n = z["nx"]
    xs = (np.arange(n) + 0.5 - n / 2) * z["res"]
    X, Y = np.meshgrid(xs, -xs)
    near = (np.hypot(X - dl["mouth_km"][0], Y - dl["mouth_km"][1]) < 0.4 * dl["plain_radius_km"])
    land = near & (z["layers"]["water"] == 0)
    assert land.sum() > 10
    assert np.median(z["layers"]["elevation"][land]) < 10
    # distributaries: the river reaches the sea through several channels
    water, q = z["layers"]["water"], z["layers"]["discharge"]
    coast = (water == 0) & zoom._dilate(water == 1, 1)
    near = np.hypot(X - dl["mouth_km"][0], Y - dl["mouth_km"][1]) < dl["plain_radius_km"]
    assert z["stats"]["distributary_splits"] >= 1
    assert (coast & near & (q > 0.1 * q[near].max())).sum() >= 2


def test_waterfalls_on_a_staircase():
    """A river running east along row 10 with a 100 m step at column 30, and
    a lake at its head (surface 350 m) whose outlet pixel is at 300 m."""
    nx, ny = 40, 24
    ws = np.zeros((ny, nx))
    ws[10, :] = np.where(np.arange(nx) < 30, 300.0, 200.0) - 0.1 * np.arange(nx)
    rec = np.full(nx * ny, -1)
    r = 10 * nx + np.arange(nx - 1)
    rec[r] = r + 1
    q = np.zeros(nx * ny)
    q[r] = 1000.0
    falls = zoom.waterfalls(ws.ravel(), q, rec, nx, ny, 2.0, {10 * nx + 6: 350.0})
    big = falls[0]
    assert big["px"][0] == 10 and 27 <= big["px"][1] <= 29 and 99 <= big["height_m"] <= 101
    assert big["discharge_m3s"] == 1000 and abs(big["power_gw"] - 0.981) < 0.01
    lake = [f for f in falls if f["from_lake"]]
    assert lake and lake[0]["px"] == [10, 6] and 49 <= lake[0]["height_m"] <= 51


def test_zoom_reports_waterfalls(lake_zoom):
    for f in lake_zoom["stats"]["waterfalls"]:
        assert f["height_m"] >= zoom.WF_MIN_DROP and f["discharge_m3s"] >= zoom.WF_MIN_Q
        assert -90 <= f["lat"] <= 90 and -180 <= f["lon"] <= 180


# ---------------------------------------------------------------------------
# Real waterfalls: a continent whose rivers gather into one trunk flowing east
# down a valley, which drops off a 600 m escarpment at longitude 0 (craton
# under a thin sandstone cover).
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def falls_world():
    g = build_grid(5)
    lat, lon = latlon(g.centers)
    d0 = _dist_km(g, 0.0, 0.0)
    xk, yk = lon * 111.2, lat * 111.2
    elev = np.where(d0 < 2500, 80 + 0.1 * (2500 - xk) + 0.6 * np.abs(yk)
                    + 600 * zoom.smoothstep(150.0, -150.0, xk), -3000.0)
    precip = np.full(g.n, 1200.0)
    c = {"runoff": 0.5 * precip, "aet": 0.5 * precip, "lake_evap": np.full(g.n, 300.0)}
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c)
    land = elev > 0
    layers = {
        "elevation": np.round(elev), "precipitation": precip, "temperature": np.full(g.n, 22.0),
        "warm_month": np.full(g.n, 26.0), "flow": flow, "downstream": down, "lake": lk["wet"].astype(int),
        "rock": np.full(g.n, 5), "surface_rock": np.full(g.n, 7), "climate": np.full(g.n, 2),
        "ice": np.zeros(g.n), "sediment_cover": np.where(land, 0.2, 6.0),
    }
    return {"grid": g, "layers": layers, "meta": {"level": 5}}


@pytest.fixture(scope="module")
def falls_zoom(falls_world):
    return zoom.build(falls_world, 0.5, -1.0, size_km=1000, res_km=5, iterations=6, log=lambda *a: None)


def test_escarpment_keeps_a_waterfall(falls_zoom):
    z = falls_zoom
    nx, res = z["nx"], z["res"]
    lips = [f for f in z["stats"]["waterfalls"] if f["kind"] == "lip"]
    assert lips, z["stats"]["waterfalls"]
    f = max(lips, key=lambda f: f["height_m"])
    assert f["height_m"] >= 80 and f["discharge_m3s"] > 10000
    # concentrated: most of it over a single pixel, all of it within 3
    assert f["length_km"] <= 3 * 1.42 * res
    Lr = z["layers"]
    ws = (Lr["elevation"] + Lr["lake_depth"]).ravel().astype(float)
    lip = f["px"][0] * nx + f["px"][1]
    ch = zoom.ZK.chain(z["rec"], lip)
    drops = ws[ch[:3]] - ws[ch[1:4]]
    assert drops.max() >= 0.7 * f["height_m"], drops
    # the river above the lip is at grade with it: no further big drop just upstream
    up = np.flatnonzero(z["rec"] == ch[np.argmax(drops)])
    up = up[np.argmax(Lr["discharge"].ravel()[up])]
    assert ws[up] - ws[ch[np.argmax(drops)]] < 0.2 * f["height_m"]
    # a plunge pool at the foot
    foot = ch[np.argmax(drops) + 1]
    assert Lr["water"].ravel()[foot] == 2 and Lr["lake_depth"].ravel()[foot] >= 5
    assert f["plunge_pool_m"] >= 5
    # a gorge cut back from the escarpment: below the fall the river runs
    # between walls standing well above it
    assert f["gorge_km"] >= res
    q = Lr["discharge"].ravel()
    gorge = ch[np.argmax(drops) + 1:][:max(int(f["gorge_km"] / res), 1)]
    walls = []
    for p in gorge:
        r, c = divmod(int(p), nx)
        nb = [(r + a) * nx + c + b for a in (-1, 0, 1) for b in (-1, 0, 1)
              if (a or b) and q[(r + a) * nx + c + b] < 0.3 * q[p]]
        walls.append(max(ws[nb]) - ws[p])
    assert np.median(walls) >= 0.4 * f["height_m"], walls


def test_knickpoint_design():
    """A reach dropping 400 m over two ~110 km links on shield granite keeps
    a big share of the drop as falls; on shale less of it; a huge river
    splits it into a cascade."""
    pl = lambda x0: np.column_stack([np.linspace(x0, x0 + 110, 13), np.zeros(13)])
    ws = np.array([900.0, 700.0, 500.0, 480.0])
    down = np.array([1, 2, 3, -1])
    riv = np.ones(4, bool)
    land = np.ones(4, bool)
    polys = {0: pl(0), 1: pl(110), 2: pl(220)}
    km = {0: 110.0, 1: 110.0, 2: 110.0}

    def design(q, rock):
        kp = zoom.knickpoints(ws, down, riv, land, np.full(4, q), km, polys, {c: rock for c in polys})
        assert len(kp) == 1
        return kp[0]

    hard, soft = design(1000.0, (5, 5, 0.0)), design(1000.0, (8, 8, 2.0))
    assert len(hard["steps"]) == 1 and hard["steps"][0]["h"] > soft["steps"][0]["h"] > 0
    assert 150 <= hard["steps"][0]["h"] <= 300  # of ~350 m excess drop
    big = design(60000.0, (5, 5, 0.0))
    assert len(big["steps"]) >= 3
    assert big["steps"][0]["h"] > big["steps"][1]["h"]
    # the lip has retreated upstream of the escarpment, further on a bigger river
    assert big["steps"][0]["gorge_km"] > hard["steps"][0]["gorge_km"] > 0


def test_lake_outlet_has_no_cliff(lake_zoom):
    """Below the lake's outlet the river steps down gradually (or in one
    designed fall), not a cliff down to a river graded from far below."""
    z = lake_zoom
    lk = z["stats"]["largest_lakes"][0]
    nx, res = z["nx"], z["res"]
    Lr = z["layers"]
    ws = (Lr["elevation"] + Lr["lake_depth"]).ravel().astype(float)
    o = lk["outlet"][0] * nx + lk["outlet"][1]
    ch = zoom.ZK.chain(z["rec"], o)[:6]
    km = res * np.arange(len(ch)) * 1.42
    assert np.all(lk["level_m"] - ws[ch] <= zoom.RAPIDS_GRAD * km + 15), (lk["level_m"], ws[ch])
    assert not [f for f in z["stats"]["waterfalls"] if f["from_lake"] and f["height_m"] > 30]
