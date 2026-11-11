"""Building the level-of-detail tiles (docs/review/zoom/lod-plan-v2.md 2.2, step 1; PW-1689).

A tile of level 2-4 (zoom/lod.py) is the fine pass (zoom/fine.py) run on its level's shared pixel lattice of its cell's
plane (lod.tile_frame), from its parent level stitched into one window (lod.parent_mosaic), with seam=True: its edge
fades to a surface that depends only on the place, its parent's rivers are imposed with their meander phase and their
discharge, so tiles built at different times, in any order, meet at their edges. Level 1 is the cell's section at 4 km
(regional.zoom(section=...)), built matched (zoom/match.py) to whichever neighbouring cells' level 1 is already built:
the neighbours' ground where they own it, exact at the owner line (the cell edge), blended over match.RAMP_KM inside
(lod-plan-v2.md 2.3, step 3; PW-1699). Level-1 builds of one world queue one at a time, so each sees every one before.
A tile (levels 2-4) near its cell's edge also fades, over its ramp, to ground carved once along that edge on blocks
keyed by place on the lattice of the cell whose level 1 the other matched (line_owner), from that cell's tiles of the
parent level (built first if they aren't: build_line_parents): both cells' tiles compute the same ground there, one on
its own pixels, the other resampled (PW-1705, PW-1708). Within ~2 ramps of a corner where three or four cells meet,
every one of them blends to one ground carved round the corner on its owner's lattice (owner_of, corner_block).

    build(world, key, sources, seed)       the tile (a zoom dict, as fine.build)
    edge_surface(world, key, sources, seed) the ground at its edges, carved on blocks keyed by place (PW-1694)
    line_surface(world, key, lines, seed)   the ground along its cell's edges and how far it fades to it (PW-1705)
    near_lines(key), line_owner(...)       the cell edges a tile fades to, and whose lattice carves them
    near_corners(key), owner_of(...)       the cell corners it blends at, and whose lattice carves them
    load_lines / build_line_parents         the owners' parent tiles those are carved from: loaded / built
    save(z, world_id, key, pmeta, seed)    an ordinary zoom directory under zooms/<lod.tile_id>, with a `tile` block
    find(world_id, key, seed)              the saved tile's (or level-1 section's) directory, or None
    load_sources(world_id, key, seed)      the parent tiles its build reads (lod.parent_sources), loaded
    built_neighbours(world_id, cell, seed) the ids of the neighbouring cells' level-1 sections already built
    build_level1(world_ref, cell, seed)    find or build-and-save a cell's level 1, matched to them
    tile(world_ref, key, seed)             find or build-and-save one tile whose parent tiles are built (and the
                                           owners' tiles along its cell's edges, built here if they aren't)
Seam diagnostics: edge_steps (siblings), cell_line, line_seam, resampled, line_rivers (two cells' level 1 at their edge).
"""
from __future__ import annotations

import json
import time
from functools import lru_cache
from pathlib import Path

import numpy as np

from .. import store as S
from .. import world as W
from . import fine as ZF
from . import lod as L
from . import regional as Z
from . import tiling as ZT

STRIP_PX = 32  # px: an edge block's half width (a strip centred on a tile's edge; its carving clear of its own edge)
LINE_PER_EDGE = 4000  # points along a cell's edge for its line (1 km apart on a 4,000 km cell)
LINE_LEVEL = 2  # the first level whose tiles fade to their cell's edges (PW-1705; levels 3-4 too, PW-1708)
CORNER_X = 1.5  # a corner's inner radius in line fades (ramp + 2 px): beyond it a point on one edge is clear of the others


def ramp_px(level: int) -> int:
    """Pixels over which a tile of this level fades to its edge surface (fine.build's ramp)."""
    rp, res = L.res_km(level - 1), L.res_km(level)
    return int(np.ceil(max(rp, 8 * res) / res - 1e-9))


def edge_blocks(key: L.Key) -> dict:
    """The blocks round a tile's edges, keyed by place: {name: (c0, c1, r0, r1)} on its level's lattice (columns from
    the square's west edge, rows from its north). A strip centred on each edge (2 x STRIP_PX wide, as long as the edge
    and STRIP_PX past each end) and a square centred on each corner (reaching a corner's fade further): a neighbour
    sharing an edge or a corner names the same rectangles."""
    n, h = L.tile_px(key.level), STRIP_PX
    hc = h + 2 * ramp_px(key.level) + 4
    x0, y0 = key.tx * n, key.ty * n
    x1, y1 = x0 + n, y0 + n
    out = {"w": (x0 - h, x0 + h, y0 - h, y1 + h), "e": (x1 - h, x1 + h, y0 - h, y1 + h),
           "n": (x0 - h, x1 + h, y0 - h, y0 + h), "s": (x0 - h, x1 + h, y1 - h, y1 + h)}
    for nm, (cx, cy) in (("nw", (x0, y0)), ("ne", (x1, y0)), ("sw", (x0, y1)), ("se", (x1, y1))):
        out[nm] = (cx - hc, cx + hc, cy - hc, cy + hc)
    return out


def _block_rect(level: int, b: tuple) -> tuple[float, float, float, float]:
    """A lattice rectangle (c0, c1, r0, r1) of a level as plane km (x0, x1, y0, y1)."""
    r = L.res_km(level)
    return -L.HALF + b[0] * r, -L.HALF + b[1] * r, L.HALF - b[3] * r, L.HALF - b[2] * r


def carve_block(world: dict, key: L.Key, sources: dict, b: tuple, seed: int = 1) -> np.ndarray:
    """The landscape pass's ground on the lattice rectangle b (rows x columns), from the parent window round it:
    the same arrays whichever tile asks (its parent window is cut by place, its pixels are the level's lattice)."""
    return carve(world, key, sources, b, seed)["hw"]


def carve(world: dict, key: L.Key, sources: dict, b: tuple, seed: int = 1) -> dict:
    """carve_block's whole result: fine.build(carve=True)'s {hw, courses (its one-pixel courses over the block and its
    halo, flat), hb, nbx, nby}."""
    r = _block_rect(key.level, b)
    pm = L.parent_mosaic(key, sources, r)
    fr = Z.PlaneFrame(L.frame(key.cell), 0.5 * (r[0] + r[1]), 0.5 * (r[2] + r[3]))
    lat, lon = Z._latlon(fr.c)
    res = L.res_km(key.level)
    w, h = b[1] - b[0], b[3] - b[2]
    return ZF.build(pm, world, lat, lon, max(w, h) * res, res, seed, log=lambda *_: None, frame=fr, seam=True,
                    shape=(w, h), carve=True)


def edge_surface(world: dict, key: L.Key, sources: dict, seed: int = 1) -> np.ndarray:
    """The ground a tile fades to at its edges, over its built area (fine.build's, halo included; flat; nan where
    unused): each pixel near one edge that edge's strip, near a corner the corner's block (blended between them by
    the distance to the corner), every block carved by the landscape pass (carve_block). A function of the place:
    the neighbour across an edge or a corner finds the same values there (docs/review/zoom/lod-plan-v2.md 2.2)."""
    n = L.tile_px(key.level)
    hb = ZF._halo_px(L.res_km(key.level - 1), L.res_km(key.level))
    nb = n + 2 * hb
    r_ = ramp_px(key.level)
    x0, y0 = key.tx * n, key.ty * n
    x1, y1 = x0 + n, y0 + n
    gc = x0 - hb + np.arange(nb) + 0.5  # (pixel centres on the lattice)
    gr = y0 - hb + np.arange(nb) + 0.5
    GC, GR = np.meshgrid(gc, gr)
    d = np.stack([GC - x0, x1 - GC, GR - y0, y1 - GR])  # (to the w, e, n, s edges; negative in the halo)
    near = np.argmin(d, axis=0)
    dmin = d.min(axis=0)
    cx = np.where(GC - x0 < x1 - GC, x0, x1)
    cy = np.where(GR - y0 < y1 - GR, y0, y1)
    cheb = np.maximum(np.abs(GC - cx), np.abs(GR - cy))
    wc = 1.0 - ZF.smoothstep(r_ + 2.0, 2.0 * r_ + 4.0, cheb)
    used = dmin < r_ + 1  # (the ramp and the halo)
    blocks = edge_blocks(key)
    E = np.full((nb, nb), np.nan)
    S = np.full((nb, nb), np.nan)
    C = np.full((nb, nb), np.nan)
    for nm, b in blocks.items():
        if len(nm) == 1:
            sel = used & (near == "wens".index(nm)) & (wc < 1)
        else:
            sel = used & (wc > 0) & (cx == (x0 if "w" in nm else x1)) & (cy == (y0 if "n" in nm else y1))
        if not sel.any():
            continue
        hw = carve_block(world, key, sources, b, seed)
        rr = (GR[sel] - 0.5).astype(int) - b[2]
        cc = (GC[sel] - 0.5).astype(int) - b[0]
        (S if len(nm) == 1 else C)[sel] = hw[rr, cc]
    E = np.where(wc >= 1, C, np.where(wc <= 0, S, wc * C + (1 - wc) * S))
    return np.where(used, E, np.nan).ravel()


@lru_cache(maxsize=None)
def _line(a: str, b: str) -> np.ndarray:
    """The edge two cells share, unit vectors in order along it (the same points whichever cell asks)."""
    lo, hi = sorted((a, b))
    return cell_line(lo, hi, LINE_PER_EDGE)


@lru_cache(maxsize=None)
def cell_lines(cell: str) -> tuple[str, ...]:
    """The neighbouring cells sharing an edge (not only a corner) with `cell`."""
    return tuple(b for b in ZT.section(cell, L.SQUARE_KM)["neighbours"] if len(_line(cell, b)) >= 2)


def _line_px(key: L.Key) -> int:
    """How far (the level's px) the line's fade reaches inside the cell: the edge ramp and a pixel and a half."""
    return ramp_px(key.level) + 2


def _built_xy(key: L.Key) -> tuple[np.ndarray, np.ndarray, int]:
    """The plane km (x, y) of a tile's built area (fine.build's: its halo included), row-major; and its side in px."""
    n = L.tile_px(key.level)
    hb = ZF._halo_px(L.res_km(key.level - 1), L.res_km(key.level))
    x, y = L.lattice(key, hb)
    return x, y, n + 2 * hb


def near_lines(key: L.Key) -> list[str]:
    """The cells whose shared edge with key's cell comes within the line's fade of the tile's built area (levels 2-4)."""
    if key.level < LINE_LEVEL:
        return []
    x0, x1, y0, y1 = L.rect(key)
    res = L.res_km(key.level)
    m = (ZF._halo_px(L.res_km(key.level - 1), res) + _line_px(key) + 2) * res
    out = []
    for b in cell_lines(key.cell):
        x, y = L.frame(key.cell).to_plane(_line(key.cell, b))
        if ((x > x0 - m) & (x < x1 + m) & (y > y0 - m) & (y < y1 + m)).any():
            out.append(b)
    return out


@lru_cache(maxsize=None)
def cell_corners(cell: str) -> tuple[tuple[tuple[str, ...], tuple[float, float, float]], ...]:
    """The corners of a cell where three or four cells meet: ((the cells, sorted), the point as a unit vector). The
    point is the corner of the first of those cells by name (ZT._boundary's vertex), so every one of them names the
    same floats."""
    n = ZT.choose_n(L.SQUARE_KM, 190.0)
    out = []
    for P in ZT._boundary(*_fij(cell), n, per_edge=1):
        t1 = np.cross(P, [0.0, 0.0, 1.0] if abs(P[2]) < 0.9 else [1.0, 0.0, 0.0])
        t1 /= np.linalg.norm(t1)
        t2 = np.cross(P, t1)
        ang = np.linspace(0.0, 2 * np.pi, 24, endpoint=False)
        Q = P + 2e-4 * (np.cos(ang)[:, None] * t1 + np.sin(ang)[:, None] * t2)  # (~1.3 km round it)
        cells = tuple(sorted(set(_cells_of(Q).tolist())))
        if len(cells) < 3:
            continue
        first = ZT._boundary(*_fij(cells[0]), n, per_edge=1)
        out.append((cells, tuple(float(v) for v in first[np.argmax(first @ P)])))
    return tuple(out)


def _fij(cell: str) -> tuple[int, int, int]:
    s = ZT.section(cell, L.SQUARE_KM)
    return list(ZT.FACES).index(s["face"]), s["i"], s["j"]


def _corner_px(level: int) -> tuple[float, float]:
    """(inner, outer) radius in the level's px of a corner's ground round a corner: every cell meeting there blends to
    it alone within the inner (far enough out that a point on one edge is beyond the line's fade of the others), to
    nothing at the outer."""
    r0 = CORNER_X * (ramp_px(level) + 2.0)
    return r0, r0 + ramp_px(level) + 2.0


def near_corners(key: L.Key) -> list[tuple[str, ...]]:
    """The corners of key's cell (cell_corners) whose ground reaches the tile's built area (levels 2-4)."""
    if key.level < LINE_LEVEL:
        return []
    x0, x1, y0, y1 = L.rect(key)
    res = L.res_km(key.level)
    m = (ZF._halo_px(L.res_km(key.level - 1), res) + _corner_px(key.level)[1] + 2) * res
    out = []
    for cells, P in cell_corners(key.cell):
        x, y = L.frame(key.cell).to_plane(np.array([P]))
        if x0 - m < x[0] < x1 + m and y0 - m < y[0] < y1 + m:
            out.append(cells)
    return out


def corner_block(owner: str, cells: tuple[str, ...], level: int) -> tuple[int, int, int, int]:
    """The block a corner's ground is carved on: a square on owner's lattice of a level round the corner's pixel,
    reaching the corner's outer radius and STRIP_PX past it (a function of the corner and the owner only)."""
    P = dict(cell_corners(cells[0]))[cells]
    res = L.res_km(level)
    x, y = L.frame(owner).to_plane(np.array([P]))
    c, r = int(np.floor((x[0] + L.HALF) / res)), int(np.floor((L.HALF - y[0]) / res))
    h = int(np.ceil(_corner_px(level)[1])) + STRIP_PX + 4
    return c - h, c + h + 1, r - h, r + h + 1


def _polyline_dist(px: np.ndarray, py: np.ndarray, x: np.ndarray, y: np.ndarray, reach: float) -> np.ndarray:
    """km from each point (px, py) to the polyline (x, y) (inf beyond `reach` of every vertex's segment)."""
    d = np.full(len(px), np.inf)
    ax, ay, bx, by = x[:-1], y[:-1], x[1:], y[1:]
    lo_x, hi_x, lo_y, hi_y = px.min() - reach, px.max() + reach, py.min() - reach, py.max() + reach
    for k in np.flatnonzero((np.maximum(ax, bx) > lo_x) & (np.minimum(ax, bx) < hi_x) & (np.maximum(ay, by) > lo_y)
                            & (np.minimum(ay, by) < hi_y)):
        dx, dy = bx[k] - ax[k], by[k] - ay[k]
        t = np.clip(((px - ax[k]) * dx + (py - ay[k]) * dy) / max(dx * dx + dy * dy, 1e-12), 0.0, 1.0)
        d = np.minimum(d, np.hypot(px - ax[k] - t * dx, py - ay[k] - t * dy))
    return d


def line_blocks(owner: str, other: str, level: int) -> tuple[bool, int, list[tuple[int, tuple]]]:
    """The blocks the ground along two cells' shared edge is carved on, on `owner`'s lattice of a level: (along rows?,
    the blocks' period in px, [(j, (c0, c1, r0, r1))]): block j holds the line's stretch in owner's tiles j (rows j n ..
    (j + 1) n of a line running down the lattice, else columns), STRIP_PX + the ramp past it on every side. A function
    of the two cells and the owner only: both cells' tiles name the same rectangles."""
    n, res = L.tile_px(level), L.res_km(level)
    x, y = L.frame(owner).to_plane(_line(owner, other))
    col, row = (x + L.HALF) / res, (L.HALF - y) / res
    rows = np.ptp(row) >= np.ptp(col)
    along, across = (row, col) if rows else (col, row)
    h = STRIP_PX + ramp_px(level) + 4
    lo, hi = int(np.floor(along.min())) - h, int(np.ceil(along.max())) + h
    out = []
    for j in range(int(np.floor(along.min() / n)), int(np.floor(along.max() / n)) + 1):
        a0, a1 = max(j * n - h, lo), min((j + 1) * n + h, hi)
        sel = (along >= a0 - 2) & (along <= a1 + 2)
        if not sel.any():
            continue
        b0, b1 = int(np.floor(across[sel].min())) - h, int(np.ceil(across[sel].max())) + h
        out.append((j, (b0, b1, a0, a1) if rows else (a0, a1, b0, b1)))
    return rows, n, out


def _owner_px(key: L.Key, owner: str, X: np.ndarray, Y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Plane points (km) of key's cell as fractional (column, row) on owner's lattice of key's level (pixel centres at
    integers; on key's own cell, exactly its pixels' indices)."""
    res = L.res_km(key.level)
    if owner != key.cell:
        X, Y = L.frame(owner).to_plane(L.frame(key.cell).to_sphere(X, Y))
    return (X + L.HALF) / res - 0.5, (L.HALF - Y) / res - 0.5


def _bilinear(hw: np.ndarray, b: tuple, ck: np.ndarray, rk: np.ndarray, what: str) -> np.ndarray:
    """A carved block hw (on lattice rectangle b) read at owner-lattice (column, row) points."""
    fr, fc = rk - b[2], ck - b[0]
    if fr.min() < 0 or fc.min() < 0 or fr.max() > hw.shape[0] - 1 or fc.max() > hw.shape[1] - 1:
        raise ValueError(f"{what}: the block doesn't cover the tile's ramp")
    r0 = np.minimum(np.floor(fr).astype(int), hw.shape[0] - 2)
    c0 = np.minimum(np.floor(fc).astype(int), hw.shape[1] - 2)
    tr, tc = fr - r0, fc - c0
    return (hw[r0, c0] * (1 - tr) * (1 - tc) + hw[r0, c0 + 1] * (1 - tr) * tc + hw[r0 + 1, c0] * tr * (1 - tc)
            + hw[r0 + 1, c0 + 1] * tr * tc)


def _line_plan(key: L.Key, other: str, owner: str) -> tuple | None:
    """Where a tile fades to the ground along its cell's edge with `other` (carved on owner's lattice): (the built
    area's pixels within the fade, their fade weight, their (column, row) on owner's lattice, [(block, its weight
    along the line at those pixels)] of line_blocks it reads), or None if the edge's fade misses the tile."""
    res, r_ = L.res_km(key.level), ramp_px(key.level)
    X, Y, _ = _built_xy(key)
    lx, ly = L.frame(key.cell).to_plane(_line(key.cell, other))
    d = _polyline_dist(X, Y, lx, ly, (_line_px(key) + 2) * res)
    a = 1.0 - ZF.smoothstep(1.5 * res, (r_ + 1.5) * res, d)
    sel = np.flatnonzero(a > 0)
    if not len(sel):
        return None
    ck, rk = _owner_px(key, owner, X[sel], Y[sel])
    rows, n, blocks = line_blocks(owner, other if owner == key.cell else key.cell, key.level)
    along = rk if rows else ck
    bz = r_ + 2.0
    out = []
    for i, (j, b) in enumerate(blocks):
        up = 1.0 if i == 0 else ZF.smoothstep(j * n - 0.5 - bz, j * n - 0.5 + bz, along)
        down = 0.0 if i == len(blocks) - 1 else ZF.smoothstep((j + 1) * n - 0.5 - bz, (j + 1) * n - 0.5 + bz, along)
        w = up * (1.0 - down)
        if (w > 0).any():
            out.append((b, w, j))
    return sel, a[sel], ck, rk, out


def _corner_plan(key: L.Key, cells: tuple[str, ...], owner: str) -> tuple | None:
    """Where a tile blends to a corner's ground (carved on owner's lattice, corner_block): (the built area's pixels
    within the corner's outer radius, their weight, their (column, row) on owner's lattice, the block), or None."""
    res = L.res_km(key.level)
    X, Y, _ = _built_xy(key)
    x, y = L.frame(key.cell).to_plane(np.array([dict(cell_corners(cells[0]))[cells]]))
    r0, r1 = _corner_px(key.level)
    wc = 1.0 - ZF.smoothstep(r0 * res, r1 * res, np.hypot(X - x[0], Y - y[0]))
    sel = np.flatnonzero(wc > 0)
    if not len(sel):
        return None
    ck, rk = _owner_px(key, owner, X[sel], Y[sel])
    return sel, wc[sel], ck, rk, corner_block(owner, cells, key.level)


def _okey(owner: str, level: int, osrc: dict) -> L.Key:
    """A tile of owner's level whose parent is among the sources (parent_mosaic's key for a block: only its level and
    cell count once the window is given)."""
    k = min(osrc)
    if k.level == min(L.LEVELS):
        return L.Key(owner, level, 0, 0)
    br = L.branching(k.level)
    return L.Key(owner, level, k.tx * br, k.ty * br)


def line_surface(world: dict, key: L.Key, lines: dict, seed: int = 1, log=print, corners: dict | None = None
                 ) -> tuple | None:
    """The ground a tile (levels 2-4) fades to along its cell's edges, and how far: (surface, weight, courses) over
    its built area (flat, as fine.build's `line`), or None if no edge is near; courses: the blocks' one-pixel courses
    on the tile's pixels and which pixels lie beyond the line (_block_courses, _beyond), the courses every tile there
    lays (PW-1713). lines: {other cell: (owner cell, owner's parent-
    level {Key: (meta, layers)} under the blocks)}; corners: {cells meeting at a corner: (owner, its sources)}. Each
    edge's ground is carved on line_blocks of the owner's lattice from the owner's parent level (carve_block), blended
    between blocks over the ramp, and read here at the tile's pixels (bilinear; on the owner's own pixels, exact); the
    weight is 1 within a pixel and a half of the edge (both sides) and 0 a ramp away. Near a corner every cell meeting
    there blends to one ground carved round the corner on its owner's lattice (corner_block): alone within the inner
    radius (_corner_px), where a point on one edge is clear of the others' fades, so every cell's surface is the same
    function of the place there. Both cells' tiles meet that ground at the edge (lod-plan-v2.md 2.3; PW-1705/1708)."""
    if not lines:
        return None
    _, _, nb = _built_xy(key)
    num, den, wmax = np.zeros(nb * nb), np.zeros(nb * nb), np.zeros(nb * nb)
    pieces, far = [], np.zeros(nb * nb, bool)
    for other, (owner, osrc) in sorted(lines.items()):
        plan = _line_plan(key, other, owner)
        if plan is None:
            continue
        sel, a, ck, rk, blocks = plan
        far[sel] |= _beyond(key, other, sel)
        okey = _okey(owner, key.level, osrc)
        t0 = time.time()
        val = np.zeros(len(sel))
        rows, n, _ = line_blocks(owner, other if owner == key.cell else key.cell, key.level)
        for b, w, j in blocks:
            use = w > 0
            cb = carve(world, okey, osrc, b, seed)
            val[use] += w[use] * _bilinear(cb["hw"], b, ck[use], rk[use], f"cell line {key.cell}|{other}")
            pieces.append(_block_courses(key, owner, b, cb, rows, n, j))
        log(f"  cell line {key.cell}|{other} on {owner}'s lattice: {len(sel)} px, {len(blocks)} blocks "
            f"[{time.time() - t0:.1f}s]")
        num[sel] += a * val
        den[sel] += a
        wmax[sel] = np.maximum(wmax[sel], a)
    if not (wmax > 0).any():
        return None
    surf = np.where(den > 0, num / np.maximum(den, 1e-12), np.nan)
    for cells, (owner, osrc) in sorted((corners or {}).items()):
        plan = _corner_plan(key, cells, owner)
        if plan is None:
            continue
        sel, wc, ck, rk, b = plan
        keep = wmax[sel] > 0  # (only where the tile fades to the line at all)
        if not keep.any():
            continue
        sel, wc, ck, rk = sel[keep], wc[keep], ck[keep], rk[keep]
        t0 = time.time()
        g = _bilinear(carve_block(world, _okey(owner, key.level, osrc), osrc, b, seed), b, ck, rk,
                      f"corner {'+'.join(cells)}")
        s_ = surf[sel]
        surf[sel] = np.where(np.isnan(s_), g, wc * g + (1.0 - wc) * s_)
        log(f"  corner {'+'.join(cells)} on {owner}'s lattice: {len(sel)} px [{time.time() - t0:.1f}s]")
    courses = {k: np.concatenate([p[k] for p in pieces]) for k in pieces[0]}
    return surf, wmax, {**courses, "far": far}


def _beyond(key: L.Key, other: str, sel: np.ndarray) -> np.ndarray:
    """Whether each of the built area's pixels sel lies beyond key's cell's edge with `other` (on the far side of the
    nearest stretch of the line from the cell's centre, the plane's origin)."""
    X, Y, _ = _built_xy(key)
    x, y = X[sel], Y[sel]
    lx, ly = L.frame(key.cell).to_plane(_line(key.cell, other))
    m = (_line_px(key) + 4) * L.res_km(key.level)
    k = np.flatnonzero((lx > x.min() - m) & (lx < x.max() + m) & (ly > y.min() - m) & (ly < y.max() + m))
    k = np.unique(np.clip(np.r_[k - 1, k], 0, len(lx) - 2))
    if not len(k):
        return np.zeros(len(sel), bool)
    best, side = np.full(len(sel), np.inf), np.zeros(len(sel), bool)
    for i in k:
        dx, dy = lx[i + 1] - lx[i], ly[i + 1] - ly[i]
        t = np.clip(((x - lx[i]) * dx + (y - ly[i]) * dy) / max(dx * dx + dy * dy, 1e-12), 0.0, 1.0)
        d = np.hypot(x - lx[i] - t * dx, y - ly[i] - t * dy)
        s = (dx * (y - ly[i]) - dy * (x - lx[i])) * (dx * (0.0 - ly[i]) - dy * (0.0 - lx[i])) < 0
        side = np.where(d < best, s, side)
        best = np.minimum(best, d)
    return side


def _to_tile(key: L.Key, owner: str, col: np.ndarray, row: np.ndarray) -> np.ndarray:
    """Pixels (column, row) of owner's lattice of key's level as flat indices of key's built area (-1 off it)."""
    res = L.res_km(key.level)
    x, y = -L.HALF + (col + 0.5) * res, L.HALF - (row + 0.5) * res
    if owner != key.cell:
        x, y = L.frame(key.cell).to_plane(L.frame(owner).to_sphere(x, y))
    hb = ZF._halo_px(L.res_km(key.level - 1), res)
    nb = L.tile_px(key.level) + 2 * hb
    x0, _, _, y1 = L.rect(key)
    tc = np.floor((x - x0) / res + 1e-9).astype(np.int64) + hb
    tr = np.floor((y1 - y) / res + 1e-9).astype(np.int64) + hb
    return np.where((tc >= 0) & (tc < nb) & (tr >= 0) & (tr < nb), tr * nb + tc, -1)


def _block_courses(key: L.Key, owner: str, b: tuple, cb: dict, rows: bool, n: int, j: int) -> dict:
    """A line block's one-pixel courses in its own stretch of the line (owner's tiles j, as line_blocks), moved onto
    key's built area: {px, rec, bed, q, a, qa, aa, phase} (rec: the next pixel down, flat; -1 none). A pixel's next
    pixel is the first one down its course on another of key's pixels; a step of more than a pixel between the two
    lattices is filled in."""
    cc, hb, nbx = cb["courses"], cb["hb"], cb["nbx"]
    keys = ("bed", "q", "a", "qa", "aa", "phase")
    empty = {"px": np.zeros(0, np.int64), "rec": np.zeros(0, np.int64), **{k: np.zeros(0) for k in keys}}
    if cc is None or not cc["course"].any():
        return empty
    idx = np.flatnonzero(cc["course"])
    r, c = np.divmod(idx, nbx)
    row, col = b[2] - hb + r, b[0] - hb + c
    along = row if rows else col
    tp = np.full(len(cc["course"]), -1, np.int64)
    tp[idx] = _to_tile(key, owner, col, row)
    mine = idx[(along >= j * n) & (along < (j + 1) * n) & (tp[idx] >= 0)]
    if not len(mine):
        return empty
    rec = cc["rec"]
    nxt = rec[mine].copy()
    for _ in range(4):  # (two of the block's pixels on one of key's: on down)
        same = (nxt >= 0) & (tp[np.maximum(nxt, 0)] == tp[mine])
        if not same.any():
            break
        nxt = np.where(same, rec[np.maximum(nxt, 0)], nxt)
    rt = np.where(nxt >= 0, tp[np.maximum(nxt, 0)], -1)
    rt = np.where(rt == tp[mine], -1, rt)
    out = {"px": list(tp[mine]), "rec": list(rt), **{k: list(cc[k][mine]) for k in keys}}
    nb = L.tile_px(key.level) + 2 * ZF._halo_px(L.res_km(key.level - 1), L.res_km(key.level))
    for m in np.flatnonzero(rt >= 0):  # (gaps: a step of more than a pixel between the two lattices)
        (ra, ca), (rz, cz) = divmod(int(tp[mine[m]]), nb), divmod(int(rt[m]), nb)
        s = max(abs(rz - ra), abs(cz - ca))
        if s <= 1:
            continue
        steps = [int(round(ra + (rz - ra) * t / s)) * nb + int(round(ca + (cz - ca) * t / s)) for t in range(1, s)]
        out["rec"][m] = steps[0]
        for t, k in enumerate(steps):
            out["px"].append(k)
            out["rec"].append(steps[t + 1] if t + 1 < len(steps) else int(rt[m]))
            for kk in keys:
                out[kk].append(cc[kk][mine[m]])
    return {"px": np.asarray(out["px"], np.int64), "rec": np.asarray(out["rec"], np.int64),
            **{k: np.asarray(out[k], float) for k in keys}}


def owner_of(world_id: str, cells, seed: int = 1) -> str:
    """Whose lattice and level 1 carve the ground cells meet on (an edge, or a corner): the earliest built of them,
    i.e. a built one whose level 1 was matched to none of the others (the later ones were matched to it); the first by
    name if several were built alone. The same answer from any of them once the earliest is built."""
    dirs = {c: _section_dir(world_id, c, seed) for c in sorted(set(cells))}
    built = {c: d for c, d in dirs.items() if d is not None}
    if not built:
        raise ValueError(f"none of {', '.join(sorted(dirs))} has its level 1 built")
    ids = {d.name for d in built.values()}

    def matched(d):
        return set(json.loads((d / "zoom.json").read_text()).get("matched_to") or [])
    roots = [c for c, d in built.items() if not (matched(d) & (ids - {d.name}))]
    return min(roots or built)


def line_owner(world_id: str, a: str, b: str, seed: int = 1) -> str:
    """Whose lattice and level 1 carve the ground along cells a and b's shared edge: the one the other's level 1 was
    matched to (the earlier); if only one is built, that one (the other will be matched to it); if both were built
    alone, the first by name (owner_of)."""
    return owner_of(world_id, (a, b), seed)


def _with_phase(sources: dict, seed: int) -> dict:
    """A level-1 section's sources with its whole network's meander phase (every level-2 tile of it reads the same)."""
    out = dict(sources)
    for k, (m1, l1) in sources.items():
        if k.level == min(L.LEVELS) and "river_phase" not in l1:
            out[k] = (m1, {**l1, "river_phase": ZF.network_phase(m1, l1, seed)})
    return out


def _block_parents(owner: str, level: int, b: tuple) -> list[L.Key]:
    """owner's parent-level tiles a block of a level is carved from (lod.parent_mosaic's window round it)."""
    if level - 1 == min(L.LEVELS):
        return [L.Key(owner, level - 1, 0, 0)]
    rp = L.res_km(level - 1)
    c0, c1, r0, r1 = L._window_px(L.Key(owner, level, 0, 0), _block_rect(level, b))
    return L.covering(owner, level - 1, (-L.HALF + c0 * rp, -L.HALF + c1 * rp, L.HALF - r1 * rp, L.HALF - r0 * rp))


def _cell_edge_parents(world_id: str, key: L.Key, seed: int = 1) -> tuple[dict, dict]:
    """({other cell: (owner, [parent-level keys])}, {corner cells: (owner, [keys])}): the owners' tiles of key's parent
    level the ground along its cell's edges and corners is carved from."""
    lines, corners = {}, {}
    for b in near_lines(key):
        owner = line_owner(world_id, key.cell, b, seed)
        plan = _line_plan(key, b, owner)
        if plan is not None:
            lines[b] = (owner, sorted({k for bl in plan[4] for k in _block_parents(owner, key.level, bl[0])}))
    if lines:
        for cells in near_corners(key):
            owner = owner_of(world_id, cells, seed)
            plan = _corner_plan(key, cells, owner)
            if plan is not None:
                corners[cells] = (owner, _block_parents(owner, key.level, plan[4]))
    return lines, corners


def build_line_parents(world_ref: str, key: L.Key, seed: int = 1, log=print) -> list[L.Key]:
    """Builds (tile) the owners' parent-level tiles the ground along a tile's cell edges and corners is carved from that
    aren't built yet (levels 3-4: the other cell's tiles along the line need not have been wanted). Returns them."""
    wid = Z.find_world(world_ref).stem
    lines, corners = _cell_edge_parents(wid, key, seed)
    need = sorted({k for _, ks in (*lines.values(), *corners.values()) for k in ks if find(wid, k, seed) is None})
    for k in need:
        log(f"  {key} needs {k} along its cell's edge: building it")
        tile(world_ref, k, seed, log=log)
    return need


def load_lines(world_id: str, key: L.Key, sources: dict, seed: int = 1) -> tuple[dict, dict]:
    """({other cell: (owner, owner's parent-level sources under the blocks)}, {corner cells: (owner, sources)}) of the
    cell edges and corners a tile (levels 2-4) fades to; reused from `sources` where they are the tile's own. The
    owners' tiles must be built (build_line_parents)."""
    cache = dict(sources)

    def load(keys):
        out = {}
        for k in keys:
            if k not in cache:
                d = find(world_id, k, seed)
                if d is None:
                    raise ValueError(f"tile {key} needs {k} along its cell's edge, which is not built")
                cache[k] = Z.load(d, decode=True)
            out[k] = cache[k]
        return out
    lines, corners = _cell_edge_parents(world_id, key, seed)
    return ({b: (o, load(ks)) for b, (o, ks) in lines.items()}, {c: (o, load(ks)) for c, (o, ks) in corners.items()})


def build(world: dict, key: L.Key, sources: dict, seed: int = 1, log=print, lines: dict | None = None,
          corners: dict | None = None) -> dict:
    """The tile `key` from its parent tiles `sources` ({Key: (meta, decoded layers)}, load_sources), faded at its
    cell's edges and corners to the ground along them (`lines`, `corners`: load_lines). Deterministic: the same
    sources give the same arrays."""
    if key.level == min(L.LEVELS):
        raise ValueError("level 1 is the cell's section: regional.zoom(section=...)")
    # (a section has no river_phase: its whole network's, so every level-2 tile of the cell reads the same)
    sources = _with_phase(sources, seed)

    def phased(o, s):
        return sources if o == key.cell and key.level == LINE_LEVEL else _with_phase(s, seed)
    lines = {b: (o, phased(o, s)) for b, (o, s) in (lines or {}).items()}
    corners = {c: (o, phased(o, s)) for c, (o, s) in (corners or {}).items()}
    pm = L.parent_mosaic(key, sources)
    fr = L.tile_frame(key)
    lat, lon = Z._latlon(fr.c)
    t0 = time.time()
    edge = edge_surface(world, key, sources, seed)
    log(f"  edge blocks carved [{time.time() - t0:.1f}s]")
    t0 = time.time()
    line = line_surface(world, key, lines, seed, log=log, corners=corners)
    if line is not None:
        log(f"  cell edges carved [{time.time() - t0:.1f}s]")
    z = ZF.build(pm, world, lat, lon, L.tile_km(key.level), L.res_km(key.level), seed, log=log, frame=fr, seam=True,
                 edge=edge, line=line)
    z["parent_meta"] = pm[0]  # (what save() records the tile was built from)
    z["cell_lines"] = {**{b: o for b, (o, _) in sorted(lines.items())},
                       **{"+".join(c): o for c, (o, _) in sorted(corners.items())}}
    return z


def tile_block(world_id: str, key: L.Key, seed: int, pmeta: dict, cell_lines: dict | None = None) -> dict:
    """zoom.json's `tile` block: the tile's address, its rectangle in the cell's plane and what it was built from
    (cell_lines: {neighbouring cell: the owner whose lattice carved their shared edge's ground})."""
    return {**({"cell_lines": cell_lines} if cell_lines else {}), "world": world_id, "cell": key.cell, "level": key.level, "tx": key.tx, "ty": key.ty, "key": str(key),
            "seed": seed, "rect_km": [round(v, 6) for v in L.rect(key)], "res_km": L.res_km(key.level),
            "px": L.tile_px(key.level), "parent": str(L.parent(key)), "parent_id": pmeta["id"],
            "parent_sources": (pmeta.get("mosaic") or {}).get("sources", [])}


def save(z: dict, world_id: str, key: L.Key, seed: int = 1) -> Path:
    """Writes the tile as a zoom directory (zooms/<lod.tile_id>): zoom.load, the zoom page and fine zooms read it."""
    pmeta = z["parent_meta"]
    lat, lon = Z._latlon(z["frame"].c)
    zid = L.tile_id(world_id, key, seed)
    base = str(pmeta.get("name", world_id)).split(":")[0]
    name = f"{base}: tile {key} ({z['size_km']:g} km @ {z['res'] * 1000:g} m)"
    return ZF.save(z, pmeta, lat, lon, z["size_km"], z["res"], seed, zid=zid, name=name,
                   extra={"tile": tile_block(world_id, key, seed, pmeta, z.get("cell_lines"))})


SECTIONS_FILE = "sections.json"  # in the zoom store (a world's tile store): {"<world>/<cell>/<seed>": zoom id}


def _sections() -> dict:
    try:
        return json.loads((S.zooms_dir() / SECTIONS_FILE).read_text())
    except (OSError, ValueError):
        return {}


def _remember_section(world_id: str, cell: str, seed: int, zid: str) -> None:
    """Records a cell's level-1 section in the store's sections.json (PW-1707), under a lock (read, add, replace)."""
    with S.lock(S.zooms_dir(), "lod-sections"):
        m = _sections()
        k = f"{world_id}/{cell}/{seed}"
        if m.get(k) != zid:
            S.write_json(S.zooms_dir() / SECTIONS_FILE, {**m, k: zid})


def _section_dir(world_id: str, cell: str, seed: int) -> Path | None:
    """The cell's level-1 section of this world: looked up in the store's sections.json (written by build_level1);
    else found by scanning the store (a zoom with section == cell at level 1's res_km, newest first) and recorded."""
    zid = _sections().get(f"{world_id}/{cell}/{seed}")
    if zid and (S.zooms_dir() / zid / "zoom.json").exists():
        return S.zooms_dir() / zid
    d = _scan_section(world_id, cell, seed)
    if d is not None:
        _remember_section(world_id, cell, seed, d.name)
    return d


def _scan_section(world_id: str, cell: str, seed: int) -> Path | None:
    best = None
    for d in sorted(S.zooms_dir().glob("*/zoom.json")):
        try:
            m = json.loads(d.read_text())
        except (OSError, ValueError):
            continue
        if (m.get("section") == cell and abs(float(m.get("res_km", 0)) - L.res_km(1)) < 1e-9
                and (m.get("source_world") or {}).get("id") == world_id and int(m.get("seed", 1)) == seed):
            if best is None or m.get("created", "") > best[0]:
                best = (m.get("created", ""), d.parent)
    return None if best is None else best[1]


def find(world_id: str, key: L.Key, seed: int = 1) -> Path | None:
    if key.level == min(L.LEVELS):
        return _section_dir(world_id, key.cell, seed)
    d = S.zooms_dir() / L.tile_id(world_id, key, seed)
    return d if (d / "zoom.json").exists() else None


def built_neighbours(world_id: str, cell: str, seed: int = 1) -> list[str]:
    """The ids of the level-1 sections already built of the cells sharing an edge or a corner with `cell` (tiling's
    neighbours), in the neighbours' order."""
    out = []
    for c in ZT.section(cell, L.SQUARE_KM)["neighbours"]:
        d = _section_dir(world_id, c, seed)
        if d is not None:
            out.append(d.name)
    return out


def build_level1(world_ref: str, cell: str, seed: int = 1, log=print) -> Path:
    """A cell's level 1 (its 4 km section): found, or built matched to the neighbouring cells' level 1 already built
    (regional.zoom(section=, match=), zoom/match.py) and saved. The order the cells are built in decides who matches
    whom: one lock per world and seed queues level-1 builds, so a cell built after a neighbour always sees it (two
    built side by side would each be built alone and disagree at their edge)."""
    wpath = Z.find_world(world_ref)
    wid = wpath.stem
    with S.lock(S.zooms_dir(), f"lod-level1-{wid}-{seed}"):
        d = _section_dir(wid, cell, seed)
        if d is not None:
            return d
        nb = built_neighbours(wid, cell, seed)
        if nb:
            log(f"level 1 of {cell}: matched to {', '.join(nb)}")
        d = Z.zoom(str(wpath), None, None, L.SQUARE_KM, L.res_km(1), seed, log=log, section=cell, match=tuple(nb))
        _remember_section(wid, cell, seed, Path(d).name)
        return d


def load_sources(world_id: str, key: L.Key, seed: int = 1) -> dict:
    """{parent-level Key: (meta, decoded layers)} of the tiles the build of `key` reads; raises if one isn't built."""
    out = {}
    for k in L.parent_sources(key):
        d = find(world_id, k, seed)
        if d is None:
            raise ValueError(f"tile {key} needs {k}, which is not built")
        out[k] = Z.load(d, decode=True)
    return out


def tile(world_ref: str, key: L.Key | str, seed: int = 1, log=print) -> Path:
    """The saved tile `key` of a world: found, or built from its parent tiles (which must be built) and saved. Level 1
    (the cell's section) is built from the world, matched to its built neighbours (build_level1)."""
    key = L.Key.parse(key) if isinstance(key, str) else key
    if key.level == min(L.LEVELS):
        return build_level1(world_ref, key.cell, seed, log=log)
    wpath = Z.find_world(world_ref)
    wid = wpath.stem
    d = find(wid, key, seed)
    if d is not None:
        return d
    if not L.exists(key):
        raise ValueError(f"tile {key} is not part of cell {key.cell}'s pyramid")
    t0 = time.time()
    build_line_parents(str(wpath), key, seed, log=log)  # (first: nothing of this tile's is loaded meanwhile)
    src = load_sources(wid, key, seed)
    lines, corners = load_lines(wid, key, src, seed)
    world = W.load(wpath)
    z = build(world, key, src, seed, log=log, lines=lines, corners=corners)
    with S.lock(S.zooms_dir(), L.tile_id(wid, key, seed)):
        out = save(z, wid, key, seed)
    # (its parent's deposits that lie inside it, at their place: each deposit in the one tile holding its point, the
    # parent tile's or the section's own; resources.add_to_zoom, PW-618/1695)
    Z.add_deposits(out, world)
    log(f"tile {key}: {out.name} [{time.time() - t0:.1f}s]")
    return out


def edge_steps(a: np.ndarray, b: np.ndarray, axis: int, band: tuple[int, int] | None = None
               ) -> tuple[np.ndarray, np.ndarray]:
    """Two sibling tiles' layer a (west or north) and b (east or south) meeting along `axis` (1: a's east edge on b's
    west, 0: a's south edge on b's north): (|steps across the shared edge|, |steps between neighbouring pixels inside
    both, in the same direction|): the seam test (lod-plan-v2.md 2.2's done-when). band (lo, hi): the inside steps only
    lo..hi px from the shared edge, on the same lines across it (the same ground as the edge's); else all of both."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if axis == 0:  # (as axis 1, transposed: lines across the edge are columns)
        a, b = a.T, b.T
    across = np.abs(b[:, 0] - a[:, -1])
    da, db = np.abs(np.diff(a, axis=1)), np.abs(np.diff(b, axis=1))  # (da[:, k]: a's step k -> k + 1)
    if band is not None:
        lo, hi = band
        n = a.shape[1]
        da, db = da[:, n - 1 - hi:n - 1 - lo], db[:, lo:hi]
    return across, np.concatenate([da.ravel(), db.ravel()])


def _cells_of(P: np.ndarray) -> np.ndarray:
    """The tiling cell id of each unit vector."""
    f, i, j = ZT.locate(P / np.linalg.norm(P, axis=1, keepdims=True), ZT.choose_n(L.SQUARE_KM, 190.0))
    names = np.array(list(ZT.FACES))
    return np.char.add(np.char.add(np.char.add(names[f], "."), i.astype(str)), np.char.add(".", j.astype(str)))


def cell_line(a: str, b: str, per_edge: int = 1000) -> np.ndarray:
    """Points (unit vectors, (m, 3)) on the edge cells a and b share: the owner line where their level 1 meet (the
    seam test of step 3, lod-plan-v2.md 2.3). Empty if they share no edge."""
    s = ZT.section(a, L.SQUARE_KM)
    n = ZT.choose_n(L.SQUARE_KM, 190.0)
    P = ZT._boundary(list(ZT.FACES).index(s["face"]), s["i"], s["j"], n, per_edge)
    d = P - L.frame(a).c
    keep = (_cells_of(P + 1e-4 * d) == b) & (_cells_of(P - 1e-4 * d) == a)
    return P[keep]


def line_seam(sa: dict, sb: dict, P: np.ndarray) -> dict:
    """Two level-1 sections (match.sources / match.source_of dicts) at the points P of their shared line: |a - b| of
    their ground there (bilinear; a lake at its surface), over the points both call land and both cover."""
    from . import match as ZM
    ha, _, la, _, _, ina = ZM._sample(sa, P, sa["res"])
    hb, _, lb, _, _, inb = ZM._sample(sb, P, sb["res"])
    d = np.abs(ha - hb)[la & lb & (ina > 0) & (inb > 0)]
    if not len(d):
        return {"n": 0, "median": np.nan, "p90": np.nan, "max": np.nan, "d": d}
    return {"n": len(d), "median": float(np.median(d)), "p90": float(np.percentile(d, 90)), "max": float(d.max()),
            "d": d}


def resampled(sa: dict, sb: dict) -> dict:
    """sb with sa's ground (bilinear) at every pixel of sb's that sa covers: the best any section on sb's lattice can
    do to agree with sa. line_seam(sa, resampled(sa, sb), P) is the floor of the seam at the line between two
    lattices (each drawn by interpolating its own pixels; their difference at the line is sa's roughness between its
    pixels), the reference a matched section's seam is judged against."""
    from . import match as ZM
    nx, ny, res = sb["nx"], sb["ny"], sb["res"]
    r, c = np.divmod(np.arange(nx * ny), nx)
    h, _, la, _, _, ins = ZM._sample(sa, sb["frame"].to_sphere((c + 0.5 - nx / 2) * res, (ny / 2 - r - 0.5) * res), sa["res"])
    hb = np.where(ins > 0, h, sb["h"].ravel()).astype(np.float32).reshape(ny, nx)
    return {**sb, "h": hb, "land": np.where((ins > 0).reshape(ny, nx), la.reshape(ny, nx), sb["land"])}


def line_rivers(sa: dict, a: str, sb: dict, b: str, qmin: float = 100.0) -> list[tuple[float, float]]:
    """The rivers of section a (its own network, on its own ground) flowing into cell b: [(a's discharge at its last
    pixel, b's largest discharge within 2 of b's pixels round where it enters)] for each crossing of >= qmin m3/s.
    Carried on: the second about the first (more, with b's own tributaries joining at the line)."""
    def pts(s, idx):
        r, c = np.divmod(idx, s["nx"])
        return s["frame"].to_sphere((c + 0.5 - s["nx"] / 2) * s["res"], (s["ny"] / 2 - r - 0.5) * s["res"])
    cand = np.flatnonzero((sa["rec"] >= 0) & (sa["q"] >= qmin) & sa["land"].ravel())
    cand = cand[_cells_of(pts(sa, cand)) == a]
    cand = cand[_cells_of(pts(sa, sa["rec"][cand])) == b]
    qb = sb["q"].reshape(sb["ny"], sb["nx"])
    out = []
    for k in cand:
        x, y = sb["frame"].to_plane(pts(sa, sa["rec"][k:k + 1]))
        r = int(np.floor(sb["ny"] / 2 - y[0] / sb["res"]))
        c = int(np.floor(x[0] / sb["res"] + sb["nx"] / 2))
        if not (2 <= r < sb["ny"] - 2 and 2 <= c < sb["nx"] - 2):  # (enters b's ground off b's raster)
            continue
        out.append((float(sa["q"][k]), float(qb[r - 2:r + 3, c - 2:c + 3].max())))
    return out
