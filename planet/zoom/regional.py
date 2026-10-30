"""Regional zoom: refine a patch of a sliced world from ~110 km cells to ~2 km.

    uv run python -m planet zoom <world_id> --lat L --lon L [--size-km 1000] [--res-km 2] [--seed N]

A static refinement at one moment, deterministic in (world, centre, size,
resolution, seed). All noise is sampled at 3D positions on the planet (in
km), so two overlapping zooms of the same world share their detail.

The build() function is a list of named stages (stage_terrain.py, stage_rivers.py, stage_landscape.py, stage_finish.py)
that work on one shared ZoomCtx; this module holds the helpers and constants they share, ZoomCtx, and the zoom's I/O.

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
   value (smooth correction fields, MEAN_PASSES of them, so a one-cell
   trench keeps its depth), so the region doesn't drift.
   This is the *target* surface for step 6.
   Big river mouths (>= DELTA_MIN_Q) get a delta plain: within a radius R
   growing with discharge and the coarse sediment cover offshore, the
   detail is damped and the land pulled down to a few metres above the
   sea, the sea floor shallows (on the shelf, not over deep water), and a
   lobe of land is pushed out to sea.
   Volcanoes (zoom.volcanoes): every volcano of the world's table becomes
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
   (Steps 2-6 run on the region plus a halo of HALO_CELLS coarse cells
   round it, cropped off before the climate: the landscape goes on past
   the region's edge, whose pixels are outlets held at the target, so the
   drainage near the edge isn't cut short there, PW-321.)
6. Landscape pass on the raster: a steady-state stream-power landscape.
   Priority flood + steepest-descent D8 routing gives a drainage network
   and discharge Q (the world's runoff + inflow: the rivers, falls and
   lakes); walking up from the outlets (sea, lakes, region edge), each
   pixel sits above its receiver by slope = C / K * Qg^-0.5 (Qg: the
   rain-weighted drainage area, which shapes a desert's wadis too;
   K = surface.ROCKS erodibility): big rivers
   are gentle, small gullies and ridges steep, so valleys nest
   dendritically. C is a smooth field at the coarse cells' scale, refitted
   each iteration (a Newton step per cell on the relief its own slopes
   make, PW-298) so every coarse cell keeps the target's mean as it was
   before the coarse valleys were cut into it (so the valleys are cut
   mass-neutrally: the hillslopes between them stand a little higher,
   PW-268); the network is
   recomputed on the new surface and the whole thing repeated (~15x).
   Lakes are outlets held at their surface, with a rim kept above the
   water except at the outlet (the shore pixel nearest the coarse lake's
   exit); an open lake's inflow leaves again there, and the ground below
   the outlet (in a corridor along its river) steps down as fast as the
   coarse outflow descends, at least RAPIDS_GRAD m/km (rapids, not a
   cliff; a mountain lake's outflow cascades down its valley).
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
   ice; what it takes off a cell's mean goes back on its hillslopes). Glaciers (glaciers(), PW-127, PW-159) from each pixel's own climate:
   accumulation where its snow outlasts the summer (icemass.balance, the
   run's and time zoom's surface mass balance; under the coarse sheet with
   its ice), the surplus routed down the valleys as melting tongues; outlined on the
   target surface, redrawn on the finished one.
   Landform classes (zoom.landforms, PW-010..012): each coarse cell's class
   shapes the target (the structure the drainage organises around: fold
   ridges, fault blocks, domes; a coastal plain or a sand sheet smoothed)
   and reshapes the finished landscape,
   blended by smooth class weights: the relief around the drainage (flat
   interfluves over steep valley walls), the structure itself (tilted
   fault blocks over flat half-grabens, folds and hogbacks, inselbergs)
   and hard beds as benches and cliffs (a great escarpment's scarp, caprock
   benches, mesas and cuestas, a lava plateau's stepped valley sides);
   rivers crossing a cliff fall over it, and the falls retreat into
   gorges. Sills across a flow path are cut through as gaps a few pixels
   wide, but not across a rift's or a scoured shield's closed basins
   (in the final drainage their water balance makes them full lakes that
   spill into the next, closed lakes below the spill, or dry flats where
   the streams end: basin_lakes, PW-167); each coarse cell's mean is kept.
   After the final drainage, overlays (Landforms.finish): dunes on the
   land, karst's dolines, poljes and towers (ponds where they reach the
   water table), karst streams sinking (dry valleys) and resurging at
   springs. A coastal plain's wave-dominated coast gets a barrier island,
   a lagoon and inlets with the coastline (step 3), and marshes (the
   `wetland` layer). A designed reach crossing
   an escarpment takes its main fall at the scarp, with the plateau above
   it (the ground it must fit under is lifted: scarp_fall). Any pits
   left are filled. Falls are listed only where the drop stands out from
   the river around it (waterfalls()): stats.falls has every fall >= 30 m
   (kind lip / scarp / bench / lake outlet / drop; scarp and bench falls
   get a plunge pool), stats.waterfalls the top 5 for the panel.

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

from .. import coast, icemass, kernels
from .. import humanuse as HU
from .. import gameattrs as GA
from .. import store as S
from .. import world as W
from . import kernels as ZK
from . import landforms as ZL
from .. import satellite as SAT
from .. import vegetation
from . import vegetation as ZVG
from . import peoples as ZP
from . import coast as ZC
from . import stage_terrain as STG_T
from . import stage_rivers as STG_R
from . import stage_landscape as STG_L
from . import stage_finish as STG_F
from ..geo import R_KM, latlon, xyz
from ..images import write_png
from ..climate import LAPSE
from ..tectonics.isostasy import land_view

SEC_PER_YR = 3.156e7
KM2_M_PER_YR_TO_M3S = 1e6 / SEC_PER_YR  # discharge unit used internally -> m^3/s

# How rugged the sub-cell detail is, by basement rock (surface.ROCKS ids).
RUGGED = {0: 0.35, 1: 0.85, 2: 0.9, 3: 0.45, 4: 1.0, 5: 0.35, 11: 0.6}
SEA_CLIMATE = 30  # KOPPEN "-"
LIMESTONE = 6  # surface.ROCKS
# landscape pass: discharge exponent of the steady-state slope, hillslope
# creep per smoothing step (and number of steps), steepest slope allowed
SPL_M, KD, MAX_SLOPE, SMOOTH_STEPS = 0.5, 0.25, 450.0, 6  # MAX_SLOPE in m/km
KD_RES_KM, KD_ICE = 2.0, 0.4  # km: the pixel size KD (and the ice's KD_ICE) was set at


def creep_kd(res: float) -> float:
    """Creep's per-step share of the way to the neighbour mean at pixel size
    res km, for a unit KD: creep is a diffusivity (dh/dt = D lap h, the
    discrete step D dt / res^2), so above KD_RES_KM its per-pixel step falls
    as (KD_RES_KM / res)^2 and a hill of a given size in km rounds as much on
    4 km pixels as on 2 km ones (PW-125: at a fixed share, 4 km zooms crept
    4x as far in km and lifted 20-50 m^3/s stream beds 50-470 m). Finer
    pixels keep the 2 km share for now (physically theirs would be larger:
    docs/review/zoom-polish/pw125.md)."""
    return min(1.0, (KD_RES_KM / res) ** 2)


DELTA_MIN_Q = 1500.0  # m^3/s at a coarse river mouth for a delta plain
# m: the plain (a few metres up to coast.PLAIN_Z0 + PLAIN_RISE ~11 m at its
# edge) lies where the coarse ground is this low, fading out above (PW-349:
# 250-800 m before, so it flattened cells standing 130-480 m to a few metres
# and left river-mouth zooms ~25 m low inland: a lowland the world doesn't have)
DELTA_PLAIN_GROUND = (30.0, 250.0)
FIT_STEP, FIT_SIGMA = 4.0, 0.35  # the landscape pass's slope fit: C changes at most x4 a pass, smooth over 0.35 cells
FLOOR_MIN_M = 100.0  # m: lower flats are plains (deltas, coastal fill)
FLOOR_SLOPE, FLOOR_MAX_SHARE = 2.0, 0.5  # m/km a filled basin's floor falls to its exit, at most this share of its fill depth (PW-521)
MEAN_PASSES = 12  # smooth corrections that pull each coarse cell's mean back to its coarse height
SEA_SHARE_PASSES = 3  # ... after a land cell's own sea pixels took what its mean lacks, up to the shore (PW-362)
# Delta fingers (PW-847). A finger is a distributary between its levees building out beyond the
# delta's lobe; only a river-dominated delta into water many channel depths deep grows them (BUOYANT_DEPTHS:
# the basin's depth over the river's bankfull depth 0.27 Q^0.39, Leopold & Maddock 1953; from a friction-
# dominated to an inertia/buoyancy-dominated outflow, Wright 1977, GSA Bulletin 88:857-868; the two ratios
# are judgement). Their length: the Mississippi's passes run ~30 km beyond the delta front on a ~250 km
# plain, so FINGER_LEN 0.12 R; their width a few km (levees and channel), FINGER_W 0.012 R; at most
# FINGER_MAX of them (the Mississippi's three main passes; Coleman & Wright 1975, in Broussard ed.,
# Deltas: Models for Exploration). Earlier fingers were 1.1 R long and 0.06 R wide, a hand of up to 9.
BUOYANT_DEPTHS = (2.0, 6.0)
FINGER_LEN, FINGER_W, FINGER_MAX = 0.12, 0.012, 4
BRANCH_MAX_Z = 250.0  # m: distributaries aren't laid out where the target surface is higher than this
BRANCH_CLIMB_M = 30.0  # m: ... nor where it stands higher than this above the delta's apex (PW-061)


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


def shore_apron(h, lake, lakes, free, held, held_px, rec, order, q, nx, ny, res):
    """Grade the plain beside each big lake up from its shore (PW-531; SHORE_*
    constants): within the lake's reach, every land pixel that isn't a river
    stands at least SHORE_GRAD m/km above its receiver (ZK.raise_to_run, so
    drainage and the lake's level are untouched; the ground that is already
    steeper stays as it is), after a beach a couple of pixels wide. `free`
    pixels may change; the `held` ones and `held_px` (rims, rapids, designed
    courses) don't, and the grade fades in 2 px from them and out towards
    the reach's edge. Returns (h, pixels raised)."""
    npx = nx * ny
    hold = held.copy()
    hold[held_px] = True
    dh = ZK.inside_distance(~hold, nx, ny, False) * res  # km from the held pixels
    grade, best = np.zeros(npx), np.full(npx, np.inf)
    for lk in lakes:
        area = len(lk["px"]) * res * res
        if area < SHORE_MIN_KM2:
            continue
        reach = min(0.6 * np.sqrt(area), SHORE_MAX_KM)
        m = np.zeros(npx, bool)
        m[lk["px"]] = True
        d = ZK.inside_distance(~m, nx, ny, False) * res  # km to this lake
        zone = free & (d < reach) & (d < best) & (q < SHORE_RIVER_Q)
        w = (0.65 + 0.35 * np.clip((reach - d) / (0.25 * reach), 0.0, 1.0)) * smoothstep(0.0, 2.0 * res, dh) * smoothstep(SHORE_BEACH_KM, SHORE_BEACH_KM + 2 * res, d)
        grade = np.where(zone, SHORE_GRAD * w, grade)
        best = np.where(zone, d, best)
    if not (grade > 0).any():
        return h, 0
    idx = np.arange(npx)
    diag = (rec >= 0) & ((rec % nx) != (idx % nx)) & ((rec // nx) != (idx // nx))
    run0 = SHORE_GRAD * res * np.where(diag, 1.4142, 1.0)
    run = grade / SHORE_GRAD * run0
    out = ZK.raise_to_run(h, rec, order, run, run0 * 1.1 / SHORE_GRAD)  # (a ramp's tail keeps just over 1 m/km)
    return out, int((out > h + 1e-6).sum())


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


def tie_jitter(Pk: np.ndarray, res: float, seed: int) -> np.ndarray:
    """The drainage's tie-break lift (ZK.flood_d8's jitter, 0..1) per pixel,
    planet-fixed (PW-339): noise sampled at the pixel's position on the
    planet, varying from pixel to pixel (two octaves at 2 and 1 px), so
    overlapping zooms of one place break their ties on flats alike. (One
    random number per pixel index gave a zoom of another size, centre or
    halo another drainage on its flats.)"""
    return 0.5 + 0.5 * np.tanh(ZK.fbm(Pk, 2.0 * res, 2, 0.6, seed) / 0.25)


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
WF_MIN_Q, WF_MIN_DROP, WF_MIN_GRAD, WF_STEPS = 20.0, 30.0, 15.0, 3  # (Q: routed runoff, PW-180)
WF_MAX_KM = 5.0  # ... and over at most this far (at least one pixel): on coarse pixels a steep reach isn't a fall
WF_EDGE_PX = 8  # ... and not next to the built area's edge (held at the target surface; it lies in the halo, cropped off)
WF_CONTRAST, WF_CONTEXT_KM = 3.0, 6.0  # ... and WF_CONTRAST x steeper than the river within WF_CONTEXT_KM (see waterfalls())
WF_DESIGNED_SHARE = 0.3  # ... unless within 3 px of a designed lip on its river (carrying this share of the lip's water)
HALO_CELLS = 0.5  # coarse cells of terrain built round the region and cropped off (at least WF_EDGE_PX, at most 1/4 of it)


def waterfalls(ws: np.ndarray, q: np.ndarray, rec: np.ndarray, nx: int, ny: int, res: float,
               starts: dict | None = None, top: int | None = 5, designed=(), sep_km: float = 15.0) -> list[dict]:
    """Pixel-scale falls along the drainage network. ws: water surface (lake
    surface on lakes, 0 at sea), q: discharge m^3/s, rec: D8 receivers (-1
    at outlets); starts: {lake outlet pixel: lake level}, where a fall
    starts at the lake surface a pixel upstream. A drop that isn't at a
    lake outlet or within 3 px of a `designed` lip pixel must stand out from
    the river around it: at least WF_CONTRAST x as steep as the reaches
    just above and below it (else it's a steep reach, rapids or a cascade
    of a mountain stream, not a fall: coarse pixels and small steep streams
    have many). Best first by power (discharge x height), at least sep_km
    (and 3 px) apart, the first `top` (None: all), none within WF_EDGE_PX of
    the edge. Each: px (row, col), height_m, length_km, discharge_m3s,
    power_gw, top_m, bottom_m, from_lake; _foot: the pixel the drop is
    measured to, the fall's foot (its plunge pool goes there: on a fall
    over several pixels the one below the top has little of the drop
    above it, PW-341)."""
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
    # concentrated: steeper than the river above and than the river below
    # (each over ~2x the fall's length, at least WF_CONTEXT_KM), by WF_CONTRAST
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
    # (each side on its own: pooled, a flat valley floor or main river below
    # halved the context, and a mountain stream as steep above as at its
    # last link, where it reaches the floor, was listed as a fall, PW-125)
    g_ctx = np.maximum(np.maximum(ws[pu] - lvl[i], 0) / np.maximum(ku, res),
                       np.maximum(ws[jj] - ws[pd_], 0) / np.maximum(kd_, res))
    fixed = d0[i] > 0  # (lake outlets and designed lips are falls whatever the river around them)
    r_, c_ = np.divmod(i, nx)
    for p in designed:  # (on the designed river: a tributary joining it near the lip is tested like any other)
        a, b = divmod(int(p), nx)
        fixed |= (np.abs(r_ - a) <= 3) & (np.abs(c_ - b) <= 3) & (q[i] >= WF_DESIGNED_SHARE * q[int(p)])
    ok = fixed | (h / np.maximum(d, 1e-9) >= WF_CONTRAST * g_ctx)
    i, h, d, jj = i[ok], h[ok], d[ok], jj[ok]
    gw = 1000 * 9.81 * q[i] * h / 1e9
    out, sep = [], max(3, int(round(sep_km / res)))
    taken = np.zeros((ny, nx), bool)  # (spacing by a mask: the full list can be long)
    for k in np.argsort(-gw):
        r0, c0 = divmod(int(i[k]), nx)
        if taken[r0, c0]:
            continue
        taken[max(r0 - sep + 1, 0):r0 + sep, max(c0 - sep + 1, 0):c0 + sep] = True
        out.append({"px": [r0, c0], "height_m": round(float(h[k]), 1), "length_km": round(float(d[k]), 1),
                    "discharge_m3s": round(float(q[i[k]]), 1), "power_gw": round(float(gw[k]), 3),
                    "top_m": round(float(lvl[i[k]]), 1), "bottom_m": round(float(ws[jj[k]]), 1),
                    "from_lake": bool(d0[i[k]] > 0), "_foot": int(jj[k])})
        if top is not None and len(out) >= top:
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
KP_RESIST = ZL.RESIST
COAST_FLOOR_GRAD = 2.0  # m/km: a river's valley floor rises no faster than this from the coast
RAPIDS_GRAD = 2.0  # m/km: a lake's outflow steps down no faster than this below its outlet (and any fall there)
# A big lake's shore (PW-531). The slope fit holds each coarse cell's mean, and the cell beside a lake lies only
# tens of metres above it, so the fit leaves a plain of ~1 m/km tens of km wide. Land within a lake's reach is
# graded to rise at least SHORE_GRAD from the water after a beach (shore_apron).
SHORE_MIN_KM2 = 150.0  # lakes at least this big (km2); the reach is 0.6 x sqrt(area) km, at most SHORE_MAX_KM
SHORE_MAX_KM = 40.0
SHORE_GRAD, SHORE_BEACH_KM = 2.0, 1.0  # m/km, km
SHORE_RIVER_Q = 20.0  # m^3/s: rivers this big keep their own (valley floor) grade
FALLS_MIN_SHARE = 0.05  # a reach's falls are placed from where its pinned course carries this share of the coarse discharge
SETTLE_M = 10.0  # m: an uphill step along a pinned course up to this high is evened out, a bigger one unpinned
BANK_KM, BANK_SIDE_GRAD = 4.0, 30.0  # held river courses: banks this wide (km, >= 2 px), then falling off (m/km)
ICE_SNOUT_GRAD = 50.0  # m/km: under ice, creep may lift a stream's bed by this much per km in from the ice's edge
BANK_MAX_Q = 300.0  # m^3/s: ... not lifting other rivers carrying this much
LIP_CAP_KM = 0.5  # km: a top stratum this thick holds a lip by itself (see lip_resistance)
SCARP_MIN_W = 0.3  # a designed reach takes its main fall at a landform scarp where the class weighs this much
LF_CHANNEL_Q = 5.0  # m^3/s: landform relief (zoom.landforms) is shaped around channels carrying this much
LF_FALL_KIND = {ZL.LF.ESCARPMENT: "scarp", ZL.LF.RIFT: "scarp", ZL.LF.CAPROCK: "bench", ZL.LF.LAVA_PLATEAU: "bench"}
BASIN_THROUGH_Q = 100.0  # m^3/s: a river this big cuts through a landform's closed basins (rift, scoured shield)
LF_LAKE_M, LF_LAKE_KM2 = 5.0, 2.0  # a landform's closed depression this deep and big can hold a lake...
LF_FULL_KM2 = 5.0  # ... one full to the brim (spilling) at least this big (a smaller one silts up: a flat)
LF_LOSS_MM = 300.0  # mm/yr: a lake's net evaporation where the world has no lake_evap / evaporation layers
# coastal plains' barrier coasts (PW-012): wave power (kW/m) and tide range (m) between which they
# fade in, the widest lagoon (km); marshes on land below MARSH_M m within MARSH_KM of the sea
BARRIER_WAVE, BARRIER_TIDE, BARRIER_LAGOON_KM = (4.0, 15.0), (2.5, 4.5), 8.0
MARSH_M, MARSH_KM = 4.0, 12.0


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
    e = np.asarray(elev, float)
    level = kernels.flood_fill(e, e <= 0, g.nbr_off, g.nbr_idx, 0.01)  # (priority_flood's filled surface alone)
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


def outflow_grad(g, elev: np.ndarray, down: np.ndarray, lab: np.ndarray, lvl: np.ndarray, exit_: np.ndarray,
                 reach_km: float) -> np.ndarray:
    """Per coarse lake, how steeply its outflow falls in the coarse world,
    m/km: the steepest mean descent from the lake's level to a cell on its
    river (the exit cell, then down the `downstream` chain), over the path
    from the nearest lake cell, up to `reach_km` along it (0 for a closed
    lake). A lake high in the mountains drains down a steep valley; one on
    a plain, gently."""
    out = np.zeros(len(lvl))
    for k, e in enumerate(exit_):
        if e < 0:
            continue
        cc = np.flatnonzero(lab == k)
        s = float(np.min(np.arccos(np.clip(g.centers[cc] @ g.centers[e], -1, 1)))) * R_KM
        c = int(e)
        for _ in range(64):
            if s > 0:
                out[k] = max(out[k], (lvl[k] - max(float(elev[c]), 0.0)) / s)
            n = int(down[c])
            if n < 0 or lab[n] == k or s > reach_km:
                break
            s += float(np.arccos(np.clip(g.centers[c] @ g.centers[n], -1, 1))) * R_KM
            c = n
    return out


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
        # the water the river runs out into, against its own depth (PW-847; Wright 1977): over a
        # shallow floor the outflow drags on the bed and drops its load in middle-ground bars that
        # split the channel again and again (a lobate fan of many mouths: the Lena, the Volga);
        # into water many channel depths deep it spreads as a buoyant plume that keeps its jet, and
        # a few channels build long between their levees (the Mississippi's bird's foot)
        depth = float(np.median(-elev[sea_sel][near])) if near.any() else 0.0
        buoy = float(smoothstep(*BUOYANT_DEPTHS, depth / max(0.27 * float(q[k]) ** 0.39, 1.0)))
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
                    "nb": n_mouths, "buoy": buoy, "depth_front_m": depth})
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


def _polyline_dist(x, y, line: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per point (x, y km): the distance to the polyline (km) and the arc
    length along it at the nearest point."""
    best, arc = np.full(len(x), np.inf), np.zeros(len(x))
    s0 = 0.0
    for a, b in zip(line[:-1], line[1:]):
        v = b - a
        L2 = float(v @ v)
        t = np.clip(((x - a[0]) * v[0] + (y - a[1]) * v[1]) / max(L2, 1e-12), 0.0, 1.0)
        d = np.hypot(a[0] + t * v[0] - x, a[1] + t * v[1] - y)
        m = d < best
        best[m], arc[m] = d[m], s0 + t[m] * np.sqrt(L2)
        s0 += np.sqrt(L2)
    return best, arc


def _finger_axis(x0: float, y0: float, dk, tk, Lk: float, th: float, rng) -> np.ndarray:
    """A delta finger's axis (km), from 0.3 Lk inland of the mouth (x0, y0)
    out to its tip Lk beyond it along dk: bending away from the fan's middle
    (th, its angle off the seaward direction) and wandering a little, as a
    distributary's levees build out (the Mississippi's passes curve)."""
    f = np.linspace(-0.3, 1.0, 27)
    out = np.clip(f, 0.0, 1.0)
    bend = (np.sign(th) * abs(rng.normal(0.06, 0.04))) if abs(th) > 0.05 else rng.normal(0.0, 0.05)
    wob = 0.02 * np.sin(2 * np.pi * f / rng.uniform(0.5, 0.8) + rng.uniform(0, 2 * np.pi)) * out
    off = Lk * (bend * out**2 + wob)
    return np.column_stack([x0 + f * Lk * dk[0] + off * tk[0], y0 + f * Lk * dk[1] + off * tk[1]])


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
    # the lobe, centred on the coast seaward of the mouth: furthest out for a river-dominated delta,
    # a broad low arc for waves (they spread its sand along the shore: cuspate, arcuate fronts)
    s0 = _coast_along(ind, nx, ny, res, dl["x"], dl["y"], u, 1.5 * R)
    la = R * (0.08 + 0.30 * wR + 0.06 * wW)  # (river: the front ~0.3 R out, ~0.4 R with the fingers: the Mississippi)
    lb = R * (0.3 - 0.1 * wR + 0.7 * wW + 0.2 * wT)
    amp = 1.0 - 0.5 * wT
    lobe[near] = amp * np.exp(-((a[near] - s0) / la) ** 2 - (b[near] / lb) ** 2)
    # ... and that lobe is land: the delta front stands out from the coast as far as the lobe
    # reaches (PW-847: it only nudged the indicator, so a big delta's front lay flush with the
    # coast and its fingers reached out of a straight shore), its rim scalloped by the mouth bars
    # of the many channels a fan builds (a few per lobe; fewer bigger ones where waves smooth it)
    phi = np.arctan2(b[near], a[near] - s0)
    m_ = 3 + int(rng.integers(0, 4))
    rim = 1.0 + 0.12 * (1 - wW) * np.sin(m_ * phi + rng.uniform(0, 2 * np.pi))
    e_rim = amp * np.exp(-(((a[near] - s0) / la) ** 2 + (b[near] / lb) ** 2) / rim ** 2)
    keep[near] = np.maximum(keep[near], 0.6 * (e_rim - 0.5))
    dl["lobe_at"] = (dl["x"] + s0 * u[0], dl["y"] + s0 * u[1])
    smooth[near] = smoothstep(1.4 * R, 0.9 * R, r[near]) * np.clip(0.85 * wW + 0.5 * wR, 0, 0.9)
    goals, kind = [], "fan"
    dl["finger_lines"] = []
    n = dl["nb"]
    # fingers: from the mouth out along a fan of directions, each bending
    # away from the fan's middle and wandering a little as it builds out
    # (the Mississippi's passes), narrowing to its tip
    # beyond the lobe's front (FINGER_LEN, BUOYANT_DEPTHS); a fan of many mouths over a shallow floor
    Lf = FINGER_LEN * R * wR ** 2 * dl.get("buoy", 1.0)
    front = 0.8 * la  # (how far the lobe carries the coast out)
    # (not where the tide's funnels take the branches instead: a finger
    # no branch heads for stood as a strip of land with no channel, PW-363)
    if Lf > 3 * res and n >= 1 and not (1.6 * wT > 0.3 and wT >= wR):
        n = min(n, FINGER_MAX)
        wf = max(1.5 * res, FINGER_W * R)
        spread = np.radians(50 + 15 * min(n, 5))
        th = (np.linspace(-0.5, 0.5, n) if n > 1 else np.zeros(1)) * spread + rng.normal(0, 0.08, n)
        for k in range(n):
            dk = np.cos(th[k]) * u + np.sin(th[k]) * t
            tk = np.array([-dk[1], dk[0]])
            Lk = front * np.cos(th[k]) + Lf * rng.uniform(0.6, 1.1)
            sc = _coast_along(ind, nx, ny, res, dl["x"], dl["y"], dk, 1.5 * R)
            line = _finger_axis(dl["x"], dl["y"], dk, tk, Lk + sc, th[k], rng)
            # (a finger builds out into the sea: none along a direction that runs on over land)
            lc_ = np.clip(np.floor(line[:, 0] / res + nx / 2).astype(int), 0, nx - 1)
            lr_ = np.clip(np.floor(ny / 2 - line[:, 1] / res).astype(int), 0, ny - 1)
            if sc > 0.3 * R or np.mean(ind[(lr_ * nx + lc_)[len(line) // 4:]] > 0) > 0.4:
                continue
            Lk += sc  # out from the coast
            near_k = near & (r < 1.2 * Lk + 3 * wf)
            c, s = np.full_like(px, np.inf), np.zeros_like(px)
            c[near_k], s[near_k] = _polyline_dist(px[near_k], py[near_k], line)
            s -= 0.3 * Lk  # (the axis starts 0.3 Lk inland of the mouth)
            wk_ = wf * (1.0 - 0.5 * np.clip(s / Lk, 0.0, 1.0))
            f = np.exp(-(c / wk_) ** 2) * smoothstep(-0.3 * Lk, 0.0, s) * smoothstep(Lk, 0.85 * Lk, s)
            # land at least along the axis, wider the more the river dominates
            # (none below a river weight of ~0.4)
            keep = np.maximum(keep, 0.3 * (1.6 * wR * f - 0.6))
            goals.append(tuple(line[-1]))
            dl["finger_lines"].append(line[np.searchsorted(np.linspace(-0.3, 1.0, len(line)), 0.0):])
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


def _count_mouths(dl: dict, px, py, land, rec, discharge, nx: int, ny: int, splits=()) -> int:
    """Channels of a delta reaching the sea: groups of land pixels that drain
    straight into the sea carrying >= 5% of the delta's discharge, among
    those its river's water reaches from the apex (down the receivers and
    every distributary split on the way); without an apex, those within R of
    the mouth. (Not a disc around the mouth: a ~350 km plain's would take in
    the neighbouring rivers' mouths.)"""
    mouth = land & (rec >= 0) & ~land[np.maximum(rec, 0)] & (discharge >= 0.05 * dl["q"])
    if dl.get("apex", -1) >= 0:
        kids = {s: k for s, k, _ in splits}
        seen = np.zeros(len(rec), bool)
        stack = [int(dl["apex"])]
        while stack:
            p = stack.pop()
            while p >= 0 and land[p] and not seen[p]:
                seen[p] = True
                stack += [c for c in kids.get(p, []) if c != rec[p]]
                p = int(rec[p])
        out = mouth & seen
    else:
        out = mouth & (np.hypot(px - dl["x"], py - dl["y"]) < dl["R"])
    if not out.any():
        return 0
    lab, _ = ZK.label_components(out, nx, ny)
    return int(len(np.unique(lab[out])))


# ---------------------------------------------------------------------------
# Glaciers (PW-127, PW-159): from each pixel's own climate, by the run's rule
# ---------------------------------------------------------------------------
# The surface mass balance is the run's and the time zoom's (icemass.balance),
# on each pixel's own climate (the bare ground's summer and winter at its own
# height, its rain): accumulation where its snow outlasts the summer on bare
# ground (so the snowline depends on the snowfall as well as the summer,
# PW-159), or under the coarse sheet's ice (its height and, on a big sheet,
# its own air mass keep it colder) where connected to such a start or to the
# coarse sheet's interior: the coarse ice's feedback applies only on the
# sheet itself, not on the warm valley floors of an iced coarse cell. From
# there the surplus is routed down the valleys (glacier_flow) as tongues that
# melt as bare ice (the same balance, no ice under them) over their width as
# they descend, so valley glaciers reach below the snowline only as narrow
# tongues fed from above (Franz Josef ends in rainforest at ~300 m). Widths:
# ~0.8 km at 0.1 km3/yr water equivalent (Franz Josef), ~2.6 km at the
# GL_F_MAX cap.
GL_W0, GL_F0, GL_W_EXP = 0.8, 1e8, 0.35  # tongue width km = W0 x (flux m3/yr / F0)^W_EXP
GL_F_MAX = 3e9  # m3/yr: at most this enters one tongue (Bering, Malaspina: a few km3/yr; a sheet's margin loses the rest along its length)
GL_MAX_KM = 100.0  # km: no tongue runs further below its zone (Pio XI ~64 km, Bering ~190 km in all)
GL_DRAW = 0.5  # a tongue narrower than this many pixels isn't drawn
GL_H0, GL_H_EXP = 250.0, 0.25  # m: valley ice thickness ~ H0 x (flux / F0)^H_EXP
# ... and no thicker than Nye's plastic snout, H = sqrt(L x) at x m from the
# terminus on land, L = 2 tau / (rho g) with a yield stress tau ~100 kPa
# (H ~150 m 1 km back, ~330 m 5 km back): a tongue thins to its end instead of
# stopping in an ice cliff (PW-350; calving fronts in water keep their height)
GL_NYE_M = 2 * 1.0e5 / (917.0 * 9.81)  # m (~22)
GL_NOISE_C = 1.0  # C: shade, aspect, drift: noise on the summer, lobate margins


def ice_ground(g, L: dict, ice: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per coarse cell: the warmest and coldest month (C) of the bare ground
    under any ice. The world's climate is on the ice surface
    (climate.ice_surface): this undoes it (icemass.ground_from_surface)."""
    land = L["elevation"] > 0
    ice = np.where(land, ice, 0.0)
    tw = np.asarray(L.get("warm_month", L["temperature"]), float)
    tc = np.asarray(L["cold_month"], float) if "cold_month" in L else 2 * np.asarray(L["temperature"], float) - tw
    gw, gc = tw.copy(), tc.copy()
    i = np.flatnonzero(ice > 0)
    if len(i):
        p = np.asarray(L["precipitation"], float)
        pj, pn = (np.asarray(L.get(k, p), float) for k in ("precipitation_jul", "precipitation_jan"))
        cov = icemass.sheet_cover(g, ice, air=icemass.sheet_air(g, ice))  # (as climate.compute's own, PW-1050)
        gw[i], gc[i] = icemass.ground_from_surface(g.lat[i], tw[i], tc[i], pj[i], pn[i], ice[i], cov[i])
    return gw, gc


def glaciers(h, rec, order, land, stop, nx: int, ny: int, res: float, warm_sl, cold_sl, cover, precip, jul,
             ice_c, lat, noise, tilt: float = 23.4) -> tuple[np.ndarray, np.ndarray]:
    """Glacier mask and ice thickness (m) on the surface h (with its
    drainage rec, order): see GL_*. warm_sl, cold_sl: the bare ground's
    warmest and coldest month reduced to sea level; cover: the coarse
    ice's icemass.sheet_cover; precip (mm/yr) and jul, its share in the
    April-September half; ice_c: the interpolated coarse ice (m); lat (deg);
    noise: ~unit fbm; tilt: the planet's (the balance is the ice-age cycle's
    average, as the run's)."""
    from ..tectonics.earth import ICE_MAX
    hl = np.maximum(h, 0)
    tw = warm_sl - LAPSE * hl + GL_NOISE_C * noise
    tc = np.minimum(cold_sl - LAPSE * hl, tw)
    pj, pn = 2 * precip * jul, 2 * precip * (1 - jul)
    ok = land & ~stop
    bare, _ = icemass.balance(lat, ok, tw, tc, pj, pn, 0.0, 0.0, tilt=tilt)
    on, _ = icemass.balance(lat, ok, tw, tc, pj, pn, ice_c, cover, tilt=tilt)
    acc = ok & (np.where(ice_c > 1, on, bare) > 0)
    lab, _ = ZK.label_components(acc, nx, ny)
    fed = np.zeros(int(lab.max()) + 2, bool)
    fed[lab[acc & ((bare > 0) | (ice_c > icemass.EDGE_H))]] = True
    zone = acc & fed[lab]
    # a tongue melts as bare ice, at the air's summer (no ice under it to raise it)
    bal = np.where(zone, np.where(ice_c > 1, on, bare), bare) * 0.917  # m w.e. per yr
    flux, wid, _ = ZK.glacier_flow(rec, order, bal, zone, stop | ~land, nx, res, GL_W0, GL_F0, GL_W_EXP,
                                   GL_F_MAX, GL_MAX_KM)
    tongue = ~zone & (flux > 0) & (wid >= GL_DRAW * res)
    # tongues wider than a pixel spread across their valley
    ice = zone | tongue
    half = np.where(tongue, wid / (2 * res), 0.0).reshape(ny, nx)
    for r in range(1, int(min(half.max(), 4.0)) + 1):
        ice |= _dilate(half >= r + 0.5, r).ravel() & land & ~stop
    th = np.clip(GL_H0 * (np.maximum(flux, 1.0) / GL_F0) ** GL_H_EXP, 20.0, ICE_MAX)
    # the snout (a tongue's, or the zone's where its outflow is too narrow to
    # draw): Nye's profile, the mean of sqrt(L x) over each pixel's span along the flow
    flow = zone | tongue
    x = ZK.snout_distance(rec, order, flow, land & ~stop & ~flow, nx, res)
    fin = np.isfinite(x)
    a, b = 1000 * np.maximum(x[fin] - 0.5 * res, 0.0), 1000 * (x[fin] + 0.5 * res)
    nye = np.full(len(th), np.inf)
    nye[fin] = 2 / 3 * np.sqrt(GL_NYE_M) * (b**1.5 - a**1.5) / (b - a)
    th = np.minimum(th, nye)
    th = np.where(zone, np.maximum(th, ice_c), th)  # (the coarse sheet's ice is the world's)
    th = np.where(ice & ~zone & ~tongue, _spread(th, tongue, nx, ny), th)
    return ice, np.where(ice, th, 0.0)


D8_NONE = 255  # the receiver layer's "no receiver" (an outlet, the sea, or water leaving the zoom)


def d8_slots(rec: np.ndarray, nx: int) -> np.ndarray:
    """Receivers (pixel indices, -1 none) as D8 slots, uint8: the neighbour
    (dr, dc) is slot 3 * (dr + 1) + (dc + 1), skipping the centre (0 NW, 1 N,
    2 NE, 3 W, 4 E, 5 SW, 6 S, 7 SE; rows run south), D8_NONE without one.
    The zoom's `receiver` layer (PW-373), as runs' nbr_slot layers."""
    rec = np.asarray(rec, np.int64)
    i = np.arange(len(rec))
    has = rec >= 0
    dr, dc = rec // nx - i // nx, rec % nx - i % nx
    if (has & ((np.abs(dr) > 1) | (np.abs(dc) > 1) | (rec == i))).any():
        raise ValueError("receivers must be D8 neighbours")
    s = 3 * (dr + 1) + (dc + 1)
    return np.where(has, s - (s > 4), D8_NONE).astype(np.uint8)


def _spread(v: np.ndarray, m: np.ndarray, nx: int, ny: int) -> np.ndarray:
    """v carried a few pixels out from the pixels m: each pixel takes its
    nearest (the max of the equally near; a tongue's sides take the
    tongue's thickness beside them, so a thinned snout stays thin)."""
    out = np.where(m, v, 0.0).reshape(ny, nx)
    for _ in range(4):
        b = out.copy()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            b = np.maximum(b, _shift(out, dy, dx, 0.0))
        out = np.where(out > 0, out, b)
    return out.ravel()


# ---------------------------------------------------------------------------
# The refinement
# ---------------------------------------------------------------------------
def land_world(world: dict) -> tuple[dict, np.ndarray]:
    """(the world the zoom's terrain is built on, per coarse cell how far
    its true bed lies below that, m). Worlds store the true bed, and a bed
    below the sea under grounded ice is land (geo.is_land, PW-307). The
    zoom's terrain passes model land as ground above the sea (a pixel is
    land where its ground is above it; rivers graded to it, lakes, creep),
    so they build on the land view: such a cell's bed at 1 m, its ice
    thinned to keep the surface (isostasy.land_view), so the coastline and
    the ice surface are the world's. build() then sinks the bed under its
    glaciers to the true one, the ice thickened by as much (PW-356)."""
    L = world["layers"]
    if "ice" not in L:
        return world, np.zeros(len(L["elevation"]))
    e, ice, low = land_view(L["elevation"], L["ice"])
    if not low.any():
        return world, np.zeros(len(e))
    sunk = e - np.asarray(L["elevation"], float)
    e = e.astype(np.asarray(L["elevation"]).dtype)
    out = {**L, "elevation": e, "ice": ice}
    if "lake_level" in L:  # (no lake under the ice: its level is the ground's)
        out["lake_level"] = np.where(low, e, L["lake_level"])
    return {**world, "layers": out}, sunk


class ZoomCtx:
    """The working state of one regional zoom build: the build() arguments and every array or table that more than one
    stage reads. The stages (stage_*.py) read and write it as attributes; a stage's own temporaries stay local to it.
    An attribute a stage has not set yet raises AttributeError, as an unbound local would."""

    __slots__ = ("iterations", "lat", "log", "lon", "peoples", "res_km", "river_min_flow", "seed", "size_km", "world",
                 "BR", "Kr", "L", "P", "Pc", "Pk", "S", "active", "all_falls", "amp_land", "area", "banks", "barrier",
                 "base", "bi_island", "bi_layer", "biome", "bottom", "branch", "c_idx", "cap", "carved", "cell_area",
                 "cell_means", "cexit", "cgrad", "chain_km", "clab", "clamp", "clim_f", "clvl", "coarse", "course",
                 "cov_f", "cqout", "cut", "cx", "cy", "cz", "d_sea", "delta_floor", "deltas", "depth", "detail",
                 "discharge", "down", "e_bed", "e_c", "e_land", "e_sea", "edge", "elev", "fields", "fit_c", "fit_log",
                 "fit_w", "fjord", "flow", "form_f", "fr", "full_px", "g", "gc_sl", "glac_form", "glac_loess",
                 "glac_stats", "glacier", "glacier_mask", "ground_up", "gw_sl", "h", "halo", "hf", "ice", "ice_n",
                 "ice_th", "idx", "ind", "ind_n", "inflow", "inflow_pts", "inside", "interior_c", "isl", "jitter",
                 "jitter_g", "jul_f", "keep", "keep_means", "kpix", "kps", "lake", "lake_c", "lake_depth", "lake_id",
                 "lake_in", "lake_info", "lake_kind", "lake_loss", "lake_outlets", "lake_seq", "lakes", "lakes_out",
                 "land", "land_all", "land_c", "lat_px", "layers", "lf", "lf_counts", "lf_gorges", "lf_lake",
                 "lf_overlay", "lf_sink", "lobe", "logC", "make_branches", "marsh", "minor_add", "n_in",
                 "n_rivers_in", "n_splits", "north", "npx", "nx", "ny", "outlet", "outs", "ov_dst", "ov_src", "own",
                 "own_s", "pin_dst", "pin_pairs", "pin_src", "pix_lat", "place_falls", "plunge", "precip", "px", "py",
                 "q_course", "r_c", "rapids", "rapids_lift", "rec", "rec_out", "region", "rel", "reroute", "res",
                 "rims", "ring", "ring_lvl", "ring_px", "riv_cells", "riv_ids", "riv_q", "river_segs", "rock",
                 "rock_f", "rough", "route", "rug", "runoff", "s_land", "s_pix", "s_sea", "sat", "scarp", "sea",
                 "sea_floor", "sel", "size_in", "smooth_c", "soft", "sp", "splits", "srcg", "srcq", "stages", "stats",
                 "sunk", "surf", "surf_f", "t0", "t_cold", "t_fit", "t_warm", "taper", "target", "temp", "tide_f",
                 "tilt_w", "top_falls", "tr", "trunk_px", "veg_l", "vf", "vpin", "vtarget", "vz", "wC", "wD", "wR_f",
                 "wS", "wW_f", "w_cp", "water", "wave_f", "wetland", "wv", "xs", "ys", "zD", "zS", "z_course")


def build(world: dict, lat: float, lon: float, size_km: float = 1000.0, res_km: float = 2.0,
          seed: int = 1, iterations: int = 15, river_min_flow: float = 3.0, log=print, peoples: dict | None = None) -> dict:
    """Build the regional zoom of the world round (lat, lon): size_km square at res_km per pixel. The pipeline, stage by
    stage (each in stage_*.py, on a shared ZoomCtx): see the module docstring."""
    ctx = ZoomCtx()
    ctx.world = world
    ctx.lat = lat
    ctx.lon = lon
    ctx.size_km = size_km
    ctx.res_km = res_km
    ctx.seed = seed
    ctx.iterations = iterations
    ctx.river_min_flow = river_min_flow
    ctx.log = log
    ctx.peoples = peoples
    STG_T.frame_and_grid(ctx)
    STG_T.coarse_fields(ctx)
    STG_T.delta_plains(ctx)
    STG_T.coastline(ctx)
    STG_T.detail(ctx)
    STG_T.mean_correction(ctx)
    STG_T.volcanoes(ctx)
    STG_T.tides_and_flats(ctx)
    STG_T.landform_classes(ctx)
    STG_R.coarse_rivers(ctx)
    STG_R.categorical_layers(ctx)
    STG_L.first_glaciers(ctx)
    STG_L.lakes(ctx)
    STG_L.drainage_tools(ctx)
    STG_L.fit_setup(ctx)
    STG_L.landscape_loop(ctx)
    STG_L.final_drainage(ctx)
    STG_L.shoreface(ctx)
    STG_F.crop_halo(ctx)
    STG_F.climate_on_terrain(ctx)
    STG_F.vegetation_layers(ctx)
    STG_F.coastal_life(ctx)
    STG_F.ice_bed(ctx)
    STG_F.stats(ctx)
    return STG_F.assemble(ctx)


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
            (2600, (136, 116, 104)), (3600, (184, 178, 170)), (4800, (224, 218, 208))]  # (bare rock: ice is tinted apart)
LAND_DRY = [(0, (206, 188, 140)), (300, (196, 172, 124)), (900, (184, 154, 112)), (1700, (160, 128, 96)),
            (2600, (136, 116, 104)), (3600, (184, 178, 170)), (4800, (224, 218, 208))]  # (bare rock: ice is tinted apart)
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
    """The satellite view in each hemisphere's summer (satellite.py), hill-shaded, with the rivers."""
    Lr = z["layers"]
    h, res = Lr["elevation"].astype(float), z["res"]
    water = Lr["water"]
    col = z["satellite"]["year"].astype(float)
    shade = hillshade(np.where(water == 2, h + Lr["lake_depth"], h), res)
    s = np.where((water == 0)[..., None], 0.35 + 0.85 * shade[..., None], 0.9 + 0.15 * shade[..., None])
    col = col * s
    if "tide_range" in Lr:  # tidal flats: sea floor above low tide (mud at low water)
        tr = Lr["tide_range"]
        flat = (water == 1) & (h > -0.5 * tr) & (tr > 0.8)
        col = np.where(flat[..., None], col * 0.5 + np.array([112, 104, 84.0]) * 0.5, col)
    q, area = Lr["discharge"], Lr["drainage_area"]
    land = (water == 0) & (Lr["ice"] <= 0)
    riv = (area >= RIVER_MIN_AREA * max(res / 2.0, 1.0)) & (q > 30.0) & land
    a = np.clip(0.25 + 0.2 * np.log10(np.maximum(q, 1e-9) / 100.0), 0.2, 0.9) * riv
    wide = (2.0 / res) ** 2  # a pixel covers less river at finer resolution
    for qq, r in ((3000.0 * wide, 1), (30000.0 * wide, 2)):  # big rivers are drawn wider
        a = np.maximum(a, 0.9 * (_dilate(q > qq, r) & land))
    col = col * (1 - a[..., None]) + np.array(RIVER_RGB) * a[..., None]
    # (waterfalls and volcanoes are the viewer's overlays, not marks baked in here: PW-181)
    return np.clip(col, 0, 255).astype(np.uint8)


RIVER_RGB = (40, 72, 92)  # river water in the satellite view (as zoom.html draws it)


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
    "lake_kind": ("enum", "0 none; on lake pixels 1 fresh (open), 2 salt (closed: its river ends there); "
                          "3 a salt pan: a closed landform basin's dry floor (land)"),
    "discharge": ("m^3/s", "mean river discharge (runoff routed downhill, plus inflow at the edges; "
                           "open lakes pass theirs on at the outlet; split among delta distributaries)"),
    "drainage_area": ("km^2", "upstream area inside the region"),
    "receiver": ("D8 slot", "the pixel's downstream neighbour, as the landscape pass routed the water: "
                            "3 * (dr + 1) + (dc + 1) skipping the centre (0 NW, 1 N, 2 NE, 3 W, 4 E, 5 SW, 6 S, "
                            "7 SE; rows run south); 255 none (an outlet, the sea, or the water leaves the zoom)"),
    "precipitation": ("mm/yr", "annual precipitation (interpolated from the coarse world)"),
    "temperature": ("C", "mean annual temperature, lapse-rate adjusted to the fine elevation"),
    "ice": ("m", "glacier ice thickness: the coarse ice in accumulation zones, else from the ice flux (glaciers())"),
    "tide_range": ("m", "tidal range at sea (interpolated from the world's tide_range; 0 on land)"),
    "wave_power": ("kW/m", "mean wave power at sea (interpolated from the world's wave_power; 0 on land)"),
    "rock": ("ROCKS id", "basement rock (surface.ROCKS)"),
    "surface_rock": ("ROCKS id", "exposed rock: basement or sediment cover"),
    "climate": ("KOPPEN id", "Koppen class; alpine tundra/ice cap added from the fine elevation"),
    "biome": ("BIOMES id", "coarse grouping of the vegetation types (vegetation.biome_of); sea and lakes by "
                           "climate.biomes"),
    "landform": ("landform id", "landform class of the coarse cell (landform.CLASSES; legend 'landforms')"),
    "glacial_form": ("enum", "what the ice left (zoom.glacial, PW-092): 0 none; 1 trough (U-valley), 2 cirque, "
                             "3 moraine belt, 4 drumlin field, 5 outwash plain, 6 loess blanket (>= 2 m), "
                             "7 fjord (a trough the sea floods), 8 overdeepened or moraine-dammed lake, 9 esker, 10 kettle pit"),
    "loess": ("m", "wind-blown silt thickness: the world's soils' loess, or the zoom's glacial loess downwind of the "
                   "outwash where thicker (zoom.glacial; the ground under it is softened)"),
    "coastal_life": ("enum", "coastal and shallow-sea life (zoom.coastal, PW-188): 0 none, 1 coral reef, 2 kelp "
                             "forest, 3 seagrass meadow (sea); 4 mangrove, 5 salt marsh (land between the tides); "
                             "legend 'coastal_life'"),
    "barrier_island": ("enum", "1 barrier island, 2 lagoon, 3 tidal inlet (zoom.coast.islands, PW-622)"),
    "wetland": ("enum", "0 none; 1 marsh: a coastal plain's lowest wet ground near the sea and its lagoons; "
                        "2 the vegetation's wetlands (floodplains, mires, lake shores: swamp forest, marsh, bog, fen)"),
    "land_use": ("enum", "peoples' land use (zoom.peoples, PW-667; only on a zoom made with a peoples run): 0 wild, "
                         "1 cropland, 2 pasture, 3 burned grass, 4 managed woods, 5 settlement; legend 'land_use'"),
    "valley_floor": ("enum", "fine zooms (PW-412): 0 none; an alluvial river's valley floor: 1 floodplain, 2 its "
                             "meander belt (where a migrating channel sweeps), 3 the channel on it"),
    "floor_m": ("m", "fine zooms (PW-412): the valley floor's surface (under its channel too: where a migrating "
                     "channel leaves its bed); 0 off the floors"),
    # (layers with an encoding: stored scaled / as integers, store.encode; read with store.decode)
    "temperature_jul": ("C", "July mean temperature (the cells' July interpolated, so continuous across the equator), "
                             "lapse-rate adjusted", {"dtype": "<i2", "scale": 0.1}),
    "temperature_jan": ("C", "January mean temperature, lapse-rate adjusted", {"dtype": "<i2", "scale": 0.1}),
    "precipitation_jul": ("mm/yr", "precipitation in the July half-year (Apr-Sep), as a rate per year",
                          S.LAYERS["precipitation_jul"]),
    "precipitation_jan": ("mm/yr", "precipitation in the January half-year (Oct-Mar), as a rate per year",
                          S.LAYERS["precipitation_jan"]),
    "vegetation": ("id", "named vegetation type (vegetation.TYPES; legend 'vegetation'), per pixel "
                         "(zoom.vegetation)", S.LAYERS["vegetation"]),
    "tree_cover": ("%", "tree canopy cover", S.LAYERS["tree_cover"]),
    "plant_cover": ("%", "ground shaded by plants of any kind", S.LAYERS["plant_cover"]),
    "lai": ("m2/m2", "leaf area index, the year's mean", S.LAYERS["lai"]),
    "canopy_height": ("m", "height of the tallest layer covering >= 10% of the pixel (younger stands lower)",
                      S.LAYERS["canopy_height"]),
    "npp": ("g C/m2/yr", "net primary productivity", S.LAYERS["npp"]),
    "fire_return": ("yr", "mean years between fires (0: none)", S.LAYERS["fire_return"]),
    "radiation_index": ("ratio", "the year's sunshine on the slope / on flat ground at the same place "
                                 "(poleward slopes < 1; zoom.terrain)", {"dtype": "u1", "scale": 0.01}),
    "twi": ("ln m", "topographic wetness index ln(upslope area per m of contour / tan slope); "
                    "depends on the pixel size (zoom.terrain)", {"dtype": "u1", "scale": 0.1}),
    "river_dist": ("px", "distance to the nearest river (>= zoom.terrain.RIVER_Q m^3/s), pixels (x res_km "
                         "for km), at most 255", {"dtype": "u1"}),
    "coast_dist": ("px", "distance to the sea, pixels, at most 255 (0 at sea)", {"dtype": "u1"}),
    "cloud_jul": ("%", "cloud cover, July half-year (the world's, interpolated; the satellite view's clouds)",
                  {"dtype": "u1"}),
    "cloud_jan": ("%", "cloud cover, January half-year (the world's, interpolated)", {"dtype": "u1"}),
    # soils per pixel (zoom.vegetation / soils.zoom_mineral, PW-331), the world's names and encodings
    **ZVG.SOIL_LAYER_DOC,
    # human-use layers (humanuse.py, PW-099)
    **HU.zoom_layer_doc(),
    # game attributes (gameattrs.py, PW-206)
    **GA.zoom_layer_doc(),
}


def zoom_id(world_id: str, lat: float, lon: float, size_km: float, res_km: float, seed: int,
            iterations: int = 15, peoples: str | None = None) -> str:
    key = f"{world_id}|{lat:.4f}|{lon:.4f}|{size_km:g}|{res_km:g}|{seed}"
    if iterations != 15:  # the default keeps the ids it always had
        key += f"|it{iterations}"
    if peoples:  # (a zoom with a peoples run's land use is another zoom)
        key += f"|peoples{peoples}"
    return hashlib.sha1(key.encode()).hexdigest()[:6]


def save(z: dict, world_path: Path, world: dict, lat: float, lon: float, size_km: float, res_km: float,
         seed: int, iterations: int = 15, peoples: str | None = None) -> Path:
    world_id = world_path.stem
    zid = zoom_id(world_id, lat, lon, size_km, res_km, seed, iterations, peoples)
    out = S.path_of("zoom", zid)
    out.mkdir(parents=True, exist_ok=True)
    specs, arrays = {}, {}
    for k, v in z["layers"].items():
        units, desc, *enc = LAYER_DOC[k]
        specs[k] = {**(enc[0] if enc else {}), "units": units, "description": desc}
        arrays[k] = S.encode(v, specs[k]) if enc else v
    layout = S.write_layers(out, arrays, specs)
    h = z["layers"]["elevation"].astype(float)
    lo, hi = float(np.floor(h.min())), float(np.ceil(h.max()))
    hi = max(hi, lo + 1)
    write_png(out / "heightmap.png", np.round((h - lo) / (hi - lo) * 65535).astype(np.uint16))
    write_png(out / "preview.png", preview(z))
    for k, img in z["satellite"].items():
        write_png(out / SAT_FILES[k], img)
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
        "files": {"heightmap": "heightmap.png", "preview": "preview.png", "coarse": "coarse.png",
                  **{f[:-4]: f for f in SAT_FILES.values()}},
        "layers": layout,
        "heightmap": {"bits": 16, "min_m": lo, "max_m": hi,
                      "sea_level_value": int(round((0 - lo) / (hi - lo) * 65535)) if lo < 0 < hi else None,
                      "formula": "elev_m = min_m + value / 65535 * (max_m - min_m)",
                      "metres_per_step": round((hi - lo) / 65535, 4)},
        "legend": {**S.legends(), **({"land_use": ZP.legend()} if peoples else {})},
        **({"peoples": {"run": peoples, **z["stats"]["peoples"]}} if peoples else {}),
        "params": z["params"],
        "stats": z["stats"],
    }
    S.write_atomic(out / "zoom.json", json.dumps(meta, indent=1))
    update_index()
    return out


# the satellite view's images (unshaded; satellite.py's seasons -> file; zoom.json's files: name without .png)
SAT_FILES = {"year": "satellite.png", "jul": "satellite_jul.png", "jan": "satellite_jan.png"}


def add_satellite(ref: str | Path) -> Path:
    """(Re)makes a saved zoom's satellite view in place (satellite.py): its
    images, the cloud layers and the preview. Recomputes the plant fractions
    (zoom.vegetation.fractions, ~5 s)."""
    d = S.find_zoom(ref)
    meta, lay = load(d, decode=True)
    world = land_world(W.load(find_world(meta["source_world"]["id"])))[0]
    nx, ny, res = meta["nx"], meta["ny"], meta["res_km"]
    fr = Frame(meta["center"]["lat"], meta["center"]["lon"])
    xs = (np.arange(nx) + 0.5 - nx / 2) * res
    ys = (ny / 2 - np.arange(ny) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    lat = latlon(fr.to_sphere(X.ravel(), Y.ravel()))[0]
    fra = ZVG.fractions(d)
    nu = np.stack([fra[c].ravel() for c in vegetation.CODES])
    fields = ZVG.fine_fields(world, fr, X.ravel(), Y.ravel(), meta["size_km"])
    if fields.get("cloud_jul") is not None:
        cl = {f"cloud_{s}": np.round(100 * fields[f"cloud_{s}"]).reshape(ny, nx) for s in ("jul", "jan")}
        specs = {k: {**LAYER_DOC[k][2], "units": LAYER_DOC[k][0], "description": LAYER_DOC[k][1]} for k in cl}
        meta["layers"].update(S.write_layers(d, {k: S.encode(v, specs[k]) for k, v in cl.items()}, specs))
        lay.update(cl)
    tilt = float(world["meta"].get("params", {}).get("tilt", 23.4))
    sat = SAT.zoom_images(lay, nu, lat, tilt, res)
    for k, img in sat.items():
        write_png(d / SAT_FILES[k], img)
    write_png(d / meta["files"]["preview"], preview({"layers": lay, "res": res, "satellite": sat}))
    meta["files"].update({f[:-4]: f for f in SAT_FILES.values()})
    S.write_atomic(d / "zoom.json", json.dumps(meta, indent=1))
    return d


def add_game(ref: str | Path) -> Path:
    """(Re)makes a saved zoom's game attributes in place (gameattrs.py, PW-206). Recomputes the plant
    fractions (zoom.vegetation.fractions, ~5 s)."""
    d = S.find_zoom(ref)
    meta, lay = load(d, decode=True)
    world = W.load(find_world(meta["source_world"]["id"]))
    nx, ny, res = meta["nx"], meta["ny"], meta["res_km"]
    fr = Frame(meta["center"]["lat"], meta["center"]["lon"])
    xs = (np.arange(nx) + 0.5 - nx / 2) * res
    ys = (ny / 2 - np.arange(ny) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    lat = latlon(fr.to_sphere(X.ravel(), Y.ravel()))[0]
    fra = ZVG.fractions(d)
    nu = np.stack([fra[c].ravel() for c in vegetation.CODES])
    tilt = float(world["meta"].get("params", {}).get("tilt", 23.4))
    new = GA.zoom_layers(lay, res, lat, nu, tilt)
    specs = {}
    for k in new:
        units, desc, *enc = LAYER_DOC[k]
        specs[k] = {**(enc[0] if enc else {"dtype": "u1"}), "units": units, "description": desc}
    meta["layers"].update(S.write_layers(d, {k: S.encode(v, specs[k]) for k, v in new.items()}, specs))
    meta.setdefault("legend", {})["game"] = GA.legend()
    S.write_atomic(d / "zoom.json", json.dumps(meta, indent=1))
    return d


def add_humanuse(ref: str | Path) -> Path:
    """(Re)makes a saved zoom's human-use layers in place (humanuse.py, PW-099): the class maps and the legend."""
    d = S.find_zoom(ref)
    meta, lay = load(d, decode=True)
    nx, ny, res = meta["nx"], meta["ny"], meta["res_km"]
    fr = Frame(meta["center"]["lat"], meta["center"]["lon"])
    new = HU.zoom_layers(lay, res, HU.falls_pixels(meta.get("stats", {}).get("falls", []), fr, nx, ny, res))
    specs = {}
    for k in new:
        units, desc, *enc = LAYER_DOC[k]
        specs[k] = {**(enc[0] if enc else {"dtype": "u1"}), "units": units, "description": desc}
    meta["layers"].update(S.write_layers(d, {k: S.encode(v, specs[k]) for k, v in new.items()}, specs))
    meta.setdefault("legend", {})["human_use"] = HU.legend()
    S.write_atomic(d / "zoom.json", json.dumps(meta, indent=1))
    return d


def load(ref: str | Path, decode: bool = False) -> tuple[dict, dict]:
    """(meta, {layer: (ny, nx) array}) for zooms/<id> (or a path to it);
    raw as stored, or in real units with decode (scaled layers: float)."""
    d = S.find_zoom(ref)
    meta = json.loads((d / "zoom.json").read_text())
    raw = S.read_layers(d, meta["layers"])
    if decode:
        raw = {k: S.decode(np.asarray(v), meta["layers"][k]) for k, v in raw.items()}
    return meta, raw


def update_index():
    S.update_index("zoom")


def zoom(world_ref: str, lat: float, lon: float, size_km: float = 1000.0, res_km: float = 2.0, seed: int = 1,
         iterations: int = 15, log=print, peoples: str | None = None) -> Path:
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
    A = ZP.load(peoples, path.stem) if peoples else None  # (a peoples run of this world: its land use, PW-667)
    if A:
        peoples = A["id"]
    z = build(world, lat, lon, size_km, res_km, seed, iterations, log=log, peoples=A)
    with S.lock(S.zooms_dir(), zoom_id(path.stem, lat, lon, size_km, res_km, seed, iterations, peoples)):
        out = save(z, path, world, lat, lon, size_km, res_km, seed, iterations, peoples)  # (one writer per zoom folder)
    ZC.add_to_zoom(out.name, world=world)  # (the coast layers and features, PW-097: the islands are in the terrain already)
    add_deposits(out, world)
    return out


def add_deposits(zoom_dir: Path, world: dict) -> None:
    """The zoom's mineral deposits (zoom/resources.py, PW-610/618), a step of every zoom build: sited from the
    world's resource layers and the history kept with it (~1 s). Left out when the world has no resource layers
    (`--no-resources`, or a world not from a run)."""
    if W._RESOURCES.get() and "resource" in world["layers"]:
        from . import resources as ZR
        ZR.add_to_zoom(zoom_dir.name, log=lambda *a: None, world=world)
