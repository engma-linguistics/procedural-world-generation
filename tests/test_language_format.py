"""languages.json format procgen-languages/2 (output.pack / expand / save / load; architecture section 11): the packed main
file and its two sidecars expand back to exactly the in-memory doc, in Python and in viewer/langcore.js (under node)."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from planet.language import output as OU

ROOT = Path(__file__).resolve().parent.parent


def _doc():
    nodes = [[-1, 20.0, "p0", "proto", "pata", "water"], [0, 10.0, "d1", "sound_change:S001+S002", "pada", 0],
             [1, 5.0, "d2", "shift:RIVER", "pada", "river", "a note"], [-1, 20.0, "p0", "proto", "ki", "fire"],
             [3, 8.0, "d1", "derive:do", "kiwa", "burn", "FIRE + 'do'"], [4, 2.0, "d1", "sound_change:S009", "kiwa", 0],
             [-1, 3.0, "d2", "coin", "zu", "cold"]]
    roots = {"p0:WATER": {"node": 0, "lect": "p0", "kyr": 20.0, "concept": "WATER", "gloss": "water", "ipa": "pata", "pos": "N"},
             "p0:FIRE": {"node": 3, "lect": "p0", "kyr": 20.0, "concept": "FIRE", "gloss": "fire", "ipa": "ki", "pos": "N"},
             "d1:BURN@8": {"node": 4, "lect": "d1", "kyr": 8.0, "concept": "BURN", "gloss": "burn", "ipa": "kiwa", "pos": "V"},
             "d2:COLD@3": {"node": None, "lect": "d2", "kyr": None, "concept": "COLD", "gloss": "cold", "ipa": None, "pos": "ADJ"},
             "weird-root": {"node": 6, "lect": "d2", "kyr": 3.0, "concept": "COLD", "gloss": "chilly", "ipa": "zu", "pos": "ADJ"}}
    w = lambda ipa, pos, etym, rs, er=None, **kw: {"ipa": ipa, "roman": ipa.upper(), "pos": pos, "freq": 2, "etym": etym,  # noqa: E731
                                                  "roots": rs, "etym_roots": rs if er is None else er, **kw}
    snap = [[20.0, {"c": ["p", "t"], "v": ["a"], "core": ["pata", None], "typ": {}, "grams": [], "cx": 1.5, "shares": {}}],
            [19.5, {"d": 1, "core": {"0": "pada"}, "cx": 2.0}]]
    lects = [
        {"id": "p0", "deme": None, "people": "human", "parent": None, "lexicon": {}, "snapshots": []},
        {"id": "d1", "deme": 1, "people": "human", "parent": "p0", "snapshots": snap,
         "lexicon": {"BURN": w("kiwa", "V", 5, ["d1:BURN@8"], ["p0:FIRE"]), "WATER": w("pada", "N", 1, ["p0:WATER"]),
                     "NAME:x": w("ki", "NAME", 3, ["p0:FIRE"], extra=1)}},
        {"id": "d2", "deme": 2, "people": "kenku", "parent": "d1",
         "lexicon": {"RIVER": w("pada", "N", 2, ["p0:WATER"]), "COLD": w("zu", "ADJ", 6, ["d2:COLD@3", "weird-root"])}},
    ]
    lects[2]["lexicon"]["RIVER"].pop("etym_roots")
    return {"format": OU.FORMAT, "run": "r1", "etym_nodes": nodes, "roots": roots, "lects": lects, "names": {"x": 1},
            "checks": []}


def test_pack_expand_is_exact():
    d = _doc()
    main, side = OU.pack(d)
    assert "etym_nodes" not in main and "roots" not in main and all("snapshots" not in l for l in main["lects"])
    back = OU.expand(json.loads(OU.dumps(main)), {k: json.loads(OU.dumps(v)) for k, v in side.items()})
    assert back == d


def test_save_load_and_main_only(tmp_path):
    d = _doc()
    sizes = OU.save(d, tmp_path / "languages.json")
    assert set(sizes) == {"languages.json", "languages-etym.json", "languages-snapshots.json"}
    assert OU.load(tmp_path / "languages.json") == d
    m = OU.load(tmp_path / "languages.json", sidecars=False)
    assert "etym_nodes" not in m and m["lects"][1]["lexicon"]["WATER"] == {"ipa": "pada", "roman": "PADA", "pos": "N", "freq": 2}
    (tmp_path / "old.json").write_text(json.dumps(d))
    assert OU.load(tmp_path / "old.json") == d                      # (a /1 file reads as it is)


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_viewer_expander_matches(tmp_path):
    d = _doc()
    main, side = OU.pack(d)
    for name, x in (("m.json", main), ("e.json", side["etym"]), ("s.json", side["snapshots"])):
        (tmp_path / name).write_text(OU.dumps(x))
    js = tmp_path / "x.js"
    js.write_text("const L = require(process.argv[2]); const fs = require('fs'); const r = (f) => JSON.parse(fs.readFileSync(f));"
                  "const d = L.expand(r(process.argv[3]), {etym: r(process.argv[4]), snapshots: r(process.argv[5])});"
                  "process.stdout.write(JSON.stringify([d, L.sidecarName('languages.json', 'etym')]));")
    out = subprocess.run(["node", str(js), str(ROOT / "viewer" / "langcore.js"), *(str(tmp_path / n) for n in ("m.json", "e.json", "s.json"))],
                         capture_output=True, text=True, check=True)
    got, name = json.loads(out.stdout)
    assert got == json.loads(json.dumps(d)) and name == "languages-etym.json"
