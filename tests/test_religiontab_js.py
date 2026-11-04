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
global.window = global; global.NumFmt = { kyr: String };
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
