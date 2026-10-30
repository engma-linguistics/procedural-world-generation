"""Founding a set number of people at a place (PW-1150, lane 78): an arrival's wave through a portal."""

from __future__ import annotations

import numpy as np

from ..spread import EST, rings


def found_people(h, k: int, cell: int, K: np.ndarray, people: float, max_km: float) -> tuple[np.ndarray, float]:
    """Line k's founders hold the country round `cell` ring by ring (through its habitat, K > EST), each cell at its habitat (at
    least 0.3, as the other founding blobs), until they number `people` or the rings reach `max_km`. Returns (the blob, the people it
    carries). Where others live they arrive all the same, and the competition then sorts them out."""
    g = h.grid
    area = h.cell_mkm2 * 1e6
    d = h.dens_at(k)
    held = np.clip(K, 0.3, 1.0)
    mask = K > EST
    blob = np.zeros(g.n, bool)
    blob[cell] = True
    carried = 0.0
    for r in range(0, max(1, int(round(max_km / h.cell_km))) + 1):
        blob = rings(int(cell), mask | (np.arange(g.n) == cell), r, g.nbr_off, g.nbr_idx) & (mask | (np.arange(g.n) == cell))
        carried = float((held[blob] * (d[blob] if np.ndim(d) else d) * area).sum())
        if carried >= people:
            break
    h.p[k][blob] = np.maximum(h.p[k][blob], held[blob])
    return blob, carried
