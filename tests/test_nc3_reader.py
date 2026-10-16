"""tools/nc3_reader.py on a small hand-built classic netCDF file. No network, no netCDF library."""

import struct
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.nc3_reader import header, read_variable  # noqa: E402


def _name(s):
    b = s.encode()
    return struct.pack(">I", len(b)) + b + b"\0" * (-len(b) % 4)


def _vals(typ, a):
    raw = a.encode() if typ == 2 else np.asarray(a).astype({1: ">i1", 3: ">i2", 4: ">i4", 5: ">f4", 6: ">f8"}[typ]).tobytes()
    n = len(a) if typ == 2 else np.asarray(a).size
    return struct.pack(">II", typ, n) + raw + b"\0" * (-len(raw) % 4)


def _attrs(d):
    if not d:
        return b"\0" * 8
    return struct.pack(">II", 12, len(d)) + b"".join(_name(k) + _vals(t, v) for k, (t, v) in d.items())


def build(dims, vars_, version=1, numrecs=0):
    """dims [(name, len)] (len 0: the record dimension); vars_ [(name, dimids, typ, data, attrs)]."""
    osz = 4 if version == 1 else 8
    typ_dt = {1: ">i1", 3: ">i2", 4: ">i4", 5: ">f4", 6: ">f8"}

    def head(begins):
        h = b"CDF" + bytes([version]) + struct.pack(">I", numrecs)
        h += struct.pack(">II", 10, len(dims)) + b"".join(_name(n) + struct.pack(">I", ln) for n, ln in dims)
        h += _attrs({"title": (2, "test")})
        h += struct.pack(">II", 11, len(vars_))
        for (name, ids, typ, data, at), beg in zip(vars_, begins):
            rec = ids and dims[ids[0]][1] == 0
            per = data[0] if rec else data
            raw = np.asarray(per).astype(typ_dt[typ]).tobytes()
            vsize = len(raw) + (-len(raw) % 4)
            h += _name(name) + struct.pack(">I", len(ids)) + b"".join(struct.pack(">I", i) for i in ids)
            h += _attrs(at) + struct.pack(">II", typ, vsize) + beg.to_bytes(osz, "big")
        return h

    h0 = len(head([0] * len(vars_)))
    fixed = [v for v in vars_ if not (v[1] and dims[v[1][0]][1] == 0)]
    rec = [v for v in vars_ if v not in fixed]
    body, begins = b"", {}
    for name, ids, typ, data, at in fixed:
        begins[name] = h0 + len(body)
        raw = np.asarray(data).astype(typ_dt[typ]).tobytes()
        body += raw + b"\0" * (-len(raw) % 4)
    rec_start = h0 + len(body)
    pad = len(rec) > 1  # each record's slab of a variable is padded to 4 bytes, unless it is the only one
    sizes = [np.asarray(v[3][0]).astype(typ_dt[v[2]]).nbytes for v in rec]
    off = 0
    for v, s in zip(rec, sizes):
        begins[v[0]] = rec_start + off
        off += s + (-s % 4 if pad else 0)
    for r in range(numrecs):
        for v in rec:
            raw = np.asarray(v[3][r]).astype(typ_dt[v[2]]).tobytes()
            body += raw + (b"\0" * (-len(raw) % 4) if pad else b"")
    return head([begins[v[0]] for v in vars_]) + body


@pytest.mark.parametrize("version", [1, 2])
def test_fixed_and_record(version):
    rng = np.random.default_rng(0)
    tree = rng.integers(0, 101, (1, 3, 5)).astype(np.int8)
    lat = np.array([1.5, 0.5, -0.5], np.float32)
    sst = rng.normal(size=(2, 3)).astype(np.float64)
    cnt = rng.integers(-5, 5, (2, 3)).astype(np.int16)
    f = build([("time", 1), ("lat", 3), ("lon", 5), ("rec", 0)], [
        ("lat", [1], 5, lat, {"units": (2, "degrees_north")}),
        ("tree", [0, 1, 2], 1, tree, {"_FillValue": (1, [127]), "units": (2, "percent")}),
        ("sst", [3, 1], 6, sst, {}),
        ("cnt", [3, 1], 3, cnt, {}),  # 6 bytes a record, padded to 8 in the record block
    ], version=version, numrecs=2)
    h = header(f)
    assert h["dims"] == {"time": 1, "lat": 3, "lon": 5, "rec": 0} and h["numrecs"] == 2
    assert h["attrs"]["title"] == "test"
    assert h["vars"]["tree"]["attrs"]["units"] == "percent" and int(h["vars"]["tree"]["attrs"]["_FillValue"][0]) == 127
    assert np.array_equal(read_variable(f, "tree"), tree)
    assert np.array_equal(read_variable(f, "lat"), lat)
    assert np.array_equal(read_variable(f, "sst"), sst)
    assert np.array_equal(read_variable(f, "cnt"), cnt)


def test_rejects():
    with pytest.raises(ValueError):
        header(b"\x89HDF\r\n\x1a\n" + b"\0" * 32)
