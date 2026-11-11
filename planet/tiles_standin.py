"""STAND-IN tile source for the level-of-detail globe (PW-1688, lane 291). **Replaced by the tile service, PW-1690.**

It builds nothing. It serves the section zooms a world already has as the tile pyramid of `zoom/lod.py`, enough to drive
the globe's tiles (viewer/globe/tilesource.js is the viewer's side of the same contract):

    GET /api/tiles/index?world=<id>
        {standin: true, world, ladder: lod.describe(), cells: [{id, lat, lon, up, outline: [[x, y] km in the cell's plane],
         tiles: {"1": [[0, 0]], "2": [[tx, ty], ...]}}]}   only cells with a section zoom; tiles: those it can serve
    GET /api/tiles/<world>/<cell>/<level>/<tx>/<ty>/view.bin
        b"PWT1", int32 n, then n*n float16 ground elevation (m, row-major from the north-west, lod.lattice order), then
        n*n uint8 water (0 land, 1 sea, 2 lake)
    GET /api/tiles/<world>/<cell>/<level>/<tx>/<ty>/satellite.png      the tile's satellite view (the year's)
    GET /api/tiles/<world>/<cell>/<level>/<tx>/<ty>/layer/<name>.bin   one zoom layer as n*n float32 (decoded units)

Level 1 is the cell's 4 km section (or its 1 km one, 4 x 4 block means); level 2 is a 500 km slice of the cell's 1 km
section (500 px), else of the 4 km one (125 px: stretched, no new detail). A section zoom's pixel grid is exactly the
lod lattice (x = -2000 + (i + 0.5) res), so a slice is a tile. Answers are cached under <data root>/.tiles-standin.

What PW-1690 replaces: all of this module and its three routes in server.py. It keeps the file names and view.bin's layout
(or changes tilesource.js with it) and adds POST /api/tiles/want and GET /api/tiles/status (lod-plan-v2.md section 3);
the viewer already sends nothing but GETs of tiles the index lists, centre-first, at most a few at a time.
"""
from __future__ import annotations

import json
import struct
import zlib
from functools import lru_cache
from pathlib import Path

import numba
import numpy as np

from . import store as S
from .images import png_bytes
from .zoom import lod

FILES = ("view.bin", "satellite.png")


class NotFound(Exception):
    pass


def _sections(world: str) -> dict[str, dict[float, str]]:
    """cell -> {res_km: zoom id} of the world's section zooms (newest first wins)."""
    stem = S.find_world(world).stem
    return _sections_at(stem, S.zooms_dir().stat().st_mtime_ns)


@lru_cache(maxsize=16)
def _sections_at(stem: str, _mtime: int) -> dict[str, dict[float, str]]:
    out: dict[str, dict[float, str]] = {}
    for _, e in S.items("zoom"):
        if e.get("world") == stem and e.get("section") and not e.get("parent_zoom") and e.get("size_km") == lod.SQUARE_KM:
            out.setdefault(e["section"], {}).setdefault(float(e["res_km"]), e["id"])
    return out


def _source(world: str, key: lod.Key) -> tuple[str, int]:
    """(zoom id, block): the section zoom a tile is cut from and the block-mean factor (1: none)."""
    secs = _sections(world).get(key.cell, {})
    if key.level == 1:
        if 4.0 in secs:
            return secs[4.0], 1
        if 1.0 in secs:
            return secs[1.0], 4
    elif key.level == 2:
        for r in (1.0, 4.0):
            if r in secs:
                return secs[r], 1
    raise NotFound(f"no section zoom for {key}")


def index(world: str) -> dict:
    cells = []
    for cell, secs in sorted(_sections(world).items()):
        if not ({1.0, 4.0} & set(secs)):
            continue
        fr = lod.frame(cell)
        lat, lon = np.degrees(np.arcsin(np.clip(fr.c[2], -1, 1))), np.degrees(np.arctan2(fr.c[1], fr.c[0]))
        ol = lod.outline(cell)
        two = [[k.tx, k.ty] for k in lod.covering(cell, 2, (-lod.HALF, lod.HALF, -lod.HALF, lod.HALF))]
        cells.append({"id": cell, "lat": round(float(lat), 6), "lon": round(float(lon), 6),
                      "up": [round(float(v), 8) for v in fr.n],
                      "outline": np.round(ol, 3).tolist(), "tiles": {"1": [[0, 0]], "2": two},
                      "sources": {f"{r:g}": z for r, z in secs.items()}})
    return {"standin": True, "world": S.find_world(world).stem, "ladder": lod.describe(), "cells": cells}


def _zoom_dir(zid: str) -> Path:
    return S.find_zoom(zid)


@lru_cache(maxsize=8)
def _meta(zid: str) -> dict:
    return json.loads((_zoom_dir(zid) / "zoom.json").read_text())


def _layer(zid: str, name: str) -> np.ndarray:
    m = _meta(zid)
    spec = m["layers"].get(name)
    if spec is None or spec.get("transform") not in (None, "log2p1"):
        raise NotFound(f"zoom {zid} has no layer {name}")
    raw = np.memmap(_zoom_dir(zid) / spec["file"], dtype=np.dtype(spec["dtype"]).newbyteorder("<"), mode="r",
                    shape=tuple(spec["shape"]))
    return raw, spec


def _cut(a: np.ndarray, key: lod.Key, res: float, block: int) -> np.ndarray:
    """The tile's block of a section-sized array (rows from the north)."""
    if key.level == 1:
        out = np.asarray(a)
    else:
        n = int(round(lod.tile_km(key.level) / res))
        out = np.asarray(a[key.ty * n:(key.ty + 1) * n, key.tx * n:(key.tx + 1) * n])
    if block > 1:
        h, w = out.shape[:2]
        out = out[:h - h % block, :w - w % block].reshape(h // block, block, w // block, block, *out.shape[2:])
        out = out.mean(axis=(1, 3)) if out.dtype.kind == "f" else out[:, 0, :, 0]
    return out


def _decoded(raw, spec) -> np.ndarray:
    return np.asarray(S.decode(np.asarray(raw), spec), dtype=np.float32)


# ---- satellite: the source zoom's PNG decoded once (no image library) ------------------------------------------------
@numba.njit(cache=True)
def _unfilter(data, h, stride, bpp):
    out = np.empty((h, stride), np.uint8)
    pos = 0
    for y in range(h):
        f = data[pos]
        pos += 1
        for x in range(stride):
            v = np.int32(data[pos + x])
            a = np.int32(out[y, x - bpp]) if x >= bpp else 0
            b = np.int32(out[y - 1, x]) if y > 0 else 0
            c = np.int32(out[y - 1, x - bpp]) if (y > 0 and x >= bpp) else 0
            if f == 1:
                v += a
            elif f == 2:
                v += b
            elif f == 3:
                v += (a + b) >> 1
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                v += a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
            out[y, x] = v & 255
        pos += stride
    return out


def read_png(path: Path) -> np.ndarray:
    """8-bit RGB / RGBA non-interlaced PNG -> (h, w, ch) uint8."""
    b = path.read_bytes()
    pos, idat, w, h, ch = 8, [], 0, 0, 3
    while pos < len(b):
        ln, tag = struct.unpack(">I4s", b[pos:pos + 8])
        body = b[pos + 8:pos + 8 + ln]
        if tag == b"IHDR":
            w, h, depth, ctype, _, _, inter = struct.unpack(">IIBBBBB", body)
            if depth != 8 or ctype not in (2, 6) or inter:
                raise ValueError(f"unsupported PNG {path}")
            ch = 3 if ctype == 2 else 4
        elif tag == b"IDAT":
            idat.append(body)
        pos += 12 + ln
    data = np.frombuffer(zlib.decompress(b"".join(idat)), np.uint8)
    return _unfilter(data, h, w * ch, ch).reshape(h, w, ch)


def _satellite(zid: str) -> np.ndarray:
    f = S.root() / ".tiles-standin" / "src" / f"{zid}-satellite.npy"
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        np.save(f, read_png(_zoom_dir(zid) / _meta(zid)["files"].get("satellite", "satellite.png"))[..., :3])
    return np.load(f, mmap_mode="r")


# ---- one tile file --------------------------------------------------------------------------------------------------
def tile_file(world: str, key: lod.Key, name: str) -> tuple[bytes, str]:
    """(body, content type) of one tile file; raises NotFound."""
    if not lod.exists(key) or key.level > 2:
        raise NotFound(f"no tile {key}")
    zid, block = _source(world, key)
    res = float(_meta(zid)["res_km"])
    cache = S.root() / ".tiles-standin" / S.find_world(world).stem / str(key).replace("/", "_") / name.replace("/", "_")
    ctype = "image/png" if name.endswith(".png") else "application/octet-stream"
    if cache.exists():
        return cache.read_bytes(), ctype
    if name == "view.bin":
        raw, spec = _layer(zid, "elevation")
        e = _cut(_decoded(raw, spec), key, res, block)
        wraw, _ = _layer(zid, "water")
        w = _cut(np.asarray(wraw), key, res, block).astype(np.uint8)
        n = e.shape[0]
        body = b"PWT1" + struct.pack("<i", n) + e.astype("<f2").tobytes() + w.tobytes()
    elif name == "satellite.png":
        body = png_bytes(np.ascontiguousarray(_cut(_satellite(zid), key, res, block).astype(np.uint8)))
    elif name.startswith("layer/") and name.endswith(".bin"):
        raw, spec = _layer(zid, name[6:-4])
        body = _cut(_decoded(raw, spec), key, res, block).astype("<f4").tobytes()
    else:
        raise NotFound(f"no tile file {name}")
    cache.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache.with_suffix(cache.suffix + ".part")
    tmp.write_bytes(body)
    tmp.replace(cache)
    return body, ctype


def get(path: str, query: str) -> tuple[bytes | dict, int, str]:
    """Route a GET under /api/tiles: (body, status, content type)."""
    from urllib.parse import parse_qsl
    try:
        if path == "/api/tiles/index":
            return index(dict(parse_qsl(query)).get("world", "")), 200, "application/json"
        parts = path.split("/")[3:]  # world, cell, level, tx, ty, file...
        if len(parts) < 6:
            raise NotFound("bad tile path")
        world, cell, level, tx, ty = parts[:5]
        key = lod.Key(cell, int(level), int(tx), int(ty))
        body, ctype = tile_file(world, key, "/".join(parts[5:]))
        return body, 200, ctype
    except (NotFound, SystemExit, FileNotFoundError, KeyError) as e:
        return {"error": str(e)}, 404, "application/json"
    except ValueError as e:
        return {"error": str(e)}, 400, "application/json"
