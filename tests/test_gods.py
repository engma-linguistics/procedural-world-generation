"""Gods as a lect-like tree (PW-1306) and food taboos (PW-1305): the pure cores, on synthetic cultures."""
import numpy as np
import pytest

from planet.lineages import gods as G
from planet.lineages import taboos as TB

D = {d: i for i, d in enumerate(G.DOMAINS)}
KNOW = {"spirit_ritual", "burial"}


def sal(**kw):
    s = np.zeros(len(G.DOMAINS))
    for k, v in kw.items():
        s[D[k]] = v
    return s


def run(P, frames):
    """frames: [(ago, {culture: (salience, know)})]"""
    for ago, cs in frames:
        P.frame(ago, {c: {"sal": s, "know": k} for c, (s, k) in cs.items()})


def test_domains_are_twenty_in_five_groups():
    assert len(G.DOMAINS) == 20 and len(set(G.DOMAINS)) == 20 and len(G.GROUPS) == 5


def test_salience_follows_the_land():
    coast = G.salience({"coast": 0.4}, KNOW, traits=("coastal",))
    inland = G.salience({"coast": 0.0, "mountain": 0.3}, KNOW)
    assert coast[D["sea"]] > inland[D["sea"]] and inland[D["mountain"]] > coast[D["mountain"]]
    assert G.salience({}, KNOW)[D["smithing"]] == 0 < G.salience({}, KNOW | {"bronze"})[D["smithing"]]
    assert ((coast >= 0) & (coast <= 1)).all()


def test_no_ritual_no_gods_is_the_callers_gate_and_a_founding_culture_gets_three_beings():
    P = G.Pantheons()
    run(P, [(10.0, {0: (sal(sea=0.9, storm=0.8, hunt=0.7, hearth=0.1), KNOW)})])
    assert len(P.by[0]) == G.BEING_MIN
    assert {G.DOMAINS[int(np.argmax(b.w))] for b in P.by[0]} == {"sea", "storm", "hunt"}


def test_an_inland_sea_god_becomes_a_rain_god_slowly():
    P = G.Pantheons()
    coast, dry = sal(sea=0.9, hunt=0.5, hearth=0.4), sal(rain=0.9, sea=0.0, hunt=0.5, hearth=0.4)
    run(P, [(100.0, {0: (coast, KNOW)})])
    god = max(P.by[0], key=lambda b: b.w[D["sea"]])
    assert G.DOMAINS[int(np.argmax(god.w))] == "sea"
    run(P, [(99.0, {0: (dry, KNOW)})])
    assert G.DOMAINS[int(np.argmax(god.w))] == "sea"  # (one kyr is not enough: ritual is conservative)
    run(P, [(100.0 - 40.0 - k, {0: (dry, KNOW)}) for k in range(0, 40, 10)])
    assert G.DOMAINS[int(np.argmax(god.w))] == "rain"
    assert god.status == "living"


def test_a_new_culture_copies_its_parents_beings_and_cousins_drift_apart():
    P = G.Pantheons()
    run(P, [(100.0, {0: (sal(sea=0.9, storm=0.8, hunt=0.7), KNOW)})])
    P.split(1, 0, 99.0)
    assert len(P.by[1]) == len(P.by[0]) and all(b.parent is not None and b.how == "split" for b in P.by[1])
    assert {b.parent for b in P.by[1]} == {b.id for b in P.by[0]}
    ids0 = {b.id for b in P.by[0]}
    assert not ids0 & {b.id for b in P.by[1]}


def test_merging_cultures_fuse_alike_gods_and_carry_the_rest():
    P = G.Pantheons()
    run(P, [(100.0, {0: (sal(sea=0.9, storm=0.8, hunt=0.7), KNOW), 1: (sal(sea=0.9, mountain=0.8, herd=0.7), KNOW)})])
    n0, n1 = len(P.by[0]), len(P.by[1])
    P.merge(1, 0, 90.0)
    assert 1 not in P.by and n0 < len(P.by[0]) <= n0 + n1
    fused = [b for b in P.beings if b.status == "merged"]
    assert fused and all(b.into is not None for b in fused)  # (the two sea gods are one)


def test_faith_made_gods_die_with_their_worshippers_absolute_ones_stay_dormant():
    for mode, status in (("faith_made", "faded"), ("belief_only", "faded"), ("absolute", "dormant")):
        P = G.Pantheons(mode)
        run(P, [(10.0, {0: (sal(sea=0.9, storm=0.8, hunt=0.7), KNOW)})])
        P.died(0, 5.0)
        assert not P.by.get(0) and {b.status for b in P.beings} == {status}


def test_individuation_rises_with_faith_techs_and_only_high_beings_grant_spells():
    s = sal(sea=0.9, storm=0.8, hunt=0.7)
    know = {"spirit_ritual"}
    P = G.Pantheons()
    run(P, [(30.0 - k, {0: (s, know)}) for k in range(0, 10)])
    low = max(b.ind for b in P.by[0])
    assert low < 0.2 and not any(P.grants_spells(b) for b in P.by[0])
    big = know | {"burial", "temples", "kingship", "moralizing_high_god"}
    run(P, [(20.0 - k, {0: (s, big)}) for k in range(0, 15)])
    top = max(P.by[0], key=lambda b: b.ind)
    assert top.high and top.ind > 0.6 and P.grants_spells(top)
    others = [b for b in P.by[0] if b is not top]
    assert all(b.ind <= G.tier(big, False) for b in others)  # (only the leader takes the high god)
    P.mode = "belief_only"
    assert not P.grants_spells(top)


def test_tier_and_modes():
    assert G.tier(set()) == 0 and G.tier({"temples"}) < G.tier({"kingship"}) < G.tier({"moralizing_high_god"})
    assert G.tier({"moralizing_high_god", "kingship"}, high_god=False) == G.tier({"kingship"})
    with pytest.raises(ValueError):
        G.Pantheons("nonsense")


def test_labels_run_from_spirit_to_person_god():
    w = np.zeros(20)
    w[D["sea"]] = 1.0
    assert G.label(w, 0.1).startswith("spirit") and G.label(w, 0.4).startswith("power") and G.label(w, 0.6).startswith("god") \
        and G.label(w, 0.9).startswith("person-god")


# ---- food taboos ----------------------------------------------------------------------------------------------------
def tb(seed=1, **kw):
    a = dict(domestic=["cattle", "caprine"], crops=["wheat"], wild=set(TB.ITEMS), enemies={}, beings=[], purity=0.5)
    a.update(kw)
    return TB.culture_taboos(np.random.default_rng(seed), **a)


def test_purity_rules_scale_with_the_weight_and_never_hit_what_the_culture_keeps():
    n = {p: len([t for t in tb(purity=p) if t["origin"] == "purity"]) for p in (0.0, 0.25, 0.5, 1.0)}
    assert n[0.0] == 0 and n[0.0] <= n[0.25] <= n[0.5] <= n[1.0] == TB.PURITY_MAX
    for t in tb(purity=1.0):
        assert t["target"] not in ("cattle", "caprine") or t["origin"] != "purity"
        if t["origin"] == "purity":
            assert t["straddles"] and t["scope"] == "everyone"


def test_taboos_are_seeded_and_unique_per_target():
    assert tb(seed=3) == tb(seed=3)
    t = tb(seed=3, purity=1.0)
    assert len({x["target"] for x in t}) == len(t)


def test_divine_taboo_follows_the_gods_domain_and_scope_follows_its_individuation():
    big = {"id": 1, "label": "god of herd", "ind": 0.7, "domains": ["herd"]}
    small = {"id": 2, "label": "spirit of the sea", "ind": 0.2, "domains": ["sea"]}
    t = [x for x in tb(beings=[big, small], purity=0.0) if x["origin"] == "divine"]
    by = {x["target"]: x for x in t}
    assert by["cattle"]["scope"] == "everyone" and by["sea_beasts"]["scope"] == "priests"


def test_identity_taboo_is_the_feared_peoples_staple():
    t = tb(enemies={"the elves": [{"id": "rice", "valence": "feared"}]}, purity=0.0)
    assert any(x["origin"] == "identity" and x["target"] == "rice" for x in t)
    t = tb(enemies={"the elves": [{"id": "wheat", "valence": "feared"}]}, purity=0.0)  # (it grows wheat itself)
    assert not any(x["origin"] == "identity" for x in t)


def test_sea_kinds_need_a_coast():
    inland = TB.available({"traits": []}, "steppe")
    coast = TB.available({"traits": ["coastal"]}, "steppe")
    assert "shellfish" not in inland and "shellfish" in coast and "snakes" in inland
