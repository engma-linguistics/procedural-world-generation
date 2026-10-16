"""The viewer's pages parse: each inline script (module or classic) is checked with
`node --check` (a syntax error, or a name declared twice, would leave the page
blank). Skipped where node isn't installed."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parent.parent / "viewer"


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
@pytest.mark.parametrize("page", ["index.html", "zoom.html"])
def test_viewer_scripts_parse(page, tmp_path):
    html = (VIEWER / page).read_text()
    scripts = re.findall(r'<script( type="module")?>(.*?)</script>', html, re.S)  # (not the importmap)
    assert scripts, f"no script in {page}"
    for k, (module, js) in enumerate(scripts):
        f = tmp_path / f"{page}.{k}.{'mjs' if module else 'cjs'}"
        f.write_text(js)
        r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
        assert r.returncode == 0, f"{page} script {k}:\n{r.stderr}"


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
@pytest.mark.parametrize("script", ["zoom3d.js", "zoom3d_look.js", "zoom3d_fly.js", "zoom3d_mesh.js", "relief.js"])
def test_viewer_modules_parse(script, tmp_path):
    """The viewer's own ES modules (zoom3d.js: the zoom's 3D view, PW-072; relief.js: the globe's 3D relief)."""
    f = tmp_path / (Path(script).stem + ".mjs")
    f.write_text((VIEWER / script).read_text())
    r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, f"{script}:\n{r.stderr}"


_GORGE_JS = r"""
import { quadSplits, meshHeight, chaikin, hugChaikin, riverNet } from '%s';
// a river zigzagging down a gorge one pixel wide between 900 m walls, over a 200 m fall on a diagonal
const nx = 12, ny = 14, n = nx * ny;
const L = { elevation: new Float32Array(n).fill(900), water: new Uint8Array(n), lake_depth: new Float32Array(n),
            discharge: new Float32Array(n), drainage_area: new Float32Array(n), ice: new Float32Array(n),
            receiver: new Uint8Array(n).fill(255) };
const moves = [[1, 1], [1, -1], [1, 1], [1, 0], [1, -1], [1, 0], [1, 1], [1, -1], [1, 1], [1, 0], [1, -1]];
const heights = [700, 650, 450, 430, 425, 420, 415, 410, 405, 400, 395, 390];
let r = 1, c = 5; const path = [r * nx + c];
for (const [dr, dc] of moves) {
  const s = 3 * (dr + 1) + (dc + 1);
  L.receiver[r * nx + c] = s - (s > 4);  // (the zoom's D8 slot, planet/zoom.py d8_slots)
  r += dr; c += dc; path.push(r * nx + c);
}
path.forEach((i, k) => { L.elevation[i] = heights[k]; L.discharge[i] = 50 + k; L.drainage_area[i] = 1e4; });
const { rec } = riverNet(L, nx, ny, 1, 10);
const follows = path.slice(0, -1).every((i, k) => rec[i] === path[k + 1]);
const h = L.elevation, P = path.map((i) => [i %% nx, (i / nx) | 0]);
const oldSplit = new Uint8Array((nx - 1) * (ny - 1));
for (let r = 0; r < ny - 1; r++) for (let c = 0; c < nx - 1; c++) {
  const a = r * nx + c; oldSplit[r * (nx - 1) + c] = Math.abs(h[a] - h[a + nx + 1]) <= Math.abs(h[a + 1] - h[a + nx]) ? 1 : 0;
}
const split = quadSplits(h, rec, L.discharge, nx, ny);
// how far the drawn line climbs above its lowest point so far
const climb = (pts, sp) => {
  let lo = Infinity, up = 0;
  for (let j = 0; j < pts.length - 1; j++) for (let t = 0; t < 1; t += 0.125) {
    const v = meshHeight(h, sp, nx, ny, pts[j][1] + t * (pts[j + 1][1] - pts[j][1]), pts[j][0] + t * (pts[j + 1][0] - pts[j][0]));
    lo = Math.min(lo, v); up = Math.max(up, v - lo);
  }
  return up;
};
const H = (x, y) => meshHeight(h, split, nx, ny, y, x);
console.log(JSON.stringify({ follows, path_old: climb(P, oldSplit), path_new: climb(P, split),
  chaikin: climb(chaikin(P), split), hug: climb(hugChaikin(P, H), split),
  corner: meshHeight(h, split, nx, ny, 3, 5) }));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_zoom3d_river_runs_down_its_gorge():
    """PW-375: the 3D mesh splits each quad along a river crossing it diagonally, and the painted
    river's smoothed line stays on the valley floor, so the water never climbs a step below a fall
    (the walls' diagonal had drawn a ridge across the river; smoothing cut corners up the walls)."""
    import json
    js = _GORGE_JS % (VIEWER / "zoom3d_mesh.js").as_uri()
    r = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    assert o["follows"], o
    assert o["path_old"] > 100, o      # (the old split: a ridge across the river)
    assert o["path_new"] < 0.01, o     # along the river's own links: always down
    assert o["chaikin"] > 20, o        # (plain smoothing cuts corners up the walls)
    assert o["hug"] < 2, o             # the painted line: within its 1 m tolerance
    assert abs(o["corner"] - 450) < 1e-3, o  # (pixel centres keep their heights)
