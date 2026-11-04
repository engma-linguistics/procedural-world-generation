"""viewer/numfmt.js (PW-1429, years everywhere): dates read as 'N years ago', or as years once the present's year
is set; typed dates parse back. Skipped where node isn't installed."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parent.parent / "viewer"

_JS = r"""
const store = {};
globalThis.localStorage = { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: (k) => { delete store[k]; } };
(0, eval)(require('fs').readFileSync(process.argv[1], 'utf8'));
const N = NumFmt, out = {};
out.plain = [0, 0.3, 1, 12.4, 12.345, 2500].map((k) => N.ago(k));
N.run = 'r1'; N.setPresent(1400);
out.year = [0, 0.3, 1.2, 1.4, 1.5, 3.4].map((k) => N.ago(k));
out.since = N.since(0.2);
out.parse = ['year 1400', '1000 before year 1', 'year 1', '12,400 years ago', '12.4 kyr', '8 Myr', '300 yr', 'now', 'junk'].map((t) => N.parseDate(t));
out.bare = [N.parseDate('1200', 'year'), N.parseDate('3', 'kyr'), N.parseDate('300', 'ago')];
N.run = 'r2'; out.other = N.present();   // a run with none set takes the last chosen
N.setPresent('', 'r2'); out.cleared = [N.present('r2'), N.ago(12.4, null)];
out.noPresent = N.parseDate('year 5', 'kyr', null);
console.log(JSON.stringify(out));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_numfmt_dates():
    r = subprocess.run(["node", "-e", _JS, str(VIEWER / "numfmt.js")], capture_output=True, text=True, check=True)
    o = json.loads(r.stdout)
    assert o["plain"] == ["the present", "300 years ago", "1,000 years ago", "12,400 years ago", "12,300 years ago", "2,500,000 years ago"]
    assert o["year"] == ["year 1400", "year 1100", "year 200", "1 before year 1", "101 before year 1", "2001 before year 1"]
    assert o["since"] == "since year 1200"
    assert o["parse"][:-1] == pytest.approx([0.0, 2.399, 1.399, 12.4, 12.4, 8000, 0.3, 0]) and o["parse"][-1] is None
    assert o["bare"] == pytest.approx([0.2, 3, 0.3])
    assert o["other"] == 1400
    assert o["cleared"] == [None, "12,400 years ago"]
    assert o["noPresent"] is None
