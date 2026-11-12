"""planet make (PW-248), the New planet form's API (PW-472), and the planet grouping and thumbnails
behind the start screen and the navigator (PW-472, PW-473)."""

import http.client
import http.server
import json
import re
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


def test_parse_now():
    assert make.parse_make_request({"seed": 1})["now"] == "interglacial"  # the default (PW-479)
    assert make.parse_make_request({"now": "glacial"})["now"] == "glacial"
    assert make.parse_make_request({"now": "end"})["now"] == "end"
    assert make.parse_make_request({"now": "120", "kyr": 300})["now"] == 120.0
    for bad in ("sometime", 400, -1):
        with pytest.raises(api.BadRequest):
            make.parse_make_request({"now": bad, "kyr": 300})
    assert [w["key"] for w in make.options()["nows"]] == ["interglacial", "glacial", "end"]
    assert make.options()["defaults"]["now"] == "interglacial"
    assert server.make_query("seed=1&now=glacial")["now"] == "glacial"


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
    assert 10 * 60 < sim < 14 * 60  # L6: 659-802 s per Gyr measured on this machine (PW-478)
    short = make.estimate(make.parse_make_request({"seed": 1, "level": 6, "timezoom": False, "highlights": False,
                                                   "zooms": 0}))
    assert [s["key"] for s in short["stages"]] == ["simulate", "world"]
    l7 = make.estimate(make.parse_make_request({"seed": 1, "level": 7}))
    assert l7["stages"][0]["s"] > 4 * sim


def test_peoples_option_parses_estimates_and_lists_trees():
    """PW-1394: `peoples` names a tree (a preset or saved one); it needs the time zoom and the world."""
    assert make.parse_make_request({"seed": 1})["peoples"] == ""
    assert make.parse_make_request({"seed": 1, "peoples": "seven_meals"})["peoples"] == "seven_meals"
    for bad in ({"peoples": "nope"}, {"peoples": "dnd", "timezoom": False}, {"peoples": "dnd", "finish": False}):
        with pytest.raises(api.BadRequest):
            make.parse_make_request({"seed": 1, **bad})
    assert {"dnd", "seven_meals"} <= set(make.options()["peoples"]) and "techtree" not in make.options()["peoples"]
    est = make.estimate(make.parse_make_request({"seed": 1, "level": 6, "peoples": "dnd", "languages": False}))
    assert [s["key"] for s in est["stages"]][-1] == "peoples" and est["stages"][-1]["s"] == make.PEOPLES_S[6]
    assert server.make_query("seed=1&peoples=dnd")["peoples"] == "dnd"


def test_languages_stage_on_by_default_with_peoples():
    """PW-1634: with peoples, make runs the language pass as its own stage (on unless switched off), over at most
    `language_workers` processes (default 8), and the estimate counts it; without peoples there is no such stage."""
    assert make.parse_make_request({"seed": 1})["languages"] is False   # (no peoples, no languages)
    r = make.parse_make_request({"seed": 1, "level": 6, "peoples": "dnd"})
    assert r["languages"] is True and r["language_workers"] == 8
    assert make.parse_make_request({"seed": 1, "peoples": "dnd", "languages": False})["languages"] is False
    for bad in (0, 17):
        with pytest.raises(api.BadRequest):
            make.parse_make_request({"seed": 1, "peoples": "dnd", "language_workers": bad})
    est = make.estimate(r)
    assert [s["key"] for s in est["stages"]][-2:] == ["peoples", "languages"] and est["stages"][-1]["s"] == make.LANGUAGES_S[6]
    slow = make.estimate(make.parse_make_request({"seed": 1, "level": 6, "peoples": "dnd", "language_workers": 2}))
    assert slow["stages"][-1]["s"] == 4 * make.LANGUAGES_S[6]
    assert server.make_query("seed=1&peoples=dnd&languages=0")["languages"] is False
    assert server.make_query("seed=1&peoples=dnd&language_workers=4")["language_workers"] == "4"
    assert make.options()["defaults"]["languages"] is True


# ---------------------------------------------------------------- the command line
def test_cli_dry_run(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["planet", "make", "--seed", "5", "--preset", "hothouse", "--level", "5",
                                      "--no-timezoom", "--zooms", "0", "--dry-run"])
    cli.main()
    out = capsys.readouterr().out
    assert "seed 5, preset hothouse, level 5" in out and "Simulating 1000 Myr" in out
    assert "time zoom" not in out and "regional zoom" not in out


def test_cli_now(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["planet", "make", "--seed", "5", "--level", "5", "--now", "glacial", "--dry-run"])
    cli.main()
    assert "now = glacial" in capsys.readouterr().out
    monkeypatch.setattr(sys, "argv", ["planet", "make", "--seed", "5", "--now", "never", "--dry-run"])
    with pytest.raises(SystemExit, match="now must be"):
        cli.main()


def test_cli_rejects_bad_settings(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["planet", "make", "--seed", "5", "--set", "n_plates=1", "--dry-run"])
    with pytest.raises(SystemExit, match="n_plates"):
        cli.main()


def test_require_ice_parses_and_defaults_off():
    r = make.parse_make_request({"seed": 1})
    assert r["require_ice"] is False and r["tries"] == 3  # (default off: no change)
    r = make.parse_make_request({"seed": 1, "require_ice": True, "tries": 5})
    assert r["require_ice"] and r["tries"] == 5
    with pytest.raises(api.BadRequest, match="tries"):
        make.parse_make_request({"tries": 0})


def _fake_simulate(has_ice, calls):
    """A stand-in for timeline.simulate: writes a run.json whose finish moment has permanent ice per has_ice[seed]."""
    def sim(seed, level, myr, dt, every, name, params, progress=None, **kw):
        calls.append((seed, params.finish_require_ice))
        d = S.root() / "runs" / f"fake{seed}"
        d.mkdir(parents=True, exist_ok=True)
        fm = {"t": 100.0, "passes": True, "why": "fake", "no_permanent_ice": not has_ice(len(calls))}
        (d / "run.json").write_text(json.dumps({"id": f"fake{seed}", "frames": [], "meta": {"finish_moment": fm}}))
        return d
    return sim


def test_require_ice_rerolls_the_seed_until_a_roll_has_permanent_ice(data_root, monkeypatch):
    from planet import timeline as T
    calls = []
    monkeypatch.setattr(T, "simulate", _fake_simulate(lambda n: n >= 3, calls))
    out = make.make({"seed": 5, "level": 4, "myr": 40, "finish": False, "timezoom": False, "require_ice": True})
    assert [c[0] for c in calls] == [5, make.reroll_seed(5, 1), make.reroll_seed(5, 2)] and all(c[1] for c in calls)
    assert [r["permanent_ice"] for r in out["rolls"]] == [False, False, True] and out["seed"] == calls[-1][0]
    assert out["run"] == f"fake{calls[-1][0]}"


def test_require_ice_gives_up_after_the_tries_and_off_never_rerolls(data_root, monkeypatch):
    from planet import timeline as T
    calls = []
    monkeypatch.setattr(T, "simulate", _fake_simulate(lambda n: False, calls))
    with pytest.raises(RuntimeError, match="no roll had permanent ice in 2 tries"):
        make.make({"seed": 5, "level": 4, "myr": 40, "finish": False, "timezoom": False, "require_ice": True, "tries": 2})
    assert len(calls) == 2
    calls.clear()
    out = make.make({"seed": 5, "level": 4, "myr": 40, "finish": False, "timezoom": False})  # off: one run, ice ignored
    assert len(calls) == 1 and not calls[0][1] and "rolls" not in out and "seed" not in out


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
    from planet import finish as F  # (the default now: the interglacial pick, or the end of a zoom too short for a cycle)
    tz_run = json.loads((S.find_run(out["timezoom"]) / "run.json").read_text())
    assert w["timezoom_kyr"] == F.now_kyr(tz_run, "interglacial")[0]
    fr = [f for f, _ in log]
    assert fr == sorted(fr) and fr[-1] == 1.0 and fr[0] < 0.1  # progress only goes forward
    assert any("zoom 1/1" in m for _, m in log)


def test_make_builds_a_peoples_run_of_its_own_kind(made, tmp_path):
    """PW-1394: make's peoples stage (after the world, here by resuming the tiny chain) stores a run of kind 'peoples',
    which the index, the planet family and the land-use reader know as such, and not as a time zoom."""
    from planet.lineages import landuse
    out, _ = made
    req = {"seed": 2, "level": 4, "myr": 40, "kyr": 6, "zooms": 0, "name": "tiny make", "peoples": "dnd", "language_workers": 1}
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"spec": make.parse_make_request(req), "out": {k: out[k] for k in ("run", "t_myr", "timezoom", "world")}}))
    log = []
    res = make.make(req, lambda f, m: log.append((f, m)), state=state, resume=True)
    pid = res["peoples"]
    run = json.loads((S.find_run(pid) / "run.json").read_text())
    assert run["kind"] == "peoples" and run["meta"]["kind"] == "peoples" and "phase" not in run["meta"]
    assert run["meta"]["world"] == out["world"] and run["meta"]["tree_name"]
    assert [f for f, _ in log][-1] == 1.0
    # (PW-1634: the languages stage, after the peoples stage, which leaves the pass to it; one report section in run.txt)
    rd = S.find_run(pid)
    assert (rd / "run.txt").read_text().count("languages (PW-986)") == 1 and any(m.startswith("languages:") for _, m in log)
    if "error" in res["languages"]:   # (this tiny chain's 6 kyr time zoom is shorter than the pass's 20 kyr: logged, not fatal)
        assert "lacks frames" in res["languages"]["error"] and not (rd / "languages.json").exists()
    else:
        assert res["languages"]["living"] > 0 and (rd / "languages.json").exists()
    item = next(e for e in S.update_index("run") if e["dir"] == pid)
    assert item["kind"] == "peoples" and item["world"] == out["world"] and item["timezoom"] == out["timezoom"] and "phase" not in item
    ps = family.planets()
    node = next(n for n in ps[0]["nodes"] if n["key"] == f"run:{pid}")
    assert node["kind"] == "peoples" and node["parent"] == f"run:{out['timezoom']}" and node["world"] == out["world"]
    assert ps[0]["counts"]["peoples"] == 1 and ps[0]["counts"]["timezoom"] == 1
    assert landuse._load(S.find_run(pid))[1]["world"] == out["world"]
    with pytest.raises(api.BadRequest, match="peoples run"):  # (a peoples run is neither a time zoom to finish nor a run to zoom in time)
        api.parse_finish_request({"run": pid, "t": 0})
    with pytest.raises(api.BadRequest, match="peoples run"):
        api.parse_timezoom_request({"run": pid, "t": 0})


def test_make_failure_names_the_stage(data_root):
    with pytest.raises(RuntimeError, match=r"simulate failed.*made so far: nothing"):
        make.make({"seed": 1, "level": 4, "myr": 40, "set": {"n_plates": 12}}, lambda f, m: (_ for _ in ()).throw(ValueError("x")))


def test_a_failed_stage_logs_its_traceback(data_root, monkeypatch, capsys):
    """A stage that fails after the run exists (PW-1760: the zoom step on the Windows CI) appends its full traceback to
    the run's run.txt and names the file; with $PLANET_DEBUG it is printed to stderr too."""
    def boom(*a, **k):
        raise OSError(22, "Invalid argument", "layers/barrier_island.bin")
    monkeypatch.setattr(api, "timezoom_job", boom)
    monkeypatch.setenv("PLANET_DEBUG", "1")
    with pytest.raises(RuntimeError, match=r"timezoom failed: \[Errno 22\].*the traceback is in .*run\.txt") as ei:
        make.make({"seed": 1, "level": 4, "myr": 40, "kyr": 10, "zooms": 0})
    rid = re.search(r"made so far: run (\w+)", str(ei.value)).group(1)
    log = (S.find_run(rid) / "run.txt").read_text()
    assert "planet make: timezoom failed:" in log and "Traceback (most recent call last)" in log and "in boom" in log
    assert "in boom" in capsys.readouterr().err


def test_family_and_thumbs_of_a_made_planet(made):
    out, _ = made
    ps = family.planets()
    assert len(ps) == 1
    p = ps[0]
    by = {n["key"]: n for n in p["nodes"]}
    assert by[f"run:{out['timezoom']}"]["parent"] == f"run:{out['run']}"
    assert by[f"world:{out['world']}"]["parent"] == f"run:{out['timezoom']}"
    assert by[f"zoom:{out['zooms'][0]}"]["parent"] == f"world:{out['world']}"
    assert {**p["counts"], "peoples": 0} == {"timezoom": 1, "peoples": 0, "world": 1, "zoom": 1, "fine": 0} and p["thumb"].endswith(out["world"])
    from planet import thumbs
    for kind, i in (("world", out["world"]), ("run", out["run"]), ("run", out["timezoom"])):
        png = thumbs.thumb(kind, i)
        assert png and png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
        assert thumbs.thumb(kind, i) == png  # cached
    eq = thumbs.thumb("world", out["world"], "equirect", 512)  # the globe picker's texture (PW-546)
    assert eq and eq != thumbs.thumb("world", out["world"]) and thumbs.thumb("world", out["world"]) is not None
    assert thumbs.thumb("world", out["world"], "mollweide") is None and thumbs.thumb("world", out["world"], width=77) is None
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
        c.request(method, path, body=json.dumps(body) if body is not None else None,
                  headers={"Content-Type": "application/json"} if body is not None else {})
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


def test_highlight_zooms_job(made):
    """POST /api/highlight-zooms' work: the top highlights' zooms; the same ones `make` made are reused."""
    out, _ = made
    res = api.highlight_zooms_job({"type": "hlzooms", "world": out["world"], "n": 1})
    assert res["zooms"] == out["zooms"] and res["zoom"] == out["zooms"][0] and res["world"] == out["world"]
    assert api.JOBS["hlzooms"] is api.highlight_zooms_job


# ---------------------------------------------------------------- the memory guard says no: skip the zoom (PW-1760)
def _short_of_memory(monkeypatch):
    """The macOS CI runner's case (run 43124045149: 3 GB free, the 2000 km at 4 km/px zoom needs ~4 GB in all): the
    guard's numbers are its own; only the free RAM it reads is made short."""
    monkeypatch.setattr(api, "free_ram_gb", lambda: 0.5)
    built = []
    monkeypatch.setattr(api, "_build_zoom", lambda r, wp, progress: built.append(r) or {"zoom": "never", "world": wp.stem})
    return built


def test_a_zoom_asked_for_on_its_own_still_refuses(made, monkeypatch):
    out, _ = made
    built = _short_of_memory(monkeypatch)
    hl = api.highlights({"world": out["world"]})
    f = next(f for f in hl["features"] if f.get("zoom") is None and f.get("size_km"))  # (one not built by the chain)
    with pytest.raises(api.NoRoom, match=r"not started: not enough free memory: 0 GB free.*to spare") as ei:
        api.zoom_job(api.zoom_request({"world": out["world"]}, f))
    assert isinstance(ei.value, api.BadRequest) and built == []  # (the server's 400 and `planet zoom`'s error, as before)


def test_make_skips_a_zoom_the_memory_guard_refuses(made, monkeypatch, tmp_path):
    """The chain's zooms stage: refused zooms are skipped with a note and the make finishes (the world is usable); a
    zoom already on disk is still reused (no guard)."""
    out, _ = made
    built = _short_of_memory(monkeypatch)
    req = {"seed": 2, "level": 4, "myr": 40, "kyr": 6, "zooms": 3, "name": "tiny make"}
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"spec": make.parse_make_request(req), "out": {k: out[k] for k in ("run", "t_myr", "timezoom", "world")}}))
    log = []
    res = make.make(req, lambda f, m: log.append((f, m)), state=state, resume=True)
    assert built == []
    hl = api.highlights({"world": out["world"]})
    picked = len(api.H.pick_zooms(hl["features"], 3))
    assert res["zooms"] == out["zooms"][:1] and res["world"] == out["world"]  # (the chain's zoom, reused)
    if picked > 1:
        assert re.fullmatch(rf"skipped {picked - 1} of {picked} regional zooms: not enough free memory: 0 GB free, "
                            r"the .* zoom needs about \d+ GB plus .* to spare .*", res["zooms_skipped"])
        assert any(m == res["zooms_skipped"] for _, m in log) and log[-1][0] == 1.0
    else:
        assert "zooms_skipped" not in res


def test_make_skips_its_only_zoom_and_the_cli_exits_0(made, monkeypatch, capsys):
    """`planet make` (and so the installers' warm-up, which runs it) prints a one-line note and exits 0."""
    out, _ = made
    _short_of_memory(monkeypatch)
    fake = {k: out[k] for k in ("run", "t_myr", "timezoom", "world", "highlights")}
    seen = []

    def fake_make(req, progress):  # (the chain from its zooms stage on: the real zoom_highlights, a fresh world's zoom)
        seen.append(req)
        hl = api.highlights({"world": out["world"]})
        feats = [f for f in hl["features"] if f.get("zoom") is None]
        skipped = []
        z = api.zoom_highlights(out["world"], feats, 1, skipped=skipped)
        assert z == [] and skipped[0]["not_made"] == skipped[0]["picked"] == 1
        return {**fake, "zooms": z, "zooms_skipped": f"skipped 1 of 1 regional zoom: {skipped[0]['reason']}"}
    monkeypatch.setattr(make, "make", fake_make)
    monkeypatch.setattr(sys, "argv", ["planet", "make", "--seed", "7", "--level", "4", "--myr", "20", "--kyr", "10",
                                      "--zooms", "1", "--name", "ci"])
    cli.main()  # (no SystemExit: exit 0)
    lines = capsys.readouterr().out.splitlines()
    note = [l for l in lines if l.startswith("note: ")]
    assert len(note) == 1 and seen
    assert note[0].startswith("note: skipped 1 of 1 regional zoom: not enough free memory: 0 GB free")
    assert note[0].endswith("The world is made; zoom in later from the viewer or with `planet zoom`.")
    assert not any(l.startswith("ERROR") for l in lines)


def test_http_cancel_route(made, http_get, monkeypatch):
    gate = threading.Event()
    jobs = api.Jobs(lambda req, progress: (gate.wait(10), {"zoom": "z"})[1])
    monkeypatch.setattr(server.Handler, "jobs", jobs)
    a, b = jobs.submit({"n": 1}), jobs.submit({"n": 2})
    st, _, body = http_get("DELETE", f"/api/jobs/{b}")
    assert st == 200 and json.loads(body)["cancelled"] is True
    st, _, body = http_get("GET", f"/api/jobs/{b}")
    assert json.loads(body)["error"] == "cancelled"
    assert http_get("DELETE", "/api/jobs/nope")[0] == 404
    gate.set()
    jobs.wait(a)
