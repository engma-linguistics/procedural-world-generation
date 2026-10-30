"""The viewer's pages parse: each inline script (module or classic) is checked with
`node --check` (a syntax error, or a name declared twice, would leave the page
blank). Skipped where node isn't installed."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parent.parent / "viewer"


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
@pytest.mark.parametrize("page", ["zoom.html", "lineages.html"])  # (index.html: its modules, test_viewer_globe.py)
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
@pytest.mark.parametrize("script", ["zoom3d.js", "zoom3d_look.js", "zoom3d_fly.js", "zoom3d_mesh.js", "zoom3d_place.js", "relief.js",
                                    "planets.js", "start.js", "navigator.js", "projmap.js"])
def test_viewer_modules_parse(script, tmp_path):
    """The viewer's own ES modules (zoom3d.js: the zoom's 3D view, PW-072; relief.js: the globe's 3D relief)."""
    f = tmp_path / (Path(script).stem + ".mjs")
    f.write_text((VIEWER / script).read_text())
    r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, f"{script}:\n{r.stderr}"


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
@pytest.mark.parametrize("script", ["pickfilter.js", "techtab.js"])
def test_viewer_classic_scripts_parse(script, tmp_path):
    """The classic scripts the pages load with <script src> (pickfilter.js: the pickers' filter box, PW-407; techtab.js:
    the peoples workbench's Technology tab, PW-913)."""
    f = tmp_path / (Path(script).stem + ".cjs")
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
  L.receiver[r * nx + c] = s - (s > 4);  // (the zoom's D8 slot, planet/zoom/regional.py d8_slots)
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


_COARSE_JS = r"""
import { quadSplits, coarseMesh, meshAt, meshHeight } from '%s';
// a 1 px gorge (as _GORGE_JS) across a 40 x 37 tile of rough walls, meshed at half and quarter detail
const nx = 40, ny = 37, n = nx * ny;
let seed = 3; const rnd = () => ((seed = (seed * 16807) %% 2147483647) / 2147483647);
const h = Float32Array.from({ length: n }, () => 800 + 200 * rnd());
const rec = new Int32Array(n).fill(-1), q = new Float32Array(n), keep = new Uint8Array(n);
let r = 0, c = 7; const path = [c];
for (let k = 0; r < ny - 1; k++) { r++; c += [1, 1, 0, -1, 0, 1, -1, 0][k %% 8]; path.push(r * nx + c); }
path.forEach((i, k) => { h[i] = 600 - 5 * k - (k > 6 ? 150 : 0); q[i] = 50; keep[i] = 1; if (k) rec[path[k - 1]] = i; });
const split = quadSplits(h, rec, q, nx, ny), out = {};
for (const step of [1, 2, 4]) {
  const m = coarseMesh(h, split, keep, nx, ny, step);
  // a tiling: every triangle counter-clockwise from above (z south), areas summing to the tile's,
  // every inner edge shared by exactly two triangles (no cracks, no overlaps)
  const P = (v) => { const i = m.vert[v]; return [i %% nx, (i / nx) | 0]; };
  let area = 0, flipped = 0; const edges = new Map();
  for (let t = 0; t < m.idx.length; t += 3) {
    const [a, b, d] = [P(m.idx[t]), P(m.idx[t + 1]), P(m.idx[t + 2])];
    const s = (b[0] - a[0]) * (d[1] - a[1]) - (d[0] - a[0]) * (b[1] - a[1]);
    if (s >= 0) flipped++;
    area += Math.abs(s) / 2;
    for (const [u, v] of [[m.idx[t], m.idx[t + 1]], [m.idx[t + 1], m.idx[t + 2]], [m.idx[t + 2], m.idx[t]]]) {
      const key = Math.min(u, v) + ',' + Math.max(u, v); edges.set(key, (edges.get(key) || 0) + 1);
    }
  }
  const once = [...edges.values()].filter((x) => x === 1).length, more = [...edges.values()].filter((x) => x > 2).length;
  // the river's course on the drawn mesh: how far it climbs above its lowest point so far
  let lo = Infinity, up = 0;
  for (let j = 0; j < path.length - 1; j++) for (let t = 0; t < 1; t += 0.125) {
    const a = path[j], b = path[j + 1];
    const rr = ((a / nx) | 0) * (1 - t) + ((b / nx) | 0) * t, cc = (a %% nx) * (1 - t) + (b %% nx) * t;
    const v = meshAt(h, split, m, nx, ny, rr, cc);
    lo = Math.min(lo, v); up = Math.max(up, v - lo);
  }
  // meshAt agrees with the full mesh in a block kept at full detail, and at every vertex
  const vOk = [...m.vert].every((i) => Math.abs(meshAt(h, split, m, nx, ny, (i / nx) | 0, i %% nx) - h[i]) < 1e-3);
  out[step] = { area, flipped, boundary: once, ring: m.ring.length - 1, more, climb: up, vOk, tris: m.idx.length / 3 };
}
console.log(JSON.stringify(out));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_zoom3d_coarse_mesh_keeps_the_rivers():
    """PW-376: at half and quarter detail the mesh keeps the blocks round the drawn rivers at full
    detail (fans round the centre of their coarse neighbours, so no cracks), and a river in a gorge
    one pixel wide stays on its floor instead of riding over the walls between the coarse corners."""
    import json
    js = _COARSE_JS % (VIEWER / "zoom3d_mesh.js").as_uri()
    r = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    for step, s in o.items():
        assert abs(s["area"] - 39 * 36) < 1e-6 and s["flipped"] == 0 and s["more"] == 0, (step, s)
        assert s["boundary"] == s["ring"] and s["vOk"], (step, s)
        assert s["climb"] < 0.01, (step, s)
    assert o["4"]["tris"] < o["2"]["tris"] < o["1"]["tris"] == 2 * 39 * 36


_PLACE_JS = r"""
import { aeFrame, latlonOf, place } from '%s';
// a 50 km fine zoom 66.5 km east and 9.6 km south of a 1 km/px zoom's centre (as 97b3e7 in 170672)
const root = { lat: 16.3, lon: 155.1 }, R = aeFrame(root.lat, root.lon);
const [la, lo] = latlonOf(R.toSphere(66.5, -9.6)), F = aeFrame(la, lo);
const pl = place({ lat: la, lon: lo }, root, 50, 50), [a, b, c, d] = pl.M;
let miss = 0;
for (const [x, z] of [[-25, -25], [25, 25], [10, -20], [0, 0], [-25, 25]]) {
  const [X, Y] = R.toPlane(F.toSphere(x, -z));
  miss = Math.max(miss, Math.hypot(a * x + b * z + pl.T[0] - X, c * x + d * z + pl.T[1] + Y));
}
console.log(JSON.stringify({ miss, err: pl.err, T: pl.T, same: place(root, root, 500, 500) }));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_zoom3d_fine_tile_placed_by_reprojection():
    """A fine zoom's tile (PW-129) lands where reprojecting its pixels puts them: the
    affine fit misses by under a metre, and a zoom in its own frame is the identity."""
    js = _PLACE_JS % (VIEWER / "zoom3d_place.js").as_uri()
    r = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["miss"] < 0.001 and out["err"] < 0.001
    assert abs(out["T"][0] - 66.5) < 0.01 and abs(out["T"][1] - 9.6) < 0.01
    s = out["same"]
    assert abs(s["M"][0] - 1) < 1e-9 and abs(s["M"][1]) < 1e-9 and abs(s["T"][0]) < 1e-6


_LAKE_JS = r"""
import { lakeSurfaces, quadSplits, meshHeight } from '%s';
// a 20 x 20 slope (rising 30 m per pixel to the east) with a 2 x 1 lake basin dug in it
const nx = 20, ny = 20, n = nx * ny;
const h = Float32Array.from({ length: n }, (_, i) => 30 * (i %% nx));
const water = new Uint8Array(n), depth = new Float32Array(n);
for (const [r, c] of [[10, 10], [10, 11]]) { water[r * nx + c] = 2; depth[r * nx + c] = 40; h[r * nx + c] -= 40; }
// (the two pixels' stored levels differ by the slope, 300 and 330 m: the lake takes their mean)
const rec = new Int32Array(n).fill(-1), q = new Float32Array(n);
const split = quadSplits(h, rec, q, nx, ny);
const S = lakeSurfaces(h, water, depth, split, nx, ny, null);
const ys = new Set(); let outside = 0, above = 0;
for (let t = 0; t < S.pos.length; t += 3) {
  ys.add(S.pos[t + 1].toFixed(3));
  const c = S.pos[t], r = S.pos[t + 2];
  if (Math.abs(r - 10) > 1.0001 || c < 9 || c > 12) outside++;
}
// at the shore the ground meets the level (no water over ground above the level)
for (let t = 0; t < S.pos.length; t += 9) {
  const cx = (S.pos[t] + S.pos[t + 3] + S.pos[t + 6]) / 3, cy = (S.pos[t + 2] + S.pos[t + 5] + S.pos[t + 8]) / 3;
  if (meshHeight(h, split, nx, ny, cy, cx) > S.pos[t + 1] + 1e-3) above++;
}
console.log(JSON.stringify({ levels: S.levels.length, ys: [...ys], outside, above, tris: S.pos.length / 9 }));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_zoom3d_lake_is_one_flat_clipped_surface():
    """PW-537: a lake on a slope is ONE flat surface at its level (not tilting with the ground), cut
    where the ground rises through it, and it has no water away from its own pixels."""
    import json
    js = _LAKE_JS % (VIEWER / "zoom3d_mesh.js").as_uri()
    r = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    o = json.loads(r.stdout)
    assert o["levels"] == 1 and len(o["ys"]) == 1, o   # one lake, one level
    assert o["outside"] == 0 and o["tris"] > 0, o      # no orphan water
    assert o["above"] == 0, o                          # nowhere over higher ground


def test_brief_endpoint_rejects_bad_requests():
    """GET /api/brief (PW-837) answers 400 for a missing run or target, 404 for a run that doesn't exist."""
    from planet import server
    assert server.brief("people=x")[1] == 400
    assert server.brief("run=nope")[1] == 400
    assert server.brief("run=no-such-run-xyz&people=orc")[1] == 404


def test_peoples_editor_has_no_copied_option_lists():
    """PW-1033: the peoples editor (viewer/lineages.html) takes its option lists and defaults from GET /api/lineage-schema
    (planet/lineages/run.editor_schema, from spec.py, land.GOODS and dragon_ages), so none may be copied into it:
    no two neighbouring values of any list appear as a literal sequence, no goods label is copied, and the stale
    "candidates" and "nothing reads it yet" texts are gone. The schema itself answers for every list."""
    from planet.lineages import run as LR
    from planet.lineages import spec as SP
    from planet.lineages import land as LD
    d = LR.editor_schema()
    assert set(d["traits"]) == set(SP.TRAITS) and {"aggressive", "hunter"} <= set(d["traits"])
    assert {"fish", "shellfish", "salt", "salt_rock", "sea_mammals"} <= set(d["goods"]) == set(LD.GOODS)
    assert [k for k, _ in d["megafauna_natural"]] == list(SP.MEGAFAUNA_NATURAL) and d["defaults"]["megafauna_natural"] == "food"
    assert "grain" in d["body_choices"] and set(d["body_default"]) == set(SP.BODY_DEFAULT)
    html = (VIEWER / "lineages.html").read_text()
    lists = [d[k] for k in ("traits", "places", "groups", "ways", "realms", "toxins", "eras", "modes", "portal_modes",
                            "dragon_ages", "dragon_generation", "pair_wants", "stages")]
    assert d["pair_wants"] == list(SP.PAIR_WANTS) and d["stages"] == list(SP.STAGES) and set(d["stage_notes"]) == set(SP.STAGES)
    lists += [[k for k, _ in d["megafauna_natural"]], list(d["goods"])] + list(d["body_choices"].values())
    for vals in lists:
        for a, b in zip(vals, vals[1:]):
            assert not re.search(rf"""['"]{re.escape(a)}['"]\s*,\s*['"]{re.escape(b)}['"]""", html), (a, b)
    for k, label in d["goods"].items():
        assert f"'{label}'" not in html, k
    assert "fertile: 'farmland'" not in html
    assert "density: 2.0" not in html and "Candidates until" not in html and "nothing reads it yet" not in html
    assert "/api/lineage-schema" in html
