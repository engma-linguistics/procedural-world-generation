"""planet/langserve.py (the languages viewer on its own) and tools/language/demo_page.py (one offline HTML page)."""
from __future__ import annotations

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
