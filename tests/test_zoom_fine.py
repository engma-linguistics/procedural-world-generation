"""Nested fine zooms (zoom_fine, PW-129) of a small synthetic parent zoom:
a valley whose river drops 500 m over a scarp (a fall in the parent's
stats) and a stratovolcano beside it, on a synthetic world for the climate.
Checked: the parent's means kept (over 3x3 parent pixels: see zoom_fine's
landscape pass), the fall's and the volcano's heights exactly, the edge
on the parent's surface, a fine zoom of a fine zoom, the step limit, and
saving / indexing / deleting with the parent."""

import json
from types import SimpleNamespace

import numpy as np
import pytest

from planet import api
from planet import store as S
from planet import world as W
from planet import zoom as Z
from planet import zoom_fine as ZF
from planet.geo import R_KM, xyz
from planet.grid import build_grid

CENTRE = (38.0, 10.0)  # the parent zoom's centre
NP, RP = 100, 1.0  # parent: 100 x 100 px at 1 km
LIP = (50, 51)  # the fall's lip (row, col); the river runs west along row 50
VOLC = (44, 57)  # the volcano's summit pixel
SUMMIT_LIFT = 15.0  # m: the stated summit stands this much above the parent's highest pixel (sub-pixel peak)


def _dist_km(g, lat, lon):
    c = xyz(np.radians(lat), np.radians(lon))
    return np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM


@pytest.fixture(scope="module")
def world():
    g = build_grid(4)
    d = _dist_km(g, *CENTRE)
    elev = np.where(d < 2500, 300 + 0.3 * (2500 - d), -3000.0)
    land = elev > 0
    extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2), "sediment_cover": np.where(land, 0.2, 6.0)}
    return W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 4}, erosion=0.0)


def _parent():
    """(meta, layers) of a synthetic 1 km zoom: lower plateau west of the
    scarp (col 50), upper plateau east, a river along row 50 flowing west
    over the scarp (a 500 m fall), valley sides, a cone with a crater."""
    r, c = np.mgrid[0:NP, 0:NP].astype(float)
    bed = np.where(c <= 50, 400 + 1.0 * c, 950 + 1.0 * (c - 51))
    h = bed + 25 * np.abs(r - LIP[0]) + 20 * np.sin(c / 3.1) * np.cos(r / 4.3)
    river = r == LIP[0]
    h = np.where(river, bed, h)
    dv = np.hypot(r - VOLC[0], c - VOLC[1])
    cone = 1500 * np.exp(-dv / 5.0) - 600 * np.exp(-dv ** 2)  # (a crater ~100 m deep at the top)
    h = np.where(river, h, h + cone)
    # receivers: the river west, the rest down to it
    slot = np.where(river, 3, np.where(r < LIP[0], 6, 1)).astype(np.uint8)
    slot[LIP[0], 0] = Z.D8_NONE
    q = np.where(river, 30.0, 0.05)
    area = np.where(river, 800.0, 1.0)
    fr = Z.Frame(*CENTRE)

    def latlon_of(rr, cc):
        x, y = (cc + 0.5 - NP / 2) * RP, (NP / 2 - rr - 0.5) * RP
        return Z._latlon(fr.to_sphere(np.array([x]), np.array([y]))[0])

    top = float(h[LIP])
    drop = top - float(h[LIP[0], LIP[1] - 1])
    vtop = float(h[dv <= 1.5].max()) + SUMMIT_LIFT
    vla, vlo = latlon_of(*VOLC)
    z0 = np.zeros((NP, NP))
    layers = {
        "elevation": h.astype(np.float32), "water": np.zeros((NP, NP), np.uint8), "lake_depth": z0,
        "lake_kind": np.zeros((NP, NP), np.uint8), "discharge": q, "drainage_area": area, "receiver": slot,
        "precipitation": np.full((NP, NP), 900.0), "precipitation_jul": np.full((NP, NP), 600.0),
        "precipitation_jan": np.full((NP, NP), 1200.0), "temperature": np.full((NP, NP), 12.0), "ice": z0,
        "tide_range": z0, "wave_power": z0, "rock": np.full((NP, NP), 2, np.uint8),
        "surface_rock": np.full((NP, NP), 2, np.uint8), "climate": np.full((NP, NP), 14, np.uint8),
        "biome": np.full((NP, NP), 3, np.uint8), "landform": np.zeros((NP, NP), np.uint8),
        "wetland": np.zeros((NP, NP), np.uint8), "coastal_life": np.zeros((NP, NP), np.uint8),
    }
    fall = {"px": list(LIP), "lat": 0.0, "lon": 0.0, "height_m": round(drop, 1), "discharge_m3s": 30.0,
            "kind": "scarp", "length_km": 1.0, "from_lake": False}
    volc = {"lat": vla, "lon": vlo, "kind": "arc", "form": "active stratovolcano", "active": True, "top_m": vtop,
            "height_m": 1500.0, "x_km": (VOLC[1] + 0.5 - NP / 2) * RP, "y_km": (NP / 2 - VOLC[0] - 0.5) * RP}
    meta = {"id": "fpar01", "name": "test world: parent", "res_km": RP, "nx": NP, "ny": NP,
            "center": {"lat": CENTRE[0], "lon": CENTRE[1]}, "size_km": NP * RP,
            "source_world": {"id": "none", "name": "test world"},
            "stats": {"falls": [fall], "waterfalls": [], "volcanoes": [volc]}}
    return meta, layers


def _at(meta, row, col):
    fr = Z.Frame(meta["center"]["lat"], meta["center"]["lon"])
    x, y = (col + 0.5 - meta["nx"] / 2) * meta["res_km"], (meta["ny"] / 2 - row - 0.5) * meta["res_km"]
    return Z._latlon(fr.to_sphere(np.array([x]), np.array([y]))[0])


@pytest.fixture(scope="module")
def parent():
    return _parent()


@pytest.fixture(scope="module")
def fine(parent, world):
    meta, _ = parent
    lat, lon = _at(meta, 48, 53)  # between the fall and the volcano
    return ZF.build(parent, world, lat, lon, size_km=20, res_km=0.1, log=lambda *a: None), (lat, lon)


def _as_parent(z, pmeta, lat, lon, zid):
    """A built fine zoom as a parent (meta, layers), as zoom.load gives it."""
    meta = {"id": zid, "name": "test world: fine", "res_km": z["res"], "nx": z["nx"], "ny": z["ny"],
            "center": {"lat": lat, "lon": lon}, "size_km": z["size_km"], "source_world": pmeta["source_world"],
            "parent_zoom": z["parent"], "stats": z["stats"]}
    return meta, {k: np.asarray(v) for k, v in z["layers"].items()}


def test_parent_means_kept(parent, fine):
    s = fine[0]["stats"]
    assert s["parent_pixels"] > 200
    assert abs(s["mean_elev_m"] - s["parent_mean_elev_m"]) < 5.0
    relief = float(np.ptp(parent[1]["elevation"]))  # (~1800 m: steep valley sides, a scarp, a cone)
    assert s["parent_block_mean_rms_error_m"] < 0.025 * relief
    assert abs(s["parent_mean_bias_m"]) < 5.0


def test_fall_keeps_the_parents_drop(parent, fine):
    z = fine[0]
    f, = z["stats"]["falls"]
    pf = parent[0]["stats"]["falls"][0]
    L = z["layers"]
    h, ld = L["elevation"].astype(float), L["lake_depth"].astype(float)
    assert f["parent_fall"] == 0 and f["lineage"] == [0]
    assert f["height_m"] == pf["height_m"]
    assert abs(f["top_m"] - float(parent[1]["elevation"][LIP])) < 0.01
    assert abs(h[tuple(f["px"])] - f["top_m"]) < 0.01  # the lip
    pool = tuple(f["pool_px"])
    assert L["water"][pool] == 2  # the plunge pool, its surface the lip minus the drop
    assert abs(h[pool] + ld[pool] - (f["top_m"] - f["height_m"])) < 0.01
    # and the river's water goes over it
    assert L["discharge"][tuple(f["px"])] > 0.5 * pf["discharge_m3s"]


def _gorge_plane(z, f):
    """A fine zoom's fall's gorge path in its pixel coordinates (row, col)."""
    P = np.array([xyz(np.radians(a), np.radians(b)) for a, b in f["gorge_path"]])
    x, y = z["frame"].to_plane(P)
    return z["ny"] / 2 - y / z["res"] - 0.5, x / z["res"] + z["nx"] / 2 - 0.5


def test_gorge_follows_a_smooth_path_with_climbing_walls(fine):
    """PW-390: the gorge below a fall is laid along a smooth path, its floor
    falling all the way (no stair steps) and its walls climbing from the
    floor to the rim (no bands, ridges or trenches along them)."""
    z = fine[0]
    f, = z["stats"]["falls"]
    h = z["layers"]["elevation"].astype(float)
    res = z["res"]
    assert f["gorge_km"] > 0.5 and len(f["gorge_path"]) >= 4 and f["gorge_half_km"] > res
    r, c = _gorge_plane(z, f)
    turn = np.abs(np.diff(np.unwrap(np.arctan2(np.diff(r), np.diff(c)))))
    assert turn.max() < np.radians(30)  # (smooth: no D8 elbows)
    # the floor: the course from the pool to the foot never climbs, and drops in no single step
    rec = ZF._Parent.receivers(SimpleNamespace(L=z["layers"], nx=z["nx"], ny=z["ny"]))
    i, foot = f["pool_px"][0] * z["nx"] + f["pool_px"][1], f["foot_px"][0] * z["nx"] + f["foot_px"][1]
    path = [i]
    while path[-1] != foot and rec[path[-1]] >= 0 and len(path) < 1000:
        path.append(int(rec[path[-1]]))
    assert path[-1] == foot
    zf = (h + z["layers"]["lake_depth"].astype(float)).ravel()[path]  # (the water surface: the pool too)
    assert np.all(np.diff(zf) <= 0.01)
    assert -np.diff(zf).max() < 0.25 * f["height_m"]
    # the walls: cross-sections at right angles to the path climb from the floor
    t = np.linspace(0, 0.8 * f["gorge_half_km"] / res, 24)
    climbs = 0
    for k in range(1, len(r) - 2):
        dr, dc = r[k + 1] - r[k - 1], c[k + 1] - c[k - 1]
        nrm = np.hypot(dr, dc)
        for sg in (1, -1):
            rr = np.rint(r[k] - sg * dc / nrm * t).astype(int)
            cc = np.rint(c[k] + sg * dr / nrm * t).astype(int)
            prof = h[np.clip(rr, 0, z["ny"] - 1), np.clip(cc, 0, z["nx"] - 1)]
            climbs += int(np.all(np.maximum.accumulate(prof) - prof < 5.0))
    assert climbs >= 0.9 * 2 * (len(r) - 3)


def test_no_needles(fine):
    """No pixel stands more than 1.5 x a 35 degree slope above all its
    neighbours (but at the fall's face)."""
    z = fine[0]
    h = z["layers"]["elevation"].astype(float)
    res = 1000.0 * z["res"]
    p = np.pad(h, 1, mode="edge")
    gentlest = np.full_like(h, np.inf)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr or dc:
                gentlest = np.minimum(gentlest, (h - p[1 + dr:1 + dr + h.shape[0], 1 + dc:1 + dc + h.shape[1]])
                                      / (res * np.hypot(dr, dc)))
    f, = z["stats"]["falls"]
    gentlest[f["px"][0] - 2:f["px"][0] + 3, f["px"][1] - 2:f["px"][1] + 3] = 0.0
    assert gentlest.max() < 1.5 * np.tan(np.radians(35.0))


def test_volcano_keeps_its_summit(parent, fine):
    z = fine[0]
    v, = z["stats"]["volcanoes"]
    h = z["layers"]["elevation"].astype(float)
    pv = parent[0]["stats"]["volcanoes"][0]
    assert v["parent_volcano"] == 0 and v["top_m"] == pv["top_m"]
    r, c = v["summit_px"]
    assert abs(h[r, c] - pv["top_m"]) < 0.01
    near = h[max(r - 15, 0):r + 16, max(c - 15, 0):c + 16]
    assert near.max() <= pv["top_m"] + 0.01  # the summit is the highest point round it
    # the crater: the summit pixel isn't at the cone's centre, a ring round a lower floor
    rr, cc = np.mgrid[0:z["ny"], 0:z["nx"]]
    sx, sy = v["x_km"] / z["res"] + z["nx"] / 2 - 0.5, z["ny"] / 2 - v["y_km"] / z["res"] - 0.5
    centre = h[int(round(sy)), int(round(sx))]
    assert centre < pv["top_m"] - 20


def test_edge_meets_the_parent(parent, fine):
    z = fine[0]
    s = z["stats"]
    assert s["edge_max_error_m"] < 0.5
    # independently: the edge ring against the parent's bicubic surface
    pa = ZF._Parent(*parent)
    fr = z["frame"]
    n, res = z["nx"], z["res"]
    xs = (np.arange(n) + 0.5 - n / 2) * res
    edge = np.r_[[(0, j) for j in range(n)], [(n - 1, j) for j in range(n)]]
    x, y = xs[edge[:, 1]], (n / 2 - edge[:, 0] - 0.5) * res
    pr, pc = pa.coords(fr.to_sphere(x, y))
    want = pa.bicubic("elevation", pr, pc)
    got = z["layers"]["elevation"].astype(float)[edge[:, 0], edge[:, 1]]
    river = np.abs(pr - LIP[0]) < 1.0
    assert np.abs(got - want)[~river].max() < 0.5


def test_fine_of_fine(parent, fine, world):
    z1, (lat, lon) = fine
    p1 = _as_parent(z1, parent[0], lat, lon, "fine01")
    f1 = z1["stats"]["falls"][0]
    flat, flon = f1["lat"], f1["lon"]
    z2 = ZF.build(p1, world, flat, flon, size_km=4, res_km=0.025, log=lambda *a: None)
    f2, = z2["stats"]["falls"]
    h = z2["layers"]["elevation"].astype(float)
    assert f2["height_m"] == f1["height_m"] and f2["lineage"] == [0, 0]
    assert abs(h[tuple(f2["px"])] - f1["top_m"]) < 0.01
    pool = tuple(f2["pool_px"])
    assert abs(h[pool] + z2["layers"]["lake_depth"][pool] - f1["bottom_m"]) < 0.01
    assert z2["parent"]["lineage"] == ["fine01"] or z2["parent"]["lineage"][-1] == "fine01"
    assert abs(z2["stats"]["mean_elev_m"] - z2["stats"]["parent_mean_elev_m"]) < 5.0


def test_step_limit(parent):
    meta, _ = parent
    lat, lon = _at(meta, 50, 50)
    with pytest.raises(ValueError, match="at most 20x"):
        ZF.check(meta, lat, lon, 10, 0.025)  # 40x finer than 1 km
    with pytest.raises(ValueError, match="doesn't fit"):
        ZF.check(meta, *_at(meta, 2, 2), 20, 0.1)
    ZF.check(meta, lat, lon, 20, 0.05)  # 20x: allowed
    assert ZF.default_size(1.0) == (50.0, 0.1) and ZF.default_size(0.1) == (25.0, 0.05)


def _save_parent(meta, layers):
    out = S.path_of("zoom", meta["id"])
    out.mkdir(parents=True)
    specs, arrays = {}, {}
    for k, v in layers.items():
        units, desc, *enc = Z.LAYER_DOC[k]
        specs[k] = {**(enc[0] if enc else {}), "units": units, "description": desc}
        arrays[k] = S.encode(v, specs[k]) if enc else v
    m = {**meta, "created": "2026-10-16 00:00:00", "layers": S.write_layers(out, arrays, specs)}
    S.write_atomic(out / "zoom.json", json.dumps(m))
    return out


def test_save_index_and_delete_with_parent(data_root, parent, world):
    meta, layers = parent
    wpath = W.save(world, "fine test world")
    meta = {**meta, "source_world": {"id": wpath.stem, "name": "fine test world"}}
    _save_parent(meta, layers)
    lat, lon = _at(meta, 48, 53)
    out = ZF.zoom(meta["id"], lat, lon, size_km=20, res_km=0.1, log=lambda *a: None)
    m2, lay = Z.load(out, decode=True)
    assert m2["parent_zoom"]["id"] == meta["id"] and m2["source_world"]["id"] == wpath.stem
    assert lay["elevation"].shape == (200, 200)
    idx = {e["id"]: e for e in json.loads((S.zooms_dir() / "index.json").read_text())}
    assert idx[out.name]["parent_zoom"] == meta["id"] and idx[meta["id"]]["children"] == [out.name]
    # the API: a zoom as the source, sizes defaulted from the parent's resolution, the step limit
    r = api.parse_zoom_request({"zoom": meta["id"], "lat": lat, "lon": lon})
    assert (r["size_km"], r["res_km"]) == (50.0, 0.1) and "world" not in r
    with pytest.raises(api.BadRequest, match="at most 20x"):
        api.parse_zoom_request({"zoom": meta["id"], "lat": lat, "lon": lon, "res_km": 0.025})
    with pytest.raises(api.BadRequest):
        api.parse_zoom_request({"zoom": meta["id"], "world": wpath.stem, "lat": lat, "lon": lon})
    gone = S.delete("zoom", meta["id"])
    assert out in gone and not out.exists()


# --- river planform (PW-405) ------------------------------------------------
RP2, NP2 = 0.2, 150  # a 30 km parent at 200 m, its river a D8 path wandering a pixel either way


def _river_parent(kind):
    """(meta, layers) of a parent whose one river runs east across it as a
    D8 path (E, E, NE, E, E, SE, ...: the pixel-scale zigzag of a parent's
    receivers). "bedrock": 3% down a V valley in granite, 30 m^3/s;
    "alluvial": 0.02% across a 4 km wide floodplain in shale, 400 m^3/s."""
    moves = [(0, 1), (0, 1), (-1, 1), (0, 1), (0, 1), (1, 1)]
    path = [(75, 0)]
    while path[-1][1] < NP2 - 1:
        dr, dc = moves[len(path) % len(moves)]
        path.append((path[-1][0] + dr, path[-1][1] + dc))
    prow = np.array([p[0] for p in path])  # (one pixel per column)
    r, c = np.mgrid[0:NP2, 0:NP2].astype(float)
    d = np.abs(r - prow[None, :])
    if kind == "bedrock":
        bed, q, rock = 1500.0 - 0.03 * 1000 * RP2 * c, 30.0, 11
        h = bed + 40.0 * d
    else:
        bed, q, rock = 100.0 - 0.0002 * 1000 * RP2 * c, 400.0, 8
        h = bed + 0.3 * np.minimum(d, 10) + 15.0 * np.maximum(d - 10, 0)
    river = d == 0
    slot = np.where(r < prow[None, :], 6, 1).astype(np.uint8)  # (down to the river)
    for k, (pr_, pc_) in enumerate(path[:-1]):
        dr, dc = path[k + 1][0] - pr_, path[k + 1][1] - pc_
        s_ = 3 * (dr + 1) + (dc + 1)
        slot[pr_, pc_] = s_ - (s_ > 4)
    slot[path[-1]] = Z.D8_NONE
    full = np.full((NP2, NP2), 1.0)
    z0 = np.zeros((NP2, NP2))
    layers = {
        "elevation": h.astype(np.float32), "water": np.zeros((NP2, NP2), np.uint8), "lake_depth": z0,
        "lake_kind": np.zeros((NP2, NP2), np.uint8), "discharge": np.where(river, q, 0.01),
        "drainage_area": np.where(river, 2000.0, 0.04), "receiver": slot,
        "precipitation": 900 * full, "precipitation_jul": 600 * full, "precipitation_jan": 1200 * full,
        "temperature": 12 * full, "ice": z0, "tide_range": z0, "wave_power": z0,
        "rock": np.full((NP2, NP2), rock, np.uint8), "surface_rock": np.full((NP2, NP2), rock, np.uint8),
        "climate": np.full((NP2, NP2), 14, np.uint8), "biome": np.full((NP2, NP2), 3, np.uint8),
        "landform": np.zeros((NP2, NP2), np.uint8), "wetland": np.zeros((NP2, NP2), np.uint8),
        "coastal_life": np.zeros((NP2, NP2), np.uint8),
    }
    meta = {"id": f"friv{kind[:2]}", "name": "test world: river", "res_km": RP2, "nx": NP2, "ny": NP2,
            "center": {"lat": CENTRE[0], "lon": CENTRE[1]}, "size_km": NP2 * RP2,
            "source_world": {"id": "none", "name": "test world"},
            "stats": {"falls": [], "waterfalls": [], "volcanoes": []}}
    return meta, layers


def _main_river(z, qmin):
    """The fine zoom's main river, west to east: pixel (row, col)s and discharge."""
    q = z["layers"]["discharge"].ravel().astype(float)
    rec = np.asarray(z["rec"])
    col = np.arange(len(q)) % z["nx"]
    i = int(np.argmin(np.where(q >= qmin, col, 10 ** 9)))  # (its westmost pixel)
    path = [i]
    while rec[path[-1]] >= 0 and len(path) < 10 * z["nx"]:
        path.append(int(rec[path[-1]]))
    p = np.array(path)
    return np.column_stack(np.divmod(p, z["nx"])).astype(float), q[p]


@pytest.mark.parametrize("kind", ["bedrock", "alluvial"])
def test_river_planform(world, kind):
    """No grid-aligned zigzags from the parent's D8 path: a steep bedrock
    river runs straight; a gentle alluvial one meanders at ~10-14 channel
    widths, no bend tighter than ~1.5 widths (zoom_fine.planform)."""
    parent = _river_parent(kind)
    lat, lon = _at(parent[0], 75, 75)
    z = ZF.build(parent, world, lat, lon, size_km=8, res_km=0.025, log=lambda *a: None)
    pf = z["stats"]["river_planform"]
    assert pf["river_km"] > 6 and pf["switchbacks"] == 0 and pf["sharp_pct"] == 0
    xy, q = _main_river(z, 5.0)
    res = z["res"]
    k = np.arange(-4, 5)
    g = np.exp(-0.5 * (k / 2.0) ** 2)
    g /= g.sum()
    sm = np.column_stack([np.convolve(xy[:, d], g, "valid") for d in (0, 1)]) * res  # (the raster's steps)
    chord = float(np.hypot(*(sm[-1] - sm[0])))
    length = float(np.hypot(*np.diff(sm, axis=0).T).sum())
    assert chord > 7.0
    if kind == "bedrock":
        assert length / chord < 1.05
        return
    # meanders: sinuous, their wavelength from the crossings of the course's mean line
    assert 1.15 < length / chord < 2.0
    w = 4.0 * np.sqrt(np.median(q)) / 1000.0
    y = sm[:, 0] - np.polyval(np.polyfit(sm[:, 1], sm[:, 0], 2), sm[:, 1])  # (rows off a smooth mean line)
    flips = np.flatnonzero(np.diff(np.sign(y)) != 0)
    wl = 2 * (sm[flips[-1], 1] - sm[flips[0], 1]) / max(len(flips) - 1, 1)
    assert len(flips) >= 4 and 8 * w < wl < 16 * w
