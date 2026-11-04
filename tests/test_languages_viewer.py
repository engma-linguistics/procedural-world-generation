"""viewer/langcore.js (the languages viewer's pure helpers) under node: the true-tree layout, the scholars' dendrogram, the
intelligibility colours, the continuum helpers (values at a frame, when a chain broke, the continua search), the snapshot
decoding and stitching through ancestors, the IPA grid placement, etymology chains; then the same helpers over the synthetic
languages.json from tools/language/fake_languages_json.py; and every viewer/lang*.js file parses. Skipped without node."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VIEWER = ROOT / "viewer"
pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="needs node")

_JS = r"""
const L = require(process.argv[2]);
const out = {};
// a small document: proto p0 -> d1 (bud, 20 kyr) -> d2 (bud 10 kyr), d3 (shift 5 kyr, substrate d9), d4 dead at 5
const frames = [20, 15, 10, 5, 0];
const snap = (c, core) => ({ c, v: ['a', 'i'], core, typ: {}, grams: [['PL', 'ka', 2]], cx: 1, shares: {} });
const doc = {
  frames_kyr: frames,
  lects: [
    { id: 'p0', deme: null, people: 'human', parent: null, how: 'proto', born_kyr: 20, died_kyr: 20, snapshots: [], changes: [] },
    { id: 'd1', deme: 1, people: 'human', parent: 'p0', how: 'proto', born_kyr: 20, died_kyr: null,
      snapshots: [[20, snap(['p', 't'], ['pa', 'ta'])], [15, { d: 1, core: { 1: 'da' } }], [10, { d: 1, core: {}, c: ['p', 't', 'k'] }], [5, { d: 1, core: {} }], [0, { d: 1, core: { 0: 'ba' } }]],
      changes: [[15, 'S001', 'effort', null], [12, 'S002', 'prosody', 'd9'], [2, 'S003', 'effort', null]] },
    { id: 'd2', deme: 2, people: 'human', parent: 'd1', how: 'bud', born_kyr: 10, died_kyr: null,
      snapshots: [[10, snap(['p', 't', 'k'], ['pa', 'da'])], [5, { d: 1, core: { 1: 'za' } }], [0, { d: 1, core: {} }]], changes: [[5, 'S010', 'perception', null]] },
    { id: 'd3', deme: 3, people: 'elf', parent: 'd1', how: 'shift', substrate: 'd9', born_kyr: 5, died_kyr: null, snapshots: [], changes: [] },
    { id: 'd4', deme: 4, people: 'human', parent: 'd2', how: 'bud', born_kyr: 10, died_kyr: 5, snapshots: [], changes: [] },
    { id: 'd9', deme: 9, people: 'elf', parent: null, how: 'proto', born_kyr: 20, died_kyr: 5, snapshots: [], changes: [] },
  ],
  intelligibility: { frames, pairs: [['d1', 'd2', [null, null, 1.0, 0.8, 0.75]], ['d1', 'd3', [null, null, null, 0.9, 0.7]], ['d2', 'd3', [null, null, null, 0.8, 0.3]]],
                     now: [['d1', 'd2', 0.6]] },
  families: { languages: [{ id: 'lang0', lects: ['d1', 'd2'] }] },
  etym_nodes: [[-1, 20, 'p0', 'proto', 'pata', 'water'], [0, 10, 'd1', 'sound_change:S001+S002', 'pada', 0], [1, 5, 'd2', 'shift:RIVER', 'pada', 'river', 'a note']],
};
const ix = L.index(doc);
const T = L.layoutTree(ix, {});
out.tree = T.rows.map((r) => [r.id, r.y, r.depth, r.how, r.dead]);
out.links = T.links.map((l) => [l.from, l.to, l.how, l.x]);
const Tc = L.layoutTree(ix, { collapsed: new Set(['d1']) });
out.collapsed = Tc.rows.map((r) => [r.id, r.collapsed, r.desc]);
const Tk = L.layoutTree(ix, { keep: (l) => l.id === 'd4' });
out.kept = Tk.rows.map((r) => r.id);
const D = L.layoutDendro([{ distance: 0.9, children: [{ distance: 0.3, children: [{ lect: 'd1' }, { lect: 'd2' }] }, { lect: 'd3' }] }]);
out.dendro = { leaves: D.leaves, nodes: D.nodes.map((n) => [n.leaf, n.x, n.y]), roots: D.roots };
const Dk = L.layoutDendro([{ distance: 0.9, children: [{ distance: 0.3, children: [{ lect: 'd1' }, { lect: 'd2' }] }, { lect: 'd3' }] }], (id) => id !== 'd2');
out.dendroKeep = { leaves: Dk.leaves, nodes: Dk.nodes.map((n) => [n.leaf, n.x, n.y, n.kids.length]) };
out.colors = [0.71, 0.7, 0.55, 0.4, 0.39, 0, null].map((v) => [L.intelClass(v), L.intelColor(v)]);
out.ramp = [L.intelRamp(0), L.intelRamp(1), L.intelRamp(null)];
out.chainNow = L.chainAt(ix, ['d2', 'd1', 'd3'], 4);
out.chainThen = L.chainAt(ix, ['d2', 'd1', 'd3'], 3);
out.brk = L.chainBreak(ix, ['d2', 'd1', 'd3']);
delete out.brk.history;
out.found = L.findContinua(['d1', 'd2', 'd3'], (a, b) => ix.intelAt(a, b, 3), () => true, () => 'f');
out.found4 = L.findContinua(['d1', 'd2', 'd3'], (a, b) => ix.intelAt(a, b, 4), () => true, () => 'f');
out.foundNoContact = L.findContinua(['d1', 'd2', 'd3'], (a, b) => ix.intelAt(a, b, 4), () => false, () => 'f');
out.snaps = ix.snaps('d1').map(([k, s]) => [k, s.core, s.c]);
out.stitch = L.stitch(ix, 'd2').map((h) => [h.kyr, h.lect, h.snap && h.snap.core, h.exists]);
out.log = L.changeLog(ix, 'd2').map((c) => [c.kyr, c.rule, c.lect]);
out.intelAt = [ix.intelAt('d2', 'd1', 2), ix.intelAt('d1', 'd3', 0), ix.intelAt('d1', 'd1', 0), ix.intelAt('d1', 'd4', 4)];
const P = (s) => { const p = L.ipaPlace(s); return [p.kind, p.place || p.height, p.manner || p.back, !!p.special, p.round == null ? null : p.round]; };
out.ipa = Object.fromEntries(['p', 'b', 'n̪', 'ts', 'tʃ', 'kʰ{voice=0}', 'ŋ‼', 'ɫ', 'ᶑʱ', 'ǃ', 'ʔ', 'w', 'a', 'u', 'e̞', 'ãː', 'aᴖ', 'ə', '‽'].map((s) => [s, P(s)]));
const xy = (s) => L.vowelXY(L.ipaPlace(s));
out.vxy = { i: xy('i'), u: xy('u'), a: xy('a'), 'ɑ': xy('ɑ') };
out.etym = L.etymChain(ix, 2);
out.proc = ['proto', 'sound_change:S001+S002+…3', 'derive:thing', 'compound:FIRE+STONE', 'borrow:d31', 'shift:EAT', 'odd:thing'].map(L.processText);
out.wrap = [L.wrapLon(10, 50), L.wrapLon(170, -170), L.wrapLon(-170, 170)];
out.cmp = ['d100', 'd12.1', 'd12', 'd13', 'p2'].sort(L.cmpId);
console.log(JSON.stringify(out));
"""

_FIXTURE_JS = r"""
const L = require(process.argv[2]);
const doc = JSON.parse(require('fs').readFileSync(process.argv[3], 'utf8'));
const ix = L.index(doc);
const T = L.layoutTree(ix, {});
const D = L.layoutDendro((doc.families || {}).scholars || []);
let unplaced = [], stitched = 0, frames = ix.frames.length;
for (const l of doc.lects) {
  for (const [, s] of ix.snaps(l.id)) for (const seg of [...s.c, ...s.v]) if (L.ipaPlace(seg).kind === 'X') unplaced.push(seg);
  if (l.deme != null) { const H = L.stitch(ix, l.id); if (H.length === frames && H.every((h) => h.snap)) stitched++; }
}
const cont = (doc.continua || []).map((c) => L.chainAt(ix, c.chain, frames - 1));
const living = ix.living;
const found = L.findContinua(living, (a, b) => ix.intelAt(a, b, frames - 1), () => true, (x) => ix.by.get(x).family_true);
const ety = Object.values(doc.lects.find((l) => l.deme != null).lexicon).map((w) => L.etymChain(ix, w.etym).length);
console.log(JSON.stringify({ rows: T.rows.length, lects: doc.lects.length, leaves: D.leaves.length, living: living.length, unplaced, stitched,
  withDeme: doc.lects.filter((l) => l.deme != null).length, cont, found: found.length, etyMin: Math.min(...ety) }));
"""


def _node(script: str, *args, tmp_path) -> dict:
    f = tmp_path / "t.js"
    f.write_text(script)
    out = subprocess.run(["node", str(f), *map(str, args)], capture_output=True, text=True, check=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def R(tmp_path_factory):
    return _node(_JS, VIEWER / "langcore.js", tmp_path=tmp_path_factory.mktemp("lc"))


def test_true_tree_rows_and_links(R):
    assert [r[0] for r in R["tree"]] == ["d9", "p0", "d1", "d2", "d4", "d3"]  # (roots by people, children oldest first)
    assert [r[2] for r in R["tree"]][1:5] == [0, 1, 2, 3]
    assert ["d1", "d3", "shift", 5] in R["links"] and ["d1", "d2", "bud", 10] in R["links"]
    assert dict((r[0], r[4]) for r in R["tree"])["d4"] is True


def test_true_tree_collapse_and_keep(R):
    assert R["collapsed"] == [["d9", False, 0], ["p0", False, 0], ["d1", True, 3]]
    assert R["kept"] == ["p0", "d1", "d2", "d4"]  # (a kept lect keeps its line of descent)


def test_dendrogram_layout_and_pruning(R):
    d = R["dendro"]
    assert d["leaves"] == ["d1", "d2", "d3"]
    inner = [n for n in d["nodes"] if n[0] is None]
    assert sorted(n[1] for n in inner) == [0.3, 0.9]
    assert [n for n in inner if n[1] == 0.3][0][2] == 0.5  # (half-way between its leaves' rows)
    k = R["dendroKeep"]
    assert k["leaves"] == ["d1", "d3"] and [n for n in k["nodes"] if n[0] is None] == [[None, 0.9, 0.5, 2]]


def test_intelligibility_colours(R):
    assert [c[0] for c in R["colors"]] == ["high", "mid", "mid", "mid", "low", "low", "none"]
    assert len({c[1] for c in R["colors"]}) == 4
    assert R["ramp"][0] != R["ramp"][1] and R["ramp"][2].startswith("#")


def test_chain_values_and_break(R):
    # d2 - d1 - d3: at 5 kyr one speech end to end; now each link holds (0.75, 0.7) but the ends do not (0.3)
    assert R["chainThen"]["adj"] == [0.8, 0.9] and R["chainThen"]["ends"] == 0.8 and R["chainThen"]["linked"] and not R["chainThen"]["broken"]
    assert R["chainNow"]["adj"] == [0.75, 0.7] and R["chainNow"]["ends"] == 0.3 and R["chainNow"]["broken"]
    assert R["brk"]["broke_kyr"] == 0 and R["brk"]["broke_frame"] == 4
    assert R["found"] == []  # (at 5 kyr every pair understands the others)
    assert [c["chain"] for c in R["found4"]] == [["d2", "d1", "d3"]] and R["found4"][0]["ends"] == 0.3
    assert R["foundNoContact"] == []


def test_continua_search_matches_families_rule(tmp_path):
    js = r"""
const L = require(process.argv[2]);
const v = { 'a|b': 0.8, 'b|c': 0.8, 'c|d': 0.8, 'a|c': 0.6, 'b|d': 0.6, 'a|d': 0.2 };
const val = (x, y) => v[x < y ? x + '|' + y : y + '|' + x] ?? 0;
console.log(JSON.stringify(L.findContinua(['d', 'c', 'b', 'a'], val, () => true, () => 'f')));
"""
    r = _node(js, VIEWER / "langcore.js", tmp_path=tmp_path)
    assert len(r) == 1 and r[0]["chain"][0] == "a" and r[0]["chain"][-1] == "d" and r[0]["ends"] == 0.2
    assert len(r[0]["chain"]) == 3  # (a-c-d or a-b-d: BFS gives the shortest path between the ends)


def test_snapshots_and_stitch(R):
    assert R["snaps"][1][1] == ["pa", "da"] and R["snaps"][2][2] == ["p", "t", "k"] and R["snaps"][4][1] == ["ba", "da"]
    st = {k: (lect, core) for k, lect, core, _ in R["stitch"]}
    assert st[20] == ("d1", ["pa", "ta"]) and st[15] == ("d1", ["pa", "da"])  # (before d2 was born: its parent)
    assert st[10][0] == "d2" and st[5] == ("d2", ["pa", "za"])
    assert [c[1] for c in R["log"]] == ["S010", "S002", "S001"]  # (newest first; d1's change after the split is not d2's)


def test_intel_lookup(R):
    assert R["intelAt"] == [1.0, None, 1, None]


def test_ipa_placement(R):
    p = R["ipa"]
    assert p["p"][:3] == ["C", "bilabial", "plosive"] and p["n̪"][:3] == ["C", "dental", "nasal"]
    assert p["ts"][:3] == ["C", "alveolar", "affricate"] and p["tʃ"][:3] == ["C", "postalveolar", "affricate"]
    assert p["kʰ{voice=0}"] == ["C", "velar", "plosive", True, None]
    assert p["ŋ‼"][:4] == ["C", "velar", "nasal", True] and p["ɫ"][2] == "lateral approximant" and p["ᶑʱ"][2] == "implosive"
    assert p["ǃ"][2] == "click" and p["ʔ"][1] == "glottal" and p["w"][2] == "approximant"
    assert p["a"] == ["V", 6, 0, False, False] and p["u"] == ["V", 0, 2, False, True] and p["e̞"][1] == 3
    assert p["ãː"][:3] == ["V", 6, 0] and p["aᴖ"][3] is True and p["ə"][1:3] == [3, 1]
    assert p["‽"][0] == "X"
    v = R["vxy"]
    assert v["i"]["y"] < v["a"]["y"] and v["u"]["x"] > v["i"]["x"] and v["ɑ"]["x"] > v["a"]["x"]


def test_etymology_and_words(R):
    e = R["etym"]
    assert [s["ipa"] for s in e] == ["pata", "pada", "pada"] and [s["gloss"] for s in e] == ["water", "water", "river"]
    assert e[2]["note"] == "a note" and e[1]["process"].startswith("sound_change")
    pr = R["proc"]
    assert pr[0] == "in the proto-language" and "S001, S002 and 3 more" in pr[1] and "'thing'" in pr[2] and "FIRE + STONE" in pr[3]
    assert pr[-1] == "odd:thing"


def test_small_helpers(R):
    assert R["wrap"][0] == [[10, 50]] and len(R["wrap"][1]) == 2 and R["wrap"][1][0] == [170, 190]
    assert R["cmp"] == ["d12", "d12.1", "d13", "d100", "p2"]


def test_helpers_over_the_synthetic_file(tmp_path):
    sys.path.insert(0, str(ROOT / "tools" / "language"))
    try:
        import fake_languages_json as F
    finally:
        sys.path.pop(0)
    doc = F.build(seed=3)
    f = tmp_path / "languages.json"
    f.write_text(json.dumps(doc, ensure_ascii=False))
    r = _node(_FIXTURE_JS, VIEWER / "langcore.js", f, tmp_path=tmp_path)
    assert r["rows"] == r["lects"] == 30 and r["leaves"] == r["living"]
    assert r["unplaced"] == [] and r["stitched"] == r["withDeme"] and r["etyMin"] >= 2
    assert all(c["adj"] is not None for c in r["cont"])


@pytest.mark.parametrize("name", ["langcore.js", "langview.js", "langtime.js", "langmap.js", "langmore.js"])
def test_viewer_scripts_parse(name):
    subprocess.run(["node", "--check", str(VIEWER / name)], check=True, capture_output=True)


def test_page_loads_its_scripts():
    html = (VIEWER / "languages.html").read_text()
    for s in ["numfmt.js", "langcore.js", "langview.js", "langtime.js", "langmap.js", "langmore.js", "theme.css"]:
        assert s in html
    assert 'href="languages.html"' in (VIEWER / "lineages.html").read_text()
