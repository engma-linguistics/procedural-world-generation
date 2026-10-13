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

import numpy as np


@dataclass
class Grid:
    level: int
    centers: np.ndarray  # (N, 3) unit vectors, one per cell
    faces: np.ndarray  # (T, 3) icosphere triangles (indices into centers)
    corners: np.ndarray  # (T, 3) unit vectors, one per triangle = cell corner
    cell_corners: list[list[int]]  # per cell, ordered corner indices (5 or 6)
    neighbors: list[list[int]]  # per cell, neighbour cell indices, same order
    edges: np.ndarray  # (E, 2) each undirected adjacency once, i < j

    @property
    def n(self) -> int:
        return len(self.centers)

    @property
    def lat(self) -> np.ndarray:
        return np.degrees(np.arcsin(np.clip(self.centers[:, 2], -1, 1)))

    @property
    def lon(self) -> np.ndarray:
        return np.degrees(np.arctan2(self.centers[:, 1], self.centers[:, 0]))

    @property
    def pentagons(self) -> np.ndarray:
        return np.array([i for i, c in enumerate(self.cell_corners) if len(c) == 5])

    @property
    def spacing(self) -> float:
        """Mean centre-to-centre distance between neighbours, in radians."""
        a, b = self.centers[self.edges[:, 0]], self.centers[self.edges[:, 1]]
        return float(np.mean(np.arccos(np.clip((a * b).sum(1), -1, 1))))


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
    verts = list(verts)
    cache: dict[tuple[int, int], int] = {}

    def midpoint(a: int, b: int) -> int:
        key = (a, b) if a < b else (b, a)
        if key not in cache:
            m = verts[a] + verts[b]
            verts.append(m / np.linalg.norm(m))
            cache[key] = len(verts) - 1
        return cache[key]

    new_faces = []
    for a, b, c in faces:
        ab, bc, ca = midpoint(a, b), midpoint(b, c), midpoint(c, a)
        new_faces += [[a, ab, ca], [b, bc, ab], [c, ca, bc], [ab, bc, ca]]
    return np.array(verts), np.array(new_faces)


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
    vert_faces: list[list[int]] = [[] for _ in range(n)]
    for fi, tri in enumerate(faces):
        for v in tri:
            vert_faces[v].append(fi)

    cell_corners: list[list[int]] = []
    neighbors: list[list[int]] = []
    for v in range(n):
        # Order the surrounding triangles counter-clockwise around the cell
        # centre (as seen from outside the sphere).
        c = verts[v]
        ref = np.cross(c, [0.0, 0.0, 1.0])
        if np.linalg.norm(ref) < 1e-6:
            ref = np.cross(c, [1.0, 0.0, 0.0])
        ref /= np.linalg.norm(ref)
        ref2 = np.cross(c, ref)
        fs = vert_faces[v]
        d = corners[fs] - c
        ang = np.arctan2(d @ ref2, d @ ref)
        ordered = [fs[i] for i in np.argsort(ang)]
        cell_corners.append(ordered)
        # The neighbour "between" consecutive corners k and k+1 is the vertex
        # those two triangles share besides v.
        nb = []
        for k in range(len(ordered)):
            shared = set(faces[ordered[k]]) & set(faces[ordered[(k + 1) % len(ordered)]])
            shared.discard(v)
            nb.append(shared.pop())
        neighbors.append(nb)

    edges = np.array(sorted({(min(a, b), max(a, b)) for a, nb in enumerate(neighbors) for b in nb}))
    return Grid(level, verts, faces, corners, cell_corners, neighbors, edges)
