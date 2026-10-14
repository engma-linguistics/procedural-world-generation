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
5. Big rivers. Coarse cells with large flow become smooth (Catmull-Rom,
   noise-warped) polylines; a valley with a monotone-downstream floor is
   cut along each, and along them the landscape pass treats discharge as
   at least the coarse river's. Rivers (and smaller streams) entering
   from outside the region bring their coarse discharge in at the edge.
   Coarse lake cells become lakes (outline like the coast; surface at the
   coarse level), which act as outlets.
6. Landscape pass on the raster: a steady-state stream-power landscape.
   Priority flood + steepest-descent D8 routing gives a drainage network
   and discharge Q (precipitation + inflow); walking up from the outlets
   (sea, lakes, region edge), each pixel sits above its receiver by
   slope = C / K * Q^-0.5 (K = surface.ROCKS erodibility): big rivers
   are gentle, small gullies and ridges steep, so valleys nest
   dendritically. C is a smooth field refitted each iteration so every
   ~35 km neighbourhood keeps the target's mean; the network is
   recomputed on the new surface and the whole thing repeated (~15x).
   Summits taper above a soft cap; hillslopes get some creep (channels
   stay sharp); any pits left are filled.

Outputs: zooms/<id>/
  zoom.json      meta: source world, centre, size, resolution, projection,
                 layer layout of layers.bin, legends, heightmap mapping, stats
  layers.bin     raw little-endian arrays (float32 / uint8), (ny, nx), row 0
                 = north; offsets in zoom.json["layers"]. load() reads it.
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

from . import climate
from . import world as W
from . import zoom_kernels as ZK
from .geo import R_KM, latlon, xyz
from .images import write_png
from .climate import BIOMES, KOPPEN, LAPSE
from .surface import ROCK_K, ROCKS

ZOOMS = W.ROOT / "zooms"
SEC_PER_YR = 3.156e7
KM2_M_PER_YR_TO_M3S = 1e6 / SEC_PER_YR  # discharge unit used internally -> m^3/s

# How rugged the sub-cell detail is, by basement rock (surface.ROCKS ids).
RUGGED = {0: 0.35, 1: 0.85, 2: 0.9, 3: 0.45, 4: 1.0, 5: 0.35}
SEA_CLIMATE = 30  # KOPPEN "-"
# landscape pass: discharge exponent of the steady-state slope, hillslope
# creep per smoothing step (and number of steps), steepest slope allowed
SPL_M, KD, MAX_SLOPE, SMOOTH_STEPS = 0.5, 0.25, 450.0, 6  # MAX_SLOPE in m/km


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
    p = Path(ref)
    for cand in (p, W.WORLDS / f"{ref}.json", W.WORLDS / ref, W.WORLDS / f"{p.name}.json"):
        if cand.is_file():
            return cand
    raise SystemExit(f"no world {ref!r} (see: uv run python -m planet list)")


def _octaves(wavelength, finest):
    """Octaves (halving the wavelength each time) until `finest` km."""
    return int(np.clip(np.ceil(np.log2(wavelength / finest)) + 1, 1, 12))


def _catmull_rom(p0, p1, p2, p3, n):
    """n+1 points from p1 to p2 (uniform Catmull-Rom)."""
    t = np.linspace(0, 1, n + 1)[:, None]
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


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

    # --- coastline -------------------------------------------------------
    lam = 0.9 * sp
    cw = ZK.fbm(Pk, lam, 4, 0.5, S + 7) / 0.17 * 0.12 * sp  # domain warp: bays, headlands
    Pc = np.ascontiguousarray(Pk + cw[:, None] * np.array([0.57, -0.41, 0.71]))
    coast_n = ZK.fbm(Pc, lam, _octaves(lam, 2 * res), 0.62, S + 1) / 0.15
    ind_n = ind + 0.22 * coast_n
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
    amp_land = rug * (0.36 * np.maximum(base, 0) + 0.3 * np.nan_to_num(rel) + 25) + 12
    amp_sea = 5 + 0.08 * np.abs(base)
    taper = np.where(land, smoothstep(0.0, 0.35, ind_n), smoothstep(0.0, 0.25, -ind_n))
    h = base + taper * np.where(land, amp_land, amp_sea) * detail

    def clamp(hh):
        return np.where(land, 0.5 + softplus(hh - 0.5, 15.0), -0.5 - softplus(-0.5 - hh, 15.0))

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

    corr_taper = np.where(land, smoothstep(0.0, 0.3, ind_n), smoothstep(0.0, 0.3, -ind_n))
    for _ in range(2):
        m, cnt = cell_means(h)
        ok = cnt > 0.25 * full_px
        resid = np.where(ok, e_c - m, 0.0)
        corr, _ = ZK.gauss_interp(px, py, cx, cy, resid[:, None], ok[:, None].astype(float), 0.5 * sp)
        h = clamp(h + corr_taper * np.nan_to_num(corr[:, 0]))
    log(f"  coast + detail + mean correction [{time.time() - t0:.1f}s]")

    # --- coarse rivers -> valleys + inflow --------------------------------
    flow, down = L["flow"].astype(float), L["downstream"].astype(int)
    lake_c = L.get("lake", np.zeros(g.n)).astype(bool)
    in_sel = np.zeros(g.n, bool)
    in_sel[sel] = True
    riv = in_sel & (elev > 0) & (flow >= river_min_flow) & (down >= 0)
    riv_ids = np.flatnonzero(riv)
    inflow = np.zeros(npx)
    T = np.full(npx, np.inf)
    riv_q = np.zeros(npx)  # coarse discharge along the coarse river courses
    n_rivers_in = 0
    river_segs = []
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
        ax, ay, bx, by, za, zb, fw, wall, reach, sq = ([] for _ in range(10))
        half = size_km / 2 - 4 * res
        for pts, z1, z2, q, rcell, i in segs:
            m = len(pts)
            pw = allp[k:k + m]
            k += m
            zz = np.linspace(z1, z2, m)
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
                n_rivers_in += 1
        arr = lambda v: np.ascontiguousarray(v, dtype=float)
        T, D, I = ZK.carve_segments(nx, ny, xs[0], ys[0], res, arr(ax), arr(ay), arr(bx), arr(by),
                                    arr(za), arr(zb), arr(fw), arr(wall), arr(reach))
        on = (I >= 0) & (D < np.maximum(arr(fw)[np.maximum(I, 0)], 0.75 * res))
        riv_q = np.where(on, arr(sq)[np.maximum(I, 0)], 0.0)
        cut = land & np.isfinite(T)
        h = np.where(cut, smin(h, np.where(np.isfinite(T), T, 1e9), 40.0), h)
        h = clamp(h)
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
    # lake/no-lake indicator plus fractal noise; surface at the coarse lake
    # elevation; bowl-shaped bed. Lakes are outlets for the landscape pass,
    # so the land around them drains in and stays above the water.
    min_px = max(3, int(np.ceil(30.0 / res**2)))  # ~30 km^2
    lake = np.zeros(npx, bool)
    lake_level = np.zeros(npx)
    lk_c = lake_c[sel] & land_c
    if lk_c.any():
        lind, _ = ZK.gauss_interp(px, py, cx, cy, np.column_stack([np.where(lk_c, 1.0, -1.0), e_c]),
                                  np.column_stack([land_c, lk_c]).astype(float), 0.42 * sp)
        lake_n = ZK.fbm(Pc, 0.5 * sp, _octaves(0.5 * sp, 2 * res), 0.6, S + 8) / 0.15
        cand = land & ~edge & ~glacier & (np.nan_to_num(lind[:, 0], nan=-1.0) + 0.2 * lake_n > 0.1)
        lab, sizes = ZK.label_components(cand, nx, ny)
        for k in np.flatnonzero(sizes >= min_px):
            comp = lab == k
            level = float(np.nanmean(lind[comp, 1])) + 3.0
            lake |= comp
            lake_level = np.where(comp, level, lake_level)
        if lake.any():
            l2 = lake.reshape(ny, nx)
            shore_d = _box_mean(l2.astype(float), np.ones((ny, nx)), max(1, int(round(8 / res)))).ravel()
            h = np.where(lake, np.maximum(lake_level - 2.0 - 40.0 * shore_d**2, 0.6), h)
            outlet = outlet | lake
    rain = precip / 1000.0 * res * res  # km^2 m/yr per pixel
    srcq = rain + inflow
    Kr = ROCK_K[np.minimum(surf_f, len(ROCK_K) - 1)]
    jitter = np.random.default_rng(seed).random(npx)
    active = land & ~edge & ~lake
    idx = np.arange(npx)
    # Steady-state stream power: slope = C / K * Q^-m. C is a smooth field
    # fitted so every ~35 km neighbourhood keeps the mean of the target
    # surface; a little noise in C varies the relief from valley to valley.
    target = h.copy()
    rad = max(1, int(round(0.3 * sp / res)))
    wmask = land.reshape(ny, nx).astype(float)
    tmean = _box_mean(np.maximum(target, 0).reshape(ny, nx) * wmask, wmask, rad).ravel()
    var = np.exp(0.35 * ZK.fbm(Pk, 0.25 * sp, 3, 0.5, S + 6) / 0.17)
    C = np.full(npx, 30.0)
    # summits: slopes taper above `soft`, nothing above `cap`
    soft = tmean + 0.7 * amp_land
    cap = tmean + np.minimum(1.8 * amp_land, 3000.0)
    rough = np.where(glacier, 0.5, 1.0) * var / Kr
    for it in range(iterations):
        filled, rec, order = ZK.flood_d8(h, outlet, nx, ny, 1e-3, jitter)
        Q = ZK.accumulate(rec, order, srcq)
        diag = (rec >= 0) & ((rec % nx) != (idx % nx)) & ((rec // nx) != (idx // nx))
        dist = res * np.where(diag, 1.4142, 1.0)
        # coarse river courses count as carrying at least their coarse discharge
        slope = np.minimum(C * rough * np.maximum(np.maximum(Q, riv_q), 1e-3) ** -SPL_M, MAX_SLOPE)
        h = target.copy()
        ZK.integrate(h, rec, order, slope, dist, ~active, 0.5, soft, 0.5 * amp_land + 1, cap)
        hmean = _box_mean(np.maximum(h, 0).reshape(ny, nx) * wmask, wmask, rad).ravel()
        C = C * np.clip(tmean / np.maximum(hmean, 1.0), 0.5, 2.0) ** 0.8
    # soften D8 streaks and knife-edge ridges on hillslopes; keep channels sharp
    chan = np.clip(np.log10(np.maximum(Q, 1e-3) / (50 * res * res)) / 2, 0, 1)
    kd = np.where(active, np.where(glacier, 0.4, KD * (1 - 0.8 * chan)), 0.0)
    for _ in range(SMOOTH_STEPS):
        h = ZK.diffuse(h, kd, active, nx, ny)
    log(f"  landscape pass: {iterations} iterations [{time.time() - t0:.1f}s]")

    # --- final drainage --------------------------------------------------
    filled, rec, order = ZK.flood_d8(h, outlet, nx, ny, 1e-3, jitter)
    h = np.where(active, np.maximum(h, filled), h)  # no pits left: everything drains
    filled, rec, order = ZK.flood_d8(h, outlet, nx, ny, 1e-3, jitter)
    Q = ZK.accumulate(rec, order, srcq)
    area = ZK.accumulate(rec, order, np.full(npx, res * res))
    lake_depth = np.where(lake, np.maximum(lake_level - h, 0.5), 0.0)
    discharge = np.where(land, Q * KM2_M_PER_YR_TO_M3S, 0.0)
    area = np.where(land, area, 0.0)

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
    water = np.where(sea, 1, np.where(lake, 2, 0)).astype(np.uint8)

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
            "stats": stats, "coarse": coarse, "seconds": round(time.time() - t0, 1),
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
    "discharge": ("m^3/s", "mean river discharge (precipitation routed downhill, plus inflow at the edges)"),
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
    out = ZOOMS / zid
    out.mkdir(parents=True, exist_ok=True)
    layout, offset = {}, 0
    with open(out / "layers.bin", "wb") as fh:
        for k, v in z["layers"].items():
            arr = np.ascontiguousarray(v.astype(v.dtype.newbyteorder("<")))
            pad = (-offset) % 8
            fh.write(b"\0" * pad)
            offset += pad
            layout[k] = {"dtype": np.dtype(v.dtype).name, "offset": offset, "shape": list(arr.shape),
                         "units": LAYER_DOC[k][0], "description": LAYER_DOC[k][1]}
            fh.write(arr.tobytes())
            offset += arr.nbytes
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
        "format": "procgen-zoom/1",
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
        "files": {"layers": "layers.bin", "heightmap": "heightmap.png", "preview": "preview.png",
                  "coarse": "coarse.png"},
        "layers": layout,
        "heightmap": {"bits": 16, "min_m": lo, "max_m": hi,
                      "sea_level_value": int(round((0 - lo) / (hi - lo) * 65535)) if lo < 0 < hi else None,
                      "formula": "elev_m = min_m + value / 65535 * (max_m - min_m)",
                      "metres_per_step": round((hi - lo) / 65535, 4)},
        "legend": {
            "rocks": [{"id": r[0], "key": r[1], "name": r[2], "color": r[4]} for r in ROCKS],
            "koppen": [{"id": k[0], "code": k[1], "name": k[2], "color": k[3]} for k in KOPPEN],
            "biomes": [{"id": b[0], "name": b[1], "color": b[3]} for b in BIOMES],
        },
        "params": z["params"],
        "stats": z["stats"],
    }
    (out / "zoom.json").write_text(json.dumps(meta, indent=1))
    update_index()
    return out


def load(ref: str | Path) -> tuple[dict, dict]:
    """(meta, {layer: (ny, nx) array}) for zooms/<id> (or a path to it)."""
    p = Path(ref)
    d = p if (p / "zoom.json").exists() else ZOOMS / str(ref)
    meta = json.loads((d / "zoom.json").read_text())
    raw = (d / "layers.bin").read_bytes()
    layers = {}
    for k, spec in meta["layers"].items():
        dt = np.dtype(spec["dtype"]).newbyteorder("<")
        layers[k] = np.frombuffer(raw, dt, int(np.prod(spec["shape"])), spec["offset"]).reshape(spec["shape"])
    return meta, layers


def update_index():
    ZOOMS.mkdir(exist_ok=True)
    items = []
    for p in sorted(ZOOMS.glob("*/zoom.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            m = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        items.append({"id": m["id"], "name": m["name"], "created": m["created"], "world": m["source_world"]["id"],
                      "center": m["center"], "size_km": m["size_km"], "res_km": m["res_km"]})
    (ZOOMS / "index.json").write_text(json.dumps(items, indent=1))


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
