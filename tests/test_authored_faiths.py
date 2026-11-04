"""Faiths you write (PW-1430): authored faiths founded under the faith rules, odd ones read out instead of crashing, the POST that saves
them (a scratch data root only), and the on-disk cache of the derived gods and taboos docs."""

import json

import numpy as np
import pytest

from planet import server
from planet import store as S
from planet.lineages import gods as G

KNOW = {"spirit_ritual", "burial"}
TEMPLE = KNOW | {"temples", "kingship"}


def sal(**kw):
    return np.array([kw.get(d, 0.05) for d in G.DOMAINS], float)


SPEC = {"id": "a1", "name": "The Tide Mother", "gods": [{"name": "Mara", "domains": ["sea", "storm"]}, {"name": "Ost", "domains": ["death"]}], "spreads": True}


def test_an_authored_faith_takes_its_culture_and_its_named_gods_lead():
    P = G.Pantheons()
    s0 = sal(mountain=0.9, sky=0.8, herd=0.7)
    P.frame(100.0, {0: {"sal": s0, "know": KNOW}})
    old = P.faith_of[0]
    spec = dict(SPEC)
    P.frame(99.0, {0: {"sal": s0, "know": KNOW}}, found=[(0, spec)])
    f = spec["faith"]
    F = P.faiths[f]
    assert P.faith_of[0] == f and F.name == "The Tide Mother" and F.how == "authored" and F.core == "sea"
    assert P.faiths[old].end == "no followers left"  # (its only culture took the new faith)
    assert P.lead(0).name == "Mara" and {b.name for b in P.by[0] if b.name} == {"Mara", "Ost"}
    assert len(P.by[0]) >= 5  # (its own gods stay, as after a conversion)
    for k in range(2, 60, 2):  # (it lives under the rules: no crash, the named gods are never fused away)
        P.frame(99.0 - k, {0: {"sal": s0, "know": KNOW}})
    assert P.faith_of[0] == f
    d = G.being_doc(P, P.lead(0))
    assert d["name"] == "Mara" and d["label"].startswith("Mara, ")


def test_a_closed_faith_takes_no_converts_and_an_open_one_spreads():
    for spreads, want in ((False, 0), (True, 1)):
        P = G.Pantheons(seed=1)
        s0, s1 = sal(sea=0.9, storm=0.8, hunt=0.7), sal(mountain=0.9, sky=0.8, herd=0.7)
        spec = dict(SPEC, spreads=spreads)
        for k in range(0, 200, 2):
            P.frame(100.0 - k / 2, {0: {"sal": s0, "know": KNOW}, 1: {"sal": s1, "know": TEMPLE}}, contacts={(0, 1)},
                    found=[(1, spec)] if k == 0 else None)
        assert P.counts["conversions"] == want
        assert (P.faith_of[0] == spec["faith"]) == bool(want)


def test_clean_authored_strict_refuses_and_lenient_skips():
    good = dict(SPEC, culture=0, ago_kyr=12.0)
    out, notes = G.clean_authored([good], 3, {"human"})
    assert out[0]["culture"] == 0 and out[0]["gods"][0]["domains"] == ["sea", "storm"] and not notes
    for bad in ({**good, "name": ""}, {**good, "culture": 9}, {**good, "ago_kyr": "soon"}, {**good, "people": "elf"},
                {**good, "culture": None}, {**good, "gods": [{"name": "X", "domains": ["nope"]}]}, {**good, "place": ["a", 1]}):
        with pytest.raises(ValueError):
            G.clean_authored([bad], 3, {"human"})
    out, notes = G.clean_authored([{**good, "name": ""}, good, "junk", {**good, "id": "a1", "place": [95, 0]}], 3, {"human"}, strict=False)
    assert len(out) == 1 and len(notes) == 3


def _inp():
    """Synthetic replay inputs: culture 0 (people human) lives throughout with ritual; culture 1 (people orc) is born at 50 kyr and
    dies out at 20 kyr; culture 2 (human) never has ritual. Frames every 10 kyr from 100 to 0."""
    C = [{"id": 0, "name": "Zero", "people": "human", "born_kyr": 300.0, "end": None, "ended_kyr": None, "into": None, "parent": None},
         {"id": 1, "name": "One", "people": "orc", "born_kyr": 50.0, "end": "died out", "ended_kyr": 20.0, "into": None, "parent": None},
         {"id": 2, "name": "Two", "people": "human", "born_kyr": 300.0, "end": None, "ended_kyr": None, "into": None, "parent": None}]
    U = np.array([[1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]])  # (cells at 0,0 / 0,90 / the north pole)
    frames = []
    for ago in range(100, -1, -10):
        cur = {0: {"sal": sal(sea=0.9, storm=0.5), "know": KNOW}}
        cell, cul = [0, 2], [0, 2]
        if 20 < ago <= 50:
            cur[1] = {"sal": sal(mountain=0.9), "know": KNOW}
            cell.append(1)
            cul.append(1)
        frames.append({"j": len(frames), "ago": float(ago), "ends": [("died", 1, None, 20.0)] if ago == 20 else [], "first": [],
                       "cur": cur, "contacts": set(), "where": {c: (1, U[c]) for c in cur}, "present": {c: 1 for c in cul},
                       "cell": np.array(cell, np.int32), "cul": np.array(cul, np.int32)})
    return {"C": C, "res": lambda c, a: c, "known": {}, "win": 100.0, "seed": 0, "frames": frames, "after": [], "U": U,
            "lines": {"human": "Humans", "orc": "Orcs"}}


def test_odd_authored_faiths_never_crash_and_say_why():
    g = [{"name": "G", "domains": ["sun"]}]
    A = [{"id": "ok", "name": "Fine", "culture": 0, "ago_kyr": 35.0, "gods": g},
         {"id": "future", "name": "Later", "culture": 0, "ago_kyr": -5.0, "gods": g},
         {"id": "early", "name": "Too soon", "culture": 1, "ago_kyr": 90.0, "gods": g},
         {"id": "dead", "name": "Too late", "culture": 1, "ago_kyr": 10.0, "gods": g},
         {"id": "noritual", "name": "No ritual", "culture": 2, "ago_kyr": 30.0, "gods": g},
         {"id": "far", "name": "Nowhere", "place": [-60.0, -120.0], "ago_kyr": 30.0, "gods": g},
         {"id": "pole", "name": "Pole", "place": [89.0, 0.0], "ago_kyr": 30.0, "gods": g},
         {"id": "ancient", "name": "Old", "people": "human", "ago_kyr": 5000.0, "gods": g},
         {"id": "broken", "name": "", "culture": 0, "ago_kyr": 1.0, "gods": g}]
    d = G.replay(_inp(), "faith_made", A)
    R = {r["id"]: r for r in d["authored"]["faiths"]}
    json.dumps(d)  # (the doc is plain JSON)
    assert R["ok"]["took_hold"] and R["ok"]["founded_kyr"] == 30.0 and d["faiths"]["list"][R["ok"]["faith"]]["authored"] == "ok"
    assert not R["future"]["took_hold"] and "after the present" in R["future"]["why"]
    assert R["early"]["took_hold"] and R["early"]["founded_kyr"] == 50.0 and "did not exist yet" in R["early"]["note"]
    assert not R["dead"]["took_hold"] and "died out" in R["dead"]["why"]
    assert not R["noritual"]["took_hold"] and "spirit ritual" in R["noritual"]["why"]
    assert not R["far"]["took_hold"] and "km" in R["far"]["why"]
    assert not R["pole"]["took_hold"] and "Two" in R["pole"]["why"]  # (the culture at the pole has no gods)
    assert R["ancient"]["took_hold"] and R["ancient"]["founded_kyr"] == 100.0 and "window" in R["ancient"]["note"]
    assert "broken" not in R and d["authored"]["problems"]
    assert d["summary"]["faiths"]["authored"] == 3


@pytest.fixture
def scratch(tmp_path):
    S.set_root(tmp_path)
    d = tmp_path / "runs" / "abc123"
    d.mkdir(parents=True)
    (d / "run.json").write_text(json.dumps({"status": "done", "meta": {"lineages": [{"id": "human", "name": "Humans"}]}, "frames": []}))
    (d / "cultures.json").write_text(json.dumps({"cultures": [{"id": 0}, {"id": 1}]}))
    yield d
    S.set_root(None)


def test_post_saves_authored_json_and_refuses_bad_faiths(scratch):
    body = {"run": str(scratch), "faiths": [dict(SPEC, culture=1, ago_kyr=3.5, year_text="3,500 years ago")], "gods_mode": "absolute"}
    out, code = server.authored_set(json.dumps(body).encode())
    assert code == 200 and out["saved"] == 1
    saved = json.loads((scratch / "authored.json").read_text())
    assert saved["gods_mode"] == "absolute" and saved["faiths"][0]["year_text"] == "3,500 years ago"
    out, code = server.authored_set(json.dumps({"run": str(scratch), "gods_mode": "faith_made"}).encode())  # (the mode alone keeps the faiths)
    assert code == 200 and out["saved"] == 1
    assert server.authored_get(f"run={scratch}")[0]["gods_mode"] == "faith_made"
    for bad in ({**body, "faiths": [dict(SPEC, culture=7, ago_kyr=1)]}, {**body, "gods_mode": "maybe"}, {"faiths": []}):
        assert server.authored_set(json.dumps(bad).encode())[1] == 400
    assert server.authored_set(json.dumps({**body, "run": "no-such-run-xyz"}).encode())[1] == 404
    assert json.loads((scratch / "authored.json").read_text())["gods_mode"] == "faith_made"  # (a refused POST leaves the file)


def test_read_authored_survives_a_broken_file(scratch):
    (scratch / "authored.json").write_text("{not json")
    assert G.read_authored(scratch) == {"format": G.AUTHORED_FORMAT, "gods_mode": None, "faiths": []}


def test_derived_docs_persist_on_disk_keyed_by_the_authored_faiths(scratch):
    calls = []
    make = lambda: calls.append(1) or {"n": len(calls)}  # noqa: E731
    k1 = ("abc123", 1.0, "faith_made", server._authored_key(scratch))
    assert server.disk_cached("gods-faith_made", scratch, k1, make) == {"n": 1}
    assert server.disk_cached("gods-faith_made", scratch, k1, make) == {"n": 1} and len(calls) == 1  # (a restart reads it back)
    assert (S.root() / server.GODS_DIR / "gods-faith_made-abc123.json").exists() and not (scratch / server.GODS_DIR).exists()
    (scratch / "authored.json").write_text(json.dumps({"faiths": [SPEC]}))
    k2 = ("abc123", 1.0, "faith_made", server._authored_key(scratch))
    assert k2 != k1 and server.disk_cached("gods-faith_made", scratch, k2, make) == {"n": 2}
