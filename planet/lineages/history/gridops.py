"""Neighbour-reduction and CSR helpers on the grid shared by the peoples modules."""

from __future__ import annotations

import numpy as np

from ..gridops import nbr_reduce

def _depth(grid, mask, cap: int = 80) -> np.ndarray:
    """How deep each cell of `mask` lies in it, in cells from the edge (successive erosions), 0 outside."""
    d = np.zeros(grid.n)
    cur = mask.copy()
    for _ in range(cap):
        if not cur.any():
            break
        d += cur
        cur = cur & nbr_reduce(grid, np.logical_and, cur[grid.nbr_idx])
    return d


def _csr_gather(off, rows):
    """The positions in a CSR edge list of the edges of `rows`, row after row, each in its own order."""
    cnt = off[rows + 1] - off[rows]
    start = np.cumsum(cnt) - cnt
    return np.repeat(off[rows] - start, cnt) + np.arange(int(cnt.sum()))


def _isin(cl, ids):
    """np.isin for the small Köppen ids (a lookup table)."""
    lut = np.zeros(max(int(cl.max()), max(ids)) + 1, bool)
    lut[list(ids)] = True
    return lut[cl]


def _soft(x, lo, hi, soft):
    return np.clip(np.minimum((x - (lo - soft)) / soft, ((hi + soft) - x) / soft), 0, 1)
