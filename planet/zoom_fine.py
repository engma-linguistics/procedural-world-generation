"""Nested fine zoom (PW-129): a zoom of a zoom, ~25-100 km across at
25-200 m/px (docs/proposals/nested_fine_zoom.md, "Owner decisions").

A fine zoom takes a finished zoom as its coarse input, not a world: the
parent has already decided the geology, the climate, the drainage and
where every fall, lake and volcano is. The fine pass only reshapes the
ground below the parent's pixel scale and redraws what depends on that
shape. Nesting is progressive (world -> zoom 0.5-4 km/px -> fine 50 km at
100 m -> finer 25 km at 50 or 25 m): each step is at most MAX_STEP x finer
than its parent, and parents from 4 km/px down to 100 m/px are accepted,
so a fine zoom of a fine zoom works the same way.

Steps (the proposal's 1-6):
1. Projection: azimuthal equidistant round the fine centre (zoom.Frame);
   every fine pixel's position in the parent's frame is computed exactly.
2. Target surface: the parent's ground, bicubic (Keys; it passes through
   the parent's pixel centres), plus detail noise from ~2 parent px down to
   ~4 fine px at 3D planet positions (sibling fine zooms agree), its
   amplitude from the parent's local relief and the rock's ruggedness
   (zoom.RUGGED). Categorical layers nearest after a noisy warp.
3. Imposed water: the parent's rivers (its `receiver` layer, PW-373) as
   Catmull-Rom polylines through the parent pixel centres, warped by < half
   a parent px between them, their beds on the parent's water surface;
   channels as wide as hydraulic geometry says (w ~ 4 Q^0.5 m). The
   parent's lakes at their surface, outlined by the warp.
4. Falls: each parent fall keeps the parent's drop exactly: the lip pixel
   at the parent's lip height, the next pixel down its course a plunge pool
   whose surface is the lip minus the parent's height_m, a gorge from there
   to the parent's foot along a smooth path (a fine parent's own, stored in
   its falls as gorge_path; else a B-spline on the parent's chain), cut by
   the distance from it: a floor, cliff walls up to the rim, a held
   headwall above the face. Gorges are drawn features: left out of the
   parent's means on both sides. Volcanoes keep the parent's summit
   height (the summit core is the parent's surface, bicubic, raised or
   lowered as one so its top is the parent's top_m): crater and vents as the
   parent drew them. Both carry the parent's index (parent_fall,
   parent_volcano) and a lineage back to the first zoom.
5. Landscape: the zoom's steady-state stream-power profile (ZK.integrate
   on priority-flood D8 routing), slope C A^-0.5 with C refitted per 3x3 parent
   pixels to keep their mean, a channel head (below HEAD_KM2 the hillslope is
   planar, at most the threshold slope of its rock), a little creep and
   texture, talus aprons under faces steeper than 45 degrees. Within one
   parent pixel of the region's edge the result blends back to the target,
   so the edge meets the parent's surface (the 3D inset needs no stitching).
6. Climate (the world's, as the parent: zoom_vegetation.fine_fields, lapse
   corrected to the fine ground; the parent's rain), the parent's ice
   (its surface kept over the fine ground), vegetation and soils
   (zoom_vegetation), coastal life (the parent's, warped), the satellite
   view.

Not redone at this scale (inbox drafts): glacier outlines (the parent's
ice, bilinear), landform overlays (dolines, dunes), deltas and reef forms
(as the parent drew them, interpolated).

Output: an ordinary zoom directory (zoom.load, the 2D viewer) with a
"parent_zoom" block in zoom.json ({id, res_km, offset_km, rect_px}) and the
parent's source_world.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from . import climate, vegetation
from . import store as S
from . import world as W
from . import zoom as Z
from . import zoom_coastal as ZCL
from . import zoom_kernels as ZK
from . import zoom_vegetation as ZVG
from . import satellite as SAT
from .climate import LAPSE
from .geo import R_KM, latlon
from .images import write_png

MAX_STEP = 20.0  # a fine zoom is at most this many times finer than its parent (owner, 2026-10-16)
MIN_STEP = 2.0  # ... and at least this many (else it adds nothing)
PARENT_RES = (0.1, 4.0)  # km/px: the parents the conditioning is designed for
MAX_PX = 1200  # pixels across
EDGE_PX = 3  # parent px: the built area (region + halo) stays this far inside the parent
HALO_PARENT_PX = 1.0  # parent px of terrain built round the region (drainage), cropped off
RIVER_AREA_PX = 25.0  # parent rivers imposed: draining at least this many parent pixels ...
RIVER_AREA_MIN = 1.0  # ... and at least this many km^2
WARP_PX = 0.4  # parent px: the rivers' and categories' warp between parent pixel centres
HEAD_KM2 = 0.25  # km^2: draining less than this, ground is hillslope, not channel
THRESHOLD_DEG = (26.0, 38.0)  # the hillslopes' threshold slope, soft .. rugged rock
RELAX_X = 1.25  # hillslopes cut down to this x their threshold slope to every neighbour
TALUS_DEG = 33.0  # apron below faces steeper than 45 degrees
ITERATIONS = 8  # landscape passes (the parent fixes the network: fewer than a zoom's 15)
MEAN_PASSES = 4  # final corrections keeping each parent pixel's mean
CORE_PX = 1.5  # parent px: a volcano's summit core held at the parent's surface (and >= CORE_FINE_PX)
CORE_FINE_PX = 8
VOLC_CUT_M = 30.0  # m: on a cone's flanks the fine ground stays within this of the parent's cone
GORGE_WALL_DEG = (55.0, 75.0)  # a gorge's walls below a fall: soft .. rugged rock (cliffs over their talus)
GORGE_FRAY_KM = 0.06  # km: its rims frayed by this much (spurs and alcoves)
POOL_DEPTH = (0.15, 3.0, 60.0)  # a plunge pool without the parent's depth: share of the drop, min, max m
SEC_PER_YR = Z.SEC_PER_YR


# ---------------------------------------------------------------------------
# Requests
# ---------------------------------------------------------------------------
def default_size(parent_res: float) -> tuple[float, float]:
    """(size_km, res_km) of a fine zoom of a parent at parent_res km/px:
    50 km at 100 m from a regional zoom, 25 km at 50 m from a fine zoom."""
    if parent_res <= 0.25:
        return 25.0, round(parent_res / 2, 4)
    res = max(0.1, parent_res / MAX_STEP)
    return 500 * res, res


def check(pmeta: dict, lat: float, lon: float, size_km: float, res_km: float) -> None:
    """Raises ValueError (with what to do instead) for a request the
    conditioning can't honour: a parent too coarse or too fine, a step over
    MAX_STEP, a region not well inside the parent."""
    rp = float(pmeta["res_km"])
    if not PARENT_RES[0] - 1e-9 <= rp <= PARENT_RES[1] + 1e-9:
        raise ValueError(f"fine zooms nest in zooms of {PARENT_RES[0]:g}-{PARENT_RES[1]:g} km/px; "
                         f"zoom {pmeta['id']} is {rp:g} km/px")
    if res_km <= 0:
        raise ValueError("res_km must be positive")
    step = rp / res_km
    if step > MAX_STEP * (1 + 1e-6):
        nest = (f"make a zoom at >= {rp / MAX_STEP * 1000:g} m/px of it first, then zoom into that"
                if rp / MAX_STEP >= PARENT_RES[0] - 1e-9 else
                f"the finest fine zoom of it is {rp / MAX_STEP * 1000:g} m/px (fine zooms nest in zooms of "
                f">= {PARENT_RES[0] * 1000:g} m/px)")
        raise ValueError(f"{res_km * 1000:g} m/px is {step:.0f}x finer than zoom {pmeta['id']} ({rp:g} km/px); "
                         f"each nesting step is at most {MAX_STEP:g}x: {nest}")
    if step < MIN_STEP * (1 - 1e-6):
        raise ValueError(f"{res_km * 1000:g} m/px is only {step:.1f}x finer than zoom {pmeta['id']}; "
                         f"a fine zoom is at least {MIN_STEP:g}x finer than its parent")
    n = int(round(size_km / res_km))
    if not 32 <= n <= MAX_PX:
        raise ValueError(f"keep size_km / res_km within 32..{MAX_PX} px (asked {n})")
    if not -90 <= lat <= 90:
        raise ValueError("lat must be within -90..90")
    fp = Z.Frame(pmeta["center"]["lat"], pmeta["center"]["lon"])
    fr = Z.Frame(lat, lon)
    half = 0.5 * size_km + _halo_px(rp, res_km) * res_km
    t = np.array([-1.0, 0.0, 1.0]) * half
    X, Y = np.meshgrid(t, t)
    xp, yp = fp.to_plane(fr.to_sphere(X.ravel(), Y.ravel()))
    lim = 0.5 * pmeta["nx"] * rp - EDGE_PX * rp
    limy = 0.5 * pmeta["ny"] * rp - EDGE_PX * rp
    if np.abs(xp).max() > lim or np.abs(yp).max() > limy:
        raise ValueError(f"a {size_km:g} km fine zoom at {lat:g}, {lon:g} doesn't fit inside zoom {pmeta['id']} "
                         f"(it must stay {EDGE_PX * rp + _halo_px(rp, res_km) * res_km:.1f} km inside its edge)")


def _halo_px(rp: float, res: float) -> int:
    return int(np.ceil(HALO_PARENT_PX * rp / res)) + 2


def fine_id(parent_id: str, lat: float, lon: float, size_km: float, res_km: float, seed: int) -> str:
    """As zoom.zoom_id, keyed on the parent zoom (a "zoom:" prefix: a world may share its id)."""
    return Z.zoom_id(f"zoom:{parent_id}", lat, lon, size_km, res_km, seed)


# ---------------------------------------------------------------------------
# Sampling the parent
# ---------------------------------------------------------------------------
def _keys(t):
    """Keys' cubic convolution weights (a = -0.5) for offsets -1, 0, 1, 2."""
    a = -0.5
    out = []
    for d in (1 + t, t, 1 - t, 2 - t):
        d = np.abs(d)
        out.append(np.where(d <= 1, (a + 2) * d ** 3 - (a + 3) * d ** 2 + 1,
                            np.where(d < 2, a * d ** 3 - 5 * a * d ** 2 + 8 * a * d - 4 * a, 0.0)))
    return out


class _Parent:
    """A parent zoom's layers (2D, real units) sampled at fractional parent
    pixel coordinates (row r, col c; pixel centres at integers)."""

    def __init__(self, meta: dict, layers: dict):
        self.meta, self.L = meta, layers
        self.id = meta["id"]
        self.rp = float(meta["res_km"])
        self.nx, self.ny = int(meta["nx"]), int(meta["ny"])
        self.fr = Z.Frame(meta["center"]["lat"], meta["center"]["lon"])

    def coords(self, P: np.ndarray):
        x, y = self.fr.to_plane(P)
        return self.ny / 2 - y / self.rp - 0.5, x / self.rp + self.nx / 2 - 0.5

    def plane(self, r, c):
        """Parent plane km of parent pixel coordinates."""
        return (np.asarray(c) + 0.5 - self.nx / 2) * self.rp, (self.ny / 2 - np.asarray(r) - 0.5) * self.rp

    def _a(self, a):
        return np.asarray(self.L[a] if isinstance(a, str) else a, float)

    def bicubic(self, a, r, c):
        A = self._a(a)
        r0, c0 = np.floor(r).astype(int), np.floor(c).astype(int)
        wr, wc = _keys(r - r0), _keys(c - c0)
        out = np.zeros(len(r))
        for i, di in enumerate((-1, 0, 1, 2)):
            rr = np.clip(r0 + di, 0, self.ny - 1)
            for j, dj in enumerate((-1, 0, 1, 2)):
                out += wr[i] * wc[j] * A[rr, np.clip(c0 + dj, 0, self.nx - 1)]
        return out

    def bilinear(self, a, r, c):
        A = self._a(a)
        r0 = np.clip(np.floor(r).astype(int), 0, self.ny - 2)
        c0 = np.clip(np.floor(c).astype(int), 0, self.nx - 2)
        tr, tc = np.clip(r - r0, 0, 1), np.clip(c - c0, 0, 1)
        return ((1 - tr) * ((1 - tc) * A[r0, c0] + tc * A[r0, c0 + 1])
                + tr * ((1 - tc) * A[r0 + 1, c0] + tc * A[r0 + 1, c0 + 1]))

    def index(self, r, c):
        """Flat index of the nearest parent pixel."""
        return (np.clip(np.rint(r).astype(int), 0, self.ny - 1) * self.nx
                + np.clip(np.rint(c).astype(int), 0, self.nx - 1))

    def nearest(self, a, r, c):
        return np.asarray(self.L[a] if isinstance(a, str) else a).ravel()[self.index(r, c)]

    def receivers(self) -> np.ndarray:
        """The parent's D8 receivers (flat index, -1 none) from its receiver layer."""
        s = np.asarray(self.L["receiver"]).ravel().astype(int)
        k = s + (s >= 4)
        i = np.arange(self.nx * self.ny)
        rec = (i // self.nx + k // 3 - 1) * self.nx + (i % self.nx + k % 3 - 1)
        return np.where(s == Z.D8_NONE, -1, rec)


def _wsurf(L: dict) -> np.ndarray:
    """Water surface of a zoom's layers (lake surface on lakes, 0 at sea), 2D."""
    h = np.asarray(L["elevation"], float)
    w = np.asarray(L["water"])
    return np.where(w == 1, 0.0, np.where(w == 2, h + np.asarray(L["lake_depth"], float), h))


def _fall_chain(pa: _Parent, rec, ws, f: dict) -> list[int] | None:
    """Parent pixels from a fall's lip to its foot (flat indices), or None."""
    lip = int(f["px"][0]) * pa.nx + int(f["px"][1])
    if "foot_px" in f:  # (a fine parent's own fall: lip, pool, gorge to foot_px)
        foot = int(f["foot_px"][0]) * pa.nx + int(f["foot_px"][1])
        ch = [lip]
        while ch[-1] != foot and rec[ch[-1]] >= 0 and len(ch) < 10_000:
            ch.append(int(rec[ch[-1]]))
        return ch if ch[-1] == foot and len(ch) > 1 else None
    top, ch, run = ws.ravel()[lip], [lip], 0.0
    while rec[ch[-1]] >= 0 and len(ch) < 64:
        j = int(rec[ch[-1]])
        run += pa.rp * (1.4142 if (j - ch[-1]) % pa.nx and abs(j - ch[-1]) != 1 else 1.0)
        ch.append(j)
        if top - ws.ravel()[j] >= f["height_m"] - 0.5 or run > f.get("length_km", pa.rp) + 2 * pa.rp:
            break
    return ch if len(ch) > 1 else None


# ---------------------------------------------------------------------------
# The fine pass
# ---------------------------------------------------------------------------
def build(parent: tuple[dict, dict], world: dict, lat: float, lon: float, size_km: float, res_km: float,
          seed: int = 1, log=print) -> dict:
    """The fine zoom of `parent` ((meta, decoded layers), zoom.load) round
    (lat, lon), size_km across at res_km per pixel. world: the parent's
    source world (climate for the fine pixels). Returns a zoom dict as
    zoom.build (layers, stats, satellite, frame, ...) plus 'parent'."""
    t0 = time.time()
    pmeta, play = parent
    check(pmeta, lat, lon, size_km, res_km)
    pa = _Parent(pmeta, {k: np.asarray(v) for k, v in play.items()})
    rp, res = pa.rp, float(res_km)
    n = int(round(size_km / res))
    size_km = n * res
    hb = _halo_px(rp, res)
    nb = n + 2 * hb
    npx = nb * nb
    S_ = 1_000_003 * seed + 517
    world = Z.land_world(world)[0]

    # --- 1. projection ---------------------------------------------------
    fr = Z.Frame(lat, lon)
    xs = (np.arange(nb) + 0.5 - nb / 2) * res
    ys = (nb / 2 - np.arange(nb) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    px, py = X.ravel(), Y.ravel()
    P = fr.to_sphere(px, py)
    Pk = np.ascontiguousarray(P * R_KM)
    pr, pc = pa.coords(P)
    own = pa.index(pr, pc)
    row, col = np.divmod(np.arange(npx), nb)
    # km inside the region's edge (negative in the halo); the blend back to the parent's surface
    d_edge = np.minimum(np.minimum(col - hb + 0.5, nb - hb - col - 0.5),
                        np.minimum(row - hb + 0.5, nb - hb - row - 0.5)) * res
    ramp = max(rp, 8 * res)
    w_in = Z.smoothstep(0.5 * res, ramp, d_edge)
    ring = (row == 0) | (row == nb - 1) | (col == 0) | (col == nb - 1)

    # --- 2. target surface -----------------------------------------------
    hp = np.asarray(pa.L["elevation"], float)
    wp = np.asarray(pa.L["water"])
    wsp = _wsurf(pa.L)
    rec_p = pa.receivers()
    # the parent's falls in the region: lip -> foot chains, and the gorge below each as a smooth
    # path (a fine parent's own, as it drew it; else its chain's pixel centres, Catmull-Rom)
    falls_p = pmeta["stats"].get("falls", []) or []
    fall_links = {}  # parent link (i, j) -> fall number
    chains, paths = {}, {}
    gorge_p = np.zeros(pa.nx * pa.ny, bool)  # the parent's gorges: drawn features, not in the means
    for k, f in enumerate(falls_p):
        ch = _fall_chain(pa, rec_p, wsp, f)
        if ch is None:
            continue
        r_, c_ = divmod(ch[0], pa.nx)
        r2, c2 = divmod(ch[-1], pa.nx)
        x1, y1 = pa.plane(np.array([r_, r2]), np.array([c_, c2]))
        fx, fy = fr.to_plane(pa.fr.to_sphere(x1, y1))
        lim = size_km / 2 - ramp
        if np.abs(fx).max() > lim or np.abs(fy).max() > lim:
            continue
        chains[k] = ch
        for a_, b_ in zip(ch[:-1], ch[1:]):
            fall_links[(a_, b_)] = k
        paths[k] = _gorge_path(pa, ch, f, S_)  # (parent plane, km)
        gorge_p |= _parent_gorge(pa, ch, f, paths[k])
    hp_f = _fill(hp, gorge_p.reshape(hp.shape))  # (the parent's ground with its gorges filled to their rims)
    target = pa.bicubic(hp, pr, pc)
    target_f = pa.bicubic(hp_f, pr, pc)
    fill_t = target_f
    # local relief per parent pixel (rms difference to its 4 neighbours), the rock's ruggedness
    d2 = np.zeros_like(hp)
    for ax in (0, 1):
        g = np.diff(hp_f, axis=ax)
        pad = [(0, 0), (0, 0)]
        pad[ax] = (1, 0)
        d2 += np.pad(g * g, pad, mode="edge")
        pad[ax] = (0, 1)
        d2 += np.pad(g * g, pad, mode="edge")
    relief_p = np.sqrt(d2 / 4)
    relief = pa.bilinear(relief_p, pr, pc)
    rug_p = np.vectorize(lambda k: Z.RUGGED.get(int(k), 0.6))(pa.L["rock"]) if "rock" in pa.L else 0.6 + 0 * hp
    rug = pa.bilinear(rug_p, pr, pc)  # (smooth: a step at a parent pixel's edge drew its outline)
    lam = 2 * rp
    noise = ZK.fbm(Pk, lam, Z._octaves(lam, 4 * res), 0.55, S_ + 1) / 0.17
    ridge = ZK.ridged(Pk, lam, Z._octaves(lam, 4 * res), 0.55, S_ + 2) - 0.5
    amp = np.where(target > 0, np.clip(0.35 * relief * rug, 1.0, 300.0), np.clip(0.1 * relief, 0.0, 20.0))
    h = target_f + w_in * amp * ((1 - rug) * noise + rug * 1.5 * ridge)
    detail = h - target_f  # (also steers the drainage of the landscape pass: no D8 grain)
    # warp for the categorical layers (parent px)
    wr = WARP_PX * np.clip(ZK.fbm(Pk, 1.5 * rp, 3, 0.5, S_ + 3) / 0.17, -1.25, 1.25)
    wc = WARP_PX * np.clip(ZK.fbm(Pk, 1.5 * rp, 3, 0.5, S_ + 4) / 0.17, -1.25, 1.25)
    cr, cc = pr + wr, pc + wc

    def cat(name, default=0):
        return pa.nearest(name, cr, cc) if name in pa.L else np.full(npx, default)

    # --- 3a. rivers ------------------------------------------------------
    q_p = np.asarray(pa.L["discharge"], float).ravel()
    a_p = np.asarray(pa.L["drainage_area"], float).ravel()
    ws_flat = wsp.ravel()
    riv_p = (a_p >= max(RIVER_AREA_PX * rp * rp, RIVER_AREA_MIN)) & (wp.ravel() != 1) & (rec_p >= 0)  # (through lakes too: a course goes on)
    # only the parent pixels round the built area
    rr_p, cc_p = np.divmod(np.arange(pa.nx * pa.ny), pa.nx)
    box = ((rr_p >= np.floor(pr.min()) - 2) & (rr_p <= np.ceil(pr.max()) + 2)
           & (cc_p >= np.floor(pc.min()) - 2) & (cc_p <= np.ceil(pc.max()) + 2))
    riv_p &= box
    for ch in chains.values():
        riv_p[ch[:-1]] = True
    up_main = np.full(pa.nx * pa.ny, -1)
    order_q = np.argsort(q_p)
    for i in order_q:  # (ascending q: the biggest tributary wins)
        if riv_p[i] and rec_p[i] >= 0:
            up_main[rec_p[i]] = i
    links = np.flatnonzero(riv_p)
    # the beds: the parent's water surface, made to fall all the way down each course (a parent's
    # receivers cross its filled pits: a course there would climb, and its water slip into another
    # valley), 1 cm a link at least; a fall's lip keeps its height
    bed_p = ws_flat.copy()
    lips = {ch[0] for ch in chains.values()}
    order_p = ZK.receiver_order(np.where(riv_p, rec_p, -1))
    for i in order_p[::-1]:  # (headwater -> outlet)
        j = rec_p[i]
        if riv_p[i] and j >= 0 and j not in lips:
            bed_p[j] = min(bed_p[j], bed_p[i] - 0.01)
    seg_pts, seg_z, seg_q, seg_a, seg_t, seg_link, seg_pin = [], [], [], [], [], [], []
    pinned = {i for ch in chains.values() for i in (ch[0], ch[-1])}  # (a fall's lip and foot: not warped)
    river_segs = []
    xc_p, yc_p = pa.plane(rr_p, cc_p)
    for i in links:
        j = rec_p[i]
        if (i, j) in fall_links:  # (a gorge: drawn along its path in step 4)
            continue
        a0 = up_main[i] if up_main[i] >= 0 else -1
        b1 = rec_p[j] if (rec_p[j] >= 0 and riv_p[j]) else -1
        p1 = np.array([xc_p[i], yc_p[i]])
        p2 = np.array([xc_p[j], yc_p[j]])
        p0 = np.array([xc_p[a0], yc_p[a0]]) if a0 >= 0 else 2 * p1 - p2
        p3 = np.array([xc_p[b1], yc_p[b1]]) if b1 >= 0 else 2 * p2 - p1
        ln = np.hypot(*(p2 - p1))
        m = max(2, int(np.ceil(ln / (0.15 * res))))
        t = np.linspace(0, 1, m + 1)[:, None]
        pts = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                     + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
        seg_pts.append(pts)
        seg_t.append(t[:, 0])
        seg_z.append(bed_p[i] + (bed_p[j] - bed_p[i]) * t[:, 0])
        seg_q.append(np.full(m + 1, q_p[i]))
        seg_a.append(np.full(m + 1, a_p[i]))
        seg_link.append(np.full(m + 1, i))
        tt_ = t[:, 0]  # (the warp fades to nothing at a fall's nodes, continuous at every node)
        seg_pin.append((Z.smoothstep(0.0, 0.5, tt_) if i in pinned else 1.0)
                       * (Z.smoothstep(0.0, 0.5, 1 - tt_) if j in pinned else 1.0) * np.ones(m + 1))
    course = np.zeros(npx, bool)
    bed = np.full(npx, np.inf)
    c_q, c_a = np.zeros(npx), np.zeros(npx)
    q_in, a_in = np.zeros(npx), np.zeros(npx)  # the parent's rivers coming in from outside the built area
    c_rec = np.full(npx, -1)  # each course pixel's next pixel down its course (the drainage is pinned to it)
    if seg_pts:
        pts = np.concatenate(seg_pts)
        tt = np.concatenate(seg_t)
        zz, qq, aa = np.concatenate(seg_z), np.concatenate(seg_q), np.concatenate(seg_a)
        ll = np.concatenate(seg_link)
        # the courses warped (a planet-fixed field: links join; none at a fall's nodes, its lip stays put)
        Pp = pa.fr.to_sphere(pts[:, 0], pts[:, 1])
        bump = np.concatenate(seg_pin)
        Ppk = np.ascontiguousarray(Pp * R_KM)
        off_x = WARP_PX * rp * bump * np.clip(ZK.fbm(Ppk, 2 * rp, 2, 0.5, S_ + 11) / 0.17, -1.25, 1.25)
        off_y = WARP_PX * rp * bump * np.clip(ZK.fbm(Ppk, 2 * rp, 2, 0.5, S_ + 12) / 0.17, -1.25, 1.25)
        Pp = pa.fr.to_sphere(pts[:, 0] + off_x, pts[:, 1] + off_y)
        fx, fy = fr.to_plane(Pp)
        ci = np.floor(fx / res + nb / 2).astype(int)
        ri = np.floor(nb / 2 - fy / res).astype(int)
        ok = (ci >= 0) & (ci < nb) & (ri >= 0) & (ri < nb)
        k_px = ri * nb + ci
        np.minimum.at(bed, k_px[ok], zz[ok])
        np.maximum.at(c_q, k_px[ok], qq[ok])
        np.maximum.at(c_a, k_px[ok], aa[ok])
        course[k_px[ok]] = True
        # the parent's rivers from outside the built area come in at the first node of their course
        # inside the region (not in the halo: its ring is an outlet, the water could leave again at once)
        at0 = (tt == 0) & ok
        node_px = dict(zip(ll[at0].tolist(), k_px[at0].tolist()))
        for ch in chains.values():  # (a gorge's lip: its link is drawn in step 4)
            node_px.setdefault(ch[0], _px_of(fr, pa, ch[0], nb, res))
        # (once a river: one that left the built area and comes back already carries its water)
        been_in = np.zeros(len(rec_p), bool)
        for i in order_p[::-1]:
            j = rec_p[i]
            if riv_p[i] and j >= 0:
                been_in[j] |= been_in[i] or i in node_px
        for i0 in np.unique(ll[(tt == 0) & ~ok]):
            k_ = int(rec_p[i0])
            if k_ not in node_px or been_in[i0]:  # (not the link that crosses into the built area)
                continue
            for _ in range(int(4 * ramp / rp) + 8):
                if k_ < 0 or not riv_p[k_]:
                    break
                if k_ in node_px and d_edge[node_px[k_]] >= 2 * res:
                    q_in[node_px[k_]] += q_p[i0]
                    a_in[node_px[k_]] += a_p[i0]
                    break
                k_ = int(rec_p[k_])
        # each course pixel's next pixel: after its last visit (samples ranked down the parent's network,
        # so the chain only ever goes on down: a course meandering back over a pixel makes no loop)
        pos = np.empty(len(order_p), np.int64)
        pos[order_p] = np.arange(len(order_p))
        rank = -pos[ll].astype(float) + 0.999 * tt
        o = np.argsort(rank)
        a_, b_ = k_px[o][:-1], k_px[o][1:]
        nxt = (ll[o][:-1] == ll[o][1:]) & ok[o][:-1] & ok[o][1:] & (a_ != b_)
        nxt &= (np.abs(a_ // nb - b_ // nb) <= 1) & (np.abs(a_ % nb - b_ % nb) <= 1)
        last = np.full(npx, -np.inf)
        np.maximum.at(last, k_px[ok], rank[ok])
        nxt &= rank[o][:-1] >= last[np.clip(a_, 0, npx - 1)]  # (the pixel's last visit)
        c_rec[a_[nxt]] = b_[nxt]
        for d_ in range(len(seg_pts)):
            river_segs.append(np.column_stack(fr.to_plane(pa.fr.to_sphere(seg_pts[d_][:, 0], seg_pts[d_][:, 1]))))
    # beds fall all the way down a course, if only by a mm a pixel (a warped course can come back to a
    # pixel lower down; a parent's river can be level: the drainage must know which way it runs)
    src_c = np.flatnonzero(c_rec >= 0)
    for _ in range(4 * nb):
        prev = bed.copy()
        np.minimum.at(bed, c_rec[src_c], bed[src_c] - 1e-3)
        if np.array_equal(prev, bed):
            break
    # channel width (hydraulic geometry): big rivers several pixels wide
    width_km = 4.0 * np.sqrt(np.maximum(c_q, 0)) / 1000.0
    rad = np.floor(0.5 * width_km / res).astype(int)
    rad = np.where(course, rad, 0)
    while (course & (rad >= 1)).any():  # (each step one pixel out, the reach left one less)
        src = course & (rad >= 1)
        bz = np.where(src, bed, np.inf).reshape(nb, nb)
        rz = np.where(src, rad, 0).reshape(nb, nb)
        nbz, nrz = bz.copy(), np.zeros_like(rz)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nbz = np.minimum(nbz, Z._shift(bz, dr, dc, np.inf))  # (the lowest bed beside it: close enough)
            nrz = np.maximum(nrz, Z._shift(rz, dr, dc, 0))
        grow = (nrz.ravel() >= 1) & ~course
        if not grow.any():
            break
        bed = np.where(grow, nbz.ravel(), bed)
        rad = np.where(grow, nrz.ravel() - 1, np.where(src, 0, rad))
        c_q = np.where(grow, 0.0, c_q)
        c_a = np.where(grow, 0.0, c_a)
        course |= grow

    # --- 3b. lakes and the sea -------------------------------------------
    lake_p = (wp == 2).ravel()
    lab_p, _ = ZK.label_components(lake_p, pa.nx, pa.ny)
    # (a parent's plunge pools are redrawn here: its lake specks on fall chains aren't lakes)
    for ch in chains.values():
        for i in ch:
            for j in (i, *(i + d for d in (-1, 1, -pa.nx, pa.nx))):
                if 0 <= j < len(lab_p) and lab_p[j] >= 0 and (lab_p == lab_p[j]).sum() <= 4:
                    lab_p[lab_p == lab_p[j]] = -1
    nlab = int(lab_p.max()) + 1 if (lab_p >= 0).any() else 0
    level_p = np.zeros(max(nlab, 1))
    for k in range(nlab):
        level_p[k] = np.median(ws_flat[lab_p == k])
    lab_f = lab_p[pa.index(cr, cc)]
    lake_frac = pa.bilinear((lab_p >= 0).reshape(pa.ny, pa.nx).astype(float), pr, pc)
    lake = (lab_f >= 0) & (lake_frac + 0.25 * noise > 0.35)
    level = np.where(lake, level_p[np.maximum(lab_f, 0)], 0.0)
    lake &= target < level + 5.0
    sea_c = (h < 0) & ~lake
    lab_s, _ = ZK.label_components(sea_c, nb, nb)
    seed_s = sea_c & (pa.nearest(wp, pr, pc) == 1)
    keep = np.unique(lab_s[seed_s])
    sea = sea_c & np.isin(lab_s, keep[keep >= 0])
    land = ~sea & ~lake
    h = np.where(sea, np.minimum(h, -0.5), h)
    h = np.where(land, np.maximum(h, 0.5), h)
    course &= land
    lake_ground = np.minimum(h, level - 0.5)

    # --- 4. falls and volcanoes ------------------------------------------
    fixed = ring | sea | lake | course
    hw = np.where(sea, 0.0, np.where(lake, level, h))
    hw = np.where(course, np.maximum(bed, 0.5), hw)
    pool = np.zeros(npx, bool)
    pool_d = np.zeros(npx)
    fall_list = []
    # each fall: the lip at the parent's lip height, a plunge pool its drop below, and the gorge from
    # there to the foot laid along the fall's path (not the pixels of a D8 chain: at 50 m and 25 m they
    # were a staircase), cut by the distance from it: a floor falling evenly along it, walls rising at
    # a cliff's gradient to the rim (the surroundings, the parent's gorge filled; at the lip's level by
    # the face), held; the ground beyond the rim is the landscape pass's
    gorge = np.zeros(npx, bool)  # (drawn features: kept out of the parent's means, as the parent's own)
    g_wall, g_floor, g_out = np.zeros(npx, bool), np.zeros(npx), np.zeros((npx, 2))  # (walls: their floor
    # and the way out from the path: cut again into the finished ground)
    for k, ch in chains.items():
        f = falls_p[k]
        top = float(round(ws_flat[ch[0]], 2))
        bottom = float(round(top - f["height_m"], 2))
        Q = np.column_stack(fr.to_plane(pa.fr.to_sphere(paths[k][:, 0], paths[k][:, 1])))  # (fine plane, km)
        S = np.r_[0.0, np.cumsum(np.hypot(*np.diff(Q, axis=0).T))]
        L_ = float(S[-1])
        lip = int(_px_of(fr, pa, ch[0], nb, res))
        foot_ = int(_px_of(fr, pa, ch[-1], nb, res))
        # the path's pixels, lip to foot, none twice
        sd = np.linspace(0, L_, max(2, int(np.ceil(L_ / (0.15 * res)))) + 1)
        qx, qy = np.interp(sd, S, Q[:, 0]), np.interp(sd, S, Q[:, 1])
        kq = np.floor(nb / 2 - qy / res).astype(int) * nb + np.floor(qx / res + nb / 2).astype(int)
        seq = []
        for v in kq[np.r_[True, kq[1:] != kq[:-1]]].tolist():
            if v in seq:
                del seq[seq.index(v) + 1:]
            else:
                seq.append(v)
        seq = seq[seq.index(lip):] if lip in seq else [lip, *seq]
        seq = np.array(seq[:seq.index(foot_) + 1] if foot_ in seq else [*seq, foot_])
        if len(seq) < 2:
            continue
        q_f = float(f.get("discharge_m3s", q_p[ch[0]]))
        w_riv = 4.0 * np.sqrt(max(q_f, 0.0)) / 1000.0
        ws_foot = min(float(bed_p[ch[-1]]), bottom)
        hf = max(2 * w_riv, 0.6 * res)  # the floor's half width (4 river widths, at least a pixel)
        g_min = 1000.0 * np.tan(np.radians(GORGE_WALL_DEG[0]))  # m/km
        margin = hf + 2.0 * (max(top - ws_foot, 0.0) + 200.0) / g_min + 2 * res
        rs_, cs_ = np.divmod(seq, nb)
        lo_r, hi_r = max(int(rs_.min() - margin / res), 0), min(int(rs_.max() + margin / res) + 1, nb)
        lo_c, hi_c = max(int(cs_.min() - margin / res), 0), min(int(cs_.max() + margin / res) + 1, nb)
        ib = (np.arange(lo_r, hi_r)[:, None] * nb + np.arange(lo_c, hi_c)[None, :]).ravel()
        d, sp = _path_dist(px[ib], py[ib], Q, S)
        # the face between the lip's pixel and the next; the floor from the pool on
        s_face = float(_path_dist(np.array([0.5 * (px[lip] + px[seq[1]])]),
                                  np.array([0.5 * (py[lip] + py[seq[1]])]), Q, S)[1][0])
        s1 = float(_path_dist(px[seq[1:2]], py[seq[1:2]], Q, S)[1][0])
        frac = np.clip((sp - s1) / max(L_ - s1, 1e-6), 0.0, 1.0)
        zf = bottom + (ws_foot - bottom) * frac
        rim = np.maximum(fill_t[ib], zf)
        rim = np.where(rim < top, top - (top - rim) * frac ** 2, rim)
        # walls: one rock's gradient along the gorge (the caprock's: a rock per pixel drew facets), their
        # rims frayed into spurs and alcoves (planet-fixed noise, km scales: finer zooms agree)
        # (its rims frayed by a smooth planet-fixed field: finer zooms fray them the same way; slow enough
        # that a wall still climbs all the way to its rim; sampled along the path instead, it drew spokes
        # round the inside of a bend)
        rug_g = float(np.median(rug[ib]))
        lam_g = 10 * GORGE_FRAY_KM
        n1 = np.clip(ZK.fbm(Pk[ib], lam_g, 2, 0.5, S_ + 21) / 0.17, -1.25, 1.25)
        grad = 1000.0 * np.tan(np.radians(GORGE_WALL_DEG[0] + (GORGE_WALL_DEG[1] - GORGE_WALL_DEG[0]) * rug_g))
        e_ = d - hf
        e_ = e_ + GORGE_FRAY_KM * n1 * Z.smoothstep(0.0, 4 * GORGE_FRAY_KM, e_)
        cut = zf + np.maximum(e_, 0.0) * grad
        free = (sp >= s_face) & ~course[ib] & ~sea[ib] & ~lake[ib] & ~ring[ib] & ~gorge[ib]
        flo = free & (d <= hf)
        wal = free & (d > hf) & (cut < rim - 0.5)
        hw[ib[flo | wal]] = cut[flo | wal]
        # the headwall: the ground just above the face, as far out as the walls reach, held at the rim
        # (left to the pass, it drained over the face into the pool, was built up from the pool's level
        # and the parent's means then stacked a block's volume on it: pillars round the lip)
        head = ((sp < s_face) & (sp >= s_face - 2 * res) & ~course[ib] & ~sea[ib] & ~lake[ib] & ~ring[ib]
                & ~gorge[ib] & ((d - hf) * grad < rim - bottom) & (ib != lip))
        hw[ib[head]] = np.maximum(rim[head], top)
        g_wall[ib[wal]] = True
        g_floor[ib[wal]] = zf[wal]
        sc = np.clip(sp[wal], 0.0, L_)
        g_out[ib[wal]] = np.column_stack([px[ib[wal]] - np.interp(sc, S, Q[:, 0]),
                                          py[ib[wal]] - np.interp(sc, S, Q[:, 1])]) / d[wal][:, None]
        land[ib[flo]] = True
        # the course down its floor, falling all the way
        on = np.searchsorted(ib, seq[1:])
        gz = np.minimum.accumulate(np.minimum(zf[on], bottom) - 1e-3 * np.arange(len(on)))
        hw[seq[1:]] = gz
        hw[lip] = top
        course[seq] = True
        land[seq] = True
        c_rec[seq[:-1]] = seq[1:]
        # plunge pool at the face's foot
        depth = f.get("plunge_pool_m") or float(np.clip(POOL_DEPTH[0] * f["height_m"], POOL_DEPTH[1], POOL_DEPTH[2]))
        pr_px = max(0.5 * max(2 * w_riv, res) / res, 0.5)
        r0, c0 = divmod(int(seq[1]), nb)
        pm = (np.hypot(ib // nb - r0, ib % nb - c0) <= pr_px) & (ib != lip) & ~sea[ib] & (sp >= s_face)
        pm &= hw[ib] <= top  # (only below the lip's side: not the pixels upstream of it)
        pmask = np.zeros(npx, bool)
        pmask[ib[pm]] = True
        pool |= pmask
        pool_d = np.where(pmask, depth, pool_d)
        hw = np.where(pmask, bottom, hw)
        held = np.zeros(npx, bool)
        held[ib[flo | wal | head]] = True
        held[seq[1:]] = True
        gorge |= held | pmask
        fixed |= gorge | course
        lip_r, lip_c = divmod(lip, nb)
        ll_ = Z._latlon(fr.to_sphere(np.array([px[lip]]), np.array([py[lip]]))[0])
        # the path as drawn (a finer zoom of this one lays its gorge along it), every pixel or so
        ks = np.unique(np.r_[np.searchsorted(S, np.arange(0, L_, max(res, L_ / 200))), len(S) - 1])
        Pq = fr.to_sphere(Q[ks, 0], Q[ks, 1])
        foot = int(seq[-1])
        fall_list.append({**{a: v for a, v in f.items() if a not in ("px", "lat", "lon", "foot_px", "pool_px")},
                          "px": [lip_r - hb, lip_c - hb], "lat": round(ll_[0], 4), "lon": round(ll_[1], 4),
                          "top_m": top, "bottom_m": bottom, "plunge_pool_m": round(float(depth), 1),
                          "gorge_km": round(max(L_ - s_face, 0.0), 2),
                          "gorge_path": [[round(float(a), 5) for a in Z._latlon(P_)] for P_ in Pq],
                          "gorge_half_km": round(float(np.percentile(d[flo | wal], 95)) + 0.5 * res, 3)
                          if (flo | wal).any() else round(hf, 3),
                          "pool_px": [int(seq[1]) // nb - hb, int(seq[1]) % nb - hb],
                          "foot_px": [foot // nb - hb, foot % nb - hb],
                          "power_gw": round(9.81e-6 * q_f * float(f["height_m"]), 3),
                          "parent_fall": k, "lineage": [*f.get("lineage", []), k]})
    land = ~sea & (~lake | course) & ~pool
    lake = lake & ~course
    vol_list = []
    core = np.zeros(npx, bool)
    vol_cap, vol_floor = np.full(npx, np.inf), np.full(npx, -np.inf)
    for k, v in enumerate(pmeta["stats"].get("volcanoes", []) or []):
        if "lat" in v:
            Pv = latlon_to_xyz(v["lat"], v["lon"])
        else:
            Pv = pa.fr.to_sphere(np.array([v["x_km"]]), np.array([v["y_km"]]))[0]
        vx, vy = fr.to_plane(Pv[None, :])
        vx, vy = float(vx[0]), float(vy[0])
        # the cone's size from the parent's surface: where it has dropped 30% (the core, held), 60%
        # (its body) and 90% (its foot: the landscape pass shapes the flanks within VOLC_CUT_M of it)
        ang = np.linspace(0, 2 * np.pi, 16, endpoint=False)
        dist = np.arange(1, 61) * 0.5 * rp
        Pr = fr.to_sphere((vx + np.outer(dist, np.cos(ang))).ravel(), (vy + np.outer(dist, np.sin(ang))).ravel())
        prof = pa.bicubic(hp, *pa.coords(Pr)).reshape(len(dist), len(ang)).mean(1)
        fall_ = float(v["top_m"]) - prof
        hv_m = max(float(v.get("height_m", 0.0)), 1.0)
        r30 = dist[np.argmax(fall_ >= 0.3 * hv_m)] if (fall_ >= 0.3 * hv_m).any() else dist[-1]
        r60 = dist[np.argmax(fall_ >= 0.6 * hv_m)] if (fall_ >= 0.6 * hv_m).any() else dist[-1]
        r90 = dist[np.argmax(fall_ >= 0.9 * hv_m)] if (fall_ >= 0.9 * hv_m).any() else dist[-1]
        R = max(CORE_PX * rp, CORE_FINE_PX * res, float(r30))
        if max(abs(vx), abs(vy)) > size_km / 2 - ramp - R:
            continue
        dv = np.hypot(px - vx, py - vy)
        fl = dv <= max(min(float(r90), 2.5 * float(r60)), 1.5 * R)  # (a cone on a high plain never drops 90%)
        b_fl = pa.bicubic(hp, pr[fl], pc[fl])
        vol_cap[fl] = np.minimum(vol_cap[fl], b_fl + VOLC_CUT_M)
        vol_floor[fl] = np.maximum(vol_floor[fl], b_fl - VOLC_CUT_M)
        # held: the summit core at the parent's surface (raised or lowered as one to its top_m), the
        # cone's body out to r60 at the parent's surface with half the detail (young cones keep their
        # form; an old one's gullies are the parent's)
        cm = dv <= max(float(r60), R)
        base = pa.bicubic(hp, pr[cm], pc[cm])
        # (the shift as a peak at the summit, not a lift of the core: the parent's pixel there is the
        # mean of a 1-4 km cone top, its surface lower than the summit; lifting it all added volume
        # the parent's means then took off the flanks round it, a moat)
        taper = np.clip(1 - dv[cm] / R, 0, 1) ** 2
        delta = 0.0
        for _ in range(4):
            delta += float(v["top_m"]) - (base + delta * taper).max()
        hv = base + delta * taper + 0.5 * detail[cm] * np.clip((dv[cm] - R) / (0.3 * R), 0, 1)
        on = (hv > 0) & ~(course | pool)[cm]  # (a river past the cone keeps its bed)
        hw[np.flatnonzero(cm)[on]] = hv[on]
        h[np.flatnonzero(cm)[on]] = hv[on]
        land[np.flatnonzero(cm)[on]] = True
        sea[np.flatnonzero(cm)[on]] = False
        lake[np.flatnonzero(cm)[on]] = False
        top_i = np.flatnonzero(cm)[int(np.argmax(np.where(on, hv, -np.inf)))]
        hw[top_i] = float(v["top_m"])  # (exact: no rounding in the shift)
        core |= cm & (dv <= R) & (hw > 0) & ~course  # (the core held; the body round it kept near the parent's cone)
        vol_list.append({**v, "x_km": round(vx, 3), "y_km": round(vy, 3),
                         "summit_px": [int(top_i // nb - hb), int(top_i % nb - hb)],
                         "parent_volcano": k, "lineage": [*v.get("lineage", []), k]})
    fixed |= core | sea | lake | pool
    hw = np.where(sea, 0.0, hw)
    log(f"  conditioned on zoom {pa.id}: {len(links)} parent river links, {len(fall_list)} falls, "
        f"{len(vol_list)} volcanoes, {int(lake.sum())} lake px [{time.time() - t0:.1f}s]")

    # --- 5. landscape ----------------------------------------------------
    thr = 1000.0 * np.tan(np.radians(THRESHOLD_DEG[0] + (THRESHOLD_DEG[1] - THRESHOLD_DEG[0]) * rug))  # m/km
    gy, gx = np.gradient(np.where(wp == 0, hp_f, np.maximum(hp_f, 0)), rp)
    logC = np.log(np.maximum(_box3(np.hypot(gx, gy)).ravel() / 9 * rp, 1e-2))  # slope = grad at a parent pixel's area
    logC0 = logC.copy()  # (the fit stays within e^2.5 of it: a block of held pixels can't run it away)
    var = 0.3 * ZK.fbm(Pk, 0.5 * rp, 3, 0.5, S_ + 6) / 0.17
    jitter = Z.tie_jitter(Pk, res, S_ + 7)
    floor = np.maximum(np.where(land, 0.5, -1e9), vol_floor)
    cap = np.minimum(1e9, vol_cap)
    soft, scale = np.full(npx, 1e9), np.ones(npx)
    a_head = max(HEAD_KM2, 4 * res * res)
    px_area = res * res
    T_own = hp.ravel()
    nown = len(T_own)
    cnt = np.bincount(own, minlength=nown)
    active = land & ~fixed

    def ground(hw_):
        return np.where(sea, h, np.where(lake, lake_ground, np.where(pool, hw_ - pool_d, hw_)))

    def routing(hw_, outlet):
        filled, rec, order = ZK.flood_d8(hw_, outlet, nb, nb, 1e-3, jitter)
        dr, dc = rec // nb - row, rec % nb - col
        dist = np.where(rec >= 0, res * np.where((dr != 0) & (dc != 0), 1.41421356, 1.0), res)
        return filled, rec, order, dist

    # Means are kept over 3x3 parent pixels round each: a parent's
    # 1-px trench or step is its pixels' rendering of something narrower
    # (a canyon along its river), and kept pixel by pixel it came back as a
    # staircase of parent-pixel blocks; corrections are bicubic (no facets)
    def per_block(v):
        return _box3(v.reshape(pa.ny, pa.nx)).ravel()

    # (a fall's gorge is drawn, not shaped by the pass: the parent's gorges and the fine ones are left
    # out of the means on both sides; counted in, the fine gorge's volume, on another path than the
    # parent's, came back as ridges along its walls)
    cnt3 = per_block(cnt.astype(float))
    cnt_k = cnt * ~gorge_p
    cnt3k = per_block(cnt_k.astype(float))
    T3 = per_block(T_own * cnt_k) / np.maximum(cnt3k, 1)
    cntf3 = per_block(np.bincount(own, ~gorge, minlength=nown).astype(float))
    ok3 = (cnt3k >= 0.3 * 9 * (rp / res) ** 2) & (cntf3 >= 0.3 * cnt3)

    def block_gap(hw_):
        """Per parent pixel: (its block's target - fine mean) spread over the
        block's movable pixels, and their count (gorges left out)."""
        n_nf = per_block(np.bincount(own, active, minlength=nown).astype(float))
        m3 = per_block(np.bincount(own, np.where(gorge, 0.0, ground(hw_)), minlength=nown)) / np.maximum(cntf3, 1)
        # (spread over at least half the block: a few movable pixels among held ones took a block's
        # whole gap and stood as pillars, e.g. at a gorge's head)
        return np.where(ok3 & (n_nf >= 0.3 * cntf3), (T3 - m3) * cntf3 / np.maximum(np.maximum(n_nf, 0.5 * cntf3), 1), 0.0), n_nf

    def fine_of(v):
        return pa.bicubic(v.reshape(pa.ny, pa.nx), pr, pc)

    lg = fine_of(logC)
    for it in range(ITERATIONS):
        _, rec, order, dist = routing(np.where(active, hw + detail, hw), fixed)
        area = ZK.accumulate(rec, order, np.full(npx, px_area))
        s = np.minimum(thr, np.exp(lg + var) * np.maximum(area, a_head) ** -0.5)
        hn = hw.copy()
        ZK.integrate(hn, rec, order, s, dist, fixed, floor, soft, scale, cap)
        lb = ZK.local_base(hn, rec, order, fixed, floor, cap, own)
        dm, n_nf = block_gap(hn)
        rel = per_block(np.bincount(own, np.where(active, hn - lb, 0.0), minlength=nown)) / np.maximum(n_nf, 1)
        ok_o = (n_nf >= 3) & (rel > 0.5) & (dm != 0)
        step = np.where(ok_o, np.log(np.clip((rel + dm) / np.maximum(rel, 1e-9), 1 / 1.6, 1.6)), 0.0)
        logC = np.clip(logC + per_block(step) / np.maximum(per_block(ok_o.astype(float)), 1), logC0 - 2.5, logC0 + 2.5)
        lg = fine_of(logC)
        hw = hn
    # creep (rounded tops), then a texture below the drainage's scale
    kd = np.where(active, 0.25, 0.0)
    for _ in range(2):
        hw = np.where(active, ZK.diffuse(hw, kd, active, nb, nb), hw)
    tex = ZK.fbm(Pk, 6 * res, 2, 0.5, S_ + 8) / 0.17
    hw = np.where(active, hw + np.clip(0.04 * relief, 0.3, 12.0) * tex, hw)
    # talus: aprons at ~33 degrees below faces steeper than 45
    hw = _talus(hw, active, nb, res)
    # hillslopes no steeper than their threshold: the stream-power pass caps a slope only along the
    # flow, so two pixels draining apart stood hundreds of metres apart (needles and sawtooth crests at
    # 50 and 25 m); cut down to RELAX_X x the threshold to every hillslope neighbour (the held
    # features, walls and faces, stay steep), the volume put back at the blocks' scale below
    s_max = RELAX_X * thr
    hw = _relax(hw, active, s_max, nb, res)
    # the blocks' means: smooth corrections on the hillslopes (a cone's flanks no higher than the parent's cone)
    hw = np.where(active, np.clip(hw, vol_floor, vol_cap), hw)
    for _ in range(MEAN_PASSES):
        _, rec, order, _ = routing(hw, fixed)  # (never below where its water goes: a tenth of its relief kept)
        lb = ZK.local_base(hw, rec, order, fixed, floor, cap, np.zeros(npx, np.int64))  # (where its water is held: by
        # parent pixel, the base jumped at their edges and drew their outlines)
        hw = np.where(active, np.maximum(hw + fine_of(block_gap(hw)[0]), np.maximum(lb + 0.1 * (hw - lb), 0.5)), hw)
        hw = np.where(active, np.clip(hw, vol_floor, vol_cap), hw)
        hw = _relax(hw, active, s_max, nb, res, needles=True)  # (the corrections leave no needle)
    # back to the parent's surface at the region's edge
    blend = active  # (the imposed courses keep their beds: the parent's, so the edge still meets it)
    hw = np.where(blend, w_in * hw + (1 - w_in) * np.maximum(target, 0.5), hw)
    # the gorges' walls no higher than the ground at their rims, straight out from the path (held at
    # the parent's surface through the pass, a rim stood as a ridge where the fine ground beyond it is
    # a valley)
    if g_wall.any():
        iw = np.flatnonzero(g_wall & ~pool)
        rim_h = np.full(len(iw), np.inf)
        todo = np.ones(len(iw), bool)
        for m_ in range(1, 2 * nb):
            if not todo.any():
                break
            jx = px[iw] + m_ * res * g_out[iw, 0]
            jy = py[iw] + m_ * res * g_out[iw, 1]
            jc, jr = np.floor(jx / res + nb / 2).astype(int), np.floor(nb / 2 - jy / res).astype(int)
            inside = (jc >= 0) & (jc < nb) & (jr >= 0) & (jr < nb)
            j_ = np.clip(jr, 0, nb - 1) * nb + np.clip(jc, 0, nb - 1)
            out_ = todo & inside & ~gorge[j_] & ~pool[j_]
            rim_h[out_] = hw[j_[out_]]
            todo &= inside & ~out_
        hw[iw] = np.clip(rim_h, g_floor[iw], hw[iw])
        hw = _relax(hw, g_wall & ~pool, RELAX_X * thr, nb, res, needles=True)  # (a wall's pixel left standing alone)
    log(f"  landscape pass: {ITERATIONS} iterations [{time.time() - t0:.1f}s]")

    # --- drainage of the finished surface --------------------------------
    # (routed on the surface with the imposed courses and lakes sunk far below the ground, and the sea
    # below them: the flood follows them down to where the parent's water leaves, never out by the edge
    # where a river comes in; then pinned along each course: no slipping into a gorge beside a lip)
    outlet = ring | sea
    sunk = np.where(sea, -2e4, np.where(course | lake | pool, hw - 1e4, hw))
    _, rec, order, _ = routing(sunk, outlet)
    pin = course & (c_rec >= 0) & ~outlet
    pin &= hw[np.maximum(c_rec, 0)] <= hw  # (never up; a loop through a flat is broken below)
    for k_ in range(24):  # (a pin closing a loop with the flood's routing is dropped)
        rec2 = np.where(pin, c_rec, rec)
        order2 = ZK.receiver_order(rec2)
        if len(order2) == npx:
            rec, order = rec2, order2
            break
        stuck = np.ones(npx, bool)
        stuck[order2] = False
        pin &= ~(_on_loops(rec2, stuck) if k_ < 20 else stuck)
    fields_b = ZVG.fine_fields(world, fr, px, py, size_km + 2 * hb * res)
    runoff_px = fields_b["runoff"] / 1000.0 * px_area * 1e6 / SEC_PER_YR  # m^3/s from each pixel
    src_q = runoff_px + q_in
    src_a = np.full(npx, px_area) + a_in
    discharge = ZK.accumulate(rec, order, src_q)
    area = ZK.accumulate(rec, order, src_a)
    h = ground(hw)
    lake_depth = np.where(lake, level - lake_ground, np.where(pool, pool_d, 0.0))

    # --- crop the halo ---------------------------------------------------
    keep_px = ((row >= hb) & (row < hb + n) & (col >= hb) & (col < hb + n))
    new = np.full(npx, -1)
    new[keep_px] = np.arange(n * n)
    rec_out = np.where(rec[keep_px] >= 0, new[np.maximum(rec[keep_px], 0)], -1)

    def crop(a):
        return np.asarray(a)[keep_px]

    (h, sea, lake, pool, land, discharge, area, lake_depth, cr, cc, pr, pc, Pk, px, py, own, target, course_c) = (
        crop(a) for a in (h, sea, lake, pool, land, discharge, area, lake_depth, cr, cc, pr, pc, Pk, px, py, own,
                          target, course))
    nx = ny = n
    npx = n * n
    water = np.where(sea, 1, np.where(lake | pool, 2, 0)).astype(np.uint8)
    land = water == 0

    # --- 6. ice, climate, life -------------------------------------------
    ice_p = np.asarray(pa.L.get("ice", np.zeros_like(hp)), float)
    glacier = land & (pa.bilinear((ice_p > 0).astype(float), pr, pc) > 0.5)
    ice_surf = pa.bilinear(np.where(ice_p > 0, hp + ice_p, hp), pr, pc)
    ice = np.where(glacier, np.maximum(ice_surf - h, 1.0), 0.0)
    P = fr.to_sphere(px, py)
    pix_lat = latlon(P)[0]
    fields = {k: (None if v is None else np.asarray(v)[..., keep_px]) for k, v in fields_b.items()}
    for k_, name in (("p_jul", "precipitation_jul"), ("p_jan", "precipitation_jan")):
        if name in pa.L:
            fields[k_] = np.maximum(pa.bilinear(name, pr, pc), 0.0)
    precip = (np.maximum(pa.bilinear("precipitation", pr, pc), 0.0) if "precipitation" in pa.L
              else 0.5 * (fields["p_jul"] + fields["p_jan"]))
    hl = np.maximum(h + ice, 0)
    temp = fields["t_sl"] - LAPSE * hl
    t_warm = fields["warm_sl"] - LAPSE * hl
    t_cold = fields["cold_sl"] - LAPSE * hl
    north = fields["jul_warm"]
    rock_f = cat("rock").astype(np.uint8)
    surf_f = cat("surface_rock").astype(np.uint8)
    form_f = cat("landform").astype(np.uint8) if "landform" in pa.L else None
    clim_f = cat("climate", Z.SEA_CLIMATE).astype(np.uint8)
    clim_f = np.where(sea, Z.SEA_CLIMATE, clim_f)
    lone = land & (clim_f == Z.SEA_CLIMATE)
    clim_f = np.where(lone, np.where(t_cold >= 18, 0, np.where(t_cold > 0, 14, 28)), clim_f)
    clim_f = np.where(land & (clim_f < 28) & (t_warm < 10), 28, clim_f)
    clim_f = np.where(land & ((t_warm < 0) | glacier), 29, clim_f).astype(np.uint8)
    biome = climate.biomes(h, temp, precip, lake | pool)
    bare = (biome == 4) & ~glacier
    biome = np.where(bare, np.where(h > 1500, 15, np.where(precip < 250, 7, 5)), biome)
    biome = np.where(glacier, 4, biome).astype(np.uint8)
    marsh = land & (cat("wetland") == 1) & (h < Z.MARSH_M) & ~glacier
    ice_l = ice.astype(np.float32)
    vz = ZVG.compute(world, fr, nx, ny, res, seed, size_km,
                     ZVG.surface(h.astype(np.float32), lake_depth.astype(np.float32), water), water, ice_l,
                     discharge.astype(np.float32), area.astype(np.float32), marsh, fields=fields, log=log,
                     want_fractions=True, rock=surf_f, landform=form_f)
    veg_l, tr = vz["layers"], vz["terrain"]
    cl = cat("coastal_life").astype(np.uint8)
    cl = np.where(sea, np.where(np.isin(cl, (1, 2, 3)), cl, 0),
                  np.where(land & np.isin(cl, (4, 5)) & (h < 5.0), cl, 0)).astype(np.uint8)
    veg_l["vegetation"] = ZCL.name_vegetation(cl, veg_l["vegetation"])
    biome = vegetation.biome_of(veg_l["vegetation"], biome).astype(np.uint8)
    wetland = np.where(marsh, 1, np.where(land & np.isin(veg_l["vegetation"], list(ZVG.WETLAND_TYPES)), 2, 0)
                       ).astype(np.uint8)
    tide = pa.bilinear("tide_range", pr, pc) if "tide_range" in pa.L else np.zeros(npx)
    wave = pa.bilinear("wave_power", pr, pc) if "wave_power" in pa.L else np.zeros(npx)

    # --- stats -----------------------------------------------------------
    cnt_o = np.bincount(own, minlength=nown)
    full_o = cnt_o >= 0.9 * (rp / res) ** 2
    m_o = np.bincount(own, h, minlength=nown) / np.maximum(cnt_o, 1)
    err = (m_o - T_own)[full_o]
    c3 = _box3(cnt_o.reshape(pa.ny, pa.nx).astype(float)).ravel()
    full3 = c3 >= 0.9 * 9 * (rp / res) ** 2
    m3 = _box3(np.bincount(own, h, minlength=nown).reshape(pa.ny, pa.nx)).ravel() / np.maximum(c3, 1)
    t3 = _box3((T_own * cnt_o).reshape(pa.ny, pa.nx)).ravel() / np.maximum(c3, 1)
    err3 = (m3 - t3)[full3]
    edge = np.zeros((n, n), bool)
    edge[[0, -1], :] = edge[:, [0, -1]] = True
    edge = edge.ravel() & land & ~course_c  # (the imposed river beds cut below it, as the parent's own)
    stats = {
        "land_pct": round(100 * land.mean(), 1),
        "parent_land_pct": round(100 * float((pa.nearest(wp, pr, pc) == 0).mean()), 1),
        "mean_elev_m": round(float(h.mean()), 1),
        "parent_mean_elev_m": round(float(pa.nearest(hp, pr, pc).mean()), 1),
        "mean_land_elev_m": round(float(h[land].mean()), 1) if land.any() else None,
        # each parent pixel's mean kept (the parent pixels wholly inside)
        "parent_pixels": int(full_o.sum()),
        "parent_mean_rms_error_m": round(float(np.sqrt(np.mean(err ** 2))), 2) if err.size else None,
        "parent_mean_bias_m": round(float(err.mean()), 2) if err.size else None,
        # ... and of each 3x3 block of them (what the pass keeps: see BLOCK above)
        "parent_block_mean_rms_error_m": round(float(np.sqrt(np.mean(err3 ** 2))), 2) if err3.size else None,
        # the edge meets the parent's surface (bicubic)
        "edge_max_error_m": round(float(np.abs(h - target)[edge].max()), 2) if edge.any() else None,
        "min_m": round(float(h.min()), 1),
        "max_m": round(float(h.max()), 1),
        "max_discharge_m3s": round(float(discharge.max()), 1),
        "lakes": int(len(np.unique(ZK.label_components(lake | pool, nx, ny)[0][lake | pool]))),
        "wetland_pct": round(100 * float((wetland > 0).mean()), 2),
        "vegetation": vz["stats"],
        "lake_pct": round(100 * lake.mean(), 2),
        "parent_river_links": int(len(links)),
        "waterfalls": sorted(fall_list, key=lambda f: -f["height_m"] * f.get("discharge_m3s", 1.0))[:5],
        "falls": fall_list,
        "falls_count": {"30m": sum(f["height_m"] >= 30 for f in fall_list),
                        "100m": sum(f["height_m"] >= 100 for f in fall_list)},
        "volcanoes": vol_list,
        "coastal_life": {k: round(float((cl == v).sum() * res * res), 2)
                         for k, v in (("coral_reef", 1), ("kelp", 2), ("seagrass", 3), ("mangrove", 4),
                                      ("salt_marsh", 5)) if (cl == v).any()},
    }
    layers = {
        "elevation": h.astype(np.float32),
        "water": water,
        "lake_depth": lake_depth.astype(np.float32),
        "lake_kind": np.where(water == 2, 1, 0).astype(np.uint8),
        "discharge": discharge.astype(np.float32),
        "drainage_area": area.astype(np.float32),
        "receiver": Z.d8_slots(rec_out, nx),
        "precipitation": precip.astype(np.float32),
        "temperature": temp.astype(np.float32),
        "temperature_jul": np.where(north, t_warm, t_cold), "temperature_jan": np.where(north, t_cold, t_warm),
        "precipitation_jul": fields["p_jul"], "precipitation_jan": fields["p_jan"],
        "ice": ice.astype(np.float32),
        "tide_range": np.where(sea, tide, 0).astype(np.float32),
        "wave_power": np.where(sea, wave, 0).astype(np.float32),
        "rock": rock_f,
        "surface_rock": surf_f,
        "climate": clim_f,
        "biome": biome,
        **({"landform": form_f} if form_f is not None else {}),
        "wetland": wetland,
        "coastal_life": cl,
        **veg_l,
        "radiation_index": tr["radiation_index"], "twi": tr["twi"],
        "river_dist": np.where(land, np.minimum(tr["river_dist"], 255), 0),
        "coast_dist": np.where(land, np.minimum(tr["coast_dist"], 255), 0),
        **({f"cloud_{s}": np.round(100 * fields[f"cloud_{s}"]) for s in ("jul", "jan")}
           if fields.get("cloud_jul") is not None else {}),
    }
    if "lake_kind" in pa.L:  # (a lake keeps the parent's kind: salt where the parent's is)
        lk = cat("lake_kind")
        layers["lake_kind"] = np.where(lake, np.where(lk == 2, 2, 1), np.where(pool, 1, 0)).astype(np.uint8)
    nu = np.zeros((vegetation.NP, npx))
    nu[:, vz["idx"]] = vz["nu"]
    tilt = float(world["meta"].get("params", {}).get("tilt", 23.4))
    sat = SAT.zoom_images({k: np.asarray(v).reshape(ny, nx) for k, v in layers.items()}, nu, pix_lat, tilt)
    coarse = {"elevation": pa.nearest(hp, pr, pc), "precipitation": precip, "river_segs": river_segs}
    # where the fine region sits in the parent
    cx_, cy_ = pa.fr.to_plane(fr.c[None, :])
    corners_rc = [pa.coords(fr.to_sphere(np.array([x]), np.array([y])))
                  for x, y in ((-size_km / 2, size_km / 2), (size_km / 2, -size_km / 2))]
    parent_block = {"id": pa.id, "res_km": rp, "name": pmeta.get("name"),
                    "offset_km": [round(float(cx_[0]), 3), round(float(cy_[0]), 3)],
                    "rect_px": [round(float(corners_rc[0][0][0]) + 0.5, 2), round(float(corners_rc[0][1][0]) + 0.5, 2),
                                round(float(corners_rc[1][0][0]) + 0.5, 2), round(float(corners_rc[1][1][0]) + 0.5, 2)],
                    "lineage": [*(pmeta.get("parent_zoom") or {}).get("lineage", []), pa.id]}
    return {"nx": nx, "ny": ny, "res": res, "frame": fr, "size_km": size_km,
            "layers": {k: np.asarray(v).reshape(ny, nx) for k, v in layers.items()},
            "stats": stats, "coarse": coarse, "rec": rec_out, "satellite": sat, "parent": parent_block,
            "seconds": round(time.time() - t0, 1),
            "params": {"iterations": ITERATIONS, "step": round(rp / res, 2), "halo_px": hb,
                       "river_area_km2": round(max(RIVER_AREA_PX * rp * rp, RIVER_AREA_MIN), 3),
                       "head_km2": a_head}}


def latlon_to_xyz(lat: float, lon: float) -> np.ndarray:
    from .geo import xyz
    return np.asarray(xyz(np.radians(lat), np.radians(lon)), float)


def _px_of(fr, pa: _Parent, i: int, nb: int, res: float) -> int:
    """The fine (built) pixel holding parent pixel i's centre."""
    r, c = divmod(int(i), pa.nx)
    x, y = pa.plane(np.array([r]), np.array([c]))
    fx, fy = fr.to_plane(pa.fr.to_sphere(x, y))
    return int(np.floor(nb / 2 - fy[0] / res)) * nb + int(np.floor(fx[0] / res + nb / 2))


def _path_dist(x: np.ndarray, y: np.ndarray, Q: np.ndarray, S: np.ndarray):
    """Distance (km) of points (x, y) from the polyline Q (k, 2), and how far
    along it (km, S its vertices') their nearest point is: negative before
    its start (along the first segment, extended)."""
    d = np.full(len(x), np.inf)
    s = np.zeros(len(x))
    for j in range(len(Q) - 1):
        vx, vy = Q[j + 1, 0] - Q[j, 0], Q[j + 1, 1] - Q[j, 1]
        ln2 = vx * vx + vy * vy
        if ln2 <= 0:
            continue
        t_raw = ((x - Q[j, 0]) * vx + (y - Q[j, 1]) * vy) / ln2
        t = np.clip(t_raw, 0.0, 1.0)
        dj = np.hypot(x - Q[j, 0] - t * vx, y - Q[j, 1] - t * vy)
        better = dj < d
        d = np.where(better, dj, d)
        s = np.where(better, S[j] + (np.minimum(t_raw, 1.0) if j == 0 else t) * np.sqrt(ln2), s)
    return d, s


def _gorge_path(pa: _Parent, ch: list[int], f: dict, seed: int) -> np.ndarray:
    """A fall's gorge, lip -> foot, as a smooth path in the parent's plane
    (km, (k, 2)): a fine parent's own path, as it drew it (its ends moved to
    the lip's and the foot's pixel centres, where the courses above and
    below meet it); else a cubic B-spline on the chain's pixel centres (through
    its ends only: through every centre, Catmull-Rom, it kept the D8 chain's
    elbows), warped as the parent's rivers are (none at its ends)."""
    r, c = np.divmod(np.asarray(ch), pa.nx)
    P = np.column_stack(pa.plane(r, c))
    if f.get("gorge_path"):
        X = np.array([latlon_to_xyz(a, b) for a, b in f["gorge_path"]])
        G = np.column_stack(pa.fr.to_plane(X))
        far = (np.hypot(*(G - P[0]).T) > 0.5 * pa.rp) & (np.hypot(*(G - P[-1]).T) > 0.5 * pa.rp)
        return np.vstack([P[:1], G[far], P[-1:]])
    ext = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    t = np.linspace(0, 1, 9)[:-1, None]
    out = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = ext[i:i + 4]
        out.append(((1 - t) ** 3 * p0 + (3 * t ** 3 - 6 * t ** 2 + 4) * p1
                    + (-3 * t ** 3 + 3 * t ** 2 + 3 * t + 1) * p2 + t ** 3 * p3) / 6)
    Q = np.vstack([*out, P[-1:]])
    S = np.r_[0.0, np.cumsum(np.hypot(*np.diff(Q, axis=0).T))]
    taper = np.sin(np.pi * S / max(S[-1], 1e-9))
    Pk = np.ascontiguousarray(pa.fr.to_sphere(Q[:, 0], Q[:, 1]) * R_KM)
    amp = min(WARP_PX * pa.rp, 0.1 * S[-1])  # (a short gorge: no more than a gentle bend)
    for ax, k in ((0, 11), (1, 12)):  # (seed: the build's; the courses' warp field)
        Q[:, ax] += amp * taper * np.clip(ZK.fbm(Pk, 2 * pa.rp, 2, 0.5, seed + k) / 0.17, -1.25, 1.25)
    return Q


def _parent_gorge(pa: _Parent, ch: list[int], f: dict, path: np.ndarray) -> np.ndarray:
    """The parent's pixels of a fall's gorge (flat mask): a fine parent's
    floor and walls (within gorge_half_km of its path), else its chain
    between the lip and the foot."""
    m = np.zeros(pa.nx * pa.ny, bool)
    half = f.get("gorge_half_km")
    if f.get("gorge_path") and half:
        r0, r1 = np.divmod(np.asarray(ch), pa.nx)
        pad = int(np.ceil(half / pa.rp)) + 2
        rr, cc = np.mgrid[max(r0.min() - pad, 0):min(r0.max() + pad + 1, pa.ny),
                          max(r1.min() - pad, 0):min(r1.max() + pad + 1, pa.nx)]
        x, y = pa.plane(rr.ravel(), cc.ravel())
        S = np.r_[0.0, np.cumsum(np.hypot(*np.diff(path, axis=0).T))]
        d, s = _path_dist(x, y, path, S)
        sel = (d <= half) & (s > 0.5 * pa.rp)
        m[(rr.ravel() * pa.nx + cc.ravel())[sel]] = True
    else:
        m[np.asarray(ch[1:-1], int)] = True
    return m


def _fill(h: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """h with its masked pixels filled from their neighbours, ring by ring."""
    out, valid = h.copy(), ~mask
    for _ in range(64):
        if valid.all():
            break
        sm = _box3(np.where(valid, out, 0.0))
        n_ = _box3(valid.astype(float))
        new = ~valid & (n_ > 0)
        out[new] = sm[new] / n_[new]
        valid = valid | new
    return out


def _on_loops(rec: np.ndarray, stuck: np.ndarray) -> np.ndarray:
    """The pixels on receiver loops, of the `stuck` ones (on a loop or
    draining into one): Kahn's pruning of those no stuck pixel drains into."""
    on = stuck.copy()
    while True:
        fed = np.zeros(len(rec), bool)
        src = np.flatnonzero(on & (rec >= 0))
        fed[rec[src]] = True
        tail = on & ~fed
        if not tail.any():
            return on
        on &= ~tail


def _box3(a: np.ndarray) -> np.ndarray:
    """Sum over each pixel's 3x3 neighbourhood (zero outside)."""
    p = np.pad(a, 1)
    return sum(p[1 + dr:1 + dr + a.shape[0], 1 + dc:1 + dc + a.shape[1]]
               for dr in (-1, 0, 1) for dc in (-1, 0, 1))


def _talus(hw: np.ndarray, active: np.ndarray, nb: int, res: float) -> np.ndarray:
    """Aprons below faces steeper than 45 degrees: the pixel at a face's
    foot rises a quarter of the way up, the apron spreads at TALUS_DEG."""
    H = hw.reshape(nb, nb).copy()
    A = active.reshape(nb, nb)
    lim = 1000.0 * res  # m: 45 degrees over one pixel
    up = np.full_like(H, -np.inf)
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        up = np.maximum(up, Z._shift(H, dr, dc, -np.inf))
    foot = A & (up - H > lim)
    H = np.where(foot, H + 0.25 * (up - H - lim), H)
    t = 1000.0 * res * np.tan(np.radians(TALUS_DEG))
    for _ in range(3):
        nbm = np.full_like(H, -np.inf)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nbm = np.maximum(nbm, Z._shift(np.where(foot, H, -np.inf), dr, dc, -np.inf))
        grow = A & ~foot & (nbm - t > H)
        H = np.where(grow, nbm - t, H)
        foot |= grow
    return H.ravel()


def _relax(hw: np.ndarray, active: np.ndarray, s_max: np.ndarray, nb: int, res: float, iters: int = 200,
           needles: bool = False) -> np.ndarray:
    """The active pixels lowered until none stands more than s_max (m/km,
    per pixel) above any active neighbour (min-plus, to convergence); with
    needles, only above all its neighbours (held ones too: a needle)."""
    H = hw.reshape(nb, nb).copy()
    A = active.reshape(nb, nb)
    step = s_max.reshape(nb, nb) * res
    for _ in range(iters):
        Ha = np.where(A, H, np.inf)
        new = H.copy() if not needles else np.full_like(H, -np.inf)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr or dc:
                    d_ = step * (1.41421356 if dr and dc else 1.0)
                    if needles:
                        new = np.maximum(new, Z._shift(H, dr, dc, -np.inf) + d_)
                    else:
                        new = np.minimum(new, Z._shift(Ha, dr, dc, np.inf) + d_)
        if needles:
            new = np.minimum(H, new)
        new = np.where(A, new, H)
        if np.abs(new - H).max() < 0.01:
            return new.ravel()
        H = new
    return H.ravel()


# ---------------------------------------------------------------------------
# Save, and the entry point
# ---------------------------------------------------------------------------
def save(z: dict, pmeta: dict, lat: float, lon: float, size_km: float, res_km: float, seed: int) -> Path:
    zid = fine_id(pmeta["id"], lat, lon, size_km, res_km, seed)
    out = S.path_of("zoom", zid)
    out.mkdir(parents=True, exist_ok=True)
    specs, arrays = {}, {}
    for k, v in z["layers"].items():
        units, desc, *enc = Z.LAYER_DOC[k]
        specs[k] = {**(enc[0] if enc else {}), "units": units, "description": desc}
        arrays[k] = S.encode(v, specs[k]) if enc else v
    layout = S.write_layers(out, arrays, specs)
    h = z["layers"]["elevation"].astype(float)
    lo, hi = float(np.floor(h.min())), float(np.ceil(h.max()))
    hi = max(hi, lo + 1)
    write_png(out / "heightmap.png", np.round((h - lo) / (hi - lo) * 65535).astype(np.uint16))
    write_png(out / "preview.png", Z.preview(z))
    for k, img in z["satellite"].items():
        write_png(out / Z.SAT_FILES[k], img)
    write_png(out / "coarse.png", Z.coarse_image(z))
    fr = z["frame"]
    half = z["size_km"] / 2
    corners = {k: [round(v, 5) for v in Z._latlon(fr.to_sphere(np.array([x]), np.array([y]))[0])]
               for k, (x, y) in {"nw": (-half, half), "ne": (half, half), "se": (half, -half),
                                 "sw": (-half, -half)}.items()}
    base = str(pmeta["name"]).split(":")[0]
    meta = {
        "format": "procgen-zoom/2",
        "id": zid,
        "name": f"{base}: {lat:g}, {lon:g} ({z['size_km']:g} km @ {z['res'] * 1000:g} m, in {pmeta['id']})",
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "generated_in_s": z["seconds"],
        "source_world": pmeta["source_world"],
        "parent_zoom": z["parent"],
        "center": {"lat": lat, "lon": lon},
        "size_km": z["size_km"],
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
                  **{f[:-4]: f for f in Z.SAT_FILES.values()}},
        "layers": layout,
        "heightmap": {"bits": 16, "min_m": lo, "max_m": hi,
                      "sea_level_value": int(round((0 - lo) / (hi - lo) * 65535)) if lo < 0 < hi else None,
                      "formula": "elev_m = min_m + value / 65535 * (max_m - min_m)",
                      "metres_per_step": round((hi - lo) / 65535, 4)},
        "legend": S.legends(),
        "params": z["params"],
        "stats": z["stats"],
    }
    S.write_atomic(out / "zoom.json", json.dumps(meta, indent=1))
    Z.update_index()
    return out


def zoom(parent_ref: str, lat: float, lon: float, size_km: float | None = None, res_km: float | None = None,
         seed: int = 1, log=print) -> Path:
    """Builds and saves the fine zoom of zoom `parent_ref` (CLI and API).
    size_km / res_km default to default_size(parent res)."""
    pdir = S.find_zoom(parent_ref)
    pmeta, play = Z.load(pdir, decode=True)
    lon = (lon + 180) % 360 - 180
    ds, dr = default_size(float(pmeta["res_km"]))
    res_km = dr if res_km is None else res_km
    size_km = (ds if res_km == dr else 500 * res_km) if size_km is None else size_km
    try:
        check(pmeta, lat, lon, size_km, res_km)
    except ValueError as e:
        raise SystemExit(str(e)) from None
    world = W.load(Z.find_world(pmeta["source_world"]["id"]))
    z = build((pmeta, play), world, lat, lon, size_km, res_km, seed, log=log)
    with S.lock(S.zooms_dir(), fine_id(pmeta["id"], lat, lon, size_km, res_km, seed)):
        return save(z, pmeta, lat, lon, size_km, res_km, seed)
