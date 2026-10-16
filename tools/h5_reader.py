"""A minimal pure zlib + numpy HDF5 / netCDF-4 reader for one kind of file.

Written for the LGM ice cover on Zenodo (tools/earth_data.py), which is a
netCDF-4 file with a flat root group of chunked, deflate-compressed arrays,
and NOAA PSL's reanalysis climatologies (the same, from an older library).
Supported: superblock v0/v2/v3, version 2 object headers, compact link
messages in the root group, version 1 or 2 dataspaces and filter pipelines,
chunked layout v3 with a version 1 B-tree index (and compact or contiguous
arrays, unblocked), deflate and shuffle filters, fixed-point and
floating-point little-endian types.
Anything else (dense groups, other layouts, compound types, ...) raises
ValueError. `src` is a random-access source (tools/tiff_reader.HttpRange or
BytesSource). Data is only parsed as numbers, never executed.
"""

from __future__ import annotations

import struct
import zlib

import numpy as np


def _messages(src, off: int) -> list[tuple[int, bytes]]:
    head = src.read(off, 64)
    if head[:4] != b"OHDR" or head[4] != 2:
        raise ValueError("unsupported HDF5 object header")
    flags = head[5]
    p = 6 + (16 if flags & 0x20 else 0) + (4 if flags & 0x10 else 0)
    n = 1 << (flags & 3)
    size = int.from_bytes(head[p:p + n], "little")
    p += n
    blocks = [(off + p, size)]  # (start of the messages, byte length)
    out = []
    while blocks:
        a, ln = blocks.pop(0)
        buf = src.read(a, ln)
        q = 0
        while q + 4 <= len(buf):
            t, sz = buf[q], struct.unpack("<H", buf[q + 1:q + 3])[0]
            q += 4 + (2 if flags & 4 else 0)
            body = buf[q:q + sz]
            q += sz
            if t == 0x10:  # continuation: a block "OCHK" ... checksum
                o, ln2 = struct.unpack("<QQ", body[:16])
                blocks.append((o + 4, ln2 - 8))
            elif t:
                out.append((t, body))
    return out


def _root_links(src) -> dict[str, int]:
    sb = src.read(0, 96)
    if sb[:8] != b"\x89HDF\r\n\x1a\n":
        raise ValueError("not an HDF5 file")
    if sb[8] in (2, 3) and sb[9] == 8:
        root = struct.unpack("<Q", sb[36:44])[0]
    elif sb[8] == 0 and sb[13] == 8 and sb[14] == 8:
        # version 0 (netCDF-4 files written by older libraries, e.g. NOAA PSL's): the root
        # group's symbol table entry holds its object header's address; the header itself
        # may still be a version 2 one with compact links (anything else raises below)
        root = struct.unpack("<Q", sb[64:72])[0]
    else:
        raise ValueError("unsupported HDF5 superblock (need v0/v2/v3 with 8-byte offsets)")
    links = {}
    for t, b in _messages(src, root):
        if t != 6:
            continue
        fl, q = b[1], 2
        if fl & 8 and b[q] != 0:
            continue  # soft / external link
        q += 1 if fl & 8 else 0
        q += 8 if fl & 4 else 0
        q += 1 if fl & 0x10 else 0
        nl = int.from_bytes(b[q:q + (1 << (fl & 3))], "little")
        q += 1 << (fl & 3)
        links[b[q:q + nl].decode()] = struct.unpack("<Q", b[q + nl:q + nl + 8])[0]
    if not links:
        raise ValueError("no compact links in the root group (dense groups unsupported)")
    return links


def _chunks(src, addr: int, rank: int):
    """Yield (offsets, file address, size, filter mask) of every chunk in a v1 B-tree."""
    head = src.read(addr, 24)
    if head[:4] != b"TREE" or head[4] != 1:
        raise ValueError("unsupported chunk index (need a version 1 B-tree)")
    level, used = head[5], struct.unpack("<H", head[6:8])[0]
    ksz = 8 + 8 * (rank + 1)
    body = src.read(addr + 24, used * (ksz + 8) + ksz)
    for i in range(used):
        key = body[i * (ksz + 8):i * (ksz + 8) + ksz]
        child = struct.unpack("<Q", body[i * (ksz + 8) + ksz:(i + 1) * (ksz + 8)])[0]
        if level:
            yield from _chunks(src, child, rank)
        else:
            size, mask = struct.unpack("<II", key[:8])
            yield struct.unpack("<" + "Q" * (rank + 1), key[8:])[:rank], child, size, mask


def variables(src) -> list[str]:
    return sorted(_root_links(src))


def read_variable(src, name: str, block: int = 1, fetch_gap: int = 1 << 16) -> np.ndarray:
    """Decode a root-group variable. block > 1 averages block x block cells
    (2-D only) while decoding, so a huge raster never exists in full; the chunk
    shape must be a multiple of block. Returns float32 when block > 1."""
    ms = dict(_messages(src, _root_links(src)[name]))
    for t in (1, 3, 8):
        if t not in ms:
            raise ValueError(f"variable {name!r}: missing header message {t}")
    ds, dt, lay = ms[1], ms[3], ms[8]
    rank = ds[1]
    d0 = 8 if ds[0] == 1 else 4  # (dataspace v1 has 5 reserved bytes, v2 none)
    shape = struct.unpack("<" + "Q" * rank, ds[d0:d0 + 8 * rank])
    cls, size = dt[0] & 15, struct.unpack("<I", dt[4:8])[0]
    if dt[1] & 1:
        raise ValueError("big-endian HDF5 data unsupported")
    if cls == 0:
        np_dt = np.dtype(f"{'i' if dt[1] & 8 else 'u'}{size}")
    elif cls == 1:
        np_dt = np.dtype(f"f{size}")
    else:
        raise ValueError(f"unsupported HDF5 datatype class {cls}")
    if lay[0] == 3 and lay[1] in (0, 1) and block == 1:  # compact / contiguous (small coordinate arrays)
        if lay[1] == 1:
            addr, nbytes = struct.unpack("<QQ", lay[2:18])
            raw = src.read(addr, nbytes)
        else:
            nbytes = struct.unpack("<H", lay[2:4])[0]
            raw = lay[4:4 + nbytes]
        return np.frombuffer(raw, np_dt, int(np.prod(shape))).reshape(shape).astype(np_dt.newbyteorder("="))
    if lay[0] != 3 or lay[1] != 2:
        raise ValueError("unsupported HDF5 layout (need compact, contiguous or chunked, layout version 3)")
    r1 = lay[2]
    btree = struct.unpack("<Q", lay[3:11])[0]
    cdims = struct.unpack("<" + "I" * r1, lay[11:11 + 4 * r1])[:rank]
    filters = []
    if 11 in ms:
        f = ms[11]
        if f[0] == 2:
            q = 2
            for _ in range(f[1]):
                fid, _, ncv = struct.unpack("<HHH", f[q:q + 6])  # v2: no name for ids < 256
                q += 6 + 4 * ncv
                filters.append(fid)
        elif f[0] == 1:  # v1: each filter's name and client data padded to 8 bytes
            q = 8
            for _ in range(f[1]):
                fid, nlen, _, ncv = struct.unpack("<HHHH", f[q:q + 8])
                q += 8 + nlen + 4 * ncv + (4 if ncv % 2 else 0)
                filters.append(fid)
        else:
            raise ValueError("unsupported filter pipeline version")
    if any(x not in (1, 2) for x in filters):
        raise ValueError(f"unsupported HDF5 filters {filters}")
    if block > 1 and (rank != 2 or any(c % block or s % block for c, s in zip(cdims, shape))):
        raise ValueError("block must divide the chunk and array shape")
    if block > 1:
        out = np.zeros((shape[0] // block, shape[1] // block), np.float32)
    else:
        out = np.zeros(shape, np_dt.newbyteorder("="))
    todo = sorted(_chunks(src, btree, rank), key=lambda c: c[1])
    k = 0
    while k < len(todo):
        j = k
        while j + 1 < len(todo) and todo[j + 1][1] - (todo[j][1] + todo[j][2]) <= fetch_gap:
            j += 1
        a = todo[k][1]
        blob = src.read(a, todo[j][1] + todo[j][2] - a)
        for offs, addr, sz, mask in todo[k:j + 1]:
            raw = blob[addr - a:addr - a + sz]
            for fid in reversed(filters):  # undo in reverse order
                if mask & (1 << filters.index(fid)):
                    continue
                if fid == 1:
                    raw = zlib.decompress(raw)
                else:  # shuffle: bytes of each element were de-interleaved
                    raw = np.frombuffer(raw, np.uint8).reshape(size, -1).T.tobytes()
            tile = np.frombuffer(raw, dtype=np_dt, count=int(np.prod(cdims))).reshape(cdims)
            sl = tuple(slice(o, min(o + c, s)) for o, c, s in zip(offs, cdims, shape))
            tile = tile[tuple(slice(0, s.stop - s.start) for s in sl)]
            if block > 1:
                h, w = tile.shape
                tile = tile.reshape(h // block, block, w // block, block).mean((1, 3), dtype=np.float32)
                sl = (slice(offs[0] // block, offs[0] // block + h // block),
                      slice(offs[1] // block, offs[1] // block + w // block))
            out[sl] = tile
        k = j + 1
    return out
