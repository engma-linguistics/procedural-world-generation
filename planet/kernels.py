"""Numba-compiled inner loops.

Everything here works on flat arrays. Neighbour lists use the CSR layout
common in sparse-matrix code: the neighbours of cell i are
nbr_idx[nbr_off[i]:nbr_off[i + 1]].

First call of each function compiles it (~1 s each). cache=True stores the
compiled code in __pycache__, so later runs start instantly.
"""

from __future__ import annotations

import numpy as np
from numba import njit, prange

# ---------------------------------------------------------------------------
# Grid construction
# ---------------------------------------------------------------------------


@njit(cache=True)
def order_cells(verts, faces, corners, vf_off, vf_idx):
    """For each vertex, sort its surrounding triangles counter-clockwise and
    derive the neighbour between each consecutive pair. Returns CSR arrays
    (off, corner_idx, nbr_idx) sharing the same offsets."""
    n = verts.shape[0]
    total = vf_off[n]
    out_corner = np.empty(total, np.int64)
    out_nbr = np.empty(total, np.int64)
    ang = np.empty(6)
    fs = np.empty(6, np.int64)
    for v in range(n):
        c = verts[v]
        # reference tangent: cross(c, z), or cross(c, x) near the poles
        r0, r1, r2 = c[1], -c[0], 0.0
        nr = np.sqrt(r0 * r0 + r1 * r1)
        if nr < 1e-6:
            r0, r1, r2 = 0.0, c[2], -c[1]
            nr = np.sqrt(r1 * r1 + r2 * r2)
        r0 /= nr
        r1 /= nr
        r2 /= nr
        s0 = c[1] * r2 - c[2] * r1
        s1 = c[2] * r0 - c[0] * r2
        s2 = c[0] * r1 - c[1] * r0
        k = vf_off[v + 1] - vf_off[v]
        for j in range(k):
            f = vf_idx[vf_off[v] + j]
            d0 = corners[f, 0] - c[0]
            d1 = corners[f, 1] - c[1]
            d2 = corners[f, 2] - c[2]
            ang[j] = np.arctan2(d0 * s0 + d1 * s1 + d2 * s2, d0 * r0 + d1 * r1 + d2 * r2)
            fs[j] = f
        # insertion sort by angle (k <= 6)
        for a in range(1, k):
            x, y = ang[a], fs[a]
            b = a - 1
            while b >= 0 and ang[b] > x:
                ang[b + 1] = ang[b]
                fs[b + 1] = fs[b]
                b -= 1
            ang[b + 1] = x
            fs[b + 1] = y
        for j in range(k):
            f1, f2 = fs[j], fs[(j + 1) % k]
            out_corner[vf_off[v] + j] = f1
            nb = -1
            for p in range(3):
                u = faces[f1, p]
                if u == v:
                    continue
                for q in range(3):
                    if faces[f2, q] == u:
                        nb = u
            out_nbr[vf_off[v] + j] = nb
    return out_corner, out_nbr


# ---------------------------------------------------------------------------
# Point location: which cell is nearest to an arbitrary point on the sphere?
# ---------------------------------------------------------------------------


@njit(cache=True)
def walk_nearest(q, start, centers, nbr_off, nbr_idx):
    """Greedy walk: hop to whichever neighbour is closer to q until none is.
    On a near-Delaunay mesh like the icosphere this finds the nearest cell."""
    cur = start
    best = q[0] * centers[cur, 0] + q[1] * centers[cur, 1] + q[2] * centers[cur, 2]
    while True:
        nxt = -1
        for e in range(nbr_off[cur], nbr_off[cur + 1]):
            j = nbr_idx[e]
            d = q[0] * centers[j, 0] + q[1] * centers[j, 1] + q[2] * centers[j, 2]
            if d > best:
                best = d
                nxt = j
        if nxt < 0:
            return cur
        cur = nxt


@njit(cache=True)
def build_raster(centers, nbr_off, nbr_idx, w, h):
    """Coarse lat/lon raster of nearest-cell ids: a starting guess for walks."""
    out = np.empty((h, w), np.int64)
    q = np.empty(3)
    cur = 0
    for y in range(h):
        lat = np.pi / 2 - (y + 0.5) * np.pi / h
        for x in range(w):
            lon = -np.pi + (x + 0.5) * 2 * np.pi / w
            q[0] = np.cos(lat) * np.cos(lon)
            q[1] = np.cos(lat) * np.sin(lon)
            q[2] = np.sin(lat)
            cur = walk_nearest(q, cur, centers, nbr_off, nbr_idx)
            out[y, x] = cur
    return out


@njit(cache=True, parallel=True)
def locate(pts, guess, raster, centers, nbr_off, nbr_idx):
    """Nearest cell for each row of pts. guess[i] >= 0 is used as the walk's
    starting point (fast when points moved only a little); otherwise the
    raster supplies one. Each point's walk is independent, so the parallel
    loop gives exactly the serial result."""
    h, w = raster.shape
    out = np.empty(pts.shape[0], np.int64)
    for i in prange(pts.shape[0]):
        s = guess[i]
        if s < 0:
            lat = np.arcsin(min(1.0, max(-1.0, pts[i, 2])))
            lon = np.arctan2(pts[i, 1], pts[i, 0])
            y = min(h - 1, int((np.pi / 2 - lat) / np.pi * h))
            x = min(w - 1, int((lon + np.pi) / (2 * np.pi) * w))
            s = raster[y, x]
        out[i] = walk_nearest(pts[i], s, centers, nbr_off, nbr_idx)
    return out


# ---------------------------------------------------------------------------
# Hydrology
# ---------------------------------------------------------------------------


@njit(cache=True)
def _heap_push(hk, hv, size, key, val):
    i = size
    hk[i] = key
    hv[i] = val
    while i > 0:
        p = (i - 1) >> 1
        if hk[p] <= hk[i]:
            break
        hk[p], hk[i] = hk[i], hk[p]
        hv[p], hv[i] = hv[i], hv[p]
        i = p
    return size + 1


@njit(cache=True)
def _heap_pop(hk, hv, size):
    key, val = hk[0], hv[0]
    size -= 1
    hk[0] = hk[size]
    hv[0] = hv[size]
    i = 0
    while True:
        l, r, m = 2 * i + 1, 2 * i + 2, i
        if l < size and hk[l] < hk[m]:
            m = l
        if r < size and hk[r] < hk[m]:
            m = r
        if m == i:
            break
        hk[m], hk[i] = hk[i], hk[m]
        hv[m], hv[i] = hv[i], hv[m]
        i = m
    return key, val, size


@njit(cache=True)
def priority_flood(elev, nbr_off, nbr_idx, eps):
    """Barnes et al. 2014 priority-flood + epsilon. Returns (filled,
    downstream, order); order runs outlet -> headwater."""
    return priority_flood_to(elev, elev <= 0, nbr_off, nbr_idx, eps)


@njit(cache=True)
def priority_flood_to(elev, outlet, nbr_off, nbr_idx, eps):
    """Priority-flood toward the cells in `outlet` (the sea, plus any
    lakes that end rivers): every other cell drains to one of them, pits
    filled. Returns (filled, downstream, order); order runs outlet -> headwater."""
    n = elev.shape[0]
    filled = elev.copy()
    down = np.full(n, -1, np.int64)
    closed = np.zeros(n, np.bool_)
    hk = np.empty(n)
    hv = np.empty(n, np.int64)
    size = 0
    any_ocean = False
    for i in range(n):
        if outlet[i]:
            closed[i] = True
            size = _heap_push(hk, hv, size, filled[i], i)
            any_ocean = True
    if not any_ocean:
        i = np.argmin(elev)
        closed[i] = True
        size = _heap_push(hk, hv, size, filled[i], i)
    order = np.empty(n, np.int64)
    k = 0
    while size > 0:
        z, i, size = _heap_pop(hk, hv, size)
        order[k] = i
        k += 1
        for e in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[e]
            if not closed[j]:
                closed[j] = True
                if filled[j] < z + eps:
                    filled[j] = z + eps
                down[j] = i
                size = _heap_push(hk, hv, size, filled[j], j)
    return filled, down, order[:k]


@njit(cache=True)
def _root(parent, i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


@njit(cache=True)
def _wet_try(r, c, q, ev, loss, wet):
    """Put cell c under root r's lake if r has the water for it: the lake
    takes cells in order of height until its evaporation matches its
    inflow. A cell it could only half fill stays dry (the shore)."""
    need = q[r] - ev[r]
    if need <= 0:
        return False
    if need >= 0.5 * loss[c]:
        wet[c] = True
        ev[r] += loss[c]
        return True
    return False


@njit(cache=True)
def _push_dry(r, c, head, tail, nxt):
    nxt[c] = -1
    if head[r] < 0:
        head[r] = c
    else:
        nxt[tail[r]] = c
    tail[r] = c


@njit(cache=True)
def _merge_dry(a, b, head, tail, nxt, elev):
    """Merge root b's list of dry cells (sorted by height) into root a's."""
    x, y = head[a], head[b]
    h, t = -1, -1
    while x >= 0 or y >= 0:
        if y < 0 or (x >= 0 and elev[x] <= elev[y]):
            c, x = x, nxt[x]
        else:
            c, y = y, nxt[y]
        if h < 0:
            h = c
        else:
            nxt[t] = c
        t = c
    if t >= 0:
        nxt[t] = -1
    head[a], tail[a] = h, t
    head[b], tail[b] = -1, -1


@njit(cache=True)
def lakes(elev, nbr_off, nbr_idx, src, loss):
    """Lakes that evaporate (fill and spill, with evaporation).

    Water runs downhill (steepest descent) into pits. Each pit's basin then
    floods from its lowest cell up, one cell at a time in order of height
    (all basins together, lowest first, like water rising everywhere at
    once). A lake stops rising when the evaporation off its surface (loss
    per wet cell) matches the water flowing in (src summed over its
    catchment): a closed lake. If it reaches the lowest point of its rim
    first, it spills: over the rim into the next basin (which gets the
    surplus and may rise in turn, so basins merge into one lake), or into
    the sea (an open lake).

    elev: m, <= 0 is sea; src: water each land cell sends downhill;
    loss: the extra water a cell loses while under a lake (same units).
    Returns (wet, open, out_z, pit, catch): cell under a lake; the cell's
    basin spills to the sea (its lakes are fresh, through-flowing);
    elevation at which that basin met the sea's drainage; cell is a pit
    (no lower neighbour); water reaching each cell downhill (catchment)."""
    n = elev.shape[0]
    sea = elev <= 0
    if not sea.any():
        sea[np.argmin(elev)] = True
    # steepest descent and catchments
    rcv = np.full(n, -1, np.int64)
    for i in range(n):
        if sea[i]:
            continue
        bz = elev[i]
        for e in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[e]
            if elev[j] < bz:
                bz, rcv[i] = elev[j], j
    asc = np.argsort(elev, kind="mergesort")
    catch = np.where(sea, 0.0, src)
    for t in range(n - 1, -1, -1):
        i = asc[t]
        if not sea[i] and rcv[i] >= 0:
            catch[rcv[i]] += catch[i]
    # flood every basin from below
    parent = np.arange(n)
    q = np.zeros(n)  # water flowing into the basin (root)
    ev = np.zeros(n)  # evaporation from its lake
    tosea = sea.copy()  # root's basin already spills to the sea
    open_ = np.zeros(n, np.bool_)
    out_z = np.zeros(n)
    head = np.full(n, -1, np.int64)
    tail = np.full(n, -1, np.int64)
    nxt = np.full(n, -1, np.int64)
    wet = np.zeros(n, np.bool_)
    done = sea.copy()
    roots = np.empty(16, np.int64)
    for t in range(n):
        i = asc[t]
        if sea[i]:
            continue
        nr = 0
        to_sea = False
        for e in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[e]
            if not done[j]:
                continue
            r = _root(parent, j)
            if tosea[r]:
                to_sea = True
                continue
            seen = False
            for k in range(nr):
                if roots[k] == r:
                    seen = True
            if not seen:
                roots[nr] = r
                nr += 1
        done[i] = True
        if to_sea:  # every basin touching i spills here into the sea's drainage
            for k in range(nr):
                r = roots[k]
                tosea[r] = True
                open_[r] = (head[r] < 0) and q[r] > ev[r]
                out_z[r] = elev[i]
            tosea[i] = True
            out_z[i] = elev[i]
            continue
        if nr == 0:  # a new pit
            q[i] = catch[i]
            if not _wet_try(i, i, q, ev, loss, wet):
                _push_dry(i, i, head, tail, nxt)
            continue
        r0 = roots[0]
        for k in range(1, nr):  # basins meet at i: one lake from here up
            r = roots[k]
            parent[r] = r0
            q[r0] += q[r]
            ev[r0] += ev[r]
            _merge_dry(r0, r, head, tail, nxt, elev)
        parent[i] = r0
        if rcv[i] < 0:  # a flat pit next to the basin
            q[r0] += catch[i]
        # the basin's surplus spreads over its dry low ground first
        while q[r0] > ev[r0] and head[r0] >= 0:
            c = head[r0]
            if not _wet_try(r0, c, q, ev, loss, wet):
                break
            head[r0] = nxt[c]
            if head[r0] < 0:
                tail[r0] = -1
        if head[r0] >= 0 or not _wet_try(r0, i, q, ev, loss, wet):
            _push_dry(r0, i, head, tail, nxt)
    for i in range(n):
        r = _root(parent, i)
        open_[i] = open_[r]
        out_z[i] = out_z[r]
    return wet, open_, out_z, (rcv < 0) & ~sea, catch


@njit(cache=True)
def accumulate_lakes(down, order, src, wet):
    """Flow accumulation where lake cells can lose water (src < 0 under a
    lake: evaporation). A river through a lake leaves it with what's left;
    a lake can't send a negative flow on downstream."""
    flow = src.copy()
    for t in range(order.shape[0] - 1, -1, -1):
        i = order[t]
        if not wet[i] and flow[i] < 0:
            flow[i] = 0.0
        d = down[i]
        if d >= 0:
            flow[d] += flow[i]
    return np.maximum(flow, 0.0)


@njit(cache=True)
def accumulate(down, order, rain):
    flow = rain.copy()
    for t in range(order.shape[0] - 1, -1, -1):
        i = order[t]
        d = down[i]
        if d >= 0:
            flow[d] += flow[i]
    return flow


@njit(cache=True)
def stream_power(h, down, order, f):
    """Implicit stream-power step (Braun & Willett 2013), outlet first."""
    for t in range(order.shape[0]):
        i = order[t]
        d = down[i]
        if d < 0:
            continue
        hd = max(h[d], 0.0)
        if h[i] > hd:
            h[i] = (h[i] + f[i] * hd) / (1 + f[i])


# ---------------------------------------------------------------------------
# Graph helpers
# ---------------------------------------------------------------------------


@njit(cache=True)
def grow_regions(seed, seeds, rates, nbr_off, nbr_idx, n):
    """Randomised flood fill from seed cells; each region grows at its own rate."""
    np.random.seed(seed)
    k = seeds.shape[0]
    label = np.full(n, -1, np.int64)
    # one frontier array per region, stored back to back
    front = np.empty((k, n), np.int64)
    flen = np.zeros(k, np.int64)
    for r in range(k):
        label[seeds[r]] = r
        front[r, 0] = seeds[r]
        flen[r] = 1
    remaining = n - k
    cum = np.empty(k)
    while remaining > 0:
        tot = 0.0
        for r in range(k):
            tot += rates[r] if flen[r] > 0 else 0.0
            cum[r] = tot
        if tot == 0:
            break
        u = np.random.random() * tot
        r = 0
        while cum[r] < u:
            r += 1
        idx = np.random.randint(flen[r])
        cell = front[r, idx]
        nfree = 0
        for e in range(nbr_off[cell], nbr_off[cell + 1]):
            if label[nbr_idx[e]] < 0:
                nfree += 1
        if nfree == 0:
            flen[r] -= 1
            front[r, idx] = front[r, flen[r]]
            continue
        pick = np.random.randint(nfree)
        for e in range(nbr_off[cell], nbr_off[cell + 1]):
            j = nbr_idx[e]
            if label[j] < 0:
                if pick == 0:
                    label[j] = r
                    front[r, flen[r]] = j
                    flen[r] += 1
                    remaining -= 1
                    break
                pick -= 1
    return label


@njit(cache=True)
def components(mask, nbr_off, nbr_idx):
    """Connected regions of a cell mask: (label per cell, -1 outside the
    mask; number of regions). Regions are numbered by their lowest cell id."""
    n = mask.shape[0]
    lab = np.full(n, -1, np.int64)
    q = np.empty(n, np.int64)
    k = 0
    for s in range(n):
        if not mask[s] or lab[s] >= 0:
            continue
        lab[s] = k
        head, tail = 0, 1
        q[0] = s
        while head < tail:
            i = q[head]
            head += 1
            for e in range(nbr_off[i], nbr_off[i + 1]):
                j = nbr_idx[e]
                if mask[j] and lab[j] < 0:
                    lab[j] = k
                    q[tail] = j
                    tail += 1
        k += 1
    return lab, k


@njit(cache=True)
def bfs_within(sources, label, nbr_off, nbr_idx, max_dist):
    """Multi-source BFS that never crosses into a different label.
    Returns (hop distance, originating source cell); -1 where unreached."""
    n = label.shape[0]
    dist = np.full(n, -1, np.int64)
    src = np.full(n, -1, np.int64)
    q = np.empty(n, np.int64)
    head, tail = 0, 0
    for s in sources:
        if dist[s] < 0:
            dist[s] = 0
            src[s] = s
            q[tail] = s
            tail += 1
    while head < tail:
        i = q[head]
        head += 1
        if dist[i] >= max_dist:
            continue
        for e in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[e]
            if dist[j] < 0 and label[j] == label[i]:
                dist[j] = dist[i] + 1
                src[j] = src[i]
                q[tail] = j
                tail += 1
    return dist, src
