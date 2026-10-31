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
  travel*, sightline*, grazing*, foraging*, timber*, fuel*, building*, mud_months*,
  fire_months*, green_months*, hazards*.png   game attributes of the plants and soils
                   (PW-206, gameattrs.py): value = stored x the layer's scale; masks 16-bit
  river_nav*, harbour*, pass*, fertile*, fresh_water*.png   8-bit human-use class ids
                   (PW-099, humanuse.py; legend.json); features.geojson gets the kinds
                   navigable_river, harbour, pass, spring and (worlds) fertile_land
  splat_0*, splat_1*.png   RGBA8 material weights, 8 materials in all (sum 255
                   on land, 0 on water); derived from tree/plant cover, ice,
                   slope, climate and wetland by simple rules (splat_weights)
  features.geojson         lon/lat points, lines (rivers with Strahler order, width, per-vertex
                   discharge) and polygons (lake outlines)
  features_local.geojson   (zooms) the same in metres from the zoom's centre,
                   with the ground height as z

Projected maps (PW-477): --projection {equirect, equal-earth, mollweide, laea, aeqd,
ortho, stereo}, --center lat,lon (any latitude: the whole-world projections are used
obliquely) and --extent (e.g. 2000km, 30deg, 3000x2000km) replace the layout by one
square-pixel map "layouts.map" (planet/projection.py): heights blend smoothly, class
maps take the nearest cell, pixels off the globe / outline / extent are nodata (a
`coverage` layer, heights 0, ids 255; the manifest says so), and features_map.geojson
holds the features in map metres.

Layouts: a world is resampled to an equirectangular raster (--res = width in
px, height = width / 2) and optionally the six faces of a cube (--cube N,
gnomonic); a zoom keeps its native grid (--res = km per pixel, a multiple of
the native one by block averaging). Big rasters are cut into --tile px tiles
(--overlap px shared between neighbours: use 1 for 2^n + 1 terrain tiles).

Layers are a registry (manifest layouts.<name>.layers): later layers add entries
and feature kinds without changing the format.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from . import gameattrs as GA
from . import humanuse as HU
from . import hydrology
from . import projection as PJ
from . import store as S
from . import world as W
from .geo import R_KM, arc, arc_km, cell_area_km2, is_land, latlon, smoothstep, world_land, xyz
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
        d = arc((grid.centers[self.cand] * pts[:, None, :]).sum(2))
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
    rock = smoothstep(25, 45, slope)
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
    snow = np.maximum(np.clip(ice / 5, 0, 1), smoothstep(8, 14, -temp) * bare)
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
    order = strahler_order(act_next, active)
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
            out.append({"nodes": np.array(nodes), "q": float(q[nodes[:-1]].max()), "q_nodes": q[nodes].astype(float),
                        "order": int(order[s])})
    return out


def strahler_order(act_next: np.ndarray, active: np.ndarray) -> np.ndarray:
    """Strahler stream order per node of a river forest (act_next: the next active node
    downstream or -1; active: nodes in a river). Sources are 1; where two or more streams of the
    highest incoming order meet the order goes up by one, otherwise it is that highest order.
    Processed in rounds from the sources down (nodes in a cycle, which a routing graph does not
    have, would stay 1)."""
    n = len(act_next)
    order = np.ones(n, int)
    rem = np.bincount(act_next[act_next >= 0], minlength=n)  # children not yet processed
    mx = np.zeros(n, int)  # highest order among processed children
    cnt = np.zeros(n, int)  # how many children have it
    ready = np.flatnonzero(active & (rem == 0))
    while len(ready):
        order[ready] = np.where(mx[ready] == 0, 1, mx[ready] + (cnt[ready] >= 2))
        has = act_next[ready] >= 0
        c, p = ready[has], act_next[ready[has]]
        if not len(c):
            break
        o = order[c]
        up = np.unique(p)
        old = mx[up].copy()
        np.maximum.at(mx, p, o)
        cnt[up[mx[up] > old]] = 0
        np.add.at(cnt, p[o == mx[p]], 1)
        np.add.at(rem, p, -1)
        ready = up[rem[up] == 0]
    return order


def river_width_m(q) -> np.ndarray:
    """Bankfull width from discharge, w = 7.2 Q^0.5 (Leopold-Maddock-style hydraulic geometry;
    the Rhine at Cologne, ~2,200 m3/s, comes out near 340 m). A guide for drawing, not a survey."""
    return 7.2 * np.sqrt(np.maximum(np.asarray(q, float), 0.0))


def _river_props(r: dict, pts: np.ndarray, qd: int) -> dict:
    """GeoJSON properties of a river line: peak discharge, Strahler order, bankfull width at the
    peak, and the discharge at each vertex (the river widens along the line as tributaries join)."""
    return {"discharge_m3s": round(r["q"], qd) if qd else round(r["q"]), "strahler": r["order"],
            "width_m": round(float(river_width_m(r["q"])), 1), "length_km": round(_path_km(pts), 2),
            "vertex_discharge_m3s": [round(float(v), qd) if qd else round(float(v)) for v in r["q_nodes"]]}


# ---------------------------------------------------------------------------
# Lake outlines
# ---------------------------------------------------------------------------
def boundary_rings(a: np.ndarray, b: np.ndarray) -> list[list[int]]:
    """Closed rings (vertex ids, first not repeated) from the boundary edges (a[i], b[i]) of a
    region made of cells: every vertex has two boundary edges, four where two cells touch at a
    corner (the walk then just takes the next unused edge there)."""
    adj: dict[int, list[int]] = {}
    for i, (u, v) in enumerate(zip(a.tolist(), b.tolist())):
        adj.setdefault(u, []).append(i)
        adj.setdefault(v, []).append(i)
    used = np.zeros(len(a), bool)
    rings = []
    for i0 in range(len(a)):
        if used[i0]:
            continue
        ring, cur, ei = [int(a[i0])], int(b[i0]), i0
        used[i0] = True
        while cur != ring[0]:
            ring.append(cur)
            nxt = next((j for j in adj[cur] if not used[j]), None)
            if nxt is None:
                break
            used[nxt] = True
            cur = int(b[nxt] if a[nxt] == cur else a[nxt])
        if len(ring) >= 3:
            rings.append(ring)
    return rings


def lake_polygon(rings_ll: list[np.ndarray]) -> list[np.ndarray]:
    """GeoJSON-ready rings (lon, lat) from boundary rings of (lat, lon): longitudes unwrapped
    (no jump over the antimeridian), the largest ring is the shore (counter-clockwise) and the
    rest are islands (clockwise holes), each closed by repeating its first vertex."""
    out = []
    for ll in rings_ll:
        lon = np.degrees(np.unwrap(np.radians(ll[:, 1])))
        xy = np.stack([lon * np.cos(np.radians(ll[:, 0].mean())), ll[:, 0]], 1)
        area = 0.5 * float(np.sum(xy[:, 0] * np.roll(xy[:, 1], -1) - np.roll(xy[:, 0], -1) * xy[:, 1]))
        out.append((abs(area), area, np.stack([ll[:, 0], lon], 1)))
    out.sort(key=lambda t: -t[0])
    rings = []
    for k, (_, area, ll) in enumerate(out):
        if (area > 0) != (k == 0):  # outer CCW, holes CW (RFC 7946)
            ll = ll[::-1]
        rings.append(np.vstack([ll, ll[:1]]))
    return rings

def _path_km(ll: np.ndarray) -> float:
    p = xyz(np.radians(ll[:, 0]), np.radians(ll[:, 1]))
    return float(arc((p[:-1] * p[1:]).sum(1)).sum() * R_KM)


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


def _u16(v: np.ndarray, lo: float, hi: float, valid: np.ndarray | None = None) -> np.ndarray:
    """16-bit encoding; with `valid` (a projected map), pixels outside it are 0 = nodata and
    data are at least 1 (a cost of one step at the bottom of the range)."""
    q = np.round(np.clip(np.nan_to_num(v - lo) / (hi - lo), 0, 1) * 65535).astype(np.uint16)
    return q if valid is None else np.where(valid, np.maximum(q, 1), 0).astype(np.uint16)


NODATA_ID = 255  # (class-map ids in a projected map: off-globe pixels)


def _write_products(w: Writer, P: dict, lo: float, hi: float, folder: str = "", valid: np.ndarray | None = None) -> dict:
    """Writes the layers of one layout; P: elevation, ice, water, biome,
    vegetation, rock, splat (ny, nx, 8). `valid` (ny, nx bool): the pixels a
    projected map covers; the others are nodata (heights 0, ids 255, splat all
    0, plus a `coverage` layer). Returns the manifest's layers."""
    layers = {}
    nd = {} if valid is None else {"nodata": 0}
    h16 = {"format": "uint16", "elev_m": "min_m + value / 65535 * (max_m - min_m)"}
    layers["heightmap"] = {"kind": "height", "bits": 16, "units": "m", "min_m": lo, "max_m": hi,
                           "metres_per_step": round((hi - lo) / 65535, 4),
                           "sea_level_value": int(round((0 - lo) / (hi - lo) * 65535)) if lo < 0 < hi else None,
                           "description": "ground height (the true bed under ice) above sea level; " + h16["elev_m"],
                           **nd, "files": w.write("heightmap", _u16(P["elevation"], lo, hi, valid), folder)}
    ice_ok = P.get("ice") is not None and (valid is None or valid.any())
    if ice_ok and np.nanmax(P["ice"] if valid is None else P["ice"][valid]) > 0:
        top = float(np.ceil(np.nanmax(P["ice"] if valid is None else P["ice"][valid])))
        layers["ice_thickness"] = {"kind": "height", "bits": 16, "units": "m", "min_m": 0.0, "max_m": top,
                                   "metres_per_step": round(top / 65535, 4),
                                   "description": "land ice thickness; surface = ground + ice",
                                   **nd, "files": w.write("ice_thickness", _u16(P["ice"], 0, top, valid), folder)}
    ids = {"water": ("water", "0 land, 1 sea, 2 lake"), "biome": ("biome", "climate.BIOMES id"),
           "vegetation": ("vegetation", "named vegetation type id (vegetation.TYPES)"),
           "rock": ("rock", "exposed rock id (surface.ROCKS)"),
           # human-use class maps (humanuse.py, PW-099); the legend is legend.json's key of the same name
           "river_nav": ("river_nav", "navigable rivers: 0 no, 1 small boats, 2 barges, 3 sea-going"),
           "harbour": ("harbour", "natural harbours at sea: 0 none, 1 anchorage, 2 harbour, 3 fine harbour"),
           "pass": ("pass", "mountain pass at the saddle: 1 open most of the year, 2 seasonal, 3 snow-bound"),
           "fertile": ("fertile", "farmland: 0 not arable .. 4 prime"),
           "fresh_water": ("fresh_water", "reach of perennial fresh water: 3 on site .. 0 none")}
    for k, (leg, desc) in ids.items():
        if P.get(k) is not None:
            ids = np.clip(P[k], 0, NODATA_ID - 1).astype(np.uint8)
            if valid is not None:
                ids = np.where(valid, ids, NODATA_ID).astype(np.uint8)
            layers[k] = {"kind": "ids", "bits": 8, "legend": leg, "description": desc,
                         **({} if valid is None else {"nodata": NODATA_ID}), "files": w.write(k, ids, folder)}
    # game attributes (gameattrs.py, PW-206): stored integers, value = stored x scale; masks 16-bit, bit 0 = January
    for k in GA.NAMES:
        if P.get(k) is not None:
            dt, sc, units, desc = GA.LAYER_SPECS[k]
            big = dt != "u1"
            v = np.clip(np.round(np.nan_to_num(np.asarray(P[k], float)) / sc), 0, 65535 if big else 255)
            layers[k] = {"kind": "mask" if units == "mask" else "scalar", "bits": 16 if big else 8, "units": units,
                         "scale": sc, "value": f"stored x {sc}" if sc != 1 else "stored", "description": desc,
                         **({"legend": "game.hazards"} if k == "hazards" else {}),
                         **({} if valid is None else {"nodata": "see coverage"}),
                         "files": w.write(k, v.astype(np.uint16 if big else np.uint8), folder)}
    if P.get("splat") is not None:
        for i in range(2):
            layers[f"splat_{i}"] = {"kind": "rgba", "bits": 8, "legend": "splat",
                                    "channels": [SPLAT[4 * i + c][0] for c in range(4)],
                                    "description": "material weights, R G B A = " + ", ".join(
                                        SPLAT[4 * i + c][0] for c in range(4)),
                                    **({} if valid is None else {"nodata": "all four channels 0 (also 0 on water)"}),
                                    "files": w.write(f"splat_{i}", np.ascontiguousarray(
                                        P["splat"][..., 4 * i:4 * i + 4] * (1 if valid is None else valid[..., None])),
                                        folder)}
    if valid is not None:
        layers["coverage"] = {"kind": "ids", "bits": 8, "description": "255 where the map covers the planet, 0 off it "
                              "(off the globe / outline, or outside --extent): the nodata pixels of every layer",
                              "files": w.write("coverage", np.where(valid, 255, 0).astype(np.uint8), folder)}
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


# Lines and polygons that cross the antimeridian (PW-533). Coordinates come in (lon, lat) with
# longitudes possibly unwrapped past +-180; they leave as RFC 7946 section 3.1.9 wants: split at
# the 180th meridian, both sides with the exact +-180 endpoint.
PER_VERTEX_KEYS = ("vertex_discharge_m3s",)  # per-vertex lists in river properties


def _window(lon):
    """The 360-degree window [-180, 180) + 360k a longitude falls in: k."""
    return np.floor((np.asarray(lon, float) + 180.0) / 360.0).astype(int)


def _antimeridian_line(lonlat, per_vertex):
    """Parts of a line: [(coords [[lon, lat], ...] with lon in [-180, 180], {key: values})].
    One part unless the line crosses the antimeridian; then a part ends and the next begins at
    the crossing (latitude interpolated, lon exactly +-180). Per-vertex values interpolate
    linearly the same way (the crossing vertex is in both parts)."""
    lon, lat = lonlat[:, 0], lonlat[:, 1]
    win = _window(lon)
    keys = list(per_vertex)
    V = {k: np.asarray(per_vertex[k], float) for k in keys}
    segs = [(int(win[0]), [])]
    for i in range(len(lon)):
        if i and win[i] != win[i - 1]:
            K = max(win[i], win[i - 1])
            b = 360.0 * K - 180.0  # the meridian crossed, unwrapped
            t = (b - lon[i - 1]) / (lon[i] - lon[i - 1])
            lat_c = lat[i - 1] + t * (lat[i] - lat[i - 1])
            vc = {k: V[k][i - 1] + t * (V[k][i] - V[k][i - 1]) for k in keys}
            segs[-1][1].append((b - 360.0 * win[i - 1], lat_c, vc))
            segs.append((int(win[i]), [(b - 360.0 * win[i], lat_c, vc)]))
        segs[-1][1].append((lon[i] - 360.0 * win[i], lat[i], {k: V[k][i] for k in keys}))
    parts = []
    for _, pts in segs:
        if len(pts) < 2:
            continue
        coords = [_round((x, y)) for x, y, _ in pts]
        vals = {}
        for k in keys:
            orig = per_vertex[k]
            as_int = all(isinstance(v, int) for v in orig)
            vals[k] = [round(float(v[k])) if as_int else round(float(v[k]), 1) for _, _, v in pts]
        parts.append((coords, vals))
    return parts


def _clip_halfplane(ring, x0, keep_ge):
    """Sutherland-Hodgman against the meridian lon = x0 (open ring of (lon, lat))."""
    out, m = [], len(ring)
    inside = (lambda x: x >= x0) if keep_ge else (lambda x: x <= x0)
    for i in range(m):
        p, q = ring[i], ring[(i + 1) % m]
        pin, qin = inside(p[0]), inside(q[0])
        if pin:
            out.append(p)
        if pin != qin:
            t = (x0 - p[0]) / (q[0] - p[0])
            c = p + t * (q - p)
            c[0] = x0
            out.append(c)
    return np.array(out).reshape(-1, 2)


def _antimeridian_polygons(rings):
    """Rings (closed, (lon, lat), outer first, holes after; longitudes may run past +-180) as
    polygons [[ring, ...], ...] with lon in [-180, 180]: one polygon, or several where the
    outline crosses the antimeridian (the pieces are clipped against the meridian, so a shared
    edge runs along it; a hole crossing it is cut the same way)."""
    opened = [np.asarray(r, float)[:-1] for r in rings]
    lon_all = np.concatenate([r[:, 0] for r in opened])
    polys = []
    for k in range(int(_window(lon_all.min())), int(_window(lon_all.max())) + 1):
        x0, x1 = 360.0 * k - 180.0, 360.0 * k + 180.0
        clipped = [_clip_halfplane(_clip_halfplane(r, x0, True), x1, False) for r in opened]
        if len(clipped[0]) < 3 or not abs(_area(clipped[0])) > 1e-12:
            continue
        poly = []
        for c in clipped:
            if len(c) >= 3 and abs(_area(c)) > 1e-12:
                c = c - np.array([360.0 * k, 0.0])
                poly.append([_round(p) for p in np.vstack([c, c[:1]])])
        polys.append(poly)
    return polys


def _area(ring):
    x, y = ring[:, 0], ring[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


class Features:
    """Collects point and line features with lat/lon (and optional metre) coordinates."""

    def __init__(self, local=None, elevation=None):
        self.items = []  # (kind, geometry type, [(lat, lon)], properties)
        self.local, self.elevation = local, elevation  # callables (lat, lon arrays) -> (x, y), z

    def point(self, kind, lat, lon, **props):
        self.items.append((kind, "Point", np.array([[lat, lon]], float), props))

    def line(self, kind, latlon_arr, **props):
        self.items.append((kind, "LineString", np.asarray(latlon_arr, float), props))

    def polygon(self, kind, rings_latlon, **props):
        """A polygon: closed rings of (lat, lon), the first the outer ring, the rest holes."""
        self.items.append((kind, "Polygon", [np.asarray(r, float) for r in rings_latlon], props))

    def projected(self, name: str, proj: PJ.Projection, in_map, cut: float) -> dict:
        """The features in the map's plane: coordinates [x, y(, z ground height)] in metres
        (planet-radius sphere, x east, y north of the projection's centre). Points off the
        map are left out; lines are cut where they leave it or jump across a seam (more
        than `cut` metres between vertices), and become MultiLineStrings."""
        feats, kept, dropped = [], 0, 0
        Rm = R_KM * 1000
        for n, (kind, gt, ll, props) in enumerate(self.items):
            if gt == "Polygon":  # kept whole where its shore is on the map, else left out
                rings = []
                for r in ll:
                    x, y = proj.forward(r[:, 0], r[:, 1])
                    x, y = x * Rm, y * Rm
                    if not (np.isfinite(x) & in_map(x, y)).all() or (np.hypot(np.diff(x), np.diff(y)) > cut).any():
                        rings = None
                        break
                    rings.append([[round(float(a), 1), round(float(b), 1)] for a, b in zip(x, y)])
                if rings is None:
                    dropped += 1
                else:
                    feats.append(_feature({"type": "Polygon", "coordinates": rings}, {"kind": kind, **_clean(props)}, f"{kind}-{n}"))
                    kept += 1
                continue
            x, y = proj.forward(ll[:, 0], ll[:, 1])
            x, y = x * Rm, y * Rm
            ok = np.isfinite(x) & in_map(x, y)
            z = self.elevation(ll[:, 0], ll[:, 1]) if self.elevation else None
            p = {"kind": kind, **_clean(props)}
            if z is not None and gt == "Point":
                p["elevation_m"] = round(float(z[0]), 1)

            def c3(i):
                return [round(float(x[i]), 1), round(float(y[i]), 1)] + ([round(float(z[i]), 1)] if z is not None else [])
            if gt == "Point":
                if ok[0]:
                    feats.append(_feature({"type": "Point", "coordinates": c3(0)}, p, f"{kind}-{n}"))
                    kept += 1
                else:
                    dropped += 1
                continue
            runs, cur = [], []
            for i in range(len(x)):
                if ok[i] and cur and np.hypot(x[i] - x[cur[-1]], y[i] - y[cur[-1]]) > cut:
                    runs.append(cur)
                    cur = []
                if ok[i]:
                    cur.append(i)
                elif cur:
                    runs.append(cur)
                    cur = []
            runs.append(cur)
            runs = [[c3(i) for i in r] for r in runs if len(r) > 1]
            if not runs:
                dropped += 1
                continue
            geom = ({"type": "LineString", "coordinates": runs[0]} if len(runs) == 1
                    else {"type": "MultiLineString", "coordinates": runs})
            feats.append(_feature(geom, p, f"{kind}-{n}"))
            kept += 1
        return _collection(name, feats, {"units": "m", "crs": {"type": "name", "properties": {"name": "map:" + proj.name}},
                                         "note": "coordinates [x east, y north(, z ground height)] in metres on the map plane; "
                                                 "features off the map are left out"})

    def collections(self, name: str, local_name: str | None = None):
        geo, loc = [], []
        for n, (kind, gt, ll, props) in enumerate(self.items):
            if gt == "Polygon":
                p = {"kind": kind, **_clean(props)}
                polys = _antimeridian_polygons([np.asarray(r, float)[:, ::-1] for r in ll])
                if polys:
                    geom = ({"type": "Polygon", "coordinates": polys[0]} if len(polys) == 1
                            else {"type": "MultiPolygon", "coordinates": polys})
                    geo.append(_feature(geom, p, f"{kind}-{n}"))
                if self.local:
                    rings = []
                    for r in ll:
                        x, y = self.local(r[:, 0], r[:, 1])
                        rings.append([[round(float(a * 1000), 1), round(float(b * 1000), 1)] for a, b in zip(x, y)])
                    loc.append(_feature({"type": gt, "coordinates": rings}, p, f"{kind}-{n}"))
                continue
            z = self.elevation(ll[:, 0], ll[:, 1]) if self.elevation else None
            p = {"kind": kind, **_clean(props)}
            if z is not None and gt == "Point":
                p["elevation_m"] = round(float(z[0]), 1)
            if gt == "Point":
                geo.append(_feature({"type": gt, "coordinates": _round((ll[0, 1], ll[0, 0]))}, p, f"{kind}-{n}"))
            else:  # a line: one part, or a MultiLineString cut at the antimeridian
                parts = _antimeridian_line(ll[:, ::-1], {k: props[k] for k in PER_VERTEX_KEYS if k in props})
                if not parts:
                    continue
                if len(parts) == 1:
                    geom = {"type": "LineString", "coordinates": parts[0][0]}
                    p.update({k: v for k, v in parts[0][1].items()})
                else:
                    geom = {"type": "MultiLineString", "coordinates": [c for c, _ in parts]}
                    for k in parts[0][1] if parts else ():
                        p[k] = [v[k] for _, v in parts]
                geo.append(_feature(geom, p, f"{kind}-{n}"))
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
    # land: the smoothed ground above the sea or under ice, and the cells below it cut off from it (geo.is_land)
    pit = sm.nearest(world_land(L, grid) & (np.asarray(L["elevation"]) <= 0)).reshape(ny, nx)
    water = np.where((elev > 0) | (ice > 0) | pit, 0, 1).astype(np.uint8)
    if "lake" in L:
        water[sm.nearest(np.asarray(L["lake"]) > 0).reshape(ny, nx)] = 2
    P = {"elevation": elev, "ice": ice, "water": water}
    for k, src in (("biome", "biome"), ("vegetation", "vegetation"), ("rock", "surface_rock")):
        if src in L:
            P[k] = sm.nearest(L[src]).reshape(ny, nx)
    for k in (*HU.CLASS_MAPS, *GA.NAMES):
        if k in L:
            P[k] = sm.nearest(L[k]).reshape(ny, nx)
    if "tree_cover" in L:
        P["splat"] = splat_weights(slope_deg(elev, dx_m, dy_m), ice, smooth("tree_cover") / 100,
                                   smooth("plant_cover") / 100, smooth("precipitation", 800), smooth("temperature", 10),
                                   smooth("flooded") / 100, water)
    return P


def _greedy(order: np.ndarray, ll: np.ndarray, min_km: float) -> list[int]:
    """Indices into `order` (best first) kept so that no two are within min_km (great circle) of each other."""
    p = xyz(np.radians(ll[:, 0]), np.radians(ll[:, 1]))
    kept: list[int] = []
    for i in range(len(order)):
        if not kept or (arc_km(p[kept] @ p[i]) >= min_km).all():
            kept.append(i)
    return kept


def _human_use_features(feats: Features, tab: dict, node_ll, kind: str, min_km: float, grid=None, L=None) -> None:
    """Feature kinds of humanuse.py (PW-099): navigable_river (lines), harbour, pass, spring, fertile_land (points).
    node_ll: node ids -> (lat, lon) array; min_km: how close two points of one kind may be."""
    net = tab["net"]
    names = {1: "small boats", 2: "barges", 3: "sea-going"}
    if "nav" in tab:
        nv = tab["nav"]
        lines = river_lines(net.nxt, nv["q"], nv["cls"] > 0)

        def km_of(seg):
            return round(_path_km(node_ll(seg)), 1)
        for r in HU.nav_reaches(lines, nv["cls"], nv["q"], nv["grad"], nv["open"], nv["conn"], km_of):
            pts = node_ll(r["nodes"])
            pts[:, 1] = np.degrees(np.unwrap(np.radians(pts[:, 1])))
            feats.line("navigable_river", pts, nav_class=names[r["cls"]], class_id=r["cls"], length_km=r["length_km"],
                       discharge_m3s=[round(r["q_min"], 1), round(r["q_max"], 1)],
                       gradient_m_per_km=round(r["gradient_m_per_km"], 2), open_months=r["open_months"],
                       reaches_sea=r["to_sea"])
    if "harbour" in tab:
        h = tab["harbour"]
        idx = np.flatnonzero(h["cls"] > 0)
        idx = idx[np.lexsort((-h["shelter"][idx], -h["cls"][idx]))]
        if len(idx):
            ll = node_ll(idx)
            for i in _greedy(idx, ll, min_km):
                n = idx[i]
                feats.point("harbour", float(ll[i, 0]), float(ll[i, 1]), harbour_class=["", "anchorage", "harbour", "fine harbour"][h["cls"][n]],
                            class_id=int(h["cls"][n]), setting="estuary" if h["q_mouth"][n] >= HU.ESTUARY_Q else "bay",
                            depth_m=round(float(h["depth"][n])), fetch_km=round(float(h["fetch_km"][n])),
                            shelter=round(float(h["shelter"][n]), 2), sea_ice_months=round(float(h["ice_months"][n]), 1),
                            river_m3s=round(float(h["q_mouth"][n])) if h["q_mouth"][n] > 0 else None)
    for p in tab.get("passes", []):
        la, lo = node_ll(np.array([p["node"]]))[0]
        feats.point("pass", float(la), float(lo), pass_class=["", "open", "seasonal", "snow-bound"][HU.pass_class(p["open_months"])],
                    class_id=HU.pass_class(p["open_months"]), height_m=round(p["height"]), open_months=p["open_months"],
                    basin_km2=[round(p["area_a"]), round(p["area_b"])])
    sp = tab.get("springs")
    if sp is not None and len(sp):
        ll = node_ll(sp)
        for i in _greedy(sp, ll, min_km):
            feats.point("spring", float(ll[i, 0]), float(ll[i, 1]))
    if kind == "world" and grid is not None and L is not None and "fertile" in L:
        comp, n = grid.components(np.asarray(L["fertile"]) >= 3)
        score = np.asarray(L["fertile_score"], float) / 100
        area = cell_area_km2(grid.n)
        for k in range(n):
            cells = np.flatnonzero(comp == k)
            if len(cells) < 3:
                continue
            c = grid.centers[cells].mean(0)
            la, lo = latlon(c / np.linalg.norm(c))
            feats.point("fertile_land", float(la), float(lo), area_km2=round(len(cells) * area),
                        mean_score=round(float(score[cells].mean()), 2),
                        prime_share=round(float((np.asarray(L["fertile"])[cells] == 4).mean()), 2))


def _world_features(world: dict, path: Path, river_min: float, with_highlights: bool, hu_tab: dict | None = None) -> Features:
    L, grid, meta = world["layers"], world["grid"], world["meta"]
    el = np.asarray(L["elevation"], float)
    ice = np.asarray(L.get("ice", np.zeros_like(el)), float)
    lat, lon = grid.lat, grid.lon
    feats = Features(elevation=lambda la, lo: el[grid.locate(xyz(np.radians(la), np.radians(lo)))])
    if "flow" in L and "downstream" in L:
        q = hydrology.discharge(grid, np.asarray(L["flow"], float))
        active = (q >= river_min) & is_land(el, ice, grid)
        ll = np.stack([lat, lon], 1)
        for r in river_lines(np.asarray(L["downstream"]), q, active):
            pts = ll[r["nodes"]]
            pts[:, 1] = np.degrees(np.unwrap(np.radians(pts[:, 1])))  # (no jump over the antimeridian)
            feats.line("river", pts, **_river_props(r, pts, 0))
    if "lake" in L or "lake_kind" in L:
        lake = np.asarray(L["lake"] if "lake" in L else L["lake_kind"]) > 0
        comps, n = grid.components(lake)
        area = cell_area_km2(grid.n)
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
            props["centroid_lat_lon"] = [round(float(la), 4), round(float(lo), 4)]
            # outline: the cell edges not shared with another cell of the lake
            cc = np.array([(c[i], c[(i + 1) % len(c)]) for k_ in cells for c in (grid.cell_corners[k_],) for i in range(len(c))])
            e = np.sort(cc, 1)
            key = e[:, 0] * len(grid.corners) + e[:, 1]
            uk, first, cntk = np.unique(key, return_index=True, return_counts=True)
            edge = e[first[cntk == 1]]
            rings = [np.stack(latlon(grid.corners[np.array(r)]), 1) for r in boundary_rings(edge[:, 0], edge[:, 1])]
            if rings:
                feats.polygon("lake", lake_polygon(rings), **props)
            else:
                feats.point("lake", float(la), float(lo), **props)
    if hu_tab:
        ll_all = np.stack([lat, lon], 1)
        _human_use_features(feats, hu_tab, lambda idx: ll_all[np.asarray(idx)].copy(), "world",
                            3 * grid.spacing * R_KM, grid, L)
    from .zoom import volcanoes as ZV
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


# ---------------------------------------------------------------------------
# Projected maps (PW-477)
# ---------------------------------------------------------------------------
class MapView:
    """A projection, its pixel grid and what the manifest says about it."""

    def __init__(self, projection: str, center, extent, width: int):
        self.extent = None if extent is None else PJ.parse_extent(extent)
        self.proj = PJ.Projection(projection, *PJ.parse_center(center))
        self.g = PJ.pixel_grid(self.proj, width, self.extent)
        self.shape = (self.g["height"], self.g["width"])
        self.valid = self.g["valid"]
        if not self.valid.any():
            raise SystemExit(f"--projection {projection} --center {self.proj.lat0:g},{self.proj.lon0:g}"
                             + (f" --extent {extent}" if extent else "") + " covers none of the planet")
        self.m_px = self.g["step"] * R_KM * 1000

    def pixel_m(self):
        return PJ.pixel_size_m(self.g["pts"], self.valid, self.shape)

    def in_map(self, x, y):
        """Which of the plane points (m) fall on the map: inside its rectangle and projection domain."""
        Rm = R_KM * 1000
        ok = (np.abs(x) <= self.g["hw"] * Rm) & (np.abs(y) <= self.g["hh"] * Rm)
        return ok & self.proj.unproject(np.where(ok, x, 0) / Rm, np.where(ok, y, 0) / Rm)[1]

    def seam_m(self):
        return 0.5 * 2 * self.proj.full_extent()[0] * R_KM * 1000

    def layout(self, tile, overlap, layers, **more) -> dict:
        Rm, g = R_KM * 1000, self.g
        d = self.proj.describe()
        return {"type": "map_projection", "projection": self.proj.name, "center": d["center"],
                "proj": d["proj"], **({"proj_note": d["proj_note"]} if d["proj_note"] else {}),
                "oblique_frame": d["oblique_frame"], "sphere_radius_m": Rm,
                "extent_km": None if self.extent is None else list(self.extent),
                "extent": "given" if self.extent else "whole projection",
                "width": g["width"], "height": g["height"], "m_per_px": round(self.m_px, 2),
                "x_range_m": [-g["hw"] * Rm, g["hw"] * Rm], "y_range_m": [-g["hh"] * Rm, g["hh"] * Rm],
                "row0": "north (up on the map)", "col0": "west (left)",
                "pixel_x_m": "x_range_m[0] + (col + 0.5) * m_per_px   (east of the projection centre)",
                "pixel_y_m": "y_range_m[1] - (row + 0.5) * m_per_px   (north of the projection centre)",
                "nodata": {"rule": "pixels the projection does not show (off the globe or outline) or outside the extent",
                           "coverage_layer": "coverage (255 on the map, 0 off it)",
                           "heights": 0, "ids": NODATA_ID, "splat": "all channels 0"},
                "tile": tile, "overlap": overlap, "layers": layers, **more}


def _log_map(log, mv: MapView):
    log(f"  {mv.proj.name} map centred {mv.proj.lat0:g},{mv.proj.lon0:g}: {mv.shape[1]}x{mv.shape[0]} px, "
        f"{mv.m_px / 1000:.1f} km/px, {100 * mv.valid.mean():.0f}% covered")


def export_world(path: Path, out: Path, res: int | None, tile: int, overlap: int, cube: int, raw: bool,
                 height_range, river_min: float | None, with_highlights: bool, log, mv_args=None) -> dict:
    world = W.load(path)
    meta = world["meta"]
    hu, hu_tab = HU.analyse_world(world["grid"], world["layers"])  # (a stored layer wins; older worlds have none)
    for k, v in hu.items():
        world["layers"].setdefault(k, v)
    if "travel" not in world["layers"]:  # (game attributes, PW-206; older worlds have none)
        world["layers"].update(GA.world_layers(world["grid"], world["layers"], float(meta.get("params", {}).get("tilt", 23.4))))
    width = int(res or WORLD_WIDTH)
    wr = Writer(out, tile, overlap, raw)
    mv = valid = None
    if mv_args:
        mv = MapView(mv_args["projection"], mv_args["center"], mv_args["extent"], width)
        valid, (height, width) = mv.valid, mv.shape
        _log_map(log, mv)
        dx, dy = mv.pixel_m()
        P = _world_rasters(world, mv.g["pts"], mv.shape, dx, dy)
        lo, hi = _height_range(P["elevation"], height_range, valid)
        layouts = {"map": mv.layout(tile, overlap, _write_products(wr, P, lo, hi, valid=valid))}
    else:
        height = max(width // 2, 1)
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
                            with_highlights, hu_tab)
    geo, = feats.collections(f"{path.stem} features")
    (out / "features.geojson").write_text(json.dumps(geo))
    counts = _kind_counts(feats)
    fe = {"geojson": "features.geojson", "counts": counts, "crs": "WGS84 lon/lat, degrees; point elevation_m = ground height"}
    if mv:
        fe.update(_projected_features(feats, mv, f"{path.stem} features (map)", out))
    return {"kind": "world", "id": path.stem, "layouts": layouts, "height": (lo, hi), "features": fe,
        "source": {"world": {"id": path.stem, "name": world.get("name"), "source_run": meta.get("source_run"),
                             "t_myr": meta.get("t_myr"), "level": meta.get("level"), "seed": meta.get("seed"),
                             "created": meta.get("created")}},
        "sea_level_m": 0.0, "eustatic_sea_level_m": meta.get("sea_level_m"), "global_temp_c": meta.get("global_temp_c")}


def _projected_features(feats: Features, mv: MapView, name: str, out: Path) -> dict:
    col = feats.projected(name, mv.proj, mv.in_map, mv.seam_m())
    (out / "features_map.geojson").write_text(json.dumps(col))
    return {"map_geojson": "features_map.geojson",
            "map_crs": f"{mv.proj.name} map plane, metres [x east, y north(, z ground height)] from the projection centre "
                       f"(see layouts.map); {len(col['features'])} of {len(feats.items)} features fall on the map",
            "map_counts": _kind_counts_of(col["features"])}


def _kind_counts_of(features: list) -> dict:
    c: dict = {}
    for f in features:
        c[f["properties"]["kind"]] = c.get(f["properties"]["kind"], 0) + 1
    return c


def _kind_counts(feats: Features) -> dict:
    c: dict = {}
    for kind, *_ in feats.items:
        c[kind] = c.get(kind, 0) + 1
    return c


def _height_range(elev: np.ndarray, rng, valid: np.ndarray | None = None) -> tuple[float, float]:
    if valid is not None:
        elev = elev[valid]
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


def _resample_zoom(A: dict, fr, pts: np.ndarray, shape: tuple, r_km: float, cat) -> dict:
    """The zoom's rasters (pixel size r_km, centred on the frame `fr`) at the unit vectors
    `pts`: bilinear for continuous fields, nearest for class maps. Returns the fields and
    `valid`, the pixels inside the zoom's square."""
    ny, nx = next(iter(A.values())).shape
    x, y = fr.to_plane(pts)
    col, row = x / r_km + nx / 2 - 0.5, ny / 2 - 0.5 - y / r_km
    valid = (col >= -0.5) & (col <= nx - 0.5) & (row >= -0.5) & (row <= ny - 0.5) & (pts @ fr.c > 0)
    col, row = np.clip(col, 0, nx - 1), np.clip(row, 0, ny - 1)
    c0, r0 = np.minimum(col.astype(int), max(nx - 2, 0)), np.minimum(row.astype(int), max(ny - 2, 0))
    c1, r1 = np.minimum(c0 + 1, nx - 1), np.minimum(r0 + 1, ny - 1)
    fc, fr_ = col - c0, row - r0
    cn, rn = np.rint(col).astype(int), np.rint(row).astype(int)
    out = {}
    for k, a in A.items():
        if k in cat or a.dtype.kind not in "fc":
            v = a[rn, cn]
        else:
            a = np.asarray(a, float)
            v = (a[r0, c0] * (1 - fc) + a[r0, c1] * fc) * (1 - fr_) + (a[r1, c0] * (1 - fc) + a[r1, c1] * fc) * fr_
        out[k] = v.reshape(shape)
    return out, valid.reshape(shape)


def _zoom_products(A: dict, r_dx, r_dy) -> dict:
    """The layers to write from a zoom's (possibly resampled) rasters."""
    el = A["elevation"].astype(float)
    water = A.get("water", np.where(el > 0, 0, 1)).astype(np.uint8)
    P = {"elevation": el, "ice": A.get("ice"), "water": water, "biome": A.get("biome"),
         "vegetation": A.get("vegetation"), "rock": A.get("surface_rock"),
         **{k: A[k] for k in (*HU.CLASS_MAPS, *GA.NAMES) if k in A}}
    if "tree_cover" in A:
        P["splat"] = splat_weights(
            slope_deg(el, r_dx, r_dy), np.asarray(A.get("ice", 0 * el), float),
            A["tree_cover"] / 100, A.get("plant_cover", A["tree_cover"]) / 100, A.get("precipitation", 800 + 0 * el),
            A.get("temperature", 10 + 0 * el), (A["wetland"] > 0).astype(float) if "wetland" in A else 0 * el, water)
    return P


def export_zoom(d: Path, out: Path, res: float | None, tile: int, overlap: int, raw: bool, height_range,
                river_min: float | None, with_highlights: bool, log, mv_args=None) -> dict:
    from .zoom import regional as Z
    meta, L = Z.load(d, decode=True)
    nat = float(meta["res_km"])
    f = 1 if mv_args else max(int(round((res or nat) / nat)), 1)
    cat = ("water", "biome", "vegetation", "surface_rock", "rock", "lake_kind", "wetland", *HU.CLASS_MAPS, "spring",
           "fire_months", "green_months", "hazards", "mud_months")
    hu, hu_tab = HU.analyse_zoom(L, nat, HU.falls_pixels(meta.get("stats", {}).get("falls", []),
                                                        Z.Frame(meta["center"]["lat"], meta["center"]["lon"]),
                                                        meta["nx"], meta["ny"], nat))
    for k, v in hu.items():  # (a stored layer wins; older zooms have none)
        L.setdefault(k, v)
    A = {k: _block(np.asarray(v), f, k in cat) for k, v in L.items()
         if np.asarray(v).ndim == 2}
    ny, nx = A["elevation"].shape
    r_km = nat * f
    log(f"  native grid, {nx}x{ny} px at {r_km:g} km" + (f" (block {f}x{f})" if f > 1 else ""))
    el = A["elevation"].astype(float)
    wr = Writer(out, tile, overlap, raw)
    fr = Z.Frame(meta["center"]["lat"], meta["center"]["lon"])
    mv = None
    if mv_args:  # a projected map: resample the native grid onto the map's pixels
        out_km = float(res or nat)
        ext = mv_args["extent"] or (meta["size_km"], meta["size_km"])
        center = mv_args["center"] or (meta["center"]["lat"], meta["center"]["lon"])
        mv = MapView(mv_args["projection"], center, ext, int(round(ext[0] / out_km)))
        _log_map(log, mv)
        Am, inside = _resample_zoom(A, fr, mv.g["pts"], mv.shape, r_km, cat)
        valid = mv.valid & inside
        dx, dy = mv.pixel_m()
        P = _zoom_products(Am, dx, dy)
        lo, hi = _height_range(P["elevation"], height_range, valid)
        layout = mv.layout(tile, overlap, _write_products(wr, P, lo, hi, valid=valid), size_km=meta["size_km"],
                           note="pixels outside the zoom's square are nodata")
        mv.valid = valid
    else:
        P = _zoom_products(A, r_km * 1000, r_km * 1000)
        lo, hi = _height_range(el, height_range)
        layout = {"type": "azimuthal_equidistant_native", "width": nx, "height": ny, "m_per_px": r_km * 1000,
                  "native_m_per_px": nat * 1000, "size_km": meta["size_km"], "row0": "north", "col0": "west",
                  "pixel_x_m": "(col + 0.5 - width/2) * m_per_px   (east of centre)",
                  "pixel_y_m": "(height/2 - row - 0.5) * m_per_px   (north of centre)",
                  "tile": tile, "overlap": overlap, "layers": _write_products(wr, P, lo, hi)}
    # features
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
            feats.line("river", pts, **_river_props(r, pts, 1))
    st = meta.get("stats", {})
    for fl in st.get("falls", []):
        feats.point("waterfall", fl["lat"], fl["lon"], height_m=fl["height_m"], discharge_m3s=fl["discharge_m3s"],
                    fall_kind=fl["kind"], length_km=fl.get("length_km"), from_lake=fl.get("from_lake"),
                    gorge_km=fl.get("gorge_km"), plunge_pool_m=fl.get("plunge_pool_m"))
    for v in st.get("volcanoes", []):
        feats.point("volcano", v["lat"], v["lon"], status=v.get("status"), form=v.get("form"),
                    summit_m=v.get("top_m"), height_m=v.get("height_m"), age_myr=v.get("age_myr"),
                    volcano_type=v.get("kind"), minor=bool(v.get("minor")))
    for dp in meta.get("resources", {}).get("deposits", []):  # (zoom/resources.py, PW-610)
        feats.point("deposit", dp["lat"], dp["lon"], resource=dp["key"], name=dp["name"], form=dp["form"],
                    size=dp["size"], tonnage=dp["tonnage"], tonnage_unit=dp["tonnage_unit"], grade=dp.get("grade"),
                    grade_unit=dp.get("grade_unit"), depth_m=dp["depth_m"], host=dp["host"])
    for dl in st.get("deltas", []):
        la, lo_ = dl["lat_lon"]
        feats.point("delta", la, lo_, delta_type=dl["type"], discharge_m3s=dl["discharge_m3s"],
                    plain_radius_km=dl["plain_radius_km"], weights=dl["weights"])
    _zoom_lakes(feats, A, nx, ny, r_km, pix_ll, fr)
    h0, w0 = L["elevation"].shape
    _human_use_features(feats, hu_tab, lambda idx: pix_ll(np.asarray(idx), w0, h0, nat), "zoom", max(5 * nat, 10.0))
    if with_highlights:
        _zoom_highlights(feats, meta, fr, ground, to_xy)
    geo, loc = feats.collections(f"{meta['id']} features", f"{meta['id']} features (local)")
    (out / "features.geojson").write_text(json.dumps(geo))
    (out / "features_local.geojson").write_text(json.dumps(loc))
    sw = meta["source_world"]
    fe = {"geojson": "features.geojson", "local_geojson": "features_local.geojson", "counts": _kind_counts(feats),
          "crs": "WGS84 lon/lat, degrees; point elevation_m = ground height", "local_crs": local.crs + ", metres"}
    if mv:
        fe.update(_projected_features(feats, mv, f"{meta['id']} features (map)", out))
    return {"kind": "zoom", "id": meta["id"], "layouts": {"map" if mv else "native": layout}, "height": (lo, hi),
            "features": fe,
        "source": {"zoom": {"id": meta["id"], "name": meta.get("name"), "created": meta.get("created"),
                            "seed": meta.get("seed"), "center": meta["center"], "size_km": meta["size_km"],
                            "res_km": nat, "params": meta.get("params"), "format": meta.get("format")},
                   "world": sw},
        "projection": {**{k: meta["projection"][k] for k in ("type", "lat0", "lon0", "planet_radius_km",
                                                              "corners_latlon")}, "x": "east, m", "y": "north, m"},
        "sea_level_m": 0.0}


def _zoom_lakes(feats: Features, A: dict, nx: int, ny: int, r_km: float, pix_ll, fr_) -> None:
    """One polygon per lake (a connected group of lake pixels), with its centroid as a property."""
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
        props["centroid_lat_lon"] = [round(float(mid[0]), 4), round(float(mid[1]), 4)]
        # outline: pixel edges between a lake pixel and anything else (vertex id = row * (nx + 1) + col
        # of the pixel corner), straight runs merged
        r0_, c0_ = rows.min() - 1, cols.min() - 1
        loc = np.zeros((rows.max() - r0_ + 2, cols.max() - c0_ + 2), bool)
        loc[rows - r0_, cols - c0_] = True
        W = nx + 1
        ea, eb = [], []
        for (rr, cc) in zip(*np.nonzero(loc[1:, 1:-1] != loc[:-1, 1:-1])):  # horizontal edge above pixel row rr+1
            v = (rr + 1 + r0_) * W + (cc + 1 + c0_)
            ea.append(v)
            eb.append(v + 1)
        for (rr, cc) in zip(*np.nonzero(loc[1:-1, 1:] != loc[1:-1, :-1])):  # vertical edge left of pixel col cc+1
            v = (rr + 1 + r0_) * W + (cc + 1 + c0_)
            ea.append(v)
            eb.append(v + W)
        rings = []
        for ring in boundary_rings(np.array(ea), np.array(eb)):
            rc = np.array(np.divmod(ring, W)).T
            d1, d2 = rc - np.roll(rc, 1, 0), np.roll(rc, -1, 0) - rc
            keep = (d1 != d2).any(1)  # drop vertices on a straight run
            rc = rc[keep] if keep.sum() >= 3 else rc
            xs, ys = (rc[:, 1] - nx / 2) * r_km, (ny / 2 - rc[:, 0]) * r_km
            rings.append(np.stack(latlon(fr_.to_sphere(xs, ys)), 1))
        if rings:
            feats.polygon("lake", lake_polygon(rings), **props)
        else:
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
           river_min: float | None = None, highlights: bool = True, projection: str | None = None,
           center=None, extent=None, log=print) -> Path:
    """Exports a world or zoom (id, 'world:<id>' / 'zoom:<id>') to the directory `out`
    (default: <data root>/exports/<id>); returns it. projection / center ('lat,lon') /
    extent ('2000km', '30deg', '3000x2000km') make a projected map (PW-477); any one of
    them does (equirect for a world, aeqd for a zoom, by default). See the module docstring."""
    kind, path = resolve(ref)
    mv_args = None
    if projection or center is not None or extent is not None:
        projection = projection or ("equirect" if kind == "world" else "aeqd")
        if projection not in PJ.NAMES:
            raise SystemExit(f"--projection {projection!r}: one of {', '.join(PJ.NAMES)}")
        try:
            center = PJ.parse_center(center) if center is not None else (0.0, 0.0) if kind == "world" else None
            extent = PJ.parse_extent(extent) if extent is not None else None
        except ValueError as e:
            raise SystemExit(str(e)) from None
        mv_args = {"projection": projection, "center": center, "extent": extent}
    if kind == "zoom" and cube:
        raise SystemExit("--cube is for worlds; a zoom keeps its native grid")
    item = path.stem if kind == "world" else path.name
    out = Path(out) if out else exports_dir() / item
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    log(f"exporting {kind} {item} -> {out}")
    args = (tile, overlap)
    if kind == "world":
        r = export_world(path, out, int(res) if res else None, *args, cube, raw, height_range, river_min, highlights, log,
                         mv_args)
    else:
        r = export_zoom(path, out, res, *args, raw, height_range, river_min, highlights, log, mv_args)
    lo, hi = r.pop("height")
    legend = S.legends()
    leg = {"water": list(WATER), "biome": legend["biomes"], "vegetation": legend["vegetation"]["types"],
           "rock": legend["rocks"], **legend["human_use"], "game": legend["game"],
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
                                                            "raw": raw, "river_min_m3s": river_min,
                                                            "projection": mv_args}},
        "human_use": "PW-099 (humanuse.py): class-map layers river_nav, harbour, pass, fertile, fresh_water (legend.json "
                     "has each one's ids) and feature kinds navigable_river (lines), harbour, pass, spring, "
                     "fertile_land (worlds) in features.geojson. Derived from the simulation's fields, not new physics.",
        "game": "PW-206 (gameattrs.py): scalar layers travel (x walking time), sightline (m), grazing, foraging, timber, "
                "fuel, building (0-5), mud_months, and 16-bit masks fire_months, green_months (bit 0 = January) and "
                "hazards (legend.json game.hazards: bit, name, rule); value = stored x scale (each layer says). "
                "Computed from the plant and soil layers by written-down rules, not new physics.",
        "reserved": "Further layers are added as new entries of layouts.<name>.layers and new feature kinds, not new "
                    "top-level keys.",
    }
    (out / "manifest.json").write_text(json.dumps(_clean(manifest), indent=1))
    log(f"  {len(list(out.rglob('*')))} files, {r['features']['counts']}")
    return out


def _all_layers(layouts: dict):
    for lay in layouts.values():
        yield from lay.get("layers", {}).values()
        for fl in lay.get("layers_by_face", {}).values():
            yield from fl.values()
