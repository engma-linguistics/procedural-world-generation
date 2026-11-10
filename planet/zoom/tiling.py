"""A tiling of the sphere by regional-zoom sections (PW-1319, epic PW-1299; design in docs/review/land-zoom/tiling.md).

The sphere is cut like an equiangular cube sphere: six faces, each split n x n into cells whose edges are great circles.
Every cell is the *home* of one section: a regional zoom (an azimuthal equidistant square, `Frame`) centred on the cell's
centre, with its +y axis along the face's v axis (a shared orientation, so neighbours' squares are parallel to the cell
edges they share), `size_km` on a side. A cell lies wholly inside its own square with a known margin; two neighbours'
squares therefore overlap in a band of at least the sum of the two margins, centred on the shared cell edge (the
bisector the seam measurements use). Nothing here builds a zoom: it only lists sections.

    sections(world, size_km=4000, min_overlap_km=190) -> list of dicts (id, face, i, j, lat, lon, up, margin_km, ...)
"""
from __future__ import annotations

import numpy as np

from ..geo import R_KM, latlon, world_land
from . import regional as RG

# face normal a, then tangent axes u (cell index i grows along it) and v (index j; the section's +y, "up")
FACES = {
    "px": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    "py": ((0, 1, 0), (-1, 0, 0), (0, 0, 1)),
    "mx": ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
    "my": ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
    "pz": ((0, 0, 1), (0, 1, 0), (-1, 0, 0)),
    "mz": ((0, 0, -1), (0, 1, 0), (1, 0, 0)),
}
_FA = np.array([FACES[f][0] for f in FACES], float)
_FU = np.array([FACES[f][1] for f in FACES], float)
_FV = np.array([FACES[f][2] for f in FACES], float)
_NAMES = list(FACES)


def cell_point(face: int, a, b) -> np.ndarray:
    """Unit vector(s) of face `face` at equiangular face angles a (along u) and b (along v), radians in +-pi/4."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    p = _FA[face] + np.tan(a)[..., None] * _FU[face] + np.tan(b)[..., None] * _FV[face]
    return p / np.linalg.norm(p, axis=-1, keepdims=True)


def locate(p: np.ndarray, n: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(face, i, j) of the cell holding each unit vector of p (shape (m, 3))."""
    p = np.atleast_2d(p)
    dots = p @ _FA.T  # (m, 6)
    face = np.argmax(dots, axis=1)
    d = dots[np.arange(len(p)), face]
    a = np.arctan2(np.einsum("ij,ij->i", p, _FU[face]), d)
    b = np.arctan2(np.einsum("ij,ij->i", p, _FV[face]), d)
    e = _edges(n)[1:-1]
    i, j = np.searchsorted(e, a), np.searchsorted(e, b)
    return face, i, j


# Cell edges at (pi/4) sign(t)|t|^WARP for t evenly in -1..1. At 1 (equiangular) a 3 x 3 face's corner cells are too big
# for a 4000 km square (margin -26 km); 0.88 shrinks them and widens the middle cell: least margin 97 km (found by scan).
WARP = 0.88


def _edges(n: int) -> np.ndarray:
    t = np.linspace(-1.0, 1.0, n + 1)
    return np.pi / 4 * np.sign(t) * np.abs(t) ** WARP


def _boundary(face: int, i: int, j: int, n: int, per_edge: int = 24) -> np.ndarray:
    """Points along a cell's four edges (great-circle arcs), corners included."""
    e = _edges(n)
    t = np.linspace(0.0, 1.0, per_edge, endpoint=False)
    a0, a1, b0, b1 = e[i], e[i + 1], e[j], e[j + 1]
    sides = [(a0 + t * (a1 - a0), np.full_like(t, b0)), (np.full_like(t, a1), b0 + t * (b1 - b0)),
             (a1 - t * (a1 - a0), np.full_like(t, b1)), (np.full_like(t, a0), b1 - t * (b1 - b0))]
    return np.concatenate([cell_point(face, a, b) for a, b in sides])


def frame_of(c: np.ndarray, up: np.ndarray) -> RG.Frame:
    lat, lon = latlon(c)
    return RG.Frame(float(lat), float(lon), up=up)


def margin_km(face: int, i: int, j: int, n: int, size_km: float) -> tuple[float, float]:
    """(least, greatest) distance in km from the cell's boundary to the edge of its section's square, measured in the
    section's own plane (positive: the cell is inside the square)."""
    e = _edges(n)
    c = cell_point(face, (e[i] + e[i + 1]) / 2, (e[j] + e[j + 1]) / 2)
    fr = frame_of(c, _FV[face])
    x, y = fr.to_plane(_boundary(face, i, j, n))
    m = size_km / 2 - np.maximum(np.abs(x), np.abs(y))
    return float(m.min()), float(m.max())


def choose_n(size_km: float, min_overlap_km: float, nmax: int = 24) -> int:
    """The fewest divisions per face for which every cell has at least min_overlap_km / 2 margin inside a size_km square."""
    for n in range(1, nmax + 1):
        if min(margin_km(f, i, j, n, size_km)[0] for f in range(6) for i in range(n) for j in range(n)) >= min_overlap_km / 2:
            return n
    raise ValueError("no tiling: size_km too small for the overlap")


def sections(world: dict | None = None, size_km: float = 4000.0, min_overlap_km: float = 190.0, n: int | None = None,
             min_land_frac: float = 0.05, keep_all: bool = False) -> list[dict]:
    """The sections of the tiling; with a world, only those whose home cell holds land: at least min_land_frac of a
    cell's even share of the world's grid cells (0.05: a twentieth of a cell's area as land; 0 keeps any land cell);
    keep_all lists every cell (GET /api/sections).

    Each is {id, face, i, j, lat, lon, up (unit vector, the section's +y), size_km, margin_km (least, greatest),
    land_cells (world cells of land in the home cell, None without a world), world_cells (all the world's cells in the
    home cell, None without a world), neighbours (ids of the cells that share an
    edge or corner, whether or not listed), overlap_km (least band shared with each neighbour: the sum of both margins)}.
    The section is built as RG.Frame(lat, lon, up=up) at size_km; it covers its home cell with margin_km[0] to spare.
    """
    n = n or choose_n(size_km, min_overlap_km)
    land = None
    if world is not None:
        g = world["grid"]
        keep = np.flatnonzero(world_land(world["layers"], g))
        f, i, j = locate(np.asarray(g.centers)[keep], n)
        land = np.zeros((6, n, n), int)
        np.add.at(land, (f, i, j), 1)
        fa, ia, ja = locate(np.asarray(g.centers), n)
        total = np.zeros((6, n, n), int)
        np.add.at(total, (fa, ia, ja), 1)
    e = _edges(n)
    out, by_id = [], {}
    for f in range(6):
        for i in range(n):
            for j in range(n):
                c = cell_point(f, (e[i] + e[i + 1]) / 2, (e[j] + e[j + 1]) / 2)
                lat, lon = latlon(c)
                lo, hi = margin_km(f, i, j, n, size_km)
                pts = _boundary(f, i, j, n, per_edge=2)  # the corners and edge midpoints' neighbours: probe a little out
                probe = pts + 1e-3 * (pts - c)
                nf, ni, nj = locate(probe / np.linalg.norm(probe, axis=1, keepdims=True), n)
                nb = sorted({f"{_NAMES[a]}.{b}.{d}" for a, b, d in zip(nf, ni, nj)} - {f"{_NAMES[f]}.{i}.{j}"})
                s = dict(id=f"{_NAMES[f]}.{i}.{j}", face=_NAMES[f], i=i, j=j, lat=float(lat), lon=float(lon), up=_FV[f].copy(),
                         size_km=size_km, margin_km=(lo, hi), land_cells=None if land is None else int(land[f, i, j]),
                         world_cells=None if land is None else int(total[f, i, j]),
                         neighbours=nb)
                out.append(s)
                by_id[s["id"]] = s
    for s in out:
        s["overlap_km"] = min(s["margin_km"][0] + by_id[k]["margin_km"][0] for k in s["neighbours"])
    if land is not None and not keep_all:
        even = len(g.centers) / (6 * n * n)
        out = [s for s in out if s["land_cells"] > 0 and s["land_cells"] >= min_land_frac * even]
    return out


def section(cell: str, size_km: float = 4000.0, min_overlap_km: float = 190.0, n: int | None = None) -> dict:
    """One section of the tiling by its cell id ('px.1.1'; `planet zoom WORLD --section px.1.1`, PW-1338)."""
    for s in sections(None, size_km, min_overlap_km, n):
        if s["id"] == cell:
            return s
    raise SystemExit(f"no section {cell!r} in the {size_km:g} km tiling (ids are face.i.j, faces {' '.join(FACES)})")
