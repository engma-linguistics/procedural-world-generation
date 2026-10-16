"""A minimal numpy reader for classic netCDF files (CDF-1 and CDF-2, "64-bit offset").

Written for the UHH-ICDC 0.5 deg MODIS tree cover (tools/earth_data.py). The
whole file is in memory (`bytes`); the header is parsed and each variable
decoded with numpy (big-endian byte, char, short, int, float, double).
Record variables are supported (the record dimension's length is numrecs).
NetCDF-4 files are HDF5: use tools/h5_reader.py. Data is only parsed as
numbers, never executed.
"""

from __future__ import annotations

import struct

import numpy as np

_TYPES = {1: ">i1", 2: "S1", 3: ">i2", 4: ">i4", 5: ">f4", 6: ">f8"}


class _Buf:
    def __init__(self, data: bytes, off_size: int):
        self.d, self.p, self.off = data, 0, off_size

    def u32(self) -> int:
        v = struct.unpack(">I", self.d[self.p:self.p + 4])[0]
        self.p += 4
        return v

    def offset(self) -> int:
        n = self.off
        v = int.from_bytes(self.d[self.p:self.p + n], "big")
        self.p += n
        return v

    def name(self) -> str:
        n = self.u32()
        s = self.d[self.p:self.p + n].decode("utf-8")
        self.p += n + (-n % 4)
        return s

    def values(self, typ: int, n: int):
        if typ not in _TYPES:
            raise ValueError(f"unsupported netCDF type {typ}")
        dt = np.dtype(_TYPES[typ])
        raw = self.d[self.p:self.p + n * dt.itemsize]
        self.p += n * dt.itemsize + (-(n * dt.itemsize) % 4)
        if typ == 2:
            return raw.decode("utf-8", "replace").rstrip("\0")
        return np.frombuffer(raw, dt).astype(dt.newbyteorder("="))

    def attrs(self) -> dict:
        tag, n = self.u32(), self.u32()
        if tag not in (0, 12):
            raise ValueError("bad netCDF attribute list")
        out = {}
        for _ in range(n):
            k = self.name()
            typ, m = self.u32(), self.u32()
            out[k] = self.values(typ, m)
        return out


def header(data: bytes) -> dict:
    """dict(dims {name: length}, attrs, vars {name: dict(dims, attrs, type, begin, vsize)}, numrecs, recsize)."""
    if data[:3] != b"CDF" or data[3] not in (1, 2):
        raise ValueError("not a classic netCDF file (CDF-1 / CDF-2)")
    b = _Buf(data, 4 if data[3] == 1 else 8)
    b.p = 4
    numrecs = b.u32()
    tag, n = b.u32(), b.u32()
    if tag not in (0, 10):
        raise ValueError("bad netCDF dimension list")
    dims = []
    for _ in range(n):
        dims.append((b.name(), b.u32()))
    gatt = b.attrs()
    tag, n = b.u32(), b.u32()
    if tag not in (0, 11):
        raise ValueError("bad netCDF variable list")
    vars_ = {}
    for _ in range(n):
        name = b.name()
        ids = [b.u32() for _ in range(b.u32())]
        va = b.attrs()
        typ, vsize = b.u32(), b.u32()
        vars_[name] = dict(dims=[dims[i][0] for i in ids], shape=[dims[i][1] for i in ids], attrs=va,
                           type=typ, begin=b.offset(), vsize=vsize,
                           record=bool(ids) and dims[ids[0]][1] == 0)
    recvars = [v for v in vars_.values() if v["record"]]
    if len(recvars) == 1 and recvars[0]["type"] in _TYPES:  # the only record variable: no padding
        v = recvars[0]
        recsize = int(np.prod(v["shape"][1:])) * np.dtype(_TYPES[v["type"]]).itemsize
    else:
        recsize = sum(v["vsize"] for v in recvars)
    return dict(dims=dict(dims), attrs=gatt, vars=vars_, numrecs=numrecs, recsize=recsize)


def read_variable(data: bytes, name: str, h: dict | None = None) -> np.ndarray:
    """One variable as stored (no scale_factor or _FillValue applied; see its attrs in header())."""
    h = h or header(data)
    v = h["vars"][name]
    if v["type"] not in _TYPES or v["type"] == 2:
        raise ValueError(f"unsupported netCDF variable type {v['type']}")
    dt = np.dtype(_TYPES[v["type"]])
    if not v["record"]:
        n = int(np.prod(v["shape"]))
        arr = np.frombuffer(data, dt, n, v["begin"])
        return arr.reshape(v["shape"]).astype(dt.newbyteorder("="))
    inner = v["shape"][1:]
    n = int(np.prod(inner))
    recs = [np.frombuffer(data, dt, n, v["begin"] + r * h["recsize"]) for r in range(h["numrecs"])]
    return np.stack(recs).reshape([h["numrecs"]] + inner).astype(dt.newbyteorder("="))
