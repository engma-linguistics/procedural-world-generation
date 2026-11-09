"""Refining a world from the viewer (PW-1438): POST /api/refine on the server's job queue, its cost and room checks,
one refine at a time, progress and cancel. The real path is a tiny L4 world refined to L5 (seconds); the heavy L8 / L9
refines are never run here."""

import json
import threading
import time

import pytest

from planet import api, family, refine as RF, server, store as S, timeline as T, world as W
from planet.tectonics import Params


@pytest.fixture(scope="module")
def src(tmp_path_factory):
    """A tiny L4 run's keyframe world (a world from a run, as the viewer refines), in its own data root."""
    tmp = tmp_path_factory.mktemp("refinejob")
    S.set_root(tmp)
    run = T.simulate(seed=1, level=4, myr=40.0, dt=2.0, every=20.0, name="tiny", params=Params())
    path = W.save(T.world_from_frame(run, 40.0), "tiny @ 40 Myr")
    yield path.stem
    S.set_root(None)


@pytest.fixture
def roomy(monkeypatch):
    """Plenty of memory, /tmp and disk, whatever the machine has now."""
    monkeypatch.setattr(api, "free_ram_gb", lambda: 500.0)
    monkeypatch.setattr(api, "free_disk_gb", lambda path: 5000.0)


def post(jobs, body):
    return server.submit(jobs, "/api/refine", json.dumps(body).encode())


def test_cost_matches_the_measured_refines():
    """The fit reproduces lane 104's L7 -> L8 (~7 min, 10.8 GB) and L7 -> L9 (38 min, 38.8 GB) within 10%."""
    c8, c9 = RF.cost(8), RF.cost(9)
    assert c8["cells"] == 655_362 and c9["cells"] == 2_621_442
    assert abs(c8["minutes"] - 7) < 0.7 and abs(c9["minutes"] - 38) < 3.8
    assert abs(c8["peak_gb"] - 10.8) < 1.1 and abs(c9["peak_gb"] - 38.8) < 3.9
    assert RF.cost(7)["minutes"] < c8["minutes"] < c9["minutes"]


def test_request_is_checked_up_front(src):
    with pytest.raises(api.BadRequest):
        api.parse_refine_request({"world": src, "level": 4})  # not finer
    with pytest.raises(api.BadRequest):
        api.parse_refine_request({"world": src, "level": 10})  # past L9
    with pytest.raises(api.BadRequest):
        api.parse_refine_request({})
    with pytest.raises(SystemExit):
        api.parse_refine_request({"world": "nosuchworld", "level": 8})
    assert api.parse_refine_request({"world": src, "level": 5}) == {"type": "refine", "world": src, "level": 5}
    body, code = server.refine_estimate(None, f"world={src}&level=99")
    assert code == 400 and "level" in body["error"]


def test_refused_when_memory_or_tmp_is_short(src, monkeypatch):
    monkeypatch.setattr(api, "free_disk_gb", lambda path: 5000.0)
    monkeypatch.setattr(api, "free_ram_gb", lambda: 12.0)
    e = api.refine_estimate({"world": src, "level": 9})  # needs ~39 GB + 8 spare
    assert not e["ok"] and any("memory" in r for r in e["refuse"])
    assert any("minutes" in w for w in e["warn"]) and any("opens slowly" in w for w in e["warn"]) and e["opens_in_viewer"]
    jobs = api.Jobs(lambda req, progress: pytest.fail("must not start"))
    body, code = post(jobs, {"world": src, "level": 9})
    assert code == 409 and "memory" in body["error"] and not jobs.jobs
    monkeypatch.setattr(api, "free_ram_gb", lambda: 500.0)
    monkeypatch.setattr(api, "free_disk_gb", lambda path: 20.0 if "tmp" in str(path) else 5000.0)
    e = api.refine_estimate({"world": src, "level": 8})
    assert not e["ok"] and any("/tmp" in r for r in e["refuse"])


def test_one_refine_at_a_time(src, roomy):
    gate, started = threading.Event(), threading.Event()

    def fn(req, progress):
        started.set()
        gate.wait(10)
        return {"world": "w"}

    jobs = api.Jobs(fn, workers=2)
    body, code = post(jobs, {"world": src, "level": 5})
    assert code == 200
    a = body["job"]
    assert started.wait(10)
    assert jobs.get(a)["request"]["estimate_min"] > 0  # (the viewer's ETA)
    body, code = post(jobs, {"world": src, "level": 6})  # another refine while one runs: refused
    assert code == 409 and a in body["error"]
    est, _ = server.refine_estimate(jobs, f"world={src}&level=6")
    assert est["busy"] == a and not est["ok"]
    act = server.active_job(jobs, "type=refine")["active"]  # (a page opened now follows it)
    assert act["id"] == a and act["request"]["world"] == src and act["status"] == "running"
    assert server.active_job(jobs, "type=zoom") == {"active": None}
    gate.set()
    assert jobs.wait(a)["status"] == "done"
    assert server.active_job(jobs, "type=refine") == {"active": None}
    assert post(jobs, {"world": src, "level": 6})[1] == 200  # free again


def test_refine_job_makes_the_world_with_progress(src, roomy):
    """The real path through the server's queue (in-process): L4 -> L5, progress through every stage, the new
    world listed under its source in the family tree, and the estimate then names it."""
    jobs = api.Jobs(api.any_job, contexts=True)
    seen = []
    orig = jobs._update

    def spy(jid, **kw):
        if "progress" in kw and "message" in kw:
            seen.append((kw["progress"], kw["message"]))
        orig(jid, **kw)
    jobs._update = spy
    body, code = post(jobs, {"world": src, "level": 5})
    assert code == 200
    j = jobs.wait(body["job"], timeout=300)
    assert j["status"] == "done", j.get("error")
    new = j["world"]
    assert j["level"] == 5 and S.exists("world", new)
    m = S.read_header(S.find_world(new), ("meta",))["meta"]
    assert m["level"] == 5 and m["refined_from"]["world"] == src
    fr = [f for f, _ in seen]
    assert fr == sorted(fr) and fr[-1] == 1.0
    stages = {msg.split(": ", 1)[1] for _, msg in seen if msg.startswith("refining to L5: ")}
    assert set(RF.STEPS) - {"erosion"} <= stages  # (erosion runs when the finish erodes: refine.EROSION > 0)
    S.update_index("world")
    node = next(n for p in family.planets() for n in p["nodes"] if n["key"] == f"world:{new}")
    assert node["parent"] == f"world:{src}" and node["refined_from"] == src and node["level"] == 5
    assert api.refine_estimate({"world": src, "level": 5})["existing"] == new


def test_cancel_stops_at_the_next_stage(src, roomy, tmp_path):
    flag = tmp_path / "x.cancel"
    flag.touch()
    with pytest.raises(api.Cancelled):
        api.any_job({"type": "refine", "world": src, "level": 5, "_job": {"cancel": str(flag)}}, lambda f, m: None)


def test_job_start_checks_the_room_again(src, monkeypatch):
    """Queued behind other jobs, memory may be gone by the time it starts: the job then fails with the reason."""
    monkeypatch.setattr(api, "free_disk_gb", lambda path: 5000.0)
    monkeypatch.setattr(api, "free_ram_gb", lambda: 1.0)
    monkeypatch.setattr(RF, "refine_world", lambda *a, **k: pytest.fail("must not run"))
    with pytest.raises(api.BadRequest, match="memory"):
        api.refine_job({"type": "refine", "world": src, "level": 5})
