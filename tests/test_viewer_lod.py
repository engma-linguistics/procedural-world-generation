"""The globe's level-of-detail tiles (PW-1688): the viewer's tile addressing (viewer/lodmath.js) agrees with
planet/zoom/lod.py, and the STAND-IN tile source (planet/tiles_standin.py) serves a section zoom as level-1 and level-2
tiles on the lod lattice. The JS half is skipped where node isn't installed."""
import json
import shutil
import struct
import subprocess
import zlib
from pathlib import Path

import numpy as np
import pytest

from planet import store as S
from planet import tiles_standin as TS
from planet.images import png_bytes
from planet.zoom import lod as L

VIEWER = Path(__file__).resolve().parent.parent / "viewer"

_JS = r"""
import * as M from '%s';
const keys = JSON.parse(process.argv[2]);
const out = keys.map(([c, l, x, y]) => { const k = M.key(c, l, x, y), p = M.parent(k);
  return { rect: M.rect(k), parent: p && [p.level, p.tx, p.ty], kids: M.children(k).map((q) => [q.tx, q.ty]),
           at: (() => { const [cx, cy] = M.centreXY(k), t = M.tileAt(c, l, cx, cy); return [t.tx, t.ty]; })(),
           px: M.tilePx(l), side: M.perSide(l) }; });
const halves = [0x3c00, 0xc000, 0x7bff, 0x0001, 0x5640].map(M.halfToFloat);
console.log(JSON.stringify({ out, halves }));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_lodmath_matches_lod_py(tmp_path):
    keys = [("py.1.1", 1, 0, 0), ("py.1.1", 2, 3, 4), ("pz.0.0", 2, 7, 0), ("px.2.1", 3, 17, 30), ("nx.0.2", 4, 211, 9)]
    f = tmp_path / "t.mjs"
    f.write_text(_JS % (VIEWER / "lodmath.js").as_uri())
    r = subprocess.run(["node", str(f), json.dumps(keys)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    got = json.loads(r.stdout)
    for (c, lv, x, y), g in zip(keys, got["out"]):
        k = L.Key(c, lv, x, y)
        assert np.allclose(g["rect"], L.rect(k))
        p = L.parent(k)
        assert g["parent"] == (None if p is None else [p.level, p.tx, p.ty])
        assert g["kids"] == [[q.tx, q.ty] for q in L.children(k)]
        assert g["at"] == [x, y]
        assert g["px"] == L.tile_px(lv) and g["side"] == L.per_side(lv)
    assert got["halves"] == [float(np.frombuffer(np.uint16(h).tobytes(), np.float16)[0]) for h in (0x3c00, 0xc000, 0x7bff, 0x0001, 0x5640)]


def _filtered_png(img: np.ndarray) -> bytes:
    """An RGB PNG whose rows use every filter type (png_bytes writes filter 0 only)."""
    h, w, ch = img.shape
    raw, prev = [], np.zeros(w * ch, np.int32)
    for y in range(h):
        row, f = img[y].reshape(-1).astype(np.int32), y % 5
        a = np.concatenate([np.zeros(ch, np.int32), row[:-ch]])
        c = np.concatenate([np.zeros(ch, np.int32), prev[:-ch]])
        if f == 0:
            enc = row
        elif f == 1:
            enc = row - a
        elif f == 2:
            enc = row - prev
        elif f == 3:
            enc = row - (a + prev) // 2
        else:
            p = a + prev - c
            pa, pb, pc = abs(p - a), abs(p - prev), abs(p - c)
            enc = row - np.where((pa <= pb) & (pa <= pc), a, np.where(pb <= pc, prev, c))
        raw.append(bytes([f]) + (enc & 255).astype(np.uint8).tobytes())
        prev = row

    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"".join(raw))) + chunk(b"IEND", b""))


def test_read_png_undoes_every_filter(tmp_path):
    img = np.random.default_rng(3).integers(0, 256, (23, 17, 3), dtype=np.uint8)
    (tmp_path / "a.png").write_bytes(_filtered_png(img))
    (tmp_path / "b.png").write_bytes(png_bytes(img))
    assert np.array_equal(TS.read_png(tmp_path / "a.png"), img)
    assert np.array_equal(TS.read_png(tmp_path / "b.png"), img)


@pytest.fixture
def section_root(tmp_path):
    """A data root with world w00001 and a fake 4 km section zoom of cell py.1.1 on the lod lattice."""
    (tmp_path / "worlds").mkdir()
    (tmp_path / "worlds" / "w00001.json").write_text(json.dumps({"meta": {"id": "w00001", "name": "test"}}))
    d = tmp_path / "zooms" / "z00001"
    (d / "layers").mkdir(parents=True)
    n = 1000
    yy, xx = np.mgrid[0:n, 0:n]
    elev = (xx * 10.0 - yy).astype(np.float32)  # metres: known values per pixel
    water = (elev < 0).astype(np.uint8)
    (d / "layers" / "elevation.bin").write_bytes(elev.tobytes())
    (d / "layers" / "water.bin").write_bytes(water.tobytes())
    sat = np.stack([xx % 256, yy % 256, (xx + yy) % 256], -1).astype(np.uint8)
    (d / "satellite.png").write_bytes(png_bytes(sat))
    meta = {"id": "z00001", "name": "s", "created": "2026-11-10", "source_world": {"id": "w00001"}, "center": {"lat": 0, "lon": 90},
            "section": "py.1.1", "size_km": 4000.0, "res_km": 4.0, "nx": n, "ny": n, "files": {"satellite": "satellite.png"},
            "layers": {"elevation": {"file": "layers/elevation.bin", "dtype": "float32", "shape": [n, n], "scale": 1, "offset": 0, "transform": None},
                       "water": {"file": "layers/water.bin", "dtype": "uint8", "shape": [n, n], "scale": 1, "offset": 0, "transform": None}}}
    (d / "zoom.json").write_text(json.dumps(meta))
    S.set_root(tmp_path)
    yield tmp_path, elev, sat
    S.set_root(None)


def test_standin_serves_a_section_as_level_1_and_2(section_root):
    root, elev, sat = section_root
    ix = TS.index("w00001")
    assert ix["standin"] and [c["id"] for c in ix["cells"]] == ["py.1.1"]
    c = ix["cells"][0]
    assert c["tiles"]["1"] == [[0, 0]] and len(c["tiles"]["2"]) == sum(L.exists(L.Key("py.1.1", 2, x, y)) for x in range(8) for y in range(8))
    # level 1: the whole section; float16 elevation in lattice order, then water
    body, ct = TS.tile_file("w00001", L.Key("py.1.1", 1, 0, 0), "view.bin")
    assert body[:4] == b"PWT1" and struct.unpack("<i", body[4:8])[0] == 1000
    e = np.frombuffer(body[8:8 + 2 * 1000 * 1000], "<f2").reshape(1000, 1000)
    assert np.allclose(e, elev, atol=4)  # (float16: steps of 4 m at ~9,000 m)
    # level 2 from a 4 km section: 125 px slices, row ty and column tx of the lattice
    k = L.Key("py.1.1", 2, 3, 5)
    body, _ = TS.tile_file("w00001", k, "view.bin")
    m = struct.unpack("<i", body[4:8])[0]
    assert m == 125
    e2 = np.frombuffer(body[8:8 + 2 * m * m], "<f2").reshape(m, m)
    assert np.allclose(e2, elev[5 * 125:6 * 125, 3 * 125:4 * 125], atol=4)
    png, ct = TS.tile_file("w00001", k, "satellite.png")
    assert ct == "image/png"
    (root / "t.png").write_bytes(png)
    assert np.array_equal(TS.read_png(root / "t.png"), sat[5 * 125:6 * 125, 3 * 125:4 * 125])
    lay, _ = TS.tile_file("w00001", k, "layer/elevation.bin")
    assert np.array_equal(np.frombuffer(lay, "<f4").reshape(m, m), elev[5 * 125:6 * 125, 3 * 125:4 * 125])
    # what it can't serve: a missing layer, a level it has no source for, a malformed path
    assert TS.get("/api/tiles/w00001/py.1.1/2/3/5/layer/nope.bin", "")[1] == 404
    assert TS.get("/api/tiles/w00001/py.1.1/3/0/0/view.bin", "")[1] == 404
    assert TS.get("/api/tiles/w00001/py.0.1/1/0/0/view.bin", "")[1] == 404
    assert TS.get("/api/tiles/w00001/py.1.1/x/0/0/view.bin", "")[1] == 400
