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
