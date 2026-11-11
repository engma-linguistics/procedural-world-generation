"""The globe's level-of-detail tiles (PW-1688): the viewer's tile addressing (viewer/lodmath.js) agrees with
planet/zoom/lod.py, which tiles exist included. The tile service itself: tests/test_tiles.py. Skipped where node isn't
installed."""
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

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


_JS_EXISTS = r"""
import * as M from '%s';
const { outlines, keys } = JSON.parse(require_input());
function require_input() { return process.argv[2]; }
console.log(JSON.stringify(keys.map(([c, l, x, y]) => M.exists(M.key(c, l, x, y), outlines[c]))));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_lodmath_exists_matches_lod_py(tmp_path):
    """has() in the viewer is lod.exists: every level-2 tile of a corner-of-face cell and a middle one, and level-3
    tiles along a level-2 tile that straddles the corner cell's outline."""
    keys = [("pz.0.0", 2, x, y) for y in range(8) for x in range(8)] + [("px.1.1", 2, x, y) for y in range(8) for x in range(8)]
    edge = next(k for k in (L.Key("pz.0.0", 2, x, y) for y in range(8) for x in range(8))
                if L.exists(k) and not all(L.exists(c) for c in L.children(k)))
    keys += [(c.cell, c.level, c.tx, c.ty) for c in L.children(edge)]
    outlines = {c: np.round(L.outline(c), 3).tolist() for c in ("pz.0.0", "px.1.1")}  # (as the tile index sends them)
    f = tmp_path / "e.mjs"
    f.write_text(_JS_EXISTS % (VIEWER / "lodmath.js").as_uri())
    r = subprocess.run(["node", str(f), json.dumps({"outlines": outlines, "keys": keys})], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    got = json.loads(r.stdout)
    want = [L.exists(L.Key(*k)) for k in keys]
    assert got == want
    assert 0 < sum(want) < len(want)  # (some don't exist: the test can tell)
