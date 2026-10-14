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
   Volcanoes (zoom_volcanoes): every volcano of the world's table becomes
   its own cone (shield or stratocone, eroded, planed or ringed by a reef
   as the run says); near hotspot vents on the sea floor the terrain is
   replaced by their floor plus the cones, so the sea between them is sea.
   Young ones are held at their smooth cone in the landscape pass.
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
   Above each fall the river runs on a plateau as high as the fall, back
   up to where it meets the valley floor (staircase()); the falls are
   scaled down until that plateau is nowhere above the coarse ground.
   Tributaries join such a reach at the staircase's level. Near the
   zoom's own coast, river floors rise at most COAST_FLOOR_GRAD m/km.
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
   the outlet (in a corridor along its river) steps down at most
   RAPIDS_GRAD m/km (rapids, not a cliff).
   A closed lake's smaller fragments drain to its biggest one; a fragment
   that should drain but finds no outlet becomes land (no fragment
   swallows its rivers).
   Distributaries take their share of the water at each split. The coarse
   rivers keep at least their valley floor (the staircase, with its falls,
   only in the valley bottom); a reach with falls has its receivers pinned
   along its course, the river held at its staircase (floor and cap; no
   higher than its foot below it, down to the next confluence) and valley
   sides a few km wide held above it (banks()), so the river reaches its
   lips and doesn't run perched above the land beside it; each fall's gorge has walls held at the lip's level (cliffs,
   hanging side valleys), and a plunge pool (a small lake) at its foot.
   Summits taper above a soft cap; hillslopes get some creep (channels
   stay sharp: creep never lifts a stream's bed, but for a little under
   ice).
   Landform classes (zoom_landforms, PW-010..012): each coarse cell's class
   reshapes the finished landscape, blended by smooth class weights: the
   relief around the drainage (flat interfluves over steep valley walls)
   and hard beds as benches and cliffs (a great escarpment's scarp, caprock
   benches, mesas and cuestas, a lava plateau's stepped valley sides);
   rivers crossing a cliff fall over it. Sills across a flow path are cut
   through and each coarse cell's mean is kept. A designed reach crossing
   an escarpment takes its main fall at the scarp, with the plateau above
   it (the ground it must fit under is lifted: scarp_fall). Any pits
   left are filled. Falls are listed only where the drop stands out from
   the river around it (waterfalls()).

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

from . import climate, coast, hydrology, kernels
from . import store as S
from . import world as W
from . import zoom_kernels as ZK
from . import zoom_landforms as ZL
from . import zoom_volcanoes as ZV
from .geo import R_KM, latlon, xyz
from .images import write_png
from .climate import LAPSE
from .surface import ROCK_K

SEC_PER_YR = 3.156e7
KM2_M_PER_YR_TO_M3S = 1e6 / SEC_PER_YR  # discharge unit used internally -> m^3/s

# How rugged the sub-cell detail is, by basement rock (surface.ROCKS ids).
RUGGED = {0: 0.35, 1: 0.85, 2: 0.9, 3: 0.45, 4: 1.0, 5: 0.35, 11: 0.6}
SEA_CLIMATE = 30  # KOPPEN "-"
LIMESTONE = 6  # surface.ROCKS
# landscape pass: discharge exponent of the steady-state slope, hillslope
# creep per smoothing step (and number of steps), steepest slope allowed
SPL_M, KD, MAX_SLOPE, SMOOTH_STEPS = 0.5, 0.25, 450.0, 6  # MAX_SLOPE in m/km
DELTA_MIN_Q = 1500.0  # m^3/s at a coarse river mouth for a delta plain
BRANCH_MAX_Z = 250.0  # m: distributaries aren't laid out where the target surface is higher than this


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
def _count(items) -> dict:
    out = {}
    for k in items:
        out[k] = out.get(k, 0) + 1
    return out


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
# biggest drop of the water surface over <= WF_STEPS pixels (and <= WF_MAX_KM)
# downstream that is >= WF_MIN_DROP m and steeper than WF_MIN_GRAD m/km on average.
WF_MIN_Q, WF_MIN_DROP, WF_MIN_GRAD, WF_STEPS = 50.0, 30.0, 15.0, 3
WF_MAX_KM = 5.0  # ... and over at most this far (at least one pixel): on coarse pixels a steep reach isn't a fall
WF_EDGE_PX = 8  # ... and not next to the region's edge (held at the target surface: steps into it aren't falls)
WF_CONTRAST, WF_CONTEXT_KM = 3.0, 6.0  # ... and WF_CONTRAST x steeper than the river within WF_CONTEXT_KM (see waterfalls())


def waterfalls(ws: np.ndarray, q: np.ndarray, rec: np.ndarray, nx: int, ny: int, res: float,
               starts: dict | None = None, top: int = 5, designed=()) -> list[dict]:
    """Pixel-scale falls along the drainage network. ws: water surface (lake
    surface on lakes, 0 at sea), q: discharge m^3/s, rec: D8 receivers (-1
    at outlets); starts: {lake outlet pixel: lake level}, where a fall
    starts at the lake surface a pixel upstream. A drop that isn't at a
    lake outlet or within 3 px of a `designed` lip pixel must stand out from
    the river around it: at least WF_CONTRAST x as steep as the reaches
    just above and below it (else it's a steep reach, rapids or a cascade
    of a mountain stream, not a fall: coarse pixels and small steep streams
    have many). Best first by power (discharge x height), at least ~15 km
    apart, none within WF_EDGE_PX of the edge. Each: px (row, col), height_m,
    length_km, discharge_m3s, power_gw, top_m, bottom_m, from_lake."""
    n = nx * ny
    lvl, d0 = ws.astype(float).copy(), np.zeros(n)
    for o, v in (starts or {}).items():
        if o >= 0 and v > lvl[o]:
            lvl[o], d0[o] = v, res
    row, col = np.divmod(np.arange(n), nx)
    e = WF_EDGE_PX
    inner = (row >= e) & (row < ny - e) & (col >= e) & (col < nx - e)
    i = np.flatnonzero((q >= WF_MIN_Q) & inner & (rec >= 0))
    # a lake outlet's own step (lake surface -> outlet pixel) counts as one
    drop = lvl[i] - ws[i]
    ok = (d0[i] > 0) & (drop >= WF_MIN_GRAD * np.maximum(d0[i], 1e-9))
    best_h, best_d, best_j = np.where(ok, drop, 0.0), d0[i].copy(), i.copy()
    j, dist, alive = i.copy(), d0[i].copy(), np.ones(len(i), bool)
    for _ in range(max(1, min(WF_STEPS, int(WF_MAX_KM // res)))):
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
    # concentrated: steeper than the river above and below (over ~2x the
    # fall's length, at least WF_CONTEXT_KM), by WF_CONTRAST
    up = np.full(n, -1)
    o = np.argsort(q, kind="stable")
    o = o[rec[o] >= 0]
    up[rec[o]] = o  # main donor (the biggest; the last write wins)
    ctx = max(2.0 * res, WF_CONTEXT_KM)

    def walk(start, nxt, length):
        """(pixel, km) after following nxt (up or rec) from start for ~length km."""
        p, km = start.copy(), np.zeros(len(start))
        for _ in range(int(np.ceil(length / res)) + 1):
            r = nxt[p]
            go = (r >= 0) & (km < length)
            if not go.any():
                break
            rr = np.maximum(r, 0)
            diag = (rr % nx != p % nx) & (rr // nx != p // nx)
            km = np.where(go, km + res * np.where(diag, 1.4142, 1.0), km)
            p = np.where(go, rr, p)
        return p, km

    L = np.maximum(2 * d, ctx)
    pu, ku = walk(i, up, float(L.max()) if len(L) else 0.0)
    pd_, kd_ = walk(jj, rec, float(L.max()) if len(L) else 0.0)
    g_ctx = (np.maximum(ws[pu] - lvl[i], 0) + np.maximum(ws[jj] - ws[pd_], 0)) / np.maximum(ku + kd_, res)
    fixed = d0[i] > 0  # (lake outlets and designed lips are falls whatever the river around them)
    r_, c_ = np.divmod(i, nx)
    for p in designed:
        a, b = divmod(int(p), nx)
        fixed |= (np.abs(r_ - a) <= 3) & (np.abs(c_ - b) <= 3)
    ok = fixed | (h / np.maximum(d, 1e-9) >= WF_CONTRAST * g_ctx)
    i, h, d, jj = i[ok], h[ok], d[ok], jj[ok]
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
# - lip resistance R (0..1) from the exposed stratum when it is at least
#   LIP_CAP_KM thick (a caprock holds the lip by itself), else the harder of
#   it and the rock under it (strata_next: a sandstone veneer over shield
#   granite holds a lip like the granite does): KP_RESIST, lip_resistance();
# - concentrated fraction f = (0.25 + 0.45 R) / (1 + Q / 50,000)^0.3: hard
#   lips hold more, the biggest rivers wear their lips into cataracts
#   (Niagara: ~51 of ~99 m between the lakes; the Congo's Livingstone falls:
#   ~270 m as 30-odd rapids);
# - split into n = 1 + 1.5 log10(1 + Q / 2000) steps (1-5), shares falling
#   off by KP_SHARE: the main fall at the lip, the rest as cascades spread
#   down the reach below the gorge;
# - the lip has retreated from the escarpment (the middle of the steepest
#   link) upstream by a gorge of length 4 km x sqrt(Q / 1000 m^3/s) x
#   (1.5 - R) x the undercut of the rock under the lip (0.6 granite .. 1.4
#   evaporite: lip_undercut(); Niagara, dolomite over shale: ~8 km at ~6,000
#   m^3/s, ~11 km real), at most 60 km and most of the reach above the
#   escarpment.
KP_MIN_GRAD, KP_GRADED, KP_MIN_EXCESS, KP_MIN_Q = 0.8, 0.2, 50.0, 100.0  # m/km, m/km, m, m^3/s
KP_SHARE, KP_MAX_H, KP_MIN_STEP = 0.55, 1000.0, 8.0
# how well each rock (surface.ROCKS id) holds a lip
KP_RESIST = {0: 0.8, 1: 0.9, 2: 0.8, 3: 0.4, 4: 0.85, 5: 1.0, 6: 0.75, 7: 0.7, 8: 0.2, 9: 0.1, 10: 0.3,
             11: 1.0, 12: 0.95, 13: 0.9, 14: 0.85, 15: 0.5}
COAST_FLOOR_GRAD = 2.0  # m/km: a river's valley floor rises no faster than this from the coast
RAPIDS_GRAD = 2.0  # m/km: a lake's outflow steps down no faster than this below its outlet (and any fall there)
FALLS_MIN_SHARE = 0.05  # a reach's falls are placed from where its pinned course carries this share of the coarse discharge
SETTLE_M = 10.0  # m: an uphill step along a pinned course up to this high is evened out, a bigger one unpinned
BANK_KM, BANK_SIDE_GRAD = 4.0, 30.0  # held river courses: banks this wide (km, >= 2 px), then falling off (m/km)
ICE_SNOUT_GRAD = 50.0  # m/km: under ice, creep may lift a stream's bed by this much per km in from the ice's edge
BANK_MAX_Q = 300.0  # m^3/s: ... not lifting other rivers carrying this much
LIP_CAP_KM = 0.5  # km: a top stratum this thick holds a lip by itself (see lip_resistance)
SCARP_MIN_W = 0.3  # a designed reach takes its main fall at a landform scarp where the class weighs this much
LF_CHANNEL_Q = 5.0  # m^3/s: landform relief (zoom_landforms) is shaped around channels carrying this much


def _under(surface_rock, basement, cover_km, top_km=None, next_rock=None) -> int:
    """The rock under the exposed one: the next stratum (strata_next), else,
    without strata layers, the basement under a thin cover (the cover's own
    mix otherwise)."""
    if next_rock is not None:
        return int(next_rock)
    return int(basement) if cover_km < 0.5 else int(surface_rock)


def lip_resistance(surface_rock: int, basement: int, cover_km: float, top_km: float | None = None,
                   next_rock: int | None = None) -> float:
    """How well the exposed rock holds a lip (0..1). A top stratum at least
    LIP_CAP_KM thick holds it by itself, hard over soft or not (Niagara: the
    dolomite cap, whatever the shale below does); a thinner one is soon cut
    through, and the rock under it (the next stratum, or the basement under
    a thin cover: strata_next) holds it if that is harder."""
    r = KP_RESIST.get(int(surface_rock), 0.5)
    thin = (cover_km if top_km is None else top_km) < LIP_CAP_KM
    if thin:
        r = max(r, KP_RESIST.get(_under(surface_rock, basement, cover_km, top_km, next_rock), 0.5))
    return r


def lip_undercut(surface_rock: int, basement: int, cover_km: float, top_km: float | None = None,
                 next_rock: int | None = None) -> float:
    """How fast a fall's gorge retreats for the rock under its lip (x the
    lip's own term): soft rock under the cap is undercut, the cap breaks off
    and the fall walks back (Niagara: shale under the dolomite), hard rock
    under it slows it. 0.6 (granite) .. 1.4 (evaporite)."""
    return 0.6 + 0.8 * (1 - KP_RESIST.get(_under(surface_rock, basement, cover_km, top_km, next_rock), 0.5))


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
        gorge = float(min(4.0 * np.sqrt(Q / 1000) * (1.5 - R) * lip_undercut(*rock[cells[k]]), 60.0,
                          0.8 * s_e + 0.4 * (s[(k + 1) * (m - 1)] - s_e)))
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
    floor between the falls, 'cont' at arc lengths 's_c', added by
    staircase()) at arc lengths sv km."""
    return np.interp(sv, kp["s_c"], kp["cont"]) - sum(st["h"] * (sv >= st["s"]) for st in kp["steps"])


def _raster_path(line: np.ndarray, res: float, nx: int, ny: int) -> tuple[np.ndarray, np.ndarray]:
    """Pixels (8-connected, no repeats; -1 where it's off the raster) along
    a polyline in km (x east, y north of the centre), and the arc length
    along the line at each."""
    seg = np.hypot(*np.diff(line, axis=0).T)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    t = np.arange(0.0, s[-1] + 1e-9, 0.25 * res)
    x, y = np.interp(t, s, line[:, 0]), np.interp(t, s, line[:, 1])
    c, r = np.floor(x / res + nx / 2).astype(int), np.floor(ny / 2 - y / res).astype(int)
    p = np.where((c >= 0) & (c < nx) & (r >= 0) & (r < ny), r * nx + c, -1)
    new = np.r_[True, p[1:] != p[:-1]]
    out, arc, seen = [], [], {}
    for q, tq in zip(p[new], t[new]):
        if q >= 0 and q in seen:  # a loop: cut it out
            for o in out[seen[q] + 1:]:
                seen.pop(o, None)
            del out[seen[q] + 1:], arc[seen[q] + 1:]
            continue
        if q >= 0:
            seen[q] = len(out)
        out.append(int(q))
        arc.append(float(tq))
    # Where a loop was cut out (a meander coming back across its own pixel),
    # the arc length jumps: let the course's arc lag and catch up at most 1.5x
    # as fast as it goes, so its floor doesn't drop the loop's fall in one step.
    out, arc = np.array(out, dtype=np.int64), np.array(arc)
    for k in range(1, len(arc)):
        a, b = out[k - 1], out[k]
        if a < 0 or b < 0:  # (off the raster: no pixels to lag on)
            continue
        step = res * (1.4142 if a % nx != b % nx and a // nx != b // nx else 1.0)
        arc[k] = min(arc[k], arc[k - 1] + 1.5 * step)
    return out, arc


def _stair_floor(s: np.ndarray, tz: np.ndarray, steps: list, f: float) -> np.ndarray:
    """The floor at arc lengths s (ascending, the lips' own s and just above
    them included) of a reach whose valley floor is tz, with each step's
    height scaled by f: below the lowest fall the valley floor; above each
    lip a plateau graded at KP_GRADED, until it meets the valley floor."""
    z = tz.copy()
    for st in sorted(steps, key=lambda st: -st["s"]):  # downstream first
        top = np.interp(st["s"], s, z) + f * st["h"]
        up = s < st["s"]
        z[up] = np.maximum(z[up], top + KP_GRADED * (st["s"] - s[up]))
    return z


def staircase(kp: dict, tz: np.ndarray, ez: np.ndarray) -> float:
    """Fit the falls of a reach (knickpoints()) into its valley. tz: the
    valley floor, ez: the coarse ground, both at kp["s"]. Above each fall
    the river runs on a plateau as high as the fall (_stair_floor()), which
    must fit in the land: the floor stays no higher than the coarse ground,
    and joins the river above the reach no higher than the valley floor
    there. (Before, the whole reach's floor was lifted to hold the falls at
    its far end: the river ran on a ridge, hundreds of metres above the land
    beside it, and the fine river left it wherever it could, dropping off
    the side in a bare step, at no lip.) Scales the steps' heights down to
    fit (returned: the factor) and sets kp["s_c"], kp["cont"] for stair_z()."""
    s = kp["s"]
    tz = np.minimum.accumulate(tz)
    lips = np.array([st["s"] for st in kp["steps"]])
    sc = np.unique(np.concatenate([s, lips, np.maximum(lips - 1e-3, 0.0)]))
    t = np.interp(sc, s, tz)
    ceil = np.maximum(np.interp(sc, s, ez), t)
    ceil[0] = t[0]

    def fits(f):
        return np.all(_stair_floor(sc, t, kp["steps"], f) <= ceil + 1e-6)

    lo, hi = 0.0, 1.0
    if not fits(hi):
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if fits(mid) else (lo, mid)
    else:
        lo = 1.0
    for st in kp["steps"]:
        st["h"] *= lo
    z = _stair_floor(sc, t, kp["steps"], 1.0)
    kp["s_c"] = sc
    kp["cont"] = z + sum(st["h"] * (sc >= st["s"]) for st in kp["steps"])
    return lo


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
        R = coast.plain_radius_km(float(q[k]), sf)
        if max(abs(mx), abs(my)) > size_km / 2 + 0.5 * R:
            continue
        if any(np.hypot(mx - o["x"], my - o["y"]) < 0.8 * o["R"] for o in out):
            continue
        # Galloway weights: the river's sediment against the waves and tides
        # at the mouth (coast.py), the marine values from the sea cells
        # around the mouth (the world's wave_power / tide_range layers)
        gw = coast.delta_at(g, L, int(i), float(q[k]), R)
        w, wave, tide, marine = gw["weights"], gw["wave_power_kw_m"], gw["tide_range_m"], gw["marine"]
        nbr = int(np.clip(round(1 + 1.2 * np.log10(q[k] / 1000) + 1.5 * sf), 2, 6))
        # waves rework the mouths into one or two; tides open many
        n_mouths = int(np.clip(round(nbr * (1 - 0.75 * w["wave"]) + 4 * w["tide"]), 1, 9))
        out.append({"x": mx, "y": my, "u": u, "q": float(q[k]), "sf": sf, "R": R,
                    "Rl": 0.22 * R * (0.6 + 0.8 * sf), "cell": int(i), "wave": wave, "tide": tide,
                    "marine": marine, "gw": gw, "wR": w["river"], "wW": w["wave"], "wT": w["tide"],
                    "nb": n_mouths})
    return out


def _coast_along(ind, nx: int, ny: int, res: float, x0: float, y0: float, d, smax: float) -> float:
    """Distance (km) from (x0, y0) along unit vector d to where the land/sea
    indicator ind (per pixel) first turns negative (the coast); smax if it
    doesn't within smax, 0 if it starts at sea."""
    for s in np.arange(0.0, smax, 0.5 * res):
        c = int(np.floor((x0 + s * d[0]) / res + nx / 2))
        r = int(np.floor(ny / 2 - (y0 + s * d[1]) / res))
        if 0 <= r < ny and 0 <= c < nx and ind[r * nx + c] < 0:
            return float(s)
    return float(smax)


def _delta_forms(dl: dict, px, py, res: float, rng, ind, nx: int, ny: int) -> dict:
    """The delta's shape in the land/sea indicator, from its Galloway
    weights (wR, wW, wT), each part scaled by its weight so mixed deltas
    get a mix (nothing is switched on or off by type):
    - lobe: new land pushed out to sea; long and narrow for a river-
      dominated delta, a broad low arc for a wave-dominated one, little for
      a tide-dominated one;
    - fingers (river): narrow strips of levee-bound land along each
      distributary, prograding far out into the sea (the bird's foot);
    - funnels (tide): estuaries along the coast that widen seaward
      exponentially (half-width ~ exp(s / Lb)), and a mesh of tidal creeks
      stretched along the flow that cuts the plain into elongate islands;
    - smooth: how much the coastline noise is damped (waves straighten the
      shore into a smooth arc; the fingers keep clean edges).
    Everything is placed relative to the coast as the land/sea indicator
    ind (per pixel) draws it, which can lie tens of km from the coarse mouth.
    Returns per-pixel fields (lobe: added to the indicator, cut: taken
    off it, keep: a floor for it, smooth: 0..1) and the points the distributaries should head for
    (finger tips or funnel heads; empty: fan out over the coast)."""
    R, Rl, wR, wW, wT = dl["R"], dl["Rl"], dl["wR"], dl["wW"], dl["wT"]
    # seaward: toward the sea as the indicator has it around the mouth (the
    # coarse cells' direction can be ~45 deg off the fine coast's)
    ang = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    rx, ry = dl["x"] + 0.4 * R * np.cos(ang), dl["y"] + 0.4 * R * np.sin(ang)
    cc = np.clip(np.floor(rx / res + nx / 2).astype(int), 0, nx - 1)
    rr_ = np.clip(np.floor(ny / 2 - ry / res).astype(int), 0, ny - 1)
    sea_w = np.clip(-ind[rr_ * nx + cc], 0, None)
    u = np.asarray(dl["u"], float)
    if sea_w.sum() > 0:
        v = np.array([np.sum(sea_w * np.cos(ang)), np.sum(sea_w * np.sin(ang))])
        if np.linalg.norm(v) > 1e-9:
            u = v / np.linalg.norm(v)
    dl["u"] = u
    t = np.array([-u[1], u[0]])
    dx, dy = px - dl["x"], py - dl["y"]
    r = np.hypot(dx, dy)
    a, b = dx * u[0] + dy * u[1], dx * t[0] + dy * t[1]  # along (seaward) and across the mouth
    near = r < 2.5 * R
    lobe, cut, smooth, keep = (np.zeros_like(px) for _ in range(4))
    keep -= 9.0
    # the lobe, centred on the coast seaward of the mouth: out ~0.3 R, and wide for waves
    s0 = _coast_along(ind, nx, ny, res, dl["x"], dl["y"], u, 1.5 * R)
    la = R * (0.12 + 0.08 * wR + 0.25 * wW)
    lb = R * (0.3 - 0.1 * wR + 0.7 * wW + 0.2 * wT)
    amp = 1.0 - 0.5 * wT
    lobe[near] = amp * np.exp(-((a[near] - s0) / la) ** 2 - (b[near] / lb) ** 2)
    dl["lobe_at"] = (dl["x"] + s0 * u[0], dl["y"] + s0 * u[1])
    smooth[near] = smoothstep(1.4 * R, 0.9 * R, r[near]) * np.clip(0.85 * wW + 0.5 * wR, 0, 0.9)
    goals, kind = [], "fan"
    n = dl["nb"]
    # fingers: from the mouth out along a fan of directions
    Lf = R * 1.1 * wR ** 2  # (the Mississippi's bird's foot reaches ~100 km out from a ~250 km plain)
    if Lf > 3 * res and n >= 1:
        wf = max(2.0 * res, 0.06 * R)
        spread = np.radians(50 + 15 * min(n, 5))
        th = (np.linspace(-0.5, 0.5, n) if n > 1 else np.zeros(1)) * spread + rng.normal(0, 0.08, n)
        for k in range(n):
            dk = np.cos(th[k]) * u + np.sin(th[k]) * t
            Lk = Lf * rng.uniform(0.6, 1.1)
            Lk += _coast_along(ind, nx, ny, res, dl["x"], dl["y"], dk, 1.5 * R)  # out from the coast
            s = dx * dk[0] + dy * dk[1]
            c = np.abs(dx * dk[1] - dy * dk[0])
            f = np.exp(-(c / wf) ** 2) * smoothstep(-0.3 * Lk, 0.0, s) * smoothstep(Lk, 0.85 * Lk, s)
            # land at least along the axis, wider the more the river dominates
            # (none below a river weight of ~0.4)
            keep = np.maximum(keep, 0.3 * (1.6 * wR * f - 0.6))
            goals.append((dl["x"] + Lk * dk[0], dl["y"] + Lk * dk[1]))
        kind = "fingers"
    # funnels: spread along the coast either side of the mouth
    amp_t = 1.6 * wT
    if amp_t > 0.3:
        span = 1.2 * R
        Wm = (0.05 + 0.07 * wT) * R  # half-width at the coast
        Lb = 0.25 * R  # convergence length: the width e-folds over this far inland
        Lfun = (0.2 + 0.3 * wT) * R  # how far inland the funnel reaches
        nf = max(n, 2)
        heads = []
        for k in range(nf):
            o = (k / (nf - 1) - 0.5) * span + rng.normal(0, 0.04 * span)
            fan = 0.35 * o / span + rng.normal(0, 0.05)
            dk = np.cos(fan) * u + np.sin(fan) * t
            cx_, cy_ = dl["x"] + o * t[0], dl["y"] + o * t[1]
            sc = _coast_along(ind, nx, ny, res, cx_, cy_, dk, 1.5 * R)  # its mouth on the coast
            cx_, cy_ = cx_ + sc * dk[0], cy_ + sc * dk[1]
            ex, ey = px - cx_, py - cy_
            s = ex * dk[0] + ey * dk[1]
            c = np.abs(ex * dk[1] - ey * dk[0])
            hw = np.maximum(Wm * np.exp(np.minimum(s, 0.6 * R) / Lb), 0.6 * res)
            f = smoothstep(hw, 0.5 * hw, c) * smoothstep(-Lfun, -Lfun + 2 * res, s) * (s < 0.8 * R)
            f *= smoothstep(0.85 * R, 0.6 * R, r)  # within the plain (no estuaries cut into hills)
            cut = np.maximum(cut, amp_t * f)
            heads.append((cx_ - Lfun * dk[0], cy_ - Lfun * dk[1]))
        if wT >= wR:
            goals, kind = heads, "funnels"
        # tidal creeks: the zero lines of a noise field stretched 3.5x along
        # the flow (long channels, few cross-links: elongate islands)
        zone = smoothstep(0.8 * R, 0.5 * R, r) * smoothstep(s0 - 0.6 * R, s0 - 0.3 * R, a)
        pts = np.ascontiguousarray(np.column_stack([a / 3.5, b, np.full_like(a, 1000.0 * (dl["cell"] % 97))]))
        nn = ZK.fbm(pts, 0.15 * R, 3, 0.5, 977 + dl["cell"]) / 0.17
        creek = smoothstep(0.12, 0.0, np.abs(nn))
        cut = np.maximum(cut, 1.3 * wT * creek * zone)
    return {"lobe": lobe, "cut": cut, "smooth": smooth, "keep": keep, "goals": goals, "kind": kind}


def _count_mouths(dl: dict, px, py, land, rec, discharge, nx: int, ny: int) -> int:
    """Channels of a delta reaching the sea: groups of land pixels within
    1.6 R of the mouth that drain straight into the sea carrying >= 5% of
    the delta's discharge."""
    r = np.hypot(px - dl["x"], py - dl["y"])
    out = land & (rec >= 0) & ~land[np.maximum(rec, 0)] & (r < 1.6 * dl["R"]) & (discharge >= 0.05 * dl["q"])
    if not out.any():
        return 0
    lab, _ = ZK.label_components(out, nx, ny)
    return int(len(np.unique(lab[out])))


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
    wD, zD, wS, zS, wC, lobe, cut, smooth_c, wR_f, wW_f = (np.zeros(npx) for _ in range(10))
    keep = np.full(npx, -9.0)
    hf = 1 - smoothstep(250.0, 800.0, e_land)  # no plain against high ground
    for j, dl in enumerate(deltas):
        R = dl["R"]
        r = np.hypot(px - dl["x"], py - dl["y"])
        w = smoothstep(R, 0.55 * R, r) * hf
        zD = np.where(w > wD, coast.PLAIN_Z0 + coast.PLAIN_RISE * (r / R) ** 1.5, zD)
        wR_f, wW_f = np.where(w > wD, dl["wR"], wR_f), np.where(w > wD, dl["wW"], wW_f)
        wD = np.maximum(wD, w)
        zS = np.where(r < 1.2 * R, np.maximum(zS, -(2.0 + 50.0 * (r / R) ** 2)), zS)
        wS = np.maximum(wS, smoothstep(1.2 * R, 0.5 * R, r))
        wC = np.maximum(wC, smoothstep(1.4 * R, 0.8 * R, r))
        # its shape from the Galloway weights; the lobe lifts the land/sea
        # indicator at its centre to a little above the coast value
        f = _delta_forms(dl, px, py, res, np.random.default_rng(seed * 7919 + 101 + j), ind, nx, ny)
        lc = np.asarray(dl["lobe_at"])
        k = int(np.argmin((px - lc[0]) ** 2 + (py - lc[1]) ** 2))
        amp_l = np.clip(0.35 - ind[k], 0.0, 2.0) if np.hypot(px[k] - lc[0], py[k] - lc[1]) < 2 * res else 1.0
        lobe += amp_l * f["lobe"]
        cut = np.maximum(cut, f["cut"])
        smooth_c = np.maximum(smooth_c, f["smooth"])
        keep = np.maximum(keep, f["keep"])
        dl["goals"], dl["form"] = f["goals"], f["kind"]
    zS = np.where(wS > 0, zS, -1e9)

    # --- coastline -------------------------------------------------------
    lam = 0.9 * sp
    cw = ZK.fbm(Pk, lam, 4, 0.5, S + 7) / 0.17 * 0.12 * sp  # domain warp: bays, headlands
    Pc = np.ascontiguousarray(Pk + cw[:, None] * np.array([0.57, -0.41, 0.71]))
    coast_n = ZK.fbm(Pc, lam, _octaves(lam, 2 * res), 0.62, S + 1) / 0.15
    ind_n = np.maximum(ind + 0.22 * coast_n * (1 - smooth_c) + lobe, keep) - cut
    # Wave-dominated deltas: a barrier of sand along the flanks, with a
    # lagoon behind it (broken by a few tidal inlets), its width growing
    # with the wave weight above ~0.3.
    lagoon = np.zeros(npx, bool)
    if any(dl["wW"] > 0.3 for dl in deltas):
        din = ZK.inside_distance(ind_n > 0, nx, ny) * res  # km inside the coast
        gate = ZK.fbm(Pk, 40.0, 2, 0.5, S + 51) / 0.17
        for dl in deltas:
            if dl["wW"] <= 0.3:
                continue
            R = dl["R"]
            dx, dy = px - dl["x"], py - dl["y"]
            r = np.hypot(dx, dy)
            flank = np.abs(dx * dl["u"][0] + dy * dl["u"][1]) < 0.7 * np.maximum(r, 1e-9)
            bw = max(2.0 * res, 3.0)  # barrier width, km (at least 2 px)
            lw = max(1.0 * res, (dl["wW"] - 0.3) / 0.7 * 0.08 * R)  # lagoon width
            band = (din > bw + 0.1 * res) & (din <= bw + lw) & (r > 0.2 * R) & (r < 1.1 * R) & flank & (hf > 0.5)
            inlet = (din > 0) & (din <= bw + 0.1 * res) & (r > 0.2 * R) & (r < 1.1 * R) & flank & (gate < -0.75)
            lagoon |= band | inlet
        ind_n = np.where(lagoon, np.minimum(ind_n, -0.05), ind_n)
        log(f"  lagoons: {int(lagoon.sum())} px")
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
    # --- volcanoes (zoom_volcanoes): each one its own cone -----------------
    vf = ZV.fields(world, fr, px, py, res, sp, Pk, seed, size_km)
    vtarget = np.full(npx, np.nan)  # the volcanoes' surface, for the landscape pass
    if vf is not None:
        # (not over a continent; a pile of hotspot lava capped with reef
        # limestone counts as continental crust in the run, so it stays in)
        ok_c = (np.asarray(L.get("crust", np.zeros(g.n)))[sel] == 0) | (rock[sel] == 1)
        oceanic, _ = ZK.gauss_interp(px, py, cx, cy, ok_c[:, None].astype(float), np.ones((len(sel), 1)), 0.35 * sp)
        oceanic = smoothstep(0.3, 0.7, np.nan_to_num(oceanic[:, 0]))
        wv = vf["province"] * oceanic * np.isfinite(vf["floor"])
        # the vents' sea floor: the terrain lowered by as much as its coarse
        # level stands above their floor (the coarse cells' share of the
        # cones themselves), keeping its texture
        ground = h - np.maximum(base - np.nan_to_num(vf["floor"], nan=-1e4), 0.0)
        ground = np.where(wv > 0, (1 - wv) * h + wv * ground, h)
        # the cones on it (absolute near their summits, on the ground at their edges)
        cz = vf["z"] + (1 - vf["z_abs"]) * (ground - vf["z_floor"])
        cb = vf["bump"] + (1 - vf["bump_abs"]) * (h - vf["bump_floor"])
        hv = np.maximum(ground, cz)
        h = np.maximum(hv, cb)
        land = np.where(wv > 0.5, h > 0, land | (h > 0.5))
        h = np.where(land, np.maximum(h, 0.5), np.minimum(h, -0.5))
        on_v = (wv > 0.5) & np.isfinite(vf["z"]) | np.isfinite(vf["bump"])
        vtarget = np.where(on_v, h, np.nan)
        log(f"  {len(vf['list'])} volcanoes: " + ", ".join(
            f"{n} {k}" for k, n in sorted(_count(v["form"] for v in vf["list"]).items(), key=lambda kv: -kv[1])))
    # waves and tides on the fine grid (from the sea cells): the deltas' tidal
    # flats, and layers of the zoom
    tide_f, wave_f = np.zeros(npx), np.zeros(npx)
    if "tide_range" in L and "wave_power" in L:
        mv, _ = ZK.gauss_interp(px, py, cx, cy, np.column_stack([np.asarray(L["tide_range"], float)[sel],
                                                                 np.asarray(L["wave_power"], float)[sel]]),
                                np.column_stack([~land_c, ~land_c]).astype(float), 0.6 * sp)
        tide_f, wave_f = np.nan_to_num(mv[:, 0]), np.nan_to_num(mv[:, 1])
    delta_floor = np.full(npx, -np.inf)  # beach ridges and levees, held as floors in the landscape pass
    if deltas:
        # Tidal flats: offshore of a tide-influenced delta, a band of sea floor
        # between low and mean tide (exposed at low water), wider with the
        # tide weight. Beach ridges: on a wave-influenced delta plain, old
        # shorelines a few metres high parallel to the coast (spacing
        # exaggerated to a few pixels), broken here and there.
        dsea = ZK.inside_distance(~land, nx, ny, False) * res
        din = ZK.inside_distance(land, nx, ny, False) * res
        gate = ZK.fbm(Pk, 30.0, 2, 0.5, S + 52) / 0.17
        lam_r = max(3.0 * res, 3.0)
        for dl in deltas:
            r = np.hypot(px - dl["x"], py - dl["y"])
            Wf = 0.15 * dl["wT"] * dl["R"]
            if Wf > res:
                flat = ~land & (dsea < Wf) & (r < 1.2 * dl["R"])
                h = np.where(flat, np.maximum(h, -0.5 * max(dl["tide"], 0.5) * dsea / Wf - 0.05), h)
                # the funnels and creeks themselves are scoured deep by the tidal
                # currents (flats only along their banks)
                chan = ~land & (cut > 0.4) & (r < 1.1 * dl["R"])
                h = np.where(chan, np.minimum(h, -(1.5 + 0.8 * dl["tide"]) * np.minimum(cut, 1.3)), h)
        ridge = 2.5 * wW_f * np.cos(np.pi * din / lam_r) ** 2 * (gate > -0.3)
        on = land & (wD > 0.5) & (wW_f > 0.25) & (din > 0.5 * res) & (ridge > 0.3)
        delta_floor = np.where(on, zD + ridge, delta_floor)
    log(f"  coast + detail + mean correction [{time.time() - t0:.1f}s]")

    # --- landform classes (zoom_landforms): weights, parameters, hooks ----
    lf = ZL.Landforms.build(L, sel, cx, cy, land_c, px, py, Pk, sp, res, nx, ny, S, land, base,
                            lambda v, w, s: ZK.gauss_interp(px, py, cx, cy, v, w, s))

    def keep_means(z, hh, where, f=None):
        """z with each coarse cell's mean change from hh undone (a smooth
        correction, like the detail's), on `where`, in proportion to f (0..1:
        the land the change came from; the rest keeps its height)."""
        f = np.where(where, 1.0 if f is None else f, 0.0)
        for _ in range(2):
            dsum = np.bincount(own_s, np.where(where, z - hh, 0.0), minlength=len(sel))
            fsum = np.bincount(own_s, f, minlength=len(sel))
            cnt = np.bincount(own_s, minlength=len(sel))
            ok = (cnt > 0.25 * full_px) & (fsum > 0.05 * cnt)
            amp = np.where(ok, -dsum / np.maximum(fsum, np.maximum(0.3 * cnt, 1e-9)), 0.0)  # (a cell barely touched: bounded)
            corr, _ = ZK.gauss_interp(px, py, cx, cy, amp[:, None], ok[:, None].astype(float), 0.5 * sp)
            z = z + f * np.nan_to_num(corr[:, 0])
        return z

    ground_up = None  # where the classes' top beds hold the ground: (weight, level) per pixel (designed falls' fit)
    scarp = None  # single scarps (escarpments): weight, level, height per pixel
    if lf is not None:
        dz = lf.target(h)
        if dz is not None:
            h = clamp(keep_means(h + dz, h, land))
        ground_up = lf.plateau(h)
        scarp = lf.scarps(h)
        log("  landforms: " + ", ".join(f"{k} {v}%" for k, v in lf.stats().items()))

    # --- coarse rivers -> valleys + inflow --------------------------------
    coast_cap = COAST_FLOOR_GRAD * res * ZK.inside_distance(land, nx, ny, False)  # (see z_course)
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
    pin_pairs = []  # (pixel, receiver) along the courses of reaches with falls
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
        # (no meanders near a delta's mouth: the river must arrive at its delta)
        for dl in deltas:
            dd = np.hypot(allp[:, 0] - dl["x"], allp[:, 1] - dl["y"])
            damp = smoothstep(0.3 * dl["R"], 1.5 * dl["R"], dd)
            wx, wy = wx * damp, wy * damp
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
                          {c: (int(srock[c]), int(rock[c]), float(cover_all[c]),
                               *((float(L["strata_top_km"][c]), int(L["strata_next"][c])) if "strata_next" in L else ()))
                           for c in polys})
        # Along a reach with falls the valley floor becomes a staircase: the
        # floor between the falls is graded at what's left of the reach's
        # slope, and drops by each fall's height at its lip.
        zseg = {i: (z1, z2) for _, z1, z2, _, _, i in segs}
        stair = {}

        def scarp_fall(kp, Tz, Ez, pix, inr):
            """A designed reach crossing a landform's scarp (an escarpment):
            the hard bed holds the river on the plateau down to the scarp, so
            the valley floor and the ground above the crossing stand at the
            scarp's level, and the main fall takes (up to) the scarp's
            height, its lip retreated from the crossing by its gorge."""
            ws_, lv_, hg_ = (np.where(inr, a[np.where(inr, pix, 0)], 0.0) for a in scarp)
            on = ws_ > SCARP_MIN_W
            a_ = np.flatnonzero(on & (Ez >= lv_))
            if not len(a_):
                return
            b_ = np.flatnonzero(on & (Ez < lv_) & (np.arange(len(Ez)) > a_[0]))
            if not len(b_):
                return
            j = int(b_[0])
            sk = kp["s"]
            st0 = kp["steps"][0]
            # (the lip on a point of the reach's polyline, so the staircase's
            # floor at it is the gorge's, not half the plateau's)
            k = int(np.searchsorted(sk, max(sk[j] - st0["gorge_km"], 0.0)))
            s_lip = float(sk[min(k, j)])
            foot = float(Tz[min(k, j)])  # (the gorge's floor below the lip: the lowland's)
            up = sk < s_lip
            # above the lip the river runs on the plateau (its floor graded up
            # from the lip), and the ground stands at the scarp's level down to
            # the crossing (the gorge's walls)
            Tz[up] = np.maximum(Tz[up], np.minimum(float(lv_[j]), Ez[up]) + KP_GRADED * (s_lip - sk[up]))
            Ez[sk <= sk[j]] = np.maximum(Ez[sk <= sk[j]], np.maximum(Tz[sk <= sk[j]], lv_[j]) + 1.0)
            st0["s"], st0["gorge_km"] = s_lip, float(sk[j] - s_lip)
            st0["h"] = max(st0["h"], float(ws_[j] * hg_[j]), float(lv_[j]) - foot)
            n = len(kp["steps"])  # (the cascades: spread down the reach below the scarp again)
            for c_, st in enumerate(kp["steps"][1:], 1):
                st["s"] = float(sk[j] + c_ / n * (sk[-1] - sk[j]))
            kp["scarp"] = True

        for kp in kps:
            cells, sk, m = kp["cells"], kp["s"], kp["m"]
            Tz = np.concatenate([np.linspace(*zseg[c], m)[(1 if j else 0):] for j, c in enumerate(cells)])
            Ez = np.concatenate([np.linspace(ws_c[c], ws_c[down[c]], m)[(1 if j else 0):] for j, c in enumerate(cells)])
            line = np.concatenate([polys[c] if j == 0 else polys[c][1:] for j, c in enumerate(cells)])
            # (the valley floor near the zoom's coast: see z_course)
            lc = np.floor(line[:, 0] / res + nx / 2).astype(int)
            lr = np.floor(ny / 2 - line[:, 1] / res).astype(int)
            inr = (lc >= 0) & (lc < nx) & (lr >= 0) & (lr < ny)
            Tz[inr] = np.minimum(Tz[inr], coast_cap[(lr * nx + lc)[inr]])
            # (a landform's plateau stands above the coarse ground: the falls may too)
            if ground_up is not None:
                wl, lv = (a[(lr * nx + lc)[inr]] for a in ground_up)
                Ez[inr] += wl * np.maximum(lv - Ez[inr], 0.0)
            if scarp is not None:
                scarp_fall(kp, Tz, Ez, (lr * nx + lc), inr)
            # the river keeps to the reach's course (receivers pinned along it, in the landscape pass)
            pp, pa = _raster_path(line, res, nx, ny)
            kp["course_px"], kp["course_s"] = pp[pp >= 0], pa[pp >= 0]
            # (and the main river above the reach, so its water arrives at the top of the course)
            ups_, u = [], up_main.get(cells[0])
            while u is not None and u in polys and len(ups_) < 8:
                ups_.append(polys[u])
                u = up_main.get(u)
            for q_ in [pp] + [_raster_path(pl, res, nx, ny)[0] for pl in ups_]:
                pin_pairs += [(a, b) for a, b in zip(q_[:-1], q_[1:])
                              if a >= 0 and b >= 0 and abs(a // nx - b // nx) <= 1 and abs(a % nx - b % nx) <= 1]
            drop = Tz[0] - Tz[-1]
            Hs = np.array([st["h"] for st in kp["steps"]])
            scale = min(1.0, 0.85 * max(drop, 0.0) / max(Hs.sum(), 1e-9))
            for st in kp["steps"]:
                st["h"] *= scale
            # the plateau above each fall must fit in the valley (staircase())
            kp["fit"] = staircase(kp, Tz, Ez)
            Z = stair_z(kp, sk)
            for j, c in enumerate(cells):
                stair[c] = (kp, j, Z[j * (m - 1):(j + 1) * (m - 1) + 1])
        # A tributary joining a reach with falls joins it at the staircase's
        # level (on the plateau above a fall), not at the valley floor below
        # it: else its valley is a trench below the main river, which spills
        # into it and leaves its course. Raised floors carry on upstream.
        zseg = {i: [z1, z2] for _, z1, z2, _, _, i in segs}
        ups = {}
        for i in zseg:
            ups.setdefault(down[i], []).append(i)
        todo = [(i, stair[down[i]][2][0]) for i in zseg if down[i] in stair and i not in stair]
        while todo:
            i, zj = todo.pop()
            if i in stair or zj <= zseg[i][1]:
                continue
            zseg[i][1] = zj
            zseg[i][0] = max(zseg[i][0], zj)
            todo += [(u, zseg[i][0]) for u in ups.get(i, [])]
        segs = [(pts, *zseg[i], q, rcell, i) for pts, _, _, q, rcell, i in segs]
        pin_px = np.array([a for a, b in pin_pairs if 3 <= a // nx < ny - 3 and 3 <= a % nx < nx - 3], dtype=np.int64)
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
                if len(pin_px):  # onto a pinned course (of a reach with falls) if it runs here
                    pr, pc = np.divmod(pin_px, nx)
                    dk = np.maximum(np.abs(pr - row), np.abs(pc - col))
                    if dk.min() <= 4:
                        row, col = (int(v) for v in divmod(int(pin_px[np.argmin(dk)]), nx))
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
        # ... but no higher than a gentle ramp up from the zoom's own coast,
        # which may lie inland of the coarse one: else the river is held at
        # the coarse valley floor right to the sea and drops into it off a cliff
        # (a reach with falls has it in its valley floor already: staircase())
        z_course = np.where(kpix < 0, np.minimum(z_course, coast_cap), z_course)
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
    form_f = np.asarray(L["landform"])[cell_l].astype(np.uint8) if "landform" in L else None
    if vf is not None:  # the volcanoes' own rock, and their reefs' limestone
        rock_f = np.where(vf["rock"] > 0, vf["rock"], rock_f).astype(np.uint8)
        surf_f = np.where(vf["reef"], LIMESTONE, np.where(vf["rock"] > 0, vf["rock"], surf_f)).astype(np.uint8)

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
            lakes.append({"px": pix, "level": float(clvl[c]), "exit": ex, "cl": int(c)})
        # A closed lake's smaller fragments (its outline broken up by the
        # noise or the coarse mask) pass their water on to its biggest one
        # instead of swallowing their rivers (the biggest stays closed).
        main = {}
        for j, lk in enumerate(lakes):
            m = main.get(lk["cl"])
            if lk["exit"] is None and (m is None or len(lk["px"]) > len(lakes[m]["px"])):
                main[lk["cl"]] = j
        for j, lk in enumerate(lakes):
            m = main.get(lk["cl"])
            if lk["exit"] is None and m is not None and m != j:
                mp = lakes[m]["px"]
                k = mp[np.argmin(np.hypot(px[mp] - px[lk["px"]].mean(), py[mp] - py[lk["px"]].mean()))]
                lk["exit"] = (float(px[k]), float(py[k]))
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

    rapids = np.zeros(npx, bool)  # below a lake's outlet (rims())

    def banks(ch, z, take_max):
        """Valley sides along a held river course (pixels ch at heights z):
        per pixel within BANK_KM (at least 2 px) of it, the height of the
        nearest course pixel (the highest, or lowest, of equally near ones)
        + 0.5 m; beyond that falling off at BANK_SIDE_GRAD m/km, out to at
        most 20 km. Returns (pixels, floor), course pixels and inactive
        ones left out."""
        wk = max(BANK_KM, 2 * res)
        wmax = wk + 20.0
        kk = int(np.ceil(wmax / res))
        r0, c0 = np.divmod(ch, nx)
        bd = np.full(npx, np.inf)
        bf = np.full(npx, -np.inf if take_max else np.inf)
        for d, dr, dc in sorted((res * np.hypot(dr, dc), dr, dc) for dr in range(-kk, kk + 1) for dc in range(-kk, kk + 1)):
            if d > wmax:
                break
            r, c = r0 + dr, c0 + dc
            inr = (r >= 0) & (r < ny) & (c >= 0) & (c < nx)
            win, f = r[inr] * nx + c[inr], z[inr]
            a = active[win] & (bd[win] >= d - 1e-9)
            bd[win[a]] = d
            (np.maximum if take_max else np.minimum).at(bf, win[a], f[a])
        near = np.flatnonzero(np.isfinite(bd) & (bd > 0))
        fz = bf[near] + 0.5 - BANK_SIDE_GRAD * np.maximum(bd[near] - wk, 0.0)
        return near, fz

    def rims(rec, outs, step):
        """Per-pixel floor (rims above their lake) and cap (outlet channels
        below it) for the landscape integration."""
        fl, cp = np.full(npx, 0.5), cap.copy()
        fl[ring] = ring_lvl[ring] + 0.5
        rapids[:] = False
        for j, o in enumerate(outs):
            if o >= 0:
                ch = ZK.chain(rec, o)
                fl[ch] = 0.5  # no rim along the outflow
                cp[ch] = np.minimum(cp[ch], lakes[j]["level"] - 0.3)
                # Below the sill the ground steps down gradually: the outflow
                # lies no more than RAPIDS_GRAD * s below the lake, s km down
                # the river (rapids), out to the first fall placed on the
                # outflow, instead of a cliff down to a river graded up from far
                # below. Its banks stand a little above the river beside them
                # (or the water just finds a neighbour that drops away): banks().
                lv = lakes[j]["level"] - 0.3
                s_ch = np.concatenate([[0.0], np.cumsum(chain_km(ch))])
                st_ = np.flatnonzero(step[ch] > 0)
                rkm = min(lv / RAPIDS_GRAD, 150.0, s_ch[st_[0]] if len(st_) else np.inf)
                ok = s_ch <= rkm
                fz = lv - RAPIDS_GRAD * s_ch[ok]
                near, fz_ = banks(ch[ok], fz, True)
                near, fz_ = np.concatenate([ch[ok], near]), np.concatenate([fz, fz_])
                a = active[near]
                near, fz_ = near[a], fz_[a]
                # (never above the coarse ground: where that drops away fast, so does the river)
                fz_ = np.minimum(fz_, np.maximum(base[near], target[near]))
                fl[near] = np.maximum(fl[near], fz_)
                rapids[near] = True
        return fl, cp

    def chain_km(ch):
        """Length of each link of a receiver chain, km."""
        a, b = ch[:-1], ch[1:]
        return res * np.where((a % nx != b % nx) & (a // nx != b // nx), 1.4142, 1.0)

    def place_falls(rec, Q, hprev):
        """Follow each reach with falls down the river as it runs now: from
        the first pixel of its course carrying the coarse river's water
        (>= FALLS_MIN_SHARE x the coarse discharge; else the most upstream
        pixel in the valley bottom with >= 0.3x), down the receivers (pinned along the reach's
        course: reroute), with the arc length along
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
        c_idx, c_val, ends, end_z, end_k = [], [], [], [], []
        rv = (kpix >= 0) & bottom & (rec >= 0) & (Q >= 0.3 * q_course) & active  # (starting in the valley bottom)
        # (on the pinned course itself, a fraction of that will do: the coarse
        # discharge is the cell's whole, and near the head of a reach, or of a
        # river rising in the region, the fine river carries much less)
        rv_c = (kpix >= 0) & (rec >= 0) & (Q >= FALLS_MIN_SHARE * q_course) & active
        for k_, kp in enumerate(kps):
            # (on its pinned course if the water is there: another river in
            # the corridor, e.g. a parallel reach, mustn't be taken for it)
            cp_ = kp["course_px"]
            r_k = cp_[rv_c[cp_] & (kpix[cp_] == k_)]
            if not len(r_k):
                r_k = np.flatnonzero(rv & (kpix == k_))
                if not len(r_k):
                    continue
                r_k = r_k[np.argsort(s_pix[r_k])]
            ch = ZK.chain(rec, int(r_k[0]))
            mine = kpix[ch] == k_
            ch = ch[:np.flatnonzero(mine)[-1] + 1]
            ch = ch[active[ch]]
            if not len(ch):
                continue
            ends.append(int(ch[-1]))
            # (the arc length along the course itself where the river is on it:
            # the nearest polyline point jumps where a meander comes back near itself)
            s_ch = np.where(kpix[ch] == k_, s_pix[ch], 0.0)
            on_c = np.isin(ch, kp["course_px"])
            if on_c.any():
                o = np.argsort(kp["course_px"])
                s_ch[on_c] = kp["course_s"][o[np.searchsorted(kp["course_px"], ch[on_c], sorter=o)]]
            sv = np.maximum.accumulate(s_ch)
            c_idx.append(ch)
            c_val.append(stair_z(kp, sv))
            end_z.append(float(c_val[-1][-1]))
            end_k.append(k_)
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
        c_idx = np.concatenate(c_idx) if c_idx else np.zeros(0, np.int64)
        c_val = np.concatenate(c_val) if c_val else np.zeros(0)
        if len(c_idx):
            # Banks: the ground beside the river on a reach with falls stands
            # above it (the lowest of the nearest river pixels), so the river
            # stays in its course down to the lip instead of leaving it
            # (sideways, down a bare step) wherever the land next to it drains
            # lower, and doesn't run perched above the land beside it: valley
            # sides a few km wide (banks()). Not on the river itself, nor on
            # its course below the reach.
            on = np.zeros(npx, bool)
            on[c_idx] = True
            for e_ in ends:
                on[ZK.chain(rec, e_)] = True
            b, fz = banks(c_idx, c_val, False)
            # (nor on other rivers: a bigger river nearby, or another coarse
            # river's valley bottom, isn't lifted onto this one's banks)
            keep = ~on[b] & ~(bottom[b] & (kpix[b] < 0)) & (Q[b] * KM2_M_PER_YR_TO_M3S < BANK_MAX_Q)
            b, fz = b[keep], fz[keep]
            flg[b] = np.maximum(flg[b], fz)
            cliff[c_idx] = True  # the course and its banks don't creep either
            r, cc = np.divmod(c_idx, nx)
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    ok = (r + dr >= 0) & (r + dr < ny) & (cc + dc >= 0) & (cc + dc < nx)
                    nb = ((r + dr) * nx + cc + dc)[ok]
                    cliff[nb[active[nb] & ~on[nb]]] = True
        if lips:
            flg[[lp for lp, _, _ in lips]] = -np.inf
        # below each reach the river runs no higher than the foot of its
        # staircase (else it holds the reach's lower falls up: they vanish)
        # (until it joins a bigger river, or another reach with falls)
        below = []
        for e_, k_ in zip(ends, end_k):
            g = ZK.chain(rec, e_)[1:]
            stop = (Q[g] > 1.5 * Q[e_]) | ((kpix[g] >= 0) & (kpix[g] != k_))
            below.append(g[:np.flatnonzero(stop)[0]] if stop.any() else g)
        b_val = np.concatenate([np.full(len(g), z_) for g, z_ in zip(below, end_z)]) if below else np.zeros(0)
        below = np.concatenate(below) if below else np.zeros(0, np.int64)
        return c_idx, c_val, step, flg, cliff, lips, (below, b_val)

    # the courses of reaches with falls (pinned receivers), on open ground
    pin = {a: b for a, b in pin_pairs if active[a] and active[b]}
    pin_src, pin_dst = np.array(list(pin), dtype=np.int64), np.array(list(pin.values()), dtype=np.int64)

    def reroute(rec, order):
        """Pin the courses of reaches with falls, then apply the distributary
        receivers (each only if it leaves the network acyclic)."""
        src, dst = pin_src, pin_dst
        while len(src):
            r2 = rec.copy()
            r2[src] = dst
            o2 = ZK.receiver_order(r2)
            if len(o2) == npx:
                rec, order = r2, o2
                break
            # a loop (a course draining back into itself): unpin the loop's pixels
            done = np.zeros(npx, bool)
            done[o2] = True
            walk, i = {}, int(np.flatnonzero(~done)[0])
            while i not in walk:
                walk[i] = len(walk)
                i = int(r2[i])
            loop = list(walk)[walk[i]:]
            keep = ~np.isin(src, loop)
            if keep.all():
                break
            src, dst = src[keep], dst[keep]
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
        # (a river-dominated delta's channels run straighter, between their levees)
        wander = [0.7 * (1 - 0.7 * wR_f) * ZK.fbm(Pk, 25.0, 3, 0.5, S + 41 + k) / 0.17 for k in range(2)]
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
            nb = dl["nb"]  # from the Galloway weights (_deltas): waves leave few mouths, tides many
            if nb < 2:  # a single mouth: no distributaries (the trunk stays pinned)
                continue
            phi = np.arctan2(py[m0] - py[a], px[m0] - px[a])
            ln = np.hypot(px[m0] - px[a], py[m0] - py[a])
            cp = np.flatnonzero(coast & ~assigned)
            cd = np.hypot(px[cp] - px[a], py[cp] - py[a])
            goals = []
            if dl["goals"]:
                # the tips of the fingers (river) or the heads of the funnels
                # (tide): the coast pixel nearest each, not too close to the apex
                for gx, gy in dl["goals"]:
                    ok = cd > 0.4 * ln
                    if ok.any():
                        q = int(cp[ok][np.argmin(np.hypot(px[cp[ok]] - gx, py[cp[ok]] - gy))])
                        if q not in goals:
                            goals.append(q)
            else:
                # coast pixels spread over a fan around the main mouth
                spread = np.radians(min(30.0 + 20.0 * (nb - 1), 130.0))
                ca = (np.arctan2(py[cp] - py[a], px[cp] - px[a]) - phi + np.pi) % (2 * np.pi) - np.pi
                for th in spread * np.linspace(-0.5, 0.5, nb) + rng.normal(0, 0.05, nb):
                    ok = (np.abs(ca - th) < 0.12) & (cd > 0.5 * ln) & (cd < 2.0 * ln)
                    if ok.any():
                        q = int(cp[ok][np.argmin(cd[ok])])
                        if q not in goals:
                            goals.append(q)
            if len(goals) < 2:
                goals = [int(m0)] + goals
            # order the goals around the fan, so each split divides neighbours
            goals.sort(key=lambda q: (np.arctan2(py[q] - py[a], px[q] - px[a]) - phi + np.pi) % (2 * np.pi))
            # (the branches stay on low ground: not up into the hills beside the plain)
            grow(a, goals, max(int(0.15 * ln / res), 2), blocked | (target > BRANCH_MAX_Z))
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
    vpin = np.full(npx, -np.inf)  # young volcanoes: held at their smooth cone
    if vf is not None:
        tv = np.isfinite(vtarget)
        soft = np.where(tv, np.maximum(soft, target), soft)
        cap = np.where(tv, np.maximum(cap, target + 150.0), cap)
        pin = tv & np.isfinite(vf["pin"]) & active
        cap = np.where(pin, target + 25.0, cap)
        vpin = np.where(pin, target - 25.0, vpin)
    rough = np.where(glacier, 0.5, 1.0) * var / Kr
    hprev = None
    was_river = bottom.copy()  # the valley bottom, and every pixel the coarse river's water has run through
    for it in range(iterations):
        filled, rec, order = ZK.flood_d8(h, outlet, nx, ny, 1e-3, jitter)
        if deltas and it == iterations // 3:  # once the network has settled a bit
            ov_src, ov_dst, splits = make_branches(rec, order)
            # levees: the land along the distributaries stands a little
            # above the plain, more so on a river-dominated delta
            chan = np.zeros(npx, bool)
            chan[ov_src] = True
            lev = _dilate(chan.reshape(ny, nx), 1).ravel() & ~chan & active & (wD > 0.3)
            delta_floor = np.where(lev, np.maximum(delta_floor, zD + 0.5 + 3.0 * wR_f), delta_floor)
        rec, order, split_ok = reroute(rec, order)
        outs = lake_outlets(rec)
        Q, _ = route(srcq, rec, order, outs, split_ok)
        diag = (rec >= 0) & ((rec % nx) != (idx % nx)) & ((rec // nx) != (idx // nx))
        dist = res * np.where(diag, 1.4142, 1.0)
        # coarse river courses count as carrying at least their coarse discharge
        slope = np.minimum(C * rough * np.maximum(np.maximum(Q, riv_q), 1e-3) ** -SPL_M, MAX_SLOPE)
        c_idx, c_val, step, flg, cliff, _, (b_idx, b_val) = place_falls(rec, Q, hprev)
        fl, cp = rims(rec, outs, step)
        was_river |= Q >= 0.3 * q_course
        # (on a reach with falls, only in the valley bottom: a stream wandering
        # off the course isn't held up at the plateau's level)
        flc = np.where(was_river & ((kpix < 0) | bottom), z_course, -np.inf)
        flc[c_idx] = c_val  # the river itself, on reaches with falls
        cp[c_idx] = np.minimum(cp[c_idx], c_val + 1.0)  # ... at its staircase, not above it
        np.minimum.at(cp, b_idx, b_val + 1.0)
        # (beach ridges and levees, but not under the channels themselves)
        fl = np.maximum(np.maximum(np.maximum(np.maximum(fl, flg), flc), vpin),
                        np.where(Q * KM2_M_PER_YR_TO_M3S < 30.0, delta_floor, -np.inf))
        h = target.copy()
        ZK.integrate(h, rec, order, slope, dist, ~active, fl, soft, 0.5 * amp_land + 1, cp)
        hprev = h
        hmean = _box_mean(np.maximum(h, 0).reshape(ny, nx) * wmask, wmask, rad).ravel()
        C = C * np.clip(tmean / np.maximum(hmean, 1.0), 0.5, 2.0) ** 0.8
    # soften D8 streaks and knife-edge ridges on hillslopes; keep channels sharp
    chan = np.clip(np.log10(np.maximum(Q, 1e-3) / (50 * res * res)) / 2, 0, 1)
    cliff = _dilate(cliff.reshape(ny, nx), 2).ravel()  # falls, gorges and their walls don't creep
    kd = np.where(active & ~cliff, np.where(glacier, 0.4, KD * (1 - 0.8 * chan)), 0.0)
    # (creep rounds the hillslopes, but never lifts a stream's bed: in a deep
    # valley it would fill the channel towards its walls in places, leaving
    # steps and pits along the stream, undesigned 'falls'. Under ice it does,
    # the ice surface is smooth, but by no more than ICE_SNOUT_GRAD m per km
    # in from the ice's edge: else the glacier ends in a cliff.)
    stream = active & (chan > 0)
    lift = np.where(glacier, ICE_SNOUT_GRAD * res * ZK.inside_distance(glacier, nx, ny, False), 0.0)
    h0 = h
    for _ in range(SMOOTH_STEPS):
        hd = ZK.diffuse(h, kd, active, nx, ny)
        h = np.where(stream, np.minimum(hd, np.maximum(h, h0 + lift)), hd)
    if lf is not None:
        # Landform bedding (zoom_landforms): benches, scarps and cliffs of the
        # finished landscape, each coarse cell's mean kept. Not on glaciers,
        # lake rims and outflows, nor the courses of designed falls and their
        # banks (their staircase is the river's; the remap would add steps to
        # it or flatten its falls).
        course = np.zeros(npx, bool)
        course[c_idx] = True
        dco = ZK.inside_distance(~course, nx, ny, False) * res
        wk = max(BANK_KM, 2 * res)
        where = active & ~glacier & ~ring & ~rapids
        # (on the drainage of the crept surface; channels: >= LF_CHANNEL_Q)
        hf, rec_, order_ = ZK.flood_d8(h, outlet, nx, ny, 1e-3, jitter)
        hf = np.where(active, np.maximum(h, hf), h)
        chan_ = (Q * KM2_M_PER_YR_TO_M3S >= LF_CHANNEL_Q) | ~active
        mask_ = where * smoothstep(wk + res, wk + 4 * res, dco)
        # (cut only inside the classes' reach: a sill where a river leaves it
        # would otherwise be cut far down its course)
        keep_ = ((mask_ <= 0) & ~(edge & land)) | (lf.weight() < 0.02)
        h = keep_means(ZL.breach(lf.remap(hf, mask_, rec_, order_, chan_), rec_, order_, keep_), h, active,
                       np.clip(3 * lf.weight(), 0, 1))
        # (a sill the remap, the correction or the summits' caps leave across a
        # flow path is cut through rather than filled into a lake; the region's
        # edge, an outlet held at the target, is lowered too where land drains into it)
        h = ZL.breach(np.where(active, np.minimum(h, cp), h), rec_, order_, keep_)
    h = np.where(active, np.maximum(h, 0.5), h)  # creep mustn't pull the coast below the sea
    h = np.where(ring | rapids, np.maximum(h, fl), h)  # nor the rims below their lake, nor its outflow's rapids
    h = np.where(active, np.minimum(h, cp), h)  # nor lift a lake's outflow above the lake
    log(f"  landscape pass: {iterations} iterations [{time.time() - t0:.1f}s]")

    # A lake fragment that should pass its water on but found no way out
    # (all of its shore drains back into it) would swallow its rivers: it
    # becomes land instead, a flat at its level that the rivers cross.
    rec = ZK.flood_d8(h, outlet, nx, ny, 1e-3, jitter)[1]
    outs = lake_outlets(reroute(rec, ZK.receiver_order(rec))[0])
    sink = [j for j, lk in enumerate(lakes) if lk["exit"] is not None and outs[j] < 0]
    if sink:
        for j in sink:
            lake[lakes[j]["px"]] = False
        kept = [j for j in range(len(lakes)) if j not in sink]
        lakes, ring_px = [lakes[j] for j in kept], [ring_px[j] for j in kept]
        lake_seq = sorted(range(len(lakes)), key=lambda j: -lakes[j]["level"])
        outlet = sea | edge | lake
        active = land & ~edge & ~lake
        log(f"  {len(sink)} lake fragments without an outlet made land")

    # --- final drainage --------------------------------------------------
    filled, rec, order = ZK.flood_d8(h, outlet, nx, ny, 1e-3, jitter)
    h = np.where(active, np.maximum(h, filled), h)  # no pits left: everything drains
    filled, rec, order = ZK.flood_d8(h, outlet, nx, ny, 1e-3, jitter)
    rec0 = rec
    rec, order, split_ok = reroute(rec, order)
    # The pinned courses (reaches with falls, delta trunks and distributaries)
    # were laid out on an earlier surface: where one now runs uphill, a small
    # step (<= SETTLE_M) is evened out by lifting the pixel above it; at a big
    # one (a course the water has left) the course is unpinned.
    up = (rec != rec0) & (rec >= 0) & active
    up &= h[np.maximum(rec, 0)] > h + SETTLE_M
    if up.any():
        r2 = np.where(up, rec0, rec)
        o2 = ZK.receiver_order(r2)
        if len(o2) == npx:
            rec, order = r2, o2
    diag = (rec >= 0) & ((rec % nx) != (idx % nx)) & ((rec // nx) != (idx // nx))
    ZK.settle(h, rec, order, ~active, res * np.where(diag, 1.4142, 1.0), SETTLE_M)
    outs = lake_outlets(rec)
    Q, lake_in = route(srcq, rec, order, outs, split_ok)
    area, _ = route(np.full(npx, res * res), rec, order, outs, split_ok)
    discharge = np.where(land, Q * KM2_M_PER_YR_TO_M3S, 0.0)
    ws_f = np.where(lake, surf, np.where(sea, 0.0, h))
    # the designed falls: where they ended up, and a plunge pool at each foot
    lips = place_falls(rec, Q, h)[5]
    falls = waterfalls(ws_f, np.where(glacier, 0.0, discharge), rec, nx, ny, res,  # (no falls under the ice)
                       {int(o): lakes[j]["level"] for j, o in enumerate(outs) if o >= 0},
                       designed=[lp for lp, _, _ in lips])
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
                          "coarse_reach_km": round(kp["reach_km"]), "plunge_pool_m": round(float(pool[foot]), 1),
                          "_kp": kps.index(kp)})
    for f in falls:
        f.setdefault("kind", "lake outlet" if f["from_lake"] else "drop")
        # the reach's other falls (cascades), which the ~15 km spacing leaves off the list
        if "_kp" in f:
            f["cascades"] = [{"px": st["lip_px"], "height_m": st["height_m"]} for st in kps[f.pop("_kp")]["steps"]
                             if "lip_px" in st and st["height_m"] >= KP_MIN_STEP
                             and max(abs(st["lip_px"][0] - f["px"][0]), abs(st["lip_px"][1] - f["px"][1])) > 3]
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
    # land the coarse map has as sea (a volcanic island in a sea cell): a
    # climate from its own temperature and rain
    lone = land & (clim_f == SEA_CLIMATE)
    if lone.any():
        t_cold = 2 * temp - t_warm
        k = np.where(t_cold >= 18, np.where(precip >= 1800, 0, np.where(precip >= 1000, 1, 2)),  # Af Am Aw
                     np.where(t_cold > 0, np.where(t_warm >= 22, 13, 14), np.where(t_warm >= 10, 26, 28)))  # Cfa Cfb Dfc ET
        clim_f = np.where(lone, np.where((precip < 350) & (t_cold > 0), 3, k), clim_f).astype(np.uint8)  # BWh
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
        # Galloway weights (coast.galloway) and the shape they gave each delta
        "deltas": [{"mouth_km": [round(d["x"], 1), round(d["y"], 1)], "discharge_m3s": round(d["q"]),
                    "plain_radius_km": round(d["R"]), "type": d["gw"]["type"], "weights": d["gw"]["weights"],
                    "wave_power_kw_m": round(d["wave"], 1), "tide_range_m": round(d["tide"], 2),
                    "sediment_mt_yr": {k: round(d["gw"][f"sediment_{k}_kgs"] * coast.SEC_PER_YR / 1e9, 1)
                                       for k in ("river", "wave", "tide")},
                    "mouths": _count_mouths(d, px, py, land, rec, discharge, nx, ny),
                    "form": d["form"], "marine_layers": d["marine"],
                    "seaward": [round(float(v), 3) for v in d["u"]],
                    "lat_lon": [round(v, 3) for v in _latlon(fr.to_sphere(np.array([d["x"]]), np.array([d["y"]]))[0])]}
                   for d in deltas],
        "distributary_splits": len(splits),
        # pixel-scale falls (see waterfalls()); kind "lip": a knickpoint kept from a steep coarse reach
        # (see knickpoints()), with its gorge and plunge pool
        "waterfalls": falls,
        "knickpoints": len(kps),
        # the volcanoes drawn (zoom_volcanoes), with what they look like now
        "volcanoes": vf["list"] if vf is not None else [],
        # % of the land each synthesised landform class shapes (zoom_landforms)
        "landforms": lf.stats() if lf is not None else {},
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
        "tide_range": np.where(sea, tide_f, 0).astype(np.float32),
        "wave_power": np.where(sea, wave_f, 0).astype(np.float32),
        "rock": rock_f,
        "surface_rock": surf_f,
        "climate": clim_f,
        "biome": biome,
        **({"landform": form_f} if form_f is not None else {}),
    }
    coarse = {"elevation": elev[own], "precipitation": L["precipitation"][own].astype(float),
              "river_segs": river_segs}
    return {"nx": nx, "ny": ny, "res": res, "frame": fr, "layers": {k: v.reshape(ny, nx) for k, v in layers.items()},
            "stats": stats, "coarse": coarse, "rec": rec, "kps": kps,
            "lakes": [{"open": lk["exit"] is not None, "outlet": int(outs[j]), "n_px": int(len(lk["px"])),
                       "level": lk["level"], "inflow_m3s": float(lake_in[j] * KM2_M_PER_YR_TO_M3S)}
                      for j, lk in enumerate(lakes)],
            "debug": {"pinned": pin_src, "overrides": ov_src},
            "seconds": round(time.time() - t0, 1),
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
    if "tide_range" in Lr:  # tidal flats: sea floor above low tide (dry at low water)
        tr = Lr["tide_range"]
        flat = (water == 1) & (h > -0.5 * tr) & (tr > 0.8)
        col = np.where(flat[..., None], np.array([156, 150, 122.0]) * (0.8 + 0.3 * shade[..., None]), col)
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
    "tide_range": ("m", "tidal range at sea (interpolated from the world's tide_range; 0 on land)"),
    "wave_power": ("kW/m", "mean wave power at sea (interpolated from the world's wave_power; 0 on land)"),
    "rock": ("ROCKS id", "basement rock (surface.ROCKS)"),
    "surface_rock": ("ROCKS id", "exposed rock: basement or sediment cover"),
    "climate": ("KOPPEN id", "Koppen class; alpine tundra/ice cap added from the fine elevation"),
    "biome": ("BIOMES id", "climate.biomes on the fine fields"),
    "landform": ("landform id", "landform class of the coarse cell (landform.CLASSES; legend 'landforms')"),
}


def zoom_id(world_id: str, lat: float, lon: float, size_km: float, res_km: float, seed: int,
            iterations: int = 15) -> str:
    key = f"{world_id}|{lat:.4f}|{lon:.4f}|{size_km:g}|{res_km:g}|{seed}"
    if iterations != 15:  # the default keeps the ids it always had
        key += f"|it{iterations}"
    return hashlib.sha1(key.encode()).hexdigest()[:6]


def save(z: dict, world_path: Path, world: dict, lat: float, lon: float, size_km: float, res_km: float,
         seed: int, iterations: int = 15) -> Path:
    world_id = world_path.stem
    zid = zoom_id(world_id, lat, lon, size_km, res_km, seed, iterations)
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
    return save(z, path, world, lat, lon, size_km, res_km, seed, iterations)
