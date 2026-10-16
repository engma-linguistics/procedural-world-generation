"""A small pure zlib + numpy TIFF / BigTIFF reader for remote, tiled overview files.

Written for the SoilGrids overview file (tools/earth_data.py); the project has
no GDAL. Reads the IFD chain (classic TIFF and BigTIFF, either byte order)
through a random-access `source` (anything with `read(offset, n) -> bytes`:
HttpRange for a URL, BytesSource for tests), then decodes one level into an
array. Supports tiled or stripped, uncompressed or deflate (compression 8 /
32946), single band, integer or float samples, predictor 1 or 2. Data is only
ever parsed as numbers, never executed. Anything unsupported raises ValueError.
"""

from __future__ import annotations

import struct
import urllib.request
import zlib

import numpy as np

# TIFF field type -> (numpy dtype, size); rationals, ASCII etc. are skipped
_NP = {1: ("u1", 1), 3: ("u2", 2), 4: ("u4", 4), 16: ("u8", 8), 6: ("i1", 1), 7: ("u1", 1),
       8: ("i2", 2), 9: ("i4", 4), 17: ("i8", 8), 18: ("u8", 8)}

TAGS = {254: "subfile", 256: "width", 257: "length", 258: "bits", 259: "compression", 273: "strip_offsets",
        277: "samples", 278: "rows_per_strip", 279: "strip_counts", 317: "predictor", 322: "tile_width",
        323: "tile_length", 324: "tile_offsets", 325: "tile_counts", 339: "sample_format"}
_SCALARS = ("width", "length", "compression", "predictor", "rows_per_strip", "tile_width", "tile_length",
            "subfile", "samples", "bits", "sample_format")


class BytesSource:
    def __init__(self, data: bytes):
        self.data = data

    def read(self, offset: int, n: int) -> bytes:
        return self.data[offset:offset + n]


class HttpRange:
    """Random access to a URL by HTTP range requests (counts the bytes fetched)."""

    def __init__(self, url: str, timeout: float = 120):
        self.url, self.timeout, self.fetched = url, timeout, 0

    def read(self, offset: int, n: int) -> bytes:
        req = urllib.request.Request(self.url, headers={
            "Range": f"bytes={offset}-{offset + n - 1}", "User-Agent": "procgen-world-earth-check"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            if r.status != 206:
                raise ValueError(f"server ignored the range request ({r.status})")
            out = r.read()
        self.fetched += len(out)
        return out


def read_ifds(src, max_ifds: int = 32) -> list[dict]:
    """The IFD chain: one dict per image (width, length, tile_offsets, ...)."""
    head = src.read(0, 16)
    bo = {b"II": "<", b"MM": ">"}.get(head[:2])
    if bo is None:
        raise ValueError("not a TIFF")
    magic = struct.unpack(bo + "H", head[2:4])[0]
    if magic == 42:
        big, off = False, struct.unpack(bo + "I", head[4:8])[0]
    elif magic == 43:
        big, off = True, struct.unpack(bo + "Q", head[8:16])[0]
    else:
        raise ValueError("not a TIFF")
    cfmt, ent, vsize = ("Q", 20, 8) if big else ("H", 12, 4)
    ofmt = "Q" if big else "I"
    csize = struct.calcsize(cfmt)
    out = []
    while off and len(out) < max_ifds:
        n = struct.unpack(bo + cfmt, src.read(off, csize))[0]
        raw = src.read(off + csize, n * ent + vsize)
        ifd = {}
        for i in range(n):
            e = raw[i * ent:(i + 1) * ent]
            tag, typ = struct.unpack(bo + "HH", e[:4])
            if tag not in TAGS or typ not in _NP:
                continue
            count = struct.unpack(bo + ofmt, e[4:4 + vsize])[0]
            dt, size = _NP[typ]
            vraw = e[4 + vsize:]
            if count * size > vsize:
                vraw = src.read(struct.unpack(bo + ofmt, vraw[:vsize])[0], count * size)
            ifd[TAGS[tag]] = np.frombuffer(vraw[:count * size], dtype=np.dtype(dt).newbyteorder(bo)).astype(np.int64)
        for k in _SCALARS:
            if k in ifd:
                ifd[k] = int(ifd[k][0])
        ifd.setdefault("bits", 1)
        ifd.setdefault("sample_format", 1)
        ifd["byteorder"] = bo
        out.append(ifd)
        off = struct.unpack(bo + ofmt, raw[n * ent:n * ent + vsize])[0]
    return out


def _decode(raw: bytes, comp: int) -> bytes:
    if comp == 1:
        return raw
    if comp in (8, 32946):
        return zlib.decompress(raw)
    raise ValueError(f"unsupported TIFF compression {comp}")


def read_image(src, ifd: dict, fetch_gap: int = 1 << 16) -> np.ndarray:
    """Decode one IFD into an array (length, width). Tiles are fetched in
    coalesced range requests (tiles closer than `fetch_gap` bytes share one)."""
    if ifd.get("samples", 1) != 1:
        raise ValueError("only single-band TIFFs")
    kind = {1: "u", 2: "i", 3: "f"}.get(ifd["sample_format"])
    if kind is None or ifd["bits"] % 8:
        raise ValueError("unsupported sample format")
    dt = np.dtype(f"{kind}{ifd['bits'] // 8}").newbyteorder(ifd["byteorder"])
    W, H = ifd["width"], ifd["length"]
    comp, pred = ifd.get("compression", 1), ifd.get("predictor", 1)
    if "tile_offsets" in ifd:
        tw, th = ifd["tile_width"], ifd["tile_length"]
        offs, cnts = ifd["tile_offsets"], ifd["tile_counts"]
        across = -(-W // tw)

        def shape_of(i):
            return th, tw

        def place(i):
            return (i // across) * th, (i % across) * tw
    else:
        rps = ifd.get("rows_per_strip", H)
        offs, cnts = ifd["strip_offsets"], ifd["strip_counts"]

        def shape_of(i):
            return min(rps, H - i * rps), W

        def place(i):
            return i * rps, 0
    out = np.zeros((H, W), dt.newbyteorder("="))
    order = np.argsort(offs)
    k = 0
    while k < len(order):
        j = k
        while j + 1 < len(order) and offs[order[j + 1]] - (offs[order[j]] + cnts[order[j]]) <= fetch_gap:
            j += 1
        a = int(offs[order[k]])
        blob = src.read(a, int(offs[order[j]] + cnts[order[j]]) - a)
        for t in order[k:j + 1]:
            if cnts[t] == 0:
                continue
            s = int(offs[t]) - a
            sh = shape_of(t)
            tile = np.frombuffer(_decode(blob[s:s + int(cnts[t])], comp), dtype=dt, count=sh[0] * sh[1]).reshape(sh)
            if pred == 2:
                tile = np.cumsum(tile, axis=1, dtype=tile.dtype)
            y, x = place(t)
            h, w = min(sh[0], H - y), min(sh[1], W - x)
            out[y:y + h, x:x + w] = tile[:h, :w]
        k = j + 1
    return out
