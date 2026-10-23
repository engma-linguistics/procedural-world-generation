"""Cancelling server jobs, make resuming after a restart (PW-480), and zooms of the top highlights (PW-482)."""

import json
import threading
import time

import pytest

from planet import api, make, server, store as S


def wait_for(cond, timeout=10):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if cond():
            return True
        time.sleep(0.01)
    return False


def test_cancel_a_queued_job_never_starts():
    gate, ran = threading.Event(), []

    def fn(req, progress):
        ran.append(req["n"])
        gate.wait(10)
        return {"zoom": "z"}

    jobs = api.Jobs(fn)
    a, b = jobs.submit({"n": 1}), jobs.submit({"n": 2})
    assert wait_for(lambda: jobs.get(a)["status"] == "running")
    out = jobs.cancel(b)
    assert out == {"id": b, "status": "error", "cancelled": True}
    j = jobs.get(b)
    assert j["status"] == "error" and j["error"] == "cancelled" and j["cancelled"]
    gate.set()
    assert jobs.wait(a)["status"] == "done"
    time.sleep(0.1)
    assert ran == [1] and jobs.get(b)["status"] == "error"  # (b was skipped, not run)
    assert jobs.cancel("nope") is None
    assert jobs.cancel(a)["cancelled"] is False  # already done


def test_cancel_a_running_job_stops_at_its_next_progress_report(monkeypatch):
    stopped, started = threading.Event(), threading.Event()

    def slow(req, progress):
        started.set()
        try:
            for k in range(1000):
                progress(k / 1000, f"step {k}")
                time.sleep(0.01)
        except api.Cancelled:
            stopped.set()
            raise
        return {"zoom": "never"}

    monkeypatch.setitem(api.JOBS, "slow", slow)
    jobs = api.Jobs(api.any_job, contexts=True)
    j = jobs.submit({"type": "slow"})
    assert started.wait(10)
    assert jobs.cancel(j)["cancelled"]
    assert jobs.get(j)["status"] == "error"  # (at once, before the worker has noticed)
    assert stopped.wait(10)  # the worker stopped at its next report
    j2 = jobs.submit({"type": "other"})  # ... and its slot is free again
    assert jobs.wait(j2)["status"] == "error"
    assert jobs.get(j)["error"] == "cancelled" and "zoom" not in jobs.get(j)


@pytest.fixture
def root(tmp_path):
    S.set_root(tmp_path)
    yield tmp_path
    S.set_root(None)


def test_make_cancel_keeps_what_finished(root):
    """A cancel during the time zoom stops make there: the finished run stays. A cancel during the
    simulation leaves nothing (timeline.simulate removes its folder)."""
    flag = root / "cancel"
    req = {"seed": 2, "level": 4, "myr": 30, "kyr": 6, "zooms": 0, "name": "cancel me"}

    def progress(f, msg):
        if "already" not in msg and ("ice" in msg.lower() or "time zoom" in msg.lower()):
            flag.touch()
        if flag.exists():
            raise api.Cancelled("cancelled")

    with pytest.raises(api.Cancelled):
        make.make(req, progress)
    runs = [p.name for p in S.runs_dir().iterdir() if (p / "run.json").is_file()]
    assert len(runs) == 1  # the tectonic run; no half-made second run
    flag.unlink()
    flag.touch()
    with pytest.raises(api.Cancelled):
        make.make({**req, "seed": 3}, progress)
    assert len([p for p in S.runs_dir().iterdir() if p.is_dir() and not p.name.startswith(".")]) == 1


def test_make_resumes_at_the_first_unfinished_stage(root, monkeypatch):
    """A restarted make job reuses a finished run (and time zoom, world) instead of simulating again."""
    state = root / "job.state.json"
    req = {"seed": 2, "level": 4, "myr": 30, "kyr": 6, "zooms": 0, "highlights": False, "name": "resume me"}
    real = api.finish_job

    def die_in_finish(r, progress):
        raise RuntimeError("the server went down")

    monkeypatch.setattr(api, "finish_job", die_in_finish)
    with pytest.raises(RuntimeError, match="world failed"):
        make.make(req, lambda f, m: None, state=state)
    saved = json.loads(state.read_text())["out"]
    assert set(saved) == {"run", "t_myr", "timezoom"}
    # the restart: no simulation, no time zoom; the world is made
    monkeypatch.setattr(api, "finish_job", real)
    from planet import timeline as T

    def fail(*a, **k):
        raise AssertionError("made again")

    monkeypatch.setattr(T, "simulate", fail)
    monkeypatch.setattr(api, "timezoom_job", fail)
    msgs = []
    out = make.make(req, lambda f, m: msgs.append(m), state=state, resume=True)
    assert out["run"] == saved["run"] and out["timezoom"] == saved["timezoom"] and S.exists("world", out["world"])
    assert any("already made" in m for m in msgs)
    assert len([p for p in S.runs_dir().iterdir() if (p / "run.json").is_file()]) == 2  # run + time zoom, no orphan
    # for another request the state is ignored
    assert make._load_state(state, make.parse_make_request({**req, "seed": 9})) == {}
    # a time zoom that was deleted since is not reused
    S.delete("run", saved["timezoom"])
    assert "timezoom" not in make._load_state(state, make.parse_make_request(req))


def test_restarted_make_job_gets_resume(tmp_path):
    """Jobs hands a job's fn a "_job" context: the state file, and resume once it was queued again after a restart."""
    path, seen = tmp_path / "jobs.json", []
    gate = threading.Event()

    def first(req, progress):
        seen.append(req["_job"])
        gate.wait(10)
        return {}

    a = api.Jobs(first, path, contexts=True)
    j = a.submit({"type": "make", "seed": 1})
    assert wait_for(lambda: seen)
    assert seen[0]["resume"] is False and seen[0]["state"].endswith(f"{j}.state.json")
    b = api.Jobs(lambda req, progress: (seen.append(req["_job"]), {})[1], path, contexts=True)  # the "restart"
    assert b.wait(j)["status"] == "done"
    assert seen[-1]["resume"] is True and seen[-1]["state"] == seen[0]["state"]
    gate.set()


def test_highlight_zooms_request():
    with pytest.raises(api.BadRequest):
        api.parse_highlight_zooms_request({})
    with pytest.raises(SystemExit):
        api.parse_highlight_zooms_request({"world": "nonexistent"})
    body, code = server.submit(api.Jobs(lambda r, p: {}), "/api/highlight-zooms", b'{"world": "zzzzzz"}')
    assert code == 404


def test_enrich_request_is_checked_up_front():
    for bad in ({}, {"world": "zzzzzz"}, {"world": "zzzzzz", "what": "ore"}):
        with pytest.raises((api.BadRequest, SystemExit)):
            api.parse_enrich_request(bad)
    body, code = server.submit(api.Jobs(lambda r, p: {}), "/api/enrich", b'{"world": "zzzzzz", "what": "coast"}')
    assert code == 404
