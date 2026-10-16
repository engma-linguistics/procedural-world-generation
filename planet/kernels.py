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
    # (sifts a hole up rather than swapping: the same comparisons, so the
    # same heap, and the same pop order for equal keys)
    i = size
    while i > 0:
        p = (i - 1) >> 1
        if hk[p] <= key:
            break
        hk[i] = hk[p]
        hv[i] = hv[p]
        i = p
    hk[i] = key
    hv[i] = val
    return size + 1


@njit(cache=True)
def _heap_pop(hk, hv, size):
    # Floyd's pop: the hole goes down to a leaf along the smaller children
    # (the left one of equals), then the last element back up above every
    # element not smaller than it. That leaves every element where the
    # textbook sift-down (stop at the first children not smaller) leaves it,
    # so the pops come in the same order, equal keys included, with about
    # half the comparisons.
    key, val = hk[0], hv[0]
    size -= 1
    if size == 0:
        return key, val, size
    k, v = hk[size], hv[size]
    hk[size] = np.inf  # (a right child past the end is never the smaller)
    i = 0
    l = 1
    while l < size:
        c = l + (hk[l + 1] < hk[l])
        hk[i] = hk[c]
        hv[i] = hv[c]
        i = c
        l = 2 * i + 1
    while i > 0:
        p = (i - 1) >> 1
        if hk[p] < k:
            break
        hk[i] = hk[p]
        hv[i] = hv[p]
        i = p
    hk[i] = k
    hv[i] = v
    return key, val, size


@njit(cache=True)
def _land_asc(elev, sea):
    """The cells that aren't sea in order of height, ties by index: what
    argsort(elev, kind="mergesort") gives with the sea's cells left out
    (every one of them must be > 0). A stable radix sort on the bits of the
    heights (a positive float's bits sort as the float does), 11 bits a
    pass; ~7x faster than numba's mergesort."""
    idx = np.nonzero(~sea)[0]
    m = idx.shape[0]
    a = idx.copy()
    ka = elev[idx].view(np.uint64)
    b = np.empty_like(a)
    kb = np.empty_like(ka)
    cnt = np.empty(2048, np.int64)
    mask = np.uint64(2047)
    for p in range(6):
        sh = np.uint64(11 * p)
        cnt[:] = 0
        for t in range(m):
            cnt[(ka[t] >> sh) & mask] += 1
        same = False  # (every height has the same digit here: nothing to do)
        for d in range(2048):
            if cnt[d] != 0:
                same = cnt[d] == m
                break
        if same:
            continue
        s = 0
        for d in range(2048):
            c = cnt[d]
            cnt[d] = s
            s += c
        for t in range(m):
            d = (ka[t] >> sh) & mask
            o = cnt[d]
            cnt[d] = o + 1
            b[o] = a[t]
            kb[o] = ka[t]
        a, b = b, a
        ka, kb = kb, ka
    return a


@njit(cache=True)
def priority_flood(elev, nbr_off, nbr_idx, eps):
    """Barnes et al. 2014 priority-flood + epsilon. Returns (filled,
    downstream, order); order runs outlet -> headwater."""
    return priority_flood_to(elev, elev <= 0, nbr_off, nbr_idx, eps)


CELL_BITS = 26  # (a cell index fits in the low bits of a flood's queue tag: up to 67M cells, level 11)


@njit(cache=True)
def _fheap_push(hk, ht, size, key, tag):
    # _heap_push for priority_flood_to: entries (height, tag), tag = push
    # count << CELL_BITS | cell, so equal heights come off first pushed
    # first; a strict order, so the pops don't depend on what else is queued
    i = size
    while i > 0:
        p = (i - 1) >> 1
        if hk[p] < key or (hk[p] == key and ht[p] < tag):
            break
        hk[i] = hk[p]
        ht[i] = ht[p]
        i = p
    hk[i] = key
    ht[i] = tag
    return size + 1


@njit(cache=True)
def _fheap_pop(hk, ht, size):
    # _heap_pop (Floyd's) on (height, tag)
    key, tag = hk[0], ht[0]
    size -= 1
    if size == 0:
        return key, tag, size
    k, t = hk[size], ht[size]
    i = 0
    l = 1
    while l < size:
        c = l
        r = l + 1
        if r < size and (hk[r] < hk[l] or (hk[r] == hk[l] and ht[r] < ht[l])):
            c = r
        hk[i] = hk[c]
        ht[i] = ht[c]
        i = c
        l = 2 * i + 1
    while i > 0:
        p = (i - 1) >> 1
        if hk[p] < k or (hk[p] == k and ht[p] < t):
            break
        hk[i] = hk[p]
        ht[i] = ht[p]
        i = p
    hk[i] = k
    ht[i] = t
    return key, tag, size


@njit(cache=True)
def priority_flood_to(elev, outlet, nbr_off, nbr_idx, eps):
    """Priority-flood toward the cells in `outlet` (the sea, plus any
    lakes that end rivers): every other cell drains to one of them, pits
    filled. Returns (filled, downstream, order); order runs outlet -> headwater.

    Cells come off the queue lowest first, so a coastal cell drains to its
    deepest sea neighbour (the steepest way down), and cells of equal height
    (a lake's surface, a filled pit) first come first (Barnes et al. 2014's
    plain queue for flats): across a flat the water takes the fewest steps
    to where it leaves, ties by cell index. That order is strict, so the
    outlet cells with no other kind of neighbour (the open sea, a closed
    lake's middle), which reach nothing, needn't be queued (PW-344: ~3.6x
    faster at L7): they lead `order`, in index order, with no downstream."""
    n = elev.shape[0]
    filled = elev.copy()
    down = np.full(n, -1, np.int64)
    closed = outlet.copy()
    hk = np.empty(n)
    ht = np.empty(n, np.int64)
    order = np.empty(n, np.int64)
    mask = (1 << CELL_BITS) - 1
    size = 0
    cnt = 0
    k = 0
    for i in range(n):
        if outlet[i]:
            edge = False
            for e in range(nbr_off[i], nbr_off[i + 1]):
                if not outlet[nbr_idx[e]]:
                    edge = True
                    break
            if edge:
                size = _fheap_push(hk, ht, size, filled[i], (cnt << CELL_BITS) | i)
                cnt += 1
            else:
                order[k] = i
                k += 1
    if cnt == 0 and k == 0:
        i = np.argmin(elev)
        closed[i] = True
        size = _fheap_push(hk, ht, size, filled[i], (cnt << CELL_BITS) | i)
        cnt += 1
    while size > 0:
        z, tag, size = _fheap_pop(hk, ht, size)
        i = tag & mask
        order[k] = i
        k += 1
        for e in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[e]
            if not closed[j]:
                closed[j] = True
                if filled[j] < z + eps:
                    filled[j] = z + eps
                down[j] = i
                size = _fheap_push(hk, ht, size, filled[j], (cnt << CELL_BITS) | j)
                cnt += 1
    return filled, down, order[:k]


@njit(cache=True)
def flood_fill(elev, outlet, nbr_off, nbr_idx, eps):
    """priority_flood_to(...)[0] alone: the filled surface, faster. It
    doesn't depend on the order in which cells with the same height are
    taken (each cell ends at max(elev, eps + its lowest neighbour's filled
    height), whichever of them reaches it first), so the outlet cells with
    no other kind of neighbour, which reach nothing, needn't be queued."""
    n = elev.shape[0]
    filled = elev.copy()
    closed = outlet.copy()
    hk = np.empty(n)
    hv = np.empty(n, np.int64)
    size = 0
    any_outlet = False
    for i in range(n):
        if outlet[i]:
            any_outlet = True
            for e in range(nbr_off[i], nbr_off[i + 1]):
                if not outlet[nbr_idx[e]]:
                    size = _heap_push(hk, hv, size, filled[i], i)
                    break
    if not any_outlet:
        i = np.argmin(elev)
        closed[i] = True
        size = _heap_push(hk, hv, size, filled[i], i)
    while size > 0:
        z, i, size = _heap_pop(hk, hv, size)
        for e in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[e]
            if not closed[j]:
                closed[j] = True
                if filled[j] < z + eps:
                    filled[j] = z + eps
                size = _heap_push(hk, hv, size, filled[j], j)
    return filled


@njit(cache=True)
def _root(parent, i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


@njit(cache=True)
def fill_shallow(elev, nbr_off, nbr_idx, min_depth, area, min_slope, eps=0.01):
    """elev with every hollow too shallow to hold water filled to its rim.

    A hollow is too shallow when its floor lies less than
    max(min_depth, min_slope * radius) below its rim, radius = sqrt(area /
    pi) of the hollow at the rim's level: a wide hollow must also fall
    towards its middle at least as steeply as min_slope (m per km), or it is
    a plain that rivers cross. Water rises in all basins at once (cells in
    order of height, as in lakes()). Where basins meet at a saddle, each one
    except the deepest that is too shallow is filled to it (it drains into
    the deepest through channels too small to see); where a basin reaches
    the sea's drainage, it is filled to that point if it is too shallow. So
    a shallow dip in the floor of a deep basin becomes part of the basin's
    floor instead of a pit of its own, and a whole basin that is too shallow
    drains. Filled ground rises by eps per cell away from where it spills,
    so water runs across it (as in priority_flood). elev: m, <= 0 is sea;
    area: km^2 per cell.
    Returns (h, keep): the filled elevation, and the cells of the basins
    left standing."""
    n = elev.shape[0]
    h = elev.copy()
    sea = elev <= 0
    if not sea.any():
        sea[np.argmin(elev)] = True
    asc = _land_asc(elev, sea)
    parent = np.arange(n)
    bottom = elev.copy()  # each basin's lowest point
    size = area.astype(np.float64).copy()  # each basin's area, km^2
    tosea = sea.copy()
    done = sea.copy()
    keep = np.zeros(n, np.bool_)
    head = np.arange(n)  # each basin's cells, as a linked list
    tail = np.arange(n)
    nxt = np.full(n, -1, np.int64)
    roots = np.empty(16, np.int64)
    mark = np.full(n, -1, np.int64)  # cells being filled at step t (and not reached yet)
    queue = np.empty(n, np.int64)
    for t in range(asc.shape[0]):
        i = asc[t]
        z = elev[i]
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
        if nr == 0 and not to_sea:  # a new pit
            continue
        # the deepest basin first: it receives the others
        for k in range(1, nr):
            if bottom[roots[k]] < bottom[roots[0]]:
                roots[0], roots[k] = roots[k], roots[0]
        if to_sea or nr > 1:  # spill point or saddle: shallow basins fill to it
            nq = 0
            for k in range(0 if to_sea else 1, nr):
                r = roots[k]
                if z - bottom[r] < max(min_depth, min_slope * np.sqrt(size[r] / np.pi)):
                    c = head[r]
                    while c >= 0:
                        mark[c] = t
                        c = nxt[c]
            for e in range(nbr_off[i], nbr_off[i + 1]):
                j = nbr_idx[e]
                if mark[j] == t:
                    mark[j] = -1
                    h[j] = z + eps
                    queue[nq] = j
                    nq += 1
            q0 = 0
            while q0 < nq:
                c = queue[q0]
                q0 += 1
                for e in range(nbr_off[c], nbr_off[c + 1]):
                    j = nbr_idx[e]
                    if mark[j] == t:
                        mark[j] = -1
                        h[j] = h[c] + eps
                        queue[nq] = j
                        nq += 1
            if to_sea:
                for k in range(nr):
                    r = roots[k]
                    tosea[r] = True
                    if z - bottom[r] >= max(min_depth, min_slope * np.sqrt(size[r] / np.pi)):
                        c = head[r]
                        while c >= 0:
                            keep[c] = True
                            c = nxt[c]
                tosea[i] = True
                continue
        r0 = roots[0]
        for k in range(1, nr):
            r = roots[k]
            parent[r] = r0
            nxt[tail[r0]] = head[r]
            tail[r0] = tail[r]
            size[r0] += size[r]
        parent[i] = r0
        nxt[tail[r0]] = i
        tail[r0] = i
        size[r0] += size[i]
    return h, keep


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
    Returns (wet, open, out_z, pit, catch, basin): cell under a lake; the
    cell's basin spills to the sea (its lakes are fresh, through-flowing);
    elevation at which that basin met the sea's drainage; cell is a pit
    (no lower neighbour); water reaching each cell downhill (catchment);
    the cell's basin (its root cell)."""
    sea, rcv, asc = lake_order(elev, nbr_off, nbr_idx)
    return lakes_on(elev, nbr_off, nbr_idx, src, loss, sea, rcv, asc)


@njit(cache=True)
def lake_order(elev, nbr_off, nbr_idx):
    """What kernels.lakes needs of elev alone (so its callers can reuse it
    for the same elev with other src, loss): (sea, rcv, asc): the sea's
    cells, each land cell's steepest-descent receiver (-1: a pit), the land
    cells in order of height."""
    n = elev.shape[0]
    sea = elev <= 0
    if not sea.any():
        sea[np.argmin(elev)] = True
    # steepest descent
    rcv = np.full(n, -1, np.int64)
    for i in range(n):
        if sea[i]:
            continue
        bz = elev[i]
        for e in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[e]
            if elev[j] < bz:
                bz, rcv[i] = elev[j], j
    return sea, rcv, _land_asc(elev, sea)


@njit(cache=True)
def lakes_on(elev, nbr_off, nbr_idx, src, loss, sea, rcv, asc):
    """kernels.lakes with lake_order(elev)'s (sea, rcv, asc) given."""
    n = elev.shape[0]
    # catchments
    catch = np.where(sea, 0.0, src)
    for t in range(asc.shape[0] - 1, -1, -1):
        i = asc[t]
        if rcv[i] >= 0:
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
    for t in range(asc.shape[0]):
        i = asc[t]
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
    basin = np.empty(n, np.int64)
    for i in range(n):
        r = _root(parent, i)
        open_[i] = open_[r]
        out_z[i] = out_z[r]
        basin[i] = r
    return wet, open_, out_z, (rcv < 0) & ~sea, catch, basin


@njit(cache=True)
def closed_excess(sink, basin, wet, down, flow, src, loss, bed):
    """Water the closed basins get from their rivers beyond what their
    lakes evaporate, where that is more than one more cell of lake would:
    it belongs to the basin (put on its lowest sink cell). A basin is
    kernels.lakes' (basin: root per cell): its rivers can end in any of its
    sink cells (a dry pit above its lake too), its lake gets all of it.
    flow: routed (accumulate_lakes) over down; src, loss as in lakes()."""
    n = sink.shape[0]
    inflow = np.zeros(n)
    evap = np.zeros(n)
    cell = np.zeros(n)  # the most one more cell of lake would evaporate
    low = np.full(n, -1, np.int64)
    has = np.zeros(n, np.bool_)
    for i in range(n):
        d = down[i]
        if not sink[i]:
            if d >= 0 and sink[d]:
                inflow[basin[d]] += flow[i]
            continue
        b = basin[i]
        has[b] = True
        inflow[b] += src[i]
        if wet[i]:
            evap[b] += loss[i]
        cell[b] = max(cell[b], loss[i])
        if low[b] < 0 or bed[i] < bed[low[b]]:
            low[b] = i
    out = np.zeros(n)
    for b in range(n):
        if has[b]:
            x = inflow[b] - evap[b]
            if x > cell[b] and x > 1e-9:
                out[low[b]] = x
    return out


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
def accumulate_months(down, order, src, damp):
    """accumulate() for each month (src: (12, n)), with the monthly profile
    flattened toward its mean by damp (0..1) where a river leaves a lake
    (a lake stores the flood and lets it out slowly)."""
    m, n = src.shape
    flow = src.copy()
    for t in range(order.shape[0] - 1, -1, -1):
        i = order[t]
        if damp[i] > 0:
            mean = 0.0
            for k in range(m):
                mean += flow[k, i]
            mean /= m
            for k in range(m):
                flow[k, i] = (1 - damp[i]) * flow[k, i] + damp[i] * mean
        d = down[i]
        if d >= 0:
            for k in range(m):
                flow[k, d] += flow[k, i]
    return flow


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
def carve(h, down, order, cut):
    """h with each cell lowered by cut (m) where its river runs in a valley
    below the cell's mean height, but never below the next cell downstream
    as carved (a valley floor doesn't climb toward the sea, nor dig a pit).
    order runs outlet -> headwater."""
    out = h.copy()
    for t in range(order.shape[0]):
        i = order[t]
        d = down[i]
        if d < 0 or cut[i] <= 0:
            continue
        floor = max(out[d], 0.5 if h[i] > 0 else h[i])
        out[i] = min(h[i], max(h[i] - cut[i], floor))
    return out


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
