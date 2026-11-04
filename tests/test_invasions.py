"""Invasions you schedule (PW-1433): the rows are checked for shape only, war_v0 follows them (light x2, strong certain with no edge
needed, by people with its groups, by culture uid, from a place), every row reads "it happened" or why not, odd rows never crash,
and the POST keeps them in authored.json beside the faiths (a scratch data root only) and keys the polities cache by them alone."""

import json
from types import SimpleNamespace

import numpy as np
import pytest

from planet import server
from planet import store as S
from planet.grid import shared_grid
from planet.lineages import gods as G
from planet.lineages import invasions as IV
from planet.lineages import polities as PO

LINES = [{"id": "ruminant"}, {"id": "antelope_folk", "parents": ["ruminant"]}, {"id": "antelope_steppe", "group_of": "antelope_folk", "parents": ["antelope_folk"]},
         {"id": "human"}, {"id": "orc"}]


def _world(tiers=("state", "state"), people=("antelope_steppe", "human"), uids=("u0", "u1")):
    """Two polities side by side on a level-4 grid: 0 holds cell 0, 1 its ring."""
    g = shared_grid(4)
    off, idx = np.asarray(g.nbr_off, np.int64), np.asarray(g.nbr_idx, np.int64)
    owner = np.full(g.n, -1, np.int64)
    owner[0] = 0
    owner[idx[off[0]:off[1]]] = 1
    seats = [{"key": f"s{i}", "tier": t, "people": p, "uid": u} for i, (t, p, u) in enumerate(zip(tiers, people, uids))]
    return g, owner, seats


def _ctx(g, owner, seats, S_, rows, ago=1.0, eligible=lambda p: True):
    anc = IV.ancestors(LINES)
    hook = IV.hook_rows(IV.clean(rows)[0], SimpleNamespace(g=g), 0.1)
    return {"seats": seats, "strength": list(S_), "eligible": eligible, "borders": lambda: PO.borders(owner, g), "run": "t", "step": 3,
            "ago": ago, "invasions": hook, "inv_log": [IV.new_log() for _ in hook], "ancestors": lambda p: anc.get(p, (p,))}


ROW = {"id": "i1", "who": {"people": "antelope_folk"}, "whom": {"people": "human"}, "from_kyr": 1.0, "to_kyr": 1.0, "strength": "strong"}


def test_clean_checks_shape_only_and_keeps_odd_rows():
    out, notes = IV.clean([ROW, {**ROW, "id": "", "who": "elf", "whom": "elf", "from_kyr": -3, "to_kyr": 2, "place": [10, 200]}], strict=True)
    assert out[0]["who"] == {"people": "antelope_folk"} and out[0]["strength"] == "strong" and not notes
    assert out[1]["who"] == {"people": "elf"} and out[1]["from_kyr"] == 2 and out[1]["to_kyr"] == -3 and out[1]["place"] == [10.0, -160.0]
    for bad in ({**ROW, "who": None}, {**ROW, "from_kyr": "soon"}, {**ROW, "strength": "huge"}, {**ROW, "place": [99, 0]}, {**ROW, "who": 7}, "x"):
        with pytest.raises(ValueError):
            IV.clean([bad], strict=True)
        assert IV.clean([bad], strict=False) == ([], IV.clean([bad], strict=False)[1]) and IV.clean([bad], strict=False)[1]
    assert IV.clean(None) == ([], [])


def test_a_people_row_names_its_groups_and_one_year_is_the_century_around_it():
    g, owner, seats = _world()
    ctx = _ctx(g, owner, seats, (1.0, 1.0), [ROW])  # (equal strength: a strong row needs no edge)
    out = PO.war_v0(owner.copy(), ctx)
    assert ctx["taken"] == [(0, 1, "invasion")] and ctx["taken_row"] == {1: 0} and (out[owner == 1] == 0).all()
    assert ctx["invasions"][0]["from_kyr"] > 1.0 > ctx["invasions"][0]["to_kyr"]
    for ago in (0.9, 1.1):  # (the next step either side is outside it)
        ctx = _ctx(g, owner, seats, (1.0, 1.0), [ROW], ago=ago)
        PO.war_v0(owner.copy(), ctx)
        assert ctx["taken"] == [] and ctx["inv_log"][0]["steps"] == 0


def test_strong_needs_no_edge_light_keeps_the_odds_and_doubles_the_chance(monkeypatch):
    g, owner, seats = _world()
    ctx = _ctx(g, owner, seats, (0.3, 1.0), [ROW])  # (far weaker, strong: still certain)
    PO.war_v0(owner.copy(), ctx)
    assert ctx["taken"] == [(0, 1, "invasion")]
    light = {**ROW, "strength": "light"}
    ctx = _ctx(g, owner, seats, (1.0, 1.0), [light])
    PO.war_v0(owner.copy(), ctx)
    assert ctx["taken"] == [] and ctx["inv_log"][0]["odds"] == 1
    monkeypatch.setattr(PO, "draw", lambda *a: 0.45)  # (between WAR_P and 2 x WAR_P: only the light row's chance takes it)
    for rows, want in (([], []), ([light], [(0, 1, "invasion")])):
        ctx = _ctx(g, owner, seats, (3.0, 1.0), rows)
        PO.war_v0(owner.copy(), ctx)
        assert ctx["taken"] == want
    monkeypatch.setattr(PO, "draw", lambda *a: 0.6)
    ctx = _ctx(g, owner, seats, (3.0, 1.0), [light])
    PO.war_v0(owner.copy(), ctx)
    assert ctx["taken"] == [] and ctx["inv_log"][0]["chance"] == 1 and ctx["inv_log"][0]["p"] == 0.5


def test_an_invasion_outranks_a_stronger_neighbour():
    g, owner, seats = _world(tiers=("state", "state", "state"), people=("antelope_steppe", "human", "orc"), uids=("u0", "u1", "u2"))
    off, idx = np.asarray(g.nbr_off, np.int64), np.asarray(g.nbr_idx, np.int64)
    ring = idx[off[0]:off[1]]
    outer = np.setdiff1d(np.concatenate([idx[off[c]:off[c + 1]] for c in ring]), np.concatenate([ring, [0]]))
    owner[outer] = 2  # (the orcs border the humans too, and are far stronger)
    ctx = _ctx(g, owner, seats, (1.0, 1.0, 50.0), [ROW])
    PO.war_v0(owner.copy(), ctx)
    assert (0, 1, "invasion") in ctx["taken"]


def test_culture_rows_and_places_and_why_not():
    g, owner, seats = _world()
    ctx = _ctx(g, owner, seats, (1.0, 1.0), [{**ROW, "who": {"culture": "u0"}, "whom": {"culture": "u1"}}])
    PO.war_v0(owner.copy(), ctx)
    assert ctx["taken"] == [(0, 1, "invasion")]
    c0 = np.asarray(g.centers, float)[0]
    lat, lon = float(np.degrees(np.arcsin(c0[2]))), float(np.degrees(np.arctan2(c0[1], c0[0])))
    far = {**ROW, "place": [-lat, lon + 180]}
    ctx = _ctx(g, owner, seats, (1.0, 1.0), [{**ROW, "place": [lat, lon]}, far])
    PO.war_v0(owner.copy(), ctx)
    assert ctx["taken"] == [(0, 1, "invasion")] and ctx["taken_row"] == {1: 0}
    assert ctx["inv_log"][1]["state_far"] == 1 and ctx["inv_log"][1]["state"] == 0
    g, owner, seats = _world(tiers=("chiefdom", "state"))
    ctx = _ctx(g, owner, seats, (5.0, 1.0), [ROW])
    PO.war_v0(owner.copy(), ctx)
    lg = ctx["inv_log"][0]
    assert ctx["taken"] == [] and lg["chief"] == 1 and lg["state"] == 0 and lg["state_kyr"] == []
    g, owner, seats = _world()
    ctx = _ctx(g, owner, seats, (1.0, 1.0), [ROW], eligible=lambda p: p != 0)  # (the invaders' state was founded this century)
    PO.war_v0(owner.copy(), ctx)
    assert ctx["taken"] == [] and ctx["inv_log"][0]["state_new"] == 1


def _R():
    C = {"cultures": [{"name": "zero"}, {"name": "one"}]}
    return SimpleNamespace(uids=["u0", "u1"], C=C, lidx={l["id"]: i for i, l in enumerate(LINES)}, lname={"human": "humans", "antelope_folk": "antelope-kin"})


def test_readout_says_what_happened_or_why_and_never_crashes_on_odd_rows():
    rows, _ = IV.clean([ROW, {**ROW, "id": "nobody", "who": "elf"}, {**ROW, "id": "self", "whom": {"people": "antelope_folk"}},
                        {**ROW, "id": "later", "from_kyr": -0.4, "to_kyr": -0.4}, {**ROW, "id": "old", "from_kyr": 40, "to_kyr": 30},
                        {**ROW, "id": "nocult", "who": {"culture": "u9"}}, {**ROW, "id": "nostate"}])
    logs = [IV.new_log() for _ in rows]
    logs[0]["steps"], logs[0]["took"] = 1, [[1.0, 1, 0, 3113.4]]
    logs[6].update(steps=2, chief=2)
    pol = [{"name": "Antelope State"}, {"name": "Chiefdom of humans"}]
    out = {o["id"]: o for o in IV.readout(rows, logs, pol, [12.5, 1.0, 0.0], _R())}
    json.dumps(out)
    assert out["i1"]["happened"] and out["i1"]["took"][0]["winner"] == "Antelope State" and out["i1"]["km2"] == 3113
    assert "no people" in out["nobody"]["why"] and "elf" in out["nobody"]["why"]
    assert "victims" in out["self"]["why"] and "after the present" in out["later"]["why"]
    assert "before the first century" in out["old"]["why"] and "no culture" in out["nocult"]["why"]
    assert "only chiefdoms" in out["nostate"]["why"] and out["nostate"]["states"]["centuries"] == 0


@pytest.fixture
def scratch(tmp_path):
    S.set_root(tmp_path)
    d = tmp_path / "runs" / "abc123"
    d.mkdir(parents=True)
    (d / "run.json").write_text(json.dumps({"status": "done", "meta": {"lineages": [{"id": "human", "name": "Humans"}]}, "frames": []}))
    (d / "cultures.json").write_text(json.dumps({"cultures": [{"id": 0, "uid": "human:founding:1", "name": "first humans", "people": "human"}]}))
    yield d
    S.set_root(None)


def test_post_keeps_invasions_beside_the_faiths_and_keys_only_the_polities(scratch):
    faith = {"id": "a1", "name": "F", "culture": 0, "ago_kyr": 3.0, "gods": [{"name": "Mara", "domains": ["sea"]}]}
    assert server.authored_set(json.dumps({"run": str(scratch), "faiths": [faith]}).encode())[1] == 200
    g0, p0 = server._authored_key(scratch), server._authored_key(scratch, "invasions")
    out, code = server.authored_set(json.dumps({"run": str(scratch), "invasions": [ROW, {**ROW, "id": "i2", "who": "nobody"}]}).encode())
    assert code == 200 and out["invasions"] == 2 and out["saved"] == 1  # (the odd row is saved: its read-out says why)
    saved = json.loads((scratch / "authored.json").read_text())
    assert saved["format"] == G.AUTHORED_FORMAT and len(saved["faiths"]) == 1 and saved["invasions"][1]["who"] == {"people": "nobody"}
    assert server._authored_key(scratch) == g0 and server._authored_key(scratch, "invasions") not in (p0, "")
    assert server.authored_set(json.dumps({"run": str(scratch), "faiths": []}).encode())[1] == 200  # (faiths alone keep the invasions)
    assert len(G.read_authored(scratch)["invasions"]) == 2
    assert server.authored_set(json.dumps({"run": str(scratch), "invasions": [{**ROW, "strength": "huge"}]}).encode())[1] == 400
    assert len(G.read_authored(scratch)["invasions"]) == 2
    got, code = server.authored_get(f"run={scratch}&choices=1")
    assert code == 200 and got["choices"]["peoples"] == [{"id": "human", "name": "Humans"}]
    assert got["choices"]["cultures"][0]["uid"] == "human:founding:1"
