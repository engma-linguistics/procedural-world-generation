"""Small raster (2-D image-grid) helpers shared by the zoom modules."""

from __future__ import annotations

import numpy as np


def box_mean(a: np.ndarray, w: np.ndarray, r: int) -> np.ndarray:
    """Weighted mean of a (2-D) with weights w over (2r+1)^2 windows; the edge rows and
    columns repeat outward."""
    def box(x):
        c = np.cumsum(np.pad(x, ((r + 1, r), (0, 0)), mode="edge"), 0)
        x = c[2 * r + 1:] - c[:-2 * r - 1]
        c = np.cumsum(np.pad(x, ((0, 0), (r + 1, r)), mode="edge"), 1)
        return c[:, 2 * r + 1:] - c[:, :-2 * r - 1]
    return box(a) / np.maximum(box(w), 1e-9)
