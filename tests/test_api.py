"""The viewer's zoom API (planet/api.py), driven as plain functions on a tiny
fake run in a temporary data directory."""

import json
import shutil
import time

import pytest

from planet import api, server, store as S, timeline as T, world as W, zoom as Z
from planet.tectonics import Params


@pytest.fixture(scope="module")
def dirs(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("api")
    S.set_root(tmp)
    run = T.simulate(seed=1, level=4, myr=40.0, dt=2.0, every=20.0, name="tiny", params=Params())
    (tmp / "runs" / run.name).rename(tmp / "runs" / "tiny01")
    yield tmp
    S.set_root(None)


def test_parse_zoom_request():
    r = api.parse_zoom_request({"world": "abc.json", "lat": 10, "lon": 190})
    assert r["world"] == "abc" and r["lon"] == -170 and r["size_km"] == 1000 and r["res_km"] == 2
    assert r["iterations"] == 15
    assert api.parse_zoom_request({"world": "abc", "lat": 0, "lon": 0, "iterations": 30})["iterations"] == 30
    # the default keeps the old ids; other iteration counts get their own zoom
    assert Z.zoom_id("abc", 0, 0, 100, 1, 1) == Z.zoom_id("abc", 0, 0, 100, 1, 1, 15) != Z.zoom_id("abc", 0, 0, 100, 1, 1, 30)
    for bad in ({"lat": 0, "lon": 0}, {"run": "x", "world": "y", "lat": 0, "lon": 0},
                {"world": "x", "lat": 95, "lon": 0}, {"world": "x", "lat": 0, "lon": 0, "size_km": 5},
                {"world": "x", "lat": "north", "lon": 0}, {"world": "x", "lat": 0, "lon": 0, "iterations": 0}, {"run": "x", "lat": 0, "lon": 0}):
        with pytest.raises(api.BadRequest):
            api.parse_zoom_request(bad)


def test_zoom_job_from_run(dirs):
    req = {"run": "tiny01", "t": 20, "lat": 5, "lon": 30, "size_km": 400, "res_km": 20}
    seen = []
    res = api.zoom_job(req, lambda f, msg: seen.append(f))
    assert seen and all(0 <= f <= 1 for f in seen) and seen[-1] == 1.0
    meta, layers = Z.load(dirs / "zooms" / res["zoom"])
    assert meta["source_world"]["source_run"] == "tiny01" and meta["source_world"]["t_myr"] == 20
    assert api.world_header(dirs / "worlds" / f"{res['world']}.json")["meta"]["from_keyframe"]
    assert layers["elevation"].shape == (20, 20)
    idx = json.loads((dirs / "zooms" / "index.json").read_text())
    assert idx[0]["source_run"] == "tiny01" and idx[0]["t_myr"] == 20

    # the same run/t again: the slice is reused, not replayed
    assert api.find_slice(dirs / "runs" / "tiny01", 20.0).stem == res["world"]
    res2 = api.zoom_job({**req, "lat": -5}, lambda f, msg: None)
    assert res2["world"] == res["world"] and res2["zoom"] != res["zoom"]
    assert len([p for p in (dirs / "worlds").glob("*.json") if p.name != "index.json"]) == 1


def test_jobs_queue(dirs):
    def fake(req, progress):
        progress(0.5, "half")
        if req.get("fail"):
            raise SystemExit("bad input")
        return {"zoom": "z" + str(req["n"])}

    jobs = api.Jobs(fake)
    a, b, c = jobs.submit({"n": 1}), jobs.submit({"n": 2, "fail": True}), jobs.submit({"n": 3})
    assert jobs.wait(a)["zoom"] == "z1"
    assert jobs.wait(b)["status"] == "error" and jobs.get(b)["error"] == "bad input"
    assert jobs.wait(c)["status"] == "done"
    assert jobs.get("nope") is None


def test_highlights_from_run(dirs):
    # nothing computed yet at 40 Myr: cached_only just says so, without building a world
    res = api.highlights({"run": "tiny01", "t": "40"}, cached_only=True)
    assert res["features"] is None and res["world"] is None
    worlds = lambda: [p for p in (dirs / "worlds").glob("*.json") if p.name != "index.json"]
    n_worlds = len(worlds())

    res = api.highlights({"run": "tiny01", "t": "40"})
    assert res["t_myr"] == 40 and res["features"] and all(f["zoom"] is None for f in res["features"])
    wid = res["world"]
    assert (dirs / "worlds" / "highlights" / f"{wid}.json").exists()
    # the cache is in a subfolder: world listings and slice lookups don't see it
    W.update_index()
    assert [w["id"] for w in json.loads((dirs / "worlds" / "index.json").read_text())].count(wid) == 1
    assert len(worlds()) == n_worlds + 1
    assert api.find_slice(dirs / "runs" / "tiny01", 40.0).stem == wid

    # now cached (also by world id), and a zoom made the way the viewer makes it is found
    again = api.highlights({"world": wid}, cached_only=True)
    assert [f["title"] for f in again["features"]] == [f["title"] for f in res["features"]]
    f = next(f for f in res["features"] if f["zoomable"])
    zr = api.zoom_request(res["source"], f)
    zid = Z.zoom_id(wid, zr["lat"], zr["lon"], zr["size_km"], zr["res_km"], 1)
    (dirs / "zooms" / zid).mkdir(parents=True)
    (dirs / "zooms" / zid / "zoom.json").write_text("{}")
    hit = [g for g in api.highlights({"run": "tiny01", "t": 40})["features"] if g["zoom"]]
    assert [g["title"] for g in hit] == [f["title"]] and hit[0]["zoom"] == zid
    shutil.rmtree(dirs / "zooms" / zid)

    # deleting the world deletes its highlights (through the server's DELETE route)
    assert server.delete(f"/worlds/{wid}") == 204
    assert not (dirs / "worlds" / "highlights" / f"{wid}.json").exists()
    assert server.delete(f"/worlds/{wid}") == 404 and server.delete("/worlds/../runs") == 400

    for bad in ({}, {"run": "tiny01"}, {"run": "tiny01", "t": 900}, {"run": "x", "world": "y"}):
        with pytest.raises(api.BadRequest):
            api.highlights(bad)


def test_timezoom_job(dirs):
    seen = []
    res = api.timezoom_job({"run": "tiny01", "t": 21, "kyr": 4}, lambda f, msg: seen.append((f, msg)))
    assert seen and all(0 <= f <= 1 for f, _ in seen) and seen[-1][0] == 1.0
    run = json.loads((dirs / "runs" / res["run"] / "run.json").read_text())
    m = run["meta"]
    tiny_id = json.loads((dirs / "runs" / "tiny01" / "run.json").read_text())["id"]
    assert run["kind"] == "timezoom" and m["source_run"] == tiny_id and m["at_myr"] == 20 and m["kyr"] == 4
    assert run["frames"][-1]["t"] == 4 and run["layers"]["plate"]["shape"][0] == 1
    # the same request again: the existing time zoom, not a new one
    assert api.timezoom_job({"run": "tiny01", "t": 20, "kyr": 4})["run"] == res["run"]

    # through the shared queue, as the server does; the job carries the new run's id
    jobs = api.Jobs(api.any_job)
    j = jobs.wait(jobs.submit(api.parse_timezoom_request({"run": "tiny01", "t": 20, "kyr": "4"})))
    assert j["status"] == "done" and j["run"] == res["run"]

    for bad in ({}, {"run": "tiny01"}, {"run": "tiny01", "t": 20, "kyr": 0}, {"run": "tiny01", "t": 900},
                {"run": res["run"], "t": 0}):  # the last: a time zoom of a time zoom
        with pytest.raises(api.BadRequest):
            api.parse_timezoom_request(bad)
    with pytest.raises(SystemExit):
        api.parse_timezoom_request({"run": "nope", "t": 0})
    assert S.delete("run", res["run"])


def test_jobs_survive_restart(tmp_path):
    """Job state is saved; a new Jobs on the same file (a restarted server)
    answers for finished jobs and runs again the ones that were cut off,
    once (PW-085)."""
    import threading
    path = tmp_path / "jobs.json"
    gate = threading.Event()

    def slow(req, progress):
        progress(0.5, "half")
        if req["n"] == 2:
            gate.wait(10)
        return {"zoom": "z" + str(req["n"])}

    a = api.Jobs(slow, path)
    j1 = a.submit({"n": 1})
    assert a.wait(j1)["status"] == "done"
    j2, j3 = a.submit({"n": 2}), a.submit({"n": 3})  # j2 hangs, j3 waits behind it: the server "dies" now
    while a.get(j2)["status"] != "running":
        time.sleep(0.01)
    b = api.Jobs(lambda req, progress: {"zoom": "again" + str(req["n"])}, path)
    assert b.get(j1)["zoom"] == "z1"
    assert b.wait(j2)["zoom"] == "again2" and b.get(j2)["restarts"] == 1
    assert b.wait(j3)["zoom"] == "again3"
    j4 = b.submit({"n": 4})
    assert j4 not in (j1, j2, j3) and b.wait(j4)["status"] == "done"  # new ids don't collide with the saved ones
    # a job cut off a second time is given up
    jobs = json.loads(path.read_text())
    jobs[j2].update(status="running")
    path.write_text(json.dumps(jobs))
    c = api.Jobs(lambda req, progress: {}, path)
    assert c.get(j2)["status"] == "error" and "twice" in c.get(j2)["error"]
    gate.set()


def test_compute_lock_serialises_jobs_and_highlights():
    """Jobs (any_job) hold api.COMPUTE, so a highlights computation in a
    server thread waits for them (numba's workqueue layer can't run two
    parallel kernels at once, PW-084)."""
    import threading
    held = []
    api.COMPUTE.acquire()
    try:
        t = threading.Thread(target=lambda: held.append(api.COMPUTE.acquire(timeout=0.2)))
        t.start()
        t.join()
        assert held == [False]
    finally:
        api.COMPUTE.release()
    with api.COMPUTE:  # re-entrant: a job slices a run inside it
        with api.COMPUTE:
            pass
