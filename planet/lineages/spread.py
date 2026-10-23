"""Range spread over the cell graph (numba): widest-path passes, one ring of cells per pass."""

from __future__ import annotations

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
