"""Process-level concurrency (planet/parallel.py) and the store's safety
between processes: atomic writes, file locks, and builds in worker processes
that give the same bytes as one after the other."""

import multiprocessing as mp
import os
import threading
import time

import pytest

from planet import api, parallel as P, store as S, timeline as T
from planet.tectonics import Params


def _double(x, progress):
    progress(0.5, f"half of {x}")
    if x == 3:
        raise SystemExit("three is bad")
    return {"x": x, "pid": os.getpid(), "threads": os.environ["NUMBA_NUM_THREADS"],
            "blas": os.environ["OPENBLAS_NUM_THREADS"], "root": str(S.root())}


def test_run_in_workers(data_root):
    seen = []
    out = P.run(_double, [1, 2], workers=2, threads=3, progress=lambda i, f, msg: seen.append((i, f, msg)))
    assert [o["x"] for o in out] == [1, 2]
    assert all(o["threads"] == "3" and o["blas"] == "1" and o["root"] == str(data_root) for o in out)
    assert all(o["pid"] != os.getpid() for o in out)
    assert sorted(seen) == [(0, 0.5, "half of 1"), (1, 0.5, "half of 2")]  # every message, before run returns
    # one item fails: the others still run, then the failure is raised (also in this process, workers=1)
    for workers in (2, 1):
        done = []
        with pytest.raises(SystemExit, match="three is bad"):
            P.run(_double, [1, 3, 2], workers=workers, threads=1, on_done=lambda i, r: done.append(i))
        assert sorted(done) == [0, 2]
    assert P.run(_double, []) == []


def test_defaults():
    assert 1 <= P.default_workers() <= max(1, P.cpus())
    assert P.default_workers(2) <= 2 and P.default_workers(1) == 1
    assert 1 <= P.worker_threads(4) <= P.MAX_WORKER_THREADS
    import numba
    import planet
    assert planet.THREADING_LAYER in ("tbb", "workqueue", "omp") or os.environ.get("NUMBA_THREADING_LAYER")
    assert numba.config.THREADING_LAYER == planet.THREADING_LAYER
    assert os.environ["OPENBLAS_NUM_THREADS"] == "1"  # (always: outputs depend on it)


def test_write_atomic(tmp_path, monkeypatch):
    p = tmp_path / "a.json"
    S.write_atomic(p, "old")
    S.write_atomic(p, b"new")
    assert p.read_text() == "new"
    real = type(p).write_bytes

    def half_then_fail(self, data):  # the disk fills half way through: the old file stays whole
        real(self, data[: len(data) // 2])
        raise OSError("disk full")
    monkeypatch.setattr(type(p), "write_bytes", half_then_fail)
    with pytest.raises(OSError):
        S.write_atomic(p, b"newer, longer")
    assert p.read_text() == "new" and [q.name for q in tmp_path.iterdir()] == ["a.json"]


def _hold(base, name, ready, seconds):
    with S.lock(base, name):
        ready.set()
        time.sleep(seconds)


def test_lock_between_processes_and_threads(tmp_path):
    ctx = mp.get_context("spawn")
    ready = ctx.Event()
    p = ctx.Process(target=_hold, args=(tmp_path, "slice-x", ready, 1.0))
    p.start()
    try:
        assert ready.wait(30)
        t0 = time.time()
        with S.lock(tmp_path, "other"):  # another name: no wait
            assert time.time() - t0 < 0.5
        with S.lock(tmp_path, "slice-x"):  # held by the other process until it lets go
            assert time.time() - t0 > 0.5
            with S.lock(tmp_path, "slice-x"):  # re-entrant in this thread
                pass
            held = []
            th = threading.Thread(target=lambda: held.append(_try(tmp_path, "slice-x")))
            th.start()
            th.join()
            assert held == [False]  # another thread waits too
    finally:
        p.join(10)
    assert not any(q.suffix == ".tmp" for q in tmp_path.rglob("*"))


def _try(base, name):
    """Whether another thread gets the lock within 0.3 s."""
    done = threading.Event()
    th = threading.Thread(target=lambda: (S.lock(base, name).__enter__(), done.set()), daemon=True)
    th.start()
    return done.wait(0.3)


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("par")
    S.set_root(tmp)
    run = T.simulate(seed=1, level=4, myr=40.0, dt=2.0, every=20.0, name="tiny", params=Params())
    (tmp / "runs" / run.name).rename(tmp / "runs" / "tiny02")
    yield tmp
    S.set_root(None)


def _files(d):
    """{relative path: bytes} of a zoom folder, zoom.json without its timing fields."""
    import json
    out = {}
    for p in sorted(d.rglob("*")):
        if p.is_file():
            b = p.read_bytes()
            if p.name == "zoom.json":
                m = json.loads(b)
                m.pop("created"), m.pop("generated_in_s")
                b = json.dumps(m, sort_keys=True).encode()
            out[str(p.relative_to(d))] = b
    return out


def test_jobs_in_worker_processes_match_sequential(tiny):
    """Two zooms of one run moment through the server's queue with two worker
    processes: they run at once, slice the run once between them (the file
    lock), and give the same bytes as building them one after the other here."""
    reqs = [{"run": "tiny02", "t": 20, "lat": la, "lon": 30, "size_km": 400, "res_km": 20} for la in (5, -5)]
    worlds = lambda: [p for p in (tiny / "worlds").glob("*.json") if p.name != "index.json"]
    with P.Pool(2, threads=2) as pool:
        jobs = api.Jobs(pool.caller(api.any_job), workers=2)
        ids = [jobs.submit(r) for r in reqs]
        assert jobs.submit(dict(reqs[0])) == ids[0]  # the same request -> the same job
        res = [jobs.wait(j, timeout=300) for j in ids]
    assert [r["status"] for r in res] == ["done", "done"], res
    assert len(worlds()) == 1 and res[0]["world"] == res[1]["world"]  # sliced once
    assert all(r["progress"] == 1.0 and r["message"] == "done" for r in res)
    t0 = [r["started"] for r in res]
    assert t0[0] <= t0[1] < min(r["finished"] for r in res)  # in submission order, and at once
    import json
    idx = {e["id"] for e in json.loads((tiny / "zooms" / "index.json").read_text())}
    assert {r["zoom"] for r in res} <= idx  # neither index write lost the other's zoom

    par = {r["zoom"]: _files(tiny / "zooms" / r["zoom"]) for r in res}
    for r in res:
        assert S.delete("zoom", r["zoom"])
    for req in reqs:  # one after the other, in this process
        api.zoom_job(req)
    seq = {z: _files(tiny / "zooms" / z) for z in par}
    assert seq == par


def test_zoom_built_twice_at_once_is_built_once(tiny):
    """The same zoom asked for by two processes at once (e.g. the CLI beside
    the server): one builds it, the other finds it."""
    req = {"run": "tiny02", "t": 20, "lat": 0, "lon": -40, "size_km": 400, "res_km": 20}
    msgs = []
    out = P.run(api.zoom_job, [req, req], workers=2, threads=2, progress=lambda i, f, m: msgs.append(m))
    assert out[0] == out[1]
    assert sum("already exists" in m for m in msgs) == 1
    assert S.delete("zoom", out[0]["zoom"])


def test_highlights_in_worker_processes(tiny):
    """The server's highlights (PW-261): what isn't cached is sliced and
    computed in worker processes, two worlds at once; then it is cached."""
    from concurrent.futures import ThreadPoolExecutor
    reqs = [{"run": "tiny02", "t": t} for t in (0, 40)]
    with P.Pool(2, threads=2) as pool, ThreadPoolExecutor(2) as ex:
        res = list(ex.map(lambda r: api.highlights(r, compute=pool.call), reqs))
    assert res[0]["world"] != res[1]["world"] and all(r["features"] for r in res)
    for req, r in zip(reqs, res):
        again = api.highlights(req, cached_only=True)
        assert again["world"] == r["world"] and again["features"] == r["features"]
