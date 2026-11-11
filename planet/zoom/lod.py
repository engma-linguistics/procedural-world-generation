"""The level-of-detail tile pyramid (docs/review/zoom/lod-plan-v2.md, PW-1673, epic PW-1198).

Every cell of the 4,000 km tiling (zoom/tiling.py) is the root of a pyramid of square tiles laid on that cell's own plane: its
section's azimuthal equidistant `Frame(lat, lon, up)`, the square [-2000, 2000] km on both axes. Level 1 is the whole square
(today's section, built from the world); every finer level is a grid of tiles on one pixel lattice per level, each tile exactly
an n x n block of the next level's tiles, so siblings built at different times share a pixel grid and a parent level. Nothing
here builds a tile: it names them, places them and says which parent tiles a build reads.

    LEVELS                          the ladder: res_km, tile_km, px per level
    Key(cell, level, tx, ty)        a tile's address (tx east, ty south, from the square's north-west corner)
    rect(key) -> (x0, x1, y0, y1)   its square in the cell's plane, km
    lattice(key, halo_px)           its pixel centres in the plane (shared by every tile of the level)
    parent(key), children(key)
    exists(key)                     the tile touches its cell (dilated by PAD_PX of its own pixels)
    covering(cell, level, rect)     the existing tiles over a rectangle of the plane (what a view needs)
    parent_sources(key)             the parent-level tiles a build's stitched parent window reads
    tile_id(world_id, key, seed)    the deterministic id it is saved under
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from . import regional as RG
from . import tiling as ZT

SQUARE_KM = 4000.0  # the tiling's section size (api.SECTION_KM)
HALF = SQUARE_KM / 2

# (res_km, tile_km): level 1 is the whole square from the world; below it the fine pass, 500 px tiles (lod-plan-v2.md 1.2:
# measured 13-17 s and ~3.5 GB a tile at 500 px against 38-43 s and 7-9 GB at 1,000 px)
LEVELS = {
    1: (4.0, 4000.0),
    2: (1.0, 500.0),
    3: (0.25, 125.0),
    4: (0.025, 12.5),
}
FINEST = max(LEVELS)
# a level's tiles exist where they come within this many of their own pixels of their cell: enough that a child pixel inside
# the cell finds every parent pixel its build reads (fine.EDGE_PX 3 + HALO_PARENT_PX 1 + the bicubic's 2)
PAD_PX = 8


def res_km(level: int) -> float:
    return LEVELS[level][0]


def tile_km(level: int) -> float:
    return LEVELS[level][1]


def tile_px(level: int) -> int:
    r, t = LEVELS[level]
    return int(round(t / r))


def per_side(level: int) -> int:
    """Tiles across the square at this level."""
    return int(round(SQUARE_KM / tile_km(level)))


def branching(level: int) -> int:
    """Children across one tile of this level (the next level's tiles per side)."""
    return int(round(tile_km(level) / tile_km(level + 1)))


@dataclass(frozen=True, order=True)
class Key:
    cell: str
    level: int
    tx: int
    ty: int

    def __post_init__(self):
        if self.level not in LEVELS:
            raise ValueError(f"no level {self.level} (levels {min(LEVELS)}-{FINEST})")
        n = per_side(self.level)
        if not (0 <= self.tx < n and 0 <= self.ty < n):
            raise ValueError(f"tile {self.tx},{self.ty} outside level {self.level}'s {n} x {n}")

    def __str__(self):
        return f"{self.cell}/{self.level}/{self.tx}/{self.ty}"

    @classmethod
    def parse(cls, s: str) -> "Key":
        cell, level, tx, ty = s.split("/")
        return cls(cell, int(level), int(tx), int(ty))


def rect(key: Key) -> tuple[float, float, float, float]:
    """(x0, x1, y0, y1) km in the cell's plane (x east, y up: the section's own axes)."""
    t = tile_km(key.level)
    x0 = -HALF + key.tx * t
    y1 = HALF - key.ty * t
    return x0, x0 + t, y1 - t, y1


def lattice(key: Key, halo_px: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Pixel centres (x, y), km, of the tile and halo_px round it, row-major from the north-west as a zoom's layers;
    every tile of a level is a block of one lattice (x = -2000 + (i + 0.5) res)."""
    r = res_km(key.level)
    n = tile_px(key.level)
    x0, _, _, y1 = rect(key)
    k = np.arange(-halo_px, n + halo_px) + 0.5
    xs = x0 + k * r
    ys = y1 - k * r
    X, Y = np.meshgrid(xs, ys)
    return X.ravel(), Y.ravel()


def centre_xy(key: Key) -> tuple[float, float]:
    x0, x1, y0, y1 = rect(key)
    return 0.5 * (x0 + x1), 0.5 * (y0 + y1)


def parent(key: Key) -> Key | None:
    if key.level == min(LEVELS):
        return None
    b = branching(key.level - 1)
    return Key(key.cell, key.level - 1, key.tx // b, key.ty // b)


def children(key: Key) -> list[Key]:
    if key.level == FINEST:
        return []
    b = branching(key.level)
    return [Key(key.cell, key.level + 1, key.tx * b + i, key.ty * b + j) for j in range(b) for i in range(b)]


def ancestors(key: Key) -> list[Key]:
    """Parent, grandparent, ... up to level 1."""
    out, k = [], parent(key)
    while k is not None:
        out.append(k)
        k = parent(k)
    return out


# ---- the cell's outline in its plane ---------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _cell(cell: str) -> tuple:
    """(section dict, Frame, outline vertices (m, 2) km in the plane, closed by wrapping)."""
    s = ZT.section(cell, SQUARE_KM)
    fr = RG.Frame(s["lat"], s["lon"], up=s["up"])
    n = ZT.choose_n(SQUARE_KM, 190.0)
    fi = list(ZT.FACES).index(s["face"])
    p = ZT._boundary(fi, s["i"], s["j"], n, per_edge=256)
    x, y = fr.to_plane(p)
    return s, fr, np.column_stack([x, y])


def frame(cell: str) -> RG.Frame:
    """The cell's plane: the Frame every tile under it is laid on."""
    return _cell(cell)[1]


def outline(cell: str) -> np.ndarray:
    """The cell's boundary in its plane, (m, 2) km (great-circle edges, finely sampled)."""
    return _cell(cell)[2]


def _inside(poly: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Even-odd test of points against a closed polygon."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ax, ay = poly[:, 0], poly[:, 1]
    bx, by = np.roll(ax, -1), np.roll(ay, -1)
    cond = (ay[None, :] > y[:, None]) != (by[None, :] > y[:, None])
    with np.errstate(divide="ignore", invalid="ignore"):
        xc = ax[None, :] + (y[:, None] - ay[None, :]) * (bx - ax)[None, :] / (by - ay)[None, :]
    return (cond & (x[:, None] < xc)).sum(axis=1) % 2 == 1


def _seg_rect_dist(poly: np.ndarray, r: tuple[float, float, float, float]) -> float:
    """Least distance (km) from the polygon's boundary to the axis-aligned rectangle r (0 where they cross)."""
    x0, x1, y0, y1 = r
    a = poly
    b = np.roll(poly, -1, axis=0)
    # crossing: Liang-Barsky clip of each segment against the rectangle
    d = b - a
    t0, t1 = np.zeros(len(a)), np.ones(len(a))
    ok = np.ones(len(a), bool)
    for p_, q_ in ((-d[:, 0], a[:, 0] - x0), (d[:, 0], x1 - a[:, 0]), (-d[:, 1], a[:, 1] - y0), (d[:, 1], y1 - a[:, 1])):
        par = p_ == 0
        ok &= ~(par & (q_ < 0))
        with np.errstate(divide="ignore", invalid="ignore"):
            t = q_ / p_
        t0 = np.where(~par & (p_ < 0), np.maximum(t0, t), t0)
        t1 = np.where(~par & (p_ > 0), np.minimum(t1, t), t1)
    if np.any(ok & (t0 <= t1)):
        return 0.0
    # else: endpoints to the rectangle, and the rectangle's corners to the segments
    dx = np.maximum(np.maximum(x0 - a[:, 0], 0), a[:, 0] - x1)
    dy = np.maximum(np.maximum(y0 - a[:, 1], 0), a[:, 1] - y1)
    best = float(np.hypot(dx, dy).min())
    L2 = np.maximum((d * d).sum(axis=1), 1e-12)
    for cx, cy in ((x0, y0), (x0, y1), (x1, y0), (x1, y1)):
        t = np.clip(((cx - a[:, 0]) * d[:, 0] + (cy - a[:, 1]) * d[:, 1]) / L2, 0, 1)
        best = min(best, float(np.hypot(a[:, 0] + t * d[:, 0] - cx, a[:, 1] + t * d[:, 1] - cy).min()))
    return best


def cell_distance(cell: str, r: tuple[float, float, float, float]) -> float:
    """km from the rectangle r (in the cell's plane) to the cell: 0 if they overlap."""
    poly = outline(cell)
    x0, x1, y0, y1 = r
    if _inside(poly, np.array([0.5 * (x0 + x1)]), np.array([0.5 * (y0 + y1)]))[0]:
        return 0.0
    return _seg_rect_dist(poly, r)


def exists(key: Key) -> bool:
    """Whether the pyramid has this tile: it comes within PAD_PX of its own pixels of its cell (level 1 always)."""
    if key.level == min(LEVELS):
        return True
    return cell_distance(key.cell, rect(key)) <= PAD_PX * res_km(key.level)


def in_cell(cell: str, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Whether plane points (km) of this cell's plane lie in the cell itself (the owner test the viewer clips by)."""
    return _inside(outline(cell), x, y)


def tile_at(cell: str, level: int, x: float, y: float) -> Key:
    """The tile of a level holding the plane point (x, y)."""
    t, n = tile_km(level), per_side(level)
    tx = int(np.clip(np.floor((x + HALF) / t), 0, n - 1))
    ty = int(np.clip(np.floor((HALF - y) / t), 0, n - 1))
    return Key(cell, level, tx, ty)


def covering(cell: str, level: int, r: tuple[float, float, float, float]) -> list[Key]:
    """The existing tiles of a level that overlap the plane rectangle r = (x0, x1, y0, y1), km."""
    x0, x1, y0, y1 = r
    a = tile_at(cell, level, x0, y1)
    b = tile_at(cell, level, x1 - 1e-9, y0 + 1e-9)
    out = []
    for ty in range(a.ty, b.ty + 1):
        for tx in range(a.tx, b.tx + 1):
            k = Key(cell, level, tx, ty)
            if exists(k):
                out.append(k)
    return out


def parent_margin_px() -> int:
    """Parent pixels a tile's build reads beyond its own edge: fine.EDGE_PX + fine.HALO_PARENT_PX + the bicubic's 2."""
    from . import fine as ZF
    return int(np.ceil(ZF.EDGE_PX + ZF.HALO_PARENT_PX)) + 2


def parent_window(key: Key) -> tuple[float, float, float, float]:
    """The parent level's rectangle a tile's build reads (its square plus parent_margin_px parent pixels round it),
    clipped to the square."""
    p = parent(key)
    if p is None:
        raise ValueError("level 1 is built from the world")
    m = parent_margin_px() * res_km(p.level)
    x0, x1, y0, y1 = rect(key)
    return max(x0 - m, -HALF), min(x1 + m, HALF), max(y0 - m, -HALF), min(y1 + m, HALF)


def parent_sources(key: Key) -> list[Key]:
    """The parent-level tiles a tile's stitched parent window is cut from (1, 2 or 4; only those that exist: beyond them
    the window lies outside the cell by more than PAD_PX parent pixels and is edge-filled)."""
    p = parent(key)
    if p is None:
        return []
    return covering(key.cell, p.level, parent_window(key))


def tile_id(world_id: str, key: Key, seed: int = 1) -> str:
    """The id a tile is saved under (deterministic, as zoom ids: 6 hex)."""
    return hashlib.sha1(f"tile:{world_id}|{key}|{seed}".encode()).hexdigest()[:6]


def to_sphere(key: Key, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Unit vectors of plane points of the tile's cell."""
    return frame(key.cell).to_sphere(np.asarray(x, float), np.asarray(y, float))


def describe() -> list[dict]:
    """The ladder for the API and the viewer: level, res_km, tile_km, px, per_side."""
    return [{"level": k, "res_km": res_km(k), "tile_km": tile_km(k), "px": tile_px(k), "per_side": per_side(k)}
            for k in sorted(LEVELS)]
