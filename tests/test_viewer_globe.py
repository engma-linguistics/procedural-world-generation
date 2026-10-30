"""The globe viewer's ES modules (viewer/globe/, split out of index.html's one inline script): every module parses,
and the whole import graph links. Linking is checked by node's vm modules without running anything: an import of a
name another module doesn't export, or a name declared twice, fails here instead of leaving the page blank. three.js
(loaded from a CDN by the page's import map) is stood in for by empty modules exporting the names asked of them.
Skipped where node isn't installed."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parent.parent / "viewer"
GLOBE = VIEWER / "globe"

_LINK_JS = r"""
import vm from 'node:vm';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
const entry = process.argv[2];
const cache = new Map();
const ctx = vm.createContext({});
// names imported from three (bare specifiers) by any module, so the stand-ins export them
const wanted = new Map();
function scanImports(src) {
  for (const m of src.matchAll(/import\s*\{([^}]*)\}\s*from\s*'(three[^']*)'/g)) {
    const s = wanted.get(m[2]) || new Set();
    m[1].split(',').map((x) => x.trim().split(/\s+as\s+/)[0]).filter(Boolean).forEach((n) => s.add(n));
    wanted.set(m[2], s);
  }
}
function load(file) {
  if (cache.has(file)) return cache.get(file);
  const src = fs.readFileSync(file, 'utf8');
  scanImports(src);
  const m = new vm.SourceTextModule(src, { identifier: pathToFileURL(file).href, context: ctx });
  cache.set(file, m);
  return m;
}
function stand(spec) {
  const key = 'three:' + spec;
  if (!cache.has(key)) {
    const names = [...(wanted.get(spec) || [])];
    cache.set(key, new vm.SyntheticModule(names, function () { names.forEach((n) => this.setExport(n, undefined)); }, { context: ctx, identifier: spec }));
  }
  return cache.get(key);
}
async function linker(spec, ref) {
  if (spec.startsWith('three')) return stand(spec);
  return load(path.resolve(path.dirname(fileURLToPath(ref.identifier)), spec));
}
// read every module first, so the three stand-ins know all the names asked of them
const root = load(entry);
for (const f of fs.readdirSync(path.dirname(entry))) if (f.endsWith('.js')) load(path.join(path.dirname(entry), f));
await root.link(linker);
const mods = [...cache.keys()].filter((k) => !k.startsWith('three:')).map((k) => path.relative(path.dirname(entry), k));
console.log(JSON.stringify({ linked: mods.length, mods }));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
@pytest.mark.parametrize("script", sorted(p.name for p in GLOBE.glob("*.js")))
def test_globe_modules_parse(script, tmp_path):
    f = tmp_path / (Path(script).stem + ".mjs")
    f.write_text((GLOBE / script).read_text())
    r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, f"{script}:\n{r.stderr}"


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_globe_modules_link(tmp_path):
    run = tmp_path / "link.mjs"
    run.write_text(_LINK_JS)
    r = subprocess.run(["node", "--experimental-vm-modules", "--no-warnings", str(run), str(GLOBE / "main.js")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout.strip().splitlines()[-1])
    # main.js reaches every module in the folder
    assert {Path(m).name for m in out["mods"] if not m.startswith("..")} == {p.name for p in GLOBE.glob("*.js")}


def test_index_loads_the_globe_modules():
    """index.html keeps the markup and loads globe/main.js; no inline module left to drift."""
    html = (VIEWER / "index.html").read_text()
    assert '<script type="module" src="globe/main.js"></script>' in html
    assert not re.search(r'<script type="module">', html)
