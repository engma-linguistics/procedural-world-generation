"""The viewer's server (planet/server.py) over real HTTP on a free port: gzipped
data files decode to the same bytes, and /api/cell gives a world cell's twelve
months as climate.months makes them."""

import gzip
import http.client
import http.server
import json
import os
import threading

import numpy as np
import pytest

from planet import climate, server, store as S, world as W
from planet.grid import build_grid


@pytest.fixture
def http_root(data_root):
    """(data root, GET function) with the server running on it."""
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    def get(path, gz=True):
        c = http.client.HTTPConnection("127.0.0.1", httpd.server_address[1], timeout=60)
        c.request("GET", path, headers={"Accept-Encoding": "gzip, deflate"} if gz else {})
        r = c.getresponse()
        out = r.status, dict(r.getheaders()), r.read()
        c.close()
        return out

    get.port = httpd.server_address[1]
    yield data_root, get
    httpd.shutdown()
    httpd.server_close()


def test_gzip_files(http_root):
    root, get = http_root
    d = root / "runs" / "r1" / "layers"
    d.mkdir(parents=True)
    rng = np.random.default_rng(0)
    raw = np.repeat(rng.integers(-3, 3, 400_000, dtype=np.int8), 2).tobytes()  # 800 kB, compresses
    (d / "x.bin").write_bytes(raw)
    (d / "small.bin").write_bytes(raw[:1000])
    for _ in range(2):  # compressed while sent, then from the cache (with a length)
        status, h, body = get("/runs/r1/layers/x.bin")
        assert status == 200 and h["Content-Encoding"] == "gzip" and len(body) < len(raw) // 2
        assert gzip.decompress(body) == raw
    assert "Content-Length" in h
    cached = list((root / server.GZIP_DIR).rglob("*.gz"))
    assert len(cached) == 1
    # not asked for gzip, or a small file: as it is
    status, h, body = get("/runs/r1/layers/x.bin", gz=False)
    assert body == raw and "Content-Encoding" not in h
    status, h, body = get("/runs/r1/layers/small.bin")
    assert body == raw[:1000] and "Content-Encoding" not in h
    # the file rewritten: a new copy, the old one pruned
    raw2 = raw[::-1]
    (d / "x.bin").write_bytes(raw2)
    os.utime(d / "x.bin", ns=(1, 1))
    assert gzip.decompress(get("/runs/r1/layers/x.bin")[2]) == raw2
    assert [p for p in (root / server.GZIP_DIR).rglob("*.gz")] != cached and len(list((root / server.GZIP_DIR).rglob("*.gz"))) == 1
    assert server.accepts_gzip("gzip;q=0.5, br") and not server.accepts_gzip("gzip;q=0") and not server.accepts_gzip("deflate")


def test_data_files_revalidate(http_root):
    """Data files carry an ETag and answer 304 when unchanged; the viewer's files stay no-store (PW-1045)."""
    root, get = http_root
    d = root / "runs" / "r2" / "layers"
    d.mkdir(parents=True)
    raw = np.repeat(np.arange(400_000, dtype=np.int8), 2).tobytes()
    (d / "x.bin").write_bytes(raw)
    (root / "runs" / "r2" / "run.json").write_text('{"a": 1}')

    def cond(path, tag, gz=True):
        c = http.client.HTTPConnection("127.0.0.1", get.port, timeout=60)
        c.request("GET", path, headers={"If-None-Match": tag, **({"Accept-Encoding": "gzip"} if gz else {})})
        r = c.getresponse()
        out = r.status, dict(r.getheaders()), r.read()
        c.close()
        return out

    for path, gz in (("/runs/r2/layers/x.bin", True), ("/runs/r2/layers/x.bin", False), ("/runs/r2/run.json", True)):
        status, h, body = get(path, gz=gz)
        assert status == 200 and h["Cache-Control"] == "no-cache" and h["ETag"].startswith('"')
        tag = h["ETag"]
        status, h2, body2 = cond(path, tag, gz)
        assert status == 304 and body2 == b"" and h2["ETag"] == tag
        assert cond(path, '"stale"', gz)[0] == 200
    # gzipped and plain answers are different bodies: different tags
    assert get("/runs/r2/layers/x.bin")[1]["ETag"] != get("/runs/r2/layers/x.bin", gz=False)[1]["ETag"]
    # the file changed: a new tag, a full answer
    old = get("/runs/r2/run.json")[1]["ETag"]
    (root / "runs" / "r2" / "run.json").write_text('{"a": 22}')
    status, h, body = cond("/runs/r2/run.json", old)
    assert status == 200 and h["ETag"] != old and body == b'{"a": 22}'
    # by date too (Chrome revalidates an HTTP/1.0 server's answers with If-Modified-Since only), gzipped or not
    for gz in (True, False):
        h = get("/runs/r2/layers/x.bin", gz=gz)[1]
        c = http.client.HTTPConnection("127.0.0.1", get.port, timeout=60)
        c.request("GET", "/runs/r2/layers/x.bin", headers={"If-Modified-Since": h["Last-Modified"], **({"Accept-Encoding": "gzip"} if gz else {})})
        r = c.getresponse()
        assert r.status == 304 and r.read() == b""
        c.close()
    # API answers stay no-store
    assert get("/api/planets")[1]["Cache-Control"] == "no-store"


@pytest.mark.filterwarnings("ignore::RuntimeWarning")  # (a level-3 world's rough water balance)
def test_cell_months(http_root):
    root, get = http_root
    w = W.generate("plates", seed=3, level=3)
    wid = W.save(w, "cells").stem
    L, lat = w["layers"], build_grid(3).lat
    tilt = w["meta"]["params"]["tilt"]
    ref = climate.months(lat, *(np.asarray(L[k], float) for k in ("temperature", "warm_month", "cold_month",
                                                                   "precipitation_jul", "precipitation_jan")),
                         tilt, *climate.shade_from_hours(lat, L["sunshine_jul"], L["sunshine_jan"], tilt))
    for i in (0, 17, len(lat) - 1):
        status, h, body = get(f"/api/cell?world={wid}.json&i={i}")
        d = json.loads(gzip.decompress(body) if h.get("Content-Encoding") == "gzip" else body)
        assert status == 200 and d["i"] == i and len(d["t"]) == len(d["p"]) == 12
        assert np.allclose(d["t"], ref["t"][:, i], atol=0.006) and np.allclose(d["p"], ref["p"][:, i], atol=0.006)
    assert get(f"/api/cell?world={wid}&i={len(lat)}")[0] == 400
    assert get(f"/api/cell?world={wid}&i=x")[0] == 400
    assert get("/api/cell?world=nope&i=0")[0] == 404


def test_fine_rules(http_root):
    _, get = http_root
    status, _, body = get("/api/fine-rules?res_km=4")
    out = json.loads(body)
    assert status == 200 and out["max_step"] == 20 and out["sizes"]["default"] == {"size_km": 100.0, "res_km": 0.2}
    assert "sizes" not in json.loads(get("/api/fine-rules")[2])
    assert get("/api/fine-rules?res_km=x")[0] == 400


def test_rename_landmass(http_root):
    """PW-886: POST /api/names saves a landmass's name to worlds/names/<id>.json (the file `planet name` writes), an empty name clears it."""
    from planet import names as NM
    root, get = http_root
    w = W.generate("plates", seed=3, level=3)
    wid = W.save(w, "cells").stem
    n = len(NM.world_landmasses(wid)[2])
    assert n >= 2
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    def post(body):
        c = http.client.HTTPConnection("127.0.0.1", httpd.server_address[1], timeout=60)
        c.request("POST", "/api/names", body=json.dumps(body), headers={"Content-Type": "application/json"})
        r = c.getresponse()
        out = r.status, json.loads(r.read())
        c.close()
        return out

    try:
        gen = NM.landmass_names(w["meta"]["seed"], n)
        st, d = post({"world": wid, "letter": "b", "name": "  Zorb   land "})
        assert st == 200 and d["names"][1]["name"] == "Zorb land" and d["names"][1]["generated"] == gen[1] and d["names"][1]["custom"]
        assert NM.load_overrides(wid) == {"B": "Zorb land"}
        st, h, body = get(f"/api/names?world={wid}", gz=False)
        assert st == 200 and [x["name"] for x in json.loads(body)["names"]] == [gen[0], "Zorb land"] + gen[2:]
        st, d = post({"world": wid, "letter": "B", "name": ""})
        assert st == 200 and d["names"][1]["name"] == gen[1] and not d["names"][1]["custom"]
        assert NM.load_overrides(wid) == {} and not NM.overrides_path(wid).exists()
        assert post({"world": wid, "letter": "Z", "name": "x"})[0] == 400
        assert post({"world": "nope", "letter": "A", "name": "x"})[0] == 404
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_post_refuses_cross_site(data_root):
    """PW-1037: a POST must be JSON, and an Origin, if sent, must be the server's own address;
    so another web page open in the browser can't start jobs (a text/plain POST needs no preflight)."""
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    port = httpd.server_address[1]

    def post(headers):
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=60)
        c.request("POST", "/api/favourites", body=json.dumps({"kind": "world", "id": "gone"}), headers=headers)
        r = c.getresponse()
        out = r.status, json.loads(r.read() or b"{}")
        c.close()
        return out

    try:
        js = {"Content-Type": "application/json"}
        assert post({"Content-Type": "text/plain"})[0] == 403
        assert post({})[0] == 403
        st, d = post({**js, "Origin": "https://evil.example"})
        assert st == 403 and "cross-site" in d["error"]
        assert post({**js, "Origin": f"http://127.0.0.1:{port + 1}"})[0] == 403
        # the viewer's own requests (and scripts, which send no Origin) go through: 404 is favourites' "no such world"
        assert post({**js, "Origin": f"http://127.0.0.1:{port}"})[0] == 404
        assert post({"Content-Type": "application/json; charset=utf-8", "Origin": f"http://localhost:{port}"})[0] == 404
        assert post(js)[0] == 404
    finally:
        httpd.shutdown()
        httpd.server_close()


def _presence_run(root, dtype, nlines=3, nframes=4):
    """A fake peoples run with a presence table (output.write_presence's layout) and demes_all: returns the run id and per-frame truth."""
    from planet.lineages import output as LO
    rid = "abc123"
    d = root / "runs" / rid
    (d / "layers").mkdir(parents=True)
    rng = np.random.default_rng(5)
    n_cells = 70000 if dtype == "<u4" else 900
    frames, truth = [], []
    for f in range(nframes):
        pl, pc, ps = [], [], []
        for k in range(nlines):
            c = np.sort(rng.choice(n_cells, int(rng.integers(0, 40)), replace=False))
            pl += [k] * len(c)
            pc += list(c)
            ps += [50] * len(c)
        frames.append({"presence": (np.array(pl), np.array(pc), np.array(ps, np.uint8))})
        truth.append((np.array(pl), np.array(pc)))
    pm = LO.write_presence(d, frames, nlines, n_cells)
    assert pm["dtypes"]["cells"] == dtype
    dem = np.arange(pm["entries"], dtype="<u2")
    (d / "layers" / "demes_all.bin").write_bytes(dem.tobytes())
    (d / "run.json").write_text(json.dumps({"meta": {"presence": pm, "demes": {"all": {"file": "layers/demes_all.bin"}}}}))
    return rid, truth, pm


@pytest.mark.parametrize("dtype", ["<u2", "<u4"])
def test_presence_frame_slice(http_root, dtype):
    """/api/presence sends one frame's offsets, cells and demes_all, equal to that frame's slice of the whole table (PW-1269)."""
    root, get = http_root
    rid, truth, pm = _presence_run(root, dtype)
    whole = np.fromfile(root / "runs" / rid / "layers/presence_cells.bin", dtype=dtype)
    offs = np.fromfile(root / "runs" / rid / "layers/presence_offsets.bin", dtype="<u4").reshape(pm["frames"], -1)
    L = pm["lines"] + 1
    cs = np.dtype(dtype).itemsize
    for f in range(pm["frames"]):
        status, h, body = get(f"/api/presence?run={rid}&frame={f}", gz=False)
        assert status == 200 and h["Content-Type"] == "application/octet-stream"
        o = np.frombuffer(body[:4 * L], "<u4")
        n = int(o[-1])
        a = int(offs[f, 0])
        assert (o == offs[f] - a).all() and n == len(truth[f][1])
        assert len(body) == 4 * L + n * (cs + 2)
        cells = np.frombuffer(body[4 * L:4 * L + n * cs], dtype)
        dem = np.frombuffer(body[4 * L + n * cs:], "<u2")
        assert (cells == truth[f][1]).all() and (cells == whole[a:a + n]).all()
        assert (dem == np.arange(a, a + n)).all()
        for k in range(pm["lines"]):  # (line k's cells within the slice)
            assert (cells[o[k]:o[k + 1]] == truth[f][1][truth[f][0] == k]).all()
    status, h, body = get(f"/api/presence?run={rid}&frame=1")  # (gzipped when the browser accepts it)
    raw = get(f"/api/presence?run={rid}&frame=1", gz=False)[2]
    assert status == 200 and h.get("Content-Encoding") == "gzip" and gzip.decompress(body) == raw
    assert get(f"/api/presence?run={rid}&frame={pm['frames']}")[0] == 400
    assert get(f"/api/presence?run={rid}&frame=x")[0] == 400
    assert get("/api/presence?frame=0")[0] == 400
    assert get("/api/presence?run=nope&frame=0")[0] == 404
