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


_LAYERS_JS = r"""
// The LAYERS table's own consistency: layers.js evaluated alone, its imports stood in for.
import vm from 'node:vm';
import fs from 'node:fs';
import path from 'node:path';
const dir = process.argv[2];
const dummy = new Proxy(function () {}, { get: (t, k) => (k === Symbol.toPrimitive ? () => '' : k === 'then' ? undefined : dummy), apply: () => dummy, construct: () => dummy, set: () => true });
const S = { V: { kind: 'world', layers: {}, run: null } };
const all = new Proxy({}, { get: () => [1], has: () => true });
const special = {
  './state.js': { S, state: { layer: 'biome' }, proj: {} },
  './load.js': { hasLayer: () => true },
  './colours.js': { animalStocks: () => ({ horse: {} }), cropStocks: () => ({ wheat: {} }) },
};
const ctx = vm.createContext({ console });
const src = fs.readFileSync(path.join(dir, 'layers.js'), 'utf8') + '\nexport { LAYERS as __LAYERS, MENUS as __MENUS, FAMILIES as __FAMILIES };\n';
const names = (spec) => {
  const s = new Set();
  for (const m of src.matchAll(/import\s*(?:\*\s*as\s*\w+|\{([^}]*)\})\s*from\s*'([^']*)'/g)) if (m[2] === spec && m[1]) m[1].split(',').map((x) => x.trim().split(/\s+as\s+/)[0]).filter(Boolean).forEach((n) => s.add(n));
  return [...s, ...Object.keys(special[spec] || {})];
};
const mod = new vm.SourceTextModule(src, { context: ctx, identifier: 'layers.js' });
const stands = new Map();
await mod.link((spec) => {
  if (!stands.has(spec)) {
    const ns = [...new Set(spec === 'three' ? ['Color'] : names(spec))], vals = special[spec] || {};
    stands.set(spec, new vm.SyntheticModule(ns.length ? ns : ['default'], function () { for (const n of ns) this.setExport(n, n in vals ? vals[n] : dummy); }, { context: ctx, identifier: spec }));
  }
  return stands.get(spec);
});
await mod.evaluate();
const { __LAYERS: L, __MENUS: M, __FAMILIES: F, availableLayers, layerDef } = mod.namespace;
const bad = [];
const KINDS = ['world', 'run', 'tz'];
for (const [k, ids] of Object.entries(M)) for (const id of ids) if (!L[id] && !id.startsWith('@')) bad.push(`menu ${k}: ${id} is not in LAYERS`);
for (const [id, d] of Object.entries(L)) {
  if (id.startsWith('@')) continue;  // a family's place in the menus
  if (!d.color && !d.ramp) bad.push(`${id}: neither color nor ramp`);
  if (d.ramp && !d.units) bad.push(`${id}: a ramp without units`);
  if (!d.group) bad.push(`${id}: no group`);
  for (const k of Object.keys(d.in || {})) if (!KINDS.includes(k)) bad.push(`${id}: in.${k}?`);
  if (!d.in || !Object.keys(d.in).some((k) => M[k].includes(id))) bad.push(`${id}: in no menu that lists it`);
  for (const k of Object.keys(d.in || {})) if (!M[k].includes(id)) bad.push(`${id}: in.${k} but menu ${k} doesn't list it`);
}
for (const [p, f] of Object.entries(F)) for (const k of Object.keys(f.in)) if (!M[k].includes('@' + p.split(':')[0])) bad.push(`family ${p}: in.${k} but not in menu ${k}`);
// every view kind with every layer present: the buttons it offers all have entries
for (const V of [{ kind: 'world', layers: all, humanUse: {}, resLeg: {}, coastLeg: {}, wAnthroRun: { fuels: {} } },
  { kind: 'run', layers: {}, run: { layers: all, meta: {} } },
  { kind: 'run', tz: true, layers: {}, run: { layers: { peoples: [1], body_tall: [1] }, meta: { anthro: 1, fuels: {}, techtree: {} } } }]) {
  S.V = V;
  for (const id of availableLayers()) if (!Object.keys(layerDef(id)).length) bad.push(`${V.tz ? 'tz' : V.kind} offers ${id} with no entry`);
}
console.log(JSON.stringify({ layers: Object.keys(L).length, bad }));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_layers_table_consistent(tmp_path):
    """globe/layers.js's LAYERS table: every menu entry has a layer, every layer a colouring (a ramp has units), a
    group, and a menu that lists it; every button a view offers (all its layers present) has an entry."""
    run = tmp_path / "layers.mjs"
    run.write_text(_LAYERS_JS)
    r = subprocess.run(["node", "--experimental-vm-modules", "--no-warnings", str(run), str(GLOBE)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout.strip().splitlines()[-1])
    assert out["layers"] > 50
    assert out["bad"] == []
