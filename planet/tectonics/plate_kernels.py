"""Compiled (numba) kernels for the plate pull/resolve step.

Each plate keeps its crust on its own copy of the grid; `idx[k, i]` is the
cell of plate k's grid under world cell i. These kernels decide who owns
each world cell, delete subducted crust, patch sampling holes and make new
ocean floor in the gaps (see the package docstring).
"""

from __future__ import annotations

import numpy as np
from numba import njit

from .. import kernels
from ..surface import CRATON, OCEAN, OROGEN
from .isostasy import OCEAN_KM


@njit(cache=True)
def _fill(k, r, refs, owned, age, cont, thick, rock, cover, extra):
    """Fill hole r in plate k's grid from its neighbours refs (-1 = not part
    of this plate). It's continental only if it's completely enclosed by
    continent; otherwise it copies just its oceanic neighbours. A notch in a
    continent's edge (no oceanic neighbour, not enclosed) is left empty.

    A majority vote here let continents fill in their own ragged edges every
    step and slowly swell (~1.5% of the planet per 100 Myr)."""
    nc, no = 0, 0
    sa, st, sc, oa, ot, oc = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    nx = extra.shape[2]
    sx, ox = np.zeros(nx), np.zeros(nx)
    rc, ro = -1, -1
    for j in refs:
        if j < 0 or not owned[k, j]:
            continue
        if cont[k, j]:
            nc += 1
            sa += age[k, j]
            st += thick[k, j]
            sc += cover[k, j]
            sx += extra[k, j]
            rc = j
        else:
            no += 1
            oa += age[k, j]
            ot += thick[k, j]
            oc += cover[k, j]
            ox += extra[k, j]
            ro = j
    if nc == len(refs):
        age[k, r], thick[k, r], cont[k, r], cover[k, r] = sa / nc, st / nc, True, sc / nc
        rock[k, r] = rock[k, rc]
        extra[k, r] = sx / nc
    elif no > 0:
        age[k, r], thick[k, r], cont[k, r], cover[k, r] = oa / no, ot / no, False, oc / no
        rock[k, r] = rock[k, ro]
        extra[k, r] = ox / no
    else:
        return False
    owned[k, r] = True
    return True


@njit(cache=True)
def resolve(alive, idx, owned, age, cont, thick, rock, cover, extra, prev_owner, nbr_off, nbr_idx, Q, centers, stacked):
    """Decide which plate owns each world cell; delete subducted crust,
    fill aliasing holes, create new ocean floor in gaps.
    Returns (owner, new_crust flag, collision count matrix).

    Continent vs continent: the loser's crust isn't destroyed, it's stacked
    onto the winner's (crust is too buoyant to sink: collisions thicken it)."""
    P, n = idx.shape
    owner = np.full(n, -1, np.int64)
    newc = np.zeros(n, np.bool_)
    coll = np.zeros((P, P), np.int64)
    cand = np.empty(P, np.int64)
    q = np.empty(3)
    # Pass 0: patch small holes inside a plate (nearest-neighbour
    # sampling of a rotated grid occasionally lands on a ref cell nobody
    # wrote). Without this, older crust underneath shows through as speckle.
    for k in range(P):
        if not alive[k]:
            continue
        for i in range(n):
            r = idx[k, i]
            if owned[k, r]:
                continue
            cnt, tot = 0, nbr_off[r + 1] - nbr_off[r]
            for e in range(nbr_off[r], nbr_off[r + 1]):
                if owned[k, nbr_idx[e]]:
                    cnt += 1
            if cnt >= tot - 2:
                _fill(k, r, nbr_idx[nbr_off[r]:nbr_off[r + 1]], owned, age, cont, thick, rock, cover, extra)
    for i in range(n):
        m = 0
        for k in range(P):
            if alive[k] and owned[k, idx[k, i]]:
                cand[m] = k
                m += 1
        if m == 0:
            continue
        w = cand[0]
        for c in range(1, m):
            k = cand[c]
            rk, rw = idx[k, i], idx[w, i]
            if cont[k, rk] != cont[w, rw]:
                if cont[k, rk]:
                    w = k
            elif cont[k, rk]:
                if k == prev_owner[i] or (w != prev_owner[i] and thick[k, rk] > thick[w, rw]):
                    w = k
            elif age[k, rk] < age[w, rw]:
                w = k
        owner[i] = w
        rw = idx[w, i]
        for c in range(m):
            k = cand[c]
            if k == w:
                continue
            rk = idx[k, i]
            if cont[k, rk] and cont[w, rw]:
                coll[w, k] += 1
                coll[k, w] += 1
                stacked[i] += thick[k, rk]  # spread over a belt by crust.stack_collisions
                if rock[w, rw] != CRATON:
                    rock[w, rw] = OROGEN  # buried, squeezed and cooked
            owned[k, rk] = False
    # gaps: first try "hole in a plate" (aliasing), else new ocean floor
    for i in range(n):
        if owner[i] >= 0:
            continue
        best_k, best_c = -1, 0
        for k in range(P):
            if not alive[k]:
                continue
            r = idx[k, i]
            cnt = 0
            for e in range(nbr_off[r], nbr_off[r + 1]):
                if owned[k, nbr_idx[e]]:
                    cnt += 1
            if cnt > best_c:
                best_c, best_k = cnt, k
        if best_k >= 0 and best_c >= 4:
            r = idx[best_k, i]
            if _fill(best_k, r, nbr_idx[nbr_off[r]:nbr_off[r + 1]], owned, age, cont, thick, rock, cover, extra):
                owner[i] = best_k
    counts = np.zeros(P, np.int64)
    for i in range(n):
        if owner[i] >= 0:
            continue
        # new ocean floor joins whichever plate holds most of its neighbours
        for k in range(P):
            counts[k] = 0
        for e in range(nbr_off[i], nbr_off[i + 1]):
            o = owner[nbr_idx[e]]
            if o >= 0:
                counts[o] += 1
        k = np.argmax(counts)
        deg = nbr_off[i + 1] - nbr_off[i]
        if counts[k] >= deg - 1 and counts[k] == counts.sum():
            # Surrounded by one plate (at most one other gap next to it): a real
            # ridge always borders another plate, so this is a sampling hole.
            # Fill it from the neighbours instead of making new sea floor.
            refs = np.full(deg, -1, np.int64)
            for e in range(nbr_off[i], nbr_off[i + 1]):
                if owner[nbr_idx[e]] == k:
                    refs[e - nbr_off[i]] = idx[k, nbr_idx[e]]
            if _fill(k, idx[k, i], refs, owned, age, cont, thick, rock, cover, extra):
                owner[i] = k
                continue
        if counts[k] == 0:
            k = prev_owner[i] if prev_owner[i] >= 0 and alive[prev_owner[i]] else np.argmax(alive)
        r = idx[k, i]
        owned[k, r] = True
        age[k, r] = 0.0
        thick[k, r] = OCEAN_KM
        rock[k, r] = OCEAN
        cover[k, r] = 0.0
        extra[k, r] = 0.0
        cont[k, r] = False
        owner[i] = k
        newc[i] = True
        # The plate's grid is rotated relative to the world grid, so several of
        # its cells can fall inside world cell i. Write all of them, or the
        # skipped ones become holes ("lace") that show up later as speckle.
        for e in range(nbr_off[r], nbr_off[r + 1]):
            r2 = nbr_idx[e]
            if owned[k, r2]:
                continue
            for a in range(3):
                q[a] = Q[k, a, 0] * centers[r2, 0] + Q[k, a, 1] * centers[r2, 1] + Q[k, a, 2] * centers[r2, 2]
            if kernels.walk_nearest(q, i, centers, nbr_off, nbr_idx) == i:
                owned[k, r2] = True
                age[k, r2] = 0.0
                thick[k, r2] = OCEAN_KM
                rock[k, r2] = OCEAN
                cover[k, r2] = 0.0
                extra[k, r2] = 0.0
                cont[k, r2] = False
    return owner, newc, coll


@njit(cache=True)
def crust_flow(t, ea, eb, k0, n_sub):
    """Thick crust spreads to its neighbours, faster the thicker it is."""
    t = t.copy()
    flux = np.empty(len(ea))
    for _ in range(n_sub):
        for e in range(len(ea)):
            a, b = ea[e], eb[e]
            x = max(max(t[a], t[b]) - 40.0, 0.0) / 10.0
            flux[e] = min(k0 * (x + x * x * x), 0.15) * (t[b] - t[a])
        for e in range(len(ea)):
            t[ea[e]] += flux[e]
            t[eb[e]] -= flux[e]
    return t


@njit(cache=True)
def cleanup_ghosts(alive, owned, Q, centers, owner, raster, nbr_off, nbr_idx):
    """Delete plate crust that sits deep under another plate (a leftover of
    nearest-neighbour sampling: a subducted cell nobody happened to 'pull')."""
    P, n = owned.shape
    h, w = raster.shape
    q = np.empty(3)
    removed = 0
    for k in range(P):
        if not alive[k]:
            continue
        for r in range(n):
            if not owned[k, r]:
                continue
            for a in range(3):
                q[a] = Q[k, a, 0] * centers[r, 0] + Q[k, a, 1] * centers[r, 1] + Q[k, a, 2] * centers[r, 2]
            lat = np.arcsin(min(1.0, max(-1.0, q[2])))
            lon = np.arctan2(q[1], q[0])
            y = min(h - 1, int((np.pi / 2 - lat) / np.pi * h))
            x = min(w - 1, int((lon + np.pi) / (2 * np.pi) * w))
            c = kernels.walk_nearest(q, raster[y, x], centers, nbr_off, nbr_idx)
            if owner[c] == k:
                continue
            deep = True
            for e in range(nbr_off[c], nbr_off[c + 1]):
                if owner[nbr_idx[e]] == k:
                    deep = False
                    break
            if deep:
                owned[k, r] = False
                removed += 1
    return removed
