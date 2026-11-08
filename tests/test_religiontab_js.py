"""viewer/religiontab.js: a second draw() while the first fetch is still in flight must wait for it
(it used to say "no faiths" at once), and a server error shows its text. Skipped where node isn't installed."""

import shutil
import subprocess
from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parent.parent / "viewer"

_JS = r"""
const fs = require('fs');
const mkEl = () => ({ innerHTML: '', style: {}, querySelectorAll: () => [], onclick: null });
const els = {};
global.document = { head: { insertAdjacentHTML() {} }, getElementById: (id) => els[id] || (els[id] = mkEl()) };
global.location = { hash: '#religion/trees', search: '?run=r1' };
global.history = { replaceState() {} };
global.window = global; global.NumFmt = { kyr: String, ago: (k) => k + ' ago' };
let release, mode = process.argv[2];
global.fetch = (u) => new Promise((res) => {
  const reply = () => res(mode === 'err'
    ? { ok: false, status: 500, text: () => Promise.resolve('{"error":"boom"}') }
    : { ok: true, json: () => Promise.resolve({ faiths: null, summary: {} }) });
  if (u.includes('/gods')) release = reply; else reply();
});
const src = fs.readFileSync(process.argv[3], 'utf8');
(0, eval)(src);
const el = mkEl(), r = { id: 'r1' };
ReligionTab.draw(el, r);
ReligionTab.draw(el, r);
setTimeout(() => {
  const mid = el.innerHTML;
  release();
  setTimeout(() => console.log(JSON.stringify({ mid, end: el.innerHTML })), 50);
}, 50);
"""


def _run(mode, tmp_path):
    f = tmp_path / "t.js"
    f.write_text(_JS)
    out = subprocess.run(["node", str(f), mode, str(VIEWER / "religiontab.js")], capture_output=True, text=True, check=True)
    import json
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_second_draw_while_loading_waits(tmp_path):
    r = _run("ok", tmp_path)
    assert "Working out" in r["mid"] and "No religion" not in r["mid"]
    assert "No religion" in r["end"]  # only once the fetch is done (this fixture has no faiths)


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_server_error_text_shown(tmp_path):
    r = _run("err", tmp_path)
    assert "boom" in r["end"]


_JS_TREE = r"""
const fs = require('fs');
const mkEl = () => ({ innerHTML: '', style: {}, querySelectorAll: () => [], onclick: null, clientWidth: 1500 });
const els = {};
global.document = { head: { insertAdjacentHTML() {} }, getElementById: (id) => els[id] || (els[id] = mkEl()) };
global.location = { hash: '#religion/trees', search: '?run=r1' };
global.history = { replaceState() {} };
global.window = global; global.NumFmt = { kyr: (k) => k + ' kyr', ago: (k) => k + ' kyr ago' };
const beings = [0, 1, 2, 3, 4].map((i) => ({ label: 'g' + i, born_kyr: 230 - i * 40, ended_kyr: null, parent: i ? 0 : null, history: [],
  individuation: 0.3, status: 'living', how: 'born', culture: 0, top: [] }));
const faith = { id: 0, name: 'F', color: '#fff', how: 'founded', founded_kyr: 230, ended_kyr: null, beings: [0, 1, 2, 3, 4],
  cultures_now: [0], peoples_now: [0], origin_people: 0, events: [], parent: null };
global.fetch = (u) => Promise.resolve({ ok: true, json: () => Promise.resolve(
  u.includes('/gods') ? { faiths: { list: [faith] }, beings, frames: [[0]], summary: {} } : {}) });
(0, eval)(fs.readFileSync(process.argv[2], 'utf8'));
const el = mkEl();
ReligionTab.draw(el, { id: 'r1' });
setTimeout(() => console.log(JSON.stringify({ html: els['rl-main'] ? els['rl-main'].innerHTML : el.innerHTML })), 100);
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_single_card_fills_width_and_axis_reaches_now(tmp_path):
    import json
    f = tmp_path / "t2.js"
    f.write_text(_JS_TREE)
    out = subprocess.run(["node", str(f), str(VIEWER / "religiontab.js")], capture_output=True, text=True, check=True)
    html = json.loads(out.stdout.strip().splitlines()[-1])["html"]
    assert 'class="rl-cards one"' in html  # one card: a single full-width column, not one auto-fill track
    assert ">now</text>" in html  # the axis labels the present


_JS_YOURS = r"""
const fs = require('fs');
const mkEl = () => ({ innerHTML: '', style: {}, value: '', checked: false, querySelectorAll: () => [], querySelector: () => null, onclick: null, clientWidth: 1500 });
const els = {};
global.document = { head: { insertAdjacentHTML() {} }, getElementById: (id) => els[id] || (els[id] = mkEl()) };
global.location = { hash: '#religion/yours', search: '?run=r1' };
global.history = { replaceState() {} };
global.window = global;
(0, eval)(fs.readFileSync(process.argv[3], 'utf8'));  // (the real numfmt.js: parseDate and ago)
(0, eval)(fs.readFileSync(process.argv[2], 'utf8'));
const beings = [{ label: 'Mara, god of sea', name: 'Mara', born_kyr: 30, ended_kyr: null, parent: null, history: [], individuation: 0.5, status: 'living', how: 'authored', culture: 0, top: [] }];
const faith = { id: 0, name: 'The Tide Mother', authored: 'a1', color: '#fff', how: 'authored', founded_kyr: 30, ended_kyr: null, beings: [0],
  cultures_now: [0], peoples_now: ['human'], origin_people: 'human', events: [], parent: null, track: [] };
const spec = { id: 'a1', name: 'The Tide Mother', culture: 0, people: null, place: null, ago_kyr: 30, year_text: '30 kyr', gods: [{ name: 'Mara', domains: ['sea'] }], spreads: true };
const bad = { ...spec, id: 'a2', name: 'Later', ago_kyr: -1, year_text: '' };
const gods = { faiths: { list: [faith] }, beings, frames: [[0, 0]], summary: { living: 1 }, gods_mode: 'faith_made', groups: { water: ['sea', 'river'] },
  cultures: { 0: { faith_now: 0 } },
  authored: { rule: 'R', problems: [], faiths: [{ ...spec, took_hold: true, faith: 0, founded_kyr: 30, founded_in: 0, founded_in_name: 'Zero', spread: 'won 1 culture by conversion', cultures_now: 2, cultures_ever: 2 },
    { ...bad, took_hold: false, why: 'its year is after the present' }] } };
const posts = [];
global.fetch = (u, o) => { if (o && o.method === 'POST') posts.push(JSON.parse(o.body));
  return Promise.resolve({ ok: true, json: () => Promise.resolve(u.includes('/gods') ? gods : u.includes('/authored') ? (o && o.method === 'POST' ? { saved: 1 } : { faiths: [spec, bad], gods_mode: null }) : u.includes('/cultures') ? { cultures: [{ id: 0, name: 'Zero', people: 'human' }] } : { cultures: {} }) }); };
const el = mkEl();
ReligionTab.draw(el, { id: 'r1', lineages: [{ id: 'human', name: 'Humans' }] });
setTimeout(() => {
  const list = els['rl-main'].innerHTML, nav = el.innerHTML;
  els['rl-add'].onclick();
  const form = els['rl-main'].innerHTML;
  els['rf-save'].onclick();
  const msg1 = els['rf-msg'].textContent;
  els['rf-name'].value = 'Sky Father'; els['rf-who'].value = 'phuman'; els['rf-year'].value = '12,000 years ago'; els['rf-spr'].checked = false;
  el.querySelectorAll = (q) => (q.includes('data-g') ? [{ querySelector: () => ({ value: 'Ana' }), querySelectorAll: () => [{ value: 'sea' }, { value: '' }] }] : []);
  els['rf-save'].onclick();
  setTimeout(() => console.log(JSON.stringify({ list, nav, form, msg1, posts })), 50);
}, 100);
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_your_faiths_view_lists_results_and_saves_a_new_faith(tmp_path):
    """PW-1430: the Your faiths view shows each written faith's result (took hold or why not), the gods-mode control sits in the bar,
    an unnamed faith is refused before any POST, and a filled form posts the whole list with the new faith (date via NumFmt.parseDate)."""
    import json
    f = tmp_path / "t3.js"
    f.write_text(_JS_YOURS)
    out = subprocess.run(["node", str(f), str(VIEWER / "religiontab.js"), str(VIEWER / "numfmt.js")], capture_output=True, text=True, check=True)
    r = json.loads(out.stdout.strip().splitlines()[-1])
    assert "✎ yours" in r["list"] and "took hold" in r["list"] and "won 1 culture" in r["list"]
    assert "did not take hold" in r["list"] and "after the present" in r["list"]
    assert "30,000 years ago" in r["list"]  # (dates through NumFmt.ago)
    assert 'id="rl-mode"' in r["nav"] and "(1 yours)" in r["nav"]
    assert 'id="rf-name"' in r["form"] and "faithmap" in r["form"]  # (the editor, with a map to pick the place)
    assert r["msg1"] == "it needs a name"
    assert len(r["posts"]) == 1
    saved = r["posts"][0]["faiths"]
    assert [x["id"] for x in saved] == ["a1", "a2", "a3"]
    new = saved[2]
    assert new["name"] == "Sky Father" and new["people"] == "human" and new["culture"] is None and abs(new["ago_kyr"] - 12.0) < 1e-9
    assert new["gods"] == [{"name": "Ana", "domains": ["sea"]}] and new["spreads"] is False
