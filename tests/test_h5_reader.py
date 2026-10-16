"""tools/h5_reader.py on a small hand-built HDF5 (netCDF-4 style) file. No network, no h5py."""

import struct
import sys
import zlib
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.h5_reader import read_variable, variables  # noqa: E402
from tools.tiff_reader import BytesSource  # noqa: E402


def _msg(t, body):
    return struct.pack("<BHB", t, len(body), 0) + body


def _ohdr(msgs):
    body = b"".join(msgs)
    return b"OHDR" + bytes([2, 1]) + struct.pack("<H", len(body)) + body + b"\0\0\0\0"


def _tree(chunks, rank, level=0):
    """chunks: [(offsets, addr, size)] (level 0) or [(offsets, child_addr, 0)] (level 1)."""
    out = b"TREE" + bytes([1, level]) + struct.pack("<H", len(chunks)) + b"\xff" * 16
    for offs, addr, size in chunks:
        out += struct.pack("<II", size, 0) + struct.pack("<" + "Q" * (rank + 1), *offs, 0)
        out += struct.pack("<Q", addr)
    return out + struct.pack("<II", 0, 0) + b"\0" * 8 * (rank + 1)  # final key


def build(arrays, two_level=False, old=False):
    """arrays: {name: (ndarray, chunk shape, filter ids)} -> bytes of a superblock-v3 file.
    old: as older netCDF-4 libraries write them (NOAA PSL's files): a version 0 superblock,
    version 1 dataspaces and filter pipelines; a chunk shape of None stores the array contiguous."""
    buf = bytearray(96 if old else 48)  # superblock, filled in last

    def put(b):
        buf.extend(b)
        return len(buf) - len(b)

    links = []
    for name, (a, cdims, filt) in arrays.items():
        size = a.dtype.itemsize
        rank = a.ndim
        head = {"f": b"\x11\x20", "u": b"\x10\x00", "i": b"\x10\x08"}[a.dtype.kind]
        space = (bytes([1, rank, 0, 0]) + b"\0" * 4 if old else bytes([2, rank, 0, 1])) \
            + struct.pack("<" + "Q" * rank, *a.shape)
        dtype_msg = _msg(3, head + b"\0\0" + struct.pack("<I", size) + b"\0" * 12)
        if cdims is None:
            addr = put(a.tobytes())
            msgs = [_msg(1, space), dtype_msg, _msg(8, bytes([3, 1]) + struct.pack("<QQ", addr, a.nbytes))]
            links.append((name, put(_ohdr(msgs))))
            continue
        placed = []
        for idx in np.ndindex(*[-(-s // c) for s, c in zip(a.shape, cdims)]):
            offs = tuple(i * c for i, c in zip(idx, cdims))
            tile = np.zeros(cdims, a.dtype)  # edge chunks are stored padded
            sl = tuple(slice(o, min(o + c, s)) for o, c, s in zip(offs, cdims, a.shape))
            tile[tuple(slice(0, s.stop - s.start) for s in sl)] = a[sl]
            raw = tile.tobytes()
            if 2 in filt:  # shuffle
                raw = np.frombuffer(raw, np.uint8).reshape(-1, size).T.tobytes()
            if 1 in filt:
                raw = zlib.compress(raw)
            placed.append((offs, put(raw), len(raw)))
        if two_level and len(placed) > 1:
            h = len(placed) // 2
            kids = [(g[0][0], put(_tree(g, rank)), 0) for g in (placed[:h], placed[h:])]
            btree = put(_tree(kids, rank, level=1))
        else:
            btree = put(_tree(placed, rank))
        if old:  # v1: every filter has a name field (empty here) and its client data padded to 8 bytes
            pipe = b"".join(struct.pack("<HHHH", f, 0, 0, 1 if f == 1 else 0)
                            + (b"\x06\0\0\0" + b"\0" * 4 if f == 1 else b"") for f in filt)
            pipe = bytes([1, len(filt)]) + b"\0" * 6 + pipe
        else:
            pipe = bytes([2, len(filt)]) + b"".join(struct.pack("<HHH", f, 0, 1 if f == 1 else 0)
                                                    + (b"\x06\0\0\0" if f == 1 else b"") for f in filt)
        msgs = [
            _msg(1, space), dtype_msg,
            _msg(8, bytes([3, 2, rank + 1]) + struct.pack("<Q", btree)
                 + struct.pack("<" + "I" * (rank + 1), *cdims, size)),
        ]
        if filt:
            msgs.append(_msg(11, pipe))
        links.append((name, put(_ohdr(msgs))))
    link_msgs = [_msg(6, bytes([1, 0, len(n)]) + n.encode() + struct.pack("<Q", addr)) for n, addr in links]
    root = put(_ohdr(link_msgs))
    if old:
        sb = (b"\x89HDF\r\n\x1a\n" + bytes([0, 0, 0, 0, 0, 8, 8, 0]) + struct.pack("<HHI", 4, 16, 0)
              + struct.pack("<QQQQ", 0, 2**64 - 1, len(buf), 2**64 - 1) + struct.pack("<QQII", 0, root, 0, 0)
              + b"\0" * 16)
    else:
        sb = b"\x89HDF\r\n\x1a\n" + bytes([3, 8, 8, 0]) + struct.pack("<QQQQ", 0, 2**64 - 1, len(buf), root)
    buf[:len(sb)] = sb
    return bytes(buf)


@pytest.fixture
def data():
    rng = np.random.default_rng(0)
    return {
        "temp": rng.normal(size=(5, 6)).astype("<f4"),  # ragged edge chunks
        "ice": (rng.random((4, 6)) < 0.5).astype("u1"),
        "lat": np.arange(-3, 3, dtype="<i2"),
    }


@pytest.mark.parametrize("two_level", [False, True])
def test_roundtrip(data, two_level):
    f = build({
        "temp": (data["temp"], (2, 4), [2, 1]),  # shuffle + deflate
        "ice": (data["ice"], (2, 2), [1]),
        "lat": (data["lat"], (4,), []),
    }, two_level=two_level)
    src = BytesSource(f)
    assert variables(src) == ["ice", "lat", "temp"]
    for k in data:
        got = read_variable(src, k)
        assert got.dtype == data[k].dtype and np.array_equal(got, data[k])
    # fetch_gap=0 forces one read per chunk; same answer
    assert np.array_equal(read_variable(src, "temp", fetch_gap=0), data["temp"])


def test_block_average(data):
    src = BytesSource(build({"ice": (data["ice"], (2, 2), [1])}))
    got = read_variable(src, "ice", block=2)
    want = data["ice"].astype("f4").reshape(2, 2, 3, 2).mean((1, 3))
    assert got.dtype == np.float32 and np.allclose(got, want)
    with pytest.raises(ValueError):
        read_variable(src, "ice", block=4)  # does not divide the chunk


def test_rejects_unsupported(data):
    f = build({"ice": (data["ice"], (2, 2), [1])})
    with pytest.raises(ValueError):
        variables(BytesSource(b"not hdf5" + f[8:]))
    with pytest.raises(KeyError):
        read_variable(BytesSource(f), "missing")


def test_old_layout(data):
    """Superblock v0, v1 dataspaces and filter pipelines, contiguous arrays (NOAA PSL's netCDF-4)."""
    f = build({
        "temp": (data["temp"], (2, 4), [2, 1]),
        "ice": (data["ice"], (2, 2), [1]),
        "lat": (data["lat"], None, []),  # contiguous
    }, old=True)
    src = BytesSource(f)
    assert variables(src) == ["ice", "lat", "temp"]
    for k in data:
        got = read_variable(src, k)
        assert got.dtype == data[k].dtype and np.array_equal(got, data[k])


def _ohdr_v1(msgs):
    """A version 1 object header: 16-byte prefix; messages type u16, size u16, flags, 3 reserved,
    bodies padded to 8 bytes."""
    body = b""
    for t, b in msgs:
        b += b"\0" * (-len(b) % 8)
        body += struct.pack("<HHB3x", t, len(b), 0) + b
    return struct.pack("<BBHII", 1, 0, len(msgs), 1, len(body)) + b"\0" * 4 + body


def build_v1(tree):
    """Nested {name: ndarray | dict} -> bytes of a superblock-v0 file with version 1 object
    headers and symbol-table groups (as h5py writes GFED4.1s), contiguous arrays."""
    buf = bytearray(96)

    def put(b):
        buf.extend(b)
        return len(buf) - len(b)

    def dataset(a):
        addr = put(a.tobytes())
        head = {"f": b"\x11\x20", "u": b"\x10\x00", "i": b"\x10\x08"}[a.dtype.kind]
        return put(_ohdr_v1([
            (1, bytes([1, a.ndim, 0, 0]) + b"\0" * 4 + struct.pack("<" + "Q" * a.ndim, *a.shape)),
            (3, head + b"\0\0" + struct.pack("<I", a.dtype.itemsize) + b"\0" * 12),
            (8, bytes([3, 1]) + struct.pack("<QQ", addr, a.nbytes))]))

    def group(members):
        addrs = {n: group(v) if isinstance(v, dict) else dataset(v) for n, v in members.items()}
        names, offs = b"\0" * 8, []  # heap offset 0: the empty name
        for n in addrs:
            offs.append(len(names))
            names += n.encode() + b"\0"
            names += b"\0" * (-len(names) % 8)
        heap = put(b"HEAP" + bytes([0, 0, 0, 0]) + struct.pack("<QQQ", len(names), 2**64 - 1, len(buf) + 32))
        put(names)
        ents = [struct.pack("<QQII16x", o, a, 0, 0) for o, a in zip(offs, addrs.values())]
        # two symbol nodes under a level-1 B-tree node, to exercise the walk
        h = max(1, len(ents) // 2)
        snods = [put(b"SNOD" + bytes([1, 0]) + struct.pack("<H", len(p)) + b"".join(p))
                 for p in (ents[:h], ents[h:]) if p]
        leaf = put(b"TREE" + bytes([0, 0]) + struct.pack("<H", len(snods)) + b"\xff" * 16
                   + b"".join(struct.pack("<QQ", 0, s) for s in snods) + struct.pack("<Q", 0))
        top = put(b"TREE" + bytes([0, 1]) + struct.pack("<H", 1) + b"\xff" * 16 + struct.pack("<QQQ", 0, leaf, 0))
        return put(_ohdr_v1([(0x11, struct.pack("<QQ", top, heap))]))

    root = group(tree)
    sb = (b"\x89HDF\r\n\x1a\n" + bytes([0, 0, 0, 0, 0, 8, 8, 0]) + struct.pack("<HHI", 4, 16, 0)
          + struct.pack("<QQQQ", 0, 2**64 - 1, len(buf), 2**64 - 1) + struct.pack("<QQII", 0, root, 1, 0)
          + b"\0" * 16)
    buf[:len(sb)] = sb
    return bytes(buf)


def test_symbol_table_groups():
    """Superblock v0, version 1 object headers, nested symbol-table groups (GFED4.1s's layout)."""
    rng = np.random.default_rng(1)
    jan, feb = rng.random((3, 4)).astype("<f4"), rng.random((3, 4)).astype("<f4")
    lat = np.arange(3, dtype="<f8")
    src = BytesSource(build_v1({"burned_area": {"01": {"burned_fraction": jan}, "02": {"burned_fraction": feb}},
                                "lat": lat}))
    assert variables(src) == ["burned_area", "lat"]
    assert variables(src, "burned_area") == ["01", "02"]
    assert np.array_equal(read_variable(src, "burned_area/01/burned_fraction"), jan)
    assert np.array_equal(read_variable(src, "burned_area/02/burned_fraction"), feb)
    assert np.array_equal(read_variable(src, "lat"), lat)
    with pytest.raises(KeyError):
        read_variable(src, "burned_area/03/burned_fraction")
