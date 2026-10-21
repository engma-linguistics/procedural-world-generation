"""planet make (PW-248), the New planet form's API (PW-472), and the planet grouping and thumbnails
behind the start screen and the navigator (PW-472, PW-473)."""

import http.client
import http.server
import json
import sys
import threading

import pytest

from planet import __main__ as cli
from planet import api, family, make, server, store as S


# ---------------------------------------------------------------- parsing and estimates
def test_parse_defaults_and_preset():
    r = make.parse_make_request({"seed": 7})
    assert (r["seed"], r["level"], r["myr"], r["preset"]) == (7, 6, 1000, "earthlike")
    assert r["timezoom"] and r["finish"] and r["highlights"] and r["zooms"] == 4
    w = make.parse_make_request({"seed": 1, "preset": "water-world"})
    assert w["myr"] == 2000 and w["set"] == {"continental_start": 0.1, "heat_start": 2}
    # the user's settings win over the preset's, and myr over the preset's length
    c = make.parse_make_request({"seed": 1, "preset": "cold", "myr": 300, "set": {"tilt": 20}})
    assert c["myr"] == 300 and c["set"] == {"tilt": 20.0, "climate_offset": -6}


def test_parse_random_seed_and_dependencies():
    assert isinstance(make.parse_make_request({})["seed"], int)
    r = make.parse_make_request({"seed": 1, "finish": False, "zooms": 3})
    assert not r["highlights"] and r["zooms"] == 0  # nothing to find highlights in
    r = make.parse_make_request({"seed": 1, "highlights": False, "zooms": 2})
    assert r["highlights"]  # zooms come from the highlights


@pytest.mark.parametrize("bad", [{"preset": "nope"}, {"level": 3}, {"myr": 5}, {"kyr": 0}, {"zooms": 99},
                                 {"set": {"nonsense": 1}}, {"set": {"n_plates": 2}}, {"set": {"start": "cube"}},
                                 {"set": {"tilt": "x"}}, {"seed": "abc"}, []])
def test_parse_rejects(bad):
    with pytest.raises(api.BadRequest):
        make.parse_make_request(bad)


def test_every_setting_and_preset_is_a_real_param():
    from dataclasses import fields
    from planet.tectonics import Params
    known = {f.name for f in fields(Params)}
    assert {s["key"] for s in make.SETTINGS} <= known
    for p in make.PRESETS.values():
        assert set(p["set"]) <= known
    opts = make.options()
    assert {s["key"]: s["default"] for s in opts["settings"]}["tilt"] == 23.4
    assert opts["unsupported"]  # the gaps are listed for the form


def test_estimate_follows_the_stages():
    full = make.estimate(make.parse_make_request({"seed": 1, "level": 6}))
    assert [s["key"] for s in full["stages"]] == ["simulate", "timezoom", "world", "highlights", "zooms"]
    assert abs(sum(s["s"] for s in full["stages"]) - full["total_s"]) < 0.5
    sim = full["stages"][0]["s"]
    assert 4 * 60 < sim < 8 * 60  # L6: ~5-6 min per Gyr (docs/coordination.md)
    short = make.estimate(make.parse_make_request({"seed": 1, "level": 6, "timezoom": False, "highlights": False,
                                                   "zooms": 0}))
    assert [s["key"] for s in short["stages"]] == ["simulate", "world"]
    l7 = make.estimate(make.parse_make_request({"seed": 1, "level": 7}))
    assert l7["stages"][0]["s"] > 4 * sim


# ---------------------------------------------------------------- the command line
def test_cli_dry_run(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["planet", "make", "--seed", "5", "--preset", "hothouse", "--level", "5",
                                      "--no-timezoom", "--zooms", "0", "--dry-run"])
    cli.main()
    out = capsys.readouterr().out
    assert "seed 5, preset hothouse, level 5" in out and "Simulating 1000 Myr" in out
    assert "time zoom" not in out and "regional zoom" not in out


def test_cli_rejects_bad_settings(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["planet", "make", "--seed", "5", "--set", "n_plates=1", "--dry-run"])
    with pytest.raises(SystemExit, match="n_plates"):
        cli.main()


# ---------------------------------------------------------------- the chain, tiny
@pytest.fixture(scope="module")
def made(tmp_path_factory):
    """One whole chain at level 4: run, time zoom, finished world, highlights, one zoom."""
    S.set_root(tmp_path_factory.mktemp("make"))
    log = []
    out = make.make({"seed": 2, "level": 4, "myr": 40, "kyr": 6, "zooms": 1, "name": "tiny make"},
                    lambda f, msg: log.append((f, msg)))
    yield out, log
    S.set_root(None)


def test_make_chain(made):
    out, log = made
    assert set(out) >= {"run", "timezoom", "world", "highlights", "zooms", "t_myr"}
    assert S.exists("run", out["run"]) and S.exists("run", out["timezoom"]) and S.exists("world", out["world"])
    assert len(out["zooms"]) == 1 and S.exists("zoom", out["zooms"][0])
    w = S.read_header(S.find_world(out["world"]), ("meta",))["meta"]
    assert w["timezoom"] == out["timezoom"] and w["source_run"] == out["run"]
    fr = [f for f, _ in log]
    assert fr == sorted(fr) and fr[-1] == 1.0 and fr[0] < 0.1  # progress only goes forward
    assert any("zoom 1/1" in m for _, m in log)


def test_make_failure_names_the_stage(data_root):
    with pytest.raises(RuntimeError, match=r"simulate failed.*made so far: nothing"):
        make.make({"seed": 1, "level": 4, "myr": 40, "set": {"n_plates": 12}}, lambda f, m: (_ for _ in ()).throw(ValueError("x")))


def test_family_and_thumbs_of_a_made_planet(made):
    out, _ = made
    ps = family.planets()
    assert len(ps) == 1
    p = ps[0]
    by = {n["key"]: n for n in p["nodes"]}
    assert by[f"run:{out['timezoom']}"]["parent"] == f"run:{out['run']}"
    assert by[f"world:{out['world']}"]["parent"] == f"run:{out['timezoom']}"
    assert by[f"zoom:{out['zooms'][0]}"]["parent"] == f"world:{out['world']}"
    assert p["counts"] == {"timezoom": 1, "world": 1, "zoom": 1, "fine": 0} and p["thumb"].endswith(out["world"])
    from planet import thumbs
    for kind, i in (("world", out["world"]), ("run", out["run"]), ("run", out["timezoom"])):
        png = thumbs.thumb(kind, i)
        assert png and png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
        assert thumbs.thumb(kind, i) == png  # cached
    assert thumbs.thumb("world", "nope") is None and thumbs.thumb("zoom", out["zooms"][0]) is None
    assert thumbs.thumb("run", "../etc") is None


def test_family_groups_what_is_left_of_deleted_runs():
    runs = [{"dir": "r1", "id": "r1", "name": "A", "seed": 1, "level": 5, "myr": 100, "created": "2026-01-01 00:00:00"},
            {"dir": "t1", "id": "t1", "name": "tz", "kind": "timezoom", "source_run": "r1", "at_myr": 40, "kyr": 100,
             "seed": 1, "level": 5, "myr": 0, "created": "2026-01-02 00:00:00"},
            {"dir": "t2", "id": "t2", "name": "tz of a deleted run", "kind": "timezoom", "source_run": "gone", "at_myr": 40,
             "kyr": 100, "seed": 1, "level": 5, "myr": 0, "created": "2026-01-03 00:00:00"}]
    worlds = [{"file": "w1.json", "id": "w1", "name": "w", "created": "2026-01-02 01:00:00", "source_run": "r1", "t_myr": 40},
              {"file": "w2.json", "id": "w2", "name": "loose", "created": "2026-01-01 01:00:00", "level": 5}]
    zooms = [{"id": "z1", "name": "z", "created": "2026-01-02 02:00:00", "world": "w1", "center": {"lat": 1, "lon": 2},
              "size_km": 500, "res_km": 1},
             {"id": "z2", "name": "fine", "created": "2026-01-02 03:00:00", "world": "w1", "parent_zoom": "z1",
              "center": {"lat": 1, "lon": 2}, "size_km": 50, "res_km": 0.1}]
    ps = {p["key"]: p for p in family.build(runs, worlds, zooms)}
    assert set(ps) == {"r1", "gone:gone", "loose:w2"}
    nodes = {n["key"]: n for n in ps["r1"]["nodes"]}
    assert nodes["zoom:z2"]["parent"] == "zoom:z1" and nodes["zoom:z2"]["kind"] == "fine"
    assert nodes["world:w1"]["parent"] == "run:r1" and nodes["run:t1"]["parent"] == "run:r1"
    assert ps["gone:gone"]["nodes"][0]["parent"] is None and ps["loose:w2"]["run"] is None


# ---------------------------------------------------------------- over HTTP
@pytest.fixture
def http_get(made):
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    def call(method, path, body=None):
        c = http.client.HTTPConnection("127.0.0.1", httpd.server_address[1], timeout=60)
        c.request(method, path, body=json.dumps(body) if body is not None else None)
        r = c.getresponse()
        data = r.read()
        c.close()
        return r.status, r.getheader("Content-Type"), data

    yield call
    httpd.shutdown()
    httpd.server_close()


def test_http_routes(made, http_get):
    out, _ = made
    st, _, body = http_get("GET", "/api/planets")
    assert st == 200 and json.loads(body)["planets"][0]["run"] == out["run"]
    st, ct, body = http_get("GET", f"/api/thumb?kind=world&id={out['world']}")
    assert st == 200 and ct == "image/png" and body[:4] == b"\x89PNG"
    assert http_get("GET", "/api/thumb?kind=world&id=zzzzzz")[0] == 404
    st, _, body = http_get("GET", "/api/make/options")
    assert st == 200 and json.loads(body)["presets"]["cold"]["set"]["tilt"] == 15
    st, _, body = http_get("GET", "/api/make/estimate?level=5&seed=3&timezoom=0&zooms=0")
    est = json.loads(body)
    assert st == 200 and [s["key"] for s in est["stages"]] == ["simulate", "world", "highlights"] and est["spec"]["seed"] == 3
    assert http_get("GET", "/api/make/estimate?level=2")[0] == 400
    assert http_get("POST", "/api/make", {"preset": "nope"})[0] == 400


def test_make_is_a_job(made):
    """POST /api/make queues a 'make' job (the same request twice is one job); run here with a stub."""
    seen = []
    jobs = api.Jobs(lambda req, progress: (seen.append(req), progress(0.5, "half"), {"world": "w"})[2])
    req = make.parse_make_request({"seed": 4, "level": 4, "myr": 20})
    j = jobs.submit(req)
    assert jobs.submit(req) == j
    res = jobs.wait(j)
    assert res["status"] == "done" and res["world"] == "w" and seen[0]["type"] == "make"
    assert api.JOBS["make"] is api.make_job
