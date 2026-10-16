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


@pytest.mark.filterwarnings("ignore::RuntimeWarning")  # (a level-3 world's rough water balance)
def test_cell_months(http_root):
    root, get = http_root
    w = W.generate("plates", seed=3, level=3)
    wid = W.save(w, "cells").stem
    L, lat = w["layers"], build_grid(3).lat
    tilt = w["meta"]["params"]["tilt"]
    ref = climate.months(lat, *(np.asarray(L[k], float) for k in ("temperature", "warm_month", "cold_month",
                                                                   "precipitation_jul", "precipitation_jan")),
                         tilt, np.asarray(L["cloud_jul"]) / 100, np.asarray(L["cloud_jan"]) / 100)
    for i in (0, 17, len(lat) - 1):
        status, h, body = get(f"/api/cell?world={wid}.json&i={i}")
        d = json.loads(gzip.decompress(body) if h.get("Content-Encoding") == "gzip" else body)
        assert status == 200 and d["i"] == i and len(d["t"]) == len(d["p"]) == 12
        assert np.allclose(d["t"], ref["t"][:, i], atol=0.006) and np.allclose(d["p"], ref["p"][:, i], atol=0.006)
    assert get(f"/api/cell?world={wid}&i={len(lat)}")[0] == 400
    assert get(f"/api/cell?world={wid}&i=x")[0] == 400
    assert get("/api/cell?world=nope&i=0")[0] == 404
