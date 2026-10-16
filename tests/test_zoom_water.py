"""Zoom lakes and deltas on a small synthetic world: a domed continent with
a basin that fills into an open lake, and radial rivers to the sea."""

import numpy as np
import pytest

from planet import climate, hydrology, zoom
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
    # (with a coastal lowland ~250 km wide, 8-30 m, where the big river's
    # delta plain can lie: the zoom builds one only on low coarse ground, PW-349)
    x = 2500 - d0  # km inland
    s = zoom.smoothstep(150.0, 450.0, x)
    elev = np.where(d0 < 2500, (1 - s) * (8 + 0.05 * x) + s * (60 + 0.3 * x), -3000.0)
    elev = elev - np.where(d0 < 2300, 500 * np.exp(-(_dist_km(g, *LAKE_AT) / 500) ** 2), 0)
    precip = np.full(g.n, 1200.0)
    # wet enough that the basin overflows: an open lake
    c = {"runoff": 0.5 * precip, "aet": 0.5 * precip, "lake_evap": np.full(g.n, 300.0)}
    # (its 53,000 m3/s river would cut the outlet of this ~200 m deep basin
    # down and drain it: hydrology.CHANNEL_K; the zoom's lakes are tested here)
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c, channel=0.0)
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
    net = lk["inflow_m3s"] - lk["evaporation_m3s"]
    assert net <= lk["outflow_m3s"] < 1.1 * net


@pytest.fixture(scope="module")
def evap_lake():
    """The open lake of water_world under a hot sky: open water evaporates
    1400 mm/yr, 800 more than the land around it (still open: its rivers
    bring more)."""
    g = build_grid(5)
    d0 = _dist_km(g, 0.0, 0.0)
    elev = np.where(d0 < 2500, 60 + 0.3 * (2500 - d0), -3000.0)
    elev = elev - np.where(d0 < 2300, 500 * np.exp(-(_dist_km(g, *LAKE_AT) / 500) ** 2), 0)
    precip = np.full(g.n, 1200.0)
    c = {"runoff": 0.5 * precip, "aet": 0.5 * precip, "lake_evap": np.full(g.n, 1400.0)}
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c, channel=0.0)
    lake = lk["wet"]
    assert lake.sum() >= 3 and np.all(lk["kind"][lake] == 1), "the basin should still hold an open lake"
    out = np.flatnonzero(lake & (down >= 0) & ~lake[np.maximum(down, 0)])
    q_coarse = float(flow[out].max() * 4 * np.pi * R_KM ** 2 / g.n * zoom.KM2_M_PER_YR_TO_M3S)
    layers = {
        "elevation": np.round(elev), "precipitation": precip, "temperature": np.full(g.n, 22.0),
        "warm_month": np.full(g.n, 26.0), "flow": flow, "downstream": down, "lake": lake.astype(int),
        "lake_level": np.maximum(np.round(lk["level"]), np.round(elev)), "lake_kind": lk["kind"].astype(int),
        "runoff": c["runoff"], "evaporation": c["aet"], "pet": c["lake_evap"] / climate.TUNE["open_water"],
        "rock": np.zeros(g.n, int), "surface_rock": np.zeros(g.n, int), "climate": np.full(g.n, 2),
        "ice": np.zeros(g.n), "sediment_cover": np.where(elev > 0, 0.5, 6.0),
    }
    z = zoom.build({"grid": g, "layers": layers, "meta": {"level": 5}}, *LAKE_AT, size_km=1600, res_km=8,
                   iterations=6, log=lambda *a: None)
    return z, q_coarse


def test_open_lake_evaporates(evap_lake):
    """An open lake loses its open-water evaporation before passing its water
    on, as the coarse world's lake does (PW-271): the zoom lake's outflow
    is close to the coarse lake's (the zoom sees ~90% of its catchment)."""
    z, q_coarse = evap_lake
    lk = z["stats"]["largest_lakes"][0]
    net = lk["inflow_m3s"] - lk["evaporation_m3s"]
    assert lk["evaporation_m3s"] > 0.25 * lk["inflow_m3s"]
    assert net <= lk["outflow_m3s"] < 1.05 * net
    assert 0.8 < lk["outflow_m3s"] / q_coarse < 1.1, (lk, q_coarse)


def test_zoom_keeps_inland_cell_means(lake_zoom):
    """Each coarse land cell away from the coast keeps its mean height
    through the valley carving and the landscape pass (PW-268: the valleys
    lowered it 60-90 m)."""
    st = lake_zoom["stats"]
    assert abs(st["inland_cell_mean_bias_m"]) < 20, st
    assert st["inland_cell_mean_rms_error_m"] < 120, st


def test_every_lake_fragment_passes_its_water_on(lake_zoom):
    """No fragment of an open lake swallows its rivers (PW-062)."""
    assert lake_zoom["lakes"]
    assert all(lk["open"] and lk["outlet"] >= 0 for lk in lake_zoom["lakes"]), lake_zoom["lakes"]


@pytest.fixture(scope="module")
def closed_zoom():
    """The same basin in a dry climate: it holds a closed lake (lake_kind 2)
    whose level (the world's lake_level) stands well below the spill level."""
    g = build_grid(5)
    d0 = _dist_km(g, 0.0, 0.0)
    elev = np.where(d0 < 2500, 260 + 0.3 * (2500 - d0), -3000.0)
    elev = elev - np.where(d0 < 2300, 500 * np.exp(-(_dist_km(g, *LAKE_AT) / 500) ** 2), 0)
    precip = np.full(g.n, 500.0)
    c = {"runoff": 0.2 * precip, "aet": 0.8 * precip, "lake_evap": np.full(g.n, 1200.0)}
    # (its 53,000 m3/s river would cut the outlet of this ~200 m deep basin
    # down and drain it: hydrology.CHANNEL_K; the zoom's lakes are tested here)
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c, channel=0.0)
    wet = lk["wet"]
    assert wet.sum() >= 3 and np.all(lk["kind"][wet] == 2), "the dry basin should hold a closed lake"
    spill = hydrology.priority_flood(g, elev)[0]
    level = float(np.median(lk["level"][wet]))
    assert level < np.median(spill[wet]) - 30
    layers = {
        "elevation": np.round(elev), "precipitation": precip, "temperature": np.full(g.n, 22.0),
        "warm_month": np.full(g.n, 26.0), "flow": flow, "downstream": down, "lake": wet.astype(int),
        "lake_level": np.where(wet, lk["level"], np.nan), "lake_kind": lk["kind"].astype(int),
        "runoff": c["runoff"],
        "rock": np.zeros(g.n, int), "surface_rock": np.zeros(g.n, int), "climate": np.full(g.n, 4),
        "ice": np.zeros(g.n), "sediment_cover": np.where(elev > 0, 0.5, 6.0),
    }
    z = zoom.build({"grid": g, "layers": layers, "meta": {"level": 5}}, *LAKE_AT, size_km=1600, res_km=8,
                   iterations=6, log=lambda *a: None)
    return z, level


def test_closed_lake_keeps_its_water(closed_zoom):
    z, level = closed_zoom
    lk = z["stats"]["largest_lakes"][0]
    assert abs(lk["level_m"] - level) < 1.0  # the world's lake_level, not the spill level
    assert lk["outlet"] is None and lk["outflow_m3s"] == 0.0
    assert lk["inflow_m3s"] > 0
    # its smaller fragments (if any) pass their water on to it
    main = max(z["lakes"], key=lambda d: d["n_px"])
    assert not main["open"] and main["outlet"] < 0
    assert all(d["outlet"] >= 0 for d in z["lakes"] if d is not main), z["lakes"]


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
    # only the outlet channel may sit below the water (the lake's, or a
    # plunge pool's below a fall's lip)
    outs = [(orow, ocol)] + [tuple(st["lip_px"]) for kp in lake_zoom["kps"] for st in kp["steps"] if "lip_px" in st]
    near = [min(max(abs(r - a), abs(c - b)) for a, b in outs) for r, c in zip(rr, cc)]
    assert np.all(np.array(near, int) <= 2), list(zip(rr, cc))


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


def test_delta_fingers_curve_and_build_out_into_the_sea():
    """PW-061: a river-dominated delta's fingers bend away from the fan's
    middle and wander (they were straight strips), narrow to their tips, and
    none runs along a direction that goes on over land; each finger's branch
    follows its axis."""
    rng = np.random.default_rng(3)
    line = zoom._finger_axis(0.0, 0.0, np.array([1.0, 0.0]), np.array([0.0, 1.0]), 100.0, 0.4, rng)
    assert np.allclose(line[0], [-30.0, 0.0])  # (from 0.3 Lk inland of the mouth)
    assert line[-1][1] > 3.0 and abs(line[-1][0] - 100.0) < 5.0  # (bent to its own side of the fan)
    d, s = zoom._polyline_dist(np.array([50.0, -30.0]), np.array([line[16][1] + 2.0, 40.0]), line)
    assert abs(d[0] - 2.0) < 0.5 and abs(s[0] - 80.0) < 3.0 and abs(d[1] - 40.0) < 1e-6 and s[1] == 0
    # a coast along x = 0 (sea east of it), but land again north of y = 40 km:
    # the fingers fanning north-east, over that land, are left out
    res, n = 2.0, 200
    xs = (np.arange(n) + 0.5 - n / 2) * res
    X, Y = np.meshgrid(xs, -xs)
    px, py = X.ravel(), Y.ravel()
    ind = np.where((px < 0) | (py > 40), 1.0, -1.0)
    dl = {"R": 150.0, "Rl": 30.0, "wR": 1.0, "wW": 0.0, "wT": 0.0, "x": -1.0, "y": 0.0, "u": (1.0, 0.0),
          "nb": 5, "cell": 7}
    f = zoom._delta_forms(dl, px, py, res, np.random.default_rng(1), ind, n, n)
    assert f["kind"] == "fingers" and 1 <= len(f["goals"]) < 5
    for ln in dl["finger_lines"]:
        c = np.clip(np.floor(ln[:, 0] / res + n / 2).astype(int), 0, n - 1)
        r = np.clip(np.floor(n / 2 - ln[:, 1] / res).astype(int), 0, n - 1)
        assert np.mean(ind[r * n + c][len(ln) // 4:] > 0) <= 0.4


def test_no_delta_plain_on_high_ground():
    """PW-349: a big river reaching the sea down a coast whose coarse
    ground stands ~300 m and more gets no delta plain flattened to a few
    metres there (it was laid on ground up to 800 m high, and left
    river-mouth zooms ~25 m low inland); the inland cells keep their means."""
    g = build_grid(5)
    d0 = _dist_km(g, 0.0, 0.0)
    elev = np.where(d0 < 2500, 300 + 0.3 * (2500 - d0), -3000.0)
    precip = np.full(g.n, 1200.0)
    c = {"runoff": 0.5 * precip, "aet": 0.5 * precip, "lake_evap": np.full(g.n, 300.0)}
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c, channel=0.0)
    layers = {
        "elevation": np.round(elev), "precipitation": precip, "temperature": np.full(g.n, 22.0),
        "warm_month": np.full(g.n, 26.0), "flow": flow, "downstream": down, "lake": lk["wet"].astype(int),
        "runoff": c["runoff"], "rock": np.zeros(g.n, int), "surface_rock": np.zeros(g.n, int),
        "climate": np.full(g.n, 2), "ice": np.zeros(g.n), "sediment_cover": np.where(elev > 0, 0.5, 6.0),
    }
    mouths = np.flatnonzero((elev > 0) & (down >= 0))
    mouths = mouths[elev[down[mouths]] <= 0]
    i = mouths[np.argmax(flow[mouths])]
    p = g.centers[i] + g.centers[down[i]]
    lat, lon = np.degrees(np.arcsin(p[2] / np.linalg.norm(p))), np.degrees(np.arctan2(p[1], p[0]))
    z = zoom.build({"grid": g, "layers": layers, "meta": {"level": 5}}, float(lat), float(lon), size_km=1600,
                   res_km=8, iterations=6, log=lambda *a: None)
    st = z["stats"]
    assert st["deltas"] and st["deltas"][0]["discharge_m3s"] >= 5 * zoom.DELTA_MIN_Q
    dl = st["deltas"][0]
    n = z["nx"]
    xs = (np.arange(n) + 0.5 - n / 2) * z["res"]
    X, Y = np.meshgrid(xs, -xs)
    # inland of the mouth, 0.2-0.5 of the plain's radius up the river (not the coast either side)
    R, u = dl["plain_radius_km"], np.array(dl["seaward"])
    dx, dy = X - dl["mouth_km"][0], Y - dl["mouth_km"][1]
    a, b = dx * u[0] + dy * u[1], dx * -u[1] + dy * u[0]
    land = (z["layers"]["water"] == 0) & (a < -0.2 * R) & (a > -0.5 * R) & (np.abs(b) < 0.3 * R)
    assert land.sum() > 50
    assert np.median(z["layers"]["elevation"][land]) > 150
    assert abs(st["inland_cell_mean_bias_m"]) < 10, st["inland_cell_mean_bias_m"]


def test_waterfalls_on_a_staircase():
    """A river running east along row 10 with a 100 m step at column 30, and
    a lake (surface 350 m) whose outlet pixel (column 10) is at 300 m."""
    nx, ny = 40, 24
    ws = np.zeros((ny, nx))
    ws[10, :] = np.where(np.arange(nx) < 30, 300.0, 200.0) - 0.1 * np.arange(nx)
    rec = np.full(nx * ny, -1)
    r = 10 * nx + np.arange(nx - 1)
    rec[r] = r + 1
    q = np.zeros(nx * ny)
    q[r] = 1000.0
    falls = zoom.waterfalls(ws.ravel(), q, rec, nx, ny, 2.0, {10 * nx + 10: 350.0})
    big = falls[0]
    assert big["px"][0] == 10 and 27 <= big["px"][1] <= 29 and 99 <= big["height_m"] <= 101
    assert big["discharge_m3s"] == 1000 and abs(big["power_gw"] - 0.981) < 0.01
    lake = [f for f in falls if f["from_lake"]]
    assert lake and lake[0]["px"] == [10, 10] and 49 <= lake[0]["height_m"] <= 51


def test_steep_reach_is_not_a_fall():
    """A stream falling a steady 40 m/km on 4 km pixels drops 160 m per
    pixel, but it's a steep reach, not a fall (PW-070); a step of the same
    height on a gentle river is one."""
    nx, ny, res = 40, 24, 4.0
    r = 10 * nx + np.arange(nx - 1)
    rec = np.full(nx * ny, -1)
    rec[r] = r + 1
    q = np.zeros(nx * ny)
    q[r] = 300.0
    ws = np.zeros((ny, nx))
    ws[10, :] = 3000.0 - 40.0 * res * np.arange(nx)
    assert not zoom.waterfalls(ws.ravel(), q, rec, nx, ny, res)
    ws[10, :] = 3000.0 - 0.5 * res * np.arange(nx) - 160.0 * (np.arange(nx) >= 20)
    f = zoom.waterfalls(ws.ravel(), q, rec, nx, ny, res)
    assert len(f) == 1 and f[0]["px"] == [10, 19] and abs(f[0]["height_m"] - 162) < 1


def test_steep_stream_reaching_a_flat_floor_is_not_a_fall():
    """A mountain stream falling 50 m/km on 4 km pixels, its last link
    100 m/km (400 m) onto a flat valley floor: only 2x as steep as the
    stream above it, so no fall, though the floor below is flat (PW-125:
    pooled over both sides, the flat side halved the context and it was
    listed). A hanging tributary, gentle above with the same 400 m step at
    the floor, is one."""
    nx, ny, res = 40, 24, 4.0
    r = 10 * nx + np.arange(nx - 1)
    rec = np.full(nx * ny, -1)
    rec[r] = r + 1
    q = np.zeros(nx * ny)
    q[r] = 50.0
    col = np.arange(nx)
    ws = np.zeros((ny, nx))
    ws[10, :] = np.where(col < 20, 500.0 + 50.0 * res * (19 - col), 100.0 - 0.1 * res * (col - 20))
    assert not zoom.waterfalls(ws.ravel(), q, rec, nx, ny, res)
    ws[10, :] = np.where(col < 20, 500.0 + 2.0 * res * (19 - col), 100.0 - 0.1 * res * (col - 20))
    f = zoom.waterfalls(ws.ravel(), q, rec, nx, ny, res)
    assert len(f) == 1 and f[0]["px"] == [10, 19] and abs(f[0]["height_m"] - 400) < 1


def test_tributary_near_a_designed_lip_is_tested_like_any_other():
    """PW-298 (PW-319): a steep tributary joining a designed fall's river
    within 3 px of its lip isn't exempt from the contrast test (only the
    designed river's own water is): at 4 km, 21 of the arc zoom's 26
    undesigned 'drops' >= 100 m were such tributaries, 1.25x as steep at
    their last link as above it. A hanging one is still a fall."""
    nx, ny, res = 40, 24, 4.0
    main = 10 * nx + np.arange(nx - 1)
    rec = np.full(nx * ny, -1)
    rec[main] = main + 1
    trib = np.arange(2, 10) * nx + 21  # (a stream down column 21 into the main river at row 10, 3 px from the lip)
    rec[trib] = trib + nx
    q = np.zeros(nx * ny)
    q[main] = np.where(np.arange(nx - 1) < 20, 1000.0, 1050.0)
    q[trib] = 40.0
    ws = np.zeros((ny, nx))
    col = np.arange(nx)
    ws[10, :] = np.where(col <= 18, 900.0 - 0.5 * res * col, 200.0 - 0.5 * res * (col - 19))  # a 650 m designed lip
    lip = 10 * nx + 18
    rows = np.arange(2, 10)
    ws[rows, 21] = 196.0 + 380.0 + 95.0 * res * (9 - rows)  # 95 m/km above, 380 m (95 m/km) at its last link
    f = zoom.waterfalls(ws.ravel(), q, rec, nx, ny, res, designed=[lip], top=None, sep_km=0.0)
    assert [x["px"] for x in f] == [[10, 18]], f
    ws[rows, 21] = 196.0 + 380.0 + 5.0 * res * (9 - rows)  # hanging: 5 m/km above the same step
    f = zoom.waterfalls(ws.ravel(), q, rec, nx, ny, res, designed=[lip], top=None, sep_km=0.0)
    assert sorted(x["px"] for x in f) == [[9, 21], [10, 18]], f


def test_local_base_starts_each_profile_in_its_own_cell():
    """PW-298: the relief a cell's own slopes make is measured from where
    its water leaves the cell (or a held point: a floor, a cap)."""
    from planet import zoom_kernels as ZK
    n = 6  # a chain 0 <- 1 <- ... <- 5, pixel 0 the outlet; cells {0, 1, 2} and {3, 4, 5}
    h = np.array([0.0, 10.0, 20.0, 35.0, 50.0, 65.0])
    rec = np.arange(n) - 1
    order = np.arange(n)
    fixed = np.zeros(n, bool)
    fixed[0] = True
    group = np.array([0, 0, 0, 1, 1, 1])
    floor, cap = np.full(n, -np.inf), np.full(n, np.inf)
    lb = ZK.local_base(h, rec, order, fixed, floor, cap, group)
    assert list(lb) == [0, 0, 0, 20, 20, 20]
    floor[4] = 45.0  # (held by a floor above its receiver: the relief starts there)
    cap[2] = 20.0  # (a capped pixel holds itself)
    lb = ZK.local_base(h, rec, order, fixed, floor, cap, group)
    assert list(lb) == [0, 0, 20, 20, 45, 45]


def test_slope_fit_keeps_the_cell_means_and_settles():
    """PW-298: the landscape pass keeps each inland cell's mean (the fit
    converges: its residual falls >10x and C stops growing), on the
    escarpment world (rivers held at a staircase, a 600 m scarp). The old
    per-pixel fit wound C up x1.5 a pass next to held courses."""
    w = _escarpment_world(0.6, 600.0)
    z = zoom.build(w, 0.0, 0.0, size_km=600, res_km=2.0, log=lambda *a: None)
    fit = z["debug"]["fit"]
    assert fit[-1][0] < 0.1 * fit[0][0], fit
    assert fit[-1][1] < 1.2 * fit[-4][1], fit
    st = z["stats"]
    assert abs(st["inland_cell_mean_bias_m"]) < 15 and st["inland_cell_mean_rms_error_m"] < 40, st


def test_zoom_reports_waterfalls(lake_zoom):
    for f in lake_zoom["stats"]["waterfalls"]:
        assert f["height_m"] >= zoom.WF_MIN_DROP and f["discharge_m3s"] >= zoom.WF_MIN_Q
        assert -90 <= f["lat"] <= 90 and -180 <= f["lon"] <= 180


# ---------------------------------------------------------------------------
# Real waterfalls: a continent whose rivers gather into one trunk flowing east
# down a valley, which drops off a 600 m escarpment at longitude 0 (craton
# under a thin sandstone cover).
# ---------------------------------------------------------------------------
def _escarpment_world(slope, scarp):
    """The continent sloping east at `slope` m/km, with a `scarp` m escarpment at longitude 0."""
    g = build_grid(5)
    lat, lon = latlon(g.centers)
    d0 = _dist_km(g, 0.0, 0.0)
    xk, yk = lon * 111.2, lat * 111.2
    elev = np.where(d0 < 2500, 80 + slope * (2500 - xk) + 0.6 * np.abs(yk)
                    + scarp * zoom.smoothstep(150.0, -150.0, xk), -3000.0)
    precip = np.full(g.n, 1200.0)
    c = {"runoff": 0.5 * precip, "aet": 0.5 * precip, "lake_evap": np.full(g.n, 300.0)}
    # (its 53,000 m3/s river would cut the outlet of this ~200 m deep basin
    # down and drain it: hydrology.CHANNEL_K; the zoom's lakes are tested here)
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c, channel=0.0)
    land = elev > 0
    layers = {
        "elevation": np.round(elev), "precipitation": precip, "temperature": np.full(g.n, 22.0),
        "warm_month": np.full(g.n, 26.0), "flow": flow, "downstream": down, "lake": lk["wet"].astype(int),
        "rock": np.full(g.n, 5), "surface_rock": np.full(g.n, 7), "climate": np.full(g.n, 2),
        "ice": np.zeros(g.n), "sediment_cover": np.where(land, 0.2, 6.0),
    }
    return {"grid": g, "layers": layers, "meta": {"level": 5}}


@pytest.fixture(scope="module")
def falls_world():
    return _escarpment_world(0.1, 600)


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
    assert lk["outflow_grad_m_km"] >= zoom.RAPIDS_GRAD
    assert np.all(lk["level_m"] - ws[ch] <= lk["outflow_grad_m_km"] * km + 15), (lk["level_m"], ws[ch])
    assert not [f for f in z["stats"]["waterfalls"] if f["from_lake"] and f["height_m"] > 30]


def test_outflow_grad_follows_the_coarse_relief(water_world):
    """A lake's rapids fall as steeply as its coarse outflow does: the
    steepest mean descent from its level down its river; 3x the relief, 3x
    the gradient (a mountain lake's outflow cascades, PW-123); closed lakes 0."""
    g, L = water_world["grid"], water_world["layers"]
    elev, down = L["elevation"].astype(float), L["downstream"].astype(int)
    lab, lvl, ex = zoom.coarse_lakes(g, L, elev)
    gr = zoom.outflow_grad(g, elev, down, lab, lvl, ex, 500.0)
    assert np.all(gr[ex < 0] == 0) and np.all(gr[ex >= 0] > 0)
    k = int(np.flatnonzero(ex >= 0)[0])
    # by hand: the mean descent to the first cell below the exit
    n = down[ex[k]]
    s = (np.min(np.arccos(np.clip(g.centers[lab == k] @ g.centers[ex[k]], -1, 1)))
         + np.arccos(np.clip(g.centers[ex[k]] @ g.centers[n], -1, 1))) * R_KM
    assert gr[k] >= (lvl[k] - max(elev[n], 0)) / s - 1e-9
    gr3 = zoom.outflow_grad(g, 3 * elev, down, lab, 3 * lvl, ex, 500.0)
    assert np.allclose(gr3, 3 * gr)


def test_coarse_lake_levels_are_the_priority_flood_spill(water_world):
    """PW-343: without a lake_level layer the levels are the pit-filled
    surface (kernels.flood_fill, priority_flood's filled surface alone),
    for integer heights too."""
    from planet import hydrology
    g, L = water_world["grid"], dict(water_world["layers"])
    L.pop("lake_level", None)
    for elev in (L["elevation"].astype(float), np.round(L["elevation"]).astype(np.int64)):
        lab, lvl, _ = zoom.coarse_lakes(g, L, elev)
        want = hydrology.priority_flood(g, elev)[0]
        assert len(lvl)
        assert all(lvl[k] == np.median(want[lab == k]) for k in range(len(lvl)))


def test_staircase_fits_the_valley():
    """The falls of a long reach whose steepest link is at its far end: the
    floor drops at the lips and stands on a plateau above each, but never
    above the coarse ground, and never below the valley floor."""
    s = np.linspace(0.0, 600.0, 61)
    tz = 1000.0 - 1.5 * s  # the valley floor, 1.5 m/km
    ez = tz + 150.0  # the coarse ground, 150 m above it
    kp = {"s": s, "steps": [{"s": 500.0, "h": 400.0}, {"s": 560.0, "h": 200.0}]}
    f = zoom.staircase(kp, tz, ez)
    assert 0 < f < 1  # 400 m doesn't fit in a 150 m deep valley: scaled down
    sv = np.linspace(0.0, 600.0, 6001)
    z = zoom.stair_z(kp, sv)
    t, e = np.interp(sv, s, tz), np.interp(sv, s, ez)
    assert np.all(z <= e + 1e-6) and np.all(z >= t - 1e-6)
    assert np.all(np.diff(z) <= 1e-9)
    assert abs(z[0] - tz[0]) < 1e-6 and abs(z[-1] - tz[-1]) < 1e-6
    for st in kp["steps"]:  # each fall is a sharp step of its (scaled) height
        top, bot = zoom.stair_z(kp, np.array([st["s"] - 1e-3, st["s"]]))
        assert abs(top - bot - st["h"]) < 0.05
    assert kp["steps"][0]["h"] >= 100  # most of the valley's depth, at the lip
    # far upstream of the falls the river is back on its valley floor
    assert np.allclose(z[sv < 300], t[sv < 300])


@pytest.fixture(scope="module")
def long_reach_zoom():
    """Rivers falling 1.2 m/km for a thousand km down to the escarpment: a
    long reach with falls, whose designed falls (at its far end) used to
    hold the river on a ridge hundreds of metres above the land all the way
    down to them."""
    return zoom.build(_escarpment_world(1.2, 400), 0.5, -3.0, size_km=1000, res_km=5, iterations=6,
                      log=lambda *a: None)


def test_big_falls_are_designed(long_reach_zoom):
    """Regression: the river used to leave its perched course wherever the
    land beside it drained lower, dropping 400-1200 m off the side in a bare
    step ("drop", no lip, gorge or plunge pool), while the designed lips
    downstream got ~0 m. Now every big fall on a big river is a designed lip."""
    falls = long_reach_zoom["stats"]["waterfalls"]
    big = [f for f in falls if f["discharge_m3s"] >= 2000 and f["height_m"] >= 100]
    assert big and all(f["kind"] == "lip" for f in big), falls
    assert max(f["height_m"] for f in big) >= 200


def test_a_hyperarid_zoom_has_no_rivers_of_its_own():
    """The zoom's streams are fed by the world's runoff, not its rain
    (PW-180): 60 mm/yr that all evaporates makes no river, while the
    landscape is still graded (its cell means kept)."""
    g = build_grid(5)
    d0 = _dist_km(g, 0.0, 0.0)
    elev = np.where(d0 < 2500, 60 + 0.3 * (2500 - d0), -3000.0)
    precip = np.full(g.n, 60.0)
    c = {"runoff": np.zeros(g.n), "aet": precip, "lake_evap": np.full(g.n, 1500.0)}
    # (its 53,000 m3/s river would cut the outlet of this ~200 m deep basin
    # down and drain it: hydrology.CHANNEL_K; the zoom's lakes are tested here)
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c, channel=0.0)
    land = elev > 0
    w = {"grid": g, "meta": {"level": 5}, "layers": {
        "elevation": np.round(elev), "precipitation": precip, "temperature": np.full(g.n, 24.0),
        "warm_month": np.full(g.n, 32.0), "flow": flow, "downstream": down, "lake": lk["wet"].astype(int),
        "lake_level": np.maximum(np.round(lk["level"]), np.round(elev)), "lake_kind": lk["kind"].astype(int),
        "runoff": c["runoff"], "rock": np.zeros(g.n, int), "surface_rock": np.zeros(g.n, int),
        "climate": np.full(g.n, 3), "ice": np.zeros(g.n), "sediment_cover": np.where(land, 0.5, 6.0)}}
    z = zoom.build(w, 5.0, 8.0, size_km=800, res_km=8, iterations=6, log=lambda *a: None)
    assert z["layers"]["discharge"].max() < 0.5
    w["layers"]["runoff"] = 0.5 * precip  # (the same land, wet: the same landscape)
    wet = zoom.build(w, 5.0, 8.0, size_km=800, res_km=8, iterations=6, log=lambda *a: None)
    assert wet["layers"]["discharge"].max() > 5.0
    assert abs(z["stats"]["cell_mean_rms_error_m"] - wet["stats"]["cell_mean_rms_error_m"]) < 10


def test_lake_kind_layer_matches_the_lakes(water_world, lake_zoom):
    """The zoom stores each lake pixel's kind (hydrology's lake_kind): an open
    coarse lake is fresh, the same lake marked closed is salt, and the layer
    is non-zero exactly on the lake pixels (no landform basins here: no pans)."""
    Lz = lake_zoom["layers"]
    lake = Lz["water"] == 2
    assert lake.any() and Lz["lake_kind"].dtype == np.uint8
    assert np.all(Lz["lake_kind"][lake] == 1) and np.all(Lz["lake_kind"][~lake] == 0)
    # the same basin closed (its water balance would keep it salty): salt
    w = {**water_world, "layers": {**water_world["layers"]}}
    kind = w["layers"]["lake_kind"].copy()
    kind[kind == 1] = 2
    w["layers"]["lake_kind"] = kind
    z = zoom.build(w, *LAKE_AT, size_km=1600, res_km=8, iterations=6, log=lambda *a: None)
    lk = z["layers"]["lake_kind"]
    wet = z["layers"]["water"] == 2
    # (all salt but the plunge pools at the falls' feet, a few pixels: always fresh)
    assert wet.any() and np.mean(lk[wet] == 2) > 0.99 and np.all(lk[~wet] == 0)
