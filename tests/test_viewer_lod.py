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


_JS_GROUND = r"""
import * as M from '%s';
const { n, gn, h } = JSON.parse(process.argv[2]);
const half = Uint16Array.from(h), vh = M.gridHeights(half, n, gn);
const at = (u, v) => M.meshHeightAt(vh, gn, u, v);
// at the grid's vertices; across the diagonal of a quad (its two triangles); across a row of vertices
const verts = [[0, 0], [1, 0], [0, 1], [1, 1], [5, 7], [gn - 1, gn - 1]].map(([i, j]) => [vh[j * gn + i], at(i / (gn - 1), j / (gn - 1))]);
const e = 1e-7, i = 3, j = 4, s = 1 / (gn - 1);
const diag = [0.2, 0.5, 0.8].map((t) => [at((i + 1 - t) * s - e, (j + t) * s - e), at((i + 1 - t) * s + e, (j + t) * s + e)]);
const row = [0.25, 0.5].map((t) => [at((i + t) * s, j * s - e), at((i + t) * s, j * s + e)]);
const tilt = [0.3, 1.5, 20, 199.9, 200, 200.1, 500, 999, 1000, 20000].map((k) => [k, M.autoTilt(k), M.capTilt(k)]);
console.log(JSON.stringify({ verts, diag, row, tilt, T: M.TILT }));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_lodmath_tile_ground_and_tilt(tmp_path):
    """PW-1696. The tile mesh's ground (gridHeights, meshHeightAt; the camera's least height and the draped overlays stand
    on it): the grid's vertex heights at the vertices (the elevation sampled as the vertex shader samples it, the sea at
    0), continuous across a quad's diagonal and between quads. The tilt: 0 above 200 km (automatic) and 1,000 km (the
    cap), growing as the camera comes down, the automatic one within the cap, so scrolling out always ends straight down."""
    rng = np.random.default_rng(3)
    n, gn = 40, 9
    elev = rng.normal(300, 400, (n, n)).astype(np.float16)  # (some below the sea)
    f = tmp_path / "g.mjs"
    f.write_text(_JS_GROUND % (VIEWER / "lodmath.js").as_uri())
    arg = {"n": n, "gn": gn, "h": elev.view(np.uint16).ravel().tolist()}
    r = subprocess.run(["node", str(f), json.dumps(arg)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    got = json.loads(r.stdout)
    for want, have in got["verts"]:
        assert want >= 0 and abs(want - have) < 1e-3
    e = np.maximum(elev.astype(np.float64), 0)
    fx, fy = 5 / (gn - 1) * n - 0.5, 7 / (gn - 1) * n - 0.5
    x0, y0 = int(np.floor(fx)), int(np.floor(fy))
    ax, ay = fx - x0, fy - y0
    v57 = (1 - ay) * ((1 - ax) * e[y0, x0] + ax * e[y0, x0 + 1]) + ay * ((1 - ax) * e[y0 + 1, x0] + ax * e[y0 + 1, x0 + 1])
    assert abs(got["verts"][4][0] - v57) < 1e-2
    for a, b in got["diag"] + got["row"]:
        assert abs(a - b) < 1e-2
    T = got["T"]
    for k, auto, cap in got["tilt"]:
        assert 0 <= auto <= cap + 1e-12
        if k >= T["AUTO_HI_KM"]:
            assert auto == 0
        if k >= T["CAP_HI_KM"]:
            assert cap == 0
    autos = [a for _, a, _ in got["tilt"]]
    assert autos == sorted(autos, reverse=True) and abs(autos[1] - np.radians(T["AUTO_DEG"])) < 1e-9


def test_tile_children_grid_and_no_double_click():
    """lodtiles.js: a tile's children grid (KIDS_PX) splits evenly at every level's branching, down to level 4 (PW-1673
    step 5); the globe has no double-click zoom (PW-1710: scroll dives, the zoom tab and picker make zooms)."""
    import re
    from planet.zoom import lod
    root = Path(__file__).resolve().parents[1] / "viewer" / "globe"
    src = (root / "lodtiles.js").read_text()
    kids = int(re.search(r"const KIDS_PX = (\d+)", src).group(1))
    for level in range(1, max(lod.LEVELS)):
        assert kids % lod.branching(level) == 0, (level, kids)
    assert "maxLevel: Math.min(+P.get('lodmax') || M.FINEST, M.FINEST)" in src
    pick = (root / "pick.js").read_text()
    assert "addEventListener('dblclick'" not in pick and "double-click: zoom" not in pick and "double-click to zoom" not in pick


_JS_CELL = r"""
import * as M from '%s';
const { ids, pts } = JSON.parse(process.argv[2]);
const cs = ids.map((id) => M.cellAngles(id));
console.log(JSON.stringify(pts.map((p) => cs.map((c) => M.inCellAngles(c, p)))));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_tile_clip_is_tiling_locate(tmp_path):
    """The tile shader's clip at the cell edge (lodmath.js::cellAngles, inCellAngles; PW-1673 step 6) is tiling.locate:
    every point of the sphere in exactly one cell, that one, points close to edges, corners and face edges included."""
    from planet.zoom import lod_build as LB
    from planet.zoom import tiling as ZT
    ids = [f"{f}.{i}.{j}" for f in ZT.FACES for i in range(3) for j in range(3)]
    rng = np.random.default_rng(3)
    P = rng.normal(size=(1500, 3))
    near = np.concatenate([LB._line("py.0.1", "py.1.1")[::200], LB._line("px.2.1", "py.0.1")[::200],
                           np.array([c[1] for c in LB.cell_corners("py.0.0")])])
    P = np.concatenate([P, near + 1e-6 * rng.normal(size=near.shape)])  # (within ~6 m of an edge or a corner)
    P /= np.linalg.norm(P, axis=1, keepdims=True)
    assert ZT.choose_n(L.SQUARE_KM, 190.0) == 3
    f = tmp_path / "c.mjs"
    f.write_text(_JS_CELL % (VIEWER / "lodmath.js").as_uri())
    r = subprocess.run(["node", str(f), json.dumps({"ids": ids, "pts": P.tolist()})], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    got = np.array(json.loads(r.stdout))
    face, i, j = ZT.locate(P, 3)
    want = [f"{list(ZT.FACES)[a]}.{b}.{c}" for a, b, c in zip(face, i, j)]
    assert (got.sum(axis=1) == 1).all()
    assert [ids[k] for k in got.argmax(axis=1)] == want
