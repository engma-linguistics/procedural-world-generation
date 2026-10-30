"""Grid geometry for the finite-volume ice flow."""

from __future__ import annotations

import numpy as np

from ..geo import arc
from ..grid import Grid
from .params import R_M

_GEO = {}


def geometry(grid: Grid) -> dict:
    """Per cell: area (m2). Per directed edge (CSR order): centre distance
    and shared side length (m), unit tangent toward the neighbour. Cached."""
    key = (id(grid), grid.n)
    if key in _GEO:
        return _GEO[key]
    n, p = grid.n, grid.centers
    src = grid.nbr_src
    dst = grid.nbr_idx
    dist = arc((p[src] * p[dst]).sum(1)) * R_M
    u = grid.edge_dir
    # the side between two cells joins the two triangle centroids (corners)
    # of the two icosphere triangles that contain both of them
    f = grid.faces
    pairs = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    pairs.sort(1)
    face = np.tile(np.arange(len(f)), 3)
    k = pairs[:, 0].astype(np.int64) * n + pairs[:, 1]
    o = np.argsort(k, kind="stable")
    k, face = k[o], face[o]
    ukeys, c1, c2 = k[0::2], face[0::2], face[1::2]
    side = arc((grid.corners[c1] * grid.corners[c2]).sum(1)) * R_M
    ek = np.minimum(src, dst).astype(np.int64) * n + np.maximum(src, dst)
    elen = side[np.searchsorted(ukeys, ek)]
    # cell area: fan of triangles from the centre over its ordered corners
    deg = np.diff(grid.nbr_off)
    cc = np.zeros((n, 7), np.int64)
    for i, cs in enumerate(grid.cell_corners):
        cc[i, :len(cs)] = cs
        cc[i, len(cs):] = cs[0]
    a = grid.corners[cc[:, :-1]] - p[:, None, :]
    b = grid.corners[cc[:, 1:]] - p[:, None, :]
    area = 0.5 * np.linalg.norm(np.cross(a, b), axis=2).sum(1)
    area *= 4 * np.pi / area.sum() * R_M**2
    assert (deg >= 5).all()
    g = dict(area=area, dist=dist, elen=elen, ux=u[:, 0].copy(), uy=u[:, 1].copy(), uz=u[:, 2].copy(),
             d2min=float(dist.min()) ** 2)
    if len(_GEO) > 4:
        _GEO.clear()
    _GEO[key] = g
    return g
