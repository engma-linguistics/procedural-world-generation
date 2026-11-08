"""viewer/techtab.js, the Technology tab's Spread view (lane 184): it fetches /api/techspread once per run and tech, a second draw
while the fetch is in flight waits for the same one, it shows who had the tech when and the headline numbers, and a server error
shows its text. Skipped where node isn't installed."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parent.parent / "viewer"

_JS = r"""
const fs = require('fs');
const els = {};
const mkEl = (id) => ({ id, innerHTML: '', style: {}, value: '', clientWidth: 800, querySelectorAll: () => [], querySelector: () => ({}), appendChild() {},
  classList: { contains: () => true, toggle() {}, remove() {} }, getBoundingClientRect: () => ({ width: 0, height: 0 }), isConnected: true });
global.document = { head: { insertAdjacentHTML() {} }, body: { appendChild() {} }, createElement: () => mkEl('x'),
  getElementById: (id) => els[id] || (els[id] = mkEl(id)) };
global.location = { hash: '#tech/spread', search: '?run=r1', origin: 'http://x' };
global.history = { replaceState() {} };
global.addEventListener = () => {}; global.innerWidth = 1200; global.innerHeight = 800;
global.window = global; global.NumFmt = { kyr: (k) => k + ' kyr', ago: (k) => k + ' kyr ago' };
let release, calls = 0, mode = process.argv[2];
const doc = { tech: 'writing', tech_name: 'writing', steps: [2, 1, 0], share_people: [0, 0.5, 1], share_towns: [0, 0.4, 1],
  stats: { first_kyr: 1.5, first_by: ['kobolds'], inventions: 1, reach_kyr: { '0.25': 1, '0.5': 1, '0.9': 0 }, big_never: ['dwarves'],
    last_big: { name: 'humans', ago: 0 }, share_now: 1 },
  peoples: [{ id: 'kobold', name: 'kobolds', ago: 1.5, how: 'invented', from: null, ready: 2, touch: null, share_now: 0.5, big: true },
            { id: 'human', name: 'humans', ago: 1, how: 'contact', from: 'kobold', from_name: 'kobolds', ready: 2, touch: 1.5, share_now: 0.5, big: true },
            { id: 'dwarf', name: 'dwarves', ago: null, how: null, from: null, ready: 2, touch: 1.5, share_now: 0.1, big: true }],
  cultures: [{ id: 0, name: 'first kobolds', people: 'kobold', ago: 1.5, how: 'invented', from: null, alive: true }] };
global.fetch = (u) => new Promise((res) => {
  if (u.includes('/api/techspread')) calls++;
  const reply = () => res(mode === 'err'
    ? { ok: false, status: 500, text: () => Promise.resolve('{"error":"boom"}') }
    : { ok: true, json: () => Promise.resolve(doc) });
  release = reply;
});
const src = fs.readFileSync(process.argv[3], 'utf8');
(0, eval)(src);
const result = { id: 'r1', lineages: [{ id: 'kobold', name: 'kobolds', leaf: true }, { id: 'human', name: 'humans', leaf: true }, { id: 'dwarf', name: 'dwarves', leaf: true }],
  techtree: { era: 'medieval', mode: 'fantasy', tracks: [{ id: 'communication', name: 'communication' }],
    techs: [{ id: 'writing', name: 'writing', track: 'communication', needs: [], env: [], env_any: [], era: 'bronze age', source: '' }],
    known: { kobold: { writing: [1.5, 'invented', null] }, human: { writing: [1, 'contact', 'kobold'] }, dwarf: {} },
    firsts: { writing: { line: 'kobold', ago_kyr: 1.5, how: 'invented' } } } };
const el = mkEl('root');
TechTab.draw(el, result);
TechTab.draw(el, result);
setTimeout(() => {
  const mid = els['tt-sp'].innerHTML;
  release();
  setTimeout(() => console.log(JSON.stringify({ mid, end: els['tt-sp'].innerHTML, side: els['tt-side'].innerHTML, calls, view: TechTab.view })), 50);
}, 50);
"""


def _run(mode, tmp_path):
    f = tmp_path / "t.js"
    f.write_text(_JS)
    out = subprocess.run(["node", str(f), mode, str(VIEWER / "techtab.js")], capture_output=True, text=True, check=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_spread_view_waits_then_shows_who_had_it(tmp_path):
    r = _run("ok", tmp_path)
    assert r["view"] == "spread"
    assert r["calls"] == 1  # (the second draw waited for the same fetch)
    assert "Working out" in r["mid"]
    end = r["end"]
    assert "How fast writing spread" in end and "<svg" in end and "polyline" in end
    assert "1.5 kyr ago" in end  # (dates through NumFmt.ago)
    assert "from</span> kobolds" in end and "never" in end and "dwarves" in end
    assert "first kobolds" in r["side"]


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_spread_server_error_text_shown(tmp_path):
    r = _run("err", tmp_path)
    assert "boom" in r["end"]
