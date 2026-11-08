"""The gods mode chosen where a peoples run is made (PW-1309): a tree meta field, a request field, validated at once."""

import pytest

from planet import api, make
from planet.lineages import spec as SP
from planet.lineages import techtree as TT


def _tree(**meta):
    return SP.parse({"meta": {"name": "t", "seed": 1, **meta}, "lineage": [{"id": "human", "name": "Humans", "origin": "root", "at": "300 kyr"}]})


def test_tree_meta_carries_the_gods_mode_and_refuses_others():
    assert _tree().gods_mode == "faith_made"
    t = _tree(gods_mode="belief_only")
    assert t.gods_mode == "belief_only" and SP.to_raw(t)["meta"]["gods_mode"] == "belief_only"
    assert SP.parse(SP.to_raw(t)).gods_mode == "belief_only"
    with pytest.raises(ValueError, match="gods_mode"):
        _tree(gods_mode="maybe")
    assert tuple(SP.GODS_MODES) == tuple(TT.GODS_MODES)


def test_requests_validate_the_gods_mode():
    assert api._gods_mode({}) == {} and api._gods_mode({"gods_mode": ""}) == {}
    assert api._gods_mode({"gods_mode": "absolute"}) == {"gods_mode": "absolute"}
    with pytest.raises(api.BadRequest):
        api._gods_mode({"gods_mode": "maybe"})
    opt = make.options()
    assert [m for m, _ in opt["gods_modes"]] == list(SP.GODS_MODES)


def test_belief_only_drops_divine_magic_from_the_built_tree():
    T = TT.load()
    divine = [i for i, t in T["techs"].items() if t.get("gods")]
    assert divine, "the tech table has divine-magic techs"
    lines = [{"id": "human", "origin": "native", "started_kyr": 300.0, "ended_kyr": None, "traits": [], "demography": {}}]
    for mode, kept in (("belief_only", False), ("faith_made", True)):
        tt = TT.build(lines, None, {}, None, None, "fantasy", "renaissance", 1, gods_mode=mode)
        assert tt["gods_mode"] == mode
        assert any(t["id"] in divine for t in tt["techs"]) is kept
