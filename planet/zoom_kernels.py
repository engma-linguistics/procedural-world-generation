"""Numba kernels for planet.zoom: noise, scattered-data interpolation and a
raster landscape pass (priority flood, D8 flow, stream power, hillslope creep).

Rasters are flattened row-major: pixel (row r, column c) is r * nx + c,
row 0 at the north edge.
"""

from __future__ import annotations

import numpy as np
from numba import njit, prange

from .kernels import _heap_pop, _heap_push

# ---------------------------------------------------------------------------
# 3D gradient noise with a hashed lattice (no 256-period repeats, so it can be
# sampled in kilometres anywhere on the planet without visible tiling).
# ---------------------------------------------------------------------------
_GRAD = np.array([[1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0],
                  [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],
                  [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1],
                  [1, 1, 0], [-1, 1, 0], [0, -1, 1], [0, -1, -1]], dtype=np.float64)


@njit(cache=True, inline="always")
def _hash(ix, iy, iz, seed):
    h = (np.uint64(ix) * np.uint64(0x9E3779B185EBCA87)) ^ (np.uint64(iy) * np.uint64(0xC2B2AE3D27D4EB4F)) \
        ^ (np.uint64(iz) * np.uint64(0x165667B19E3779F9)) ^ np.uint64(seed)
    h ^= h >> np.uint64(31)
    h *= np.uint64(0xBF58476D1CE4E5B9)
    h ^= h >> np.uint64(29)
    return h


@njit(cache=True, inline="always")
def _gdot(ix, iy, iz, seed, fx, fy, fz):
    k = _hash(ix, iy, iz, seed) & np.uint64(15)
    return _GRAD[k, 0] * fx + _GRAD[k, 1] * fy + _GRAD[k, 2] * fz


@njit(cache=True, inline="always")
def _fade(t):
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


@njit(cache=True)
def noise3(x, y, z, seed):
    """Improved-Perlin gradient noise, roughly in [-1, 1]."""
    x0, y0, z0 = np.floor(x), np.floor(y), np.floor(z)
    ix, iy, iz = np.int64(x0), np.int64(y0), np.int64(z0)
    fx, fy, fz = x - x0, y - y0, z - z0
    u, v, w = _fade(fx), _fade(fy), _fade(fz)
    a = _gdot(ix, iy, iz, seed, fx, fy, fz)
    b = _gdot(ix + 1, iy, iz, seed, fx - 1, fy, fz)
    c = _gdot(ix, iy + 1, iz, seed, fx, fy - 1, fz)
    d = _gdot(ix + 1, iy + 1, iz, seed, fx - 1, fy - 1, fz)
    e = _gdot(ix, iy, iz + 1, seed, fx, fy, fz - 1)
    f = _gdot(ix + 1, iy, iz + 1, seed, fx - 1, fy, fz - 1)
    g = _gdot(ix, iy + 1, iz + 1, seed, fx, fy - 1, fz - 1)
    h = _gdot(ix + 1, iy + 1, iz + 1, seed, fx - 1, fy - 1, fz - 1)
    x1 = a + u * (b - a)
    x2 = c + u * (d - c)
    x3 = e + u * (f - e)
    x4 = g + u * (h - g)
    y1 = x1 + v * (x2 - x1)
    y2 = x3 + v * (x4 - x3)
    return (y1 + w * (y2 - y1)) * 1.1


@njit(cache=True, parallel=True)
def fbm(pts, wavelength, octaves, gain, seed):
    """Fractal sum over points pts (N, 3) given in km. Largest wavelength
    `wavelength` km, halving each octave; normalised to roughly [-1, 1]."""
    n = pts.shape[0]
    out = np.empty(n)
    norm = 0.0
    a = 1.0
    for o in range(octaves):
        norm += a
        a *= gain
    for i in prange(n):
        s = 0.0
        a = 1.0
        f = 1.0 / wavelength
        for o in range(octaves):
            s += a * noise3(pts[i, 0] * f + 0.37 * o, pts[i, 1] * f - 0.71 * o, pts[i, 2] * f + 0.13 * o,
                            seed + 7919 * o)
            a *= gain
            f *= 2.0
        out[i] = s / norm
    return out


@njit(cache=True, parallel=True)
def ridged(pts, wavelength, octaves, gain, seed):
    """Ridged multifractal (sharp crests, each octave weighted by the one
    above so detail clusters on the ridges). Roughly in [0, 1]."""
    n = pts.shape[0]
    out = np.empty(n)
    for i in prange(n):
        s = 0.0
        norm = 0.0
        a = 1.0
        f = 1.0 / wavelength
        prev = 1.0
        for o in range(octaves):
            r = 1.0 - abs(noise3(pts[i, 0] * f - 0.53 * o, pts[i, 1] * f + 0.29 * o, pts[i, 2] * f + 0.61 * o,
                                 seed + 104729 * o))
            r = r * r
            wgt = min(max(prev * 1.6, 0.25), 1.0)
            s += a * r * wgt
            norm += a
            prev = r
            a *= gain
            f *= 2.0
        out[i] = s / norm
    return out


# ---------------------------------------------------------------------------
# Scattered coarse cells -> fine pixels
# ---------------------------------------------------------------------------
@njit(cache=True, parallel=True)
def gauss_interp(px, py, cx, cy, vals, wts, sigma):
    """Normalised Gaussian-kernel average of the coarse values around each
    point. vals (nc, nf); wts (nc, nf) per-value weights (0 = ignore that
    cell for that field). Returns (out (np, nf), weight sum (np, nf));
    out is NaN where no cell contributes."""
    n = px.shape[0]
    nc, nf = vals.shape
    out = np.empty((n, nf))
    den = np.zeros((n, nf))
    cut2 = (3.5 * sigma) ** 2
    inv = 1.0 / (2.0 * sigma * sigma)
    for p in prange(n):
        num = np.zeros(nf)
        dd = np.zeros(nf)
        for c in range(nc):
            dx = px[p] - cx[c]
            dy = py[p] - cy[c]
            d2 = dx * dx + dy * dy
            if d2 > cut2:
                continue
            w = np.exp(-d2 * inv)
            for f in range(nf):
                ww = w * wts[c, f]
                num[f] += ww * vals[c, f]
                dd[f] += ww
        for f in range(nf):
            den[p, f] = dd[f]
            out[p, f] = num[f] / dd[f] if dd[f] > 1e-12 else np.nan
    return out, den


# ---------------------------------------------------------------------------
# River valleys along coarse river polylines
# ---------------------------------------------------------------------------
@njit(cache=True)
def carve_segments(nx, ny, x0, y0, res, ax, ay, bx, by, za, zb, floor_w, wall, reach):
    """Lowest 'valley surface' over all segments: z along the segment, flat
    for floor_w km either side, rising at `wall` m/km beyond. Returns
    (T, nearest-segment distance, nearest segment index or -1) per pixel;
    T = +inf away from rivers.
    x0, y0: centre of pixel (0, 0); x east, y north (rows go south)."""
    T = np.full(nx * ny, np.inf)
    D = np.full(nx * ny, np.inf)
    I = np.full(nx * ny, -1, np.int64)
    for s in range(ax.shape[0]):
        r = reach[s]
        xmin, xmax = min(ax[s], bx[s]) - r, max(ax[s], bx[s]) + r
        ymin, ymax = min(ay[s], by[s]) - r, max(ay[s], by[s]) + r
        c0 = max(int(np.floor((xmin - x0) / res)), 0)
        c1 = min(int(np.ceil((xmax - x0) / res)), nx - 1)
        r0 = max(int(np.floor((y0 - ymax) / res)), 0)
        r1 = min(int(np.ceil((y0 - ymin) / res)), ny - 1)
        if c0 > c1 or r0 > r1:
            continue
        vx, vy = bx[s] - ax[s], by[s] - ay[s]
        L2 = vx * vx + vy * vy
        for row in range(r0, r1 + 1):
            y = y0 - row * res
            for col in range(c0, c1 + 1):
                x = x0 + col * res
                t = 0.0
                if L2 > 0:
                    t = min(max(((x - ax[s]) * vx + (y - ay[s]) * vy) / L2, 0.0), 1.0)
                qx, qy = ax[s] + t * vx - x, ay[s] + t * vy - y
                d = np.sqrt(qx * qx + qy * qy)
                if d > r:
                    continue
                z = za[s] + t * (zb[s] - za[s])
                v = z + max(d - floor_w[s], 0.0) * wall[s]
                k = row * nx + col
                if v < T[k]:
                    T[k] = v
                if d < D[k]:
                    D[k] = d
                    I[k] = s
    return T, D, I


# ---------------------------------------------------------------------------
# Raster landscape pass
# ---------------------------------------------------------------------------
_DR = np.array([-1, -1, -1, 0, 0, 1, 1, 1])
_DC = np.array([-1, 0, 1, -1, 1, -1, 0, 1])
_DL = np.array([1.4142135623730951, 1.0, 1.4142135623730951, 1.0, 1.0,
                1.4142135623730951, 1.0, 1.4142135623730951])


@njit(cache=True)
def flood_d8(h, outlet, nx, ny, eps, jitter):
    """Priority flood (Barnes 2014) from the outlet pixels, then steepest-
    descent receivers on the filled surface (8 neighbours, diagonal
    distances). Inside filled depressions, the flood's own parent is used.
    Returns (filled, receiver (-1 at outlets), order outlet -> headwater).
    jitter: tiny per-pixel random lift for the flood keys, breaks ties on
    flats so drainage there isn't a set of parallel lines."""
    n = nx * ny
    filled = h.copy()
    rec = np.full(n, -1, np.int64)
    closed = np.zeros(n, np.bool_)
    hk = np.empty(n)
    hv = np.empty(n, np.int64)
    size = 0
    for i in range(n):
        if outlet[i]:
            closed[i] = True
            size = _heap_push(hk, hv, size, filled[i], i)
    order = np.empty(n, np.int64)
    k = 0
    while size > 0:
        z, i, size = _heap_pop(hk, hv, size)
        order[k] = i
        k += 1
        r, c = i // nx, i % nx
        for m in range(8):
            rr, cc = r + _DR[m], c + _DC[m]
            if rr < 0 or rr >= ny or cc < 0 or cc >= nx:
                continue
            j = rr * nx + cc
            if closed[j]:
                continue
            closed[j] = True
            lim = filled[i] + eps * (1.0 + jitter[j])
            if filled[j] < lim:
                filled[j] = lim
            rec[j] = i
            size = _heap_push(hk, hv, size, filled[j], j)
    # steepest descent where the ground actually slopes
    for i in range(n):
        if outlet[i] or rec[i] < 0:
            continue
        if filled[i] - h[i] > 1e-6:
            continue  # in a depression: keep the flood path to the spill point
        r, c = i // nx, i % nx
        best = rec[i]
        rb, cb = best // nx, best % nx
        db = 1.4142135623730951 if (rb != r and cb != c) else 1.0
        sb = (filled[i] - filled[best]) / db
        for m in range(8):
            rr, cc = r + _DR[m], c + _DC[m]
            if rr < 0 or rr >= ny or cc < 0 or cc >= nx:
                continue
            j = rr * nx + cc
            s = (filled[i] - filled[j]) / _DL[m]
            if s > sb:
                sb = s
                best = j
        rec[i] = best
    return filled, rec, order[:k]


@njit(cache=True)
def accumulate(rec, order, src):
    q = src.copy()
    for t in range(order.shape[0] - 1, -1, -1):
        i = order[t]
        d = rec[i]
        if d >= 0:
            q[d] += q[i]
    return q


@njit(cache=True)
def integrate(h, rec, order, s, dist, fixed, floor, soft, scale, cap):
    """Steady-state profile: walking outlet -> headwater, each pixel sits
    s_i (m per km) x dist_i (km) above its receiver (or above floor_i, if
    that is higher: lake rims, gorge rims, the floors of big rivers, with
    their falls). Above `soft` the slope tapers off (rounded summits rather
    than absurd peaks) and nothing goes above `cap`; always a little above
    the receiver so drainage stays intact.
    Pixels with fixed=True (outlets, region edge) keep their height."""
    for t in range(order.shape[0]):
        i = order[t]
        d = rec[i]
        if fixed[i] or d < 0:
            continue
        base = max(h[d], floor[i])
        over = max(base - soft[i], 0.0) / scale[i]
        inc = s[i] * dist[i] / ((1.0 + over) * (1.0 + over))
        h[i] = max(min(base + inc, cap[i]), base + 0.01 * dist[i])


@njit(cache=True)
def settle(h, rec, order, fixed, dist, max_rise):
    """Walking outlet -> headwater, lift each pixel that lies below its
    receiver (+ 1 cm/km) to just above it, if that's at most max_rise m
    (small uphill steps along courses laid out on an earlier surface)."""
    for t in range(order.shape[0]):
        i = order[t]
        d = rec[i]
        if fixed[i] or d < 0:
            continue
        need = h[d] + 0.01 * dist[i]
        if h[i] < need and need - h[i] <= max_rise:
            h[i] = need


@njit(cache=True, parallel=True)
def diffuse(h, kd, active, nx, ny):
    """One explicit step of hillslope creep (8-neighbour Laplacian),
    kd = fraction of the way to the neighbour mean, per pixel."""
    out = h.copy()
    for r in prange(1, ny - 1):
        for c in range(1, nx - 1):
            i = r * nx + c
            if not active[i] or kd[i] <= 0:
                continue
            s = 0.0
            for m in range(8):
                s += h[(r + _DR[m]) * nx + c + _DC[m]] * (0.5 if _DL[m] > 1.1 else 1.0)
            out[i] = h[i] + kd[i] * (s / 6.0 - h[i])
    return out


@njit(cache=True)
def label_components(mask, nx, ny):
    """8-connected components of mask. Returns (label per pixel, -1 off
    mask; size per label)."""
    n = nx * ny
    lab = np.full(n, -1, np.int64)
    sizes = np.zeros(n, np.int64)
    stack = np.empty(n, np.int64)
    nl = 0
    for s in range(n):
        if not mask[s] or lab[s] >= 0:
            continue
        lab[s] = nl
        top = 0
        stack[top] = s
        top += 1
        cnt = 0
        while top > 0:
            top -= 1
            i = stack[top]
            cnt += 1
            r, c = i // nx, i % nx
            for m in range(8):
                rr, cc = r + _DR[m], c + _DC[m]
                if rr < 0 or rr >= ny or cc < 0 or cc >= nx:
                    continue
                j = rr * nx + cc
                if mask[j] and lab[j] < 0:
                    lab[j] = nl
                    stack[top] = j
                    top += 1
        sizes[nl] = cnt
        nl += 1
    return lab, sizes[:nl]


@njit(cache=True)
def receiver_order(rec):
    """Order outlet -> headwater of a receiver forest (rec -1 at the roots),
    breadth-first from the roots. Shorter than rec if rec has a cycle."""
    n = rec.shape[0]
    off = np.zeros(n + 1, np.int64)
    for i in range(n):
        if rec[i] >= 0:
            off[rec[i] + 1] += 1
    for i in range(n):
        off[i + 1] += off[i]
    kids = np.empty(off[n], np.int64)
    pos = off[:n].copy()
    for i in range(n):
        d = rec[i]
        if d >= 0:
            kids[pos[d]] = i
            pos[d] += 1
    order = np.empty(n, np.int64)
    k = 0
    for i in range(n):
        if rec[i] < 0:
            order[k] = i
            k += 1
    head = 0
    while head < k:
        i = order[head]
        head += 1
        for e in range(off[i], off[i + 1]):
            order[k] = kids[e]
            k += 1
    return order[:k]


@njit(cache=True)
def chain(rec, start):
    """Pixels from start down its receivers to the outlet (inclusive)."""
    out = np.empty(rec.shape[0], np.int64)
    k = 0
    i = start
    while i >= 0 and k < rec.shape[0]:
        out[k] = i
        k += 1
        i = rec[i]
    return out[:k]


@njit(cache=True)
def add_chain(q, rec, start, amount):
    """Add `amount` to q along the receiver chain from start (water put in
    at one pixel and carried downstream: lake outlets, distributaries)."""
    i = start
    k = 0
    while i >= 0 and k < q.shape[0]:
        q[i] += amount
        i = rec[i]
        k += 1


@njit(cache=True)
def inside_distance(mask, nx, ny, edge_outside=True):
    """Chamfer distance (pixels; 1 and sqrt 2 steps) from each mask pixel to
    the nearest pixel outside the mask (or outside the raster, if
    edge_outside); 0 off mask."""
    big = 1e9
    d = np.where(mask, big, 0.0)
    for r in range(ny):
        for c in range(nx):
            i = r * nx + c
            if d[i] == 0.0:
                continue
            v = d[i]
            for dr, dc, w in ((-1, -1, 1.4142135623730951), (-1, 0, 1.0), (-1, 1, 1.4142135623730951),
                              (0, -1, 1.0)):
                rr, cc = r + dr, c + dc
                if rr < 0 or cc < 0 or cc >= nx:
                    if not edge_outside:
                        continue
                    u = 0.0
                else:
                    u = d[rr * nx + cc]
                v = min(v, u + w)
            d[i] = v
    for r in range(ny - 1, -1, -1):
        for c in range(nx - 1, -1, -1):
            i = r * nx + c
            if d[i] == 0.0:
                continue
            v = d[i]
            for dr, dc, w in ((1, 1, 1.4142135623730951), (1, 0, 1.0), (1, -1, 1.4142135623730951),
                              (0, 1, 1.0)):
                rr, cc = r + dr, c + dc
                if rr >= ny or cc < 0 or cc >= nx:
                    if not edge_outside:
                        continue
                    u = 0.0
                else:
                    u = d[rr * nx + cc]
                v = min(v, u + w)
            d[i] = v
    return d
