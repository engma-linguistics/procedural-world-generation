"""Favourites (planet/favourites.py): the store, the /api/favourites endpoint over real HTTP, and `planet favourites`."""

import http.client
import http.server
import json
import sys
import threading

import pytest

from planet import favourites as F, server, store as S
from test_store import _fake


@pytest.fixture
def api(data_root):
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    def call(method, path, body=None):
        c = http.client.HTTPConnection("127.0.0.1", httpd.server_address[1], timeout=30)
        c.request(method, path, body=json.dumps(body) if body is not None else None,
                  headers={"Content-Type": "application/json"} if body is not None else {})
        r = c.getresponse()
        out = r.status, json.loads(r.read() or b"{}")
        c.close()
        return out

    yield call
    httpd.shutdown()
    httpd.server_close()


def test_store(data_root):
    _fake("run", "r1")
    _fake("world", "w1")
    _fake("world", "w2")
    assert F.listing() == []
    F.set_favourite("world", "w2", True)
    F.set_favourite("world", "w1", True)
    F.set_favourite("world", "w2", True)  # (again: no duplicate, moved to the end)
    F.set_favourite("run", "r1", True)
    assert [(e["kind"], e["id"]) for e in F.listing()] == [("world", "w1"), ("world", "w2"), ("run", "r1")]
    assert [e["id"] for e in F.listing("world")] == ["w1", "w2"] and F.is_favourite("run", "r1")
    F.set_favourite("world", "w1", False)
    assert [e["id"] for e in F.listing("world")] == ["w2"]
    # lives in a subfolder of worlds/: the world listing does not see it
    assert F.path().parent == S.worlds_dir() / "favourites"
    assert sorted(e["id"] for e in S.update_index("world")) == ["w1", "w2"]
    with pytest.raises(KeyError):
        F.set_favourite("world", "nope", True)
    with pytest.raises(ValueError):
        F.set_favourite("planet", "w1", True)
    F.set_favourite("world", "nope", False)  # (unstarring something gone is fine)


def test_deleted_items_drop_out(data_root):
    _fake("world", "w1")
    _fake("world", "w2")
    F.set_favourite("world", "w1", True)
    F.set_favourite("world", "w2", True)
    S.delete("world", "w1")
    assert [e["id"] for e in F.listing()] == ["w2"]
    assert [e["id"] for e in json.loads(F.path().read_text())["favourites"]] == ["w2"]  # (and out of the file)
    F.path().write_text("{not json")  # a half-written or foreign file reads as no favourites
    assert F.listing() == []
    F.set_favourite("world", "w2", True)
    assert [e["id"] for e in F.listing()] == ["w2"]


def test_api(api):
    _fake("world", "w1")
    _fake("run", "r1")
    assert api("GET", "/api/favourites") == (200, {"favourites": []})
    st, d = api("POST", "/api/favourites", {"kind": "world", "id": "w1.json", "starred": True})
    assert st == 200 and [(e["kind"], e["id"]) for e in d["favourites"]] == [("world", "w1")]
    assert api("POST", "/api/favourites", {"kind": "run", "id": "r1"})[0] == 200  # (starred defaults to true)
    assert [e["id"] for e in api("GET", "/api/favourites?kind=world")[1]["favourites"]] == ["w1"]
    assert len(api("GET", "/api/favourites")[1]["favourites"]) == 2
    assert api("GET", "/api/favourites?kind=bogus")[0] == 400
    assert api("POST", "/api/favourites", {"kind": "bogus", "id": "w1"})[0] == 400
    assert api("POST", "/api/favourites", {"kind": "world", "id": "gone"})[0] == 404
    assert api("POST", "/api/favourites", {"kind": "world", "id": "../etc"})[0] == 404
    st, d = api("POST", "/api/favourites", {"kind": "world", "id": "w1", "starred": False})
    assert st == 200 and [e["id"] for e in d["favourites"]] == ["r1"]
    assert api("DELETE", "/runs/r1")[0] == 204  # deleting the item drops its star
    assert api("GET", "/api/favourites")[1] == {"favourites": []}


def test_cli(data_root, capsys, monkeypatch):
    from planet.__main__ import main
    _fake("world", "w1")
    _fake("world", "w2")
    F.set_favourite("world", "w2", True)
    for argv, check in ((["favourites"], lambda o: "world:w2" in o and "world w2" in o),
                        (["favourites", "--ids"], lambda o: o.split() == ["w2"]),
                        (["favourites", "--json", "--kind", "run"], lambda o: json.loads(o) == [])):
        monkeypatch.setattr(sys, "argv", ["planet", *argv])
        main()
        assert check(capsys.readouterr().out), argv
