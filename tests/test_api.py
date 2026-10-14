"""The viewer's zoom API (planet/api.py), driven as plain functions on a tiny
fake run in a temporary data directory."""

import json
from dataclasses import asdict

import pytest

from planet import api, timeline as T, world as W, zoom as Z
from planet.tectonics import Params


@pytest.fixture
def dirs(tmp_path, monkeypatch):
    for mod, name in ((W, "WORLDS"), (T, "RUNS"), (Z, "ZOOMS")):
        (tmp_path / name.lower()).mkdir()
        monkeypatch.setattr(mod, name, tmp_path / name.lower())
    # a run is fully determined by its meta; replay doesn't need frames
    run = {"id": "tiny01", "name": "tiny", "meta": {"seed": 1, "level": 4, "dt": 2.0, "myr": 40.0,
                                                    "params": asdict(Params())}, "frames": []}
    (tmp_path / "runs" / "tiny01").mkdir()
    (tmp_path / "runs" / "tiny01" / "run.json").write_text(json.dumps(run))
    return tmp_path


def test_parse_zoom_request():
    r = api.parse_zoom_request({"world": "abc.json", "lat": 10, "lon": 190})
    assert r["world"] == "abc" and r["lon"] == -170 and r["size_km"] == 1000 and r["res_km"] == 2
    for bad in ({"lat": 0, "lon": 0}, {"run": "x", "world": "y", "lat": 0, "lon": 0},
                {"world": "x", "lat": 95, "lon": 0}, {"world": "x", "lat": 0, "lon": 0, "size_km": 5},
                {"world": "x", "lat": "north", "lon": 0}, {"run": "x", "lat": 0, "lon": 0}):
        with pytest.raises(api.BadRequest):
            api.parse_zoom_request(bad)


def test_zoom_job_from_run(dirs):
    req = {"run": "tiny01", "t": 20, "lat": 5, "lon": 30, "size_km": 400, "res_km": 20}
    seen = []
    res = api.zoom_job(req, lambda f, msg: seen.append(f))
    assert seen and all(0 <= f <= 1 for f in seen) and seen[-1] == 1.0
    meta, layers = Z.load(dirs / "zooms" / res["zoom"])
    assert meta["source_world"]["source_run"] == "tiny01" and meta["source_world"]["t_myr"] == 20
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
