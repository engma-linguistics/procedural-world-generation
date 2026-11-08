"""The cuisine sheet (PW-1391, PW-1312, PW-834, PW-1372): each rule on small hand-made cultures, no run needed."""

from types import SimpleNamespace as NS

import numpy as np

from planet.lineages import cuisine as CZ
from planet.lineages import spec as SP

TECHS = [{"id": t} for t in ("fermentation", "milking", "distilling", "feasting")]
CTX = NS(meta={"techtree": {"techs": TECHS}, "crops": {"stocks": {"wheat": {"label": "wheat and barley"}, "vine": {"label": "grapes and vines"}}},
               "animals": {"stocks": {"cattle": {"label": "cattle"}, "horse": {"label": "horses"}}}})


def _p(name="the Folk", farm=0.0, herd=0.0, know=(), crops=(), herds=(), dairy=None, body=None, taboos=(), fuel="wood", off=False):
    food = [t for t in taboos if t.get("kind", "food") == "food"]
    return {"id": 1, "name": name, "people": "folk", "people_name": "folk", "body": {**SP.BODY_DEFAULT, **(body or {})},
            "ways": {"farm": farm, "herd": herd, "forage": round(1 - farm - herd, 3), "density_km2": 1.0}, "know": set(know),
            "crops": {c: 0.5 for c in crops}, "staple_crops": [c for c in crops if c == "wheat"], "herds": {h: 0.5 for h in herds}, "dairy": dairy,
            "fuel": fuel, "faith": None, "taboos": list(taboos), "food_taboos": food,
            "forbidden": sorted(t["target"] for t in food if t["scope"] == "everyone"), "cells": 10, "traits": {}, "off_ladder": off, "coastal": False}


def test_dairy_needs_herding_milking_and_a_body_that_milks():
    """PW-834: lactase alone never makes dairy (a forager with lactase keeps no dairy herd); PW-793: `milks = false` (Seven Meals' antelope-
    and cervid-kin) never milks; PW-1372: a herding culture's lactase rises with its years of dairying, so fresh milk follows long herding."""
    body = {**SP.BODY_DEFAULT, "milk": 0.9}
    assert CZ.dairy_of(body, 0.02, ["cattle"], 8.0, 0.0, True, True) is None  # (a forager with lactase: no dairy)
    assert CZ.dairy_of({**body, "milks": False}, 0.8, ["cattle"], 8.0, 0.0, True, True) is None
    assert CZ.dairy_of(body, 0.8, ["cattle"], None, 0.0, False, False) is None  # (milking not known)
    assert CZ.dairy_of(body, 0.8, [], 8.0, 0.0, True, True) is None  # (no dairy animal on its land)
    d0 = {**SP.BODY_DEFAULT, "milk": False}
    young, old = CZ.dairy_of(d0, 0.8, ["cattle"], 1.0, 0.0, True, False), CZ.dairy_of(d0, 0.8, ["cattle"], 9.0, 0.0, True, False)
    assert young["lactase_share"] < old["lactase_share"] <= 0.8 and not young["fresh"] and old["fresh"]
    assert CZ.dairy_of(d0, 0.8, ["cattle"], 9.0, 6.0, True, False)["lactase_share"] < old["lactase_share"]  # (at an earlier era, fewer years)
    assert CZ.dairy_of(body, 0.3, ["cattle"], 1.0, 0.0, True, False)["lactase_share"] == 0.9  # (an authored share stands)


def test_drink_milk_only_where_dairy_and_beer_only_with_fermentation():
    brief = {"land": {"koppen": {}}}
    farm = _p(farm=0.8, know=("fermentation",), crops=("wheat", "vine"))
    d = CZ.drink(CTX, brief, farm)["list"]
    assert d[0] == "water" and "barley beer" in d and "wine" in d and not any("milk" in x for x in d)
    nob = CZ.drink(CTX, brief, _p(farm=0.8, crops=("wheat",)))["list"]
    assert "barley beer" not in nob and "no beer or wine yet" in nob[-1]  # (no fermentation known)
    herd = _p(herd=0.7, know=("fermentation", "milking"), herds=("horse",), dairy={"animals": ["horse"], "fresh": False, "lactase_share": 0.1})
    h = CZ.drink(CTX, brief, herd)["text"]
    assert "soured" in h and "horses" in h and "mare" in h
    assert "desert" in CZ.drink(CTX, {"land": {"koppen": {"BWh": 0.7}}}, _p())["text"]


def test_staple_follows_the_ways_and_drops_what_it_will_not_eat():
    """PW-1312: a forbidden food (scope everyone) is not a staple; an obligate carnivore eats no grain whatever the land grows."""
    tab = [{"kind": "food", "target": "cattle", "label": "cattle", "scope": "everyone", "origin": "divine", "why": "the herd god's"}]
    p = _p(farm=0.6, herd=0.3, crops=("wheat",), herds=("horse",), taboos=tab)
    p["herds"].pop("cattle", None)
    s = CZ.staple(CTX, {"fish": {}}, p)["text"]
    assert s.index("wheat") < s.index("horses") and "never cattle" in s
    cat = CZ.staple(CTX, {"fish": {}}, _p(farm=0.6, herd=0.2, crops=("wheat",), herds=("cattle",), body={"diet": "obligate_carnivore"}))["text"]
    assert "wheat" not in cat and "no grain" in cat
    assert "game" in CZ.staple(CTX, {"fish": {}}, _p())["text"]
    assert "herd animals taken" in CZ.staple(CTX, {"fish": {}}, _p(off=True))["text"]  # (a dragon kind: no farms of its own)


def test_who_eats_together_from_the_way_of_life_and_its_taboos():
    ctx = NS(meta={})
    band = CZ.who_eats_together(ctx, {}, _p(), None, 0.0)["text"]
    assert "camp" in band
    herders = CZ.who_eats_together(ctx, {}, _p(herd=0.7, know=("feasting",)), None, 0.0)["lines"]
    assert "one pot" in herders[0] and any("feasts" in x for x in herders)
    kin = [{"kind": "kinship", "target": "clan_exogamy", "label": "x", "scope": "everyone"}, {"kind": "caste", "target": "caste_eat", "label": "y", "scope": "everyone"}]
    farm = CZ.who_eats_together(ctx, {}, _p(farm=0.9, taboos=kin), None, 0.0)["lines"]
    assert "own hearth" in farm[0] and any("two clans" in x for x in farm) and any("lowest rank" in x for x in farm)
    assert "alone" in CZ.who_eats_together(ctx, {}, _p(off=True), None, 0.0)["text"]


def test_outsiders_get_wrong_contrasts_with_the_neighbours():
    tab = [{"kind": "food", "target": "eels", "label": "eels", "scope": "everyone", "origin": "purity", "why": "unclean"}]
    me = _p("the Herders", herd=0.7, herds=("horse",), dairy={"animals": ["horse"], "fresh": False, "lactase_share": 0.2}, taboos=tab, fuel="dung")
    them = _p("the Farmers", farm=0.9, crops=("wheat",), herds=("cattle",))
    o = CZ.outsiders(CTX, 0, 0.0, me, [them])
    assert len(o["lines"]) == CZ.OUTSIDER_LINES and "eels" in o["lines"][0] and "spoiled" in o["lines"][1] and "poor" in o["lines"][2]
    same = CZ.outsiders(CTX, 0, 0.0, _p("A"), [_p("B")])
    assert same["lines"] == [] and "no neighbouring culture" in same["text"]


def test_resolve_follows_merges_and_refuses_an_unborn_culture():
    import pytest
    C = [{"name": "a", "born_kyr": 10.0, "end": "merged", "into": 1, "ended_kyr": 3.0},
         {"name": "b", "born_kyr": 10.0, "end": None, "into": None, "ended_kyr": None},
         {"name": "c", "born_kyr": 1.0, "end": None, "into": None, "ended_kyr": None}]
    ctx = NS(cultures=lambda: {"cultures": C})
    assert CZ.resolve(ctx, 0, 5.0) == 0 and CZ.resolve(ctx, 0, 0.0) == 1
    with pytest.raises(SystemExit):
        CZ.resolve(ctx, 2, 5.0)
    with pytest.raises(SystemExit):
        CZ.resolve(ctx, 9, 0.0)


def test_neighbours_put_the_peoples_of_the_land_before_dragons():
    from planet.grid import shared_grid
    g = shared_grid(2)
    mask = np.zeros(g.n, bool)
    mask[:5] = True
    ring = mask.copy()
    ring[g.nbr_idx[mask[g.nbr_src]]] = True
    other = np.flatnonzero(ring & ~mask)
    cell = np.concatenate([np.arange(5), other, other[:2], np.arange(5)])
    cu = np.concatenate([np.zeros(5, int), np.full(len(other), 2), np.full(2, 1), np.full(5, 3)])  # (3: a dragon kind over all of it)
    C = [{"people": "folk"}, {"people": "folk"}, {"people": "folk"}, {"people": "dragon"}]
    ctx = NS(g=g, _cult_cells={0: (cell, cu)}, cultures=lambda: {"cultures": C},
             meta={"present": {"lines": {"folk": {"ladder": {"farm": 1}}, "dragon": {"ladder": {}}}}})
    assert CZ.neighbours(ctx, 0, 0.0, 0, mask) == [2, 1, 3]


def test_brief_religion_is_the_religion_tab_docs(monkeypatch, tmp_path):
    """PW-1440: the brief and cuisine sheet read the same gods and taboos docs as the Religion tab (authored faiths, saved gods mode), not the
    stored files; a run without cultures gives (None, None)."""
    from planet import server
    from planet.lineages import brief as BR
    monkeypatch.setattr(server, "gods_doc", lambda d, mode=None: {"gods_mode": "belief_only", "faiths": {"list": []}})
    monkeypatch.setattr(server, "taboos_doc", lambda d, mode=None: {"cultures": {"0": {"taboos": [{"label": "pigs"}]}}})
    gd, tb = BR.Ctx.religion(NS(dir=tmp_path, _religion=False))
    assert gd["gods_mode"] == "belief_only" and tb["cultures"]["0"]["taboos"][0]["label"] == "pigs"

    def none(d, mode=None):
        raise SystemExit("no cultures")
    monkeypatch.setattr(server, "gods_doc", none)
    assert BR.Ctx.religion(NS(dir=tmp_path, _religion=False)) == (None, None)
