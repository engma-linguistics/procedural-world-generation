"""Export a world or a regional zoom for game engines (PW-100).

    planet export <world-or-zoom-id> [--out DIR] [--res N] [--tile N] ...

Writes into one directory (default: <data root>/exports/<id>/):

  manifest.json    units, scale, sea level, projection, the layers and their
                   tiles, provenance ids (the one file an importer reads)
  legend.json      id -> name/colour for the class maps and the splat channels
  heightmap*.png   16-bit greyscale ground height: elev_m = min_m + v/65535 *
                   (max_m - min_m), the same mapping as a zoom's heightmap.png;
                   or raw little-endian .r16 with --raw (Unity / Unreal)
  ice_thickness*   16-bit, the same way: m of land ice on the ground
  water*.png       8-bit ids: 0 land, 1 sea, 2 lake
  biome*, vegetation*, rock*.png   8-bit class ids (legend.json)
  splat_0*, splat_1*.png   RGBA8 material weights, 8 materials in all (sum 255
                   on land, 0 on water); derived from tree/plant cover, ice,
                   slope, climate and wetland by simple rules (splat_weights)
  features.geojson         lon/lat points and lines
  features_local.geojson   (zooms) the same in metres from the zoom's centre,
                   with the ground height as z

Layouts: a world is resampled to an equirectangular raster (--res = width in
px, height = width / 2) and optionally the six faces of a cube (--cube N,
gnomonic); a zoom keeps its native grid (--res = km per pixel, a multiple of
the native one by block averaging). Big rasters are cut into --tile px tiles
(--overlap px shared between neighbours: use 1 for 2^n + 1 terrain tiles).

Layers are a registry (manifest layouts.<name>.layers): later layers
(PW-099's passes and harbours, PW-206's game attributes) add entries and
feature kinds without changing the format.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from . import hydrology
from . import store as S
from . import world as W
from .geo import R_KM, is_land, latlon, xyz
from .images import write_png
from .provenance import code_version

FORMAT = "procgen-export/1"
TILE = 1024
WORLD_WIDTH = 2048
RIVER_MIN_M3S = {"world": 300.0, "zoom": 10.0}  # smallest river drawn as a line

# the splat materials: channel c is splat_{c // 4}.png, RGBA component c % 4
SPLAT = (("rock", "#8b8178"), ("sand", "#e0c68a"), ("soil", "#7a5c3e"), ("grass", "#a9b964"),
         ("forest", "#3f7a3a"), ("wetland", "#4f7f6a"), ("tundra", "#9aa58a"), ("snow", "#f4f7fa"))
WATER = ({"id": 0, "name": "land", "color": "#000000"}, {"id": 1, "name": "sea", "color": "#3a6ea5"},
         {"id": 2, "name": "lake", "color": "#4f8fcf"})
CUBE_FACES = {  # axis, then the s (right) and t (down) directions of the face image
    "px": ((1, 0, 0), (0, 1, 0), (0, 0, -1)), "nx": ((-1, 0, 0), (0, -1, 0), (0, 0, -1)),
    "py": ((0, 1, 0), (-1, 0, 0), (0, 0, -1)), "ny": ((0, -1, 0), (1, 0, 0), (0, 0, -1)),
    "pz": ((0, 0, 1), (0, 1, 0), (-1, 0, 0)), "nz": ((0, 0, -1), (0, 1, 0), (1, 0, 0)),
}


# ---------------------------------------------------------------------------
# Resampling a world's cells onto pixels
# ---------------------------------------------------------------------------
class CellSampler:
    """Looks up a world's per-cell layers at unit vectors: the nearest cell
    (ids), or a smooth blend of the cell and its neighbours (heights)."""

    def __init__(self, grid, pts: np.ndarray):
        self.cell = grid.locate(np.ascontiguousarray(pts))
        off, idx = grid.nbr_off, grid.nbr_idx
        c = self.cell
        k = np.arange(6)[None, :]
        j = off[c][:, None] + k
        ok = j < off[c + 1][:, None]
        cand = np.where(ok, idx[np.minimum(j, len(idx) - 1)], c[:, None])
        self.cand = np.concatenate([c[:, None], cand], 1)
        d = np.arccos(np.clip((grid.centers[self.cand] * pts[:, None, :]).sum(2), -1, 1))
        w = np.clip(1 - d / (1.3 * grid.spacing), 0, None) ** 2
        w[:, 1:] *= ok
        self.w = w / np.maximum(w.sum(1, keepdims=True), 1e-12)

    def nearest(self, values: np.ndarray) -> np.ndarray:
        return np.asarray(values)[self.cell]

    def smooth(self, values: np.ndarray) -> np.ndarray:
        return (np.asarray(values, float)[self.cand] * self.w).sum(1)


# ---------------------------------------------------------------------------
# Derived layers
# ---------------------------------------------------------------------------
def _smooth01(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def slope_deg(elev: np.ndarray, dx_m, dy_m) -> np.ndarray:
    """Ground slope in degrees of an (ny, nx) raster, rows running south;
    dx_m, dy_m: metres per pixel across / down (scalars or arrays that
    broadcast against elev)."""
    gy = np.gradient(elev, axis=0) / dy_m
    gx = np.gradient(elev, axis=1) / dx_m
    return np.degrees(np.arctan(np.hypot(gx, gy)))


def splat_weights(slope, ice, tree, plant, precip, temp, wet, water) -> np.ndarray:
    """(ny, nx, 8) uint8 material weights (SPLAT order), summing to 255 on
    land and 0 on water. Inputs per pixel: slope (deg), ice (m), tree and
    plant cover (0..1), annual rain (mm), mean annual temperature (C), wet
    (0..1, wetland share), water (ids 0 land, 1 sea, 2 lake). Simple rules,
    not a physical model: steep ground is rock, bare ground is sand where dry
    and soil elsewhere, plants are forest by tree cover and grass (tundra
    where cold) by the rest, wetland takes its share, ice and cold bare
    ground are snow."""
    rock = _smooth01(slope, 25, 45)
    rest = 1 - rock
    tree = np.clip(tree, 0, 1)
    plant = np.clip(np.maximum(plant, tree), 0, 1)
    bare = 1 - plant
    dry = np.clip((300 - precip) / 200, 0, 1)
    cold = np.clip((5 - temp) / 5, 0, 1)
    low = plant - tree
    w = np.stack([rock, rest * bare * dry, rest * bare * (1 - dry), rest * low * (1 - cold),
                  rest * tree, np.zeros_like(rock), rest * low * cold, np.zeros_like(rock)], -1)
    wet = 0.6 * np.clip(wet, 0, 1)
    w *= (1 - wet)[..., None]
    w[..., 5] = wet
    snow = np.maximum(np.clip(ice / 5, 0, 1), _smooth01(-temp, 8, 14) * bare)
    w *= (1 - snow)[..., None]
    w[..., 7] = snow
    w /= np.maximum(w.sum(-1, keepdims=True), 1e-9)
    q = np.floor(w * 255).astype(np.int32)  # sums to 255 by giving the rest to the largest
    q[np.arange(q.shape[0])[:, None], np.arange(q.shape[1])[None, :], w.argmax(-1)] += 255 - q.sum(-1)
    q[water > 0] = 0
    return q.astype(np.uint8)


def river_lines(nxt: np.ndarray, q: np.ndarray, active: np.ndarray) -> list[dict]:
    """Rivers as polylines from a 'next node downstream' graph (a world's
    `downstream`, a zoom's `receiver`). nxt: node -> next node or -1; q:
    discharge per node; active: nodes in a river. A line runs from a source or a confluence
    to the next confluence (or the sea: the node after the last river node),
    so tributaries join the line they flow into. Returns [{nodes, q}]."""
    n = len(nxt)
    nxt = np.where(active & (nxt >= 0) & (nxt < n), nxt, -1)
    act_next = np.where(nxt >= 0, np.where(active[np.maximum(nxt, 0)], nxt, -1), -1)
    indeg = np.bincount(act_next[act_next >= 0], minlength=n)
    out = []
    for s in np.flatnonzero(active & (indeg != 1)):
        nodes = [int(s)]
        cur = int(s)
        for _ in range(n):
            nx = int(nxt[cur])
            if nx < 0:
                break
            nodes.append(nx)
            if not active[nx] or indeg[nx] != 1:
                break
            cur = nx
        if len(nodes) > 1:
            out.append({"nodes": np.array(nodes), "q": float(q[nodes[:-1]].max())})
    return out


def _path_km(ll: np.ndarray) -> float:
    p = xyz(np.radians(ll[:, 0]), np.radians(ll[:, 1]))
    return float(np.arccos(np.clip((p[:-1] * p[1:]).sum(1), -1, 1)).sum() * R_KM)


# ---------------------------------------------------------------------------
# Writing rasters
# ---------------------------------------------------------------------------
def _spans(n: int, tile: int, overlap: int) -> list[tuple[int, int]]:
    if not tile or tile >= n:
        return [(0, n)]
    step = max(tile - overlap, 1)
    out, a = [], 0
    while True:
        out.append((a, min(a + tile, n)))
        if a + tile >= n:
            return out
        a += step


class Writer:
    """Writes a raster, cut into tiles, and records the files for the manifest."""

    def __init__(self, out: Path, tile: int, overlap: int, raw: bool):
        self.out, self.tile, self.overlap, self.raw = out, tile, overlap, raw

    def write(self, name: str, arr: np.ndarray, folder: str = "") -> list[dict]:
        ys, xs = _spans(arr.shape[0], self.tile, self.overlap), _spans(arr.shape[1], self.tile, self.overlap)
        files = []
        for iy, (y0, y1) in enumerate(ys):
            for ix, (x0, x1) in enumerate(xs):
                sub = np.ascontiguousarray(arr[y0:y1, x0:x1])
                tiled = len(ys) * len(xs) > 1
                stem = name + (f"_x{ix}_y{iy}" if tiled else "")
                d = self.out / folder / (name if tiled else "")
                d.mkdir(parents=True, exist_ok=True)
                if self.raw and sub.dtype == np.uint16:
                    path = d / f"{stem}.r16"
                    path.write_bytes(sub.astype("<u2").tobytes())
                else:
                    path = d / f"{stem}.png"
                    write_png(path, sub)
                files.append({"file": path.relative_to(self.out).as_posix(), "x": x0, "y": y0,
                              "width": x1 - x0, "height": y1 - y0, "tile": [ix, iy]})
        return files


def _u16(v: np.ndarray, lo: float, hi: float) -> np.ndarray:
    return np.round(np.clip((v - lo) / (hi - lo), 0, 1) * 65535).astype(np.uint16)


def _write_products(w: Writer, P: dict, lo: float, hi: float, folder: str = "") -> dict:
    """Writes the layers of one layout; P: elevation, ice, water, biome,
    vegetation, rock, splat (ny, nx, 8). Returns the manifest's layers."""
    layers = {}
    h16 = {"format": "uint16", "elev_m": "min_m + value / 65535 * (max_m - min_m)"}
    layers["heightmap"] = {"kind": "height", "bits": 16, "units": "m", "min_m": lo, "max_m": hi,
                           "metres_per_step": round((hi - lo) / 65535, 4),
                           "sea_level_value": int(round((0 - lo) / (hi - lo) * 65535)) if lo < 0 < hi else None,
                           "description": "ground height (the true bed under ice) above sea level; " + h16["elev_m"],
                           "files": w.write("heightmap", _u16(P["elevation"], lo, hi), folder)}
    if P.get("ice") is not None and np.nanmax(P["ice"]) > 0:
        top = float(np.ceil(np.nanmax(P["ice"])))
        layers["ice_thickness"] = {"kind": "height", "bits": 16, "units": "m", "min_m": 0.0, "max_m": top,
                                   "metres_per_step": round(top / 65535, 4),
                                   "description": "land ice thickness; surface = ground + ice",
                                   "files": w.write("ice_thickness", _u16(P["ice"], 0, top), folder)}
    ids = {"water": ("water", "0 land, 1 sea, 2 lake"), "biome": ("biome", "climate.BIOMES id"),
           "vegetation": ("vegetation", "named vegetation type id (vegetation.TYPES)"),
           "rock": ("rock", "exposed rock id (surface.ROCKS)")}
    for k, (leg, desc) in ids.items():
        if P.get(k) is not None:
            layers[k] = {"kind": "ids", "bits": 8, "legend": leg, "description": desc,
                         "files": w.write(k, np.clip(P[k], 0, 255).astype(np.uint8), folder)}
    if P.get("splat") is not None:
        for i in range(2):
            layers[f"splat_{i}"] = {"kind": "rgba", "bits": 8, "legend": "splat",
                                    "channels": [SPLAT[4 * i + c][0] for c in range(4)],
                                    "description": "material weights, R G B A = " + ", ".join(
                                        SPLAT[4 * i + c][0] for c in range(4)),
                                    "files": w.write(f"splat_{i}", np.ascontiguousarray(P["splat"][..., 4 * i:4 * i + 4]),
                                                     folder)}
    return layers


# ---------------------------------------------------------------------------
# GeoJSON
# ---------------------------------------------------------------------------
def _feature(geom, props, fid):
    return {"type": "Feature", "id": fid, "geometry": geom, "properties": props}


def _collection(name, feats, extra=None):
    return {"type": "FeatureCollection", "name": name, **(extra or {}), "features": feats}


def _round(v, n=5):
    return [round(float(x), n) for x in v]


def _clean(o):
    """json-safe copy (numpy scalars and arrays to python)."""
    return json.loads(json.dumps(o, default=S.jsonable))


class Features:
    """Collects point and line features with lat/lon (and optional metre) coordinates."""

    def __init__(self, local=None, elevation=None):
        self.items = []  # (kind, geometry type, [(lat, lon)], properties)
        self.local, self.elevation = local, elevation  # callables (lat, lon arrays) -> (x, y), z

    def point(self, kind, lat, lon, **props):
        self.items.append((kind, "Point", np.array([[lat, lon]], float), props))

    def line(self, kind, latlon_arr, **props):
        self.items.append((kind, "LineString", np.asarray(latlon_arr, float), props))

    def collections(self, name: str, local_name: str | None = None):
        geo, loc = [], []
        for n, (kind, gt, ll, props) in enumerate(self.items):
            z = self.elevation(ll[:, 0], ll[:, 1]) if self.elevation else None
            p = {"kind": kind, **_clean(props)}
            if z is not None and gt == "Point":
                p["elevation_m"] = round(float(z[0]), 1)
            coords = [_round((lo, la)) for la, lo in ll]
            geo.append(_feature({"type": gt, "coordinates": coords[0] if gt == "Point" else coords}, p, f"{kind}-{n}"))
            if self.local:
                x, y = self.local(ll[:, 0], ll[:, 1])
                c = [[round(float(a * 1000), 1), round(float(b * 1000), 1), round(float(zz), 1)]
                     for a, b, zz in zip(x, y, z if z is not None else np.zeros(len(x)))]
                loc.append(_feature({"type": gt, "coordinates": c[0] if gt == "Point" else c}, p, f"{kind}-{n}"))
        out = [_collection(name, geo, {"crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}})]
        if self.local:
            out.append(_collection(local_name or name + "_local", loc, {
                "crs": {"type": "name", "properties": {"name": "local:" + self.local.crs}},
                "units": "m", "note": "coordinates [x east, y north, z ground height] in metres"}))
        return out


# ---------------------------------------------------------------------------
# World
# ---------------------------------------------------------------------------
def _world_rasters(world: dict, pts: np.ndarray, shape: tuple, dx_m, dy_m) -> dict:
    L, grid = world["layers"], world["grid"]
    sm = CellSampler(grid, pts)
    ny, nx = shape

    def smooth(k, default=0.0):
        return sm.smooth(L[k]).reshape(ny, nx) if k in L else np.full(shape, default)

    elev, ice = smooth("elevation"), smooth("ice")
    water = np.where(is_land(elev, ice), 0, 1).astype(np.uint8)
    if "lake" in L:
        water[sm.nearest(np.asarray(L["lake"]) > 0).reshape(ny, nx)] = 2
    P = {"elevation": elev, "ice": ice, "water": water}
    for k, src in (("biome", "biome"), ("vegetation", "vegetation"), ("rock", "surface_rock")):
        if src in L:
            P[k] = sm.nearest(L[src]).reshape(ny, nx)
    if "tree_cover" in L:
        P["splat"] = splat_weights(slope_deg(elev, dx_m, dy_m), ice, smooth("tree_cover") / 100,
                                   smooth("plant_cover") / 100, smooth("precipitation", 800), smooth("temperature", 10),
                                   smooth("flooded") / 100, water)
    return P


def _world_features(world: dict, path: Path, river_min: float, with_highlights: bool) -> Features:
    L, grid, meta = world["layers"], world["grid"], world["meta"]
    el = np.asarray(L["elevation"], float)
    ice = np.asarray(L.get("ice", np.zeros_like(el)), float)
    lat, lon = grid.lat, grid.lon
    feats = Features(elevation=lambda la, lo: el[grid.locate(xyz(np.radians(la), np.radians(lo)))])
    if "flow" in L and "downstream" in L:
        q = hydrology.discharge(grid, np.asarray(L["flow"], float))
        active = (q >= river_min) & is_land(el, ice)
        ll = np.stack([lat, lon], 1)
        for r in river_lines(np.asarray(L["downstream"]), q, active):
            pts = ll[r["nodes"]]
            pts[:, 1] = np.degrees(np.unwrap(np.radians(pts[:, 1])))  # (no jump over the antimeridian)
            feats.line("river", pts, discharge_m3s=round(r["q"]), length_km=round(_path_km(pts)))
    if "lake" in L or "lake_kind" in L:
        lake = np.asarray(L["lake"] if "lake" in L else L["lake_kind"]) > 0
        comps, n = grid.components(lake)
        area = 4 * np.pi * R_KM**2 / grid.n
        kinds = {1: "fresh", 2: "salt", 3: "salt pan"}
        for k in range(n):
            cells = np.flatnonzero(comps == k)
            c = grid.centers[cells].mean(0)
            la, lo = latlon(c / np.linalg.norm(c))
            props = {"area_km2": round(len(cells) * area)}
            if "lake_level" in L:
                props["level_m"] = round(float(np.mean(np.asarray(L["lake_level"])[cells])))
            if "lake_kind" in L:
                kd = np.bincount(np.asarray(L["lake_kind"])[cells].astype(int)).argmax()
                props["lake_kind"] = kinds.get(int(kd), "fresh")
            feats.point("lake", float(la), float(lo), **props)
    from . import zoom_volcanoes as ZV
    vols = ZV.table(world)
    if vols:
        for v, st in zip(vols, ZV.statuses(world, vols)):
            feats.point("volcano", v["lat"], v["lon"], status=st, form=ZV.form(v), summit_m=round(v["top_m"]),
                        height_m=round(v["height_m"]), radius_km=round(v["radius_km"], 1),
                        age_myr=round(v["age"], 1), volcano_type="arc" if v["kind"] == 0 else "hotspot")
    if with_highlights:
        from . import highlights as H
        try:
            hl = H.for_world(path)
        except Exception as e:  # (a world a detector can't handle still exports)
            print(f"  highlights skipped: {e}")
            hl = {"features": []}
        for f in hl["features"]:
            feats.point("highlight", f["lat"], f["lon"], highlight_kind=f["kind"], category=f["category"],
                        title=f["title"], blurb=f.get("blurb"), score=f.get("score"), size_km=f.get("size_km"),
                        stats=f.get("stats"))
    return feats


def export_world(path: Path, out: Path, res: int | None, tile: int, overlap: int, cube: int, raw: bool,
                 height_range, river_min: float | None, with_highlights: bool, log) -> dict:
    world = W.load(path)
    meta = world["meta"]
    width = int(res or WORLD_WIDTH)
    height = max(width // 2, 1)
    wr = Writer(out, tile, overlap, raw)
    lon = -180 + (np.arange(width) + 0.5) * 360 / width
    lat = 90 - (np.arange(height) + 0.5) * 180 / height
    LON, LAT = np.meshgrid(np.radians(lon), np.radians(lat))
    pts = xyz(LAT.ravel(), LON.ravel())
    dy = R_KM * 1000 * np.radians(180 / height)
    dx = np.maximum(R_KM * 1000 * np.cos(np.radians(lat)) * np.radians(360 / width), 1.0)[:, None]
    log(f"  equirectangular {width}x{height}")
    P = _world_rasters(world, pts, (height, width), dx, dy)
    lo, hi = _height_range(P["elevation"], height_range)
    layouts = {"equirect": {
        "type": "equirectangular", "width": width, "height": height, "deg_per_px": 360 / width,
        "m_per_px_equator": round(2 * np.pi * R_KM * 1000 / width, 1), "m_per_px_meridian": round(dy, 1),
        "lon_range": [-180, 180], "lat_range": [-90, 90], "row0": "north", "col0": "west (-180)",
        "pixel_lon": "-180 + (col + 0.5) * deg_per_px", "pixel_lat": "90 - (row + 0.5) * deg_per_px",
        "tile": tile, "overlap": overlap,
        "layers": _write_products(wr, P, lo, hi)}}
    if cube:
        log(f"  cube faces {cube}x{cube}")
        s = (np.arange(cube) + 0.5) / cube * 2 - 1
        S_, T_ = np.meshgrid(s, s)
        faces = {}
        base = 2 * R_KM * 1000 / cube  # metres per pixel at a face's centre
        for fname, (a, u, v) in CUBE_FACES.items():
            vec = np.array(a)[None] + S_.ravel()[:, None] * np.array(u) + T_.ravel()[:, None] * np.array(v)
            vec /= np.linalg.norm(vec, axis=1, keepdims=True)
            scale = base / (1 + S_**2 + T_**2)  # (the gnomonic pixel shrinks towards the corners)
            Pf = _world_rasters(world, vec, (cube, cube), scale, scale)
            faces[fname] = _write_products(wr, Pf, lo, hi, f"cube/{fname}")
        layouts["cube"] = {"type": "cube_gnomonic", "size": cube, "tile": tile, "overlap": overlap,
                           "m_per_px_face_centre": round(base, 1),
                           "faces": {k: {"axis": list(CUBE_FACES[k][0]), "right": list(CUBE_FACES[k][1]),
                                         "down": list(CUBE_FACES[k][2])} for k in CUBE_FACES},
                           "pixel_dir": "normalize(axis + s * right + t * down), s, t = (px + 0.5) / size * 2 - 1",
                           "z_axis": "north pole; x through (0N, 0E), y through (0N, 90E)",
                           "layers_by_face": faces}
    feats = _world_features(world, path, river_min if river_min is not None else RIVER_MIN_M3S["world"],
                            with_highlights)
    geo, = feats.collections(f"{path.stem} features")
    (out / "features.geojson").write_text(json.dumps(geo))
    counts = _kind_counts(feats)
    return {"kind": "world", "id": path.stem, "layouts": layouts, "height": (lo, hi), "features": {
        "geojson": "features.geojson", "counts": counts, "crs": "WGS84 lon/lat, degrees; point elevation_m = ground height"},
        "source": {"world": {"id": path.stem, "name": world.get("name"), "source_run": meta.get("source_run"),
                             "t_myr": meta.get("t_myr"), "level": meta.get("level"), "seed": meta.get("seed"),
                             "created": meta.get("created")}},
        "sea_level_m": 0.0, "eustatic_sea_level_m": meta.get("sea_level_m"), "global_temp_c": meta.get("global_temp_c")}


def _kind_counts(feats: Features) -> dict:
    c: dict = {}
    for kind, *_ in feats.items:
        c[kind] = c.get(kind, 0) + 1
    return c


def _height_range(elev: np.ndarray, rng) -> tuple[float, float]:
    if rng:
        lo, hi = float(rng[0]), float(rng[1])
    else:
        lo, hi = float(np.floor(np.nanmin(elev))), float(np.ceil(np.nanmax(elev)))
    return lo, max(hi, lo + 1)


# ---------------------------------------------------------------------------
# Zoom
# ---------------------------------------------------------------------------
def _block(a: np.ndarray, f: int, categorical: bool) -> np.ndarray:
    if f == 1:
        return a
    ny, nx = a.shape[0] // f * f, a.shape[1] // f * f
    a = a[:ny, :nx]
    if categorical:
        return a[f // 2::f, f // 2::f]
    return a.reshape(ny // f, f, nx // f, f).mean((1, 3))


def export_zoom(d: Path, out: Path, res: float | None, tile: int, overlap: int, raw: bool, height_range,
                river_min: float | None, with_highlights: bool, log) -> dict:
    from . import zoom as Z
    meta, L = Z.load(d, decode=True)
    nat = float(meta["res_km"])
    f = max(int(round((res or nat) / nat)), 1)
    cat = ("water", "biome", "vegetation", "surface_rock", "rock", "lake_kind", "wetland")
    A = {k: _block(np.asarray(v), f, k in cat) for k, v in L.items()
         if np.asarray(v).ndim == 2}
    ny, nx = A["elevation"].shape
    r_km = nat * f
    log(f"  native grid, {nx}x{ny} px at {r_km:g} km" + (f" (block {f}x{f})" if f > 1 else ""))
    el = A["elevation"].astype(float)
    water = A.get("water", np.where(el > 0, 0, 1)).astype(np.uint8)
    P = {"elevation": el, "ice": A.get("ice"), "water": water, "biome": A.get("biome"),
         "vegetation": A.get("vegetation"), "rock": A.get("surface_rock")}
    if "tree_cover" in A:
        P["splat"] = splat_weights(
            slope_deg(el, r_km * 1000, r_km * 1000), np.asarray(A.get("ice", 0 * el), float),
            A["tree_cover"] / 100, A.get("plant_cover", A["tree_cover"]) / 100, A.get("precipitation", 800 + 0 * el),
            A.get("temperature", 10 + 0 * el), (A["wetland"] > 0).astype(float) if "wetland" in A else 0 * el, water)
    lo, hi = _height_range(el, height_range)
    wr = Writer(out, tile, overlap, raw)
    layout = {"type": "azimuthal_equidistant_native", "width": nx, "height": ny, "m_per_px": r_km * 1000,
              "native_m_per_px": nat * 1000, "size_km": meta["size_km"], "row0": "north", "col0": "west",
              "pixel_x_m": "(col + 0.5 - width/2) * m_per_px   (east of centre)",
              "pixel_y_m": "(height/2 - row - 0.5) * m_per_px   (north of centre)",
              "tile": tile, "overlap": overlap, "layers": _write_products(wr, P, lo, hi)}
    # features
    fr = Z.Frame(meta["center"]["lat"], meta["center"]["lon"])
    def to_xy(la, lo_):
        return fr.to_plane(xyz(np.radians(np.asarray(la)), np.radians(np.asarray(lo_))))

    def ground(la, lo_):
        x, y = to_xy(la, lo_)
        c = np.clip(x / r_km + nx / 2 - 0.5, 0, nx - 1)
        r = np.clip(ny / 2 - 0.5 - y / r_km, 0, ny - 1)
        c0, r0 = np.minimum(c.astype(int), nx - 2), np.minimum(r.astype(int), ny - 2)
        fc, fr_ = c - c0, r - r0
        e = el
        return ((e[r0, c0] * (1 - fc) + e[r0, c0 + 1] * fc) * (1 - fr_)
                + (e[r0 + 1, c0] * (1 - fc) + e[r0 + 1, c0 + 1] * fc) * fr_)

    def local(la, lo_):
        return to_xy(la, lo_)
    local.crs = f"azimuthal_equidistant(lat0={meta['center']['lat']},lon0={meta['center']['lon']},R_km={R_KM})"
    feats = Features(local=local, elevation=ground)

    def pix_ll(idx, w=nx, h=ny, step=r_km):
        r, c = np.divmod(np.asarray(idx), w)
        x, y = (c + 0.5 - w / 2) * step, (h / 2 - r - 0.5) * step
        return np.stack(latlon(fr.to_sphere(x, y)), 1)

    if "receiver" in L:  # (rivers follow the native grid's routing, whatever --res)
        h0, w0 = L["elevation"].shape
        q = np.asarray(L["discharge"], float).ravel()
        rec = np.asarray(L["receiver"]).ravel()
        rr, cc = np.divmod(np.arange(h0 * w0), w0)
        k = np.where(rec < 4, rec, rec + 1).astype(int)
        nr, nc = rr + k // 3 - 1, cc + k % 3 - 1
        ok = (rec != 255) & (nr >= 0) & (nr < h0) & (nc >= 0) & (nc < w0)
        nxt = np.where(ok, nr * w0 + nc, -1)
        land0 = np.asarray(L["water"]).ravel() == 0 if "water" in L else np.asarray(L["elevation"]).ravel() > 0
        active = (q >= (river_min if river_min is not None else RIVER_MIN_M3S["zoom"])) & land0
        for r in river_lines(nxt, q, active):
            pts = pix_ll(r["nodes"], w0, h0, nat)
            pts[:, 1] = np.degrees(np.unwrap(np.radians(pts[:, 1])))
            feats.line("river", pts, discharge_m3s=round(r["q"], 1), length_km=round(_path_km(pts), 2))
    st = meta.get("stats", {})
    for fl in st.get("falls", []):
        feats.point("waterfall", fl["lat"], fl["lon"], height_m=fl["height_m"], discharge_m3s=fl["discharge_m3s"],
                    fall_kind=fl["kind"], length_km=fl.get("length_km"), from_lake=fl.get("from_lake"),
                    gorge_km=fl.get("gorge_km"), plunge_pool_m=fl.get("plunge_pool_m"))
    for v in st.get("volcanoes", []):
        feats.point("volcano", v["lat"], v["lon"], status=v.get("status"), form=v.get("form"),
                    summit_m=v.get("top_m"), height_m=v.get("height_m"), age_myr=v.get("age_myr"),
                    volcano_type=v.get("kind"), minor=bool(v.get("minor")))
    for dl in st.get("deltas", []):
        la, lo_ = dl["lat_lon"]
        feats.point("delta", la, lo_, delta_type=dl["type"], discharge_m3s=dl["discharge_m3s"],
                    plain_radius_km=dl["plain_radius_km"], weights=dl["weights"])
    _zoom_lakes(feats, A, nx, ny, r_km, pix_ll)
    if with_highlights:
        _zoom_highlights(feats, meta, fr, ground, to_xy)
    geo, loc = feats.collections(f"{meta['id']} features", f"{meta['id']} features (local)")
    (out / "features.geojson").write_text(json.dumps(geo))
    (out / "features_local.geojson").write_text(json.dumps(loc))
    sw = meta["source_world"]
    return {"kind": "zoom", "id": meta["id"], "layouts": {"native": layout}, "height": (lo, hi), "features": {
        "geojson": "features.geojson", "local_geojson": "features_local.geojson", "counts": _kind_counts(feats),
        "crs": "WGS84 lon/lat, degrees; point elevation_m = ground height",
        "local_crs": local.crs + ", metres"},
        "source": {"zoom": {"id": meta["id"], "name": meta.get("name"), "created": meta.get("created"),
                            "seed": meta.get("seed"), "center": meta["center"], "size_km": meta["size_km"],
                            "res_km": nat, "params": meta.get("params"), "format": meta.get("format")},
                   "world": sw},
        "projection": {**{k: meta["projection"][k] for k in ("type", "lat0", "lon0", "planet_radius_km",
                                                              "corners_latlon")}, "x": "east, m", "y": "north, m"},
        "sea_level_m": 0.0}


def _zoom_lakes(feats: Features, A: dict, nx: int, ny: int, r_km: float, pix_ll) -> None:
    """One point per lake: the centroid of each connected group of lake pixels."""
    if "water" not in A or not (A["water"] == 2).any():
        return
    from collections import deque
    m = A["water"] == 2
    seen = np.zeros_like(m)
    for r0, c0 in zip(*np.nonzero(m)):
        if seen[r0, c0]:
            continue
        seen[r0, c0] = True
        todo, cells = deque([(r0, c0)]), []
        while todo:
            r, c = todo.popleft()
            cells.append(r * nx + c)
            for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= rr < ny and 0 <= cc < nx and m[rr, cc] and not seen[rr, cc]:
                    seen[rr, cc] = True
                    todo.append((rr, cc))
        cells = np.array(cells)
        rows, cols = np.divmod(cells, nx)
        mid = pix_ll(np.array([int(np.round(rows.mean())) * nx + int(np.round(cols.mean()))]))[0]
        props = {"area_km2": round(len(cells) * r_km**2, 2)}
        if "lake_depth" in A:
            props["max_depth_m"] = round(float(A["lake_depth"].ravel()[cells].max()), 1)
            props["level_m"] = round(float((A["elevation"].ravel()[cells] + A["lake_depth"].ravel()[cells]).max()), 1)
        if "lake_kind" in A:
            props["lake_kind"] = {1: "fresh", 2: "salt", 3: "salt pan"}.get(int(np.bincount(
                A["lake_kind"].ravel()[cells].astype(int)).argmax()), "fresh")
        feats.point("lake", float(mid[0]), float(mid[1]), **props)


def _zoom_highlights(feats: Features, meta: dict, fr, ground, to_xy) -> None:
    """The source world's highlights inside the zoom's square, if it has them cached."""
    from . import highlights as H
    wid = meta["source_world"]["id"]
    if not S.exists("world", wid):
        return
    hl = H.cached(S.path_of("world", wid))
    if not hl:
        return
    half = meta["size_km"] / 2
    for f in hl["features"]:
        x, y = to_xy([f["lat"]], [f["lon"]])
        if abs(x[0]) <= half and abs(y[0]) <= half and np.dot(fr.c, xyz(np.radians(f["lat"]), np.radians(f["lon"]))) > 0:
            feats.point("highlight", f["lat"], f["lon"], highlight_kind=f["kind"], category=f["category"],
                        title=f["title"], blurb=f.get("blurb"), score=f.get("score"), stats=f.get("stats"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def exports_dir() -> Path:
    return S.root() / "exports"


def resolve(ref: str) -> tuple[str, Path]:
    """('world' | 'zoom', path) for 'world:<id>', 'zoom:<id>' or a bare id."""
    kind, _, item = str(ref).rpartition(":")
    kinds = [kind] if kind else [k for k in S.kinds_of(item) if k in ("world", "zoom")]
    if kind and kind not in ("world", "zoom"):
        raise SystemExit(f"{ref}: only a world or a zoom can be exported")
    if not kinds:
        raise SystemExit(f"no world or zoom {item!r} (see: uv run python -m planet list)")
    if len(kinds) > 1:
        raise SystemExit(f"{item}: there is a world and a zoom with this id; say world:{item} or zoom:{item}")
    return kinds[0], S.find(kinds[0], item)


def export(ref: str, out: str | Path | None = None, *, res: float | None = None, tile: int = TILE, overlap: int = 0,
           cube: int = 0, raw: bool = False, height_range: tuple[float, float] | None = None,
           river_min: float | None = None, highlights: bool = True, log=print) -> Path:
    """Exports a world or zoom (id, 'world:<id>' / 'zoom:<id>') to the directory `out`
    (default: <data root>/exports/<id>); returns it. See the module docstring."""
    kind, path = resolve(ref)
    if kind == "zoom" and cube:
        raise SystemExit("--cube is for worlds; a zoom keeps its native grid")
    item = path.stem if kind == "world" else path.name
    out = Path(out) if out else exports_dir() / item
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    log(f"exporting {kind} {item} -> {out}")
    args = (tile, overlap)
    if kind == "world":
        r = export_world(path, out, int(res) if res else None, *args, cube, raw, height_range, river_min, highlights, log)
    else:
        r = export_zoom(path, out, res, *args, raw, height_range, river_min, highlights, log)
    lo, hi = r.pop("height")
    legend = S.legends()
    leg = {"water": list(WATER), "biome": legend["biomes"], "vegetation": legend["vegetation"]["types"],
           "rock": legend["rocks"],
           "splat": [{"channel": i, "file": f"splat_{i // 4}", "component": "RGBA"[i % 4], "name": n, "color": c}
                     for i, (n, c) in enumerate(SPLAT)]}
    (out / "legend.json").write_text(json.dumps(leg, indent=1))
    manifest = {
        "format": FORMAT, **r,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"), "generated_in_s": round(time.time() - t0, 1),
        "units": {"height": "m", "distance": "m", "discharge": "m^3/s", "area": "km^2", "angle": "degrees",
                  "temperature": "C"},
        "scale": {"planet_radius_km": R_KM, "vertical_exaggeration": 1.0},
        "height_range_m": [lo, hi], "legend": "legend.json",
        "provenance": {"exporter": code_version(), "args": {"res": res, "tile": tile, "overlap": overlap, "cube": cube,
                                                            "raw": raw, "river_min_m3s": river_min}},
        "reserved": "Further layers (PW-099 human-use layers, PW-206 game attributes) are added as new entries of "
                    "layouts.<name>.layers and new feature kinds, not new top-level keys.",
    }
    (out / "manifest.json").write_text(json.dumps(_clean(manifest), indent=1))
    log(f"  {len(list(out.rglob('*')))} files, {r['features']['counts']}")
    return out


def _all_layers(layouts: dict):
    for lay in layouts.values():
        yield from lay.get("layers", {}).values()
        for fl in lay.get("layers_by_face", {}).values():
            yield from fl.values()
