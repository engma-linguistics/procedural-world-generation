"""planet/langserve.py (the languages viewer on its own) and tools/language/demo_page.py (one offline HTML page)."""
from __future__ import annotations

import copy
import gzip
import http.server
import json
import sys
import threading
import urllib.request
from pathlib import Path

import pytest

from planet import langserve as LS
from planet import store as S

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "language"))


@pytest.fixture
def lang_server(tmp_path):
    (tmp_path / "data" / "runs" / "r1").mkdir(parents=True)
    (tmp_path / "data" / "runs" / "r1" / "run.json").write_text('{"meta": {}}')
    out = tmp_path / "elsewhere.json"
    out.write_text(json.dumps({"lects": [], "run": "r1"}))
    (tmp_path / "elsewhere-etym.json").write_text(json.dumps({"nodes": "e"}))   # (a format /2 sidecar beside it)
    S.set_root(tmp_path / "data")
    LS.LangHandler.run, LS.LangHandler.languages, LS.LangHandler._gz = "r1", out, {}
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), LS.LangHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        S.set_root(None)


def _get(url, **headers):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, b"", {}


def test_langserve_serves_only_the_languages_page_and_its_data(lang_server):
    assert _get(lang_server + "/viewer/languages.html")[0] == 200
    assert _get(lang_server + "/viewer/langgram.js")[0] == 200
    assert _get(lang_server + "/viewer/index.html")[0] == 404          # not the main viewer
    assert _get(lang_server + "/runs/r1/../../../etc/passwd")[0] == 404
    assert json.loads(_get(lang_server + "/runs/index.json")[1]) == [{"dir": "r1", "kind": "peoples", "name": "languages"}]
    assert json.loads(_get(lang_server + "/runs/r1/run.json")[1]) == {"meta": {}}
    code, body, _h = _get(lang_server + "/runs/r1/languages.json")
    assert code == 200 and json.loads(body)["run"] == "r1"             # the --languages file, not runs/r1/
    code, body, h = _get(lang_server + "/runs/r1/languages.json", **{"Accept-Encoding": "gzip"})
    assert h.get("Content-Encoding") == "gzip" and json.loads(gzip.decompress(body))["run"] == "r1"
    code, body, _h = _get(lang_server + "/runs/r1/languages-etym.json")
    assert code == 200 and json.loads(body) == {"nodes": "e"}          # the sidecar beside the --languages file
    assert _get(lang_server + "/runs/r1/languages-snapshots.json")[0] == 404
    code, body, _h = _get(lang_server + "/api/speak/backends")
    assert code == 200 and "backends" in json.loads(body)


def _mini_doc():
    from test_language_sentences import lect
    out = []
    for i, (people, fam) in enumerate([("human", "f1"), ("elf", "f2"), ("kenku", "f3"), ("red_dragon", "f4")]):
        lj = lect()
        lj.update(id=f"d{i}", people=people, deme=i, family_true=fam, born_kyr=2.0, parent=None, population=1000 * (i + 1),
                  gen_yr=25.0 if people == "human" else 120.0, stats={"core_mean_syllables": 1.5,
                                                                      "inherited_core_share": 0.5})
        lj["inventory"]["tones"] = [1, 2, 3] if people == "kenku" else []
        out.append(lj)
    return {"run": "r1", "lects": out, "roots": {}}


def test_demo_page_is_one_offline_file(tmp_path):
    import demo_page as DP
    src = tmp_path / "languages.json"
    src.write_text(json.dumps(_mini_doc()))
    page, info = DP.build(str(src), None, 10, "auto", audio=False)
    assert len(info["languages"]) == 4 and info["clips"] == 0
    assert "<script src" not in page and "<link" not in page and "fetch(" not in page
    assert page.count("class='lang'") == 5 and "Sample sentences" in page and "Word families" in page   # (4 + the complexity tab)
    assert "Languages getting more and less complex" in page
    assert "name='viewport'" in page and "localStorage" not in page


def test_demo_page_embeds_audio(tmp_path):
    from planet.language import speak as SP
    if not SP.available_backends():
        pytest.skip("no speech backend available")
    import demo_page as DP
    src = tmp_path / "languages.json"
    src.write_text(json.dumps({**_mini_doc(), "lects": _mini_doc()["lects"][:1]}))
    page, info = DP.build(str(src), None, 1, "espeak", audio=True)
    assert info["backend"] == "espeak" and info["clips"] > 5 and info["failed"] == 0
    assert "data:audio/" in page and "espeak" in page.lower()


def test_demo_page_pieces_from_the_page_read():
    """Bugs a full read of the 11-08 demo found (grammar B): self-ancestors, missing percentages, unfelt 'felt' families,
    unexplained non-IPA marks, mixed gram labels, a lowercase cause, tool jargon."""
    import demo_page as DP
    import sketch as SK
    d = _mini_doc()
    a, b = d["lects"][0], copy.deepcopy(d["lects"][0])
    b.update(id="d0.1", parent="d0", born_kyr=1.0)
    d["lects"].append(b)
    doc = SK.Doc(d)
    line = DP.lineage(doc, b)
    assert line.split("</div>")[0].count("human 0") == 1                       # (a split that kept the deme is not its own ancestor)
    c = copy.deepcopy(a)
    c.update(id="d9", deme=9, family_true=a["family_true"])
    d["lects"].append(c)
    doc = SK.Doc(d)
    assert "under 5% understood" in DP.lineage(doc, a)
    assert DP.SK.audibly_shares("le˧", "le˧ʔi˧") and not DP.SK.audibly_shares("le˧", "wja˦")
    assert DP.house_marks({"inventory": {"vowels": ["a", "iᴖ"], "consonants": ["t"]}}).count("ᴖ") == 1
    assert DP.house_marks(a) == ""
    assert DP._lab("PAST") == "PST" and DP._lab("PERF") == "PRF" and DP._lab("EVID.REP") == "REP"
    assert DP._lab("CLASS:2") == "CL2"
    assert DP._cause(doc, a, False, 2.0)[0].isupper()


def test_demo_page_has_no_tool_jargon(tmp_path):
    import demo_page as DP
    src = tmp_path / "languages.json"
    src.write_text(json.dumps(_mini_doc()))
    page, _info = DP.build(str(src), None, 10, "auto", audio=False)
    for bad in ("sketch.py", "demo_page.py", "the lane", "(G05", "<code>cx</code>", "grammar.complexity", "of run r1",
                "the file does not keep", "window read", "language d0"):
        assert bad not in page, bad


def test_demo_page_second_read_fixes():
    """Grammar C: the coordinator's read of phase B's demo: shifts explained in the ancestry line, no stage that looks
    like its own ancestor, a cause that respects population, felt families that share more than chance."""
    import demo_page as DP
    import sketch as SK
    d = _mini_doc()
    a = d["lects"][0]
    old = dict(copy.deepcopy(a), id="d0.old", parent=None, born_kyr=9.0)
    mid = dict(copy.deepcopy(d["lects"][1]), id="d1.mid", parent="d0.old", born_kyr=7.0)
    a.update(parent="d1.mid", how="shift")
    d["lects"] += [old, mid]
    doc = SK.Doc(d)
    line = DP.lineage(doc, a).split("</div>")[0]
    assert "older speech of human 0" in line and "language shift" in line
    assert not SK.audibly_shares("ma˦ka", "puma˦lo") and SK.audibly_shares("ma˦", "ma˦lo")
    big = dict(a, population=300000, l2=0.0, isolation=1.0)
    doc.living[:] = [big] + [dict(x, population=10, l2=0.9, isolation=0.0) for x in doc.living[1:]]
    assert "Trudgill" not in DP._cause(doc, big, True, 2.0)
