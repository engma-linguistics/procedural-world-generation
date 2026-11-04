"""viewer/invasiontab.js (PW-1433): the States & war tab lists each scheduled invasion with what came of it (it happened, with the land
taken, or why not), the incursions the sim found beside them, refuses a row with no invaders before any POST, and posts the whole list
with a new row (dates through the real NumFmt.parseDate). Skipped where node isn't installed."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parent.parent / "viewer"

_JS = r"""
const fs = require('fs');
const mkEl = () => ({ innerHTML: '', style: {}, value: '', checked: false, textContent: '', querySelectorAll: () => [], querySelector: () => null, onclick: null });
const els = {};
global.document = { head: { insertAdjacentHTML() {} }, getElementById: (id) => els[id] || (els[id] = mkEl()) };
global.window = global;
global.BroadcastChannel = class { constructor(n) { this.n = n; } postMessage(m) { posts.push({ channel: this.n, ...m }); } };
(0, eval)(fs.readFileSync(process.argv[3], 'utf8'));  // (the real numfmt.js)
(0, eval)(fs.readFileSync(process.argv[2], 'utf8'));
const row = { id: 'i1', who: { people: 'antelope_folk' }, whom: { people: 'human' }, from_kyr: 0.6, to_kyr: 0.6, year_text: '600 years ago', place: null, strength: 'strong' };
const odd = { id: 'i2', who: { culture: 'cervid:1' }, whom: null, from_kyr: 5.5, to_kyr: 3.3, year_text: '5500 years ago to 3300 years ago', place: [10, 20], strength: 'light' };
const authored = { faiths: [], gods_mode: null, invasions: [row, odd], choices: { peoples: [{ id: 'antelope_folk', name: 'antelope-kin' }, { id: 'human', name: 'humans' }],
  cultures: [{ uid: 'cervid:1', name: 'first cervid-kin', people: 'cervid_folk' }] } };
const pol = { steps: [{ ago: 0, frame: 7 }], invasions: { rule: 'RULE TEXT', problems: [], rows: [
  { id: 'i1', happened: true, took: [{ ago_kyr: 0.6, winner: 'Antelope State', loser: 'Human Chiefdom', km2: 3113 }], km2: 3113, states: { centuries: 3, from_kyr: 0.8, to_kyr: 0.5 } },
  { id: 'i2', happened: false, took: [], km2: 0, why: 'no state of first cervid-kin existed then', states: { centuries: 0 } }] } };
const posts = [];
global.fetch = (u, o) => { if (o && o.method === 'POST') posts.push(JSON.parse(o.body));
  return Promise.resolve({ ok: true, json: () => Promise.resolve(u.includes('/polities') ? pol : u.includes('/authored') ? (o && o.method === 'POST' ? { invasions: 3 } : authored) : {}) }); };
const el = mkEl();
const result = { id: 'r1', lineages: [], contacts: { incursions: [{ by: 'human', over: 'antelope_folk', kind: 'displacement', ago_kyr: 2.5, mkm2: 0.181, lat: -36.6, lon: 160.4, from_deg: 338 }] } };
InvasionTab.draw(el, result);
setTimeout(() => {
  const list = el.innerHTML;
  els['iv-add'].onclick();
  const form = el.innerHTML;
  els['if-save'].onclick();
  const msg1 = els['if-msg'].textContent;
  els['if-who'].value = 'phuman'; els['if-whom'].value = 'ccervid:1'; els['if-from'].value = '1,400 years ago'; els['if-to'].value = '';
  el.querySelector = (q) => (q.includes('"strong"') ? { checked: true } : q.includes('"any"') ? { checked: true } : null);
  els['if-save'].onclick();
  setTimeout(() => console.log(JSON.stringify({ list, form, msg1, posts })), 50);
}, 50);
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_states_and_war_tab_reads_out_rows_lists_incursions_and_saves(tmp_path):
    f = tmp_path / "t.js"
    f.write_text(_JS)
    out = subprocess.run(["node", str(f), str(VIEWER / "invasiontab.js"), str(VIEWER / "numfmt.js")], capture_output=True, text=True, check=True)
    r = json.loads(out.stdout.strip().splitlines()[-1])
    L = r["list"]
    assert "Your invasions" in L and "the antelope-kin" in L and "the humans" in L and "first cervid-kin" in L and "anyone they border" in L
    assert "it happened" in L and "Antelope State took Human Chiefdom 600 years ago" in L and "3,113 km²" in L
    assert "it didn&#39;t" in L or "it didn't" in L
    assert "no state of first cervid-kin existed then" in L and "never ruled a state" in L
    assert "around 600 years ago" in L and "5,500 years ago to 3,300 years ago" in L  # (dates through NumFmt.ago)
    assert "Found by the sim" in L and "displacement" in L and "from the north" in L and "2,500 years ago" in L and "RULE TEXT" in L
    assert 'id="if-who"' in r["form"] and "faithmap" in r["form"] and "frame=7" in r["form"]  # (the editor, with a map to pick where from)
    assert r["msg1"] == "pick who invades"
    saved = [p for p in r["posts"] if "invasions" in p]
    assert len(saved) == 1 and saved[0]["run"] == "r1"
    rows = saved[0]["invasions"]
    assert [x["id"] for x in rows] == ["i1", "i2", "i3"]
    new = rows[2]
    assert new["who"] == {"people": "human"} and new["whom"] == {"culture": "cervid:1"} and new["strength"] == "strong" and new["place"] is None
    assert abs(new["from_kyr"] - 1.4) < 1e-9 and new["from_kyr"] == new["to_kyr"] and "_bad" not in new
    assert any(p.get("channel") == "pw-polities" and p.get("run") == "r1" for p in r["posts"])  # (the globe is told to fetch again)
