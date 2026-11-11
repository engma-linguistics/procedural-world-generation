"""Sections in the API (PW-1674, docs/review/zoom/lod-plan.md step 1): POST /api/zoom {world, section, res_km} builds
or reuses a tiling section, GET /api/sections lists them with what is built, and zoom jobs are refused when the free
memory cannot hold their expected peak (and run one section at a time). The build itself is stubbed (regional.build
and save, and the steps after it): what is checked is the request, the id, the orientation handed to the build, the guard and the listing."""
import http.client
import http.server
import json
import threading

import numpy as np
import pytest

from planet import api, server, store as S, world as W
from planet.geo import R_KM, xyz
from planet.grid import build_grid
from planet.zoom import regional as Z
from planet.zoom import tiling as ZT


@pytest.fixture
def world_id(data_root):
    """A saved level-4 world with a continent round (10, 20) (enough for the zoom's own checks)."""
    g = build_grid(4)
    d = np.arccos(np.clip(g.centers @ xyz(np.radians(10.0), np.radians(20.0)), -1, 1)) * R_KM
    elev = np.where(d < 4000, 300 + 0.3 * (4000 - d), -3000.0)
    land = elev > 0
    extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2), "sediment_cover": np.where(land, 0.2, 6.0)}
    w = W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 4}, erosion=0.0)
    return W.save(w, "section test world").stem


@pytest.fixture
def stub_build(monkeypatch):
    """regional.build / save replaced: build returns only the frame, save writes a minimal zoom.json under the id the
    real save would give. Returns the list of build calls."""
    calls = []

    def build(world, lat, lon, size_km, res_km, seed, iterations, **kw):
        calls.append({"lat": lat, "lon": lon, "size_km": size_km, "res_km": res_km, "up": kw["up"], "section": kw["section"]})
        return {"frame": Z.Frame(lat, lon, up=kw["up"])}

    def save(z, world_path, world, lat, lon, size_km, res_km, seed, iterations=15, peoples=None, section=None, match=()):
        zid = Z.zoom_id(world_path.stem, lat, lon, size_km, res_km, seed, iterations, peoples, Z._up_list(z["frame"]), match)
        out = S.path_of("zoom", zid)
        out.mkdir(parents=True)
        meta = {"id": zid, "name": "stub", "created": "2026-11-10 00:00:00", "source_world": {"id": world_path.stem},
                "center": {"lat": lat, "lon": lon}, "size_km": size_km, "res_km": res_km,
                **({"section": section} if section else {})}
        S.write_atomic(out / "zoom.json", json.dumps(meta))
        Z.update_index()
        return out

    monkeypatch.setattr(Z, "build", build)
    monkeypatch.setattr(Z, "save", save)
    monkeypatch.setattr(Z.ZC, "add_to_zoom", lambda *a, **k: None)  # (the steps after the save)
    monkeypatch.setattr(Z, "add_deposits", lambda *a, **k: None)
    monkeypatch.setattr(api, "free_ram_gb", lambda: 500.0)  # (a stubbed build needs no RAM; the host's, under a test cgroup cap, must not refuse it)
    return calls


def test_parse_section_request():
    r = api.parse_zoom_request({"world": "abc.json", "section": "px.1.1"})
    assert r == {"world": "abc", "section": "px.1.1", "size_km": 4000.0, "res_km": 2.0, "seed": 1, "iterations": 15}
    assert api.parse_zoom_request({"world": "abc", "section": "pz.0.2", "res_km": "4"})["res_km"] == 4.0
    assert api.parse_zoom_request({"world": "abc", "section": "px.1.1", "res_km": 1})["res_km"] == 1.0
    for bad in ({"world": "abc", "section": "qq.1.1"}, {"world": "abc", "section": "px.9.9"},
                {"world": "abc", "section": "px.1.1", "res_km": 0.5},  # over 4,096 px across
                {"world": "abc", "section": "px.1.1", "res_km": 8},  # too coarse for fine zooms to nest in
                {"world": "abc", "section": "px.1.1", "res_km": "fine"},
                {"run": "r", "t": 1, "section": "px.1.1"}, {"section": "px.1.1"},
                {"world": "abc", "section": "px.1.1", "iterations": 0}):
        with pytest.raises(api.BadRequest):
            api.parse_zoom_request(bad)


def test_peak_estimate_follows_the_measured_builds():
    assert api.zoom_peak_gb(4000, 4) == pytest.approx(8.0)
    assert api.zoom_peak_gb(4000, 2) == pytest.approx(25.0)
    assert api.zoom_peak_gb(4000, 1) == pytest.approx(110.0)
    assert api.zoom_peak_gb(4000, 3) == pytest.approx(api.zoom_peak_gb(4000, 3), rel=0)
    assert 8.0 < api.zoom_peak_gb(4000, 3) < 25.0 and 25.0 < api.zoom_peak_gb(4000, 1.5) < 110.0
    assert api.zoom_peak_gb(500, 1) < 3.0 and api.zoom_peak_gb(20, 0.1) >= 1.5  # small zooms: small
    assert api.zoom_is_heavy({"size_km": 4000, "res_km": 4}) and not api.zoom_is_heavy({"size_km": 2000, "res_km": 4})


def test_section_builds_then_is_reused(data_root, world_id, stub_build):
    seen = []
    res = api.zoom_job({"world": world_id, "section": "px.1.1", "res_km": 2}, lambda f, m: seen.append(f))
    assert res["section"] == "px.1.1" and res["world"] == world_id and seen[-1] == 1.0
    sec = ZT.section("px.1.1")
    assert len(stub_build) == 1
    b = stub_build[0]
    assert (b["size_km"], b["res_km"], b["section"]) == (4000.0, 2.0, "px.1.1")
    assert b["lat"] == pytest.approx(sec["lat"]) and np.allclose(b["up"], Z.up_of(sec["lat"], sec["lon"], sec["up"]))
    # the id is the one the API predicts without building
    parsed = api.parse_zoom_request({"world": world_id, "section": "px.1.1", "res_km": 2})
    assert res["zoom"] == api.section_zoom_id(parsed, world_id) == api.existing_zoom(parsed)
    # again: reused, nothing built; another resolution is another zoom
    res2 = api.zoom_job({"world": world_id, "section": "px.1.1", "res_km": 2}, lambda f, m: None)
    assert res2["zoom"] == res["zoom"] and len(stub_build) == 1
    res3 = api.zoom_job({"world": world_id, "section": "px.1.1", "res_km": 4}, lambda f, m: None)
    assert res3["zoom"] != res["zoom"] and len(stub_build) == 2


def test_listing_marks_built_sections(data_root, world_id, stub_build):
    lst = api.sections_listing(world_id)
    assert lst["world"] == world_id and lst["size_km"] == 4000.0 and len(lst["sections"]) == 54
    assert not any(s["built"] for s in lst["sections"])
    by = {s["id"]: s for s in lst["sections"]}
    s = by["px.1.1"]
    assert set(s) >= {"id", "lat", "lon", "up", "corners", "land_share", "neighbours", "zooms", "built", "margin_km"}
    assert len(s["neighbours"]) == 8 and set(s["corners"]) == {"nw", "ne", "se", "sw"}
    assert all(0.0 <= x["land_share"] <= 1.0 for x in lst["sections"]) and max(x["land_share"] for x in lst["sections"]) > 0
    zid = api.zoom_job({"world": world_id, "section": "px.1.1", "res_km": 2}, lambda f, m: None)["zoom"]
    api.zoom_job({"world": world_id, "section": "px.1.1", "res_km": 4}, lambda f, m: None)
    by = {s["id"]: s for s in api.sections_listing(world_id)["sections"]}
    assert by["px.1.1"]["built"] and by["px.1.1"]["zooms"]["2"] == zid and set(by["px.1.1"]["zooms"]) == {"2", "4"}
    assert [k for k, s in by.items() if s["built"]] == ["px.1.1"]
    with pytest.raises(SystemExit):
        api.sections_listing("nosuch")


def test_sections_endpoint(data_root, world_id):
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        def get(path):
            c = http.client.HTTPConnection("127.0.0.1", httpd.server_address[1], timeout=60)
            c.request("GET", path)
            r = c.getresponse()
            out = r.status, json.loads(r.read())
            c.close()
            return out

        status, body = get(f"/api/sections?world={world_id}")
        assert status == 200 and len(body["sections"]) == 54
        assert get("/api/sections")[0] == 400 and get("/api/sections?world=nosuch")[0] == 404
    finally:
        httpd.shutdown()
        httpd.server_close()


class FakeJobs:
    """Enough of api.Jobs for server.submit: records submissions; `running` lists requests counted as active."""

    def __init__(self):
        self.running, self.submitted = [], []

    def active_where(self, pred):
        return next((f"j{i}" for i, q in enumerate(self.running) if pred(q)), None)

    def active(self, kind):
        return None

    def submit(self, req):
        self.submitted.append(req)
        return f"s{len(self.submitted)}"


def _post(jobs, body):
    return server.submit(jobs, "/api/zoom", json.dumps(body).encode())


def test_big_zoom_refused_without_the_ram(data_root, world_id, monkeypatch):
    jobs = FakeJobs()
    monkeypatch.setattr(api, "free_ram_gb", lambda: 40.0)  # 1 km needs 110 + 8
    out, status = _post(jobs, {"world": world_id, "section": "px.1.1", "res_km": 1})
    assert status == 409 and jobs.submitted == []
    assert "110 GB" in out["error"] and "40 GB free" in out["error"] and "118 GB in all" in out["error"]
    assert "2 km/px would fit now" in out["error"]  # (25 + 8 <= 40)
    assert out["estimate"]["peak_gb"] == 110.0 and out["estimate"]["need_gb"] == 118.0
    # the job re-checks before it builds: memory may have gone while it waited
    with pytest.raises(api.BadRequest, match="110 GB"):
        api.zoom_job({"world": world_id, "section": "px.1.1", "res_km": 1})
    # 2 km fits in 40 GB; and a small ordinary zoom needs little
    assert _post(jobs, {"world": world_id, "section": "px.1.1", "res_km": 2})[1] == 200
    monkeypatch.setattr(api, "free_ram_gb", lambda: 12.0)
    assert _post(jobs, {"world": world_id, "lat": 10, "lon": 20, "size_km": 500, "res_km": 1})[1] == 200
    assert _post(jobs, {"world": world_id, "section": "px.1.1", "res_km": 2})[1] == 409
    monkeypatch.setattr(api, "free_ram_gb", lambda: None)  # unreadable: let it through
    assert _post(jobs, {"world": world_id, "section": "px.1.1", "res_km": 1})[1] == 200


def test_an_existing_zoom_needs_no_ram(data_root, world_id, stub_build, monkeypatch):
    monkeypatch.setattr(api, "free_ram_gb", lambda: 500.0)
    api.zoom_job({"world": world_id, "section": "px.1.1", "res_km": 1}, lambda f, m: None)  # (stubbed: no real 1 km build)
    monkeypatch.setattr(api, "free_ram_gb", lambda: 1.0)
    jobs = FakeJobs()
    assert _post(jobs, {"world": world_id, "section": "px.1.1", "res_km": 1})[1] == 200
    res = api.zoom_job({"world": world_id, "section": "px.1.1", "res_km": 1}, lambda f, m: None)  # reused, not refused
    assert res["section"] == "px.1.1" and len(stub_build) == 1


def test_one_section_sized_job_at_a_time(data_root, world_id, monkeypatch):
    monkeypatch.setattr(api, "free_ram_gb", lambda: 500.0)
    jobs = FakeJobs()
    first = {"world": world_id, "section": "px.1.1", "res_km": 2}
    out, status = _post(jobs, first)
    assert status == 200
    jobs.running.append(jobs.submitted[0])
    out, status = _post(jobs, {"world": world_id, "section": "py.1.1", "res_km": 2})
    assert status == 409 and "one at a time" in out["error"] and "j0" in out["error"]
    assert _post(jobs, first)[1] == 200  # the same request is the same job (Jobs.submit): not refused
    assert _post(jobs, {"world": world_id, "lat": 10, "lon": 20, "size_km": 500, "res_km": 1})[1] == 200  # a small zoom runs beside it
    # a refine or a time zoom in the queue is not a zoom
    jobs.running[:] = [{"type": "refine", "world": "w", "level": 8}]
    assert _post(jobs, {"world": world_id, "section": "py.1.1", "res_km": 2})[1] == 200


def test_jobs_active_where():
    jobs = api.Jobs(fn=lambda req, progress: {})
    assert jobs.active_where(lambda q: True) is None
    jobs.jobs["1"] = {"id": "1", "key": "k", "request": {"size_km": 4000, "res_km": 2}, "status": "running"}
    jobs.jobs["2"] = {"id": "2", "key": "k2", "request": {"size_km": 10, "res_km": 1}, "status": "done"}
    assert jobs.active_where(api.zoom_is_heavy) == "1"
    jobs.jobs["1"]["status"] = "done"
    assert jobs.active_where(api.zoom_is_heavy) is None
