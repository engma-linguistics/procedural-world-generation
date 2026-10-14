"""Geodesic "hex" grid on a sphere (a Goldberg polyhedron).

Why you can't tile a sphere with only hexagons
------------------------------------------------
Euler's formula for any closed surface topologically like a sphere:

    V - E + F = 2

Treat each cell as a face. In an all-hex tiling every face has 6 edges and
every corner touches 3 faces, so E = 6F/2 = 3F and V = 6F/3 = 2F. Then
V - E + F = 2F - 3F + F = 0, not 2. A flat plane (or a torus) has Euler
characteristic 0, which is why hexes tile those perfectly. A sphere has 2.

The shortfall must come from smaller faces. A pentagon contributes +1/6 to
that sum, so you need exactly 12 pentagons, never more or fewer (if the
rest are hexes and every corner meets 3 cells). Note: 12, not 1. A football
(soccer ball) has 12 black pentagons for the same reason.

Construction
------------
1. Start with an icosahedron (20 triangles, 12 vertices).
2. Split every triangle into 4, `level` times, pushing new points onto the
   sphere. That's an "icosphere". Vertex count = 10 * 4**level + 2.
3. Take the *dual*: each icosphere vertex becomes a cell, and the centroid
   of each triangle becomes a cell corner. The 12 original icosahedron
   vertices have 5 neighbours and become pentagons. Every other cell is a
   (slightly irregular) hexagon.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

import numpy as np

from . import kernels
from .geo import latlon
from .kernels import build_raster, locate, order_cells


@dataclass
class Grid:
    level: int
    centers: np.ndarray  # (N, 3) unit vectors, one per cell
    faces: np.ndarray  # (T, 3) icosphere triangles (indices into centers)
    corners: np.ndarray  # (T, 3) unit vectors, one per triangle = cell corner
    cell_corners: list[list[int]]  # per cell, ordered corner indices (5 or 6)
    neighbors: list[list[int]]  # per cell, neighbour cell indices, same order
    edges: np.ndarray  # (E, 2) each undirected adjacency once, i < j
    nbr_off: np.ndarray  # CSR offsets: neighbours of i are nbr_idx[nbr_off[i]:nbr_off[i+1]]
    nbr_idx: np.ndarray
    _raster: np.ndarray | None = None

    @property
    def n(self) -> int:
        return len(self.centers)

    # Derived geometry is computed once per grid and read-only (shared by
    # every caller, so nobody may modify it in place).
    @cached_property
    def lat(self) -> np.ndarray:
        return _frozen(latlon(self.centers)[0])

    @cached_property
    def lon(self) -> np.ndarray:
        return _frozen(latlon(self.centers)[1])

    @cached_property
    def pentagons(self) -> np.ndarray:
        return _frozen(np.array([i for i, c in enumerate(self.cell_corners) if len(c) == 5]))

    @property
    def raster(self) -> np.ndarray:
        """Coarse lat/lon -> nearest cell lookup, used to seed point location."""
        if self._raster is None:
            w = int(4 * 2 ** self.level) * 2
            self._raster = build_raster(self.centers, self.nbr_off, self.nbr_idx, w, w // 2)
        return self._raster

    def locate(self, pts: np.ndarray, guess: np.ndarray | None = None) -> np.ndarray:
        """Nearest cell id for each unit vector in pts (N, 3)."""
        if guess is None:
            guess = np.full(len(pts), -1, np.int64)
        return locate(np.ascontiguousarray(pts), guess, self.raster, self.centers,
                      self.nbr_off, self.nbr_idx)

    @cached_property
    def spacing(self) -> float:
        """Mean centre-to-centre distance between neighbours, in radians."""
        a, b = self.centers[self.edges[:, 0]], self.centers[self.edges[:, 1]]
        return float(np.mean(np.arccos(np.clip((a * b).sum(1), -1, 1))))

    def components(self, mask: np.ndarray) -> tuple[np.ndarray, int]:
        """Connected regions of mask: (label per cell, -1 outside mask; count).
        Labels are numbered in order of each region's lowest cell id."""
        return kernels.components(mask, self.nbr_off, self.nbr_idx)


def _frozen(a: np.ndarray) -> np.ndarray:
    a.flags.writeable = False
    return a


def _icosahedron() -> tuple[np.ndarray, np.ndarray]:
    t = (1 + 5**0.5) / 2
    v = np.array(
        [
            [-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
            [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
            [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1],
        ],
        dtype=float,
    )
    f = np.array(
        [
            [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
            [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
            [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
            [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1],
        ]
    )
    return v / np.linalg.norm(v, axis=1, keepdims=True), f


def _subdivide(verts: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Split each triangle into 4. New midpoint vertices are appended after the
    existing ones, so the ids of coarser levels are preserved: cells
    0 .. 10*4**k+2 of any grid form the level-k grid."""
    nf = len(faces)
    e = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    e.sort(axis=1)
    uniq, inv = np.unique(e, axis=0, return_inverse=True)
    inv = inv.ravel()
    mid = verts[uniq[:, 0]] + verts[uniq[:, 1]]
    mid /= np.linalg.norm(mid, axis=1, keepdims=True)
    nv = len(verts)
    ab, bc, ca = inv[:nf] + nv, inv[nf:2 * nf] + nv, inv[2 * nf:] + nv
    a, b, c = faces.T
    new = np.stack([np.stack([a, ab, ca], 1), np.stack([b, bc, ab], 1),
                    np.stack([c, ca, bc], 1), np.stack([ab, bc, ca], 1)], 1).reshape(-1, 3)
    return np.concatenate([verts, mid]), new


def build_grid(level: int = 5) -> Grid:
    verts, faces = _icosahedron()
    for _ in range(level):
        verts, faces = _subdivide(verts, faces)

    # Tilt slightly so no pentagon sits exactly on a pole (purely cosmetic:
    # it avoids a suspiciously symmetric-looking pole).
    tilt = np.radians(7.0)
    rot = np.array(
        [[1, 0, 0], [0, np.cos(tilt), -np.sin(tilt)], [0, np.sin(tilt), np.cos(tilt)]]
    )
    verts = verts @ rot.T

    corners = verts[faces].sum(axis=1)
    corners /= np.linalg.norm(corners, axis=1, keepdims=True)

    n = len(verts)
    # vertex -> faces in CSR form
    flat = faces.ravel()
    order = np.argsort(flat, kind="stable")
    vf_idx = (order // 3).astype(np.int64)
    vf_off = np.zeros(n + 1, np.int64)
    np.cumsum(np.bincount(flat, minlength=n), out=vf_off[1:])
    corner_idx, nbr_idx = order_cells(verts, faces, corners, vf_off, vf_idx)

    cell_corners = [corner_idx[vf_off[i]:vf_off[i + 1]].tolist() for i in range(n)]
    neighbors = [nbr_idx[vf_off[i]:vf_off[i + 1]].tolist() for i in range(n)]
    src = np.repeat(np.arange(n), np.diff(vf_off))
    pairs = np.stack([src, nbr_idx], 1)
    edges = pairs[pairs[:, 0] < pairs[:, 1]]
    return Grid(level, verts, faces, corners, cell_corners, neighbors, edges, vf_off, nbr_idx)
