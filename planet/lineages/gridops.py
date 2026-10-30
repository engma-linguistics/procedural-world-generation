"""Grid helpers shared by the peoples modules."""

from __future__ import annotations

import numpy as np

from ..geo import arc_km


def nbr_reduce(grid, ufunc, vals):
    """ufunc over each cell's neighbours (vals: one per CSR edge; every cell has neighbours):
    ufunc.at(out, nbr_src, vals) without the slow unbuffered .at, as nbr_src is sorted."""
    return ufunc.reduceat(vals, grid.nbr_off[:-1])


def dist_km(grid, lat: float, lon: float) -> np.ndarray:
    """Great-circle distance (km) of every cell centre from a point (degrees)."""
    la, lo = np.radians(lat), np.radians(lon)
    c = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    return arc_km(grid.centers @ c)
