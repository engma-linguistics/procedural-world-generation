"""The level-of-detail tile service (planet/tiles.py, PW-1690): the queue follows the view (coarse first, then the
viewer's order; a new list replaces it; a running build is kept), parents are built before children, the RAM guard
and one-section-at-a-time rule, the disk cache's cap, and the tile files. Builds are faked: a fake job queue whose jobs
"finish" by writing a small zoom directory where the real build would."""
import json
import struct
import time

import numpy as np
import pytest

from planet import api
from planet import store as S
from planet import tiles as T
from planet.zoom import lod as L

W = "w00001"


def _fake_tile_dir(d, n=4, value=0.0, sat=True):
    (d / "layers").mkdir(parents=True, exist_ok=True)
    elev = (np.arange(n * n, dtype=np.float32).reshape(n, n) * 10 + value)
    water = (elev < 20).astype(np.uint8)
    (d / "layers" / "elevation.bin").write_bytes(elev.tobytes())
    (d / "layers" / "water.bin").write_bytes(water.tobytes())
    if sat:
        from planet.images import png_bytes
        (d / "satellite.png").write_bytes(png_bytes(np.zeros((n, n, 3), np.uint8)))
    meta = {"id": d.name, "source_world": {"id": W}, "files": {"satellite": "satellite.png"},
            "layers": {"elevation": {"file": "layers/elevation.bin", "dtype": "float32", "shape": [n, n]},
                       "water": {"file": "layers/water.bin", "dtype": "uint8", "shape": [n, n]}}}
    (d / "zoom.json").write_text(json.dumps(meta))
    return elev, water


class FakeJobs:
    """api.Jobs' surface the service uses; finish(jid) writes the tile where the real build would."""

    def __init__(self):
        self.jobs, self.order = {}, []

    def submit(self, req):
        key = json.dumps(req, sort_keys=True)
        for jid, j in self.jobs.items():
            if j["key"] == key and j["status"] in ("queued", "running"):
                return jid
        jid = str(len(self.jobs) + 1)
        self.jobs[jid] = {"key": key, "request": req, "status": "queued"}
        self.order.append(jid)
        return jid

    def get(self, jid):
        j = self.jobs.get(jid)
        return None if j is None else {k: v for k, v in j.items() if k != "key"}

    def cancel(self, jid):
        j = self.jobs[jid]
        if j["status"] in ("queued", "running"):
            j.update(status="error", error="cancelled", cancelled=True)

    def active_where(self, pred):
        return next((jid for jid, j in self.jobs.items() if j["status"] in ("queued", "running") and pred(j["request"])), None)

    def tile_of(self, jid) -> L.Key:
        r = self.jobs[jid]["request"]
        return L.Key.parse(r["tile"]) if r.get("type") == "tile" else L.Key(r["section"], 1, 0, 0)

    def finish(self, jid, ok=True):
        k = self.tile_of(jid)
        if ok:
            zid = (api.section_zoom_id(T.TileService._section_request(W, k.cell), W) if k.level == 1
                   else L.tile_id(W, k, T.SEED))
            _fake_tile_dir(S.zooms_dir() / zid)
            self.jobs[jid].update(status="done", zoom=zid)
        else:
            self.jobs[jid].update(status="error", error="boom")

    def started(self):
        """Keys of jobs submitted and not cancelled, in submission order."""
        return [str(self.tile_of(j)) for j in self.order if not self.jobs[j].get("cancelled")]

    def live(self):
        return [j for j in self.order if self.jobs[j]["status"] in ("queued", "running")]


@pytest.fixture
def svc(tmp_path):
    (tmp_path / "zooms").mkdir()
    S.set_root(tmp_path)
    jobs = FakeJobs()
    s = T.TileService(jobs, cap_gb=60, free_ram=lambda: 500.0)
    s._wids[W] = W
    s.fake = jobs
    yield s
    S.set_root(None)


def _l2(cell="py.1.1"):
    return [k for k in (L.Key(cell, 2, x, y) for y in range(8) for x in range(8)) if L.exists(k)]


def _finish_all(s):
    for jid in s.fake.live():
        s.fake.finish(jid)
    s.pump()


def _drain(s):
    while s.fake.live():
        _finish_all(s)


def test_parents_first_then_coarse_then_the_viewers_order(svc):
    s = svc
    l2 = _l2()
    centre, others = l2[27], [l2[3], l2[40], l2[10], l2[50]]
    st = s.want(W, [str(k) for k in [centre, *others]] + ["py.1.1/1/0/0"])
    # the level-1 section goes first (every level-2 tile reads it), whatever its place in the list
    assert [k for k, t in st["tiles"].items() if t["state"] == "building"] == ["py.1.1/1/0/0"]
    assert s.fake.started() == ["py.1.1/1/0/0"]
    assert st["tiles"][str(centre)] == {"state": "queued", "pos": 1}
    assert st["waiting"] == 5  # (queued, their parent not built yet)
    _finish_all(s)
    # then the level-2 tiles in the viewer's order (the centre first), three at once
    assert s.fake.started()[1:] == [str(centre), str(others[0]), str(others[1])]
    st = s.status(W)
    assert st["building"] == 3 and st["queued"] == 2 and st["tiles"]["py.1.1/1/0/0"] == {"state": "built"}
    _finish_all(s)
    _finish_all(s)
    st = s.status(W)
    assert st["building"] == 0 and st["queued"] == 0
    assert all(st["tiles"][str(k)]["state"] == "built" for k in [centre, *others])
    assert s.fake.started()[4:] == [str(others[2]), str(others[3])]


def test_a_new_list_replaces_the_queue_and_keeps_a_running_build(svc):
    s = svc
    l2 = _l2()
    s.want(W, ["py.1.1/1/0/0"])
    _finish_all(s)
    s.at_once = 2
    a = [l2[0], l2[1], l2[2], l2[3]]
    s.want(W, [str(k) for k in a])
    j_run, j_wait = s.fake.live()
    s.fake.jobs[j_run]["status"] = "running"  # (the first is building; the second still waits for a worker)
    b = [l2[30], l2[31]]
    st = s.want(W, [str(k) for k in b])  # panned away
    assert s.fake.jobs[j_run]["status"] == "running"  # not killed
    assert s.fake.jobs[j_wait].get("cancelled")  # dropped while it waited
    assert set(st["tiles"]) == {str(k) for k in b}  # a[2], a[3]: gone from the queue
    assert s.fake.started()[-1] == str(b[0])  # the free slot went to the new view's first tile
    s.fake.finish(j_run)  # the running one finishes and is kept
    s.pump()
    assert s.built(W, a[0]) is not None
    assert str(b[1]) in s.fake.started()
    assert str(a[2]) not in s.fake.started() and str(a[3]) not in s.fake.started()


def test_a_level_3_tile_waits_for_every_parent_tile_it_reads(svc):
    s = svc
    # a level-3 tile on the corner of four level-2 tiles reads all four (lod.parent_sources)
    k3 = next(k for k in (L.Key("py.1.1", 3, x, y) for y in range(4, 28, 4) for x in range(4, 28, 4))
              if len(L.parent_sources(k)) == 4)
    srcs = L.parent_sources(k3)
    s.want(W, [str(k3)])
    assert s.fake.started() == ["py.1.1/1/0/0"]
    _finish_all(s)
    assert sorted(s.fake.started()[1:]) == sorted(str(k) for k in srcs[:3])  # (three at once)
    _finish_all(s)
    assert s.fake.started()[4:] == [str(srcs[3])]  # the fourth parent; the child still waits
    assert s.status(W)["tiles"][str(k3)]["state"] == "queued"
    _finish_all(s)
    assert s.fake.started()[-1] == str(k3)
    _finish_all(s)
    assert s.built(W, k3) is not None


def test_a_failed_parent_blocks_its_children(svc):
    s = svc
    k2 = _l2()[20]
    s.want(W, [str(k2)])
    s.fake.finish(s.fake.live()[0], ok=False)
    s.pump()
    st = s.status(W)
    assert st["tiles"]["py.1.1/1/0/0"]["state"] == "failed" and st["tiles"][str(k2)]["state"] == "blocked"
    assert st["queued"] == 0 and st["building"] == 0  # (so the viewer's badge goes out)
    assert s.fake.started() == ["py.1.1/1/0/0"]  # not retried at once


def test_the_ram_guard(svc):
    s = svc
    s.want(W, ["py.1.1/1/0/0"])
    _finish_all(s)
    l2 = _l2()
    spare = api.ZOOM_RAM_SPARE_GB
    # room for two: the second's need counts the first's peak again (on the safe side)
    s.free_ram = lambda: T.PEAK_GB[2] * 2 + spare + 0.1
    st = s.want(W, [str(k) for k in l2[:4]])
    assert len(s.fake.live()) == 2 and "waiting for memory" in st["note"]
    s.free_ram = lambda: T.PEAK_GB[2] + spare - 0.1
    _finish_all(s)
    assert s.fake.live() == []  # nothing starts without the room
    s.free_ram = lambda: 500.0
    s.pump()
    assert len(s.fake.live()) == 2


def test_one_section_at_a_time(svc):
    s = svc
    st = s.want(W, ["py.1.1/1/0/0", "px.1.1/1/0/0"])
    assert s.fake.started() == ["py.1.1/1/0/0"] and st["queued"] == 1
    # the section RAM budget is lane 290's 8.3 GB
    s.free_ram = lambda: T.PEAK_GB[1] + api.ZOOM_RAM_SPARE_GB - 0.1
    _finish_all(s)
    assert s.fake.live() == []
    # not beside another section-sized zoom (someone's POST /api/zoom)
    s.free_ram = lambda: 500.0
    other = s.fake.submit(api.parse_zoom_request({"world": W, "section": "pz.1.1", "res_km": 2}))
    s.pump()
    assert s.fake.live() == [other] and "section-sized" in s.status(W)["note"]
    s.fake.finish(other, ok=False)
    s.pump()
    assert s.fake.started()[-1] == "px.1.1/1/0/0"


def test_the_cache_cap_drops_the_least_recently_used(svc):
    s = svc
    s.want(W, ["py.1.1/1/0/0"])
    _finish_all(s)
    a, b = L.Key("py.1.1", 2, 3, 3), L.Key("py.1.1", 2, 4, 3)  # (inside the cell: their children all exist)
    s.want(W, [str(a), str(b)])
    _finish_all(s)
    kids = L.children(a)[:2]
    s.want(W, [str(k) for k in kids])
    _drain(s)  # (with the neighbours of a they read)
    s.want(W, [])
    ix = s.idx[W]
    t = 1000.0
    for k, used in ((a, t + 1), (kids[0], t + 2), (kids[1], t + 5), (b, t + 3), (L.Key("py.1.1", 1, 0, 0), t)):
        ix[str(k)].update(used=used, bytes=10**9)
    s.cap_gb = 4.3
    # least recently used first: kids[0] (t + 2)
    assert s.evict() == [f"{W}:{kids[0]}"]
    assert not (S.zooms_dir() / L.tile_id(W, kids[0])).exists()
    # a's use is its latest child's (t + 5, later than b's t + 3); at a tie the child goes first; level 1 never
    s.cap_gb = 2.0
    assert s.evict() == [f"{W}:{b}", f"{W}:{kids[1]}", f"{W}:{a}"]  # (down to 95% of the cap)
    assert str(L.Key("py.1.1", 1, 0, 0)) in s.idx[W] and s.cache_bytes() <= 2e9
    # a tile a queued build reads is kept
    s.cap_gb = 60
    s.want(W, [str(a)])
    _finish_all(s)
    k3 = L.children(a)[5]
    s.at_once = 0  # (nothing starts: k3 stays queued, reading a)
    s.want(W, [str(k3)])
    s.idx[W][str(a)]["bytes"] = 10**10
    s.cap_gb = 1.0
    assert f"{W}:{a}" not in s.evict() and s.built(W, a) is not None
    # the index is on disk
    s.flush(force=True)
    on_disk = json.loads((S.root() / ".tiles" / f"{W}.json").read_text())
    assert set(on_disk) == set(s.idx[W])


def test_tile_files(svc):
    s = svc
    k = _l2()[9]
    assert s.get(f"/api/tiles/{W}/{k.cell}/2/{k.tx}/{k.ty}/view.bin", "")[1] == 404  # not built yet
    s.want(W, [str(k)])
    _finish_all(s)
    _finish_all(s)
    d = s.built(W, k)
    assert (d / "view.bin").exists()  # written when the build ended
    body, code, ct = s.get(f"/api/tiles/{W}/{k.cell}/2/{k.tx}/{k.ty}/view.bin", "")
    assert code == 200 and body[:4] == b"PWT1"
    n = struct.unpack("<i", body[4:8])[0]
    elev = np.frombuffer(body[8:8 + 2 * n * n], "<f2").reshape(n, n)
    water = np.frombuffer(body[8 + 2 * n * n:], np.uint8).reshape(n, n)
    ref = np.arange(n * n, dtype=np.float32).reshape(n, n) * 10
    assert np.array_equal(elev, ref.astype(np.float16)) and np.array_equal(water, (ref < 20).astype(np.uint8))
    lay = s.get(f"/api/tiles/{W}/{k.cell}/2/{k.tx}/{k.ty}/layer/elevation.bin", "")[0]
    assert np.array_equal(np.frombuffer(lay, "<f4").reshape(n, n), ref)
    assert s.get(f"/api/tiles/{W}/{k.cell}/2/{k.tx}/{k.ty}/satellite.png", "")[2] == "image/png"
    assert s.get(f"/api/tiles/{W}/{k.cell}/2/{k.tx}/{k.ty}/layer/nope.bin", "")[1] == 404
    assert s.get(f"/api/tiles/{W}/{k.cell}/x/0/0/view.bin", "")[1] == 400
    used = s.idx[W][str(k)]["used"]
    time.sleep(0.01)
    s.get(f"/api/tiles/{W}/{k.cell}/2/{k.tx}/{k.ty}/view.bin", "")
    assert s.idx[W][str(k)]["used"] > used  # (serving counts as use: the cap's order)
    ix = s.get("/api/tiles/index", f"world={W}")[0]
    assert len(ix["cells"]) == 54
    c = next(c for c in ix["cells"] if c["id"] == "py.1.1")
    assert c["built"] == {"1": [[0, 0]], "2": [[k.tx, k.ty]]}


def test_want_route(svc):
    s = svc
    body, code = s.post("/api/tiles/want", json.dumps({"world": W, "gen": 7, "tiles": [["py.1.1", 1, 0, 0]]}).encode())
    assert code == 200 and body["gen"] == 7 and body["building"] == 1
    assert s.post("/api/tiles/want", b"{not json")[1] == 400
    assert s.post("/api/tiles/want", json.dumps({"world": W, "tiles": [["py.1.1", 9, 0, 0]]}).encode())[1] == 400
