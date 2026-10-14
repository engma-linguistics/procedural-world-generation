"""Regional zoom: refine a patch of a sliced world from ~110 km cells to ~2 km.

    uv run python -m planet zoom <world_id> --lat L --lon L [--size-km 1000] [--res-km 2] [--seed N]

A static refinement at one moment, deterministic in (world, centre, size,
resolution, seed). All noise is sampled at 3D positions on the planet (in
km), so two overlapping zooms of the same world share their detail.

Pipeline
--------
1. Projection. Azimuthal equidistant around the centre: pixel (row, col) is
   at x = (col + 0.5 - n/2) * res km east, y = (n/2 - row - 0.5) * res km
   north of the centre, distances from the centre are true.
2. Coarse fields -> fine. Continuous fields (elevation, temperature reduced
   to sea level, precipitation, ice, a 'ruggedness' factor) are averaged
   with a Gaussian kernel (sigma ~ half a cell) over the projected cell
   centres: smooth, no hexagon imprint. Land and sea elevations are
   interpolated separately and a smoothed land/sea indicator (+1/-1)
   decides which applies, so coasts stay where the coarse map has them.
   Categorical layers (rock, climate) take the nearest cell after a noisy
   warp of the position, which roughens the boundaries.
3. Coastline. The land/sea indicator gets fractal noise added; its zero
   contour is the coast. The noise only matters where the indicator is
   near 0, i.e. near coarse coasts, so the large-scale pattern is kept.
   Elevation ramps smoothly to 0 at the coast on both sides.
4. Detail. fbm plus ridged noise (ranges and massifs, wavelengths from a
   cell down to ~6 px), amplitude ~ ruggedness x (elevation + local coarse
   relief). Ruggedness comes from the basement rock (orogen/arc/hotspot
   high, craton/sediment low), thick sediment cover (basins: subdued),
   plate boundaries (convergent: high), elevation itself, and ice
   (smoothed). Then each coarse cell's mean is pulled back to its coarse
   value (smooth correction field), so the region doesn't drift.
   This is the *target* surface for step 6.
   Big river mouths (>= DELTA_MIN_Q) get a delta plain: within a radius R
   growing with discharge and the coarse sediment cover offshore, the
   detail is damped and the land pulled down to a few metres above the
   sea, the sea floor shallows, and a lobe of land is pushed out to sea.
5. Big rivers. Coarse cells with large flow become smooth (Catmull-Rom,
   noise-warped) polylines; a valley with a monotone-downstream floor is
   cut along each, and along them the landscape pass treats discharge as
   at least the coarse river's. Rivers (and smaller streams) entering
   from outside the region bring their coarse discharge in at the edge.
   Coarse lakes become lakes: outline like the coast, surface at the
   coarse water level (the world's lake_level, else the spill level),
   depth following the coarse fill depth and growing away from the
   shore. Below each delta apex the river splits into distributaries.
   Waterfalls: where a coarse river drops steeply (knickpoints()), part of
   the reach's drop is kept as falls instead of being graded smooth: the
   valley floor along the reach becomes a staircase (a main fall whose lip
   has retreated upstream of the escarpment, cutting a gorge, and smaller
   cascades below), with heights set by discharge and the lip's rock.
   Rivers entering at the region's edge can't drain straight back out.
6. Landscape pass on the raster: a steady-state stream-power landscape.
   Priority flood + steepest-descent D8 routing gives a drainage network
   and discharge Q (precipitation + inflow); walking up from the outlets
   (sea, lakes, region edge), each pixel sits above its receiver by
   slope = C / K * Q^-0.5 (K = surface.ROCKS erodibility): big rivers
   are gentle, small gullies and ridges steep, so valleys nest
   dendritically. C is a smooth field refitted each iteration so every
   ~35 km neighbourhood keeps the target's mean; the network is
   recomputed on the new surface and the whole thing repeated (~15x).
   Lakes are outlets held at their surface, with a rim kept above the
   water except at the outlet (the shore pixel nearest the coarse lake's
   exit); an open lake's inflow leaves again there, and the ground below
   the outlet steps down at most RAPIDS_GRAD m/km (rapids, not a cliff).
   Distributaries take their share of the water at each split. The coarse
   rivers keep at least their valley floor (the staircase, with its falls);
   each fall's gorge has walls held at the lip's level (cliffs, hanging
   side valleys), and a plunge pool (a small lake) at its foot.
   Summits taper above a soft cap; hillslopes get some creep (channels
   stay sharp); any pits left are filled.

Outputs: zooms/<id>/ (paths and layer files: store.py)
  zoom.json      meta: source world, centre, size, resolution, projection,
                 layer specs (file, dtype, shape, units), legends, heightmap
                 mapping, stats
  layers/<name>.bin  one raw little-endian array per layer (float32 / uint8),
                 (ny, nx), row 0 = north. load() reads them.
  heightmap.png  16-bit greyscale: elev_m = min_m + v / 65535 * (max_m - min_m)
  preview.png    hillshade x hypsometric tint, lakes, rivers
  coarse.png     the source cells (nearest cell) for comparison
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np

from . import climate, hydrology, kernels
from . import store as S
from . import world as W
from . import zoom_kernels as ZK
from .geo import R_KM, latlon, xyz
from .images import write_png
from .climate import LAPSE
from .surface import ROCK_K

SEC_PER_YR = 3.156e7
KM2_M_PER_YR_TO_M3S = 1e6 / SEC_PER_YR  # discharge unit used internally -> m^3/s

# How rugged the sub-cell detail is, by basement rock (surface.ROCKS ids).
RUGGED = {0: 0.35, 1: 0.85, 2: 0.9, 3: 0.45, 4: 1.0, 5: 0.35}
SEA_CLIMATE = 30  # KOPPEN "-"
# landscape pass: discharge exponent of the steady-state slope, hillslope
# creep per smoothing step (and number of steps), steepest slope allowed
SPL_M, KD, MAX_SLOPE, SMOOTH_STEPS = 0.5, 0.25, 450.0, 6  # MAX_SLOPE in m/km
DELTA_MIN_Q = 1500.0  # m^3/s at a coarse river mouth for a delta plain


# ---------------------------------------------------------------------------
# Projection
# ---------------------------------------------------------------------------
class Frame:
    """Azimuthal equidistant projection around (lat0, lon0); x east, y north, km."""

    def __init__(self, lat0: float, lon0: float):
        la, lo = np.radians(lat0), np.radians(lon0)
        self.c = xyz(la, lo)
        e = np.cross([0.0, 0.0, 1.0], self.c)
        if np.linalg.norm(e) < 1e-9:  # at a pole: pick any east
            e = np.array([0.0, 1.0, 0.0])
        self.e = e / np.linalg.norm(e)
        self.n = np.cross(self.c, self.e)

    def to_plane(self, p: np.ndarray):
        rho = np.arccos(np.clip(p @ self.c, -1, 1))
        a, b = p @ self.e, p @ self.n
        s = np.hypot(a, b)
        k = np.where(s > 1e-12, rho * R_KM / np.maximum(s, 1e-12), 0.0)
        return a * k, b * k

    def to_sphere(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        rho = np.hypot(x, y) / R_KM
        az = np.arctan2(x, y)
        d = np.sin(az)[:, None] * self.e + np.cos(az)[:, None] * self.n
        return np.cos(rho)[:, None] * self.c + np.sin(rho)[:, None] * d


def _latlon(p):
    lat, lon = latlon(p)
    return float(lat), float(lon)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def softplus(x, s):
    return s * np.logaddexp(0, x / s)


def smin(a, b, k):
    """Polynomial smooth minimum (rounded crease where a and b cross)."""
    hh = np.clip(k - np.abs(a - b), 0, None) / k
    return np.minimum(a, b) - hh * hh * k / 4


def _box_mean(a, w, r):
    """Weighted box-filter mean of a (2D) with weights w over a (2r+1)^2 window."""
    def box(x):
        c = np.cumsum(np.pad(x, ((r + 1, r), (0, 0)), mode="edge"), 0)
        x = c[2 * r + 1:] - c[:-2 * r - 1]
        c = np.cumsum(np.pad(x, ((0, 0), (r + 1, r)), mode="edge"), 1)
        return c[:, 2 * r + 1:] - c[:, :-2 * r - 1]
    return box(a) / np.maximum(box(w), 1e-9)


def find_world(ref: str) -> Path:
    return S.find_world(ref)


def _octaves(wavelength, finest):
    """Octaves (halving the wavelength each time) until `finest` km."""
    return int(np.clip(np.ceil(np.log2(wavelength / finest)) + 1, 1, 12))


def _catmull_rom(p0, p1, p2, p3, n):
    """n+1 points from p1 to p2 (uniform Catmull-Rom)."""
    t = np.linspace(0, 1, n + 1)[:, None]
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


# Waterfalls in the raster: from a channel carrying >= WF_MIN_Q m^3/s, the
# biggest drop of the water surface over <= WF_STEPS pixels downstream that
# is >= WF_MIN_DROP m and steeper than WF_MIN_GRAD m/km on average.
WF_MIN_Q, WF_MIN_DROP, WF_MIN_GRAD, WF_STEPS = 50.0, 30.0, 15.0, 3


def waterfalls(ws: np.ndarray, q: np.ndarray, rec: np.ndarray, nx: int, ny: int, res: float,
               starts: dict | None = None, top: int = 5) -> list[dict]:
    """Pixel-scale falls along the drainage network. ws: water surface (lake
    surface on lakes, 0 at sea), q: discharge m^3/s, rec: D8 receivers (-1
    at outlets); starts: {lake outlet pixel: lake level}, where a fall
    starts at the lake surface a pixel upstream. Best first by power
    (discharge x height), at least ~15 km apart, none within 4 px of the
    edge. Each: px (row, col), height_m, length_km, discharge_m3s,
    power_gw, top_m, bottom_m, from_lake."""
    n = nx * ny
    lvl, d0 = ws.astype(float).copy(), np.zeros(n)
    for o, v in (starts or {}).items():
        if o >= 0 and v > lvl[o]:
            lvl[o], d0[o] = v, res
    row, col = np.divmod(np.arange(n), nx)
    inner = (row >= 4) & (row < ny - 4) & (col >= 4) & (col < nx - 4)
    i = np.flatnonzero((q >= WF_MIN_Q) & inner & (rec >= 0))
    # a lake outlet's own step (lake surface -> outlet pixel) counts as one
    drop = lvl[i] - ws[i]
    ok = (d0[i] > 0) & (drop >= WF_MIN_GRAD * np.maximum(d0[i], 1e-9))
    best_h, best_d, best_j = np.where(ok, drop, 0.0), d0[i].copy(), i.copy()
    j, dist, alive = i.copy(), d0[i].copy(), np.ones(len(i), bool)
    for _ in range(WF_STEPS):
        r = rec[j]
        alive &= r >= 0
        rr = np.maximum(r, 0)
        diag = (rr % nx != j % nx) & (rr // nx != j // nx)
        dist = np.where(alive, dist + res * np.where(diag, 1.4142, 1.0), dist)
        j = np.where(alive, rr, j)
        drop = lvl[i] - ws[j]
        better = alive & (drop >= WF_MIN_GRAD * dist) & (drop > best_h)
        best_h, best_d, best_j = (np.where(better, a, b) for a, b in ((drop, best_h), (dist, best_d), (j, best_j)))
    keep = best_h >= WF_MIN_DROP
    i, h, d, jj = i[keep], best_h[keep], best_d[keep], best_j[keep]
    gw = 1000 * 9.81 * q[i] * h / 1e9
    out, sep = [], max(6, int(round(15 / res)))
    for k in np.argsort(-gw):
        r0, c0 = divmod(int(i[k]), nx)
        if any(max(abs(r0 - f["px"][0]), abs(c0 - f["px"][1])) < sep for f in out):
            continue
        out.append({"px": [r0, c0], "height_m": round(float(h[k]), 1), "length_km": round(float(d[k]), 1),
                    "discharge_m3s": round(float(q[i[k]]), 1), "power_gw": round(float(gw[k]), 3),
                    "top_m": round(float(lvl[i[k]]), 1), "bottom_m": round(float(ws[jj[k]]), 1),
                    "from_lake": bool(d0[i[k]] > 0)})
        if len(out) >= top:
            break
    return out


# Knickpoints (real waterfalls). A coarse river reach steeper than
# KP_MIN_GRAD over consecutive links, with at least KP_MIN_EXCESS m of drop
# beyond a graded KP_GRADED m/km, keeps part of that drop as falls instead of
# being graded smooth. How much is concentrated, and where:
# - lip resistance R (0..1) from the exposed rock (or the basement, under a
#   thin cover: a sandstone veneer over shield granite holds a lip like the
#   granite does): KP_RESIST;
# - concentrated fraction f = (0.25 + 0.45 R) / (1 + Q / 50,000)^0.3: hard
#   lips hold more, the biggest rivers wear their lips into cataracts
#   (Niagara: ~51 of ~99 m between the lakes; the Congo's Livingstone falls:
#   ~270 m as 30-odd rapids);
# - split into n = 1 + 1.5 log10(1 + Q / 2000) steps (1-5), shares falling
#   off by KP_SHARE: the main fall at the lip, the rest as cascades spread
#   down the reach below the gorge;
# - the lip has retreated from the escarpment (the middle of the steepest
#   link) upstream by a gorge of length 4 km x sqrt(Q / 1000 m^3/s) x
#   (1.5 - R) (Niagara: ~11 km at ~6,000 m^3/s), at most 60 km and most of
#   the reach above the escarpment.
KP_MIN_GRAD, KP_GRADED, KP_MIN_EXCESS, KP_MIN_Q = 0.8, 0.2, 50.0, 100.0  # m/km, m/km, m, m^3/s
KP_SHARE, KP_MAX_H, KP_MIN_STEP = 0.55, 1000.0, 8.0
# how well each rock (surface.ROCKS id) holds a lip
KP_RESIST = {0: 0.8, 1: 0.9, 2: 0.8, 3: 0.4, 4: 0.85, 5: 1.0, 6: 0.75, 7: 0.7, 8: 0.2, 9: 0.1, 10: 0.3}
RAPIDS_GRAD = 2.0  # m/km: a lake's outflow steps down no faster than this below its outlet (and any fall there)


def lip_resistance(surface_rock: int, basement: int, cover_km: float) -> float:
    r = KP_RESIST.get(int(surface_rock), 0.5)
    if cover_km < 0.5:  # a thin cover: the river soon cuts into the basement, which then holds the lip
        r = max(r, KP_RESIST.get(int(basement), 0.5))
    return r


def knickpoints(ws: np.ndarray, down: np.ndarray, riv: np.ndarray, land: np.ndarray, q: np.ndarray,
                link_km: dict, polys: dict, rock: dict) -> list[dict]:
    """Waterfalls to keep, from the coarse river network. ws: coarse water
    surface per cell (lake level on lakes); down, riv, land per cell; q:
    discharge m^3/s; link_km {cell: km to its downstream cell}; polys {cell:
    (m, 2) polyline in km from the cell to its downstream cell}; rock {cell:
    (surface rock, basement, cover km)}. Returns, per steep reach, the main
    fall and its cascades: "steps", each at arc length "s" km along the
    reach's polyline "s" (the cells' polylines joined), with height "h" m and
    gorge length "gorge_km"; plus the lip "resistance", discharge "q" etc."""
    def steep(i):
        d = down[i]
        if i not in polys or d < 0 or not land[d] or not riv[i]:
            return False
        return (ws[i] - ws[d]) / max(link_km[i], 1.0) >= KP_MIN_GRAD
    main_up = {}  # each cell's main upstream branch (the biggest)
    for u in polys:
        d = down[u]
        if d >= 0 and (d not in main_up or q[u] > q[main_up[d]]):
            main_up[d] = u
    out = []
    for i0 in polys:
        if not steep(i0):
            continue
        # a reach starts where the link above (the main upstream one) isn't
        # steep, and ends where it stops being steep or joins a bigger river
        if i0 in main_up and steep(main_up[i0]):
            continue
        cells, i = [], i0
        while steep(i) and len(cells) < 50:
            cells.append(i)
            if main_up.get(down[i]) != i:
                break
            i = down[i]
            if i not in polys:
                break
        drop = np.array([ws[c] - ws[down[c]] for c in cells])
        km = np.array([link_km[c] for c in cells])
        excess = float(np.sum(np.maximum(drop - KP_GRADED * km, 0)))
        Q = float(q[cells[-1]])
        if excess < KP_MIN_EXCESS or Q < KP_MIN_Q:
            continue
        line = np.concatenate([polys[c] if k == 0 else polys[c][1:] for k, c in enumerate(cells)])
        seg = np.hypot(*np.diff(line, axis=0).T)
        s = np.concatenate([[0.0], np.cumsum(seg)])
        m = len(polys[cells[0]])
        k = int(np.argmax(drop / km))  # the escarpment: middle of the steepest link
        s_e = 0.5 * (s[k * (m - 1)] + s[(k + 1) * (m - 1)])
        R = lip_resistance(*rock[cells[k]])
        gorge = float(min(4.0 * np.sqrt(Q / 1000) * (1.5 - R), 60.0, 0.8 * s_e + 0.4 * (s[(k + 1) * (m - 1)] - s_e)))
        s_lip = max(s_e - gorge, 0.0)
        R = max(R, lip_resistance(*rock[cells[min(int(np.searchsorted(s, s_lip) // (m - 1)), len(cells) - 1)]]))
        f = (0.25 + 0.45 * R) / (1 + Q / 50000) ** 0.3
        n = int(np.clip(round(1 + 1.5 * np.log10(1 + Q / 2000)), 1, 5))
        w = KP_SHARE ** np.arange(n)
        H = f * excess * w / w.sum()
        steps = [{"s": float(s_lip), "h": float(min(H[0], KP_MAX_H)), "gorge_km": float(s_e - s_lip)}]
        for j in range(1, n):  # cascades: spread down the reach below the escarpment
            if H[j] >= KP_MIN_STEP:
                steps.append({"s": float(s_e + j / n * (s[-1] - s_e)), "h": float(H[j]), "gorge_km": 0.0})
        out.append({"cell": int(cells[0]), "cells": [int(c) for c in cells], "s": s, "m": m, "q": Q,
                    "excess_m": excess, "reach_km": float(km.sum()), "resistance": float(R), "steps": steps})
    return out


def stair_z(kp: dict, sv: np.ndarray) -> np.ndarray:
    """The staircase floor of a reach with falls (knickpoints(), with the
    floor between the falls, 'cont', added in build) at arc lengths sv km."""
    return np.interp(sv, kp["s"], kp["cont"]) - sum(st["h"] * (sv >= st["s"]) for st in kp["steps"])


def _shift(a: np.ndarray, dr: int, dc: int, fill):
    """a[r + dr, c + dc] at (r, c), `fill` off the raster."""
    ny, nx = a.shape
    out = np.full_like(a, fill)
    out[max(0, -dr):ny - max(0, dr), max(0, -dc):nx - max(0, dc)] = \
        a[max(0, dr):ny - max(0, -dr), max(0, dc):nx - max(0, -dc)]
    return out


def coarse_lakes(g, L: dict, elev: np.ndarray):
    """Coarse lakes as (label per cell, -1 off lakes; water level per lake;
    exit cell per lake, -1 if it's closed). The level is the world's
    `lake_level` layer when it has one (NaN or ground level = no lake;
    `lake_kind` 2 = closed, keeps its water), else the spill level from a
    priority flood of the coarse elevation. The exit is the cell the lake
    overflows into (the biggest one, if the flood found several)."""
    n = g.n
    lake = np.asarray(L.get("lake", np.zeros(n))).astype(bool)
    level = hydrology.priority_flood(g, elev)[0]
    if "lake_level" in L:
        lv = np.asarray(L["lake_level"], float)
        ok = np.isfinite(lv) & (lv > elev + 0.5)
        lake, level = ok, np.where(ok, lv, level)
    lake &= elev > 0
    lab, nl = kernels.components(lake, g.nbr_off, g.nbr_idx)
    lvl, exit_ = np.zeros(nl), np.full(nl, -1)
    if nl == 0:
        return lab, lvl, exit_
    down, flow = np.asarray(L["downstream"]).astype(int), np.asarray(L["flow"], float)
    kind = np.asarray(L["lake_kind"]).astype(int) if "lake_kind" in L else None
    cells = np.flatnonzero(lab >= 0)
    cells = cells[np.argsort(lab[cells], kind="stable")]
    for k, cc in enumerate(np.split(cells, np.flatnonzero(np.diff(lab[cells])) + 1)):
        lvl[k] = np.median(level[cc])
        out = down[cc]
        out = out[(out >= 0)]
        out = out[lab[out] != k]
        closed = kind is not None and np.bincount(kind[cc]).argmax() == 2
        if len(out) and not closed:
            exit_[k] = out[np.argmax(flow[out])]
    return lab, lvl, exit_


def _deltas(g, L, sel, fr, sp, size_km, elev, flow, down, cell_area):
    """Big coarse river mouths in or near the region, biggest first, as dicts:
    mouth point (x, y km; between the last land cell and the sea cell),
    seaward unit vector u, discharge q (m^3/s), sediment factor sf (0..1,
    from the coarse sediment cover offshore), delta plain radius R and lobe
    radius Rl (km). Mouths inside a bigger delta are dropped."""
    land = elev > 0
    cand = sel[land[sel] & (down[sel] >= 0)]
    cand = cand[~land[down[cand]]]
    q = flow[cand] * cell_area * KM2_M_PER_YR_TO_M3S
    keep = q >= DELTA_MIN_Q
    cand, q = cand[keep], q[keep]
    cover = np.asarray(L.get("sediment_cover", np.zeros(g.n)), float)
    sea_sel = sel[~land[sel]]
    out = []
    for k in np.argsort(-q):
        i, d = cand[k], down[cand[k]]
        p = g.centers[i] + g.centers[d]
        (mx,), (my,) = fr.to_plane((p / np.linalg.norm(p))[None])
        (ix, dx), (iy, dy) = fr.to_plane(g.centers[[i, d]])
        u = np.array([dx - ix, dy - iy])
        u /= max(np.linalg.norm(u), 1e-9)
        near = np.arccos(np.clip(g.centers[sea_sel] @ (p / np.linalg.norm(p)), -1, 1)) * R_KM < 2.5 * sp
        sf = float(smoothstep(0.5, 8.0, cover[sea_sel][near].max())) if near.any() else 0.0
        # Earth: Nile ~150 km of plain at 2,800 m^3/s, Mississippi ~250 km at
        # 17,000, Ganges-Brahmaputra ~350 km (huge sediment load)
        R = float(np.clip(10.0 * (q[k] / 100) ** 0.35 * (0.8 + 0.6 * sf), 15.0, 300.0))
        if max(abs(mx), abs(my)) > size_km / 2 + 0.5 * R:
            continue
        if any(np.hypot(mx - o["x"], my - o["y"]) < 0.8 * o["R"] for o in out):
            continue
        out.append({"x": mx, "y": my, "u": u, "q": float(q[k]), "sf": sf, "R": R,
                    "Rl": 0.22 * R * (0.6 + 0.8 * sf), "cell": int(i)})
    return out


# ---------------------------------------------------------------------------
# The refinement
# ---------------------------------------------------------------------------
def build(world: dict, lat: float, lon: float, size_km: float = 1000.0, res_km: float = 2.0,
          seed: int = 1, iterations: int = 15, river_min_flow: float = 3.0, log=print) -> dict:
    t0 = time.time()
    g, L = world["grid"], world["layers"]
    sp = g.spacing * R_KM  # coarse cell spacing, km
    cell_area = 4 * np.pi * R_KM**2 / g.n
    nx = ny = max(16, int(round(size_km / res_km)))
    res = size_km / nx
    npx = nx * ny
    fr = Frame(lat, lon)
    xs = (np.arange(nx) + 0.5 - nx / 2) * res
    ys = (ny / 2 - np.arange(ny) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    px, py = X.ravel(), Y.ravel()
    P = fr.to_sphere(px, py)
    Pk = np.ascontiguousarray(P * R_KM)
    S = int(seed) * 1_000_003 + 17  # noise seed base

    # --- coarse cells around the region --------------------------------
    elev = L["elevation"].astype(float)
    ang = np.arccos(np.clip(g.centers @ fr.c, -1, 1)) * R_KM
    sel = np.flatnonzero(ang < size_km * 0.7072 + 4 * sp)
    cx, cy = fr.to_plane(g.centers[sel])
    e_c = elev[sel]
    land_c = e_c > 0

    # ruggedness per coarse cell
    nb_e = np.maximum(elev, 0)
    deg = np.diff(g.nbr_off)
    src = np.repeat(np.arange(g.n), deg)
    relief = np.zeros(g.n)
    np.maximum.at(relief, src, np.abs(nb_e[src] - nb_e[g.nbr_idx]))
    rock = L["rock"].astype(int)
    r_c = np.array([RUGGED.get(int(k), 0.5) for k in rock[sel]])
    cover = L.get("sediment_cover", np.zeros(g.n))[sel]
    r_c = r_c * np.where(cover > 0.3, 0.65, 1.0)
    bnd = L.get("plate_boundary", np.zeros(g.n))[sel]
    r_c = np.where(bnd > 0, np.maximum(r_c, 0.85), np.where(bnd < 0, np.maximum(r_c, 0.6), r_c))
    r_c = np.maximum(r_c, np.clip(relief[sel] / 2500, 0, 1))
    r_c = np.maximum(r_c, 0.9 * smoothstep(600, 3500, e_c))  # high ground is rugged whatever the rock
    ice_c = L.get("ice", np.zeros(g.n))[sel].astype(float)
    r_c = np.clip(r_c * np.exp(-ice_c / 500), 0.12, 1.0)

    temp_c = L["temperature"][sel] + LAPSE * np.maximum(e_c, 0)
    warm = L.get("warm_month", L["temperature"])[sel] + LAPSE * np.maximum(e_c, 0)
    vals = np.column_stack([np.maximum(e_c, 1.0), np.minimum(e_c, -1.0), temp_c, warm,
                            L["precipitation"][sel].astype(float), ice_c, r_c, relief[sel]])
    wts = np.ones_like(vals)
    wts[:, 0] = land_c
    wts[:, 1] = ~land_c
    sig = 0.5 * sp
    fine, _ = ZK.gauss_interp(px, py, cx, cy, vals, wts, sig)
    e_land = np.nan_to_num(fine[:, 0], nan=1.0)
    e_sea = np.nan_to_num(fine[:, 1], nan=-50.0)
    t_sl, warm_sl, precip, ice, rug, rel = (fine[:, k] for k in range(2, 8))
    ind, _ = ZK.gauss_interp(px, py, cx, cy, np.where(land_c, 1.0, -1.0)[:, None],
                             np.ones((len(sel), 1)), 0.42 * sp)
    ind = ind[:, 0]
    log(f"  interpolated {len(sel)} coarse cells onto {nx}x{ny} px [{time.time() - t0:.1f}s]")

    # --- delta plains at big river mouths --------------------------------
    # Within R of the mouth (R grows with discharge and offshore sediment)
    # the land becomes a flat plain a few metres above the sea (wD, zD), the
    # sea floor shallows (prodelta: wS, zS), and a lobe of new land is pushed
    # out to sea (added to the land/sea indicator). The detail noise and the
    # coarse-mean correction are damped there (wC).
    flow, down = L["flow"].astype(float), L["downstream"].astype(int)
    deltas = _deltas(g, L, sel, fr, sp, size_km, elev, flow, down, cell_area)
    wD, zD, wS, zS, wC, lobe = (np.zeros(npx) for _ in range(6))
    hf = 1 - smoothstep(250.0, 800.0, e_land)  # no plain against high ground
    for dl in deltas:
        R = dl["R"]
        r = np.hypot(px - dl["x"], py - dl["y"])
        w = smoothstep(R, 0.55 * R, r) * hf
        zD = np.where(w > wD, 0.8 + 10.0 * (r / R) ** 1.5, zD)
        wD = np.maximum(wD, w)
        zS = np.where(r < 1.2 * R, np.maximum(zS, -(2.0 + 50.0 * (r / R) ** 2)), zS)
        wS = np.maximum(wS, smoothstep(1.2 * R, 0.5 * R, r))
        wC = np.maximum(wC, smoothstep(1.4 * R, 0.8 * R, r))
        # the lobe is centred half its radius offshore and lifts the land/sea
        # indicator there to a little above the coast value
        lc = np.array([dl["x"], dl["y"]]) + 0.5 * dl["Rl"] * dl["u"]
        k = int(np.argmin((px - lc[0]) ** 2 + (py - lc[1]) ** 2))
        amp_l = np.clip(0.35 - ind[k], 0.0, 2.0) if np.hypot(px[k] - lc[0], py[k] - lc[1]) < 2 * res else 1.0
        lobe += amp_l * np.exp(-((px - lc[0]) ** 2 + (py - lc[1]) ** 2) / dl["Rl"] ** 2)
    zS = np.where(wS > 0, zS, -1e9)

    # --- coastline -------------------------------------------------------
    lam = 0.9 * sp
    cw = ZK.fbm(Pk, lam, 4, 0.5, S + 7) / 0.17 * 0.12 * sp  # domain warp: bays, headlands
    Pc = np.ascontiguousarray(Pk + cw[:, None] * np.array([0.57, -0.41, 0.71]))
    coast_n = ZK.fbm(Pc, lam, _octaves(lam, 2 * res), 0.62, S + 1) / 0.15
    ind_n = ind + 0.22 * coast_n + lobe
    land = ind_n > 0
    ramp_l = smoothstep(0.0, 0.55, ind_n)
    ramp_s = smoothstep(0.0, 0.45, -ind_n)
    base = np.where(land, e_land * ramp_l, e_sea * ramp_s)

    # --- detail ----------------------------------------------------------
    lam_f = 0.8 * sp
    # Noise supplies ranges and massifs down to ~6 px; the valleys inside
    # them are left to the landscape pass (noise can't make drainage).
    fine_l = max(6 * res, 8.0)
    f1 = ZK.fbm(Pk, lam_f, _octaves(lam_f, fine_l), 0.55, S + 2) / 0.17
    lam_r = 0.4 * sp
    rr = ZK.ridged(Pk, lam_r, _octaves(lam_r, fine_l), 0.55, S + 3)
    rr = (rr - 0.55) / 0.175
    tex = ZK.fbm(Pk, fine_l, _octaves(fine_l, 2 * res), 0.6, S + 4) / 0.17
    w_r = np.clip(rug, 0, 1) ** 2
    detail = (1 - w_r) * f1 + w_r * (0.4 * f1 + 0.9 * rr)
    detail = 2.2 * np.tanh(detail / 2.2) + 0.06 * tex  # no absurd spikes
    amp_land = (rug * (0.36 * np.maximum(base, 0) + 0.3 * np.nan_to_num(rel) + 25) + 12) * (1 - 0.9 * wD)
    amp_sea = (5 + 0.08 * np.abs(base)) * (1 - 0.7 * wS)
    taper = np.where(land, smoothstep(0.0, 0.35, ind_n), smoothstep(0.0, 0.25, -ind_n))
    h = base + taper * np.where(land, amp_land, amp_sea) * detail

    # soft floor/ceiling at the coast (the delta plain and prodelta get a much harder one)
    s_land, s_sea = 15.0 * (1 - 0.95 * wD), 15.0 * (1 - 0.9 * wS)

    def clamp(hh):
        return np.where(land, 0.5 + softplus(hh - 0.5, s_land), -0.5 - softplus(-0.5 - hh, s_sea))

    h = clamp(h)

    # --- keep each coarse cell's mean ----------------------------------
    own = g.locate(P)
    lut = np.full(g.n, -1)
    lut[sel] = np.arange(len(sel))
    own_s = lut[own]
    full_px = cell_area / res**2

    def cell_means(hh):
        cnt = np.bincount(own_s, minlength=len(sel))
        tot = np.bincount(own_s, hh, minlength=len(sel))
        return tot / np.maximum(cnt, 1), cnt

    corr_taper = np.where(land, smoothstep(0.0, 0.3, ind_n), smoothstep(0.0, 0.3, -ind_n)) * (1 - wC)
    for _ in range(2):
        m, cnt = cell_means(h)
        ok = cnt > 0.25 * full_px
        resid = np.where(ok, e_c - m, 0.0)
        corr, _ = ZK.gauss_interp(px, py, cx, cy, resid[:, None], ok[:, None].astype(float), 0.5 * sp)
        h = clamp(h + corr_taper * np.nan_to_num(corr[:, 0]))
    if deltas:  # the plain keeps a little of the (damped) detail
        det = taper * amp_land * detail
        h = np.where(land, (1 - wD) * h + wD * (zD + det), (1 - wS) * h + wS * np.maximum(h, zS))
        h = clamp(h)
    log(f"  coast + detail + mean correction [{time.time() - t0:.1f}s]")

    # --- coarse rivers -> valleys + inflow --------------------------------
    clab, clvl, cexit = coarse_lakes(g, L, elev)
    lake_c = clab >= 0
    in_sel = np.zeros(g.n, bool)
    in_sel[sel] = True
    riv = in_sel & (elev > 0) & (flow >= river_min_flow) & (down >= 0)
    riv_ids = np.flatnonzero(riv)
    inflow = np.zeros(npx)
    T = np.full(npx, np.inf)
    z_course, q_course = np.full(npx, -np.inf), np.full(npx, np.inf)
    kpix, s_pix, bottom = np.full(npx, -1), np.zeros(npx), np.zeros(npx, bool)  # reach with falls (index into kps) and arc length, per pixel
    riv_q = np.zeros(npx)  # coarse discharge along the coarse river courses
    n_rivers_in = 0
    river_segs = []
    polys, inflow_pts = {}, []  # warped coarse river polylines per cell; (pixel, radius px) where rivers enter
    kps = []
    if len(riv_ids):
        up_main = {}
        for i in riv_ids:  # main upstream branch of each river cell
            d = down[i]
            if riv[d] and (d not in up_main or flow[i] > flow[up_main[d]]):
                up_main[d] = i
        # valley floor per river cell, monotone downstream (Kahn order)
        indeg = {i: 0 for i in riv_ids}
        for i in riv_ids:
            if riv[down[i]]:
                indeg[down[i]] += 1
        r_cell = np.zeros(g.n)
        r_cell[sel] = r_c
        zfl = {}
        queue = [i for i in riv_ids if indeg[i] == 0]
        while queue:
            i = queue.pop()
            e = elev[i]
            z = e - e * (0.12 + 0.33 * r_cell[i])
            zfl[i] = min(z, zfl.get(i, np.inf))
            d = down[i]
            if riv[d]:
                zfl[d] = min(zfl.get(d, np.inf), zfl[i])
                indeg[d] -= 1
                if indeg[d] == 0:
                    queue.append(d)
        cxy = {}

        def xy(i):
            if i not in cxy:
                a, b = fr.to_plane(g.centers[i][None])
                cxy[i] = np.array([a[0], b[0]])
            return cxy[i]

        segs = []
        for i in riv_ids:
            d = down[i]
            p1, p2 = xy(i), xy(d)
            p0 = xy(up_main[i]) if i in up_main else 2 * p1 - p2
            dd = down[d]
            p3 = xy(dd) if (riv[d] and dd >= 0) else 2 * p2 - p1
            pts = _catmull_rom(p0, p1, p2, p3, 12)
            z1 = zfl[i]
            z2 = zfl[d] if riv[d] else (min(elev[d], z1) if lake_c[d] or elev[d] > 0 else 0.0)
            z2 = min(z2, z1)
            q = flow[i] * cell_area  # km^2 m/yr
            segs.append((pts, z1, z2, q, r_cell[i], i))
        # warp the polylines with a smooth vector noise field (meanders)
        allp = np.concatenate([s[0] for s in segs])
        sp_pts = np.ascontiguousarray(fr.to_sphere(allp[:, 0], allp[:, 1]) * R_KM)
        lw = 0.6 * sp
        wamp = 0.10 * sp / 0.17
        wx = ZK.fbm(sp_pts, lw, 4, 0.5, S + 11) * wamp
        wy = ZK.fbm(sp_pts, lw, 4, 0.5, S + 12) * wamp
        allp = allp + np.column_stack([wx, wy])
        k = 0
        for pts, z1, z2, q, rcell, i in segs:
            polys[i] = allp[k:k + len(pts)]
            k += len(pts)
        # waterfalls to keep where the coarse river drops steeply (knickpoints())
        ws_c = np.where(elev > 0, elev, 0.0)
        if len(clvl):
            ws_c = np.where(lake_c, clvl[np.maximum(clab, 0)], ws_c)
        cover_all = L.get("sediment_cover", np.zeros(g.n))
        srock = L.get("surface_rock", L["rock"])
        kps = knickpoints(ws_c, down, riv, elev > 0, flow * cell_area * KM2_M_PER_YR_TO_M3S,
                          {c: float(np.arccos(np.clip(g.centers[c] @ g.centers[down[c]], -1, 1)) * R_KM)
                           for c in polys}, polys,
                          {c: (int(srock[c]), int(rock[c]), float(cover_all[c])) for c in polys})
        # Along a reach with falls the valley floor becomes a staircase: the
        # floor between the falls is graded at what's left of the reach's
        # slope, and drops by each fall's height at its lip.
        zseg = {i: (z1, z2) for _, z1, z2, _, _, i in segs}
        stair = {}
        for kp in kps:
            cells, sk, m = kp["cells"], kp["s"], kp["m"]
            Tz = np.concatenate([np.linspace(*zseg[c], m)[(1 if j else 0):] for j, c in enumerate(cells)])
            drop = Tz[0] - Tz[-1]
            Hs = np.array([st["h"] for st in kp["steps"]])
            scale = min(1.0, 0.85 * max(drop, 0.0) / max(Hs.sum(), 1e-9))
            for st in kp["steps"]:
                st["h"] *= scale
            Hs = Hs * scale
            # between the falls, the floor keeps the rest of the valley floor's drop
            kp["cont"] = Tz[0] - (1 - Hs.sum() / max(drop, 1e-9)) * (Tz[0] - np.minimum.accumulate(Tz))
            Z = stair_z(kp, sk)
            for j, c in enumerate(cells):
                stair[c] = (kp, j, Z[j * (m - 1):(j + 1) * (m - 1) + 1])
        k = 0
        ax, ay, bx, by, za, zb, fw, wall, reach, sq, kseg, s0seg = ([] for _ in range(12))
        half = size_km / 2 - 4 * res
        for pts, z1, z2, q, rcell, i in segs:
            m = len(pts)
            pw = allp[k:k + m]
            k += m
            zz = stair[i][2] if i in stair else np.linspace(z1, z2, m)
            if i in stair:  # sub-segments of a reach with falls: which one, and arc length along it
                kp, j, _ = stair[i]
                kseg += [kps.index(kp)] * (m - 1)
                s0seg += list(kp["s"][j * (m - 1):(j + 1) * (m - 1)])
            else:
                kseg += [-1] * (m - 1)
                s0seg += [0.0] * (m - 1)
            qm3 = q * KM2_M_PER_YR_TO_M3S
            w_floor = max(0.8 * res, 0.4 + 0.6 * np.log10(1 + qm3 / 50))
            s_wall = 30 + 170 * rcell
            ax += list(pw[:-1, 0]); ay += list(pw[:-1, 1]); bx += list(pw[1:, 0]); by += list(pw[1:, 1])
            za += list(zz[:-1]); zb += list(zz[1:])
            fw += [w_floor] * (m - 1); wall += [s_wall] * (m - 1)
            reach += [w_floor + min(2500 / s_wall, 40)] * (m - 1)
            sq += [q] * (m - 1)
            river_segs.append(pw)
            inside = (np.abs(pw[:, 0]) < half) & (np.abs(pw[:, 1]) < half)
            # entering the region from outside: bring the coarse discharge in
            j = np.flatnonzero(inside[1:] & ~inside[:-1])
            if len(j) and not inside[0]:
                p = pw[j[0] + 1]
                col = int(np.clip(np.floor(p[0] / res + nx / 2), 3, nx - 4))
                row = int(np.clip(np.floor(ny / 2 - p[1] / res), 3, ny - 4))
                inflow[row * nx + col] += q
                inflow_pts.append((row * nx + col, int(min(np.ceil((w_floor + min(2500 / s_wall, 40)) / res) + 2, 30))))
                n_rivers_in += 1
        arr = lambda v: np.ascontiguousarray(v, dtype=float)
        T, D, I = ZK.carve_segments(nx, ny, xs[0], ys[0], res, arr(ax), arr(ay), arr(bx), arr(by),
                                    arr(za), arr(zb), arr(fw), arr(wall), arr(reach))
        on = (I >= 0) & (D < np.maximum(arr(fw)[np.maximum(I, 0)], 0.75 * res))
        riv_q = np.where(on, arr(sq)[np.maximum(I, 0)], 0.0)
        cut = land & np.isfinite(T)
        h = np.where(cut, smin(h, np.where(np.isfinite(T), T, 1e9), 40.0), h)
        h = clamp(h)
        # the coarse river keeps at least its valley floor (the staircase, on
        # reaches with falls) in the landscape pass, wherever its water runs:
        # the floor of the nearest point of its polyline
        Ii = np.maximum(I, 0)
        sa, sb_ = arr(za)[Ii], arr(zb)[Ii]
        vx, vy = arr(bx)[Ii] - arr(ax)[Ii], arr(by)[Ii] - arr(ay)[Ii]
        tt = np.clip(((px - arr(ax)[Ii]) * vx + (py - arr(ay)[Ii]) * vy) / np.maximum(vx * vx + vy * vy, 1e-12), 0, 1)
        zc = sa + tt * (sb_ - sa)
        # on reaches with falls: the staircase, evaluated at the arc length of
        # the nearest polyline point, so each fall is a sharp step wherever
        # the fine river crosses it
        kpix = np.where(I >= 0, np.asarray(kseg, int)[Ii], -1)
        s_pix = arr(s0seg)[Ii] + tt * np.hypot(vx, vy)
        for k_, kp in enumerate(kps):
            on_k = kpix == k_
            if on_k.any():
                zc[on_k] = stair_z(kp, s_pix[on_k])
        z_course = np.where(land & (I >= 0) & (D < arr(reach)[Ii]), zc, -np.inf)
        bottom = D < np.maximum(arr(fw)[Ii], res) + 2 * res  # the valley bottom along the polyline
        q_course = np.where(I >= 0, arr(sq)[Ii], np.inf)
    # smaller coarse streams crossing into the region bring their water too
    half = size_km / 2 - 4 * res
    inner = in_sel & (elev > 0) & (down >= 0) & ~riv
    for i in np.flatnonzero(inner):
        d = down[i]
        if elev[d] <= 0 or flow[i] <= 0:
            continue
        a, b = fr.to_plane(g.centers[[i, d]])
        ins = (np.abs(a) < half) & (np.abs(b) < half)
        if ins[0] or not ins[1]:
            continue
        t = np.linspace(0, 1, 64)
        xx, yy = a[0] + t * (a[1] - a[0]), b[0] + t * (b[1] - b[0])
        k = int(np.argmax((np.abs(xx) < half) & (np.abs(yy) < half)))
        col = int(np.clip(np.floor(xx[k] / res + nx / 2), 3, nx - 4))
        row = int(np.clip(np.floor(ny / 2 - yy[k] / res), 3, ny - 4))
        inflow[row * nx + col] += flow[i] * cell_area
        inflow_pts.append((row * nx + col, 3))
    log(f"  {len(riv_ids)} coarse river cells carved, {n_rivers_in} entering from outside "
        f"[{time.time() - t0:.1f}s]")

    # --- categorical layers (nearest cell after a noisy warp) ------------
    lw = 0.5 * sp
    camp = 0.16 * sp / 0.17
    wxp = ZK.fbm(Pk, lw, _octaves(lw, 2 * res), 0.55, S + 21) * camp
    wyp = ZK.fbm(Pk, lw, _octaves(lw, 2 * res), 0.55, S + 22) * camp
    cell_w = g.locate(fr.to_sphere(px + wxp, py + wyp), own.astype(np.int64))
    # land pixels shouldn't pick up an ocean cell's attributes (and vice versa)
    land_all = elev > 0
    alt = np.arange(g.n)
    for i in np.unique(cell_w):
        nb = g.nbr_idx[g.nbr_off[i]:g.nbr_off[i + 1]]
        same = nb[land_all[nb] != land_all[i]]
        if len(same):
            alt[i] = same[np.argmax(np.abs(elev[same]))] if land_all[i] else same[np.argmax(elev[same])]
    mismatch = land != land_all[cell_w]
    cell_l = np.where(mismatch, alt[cell_w], cell_w)
    rock_f = L["rock"][cell_l].astype(np.uint8)
    surf_f = L.get("surface_rock", L["rock"])[cell_l].astype(np.uint8)
    clim_f = L.get("climate", np.full(g.n, SEA_CLIMATE))[cell_l].astype(np.uint8)

    # --- landscape pass ----------------------------------------------------
    edge = np.zeros((ny, nx), bool)
    edge[0, :] = edge[-1, :] = edge[:, 0] = edge[:, -1] = True
    for p0, rr_ in inflow_pts:  # the edge next to where a river enters is land, not an outlet,
        r0, c0 = divmod(p0, nx)    # so the river can't drain straight back out of the region
        edge[max(r0 - rr_ - 3, 0):r0 + rr_ + 4, max(c0 - rr_ - 3, 0):c0 + rr_ + 4] = False
    edge = edge.ravel()
    sea = ~land
    outlet = sea | edge
    precip = np.clip(np.nan_to_num(precip, nan=0.0), 0, None)
    ice = np.clip(np.nan_to_num(ice, nan=0.0), 0, None)
    # glacier outline: thicker ice reaches further, high ground holds ice,
    # and noise makes the margin lobate instead of a smooth contour
    ice_n = ZK.fbm(Pk, 0.4 * sp, _octaves(0.4 * sp, 2 * res), 0.6, S + 5) / 0.17
    ice_eff = ice * (1 + 0.5 * ice_n) + 0.15 * (h - base)
    glacier = land & (ice > 1) & (ice_eff > 40)
    # Lakes where the coarse world has them (a coarse lake cell is a lake
    # basin ~100 km across): outline like the coast, from a smoothed
    # lake/no-lake indicator plus fractal noise. The surface is the coarse
    # lake's water level (spill level, or the world's lake_level); the depth
    # follows the coarse fill depth (level - coarse ground), growing with
    # distance from the shore over a length set by the lake's size. In the
    # landscape pass a lake is an outlet held at its surface, so the land
    # around it drains in and is built up from the water; a one-pixel rim is
    # kept above the surface except along the outlet: the shore pixel
    # nearest the coarse lake's exit that drains away. Open lakes pass their
    # inflow (plus the rain on them) on at the outlet, closed ones keep it.
    min_px = max(3, int(np.ceil(30.0 / res**2)))  # ~30 km^2
    lake = np.zeros(npx, bool)
    surf = np.zeros(npx)  # lake surface
    depth = np.zeros(npx)
    lakes = []  # per fine lake: pixels, level, exit point (x, y) or None
    lk_c = lake_c[sel] & land_c
    if lk_c.any():
        dep_c = np.where(lk_c, clvl[np.maximum(clab[sel], 0)] - e_c, 0.0)
        lind, _ = ZK.gauss_interp(px, py, cx, cy, np.column_stack([np.where(lk_c, 1.0, -1.0), dep_c]),
                                  np.column_stack([land_c, lk_c]).astype(float), 0.42 * sp)
        lake_n = ZK.fbm(Pc, 0.5 * sp, _octaves(0.5 * sp, 2 * res), 0.6, S + 8) / 0.15
        cand = land & ~edge & ~glacier & (np.nan_to_num(lind[:, 0], nan=-1.0) + 0.2 * lake_n > 0.1)
        lab, sizes = ZK.label_components(cand, nx, ny)
        pl = np.flatnonzero(lab >= 0)
        pl = pl[sizes[lab[pl]] >= min_px]
        pl = pl[np.argsort(lab[pl], kind="stable")]
        lk_cells = sel[lk_c]
        for pix in np.split(pl, np.flatnonzero(np.diff(lab[pl])) + 1) if len(pl) else []:
            cl = clab[own[pix]]
            cl = cl[cl >= 0]
            if len(cl):
                c = np.bincount(cl).argmax()
            else:  # the outline drifted off the coarse lake cells: nearest one
                c = clab[lk_cells[np.argmin(np.hypot(cx[lk_c] - px[pix].mean(), cy[lk_c] - py[pix].mean()))]]
            ex = None
            if cexit[c] >= 0:
                (a,), (b,) = fr.to_plane(g.centers[cexit[c]][None])
                ex = (a, b)
            lake[pix] = True
            surf[pix] = clvl[c]
            lakes.append({"px": pix, "level": float(clvl[c]), "exit": ex})
    if lakes:
        ds = ZK.inside_distance(lake, nx, ny) * res  # km to the shore
        dc = np.nan_to_num(lind[:, 1], nan=0.0)
        nz = ZK.fbm(Pk, 0.3 * sp, _octaves(0.3 * sp, 2 * res), 0.55, S + 9) / 0.17
        for lk in lakes:
            pix = lk["px"]
            dcm = np.maximum(dc[pix], 2.0)
            ell = np.clip(0.25 * ds[pix].max(), 2 * res, 80.0)
            d0 = dcm * (1 - np.exp(-ds[pix] / ell)) * np.clip(1 + 0.3 * nz[pix], 0.4, 1.6)
            # about the coarse mean depth overall
            depth[pix] = np.maximum(np.clip(dcm.mean() / max(d0.mean(), 1e-6), 0.7, 3.0) * d0, 0.5)
        h = np.where(lake, surf, h)
        outlet = outlet | lake
    lake_id = np.full(npx, -1)
    for j, lk in enumerate(lakes):
        lake_id[lk["px"]] = j
    # the rim: land next to a lake (the highest one, if it touches two)
    ring_lvl, ring_id = np.full(npx, -np.inf), np.full(npx, -1)
    l2, id2 = np.where(lake, surf, -np.inf).reshape(ny, nx), lake_id.reshape(ny, nx)
    for dr in (-1, 0, 1):
        for dcol in (-1, 0, 1):
            v, i2 = _shift(l2, dr, dcol, -np.inf).ravel(), _shift(id2, dr, dcol, -1).ravel()
            ring_id = np.where(v > ring_lvl, i2, ring_id)
            ring_lvl = np.maximum(ring_lvl, v)
    ring = land & ~lake & ~edge & (ring_id >= 0)
    ring_px = [np.flatnonzero(ring & (ring_id == j)) for j in range(len(lakes))]
    lake_seq = sorted(range(len(lakes)), key=lambda j: -lakes[j]["level"])  # upstream lakes first
    rain = precip / 1000.0 * res * res  # km^2 m/yr per pixel
    srcq = rain + inflow
    Kr = ROCK_K[np.minimum(surf_f, len(ROCK_K) - 1)]
    jitter = np.random.default_rng(seed).random(npx)
    active = land & ~edge & ~lake
    idx = np.arange(npx)
    target = h.copy()

    def lake_outlets(rec):
        """Per lake, the rim pixel nearest the coarse exit that drains away (-1: none)."""
        outs = np.full(len(lakes), -1)
        for j, lk in enumerate(lakes):
            c = ring_px[j]
            if lk["exit"] is None or not len(c):
                continue
            c = c[(rec[c] >= 0) & ~lake[np.maximum(rec[c], 0)]]
            if len(c):
                outs[j] = c[np.argmin(np.hypot(px[c] - lk["exit"][0], py[c] - lk["exit"][1]))]
        return outs

    def rims(rec, outs, step):
        """Per-pixel floor (rims above their lake) and cap (outlet channels
        below it) for the landscape integration."""
        fl, cp = np.full(npx, 0.5), cap.copy()
        fl[ring] = ring_lvl[ring] + 0.5
        for j, o in enumerate(outs):
            if o >= 0:
                ch = ZK.chain(rec, o)
                fl[ch] = 0.5  # no rim along the outflow
                cp[ch] = np.minimum(cp[ch], lakes[j]["level"] - 0.3)
                # Below the sill the ground steps down gradually: nothing within
                # d km of the outlet lies more than RAPIDS_GRAD * d below the
                # lake (rapids), out to the first fall placed on the outflow,
                # instead of a cliff down to a river graded up from far below
                # (and on all sides, or the water just finds a neighbour that
                # drops away).
                lv = lakes[j]["level"] - 0.3
                s_ch = np.concatenate([[0.0], np.cumsum(chain_km(ch))])
                st_ = np.flatnonzero(step[ch] > 0)
                rkm = min(lv / RAPIDS_GRAD, 150.0, s_ch[st_[0]] if len(st_) else np.inf)
                rp = int(rkm / res) + 1
                r0, c0 = divmod(int(o), nx)
                rs, cs = np.arange(max(r0 - rp, 0), min(r0 + rp + 1, ny)), np.arange(max(c0 - rp, 0), min(c0 + rp + 1, nx))
                win = (rs[:, None] * nx + cs[None, :]).ravel()
                d = np.hypot(px[win] - px[o], py[win] - py[o])
                win, d = win[(d <= rkm) & active[win]], d[(d <= rkm) & active[win]]
                fl[win] = np.maximum(fl[win], lv - RAPIDS_GRAD * d)
        return fl, cp

    def chain_km(ch):
        """Length of each link of a receiver chain, km."""
        a, b = ch[:-1], ch[1:]
        return res * np.where((a % nx != b % nx) & (a // nx != b // nx), 1.4142, 1.0)

    def place_falls(rec, Q, hprev):
        """Follow each reach with falls down the river as it runs now: from
        its most upstream pixel carrying the coarse river's water (>= 0.3x
        the coarse discharge), down the receivers, with the arc length along
        the reach (of the nearest polyline point) taken as a running maximum
        so it only grows. The river gets the staircase floor at that arc
        length, and the lip of each fall is where it crosses the fall's step.
        Returns (chain pixels, their floor, step height at each lip, gorge
        rim floor per pixel, cliff mask (lips, feet, gorges and their walls:
        no creep), [(lip, step, knickpoint)]). The gorge runs from the foot
        of the main fall for its length; the land beside it is held at the
        lip's level (hprev: the last iteration's surface), falling off by a
        quarter of the fall towards the gorge mouth, so its walls are cliffs
        and side streams join it in hanging falls."""
        step, flg, cliff, lips = np.zeros(npx), np.full(npx, -np.inf), np.zeros(npx, bool), []
        c_idx, c_val = [], []
        rv = (kpix >= 0) & (rec >= 0) & (Q >= 0.3 * q_course) & active
        for k_, kp in enumerate(kps):
            r_k = np.flatnonzero(rv & (kpix == k_))
            if not len(r_k):
                continue
            ch = ZK.chain(rec, int(r_k[np.argmin(s_pix[r_k])]))
            mine = kpix[ch] == k_
            ch = ch[:np.flatnonzero(mine)[-1] + 1]
            ch = ch[active[ch]]
            sv = np.maximum.accumulate(np.where(kpix[ch] == k_, s_pix[ch], 0.0))
            c_idx.append(ch)
            c_val.append(stair_z(kp, sv))
            for st in kp["steps"]:
                j = np.flatnonzero(sv >= st["s"])
                if not len(j) or j[0] == 0:
                    continue
                lip = int(ch[j[0] - 1])
                foot = int(rec[lip])
                step[lip] = st["h"]
                cliff[[lip, foot]] = True
                lips.append((lip, st, kp))
                if hprev is None:
                    continue
                # (a fall without a gorge still gets walls beside its foot)
                g = ZK.chain(rec, foot)
                sg = np.concatenate([[0.0], np.cumsum(chain_km(g))])
                g, sg = g[sg <= st["gorge_km"]], sg[sg <= st["gorge_km"]]
                g, sg = g[active[g]], sg[active[g]]
                if not len(g):
                    continue
                top = hprev[lip] - 0.25 * st["h"] * sg / max(st["gorge_km"], 1e-6)
                cliff[g] = True
                r, cc = np.divmod(g, nx)
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nb = np.clip(r + dr, 0, ny - 1) * nx + np.clip(cc + dc, 0, nx - 1)
                        ok = active[nb] & (Q[nb] < 0.3 * Q[lip]) & (nb != lip)
                        np.maximum.at(flg, nb[ok], top[ok])
                        cliff[nb[ok]] = True
        if lips:
            flg[[lp for lp, _, _ in lips]] = -np.inf
        c_idx = np.concatenate(c_idx) if c_idx else np.zeros(0, np.int64)
        c_val = np.concatenate(c_val) if c_val else np.zeros(0)
        return c_idx, c_val, step, flg, cliff, lips

    def reroute(rec, order):
        """Apply the distributary receivers (if they leave the network acyclic)."""
        if not len(ov_src):
            return rec, order, False
        r2 = rec.copy()
        r2[ov_src] = ov_dst
        o2 = ZK.receiver_order(r2)
        return (r2, o2, True) if len(o2) == npx else (rec, order, False)

    def route(src, rec, order, outs, split_ok):
        """Accumulate src downstream, then pass each open lake's total on at
        its outlet and divide the water at distributary splits."""
        q = ZK.accumulate(rec, order, src)
        tot = np.zeros(len(lakes))
        for j in lake_seq:
            tot[j] = q[lakes[j]["px"]].sum()
            if outs[j] >= 0:
                ZK.add_chain(q, rec, outs[j], tot[j])
        if split_ok:
            for s, kids, f in splits:
                qs = q[s]
                ZK.add_chain(q, rec, kids[0], -(1 - f[0]) * qs)
                for c, fk in zip(kids[1:], f[1:]):
                    ZK.add_chain(q, rec, c, fk * qs)
        return q, tot

    # --- distributaries --------------------------------------------------
    # Below a delta apex (on the main river, 0.6 R up from its mouth) the
    # river splits into 2-6 branches that fan out to points on the coast
    # around the main mouth: a binary tree of wandering paths, each branch
    # taking a share of the water. D8 routing gives every pixel a single
    # receiver, so the branches are pinned as receiver overrides and the
    # shares are added down each branch (route); the landscape pass then
    # builds the plain around them. Laid out once the drainage network of
    # the landscape pass has settled a bit (a third of the way through).
    ov_src = ov_dst = np.zeros(0, np.int64)
    splits = []

    def make_branches(rec0, order0):
        """Receiver overrides (src, dst) and splits for the deltas, laid out
        on the drainage network (rec0, order0) of a landscape iteration."""
        ov, splits = {}, []
        score = route(srcq, rec0, order0, lake_outlets(rec0), False)[0]
        assigned = np.zeros(npx, bool)
        rng = np.random.default_rng(seed + 7)

        # Each branch heads for its own point on the coast, spread around the
        # main mouth: every step gets closer to its goal (so it arrives and
        # can't loop), choosing the neighbour closest to the goal's direction
        # plus a wandering noise angle, and keeping clear of the other
        # branches where it can.
        wander = [0.7 * ZK.fbm(Pk, 25.0, 3, 0.5, S + 41 + k) / 0.17 for k in range(2)]
        coast = np.zeros(npx, bool)  # land next to the sea
        for dr, dcol in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            coast |= active & _shift(sea.reshape(ny, nx), dr, dcol, False).ravel()
        nb8 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

        def crowd(q, i):
            """Other branches' pixels next to q (not counting i)."""
            r0, c0 = divmod(q, nx)
            return sum(assigned[(r0 + a) * nx + c0 + b] for a, b in nb8
                       if 0 <= r0 + a < ny and 0 <= c0 + b < nx and (r0 + a) * nx + c0 + b != i)

        def toward(s0, gx, gy, nsteps, blocked):
            """Pixels (start excluded) from s0 towards (gx, gy) km, at most
            nsteps; on arriving at a coast pixel, one more step into the sea."""
            out, i, seen = [], int(s0), {int(s0)}
            mix = rng.uniform(0, 2 * np.pi)  # each branch wanders its own way
            while len(out) < nsteps:
                r0, c0 = divmod(i, nx)
                d0 = np.hypot(px[i] - gx, py[i] - gy)
                th = np.arctan2(gy - py[i], gx - px[i]) + np.cos(mix) * wander[0][i] + np.sin(mix) * wander[1][i]
                best, bs = -1, -9.0
                for a, b in nb8:
                    if not (0 <= r0 + a < ny and 0 <= c0 + b < nx):
                        continue
                    q = (r0 + a) * nx + c0 + b
                    if blocked[q] or q in seen:
                        continue
                    dq = np.hypot(px[q] - gx, py[q] - gy)
                    if len(out) < 3:  # leave the split point: on fresh ground, not much further away
                        if assigned[q] or dq > d0 + res:
                            continue
                    elif dq >= d0 and not sea[q]:
                        continue
                    sc = np.cos(np.arctan2(-a, b) - th) - (3.0 if assigned[q] else 0.3 * crowd(q, i))
                    sc += 2.0 if (sea[q] and d0 < 1.5 * res) else 0.0
                    if sc > bs:
                        best, bs = q, sc
                if best < 0:
                    break
                out.append(best)
                seen.add(best)
                if assigned[best] or outlet[best]:
                    break
                i = best
            return out

        def commit(start, pix, blocked):
            """Pin pix as a channel after start; it ends at the sea (or a lake,
            or the region edge) or where it joins another branch. Returns
            (first pixel, last pixel, open end?)."""
            prev, first = start, -1
            for p in pix:
                if blocked[p]:
                    return first, prev, True
                if prev != start:
                    ov[prev] = p
                if first < 0:
                    first = p
                if outlet[p] or assigned[p]:
                    return first, p, False
                assigned[p] = True
                prev = p
            return first, prev, True

        def grow(s, goals, seg, blocked):
            """Split at pixel s into two groups of coast goals (one each if
            only two); a group heads for its goals' mean for `seg` pixels,
            then splits again."""
            k0 = len(splits)
            splits.append(None)
            m = max(len(goals) // 2, 1)
            groups = [goals[:m], goals[m:]] if len(goals) > 1 else [goals]
            share = np.array([len(gp) for gp in groups], float) * rng.uniform(0.75, 1.25, len(groups))
            kids, fr_ = [], []
            for gp, f in zip(groups, share):
                gx, gy = np.mean([px[q] for q in gp]), np.mean([py[q] for q in gp])
                pix = toward(s, gx, gy, npx if len(gp) == 1 else seg, blocked)
                first, last, open_ = commit(s, pix, blocked)
                if first < 0:
                    continue
                kids.append(first)
                fr_.append(f)
                if open_ and len(gp) > 1:
                    grow(last, gp, seg, blocked)
            if kids:
                ov[s] = kids[0]
            splits[k0] = (s, kids, np.array(fr_) / max(sum(fr_), 1e-9)) if len(kids) > 1 else None

        # main upstream branch of each pixel (the one bringing the most water)
        bp = np.full(npx, -1)
        by_q = np.argsort(score, kind="stable")
        by_q = by_q[rec0[by_q] >= 0]
        bp[rec0[by_q]] = by_q  # the last (biggest) write wins
        blocked = np.zeros(npx, bool)
        for dl in deltas:
            R = dl["R"]
            r = np.hypot(px - dl["x"], py - dl["y"])
            mouth = active & (r < R) & sea[np.maximum(rec0, 0)] & (rec0 >= 0)
            if not mouth.any():
                continue
            # walk up the main river from its mouth to the apex (0.6 R up
            # the river), then on up while it's still the main river; that
            # stretch is pinned so the river can't drift away from the apex
            m0 = np.flatnonzero(mouth)[np.argmax(score[mouth])]
            if score[m0] < 0.2 * dl["q"] / KM2_M_PER_YR_TO_M3S:
                continue
            up, a, run = [m0], -1, 0.0
            while len(up) < 4 * R / res and bp[up[-1]] >= 0:
                c = bp[up[-1]]
                run += res * (1.4142 if (c % nx != up[-1] % nx and c // nx != up[-1] // nx) else 1.0)
                if a < 0 and run > 0.6 * R:
                    a = up[-1]
                if a >= 0 and (score[c] < 0.5 * score[a] or not active[c]):
                    break
                up.append(c)
            if a < 0 or r[a] > 1.2 * R or assigned[up[up.index(a):]].any():
                continue
            snap = (dict(ov), len(splits), assigned.copy(), blocked.copy())
            trunk = up[up.index(a) + 1:]
            for c in trunk:  # pin the main channel down to the apex
                ov[c] = rec0[c]
            assigned[[a] + trunk] = True
            blocked[[a] + trunk] = True
            nb = int(np.clip(round(1 + 1.2 * np.log10(dl["q"] / 1000) + 1.5 * dl["sf"]), 2, 6))
            # goals: coast pixels spread over a fan around the main mouth
            phi = np.arctan2(py[m0] - py[a], px[m0] - px[a])
            ln = np.hypot(px[m0] - px[a], py[m0] - py[a])
            spread = np.radians(min(30.0 + 20.0 * (nb - 1), 130.0))
            cp = np.flatnonzero(coast & ~assigned)
            ca = (np.arctan2(py[cp] - py[a], px[cp] - px[a]) - phi + np.pi) % (2 * np.pi) - np.pi
            cd = np.hypot(px[cp] - px[a], py[cp] - py[a])
            goals = []
            for th in spread * np.linspace(-0.5, 0.5, nb) + rng.normal(0, 0.05, nb):
                ok = (np.abs(ca - th) < 0.12) & (cd > 0.5 * ln) & (cd < 2.0 * ln)
                if ok.any():
                    q = int(cp[ok][np.argmin(cd[ok])])
                    if q not in goals:
                        goals.append(q)
            if len(goals) < 2:
                goals = [int(m0)] + goals
            grow(a, goals, max(int(0.15 * ln / res), 2), blocked)
            rt = rec0.copy()
            rt[list(ov)] = list(ov.values())
            if len(ZK.receiver_order(rt)) < npx:  # a branch looped back: no distributaries here
                ov, assigned, blocked = snap[0], snap[2], snap[3]
                del splits[snap[1]:]
        return (np.array(list(ov), dtype=np.int64), np.array(list(ov.values()), dtype=np.int64),
                [sp_ for sp_ in splits if sp_ is not None])

    # Steady-state stream power: slope = C / K * Q^-m. C is a smooth field
    # fitted so every ~35 km neighbourhood keeps the mean of the target
    # surface; a little noise in C varies the relief from valley to valley.
    rad = max(1, int(round(0.3 * sp / res)))
    wmask = land.reshape(ny, nx).astype(float)
    tmean = _box_mean(np.maximum(target, 0).reshape(ny, nx) * wmask, wmask, rad).ravel()
    var = np.exp(0.35 * ZK.fbm(Pk, 0.25 * sp, 3, 0.5, S + 6) / 0.17)
    C = np.full(npx, 30.0)
    # summits: slopes taper above `soft`, nothing above `cap`
    soft = tmean + 0.7 * amp_land
    cap = tmean + np.minimum(1.8 * amp_land, 3000.0)
    rough = np.where(glacier, 0.5, 1.0) * var / Kr
    hprev = None
    was_river = bottom.copy()  # the valley bottom, and every pixel the coarse river's water has run through
    for it in range(iterations):
        filled, rec, order = ZK.flood_d8(h, outlet, nx, ny, 1e-3, jitter)
        if deltas and it == iterations // 3:  # once the network has settled a bit
            ov_src, ov_dst, splits = make_branches(rec, order)
        rec, order, split_ok = reroute(rec, order)
        outs = lake_outlets(rec)
        Q, _ = route(srcq, rec, order, outs, split_ok)
        diag = (rec >= 0) & ((rec % nx) != (idx % nx)) & ((rec // nx) != (idx // nx))
        dist = res * np.where(diag, 1.4142, 1.0)
        # coarse river courses count as carrying at least their coarse discharge
        slope = np.minimum(C * rough * np.maximum(np.maximum(Q, riv_q), 1e-3) ** -SPL_M, MAX_SLOPE)
        c_idx, c_val, step, flg, cliff, _ = place_falls(rec, Q, hprev)
        fl, cp = rims(rec, outs, step)
        was_river |= Q >= 0.3 * q_course
        flc = np.where(was_river, z_course, -np.inf)
        flc[c_idx] = c_val  # the river itself, on reaches with falls
        fl = np.maximum(np.maximum(fl, flg), flc)
        h = target.copy()
        ZK.integrate(h, rec, order, slope, dist, ~active, fl, soft, 0.5 * amp_land + 1, cp)
        hprev = h
        hmean = _box_mean(np.maximum(h, 0).reshape(ny, nx) * wmask, wmask, rad).ravel()
        C = C * np.clip(tmean / np.maximum(hmean, 1.0), 0.5, 2.0) ** 0.8
    # soften D8 streaks and knife-edge ridges on hillslopes; keep channels sharp
    chan = np.clip(np.log10(np.maximum(Q, 1e-3) / (50 * res * res)) / 2, 0, 1)
    cliff = _dilate(cliff.reshape(ny, nx), 2).ravel()  # falls, gorges and their walls don't creep
    kd = np.where(active & ~cliff, np.where(glacier, 0.4, KD * (1 - 0.8 * chan)), 0.0)
    for _ in range(SMOOTH_STEPS):
        h = ZK.diffuse(h, kd, active, nx, ny)
    h = np.where(active, np.maximum(h, 0.5), h)  # creep mustn't pull the coast below the sea
    h = np.where(ring, np.maximum(h, fl), h)  # nor the rims below their lake
    h = np.where(active, np.minimum(h, cp), h)  # nor lift a lake's outflow above the lake
    log(f"  landscape pass: {iterations} iterations [{time.time() - t0:.1f}s]")

    # --- final drainage --------------------------------------------------
    filled, rec, order = ZK.flood_d8(h, outlet, nx, ny, 1e-3, jitter)
    h = np.where(active, np.maximum(h, filled), h)  # no pits left: everything drains
    filled, rec, order = ZK.flood_d8(h, outlet, nx, ny, 1e-3, jitter)
    rec, order, split_ok = reroute(rec, order)
    outs = lake_outlets(rec)
    Q, lake_in = route(srcq, rec, order, outs, split_ok)
    area, _ = route(np.full(npx, res * res), rec, order, outs, split_ok)
    discharge = np.where(land, Q * KM2_M_PER_YR_TO_M3S, 0.0)
    ws_f = np.where(lake, surf, np.where(sea, 0.0, h))
    falls = waterfalls(ws_f, discharge, rec, nx, ny, res,
                       {int(o): lakes[j]["level"] for j, o in enumerate(outs) if o >= 0})
    # the designed falls: where they ended up, and a plunge pool at each foot
    lips = place_falls(rec, Q, h)[5]
    pool = np.zeros(npx)
    for lip, st, kp in lips:
        foot = int(rec[lip])
        hgt = float(ws_f[lip] - ws_f[foot])
        st["lip_px"], st["height_m"] = list(divmod(lip, nx)), round(hgt, 1)
        if hgt < KP_MIN_STEP or not active[foot]:
            continue
        # plunge pools are roughly as deep as the fall is high, up to ~60 m (Niagara ~50 m below a 51 m fall)
        pool[foot] = max(pool[foot], float(np.clip(0.6 * hgt, 3.0, 60.0)))
        r0, c0 = divmod(lip, nx)
        for f in falls:
            if max(abs(f["px"][0] - r0), abs(f["px"][1] - c0)) <= 3:
                f.update({"kind": "lip", "gorge_km": round(float(st["gorge_km"]), 1),
                          "lip_resistance": round(kp["resistance"], 2),
                          "coarse_reach_drop_m": round(kp["excess_m"] + KP_GRADED * kp["reach_km"]),
                          "coarse_reach_km": round(kp["reach_km"]), "plunge_pool_m": round(float(pool[foot]), 1)})
    for f in falls:
        f.setdefault("kind", "lake outlet" if f["from_lake"] else "drop")
        k = f["px"][0] * nx + f["px"][1]
        f["lat"], f["lon"] = (round(v, 3) for v in _latlon(fr.to_sphere(px[[k]], py[[k]])[0]))
    h = np.where(lake, surf - depth, h)
    lake_depth = np.where(lake, depth, 0.0)
    # plunge pools: small lakes at the foot of the falls (the water stays at the river's level)
    plunge = pool > 0
    h = np.where(plunge, h - pool, h)
    lake_depth = np.where(plunge, pool, lake_depth)
    area = np.where(land, area, 0.0)
    lake_info = sorted(({"area_km2": round(len(lk["px"]) * res * res), "level_m": round(lk["level"], 1),
                         "mean_depth_m": round(float(depth[lk["px"]].mean()), 1),
                         "max_depth_m": round(float(depth[lk["px"]].max()), 1),
                         "inflow_m3s": round(float(lake_in[j] * KM2_M_PER_YR_TO_M3S), 1),
                         "outlet": [int(outs[j] // nx), int(outs[j] % nx)] if outs[j] >= 0 else None,
                         "outflow_m3s": round(float(discharge[outs[j]]), 1) if outs[j] >= 0 else 0.0}
                        for j, lk in enumerate(lakes)), key=lambda d: -d["area_km2"])

    # --- climate on the fine terrain -------------------------------------
    hl = np.maximum(h, 0)
    temp = t_sl - LAPSE * hl
    t_warm = warm_sl - LAPSE * hl
    clim_f = np.where(sea, SEA_CLIMATE, clim_f)
    alpine = land & (clim_f < 28) & (t_warm < 10)
    clim_f = np.where(alpine, 28, clim_f)
    clim_f = np.where(land & ((t_warm < 0) | glacier), 29, clim_f).astype(np.uint8)
    biome = climate.biomes(h, temp, precip, lake)
    biome = np.where(glacier, 4, biome).astype(np.uint8)
    water = np.where(sea, 1, np.where(lake | plunge, 2, 0)).astype(np.uint8)

    # --- stats -----------------------------------------------------------
    m_fine, cnt = cell_means(h)
    full = cnt > 0.6 * full_px
    coarse_land_px = land_all[own]
    stats = {
        "land_pct": round(100 * land.mean(), 1),
        "coarse_land_pct": round(100 * coarse_land_px.mean(), 1),
        "land_sea_agreement_pct": round(100 * (land == coarse_land_px).mean(), 1),
        "mean_elev_m": round(float(h.mean()), 1),
        "coarse_mean_elev_m": round(float(elev[own].mean()), 1),
        "mean_land_elev_m": round(float(h[land].mean()), 1) if land.any() else None,
        "cell_mean_rms_error_m": round(float(np.sqrt(np.mean((m_fine - e_c)[full] ** 2))), 1) if full.any() else None,
        "cell_mean_bias_m": round(float(np.mean((m_fine - e_c)[full])), 1) if full.any() else None,
        "min_m": round(float(h.min()), 1),
        "max_m": round(float(h.max()), 1),
        "max_discharge_m3s": round(float(discharge.max()), 1),
        "lakes": int(len(np.unique(ZK.label_components(lake, nx, ny)[0][lake]))),
        "lake_pct": round(100 * lake.mean(), 2),
        "coarse_cells": int(len(sel)),
        "coarse_river_cells": int(len(riv_ids)),
        "rivers_entering": n_rivers_in,
        "largest_lakes": lake_info[:5],
        "deltas": [{"mouth_km": [round(d["x"], 1), round(d["y"], 1)], "discharge_m3s": round(d["q"]),
                    "plain_radius_km": round(d["R"])} for d in deltas],
        "distributary_splits": len(splits),
        # pixel-scale falls (see waterfalls()); kind "lip": a knickpoint kept from a steep coarse reach
        # (see knickpoints()), with its gorge and plunge pool
        "waterfalls": falls,
        "knickpoints": len(kps),
    }
    layers = {
        "elevation": h.astype(np.float32),
        "water": water,
        "lake_depth": lake_depth.astype(np.float32),
        "discharge": discharge.astype(np.float32),
        "drainage_area": area.astype(np.float32),
        "precipitation": precip.astype(np.float32),
        "temperature": temp.astype(np.float32),
        "ice": np.where(glacier, np.maximum(ice, 1.0), 0).astype(np.float32),
        "rock": rock_f,
        "surface_rock": surf_f,
        "climate": clim_f,
        "biome": biome,
    }
    coarse = {"elevation": elev[own], "precipitation": L["precipitation"][own].astype(float),
              "river_segs": river_segs}
    return {"nx": nx, "ny": ny, "res": res, "frame": fr, "layers": {k: v.reshape(ny, nx) for k, v in layers.items()},
            "stats": stats, "coarse": coarse, "rec": rec, "kps": kps, "seconds": round(time.time() - t0, 1),
            "params": {"iterations": iterations, "river_min_flow": river_min_flow, "coarse_spacing_km": round(sp, 1)}}


# ---------------------------------------------------------------------------
# Images
# ---------------------------------------------------------------------------
def hillshade(h: np.ndarray, res_km: float, exaggeration: float = 2.0, azimuth: float = 315, altitude: float = 40):
    dzdy, dzdx = np.gradient(h * exaggeration, res_km * 1000.0)
    dzdy = -dzdy  # rows go south
    az, alt = np.radians(azimuth), np.radians(altitude)
    lx, ly, lz = np.sin(az) * np.cos(alt), np.cos(az) * np.cos(alt), np.sin(alt)
    nrm = np.sqrt(1 + dzdx**2 + dzdy**2)
    return np.clip((-dzdx * lx - dzdy * ly + lz) / nrm, 0, 1)


def _ramp(v, stops):
    xs = np.array([s[0] for s in stops], float)
    cols = np.array([s[1] for s in stops], float)
    return np.stack([np.interp(v, xs, cols[:, k]) for k in range(3)], -1)


LAND_WET = [(0, (92, 140, 78)), (300, (122, 160, 92)), (900, (176, 176, 118)), (1700, (160, 132, 96)),
            (2600, (136, 116, 104)), (3600, (190, 186, 182)), (4800, (248, 248, 250))]
LAND_DRY = [(0, (206, 188, 140)), (300, (196, 172, 124)), (900, (184, 154, 112)), (1700, (160, 128, 96)),
            (2600, (136, 116, 104)), (3600, (190, 186, 182)), (4800, (248, 248, 250))]
SEA = [(-7000, (12, 28, 70)), (-4000, (20, 48, 102)), (-1500, (34, 78, 140)), (-200, (64, 124, 182)),
       (0, (104, 164, 206))]


def tint(h: np.ndarray, precip: np.ndarray) -> np.ndarray:
    wet = np.clip((precip - 250) / 700, 0, 1)[..., None]
    land = _ramp(h, LAND_WET) * wet + _ramp(h, LAND_DRY) * (1 - wet)
    return np.where((h > 0)[..., None], land, _ramp(h, SEA))


RIVER_MIN_AREA = 500.0  # km^2 upstream for a river to be drawn (at 2 km pixels)


def _dilate(m: np.ndarray, r: int) -> np.ndarray:
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r + r:
                out |= np.roll(np.roll(m, dy, 0), dx, 1)
    return out


def preview(z: dict) -> np.ndarray:
    Lr = z["layers"]
    h, res = Lr["elevation"].astype(float), z["res"]
    water = Lr["water"]
    col = tint(h, Lr["precipitation"])
    shade = hillshade(np.where(water == 2, h + Lr["lake_depth"], h), res)
    s = (0.35 + 0.85 * shade)[..., None]
    s = np.where((h > 0)[..., None], s, 0.75 + 0.3 * shade[..., None])
    col = col * s
    ice = (Lr["ice"] > 0) & (water == 0)
    col = np.where(ice[..., None], col * 0.3 + np.array([235, 242, 250]) * 0.7 * (0.55 + 0.5 * shade[..., None]), col)
    col = np.where((water == 2)[..., None], np.array([70, 130, 196.0]), col)
    q, area = Lr["discharge"], Lr["drainage_area"]
    land = (water == 0) & ~ice
    riv = (area >= RIVER_MIN_AREA * max(res / 2.0, 1.0)) & (q > 3.0) & land
    a = np.clip(0.35 + 0.25 * np.log10(np.maximum(q, 1e-9) / 30.0), 0.3, 0.95) * riv
    wide = (2.0 / res) ** 2  # a pixel covers less river at finer resolution
    for qq, r in ((3000.0 * wide, 1), (30000.0 * wide, 2)):  # big rivers are drawn wider
        a = np.maximum(a, 0.95 * (_dilate(q > qq, r) & land))
    col = col * (1 - a[..., None]) + np.array([38, 92, 178.0]) * a[..., None]
    # waterfalls: a white-water mark at the lip and just below it
    ny, nx = h.shape
    rr, cc = np.mgrid[0:ny, 0:nx]
    for f in z.get("stats", {}).get("waterfalls", []):
        r0, c0 = f["px"]
        rad = (2.0 + 0.6 * np.sqrt(f["height_m"] / 30)) * max(1.0, 1.0 / res) ** 0.5
        foam = np.clip(1.2 - np.hypot(rr - r0, cc - c0) / rad, 0, 1)[..., None]
        col = col * (1 - foam) + np.array([250, 252, 255.0]) * foam
    return np.clip(col, 0, 255).astype(np.uint8)


def coarse_image(z: dict) -> np.ndarray:
    c = z["coarse"]
    ny, nx, res = z["ny"], z["nx"], z["res"]
    e = c["elevation"].reshape(ny, nx)
    col = tint(e, c["precipitation"].reshape(ny, nx))
    # draw the coarse river polylines
    xs = (np.arange(nx) + 0.5 - nx / 2) * res
    ys = (ny / 2 - np.arange(ny) - 0.5) * res
    if c["river_segs"]:
        pts = c["river_segs"]
        a = np.concatenate([p[:-1] for p in pts])
        b = np.concatenate([p[1:] for p in pts])
        one = np.ones(len(a))
        _, D, _ = ZK.carve_segments(nx, ny, xs[0], ys[0], res, *(np.ascontiguousarray(v) for v in
                                 (a[:, 0], a[:, 1], b[:, 0], b[:, 1], one, one, one, one, one * 2 * res)))
        col = np.where((D.reshape(ny, nx) < 0.8 * res)[..., None], np.array([38, 92, 178.0]), col)
    return np.clip(col, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Save / load
# ---------------------------------------------------------------------------
LAYER_DOC = {
    "elevation": ("m", "ground elevation (lake beds included), sea level 0"),
    "water": ("enum", "0 land, 1 sea, 2 lake"),
    "lake_depth": ("m", "water depth in lakes (lake surface = elevation + lake_depth)"),
    "discharge": ("m^3/s", "mean river discharge (precipitation routed downhill, plus inflow at the edges; "
                           "open lakes pass theirs on at the outlet; split among delta distributaries)"),
    "drainage_area": ("km^2", "upstream area inside the region"),
    "precipitation": ("mm/yr", "annual precipitation (interpolated from the coarse world)"),
    "temperature": ("C", "mean annual temperature, lapse-rate adjusted to the fine elevation"),
    "ice": ("m", "land ice thickness (interpolated)"),
    "rock": ("ROCKS id", "basement rock (surface.ROCKS)"),
    "surface_rock": ("ROCKS id", "exposed rock: basement or sediment cover"),
    "climate": ("KOPPEN id", "Koppen class; alpine tundra/ice cap added from the fine elevation"),
    "biome": ("BIOMES id", "climate.biomes on the fine fields"),
}


def zoom_id(world_id: str, lat: float, lon: float, size_km: float, res_km: float, seed: int) -> str:
    key = f"{world_id}|{lat:.4f}|{lon:.4f}|{size_km:g}|{res_km:g}|{seed}"
    return hashlib.sha1(key.encode()).hexdigest()[:6]


def save(z: dict, world_path: Path, world: dict, lat: float, lon: float, size_km: float, res_km: float,
         seed: int) -> Path:
    world_id = world_path.stem
    zid = zoom_id(world_id, lat, lon, size_km, res_km, seed)
    out = S.path_of("zoom", zid)
    out.mkdir(parents=True, exist_ok=True)
    layout = S.write_layers(out, z["layers"], {k: {"units": LAYER_DOC[k][0], "description": LAYER_DOC[k][1]}
                                               for k in z["layers"]})
    h = z["layers"]["elevation"].astype(float)
    lo, hi = float(np.floor(h.min())), float(np.ceil(h.max()))
    hi = max(hi, lo + 1)
    write_png(out / "heightmap.png", np.round((h - lo) / (hi - lo) * 65535).astype(np.uint16))
    write_png(out / "preview.png", preview(z))
    write_png(out / "coarse.png", coarse_image(z))
    fr: Frame = z["frame"]
    half = size_km / 2
    corners = {k: [round(v, 4) for v in _latlon(fr.to_sphere(np.array([x]), np.array([y]))[0])]
               for k, (x, y) in {"nw": (-half, half), "ne": (half, half), "se": (half, -half),
                                 "sw": (-half, -half)}.items()}
    m = world["meta"]
    meta = {
        "format": "procgen-zoom/2",
        "id": zid,
        "name": f"{world.get('name') or world_id}: {lat:g}, {lon:g} ({size_km:g} km @ {z['res']:g} km)",
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "generated_in_s": z["seconds"],
        "source_world": {"id": world_id, "file": f"worlds/{world_path.name}", "name": world.get("name"),
                         "source_run": m.get("source_run"), "t_myr": m.get("t_myr"), "level": m.get("level")},
        "center": {"lat": lat, "lon": lon},
        "size_km": size_km,
        "res_km": z["res"],
        "nx": z["nx"], "ny": z["ny"],
        "seed": seed,
        "projection": {
            "type": "azimuthal_equidistant", "lat0": lat, "lon0": lon, "planet_radius_km": R_KM,
            "pixel_x_km": "(col + 0.5 - nx/2) * res_km   (east of centre)",
            "pixel_y_km": "(ny/2 - row - 0.5) * res_km   (north of centre; row 0 = north edge)",
            "corners_latlon": corners,
        },
        "files": {"heightmap": "heightmap.png", "preview": "preview.png", "coarse": "coarse.png"},
        "layers": layout,
        "heightmap": {"bits": 16, "min_m": lo, "max_m": hi,
                      "sea_level_value": int(round((0 - lo) / (hi - lo) * 65535)) if lo < 0 < hi else None,
                      "formula": "elev_m = min_m + value / 65535 * (max_m - min_m)",
                      "metres_per_step": round((hi - lo) / 65535, 4)},
        "legend": S.legends(),
        "params": z["params"],
        "stats": z["stats"],
    }
    (out / "zoom.json").write_text(json.dumps(meta, indent=1))
    update_index()
    return out


def load(ref: str | Path) -> tuple[dict, dict]:
    """(meta, {layer: (ny, nx) array}) for zooms/<id> (or a path to it)."""
    d = S.find_zoom(ref)
    meta = json.loads((d / "zoom.json").read_text())
    return meta, S.read_layers(d, meta["layers"])


def update_index():
    S.update_index("zoom")


def zoom(world_ref: str, lat: float, lon: float, size_km: float = 1000.0, res_km: float = 2.0, seed: int = 1,
         iterations: int = 15, log=print) -> Path:
    if not -90 <= lat <= 90:
        raise SystemExit("--lat must be within -90..90")
    if not 10 <= size_km <= 5000:
        raise SystemExit("--size-km must be within 10..5000")
    if size_km / res_km > 4096:
        raise SystemExit("too many pixels: keep size-km / res-km <= 4096")
    path = find_world(world_ref)
    world = W.load(path)
    if "rock" not in world["layers"]:
        raise SystemExit("this world has no rock/climate layers; zoom needs a world sliced from a tectonic run")
    lon = (lon + 180) % 360 - 180
    z = build(world, lat, lon, size_km, res_km, seed, iterations, log=log)
    return save(z, path, world, lat, lon, size_km, res_km, seed)
