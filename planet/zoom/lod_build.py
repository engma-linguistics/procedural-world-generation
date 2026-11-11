"""Building the level-of-detail tiles (docs/review/zoom/lod-plan-v2.md 2.2, step 1; PW-1689).

A tile of level 2-4 (zoom/lod.py) is the fine pass (zoom/fine.py) run on its level's shared pixel lattice of its cell's
plane (lod.tile_frame), from its parent level stitched into one window (lod.parent_mosaic), with seam=True: its edge
fades to a surface that depends only on the place, its parent's rivers are imposed with their meander phase and their
discharge, so tiles built at different times, in any order, meet at their edges. Level 1 is the cell's section at 4 km
(regional.zoom(section=...), the API's section build); this module finds it but does not build it.

    build(world, key, sources, seed)       the tile (a zoom dict, as fine.build)
    edge_surface(world, key, sources, seed) the ground at its edges, carved on blocks keyed by place (PW-1694)
    save(z, world_id, key, pmeta, seed)    an ordinary zoom directory under zooms/<lod.tile_id>, with a `tile` block
    find(world_id, key, seed)              the saved tile's (or level-1 section's) directory, or None
    load_sources(world_id, key, seed)      the parent tiles its build reads (lod.parent_sources), loaded
    tile(world_ref, key, seed)             find or build-and-save one tile whose parent tiles are built
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from .. import store as S
from .. import world as W
from . import fine as ZF
from . import lod as L
from . import regional as Z

STRIP_PX = 32  # px: an edge block's half width (a strip centred on a tile's edge; its carving clear of its own edge)


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
    r = _block_rect(key.level, b)
    pm = L.parent_mosaic(key, sources, r)
    fr = Z.PlaneFrame(L.frame(key.cell), 0.5 * (r[0] + r[1]), 0.5 * (r[2] + r[3]))
    lat, lon = Z._latlon(fr.c)
    res = L.res_km(key.level)
    w, h = b[1] - b[0], b[3] - b[2]
    out = ZF.build(pm, world, lat, lon, max(w, h) * res, res, seed, log=lambda *_: None, frame=fr, seam=True,
                   shape=(w, h), carve=True)
    return out["hw"]


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


def build(world: dict, key: L.Key, sources: dict, seed: int = 1, log=print) -> dict:
    """The tile `key` from its parent tiles `sources` ({Key: (meta, decoded layers)}, load_sources). Deterministic: the
    same sources give the same arrays."""
    if key.level == min(L.LEVELS):
        raise ValueError("level 1 is the cell's section: regional.zoom(section=...)")
    p = L.parent(key)
    if p.level == min(L.LEVELS) and p in sources and "river_phase" not in sources[p][1]:
        # (a section has no river_phase: its whole network's, so every level-2 tile of the cell reads the same)
        m1, l1 = sources[p]
        sources = {**sources, p: (m1, {**l1, "river_phase": ZF.network_phase(m1, l1, seed)})}
    pm = L.parent_mosaic(key, sources)
    fr = L.tile_frame(key)
    lat, lon = Z._latlon(fr.c)
    t0 = time.time()
    edge = edge_surface(world, key, sources, seed)
    log(f"  edge blocks carved [{time.time() - t0:.1f}s]")
    z = ZF.build(pm, world, lat, lon, L.tile_km(key.level), L.res_km(key.level), seed, log=log, frame=fr, seam=True,
                 edge=edge)
    z["parent_meta"] = pm[0]  # (what save() records the tile was built from)
    return z


def tile_block(world_id: str, key: L.Key, seed: int, pmeta: dict) -> dict:
    """zoom.json's `tile` block: the tile's address, its rectangle in the cell's plane and what it was built from."""
    return {"world": world_id, "cell": key.cell, "level": key.level, "tx": key.tx, "ty": key.ty, "key": str(key),
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
                   extra={"tile": tile_block(world_id, key, seed, pmeta)})


def _section_dir(world_id: str, cell: str, seed: int) -> Path | None:
    """The cell's level-1 section of this world (a zoom with section == cell at level 1's res_km), newest first."""
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
    """The saved tile `key` of a world: found, or built from its parent tiles (which must be built) and saved."""
    key = L.Key.parse(key) if isinstance(key, str) else key
    wpath = Z.find_world(world_ref)
    wid = wpath.stem
    d = find(wid, key, seed)
    if d is not None:
        return d
    if not L.exists(key):
        raise ValueError(f"tile {key} is not part of cell {key.cell}'s pyramid")
    t0 = time.time()
    src = load_sources(wid, key, seed)
    world = W.load(wpath)
    z = build(world, key, src, seed, log=log)
    with S.lock(S.zooms_dir(), L.tile_id(wid, key, seed)):
        out = save(z, wid, key, seed)
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
