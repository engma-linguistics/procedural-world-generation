"""Range spread over the cell graph (numba): widest-path passes, one ring of cells per pass."""

from __future__ import annotations

import heapq

import numpy as np
from numba import njit

EST = 0.12  # carried pressure needed to establish (and presence below which a line is gone)


@njit(cache=True)
def spread(p, room, enter, elev, relief_k, sea, land, nbr_off, nbr_idx, passes):
    """p: presence (n,) in [0, 1], updated in place and returned. The pressure starts at p and
    moves one ring per pass (Jacobi): into land cell i it keeps enter[i] (x exp(-relief_k per
    1000 m climbed)), into a sea cell `sea` (0: no crossing). A cell is taken up to its room
    where the pressure reaches EST.

    Only the front is visited: a pass looks at the neighbours of the cells that changed in the
    pass before (the first, at the neighbours of the held cells); any other cell would find what
    it found last time, so the result is the same as sweeping every cell every pass."""
    n = p.shape[0]
    c = p.copy()
    mark = np.zeros(n, np.bool_)
    cand = np.empty(n, np.int64)
    nc = 0
    for i in range(n):
        if c[i] > 0:
            for k in range(nbr_off[i], nbr_off[i + 1]):
                j = nbr_idx[k]
                if not mark[j]:
                    mark[j] = True
                    cand[nc] = j
                    nc += 1
    chg = np.empty(n, np.int64)
    val = np.empty(n)
    for _ in range(passes):
        nch = 0
        for a in range(nc):
            i = cand[a]
            mark[i] = False
            best = c[i]
            for k in range(nbr_off[i], nbr_off[i + 1]):
                j = nbr_idx[k]
                if c[j] <= best:
                    continue
                if land[i]:
                    f = enter[i]
                    dh = elev[i] - elev[j]
                    if relief_k > 0 and dh > 0:
                        f *= np.exp(-relief_k * dh / 1000.0)
                else:
                    f = sea
                v = c[j] * f
                if v > best:
                    best = v
            if best > c[i] + 1e-6:
                chg[nch] = i
                val[nch] = best
                nch += 1
        if nch == 0:
            break
        for a in range(nch):
            c[chg[a]] = val[a]
        nc = 0
        for a in range(nch):
            i = chg[a]
            for k in range(nbr_off[i], nbr_off[i + 1]):
                j = nbr_idx[k]
                if not mark[j]:
                    mark[j] = True
                    cand[nc] = j
                    nc += 1
    for i in range(n):
        if land[i] and c[i] >= EST and room[i] > p[i]:
            v = min(room[i], c[i])
            if v >= EST and v > p[i]:
                p[i] = v
    return p


@njit(cache=True)
def nearest_label(label, mask, nbr_off, nbr_idx):
    """Multi-source BFS within mask: each mask cell takes the label (>= 0) of the nearest labelled cell."""
    n = label.shape[0]
    out = label.copy()
    q = np.empty(n, np.int64)
    h, t = 0, 0
    for i in range(n):
        if out[i] >= 0:
            q[t] = i
            t += 1
    while h < t:
        i = q[h]
        h += 1
        for k in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[k]
            if mask[j] and out[j] < 0:
                out[j] = out[i]
                q[t] = j
                t += 1
    return out


@njit(cache=True)
def rings(seed, mask, r, nbr_off, nbr_idx):
    """Cells within r graph steps of seed, through mask (seed always in)."""
    n = mask.shape[0]
    d = np.full(n, -1, np.int64)
    d[seed] = 0
    q = np.empty(n, np.int64)
    q[0] = seed
    h, t = 0, 1
    while h < t:
        i = q[h]
        h += 1
        if d[i] >= r:
            continue
        for k in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[k]
            if mask[j] and d[j] < 0:
                d[j] = d[i] + 1
                q[t] = j
                t += 1
    return d >= 0


@njit(cache=True)
def rivals_load(p, rows, a, t, idx, contact):
    """Competition a line feels on the cells idx: sum_j a_j p[j] + (1 - contact) sum_j t_j p[j] over
    the rival rows (niche overlap a, closed-country extra t; history.History.run)."""
    m = idx.shape[0]
    qa = np.zeros(m)
    qt = np.zeros(m)
    for r in range(rows.shape[0]):
        j = rows[r]
        aj, tj = a[j], t[j]
        for x in range(m):
            v = p[j, idx[x]]
            qa[x] += aj * v
            qt[x] += tj * v
    for x in range(m):
        qa[x] += (1.0 - contact[x]) * qt[x]
    return qa


@njit(cache=True)
def coexist_cap(p, rows, a0, t0, ab, tb, Km, Kk, idx, contact, W):
    """The rivals' presences as line k feels them on the cells idx, each capped at its Lotka-Volterra coexistence share with k
    (mutual invasibility, lane 73). Where the pair's effective coefficients (a0 + (1 - contact) t0: k from j; ab + (1 - contact) tb:
    j from k) are both under 1, two peoples coexist at p_j* = (K_j - a_jk K_k) / (1 - a_kj a_jk) whichever came first, so the
    load k feels from j is at most a_kj p_j*: its room is then its own share p_k*, and an incumbent above its share does not lock the
    newcomer out (without the cap the newcomer's room under a full incumbent, K_k - a_kj K_j, sat under the establishment threshold).
    Where either coefficient is 1 or more one excludes the other and the presence counts as it is. W (len(rows), len(idx)): the
    contest's fit weight of rival r on k at each cell (history.params.FIT_Q, lane 83), so the pair's coefficients there are k from j
    x W and j from k / W. Returns (len(rows), len(idx))."""
    m = idx.shape[0]
    out = np.empty((rows.shape[0], m))
    for r in range(rows.shape[0]):
        j = rows[r]
        for x in range(m):
            i = idx[x]
            v = p[j, i]
            c = 1.0 - contact[x]
            akj = (a0[j] + c * t0[j]) * W[r, x]
            ajk = (ab[j] + c * tb[j]) / W[r, x]
            if v > 0.0 and akj < 1.0 and ajk < 1.0:
                kj = Km[j, i] if Km[j, i] > v else v  # (K_j >= p_j: a row not yet set reads as the presence)
                s = (kj - ajk * Kk[i]) / (1.0 - akj * ajk)
                if s < 0.0:
                    s = 0.0
                if v > s:
                    v = s
            out[r, x] = v
    return out


@njit(cache=True)
def load_rows(P, a, t, rows, contact):
    """sum_j a_j P[r] + (1 - contact) sum_j t_j P[r], P as from coexist_cap (row r is rival rows[r])."""
    m = P.shape[1]
    qa = np.zeros(m)
    qt = np.zeros(m)
    for r in range(rows.shape[0]):
        j = rows[r]
        aj, tj = a[j], t[j]
        for x in range(m):
            qa[x] += aj * P[r, x]
            qt[x] += tj * P[r, x]
    for x in range(m):
        qa[x] += (1.0 - contact[x]) * qt[x]
    return qa


@njit(cache=True)
def graph_dist(mask, maxd, nbr_off, nbr_idx):
    """Graph steps from the mask cells (0 on them), over land and sea alike; -1 beyond maxd."""
    n = mask.shape[0]
    d = np.full(n, -1, np.int64)
    q = np.empty(n, np.int64)
    h, t = 0, 0
    for i in range(n):
        if mask[i]:
            d[i] = 0
            q[t] = i
            t += 1
    while h < t:
        i = q[h]
        h += 1
        if d[i] >= maxd:
            continue
        for k in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[k]
            if d[j] < 0:
                d[j] = d[i] + 1
                q[t] = j
                t += 1
    return d


@njit(cache=True)
def jump_reach(src, cost, maxd, nbr_off, nbr_idx):
    """Least summed cost from the src cells to each cell (Dijkstra; entering cell i costs cost[i], inf: impassable),
    -1 beyond maxd: the reach of a jump (history dispersal, PW-920), each cell's cost being its width over the people's
    jump length there (land or water)."""
    n = src.shape[0]
    d = np.full(n, np.inf)
    hq = [(0.0, 0)]
    hq.pop()
    for i in range(n):
        if src[i]:
            d[i] = 0.0
            hq.append((0.0, i))
    heapq.heapify(hq)
    while len(hq):
        di, i = heapq.heappop(hq)
        if di > d[i] or di > maxd:
            continue
        for k in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[k]
            c = cost[j]
            if not np.isfinite(c):
                continue
            v = di + c
            if v < d[j] and v <= maxd:
                d[j] = v
                heapq.heappush(hq, (v, j))
    return np.where(np.isfinite(d), d, -1.0)


@njit(cache=True)
def carry_max(L, held, cls, idx, nbr_off, nbr_idx):
    """For each cell idx[x]: the largest L over its held neighbours of the same class (cls; PW-1155, the learned country a people
    carries into frontier cells of the same biome), 0 where none."""
    out = np.zeros(idx.shape[0], np.float32)
    for x in range(idx.shape[0]):
        i = idx[x]
        best = 0.0
        for k in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[k]
            if held[j] and cls[j] == cls[i] and L[j] > best:
                best = L[j]
        out[x] = best
    return out


@njit(cache=True)
def learned_load(p, rows, dA, dT, Lm, k, idx, contact):
    """The extra load line k feels on the cells idx where it or a rival lives on learned country (history.habitat._learned_load,
    PW-1155): sum_j max(L_k, L_j) p_j (dA_j + (1 - contact) dT_j) over the rival rows."""
    m = idx.shape[0]
    out = np.zeros(m)
    for r in range(rows.shape[0]):
        j = rows[r]
        a, t = dA[j], dT[j]
        if a <= 0.0 and t <= 0.0:
            continue
        for x in range(m):
            i = idx[x]
            v = p[j, i]
            if v <= 0.0:
                continue
            w = Lm[k, i]
            if Lm[j, i] > w:
                w = Lm[j, i]
            if w > 0.0:
                out[x] += w * v * (a + (1.0 - contact[x]) * t)
    return out
