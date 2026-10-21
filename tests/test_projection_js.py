"""viewer/projmap.js (the viewer's 2D map, PW-477) agrees with planet/projection.py: the same
forward and inverse maps for every projection and a few centres. Skipped where node isn't installed."""

import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from planet import projection as PJ
from planet.geo import xyz

VIEWER = Path(__file__).resolve().parent.parent / "viewer"
CENTERS = [(0, 0), (48.5, -2.5), (-70, 150), (90, 10)]

_JS = """
import * as PM from '%s';
const pts = %s, out = {};
for (const name of PM.NAMES) for (const [la, lo] of %s) {
  const pr = PM.makeProjection(name, la, lo), fw = [], back = [], q = [0, 0, 0];
  for (const p of pts) {
    const f = pr.forward(p);
    fw.push(f ? [f[0], f[1]] : null);
    back.push(f && pr.unproject(f[0], f[1], q) ? [q[0], q[1], q[2]] : null);
  }
  out[`${name}|${la}|${lo}`] = { fw, back, ext: pr.fullExtent() };
}
console.log(JSON.stringify(out));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_js_matches_python(tmp_path):
    rng = np.random.default_rng(4)
    p = rng.normal(size=(300, 3))
    p /= np.linalg.norm(p, axis=1, keepdims=True)
    mod = tmp_path / "projmap.mjs"
    mod.write_text((VIEWER / "projmap.js").read_text())
    run = tmp_path / "run.mjs"
    run.write_text(_JS % (mod.as_posix(), json.dumps(p.tolist()), json.dumps(CENTERS)))
    r = subprocess.run(["node", str(run)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    for name in PJ.NAMES:
        for c in CENTERS:
            pr = PJ.Projection(name, *c)
            got = out[f"{name}|{c[0]}|{c[1]}"]
            x, y = pr.project(p)
            for k in range(len(p)):
                f = got["fw"][k]
                if np.isfinite(x[k]):
                    assert f is not None, (name, c, k)
                    assert abs(f[0] - x[k]) < 1e-9 and abs(f[1] - y[k]) < 1e-9, (name, c, k)
                    assert got["back"][k] is not None and np.abs(np.array(got["back"][k]) - p[k]).max() < 1e-6, (name, c, k)
                else:
                    assert f is None, (name, c, k)
            assert np.allclose(got["ext"], pr.full_extent())


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_js_pixel_grid_and_cells(tmp_path):
    """The pixel grid matches pixel_grid, and cellMap finds each pixel's nearest point."""
    mod = tmp_path / "projmap.mjs"
    mod.write_text((VIEWER / "projmap.js").read_text())
    run = tmp_path / "run.mjs"
    run.write_text(f"""import * as PM from '{mod.as_posix()}';
const pr = PM.makeProjection('laea', 30, 40), g = PM.pixelGrid(pr, 64, [2000, 1000]);
const cells = PM.cellMap(pr, g, (x, y, z) => (z > 0.5 ? 1 : 0));
console.log(JSON.stringify({{g, n: cells.length, ones: cells.reduce((a, b) => a + (b === 1), 0)}}));""")
    r = subprocess.run(["node", str(run)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    g = PJ.pixel_grid(PJ.Projection("laea", 30, 40), 64, (2000, 1000))
    assert (out["g"]["width"], out["g"]["height"]) == (g["width"], g["height"])
    assert abs(out["g"]["step"] - g["step"]) < 1e-12
    assert out["n"] == g["width"] * g["height"] and 0 < out["ones"] < out["n"]
