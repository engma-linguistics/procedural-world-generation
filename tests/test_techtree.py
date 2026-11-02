"""The technology tree, v0 (planet/lineages/techtree.py, PW-675): the data file, acquisition, kits, inheritance, diffusion."""

import math

import numpy as np

from planet.lineages import techtree as TT

T = TT.load()


def line(id, origin="root", at=0.0, parents=(), ended=None, group_of=None, **kw):
    return {"id": id, "origin": origin, "ago_kyr": at, "started_kyr": at, "ended_kyr": ended, "parents": list(parents),
            "group_of": group_of, "overlay": False, "demography": {"insularity": 0.3}, **kw}


def test_file_is_a_tree_with_sources():
    assert len(T["track"]) >= 6
    assert len(T["techs"]) >= 40
    pos = {t: i for i, t in enumerate(T["order"])}
    for t in T["techs"].values():
        assert all(pos[n] < pos[t["id"]] for n in t.get("needs", []))  # (prerequisites first, no cycles)
        assert t.get("source"), t["id"]  # (a citation, "unverified ..." or "fantasy ...": never blank)
        if t.get("mode") == "fantasy":
            assert t["track"] == "arcane" or "fantasy" in t["source"]
    for k in T["kind"]:
        assert all(i in T["techs"] for i in k.get("kit", [])), k["of"]


def test_language_not_everywhere_at_once():
    lines = [line(f"stem{i}", at=3000.0) for i in range(6)]
    tt = TT.build(lines, None, None, seed=3, T=T)
    when = [tt["known"][f"stem{i}"].get("language", [None])[0] for i in range(6)]
    got = [w for w in when if w is not None]
    assert len(set(got)) >= 3  # (each stem at its own time)
    assert all(w <= 500 for w in got)  # (no ordinary people before the earliest date)


def test_language_does_not_pass_by_contact():
    lines = [line("talker", at=3000.0), line("late", at=60.0)]
    for tt_seed in range(4):
        tt = TT.build(lines, {"pairs": [{"a": "talker", "b": "late", "first_contact_kyr": 60.0, "in_contact_now": True,
                                         "series": [[60.0, 3000, 0.0], [0.0, 3000, 0.0]]}]}, None, seed=tt_seed, T=T)
        lang = tt["known"]["late"].get("language")
        assert lang is None or lang[1] == "invented"


def test_elders_come_to_language_first():
    lines = [line("draconic", at=19500.0), line("hominid", at=2000.0)]
    early = 0
    for s in range(6):
        tt = TT.build(lines, None, None, seed=s, T=T)
        d = tt["known"]["draconic"].get("language")
        h = tt["known"]["hominid"].get("language")
        assert h is None or h[0] <= 500
        early += d is not None and d[0] > 500
        assert "knapping" not in tt["known"]["draconic"]  # (no hands)
        assert "innate_magic" in tt["known"]["draconic"]
    assert early >= 4


def test_arrivals_bring_a_kit_and_splits_inherit():
    lines = [line("hominid", at=2000.0), line("dwarf", "split", 500.0, ["hominid"]), line("gnome", "arrival", 50.0)]
    tt = TT.build(lines, None, None, seed=1, T=T)
    g = tt["known"]["gnome"]
    assert g["language"] == [50.0, "kit", None] and g["fey_glamour"][1] == "kit"
    assert all(n in g for t in g for n in T["techs"][t].get("needs", []))  # (a kit carries what it needs)
    for t, v in tt["known"]["hominid"].items():
        if v[0] >= 500:
            assert t in tt["known"]["dwarf"]


def test_tamings_count_and_spread_by_contact_and_era_and_mode_cap():
    lines = [line("human", at=200.0), line("orc", at=200.0)]
    pres = {"crops": {"stocks": {"wheat": {"tamed": [{"line": "human", "ago_kyr": 11.0}]}}}}
    con = {"pairs": [{"a": "human", "b": "orc", "first_contact_kyr": 150.0, "in_contact_now": True,
                      "series": [[150.0, 3000, 0.0], [0.0, 3000, 0.0]]}]}
    tt = TT.build(lines, con, pres, seed=2, T=T)
    assert tt["known"]["human"]["cultivation"][:2] == [11.0, "tamed"]
    hows = {v[1] for v in tt["known"]["orc"].values()}
    assert "contact" in hows
    stone = TT.build(lines, con, pres, era="stone age", mode="real", seed=2, T=T)
    ids = {t["id"] for t in stone["techs"]}
    assert "writing" not in ids and "druidcraft" not in ids and "cultivation" in ids
    assert TT.build(lines, con, pres, seed=2, T=T) == tt  # (seeded)


def test_goods_gate_metals():
    g = {"copper": np.zeros(10), "fertile": np.ones(10)}
    pres = np.zeros((1, 10))
    pres[0] = 1.0
    held = TT.goods_held(T, pres, g, 0)
    assert held == {"fertile"}
    t = T["techs"]["copper"]
    assert not TT._env_ok(t, held) and TT._env_ok(t, None)


def test_sapiens_node_gates_all_but_bare_tools():  # PW-971, PW-978
    lines = [line("stem", at=4000.0, sapient_kyr=1500.0), line("kid", "split", at=1000.0, parents=["stem"])]
    saw_bare_early = False
    for s in range(6):
        tt = TT.build(lines, None, None, seed=s, T=T)
        for lid in ("stem", "kid"):
            for tid, (ago, how, _) in tt["known"][lid].items():
                if T["techs"][tid].get("bare"):
                    saw_bare_early |= ago > 1500.0
                else:
                    assert ago <= 1500.0, (s, lid, tid, ago)  # (nothing else before the node)
    assert saw_bare_early


def test_each_body_plan_has_its_own_bare_tools():  # PW-987 (owner 10-29)
    """Before the node the bird stems use found and hooked tools, not knapped stone; the cats (hands from the node) and the
    dragons (no hands) use none; a handed stem knaps; once modern the birds and cats have hands and may knap."""
    lines = [line("mammalian", at=10000.0), line("avian", at=6000.0, sapient_kyr=2000.0),
             line("feline", "split", at=4000.0, parents=["mammalian"], sapient_kyr=2000.0),
             line("hominid", at=4000.0, sapient_kyr=1600.0), line("draconic", at=19500.0, sapient_kyr=5000.0)]
    pre = {k: set() for k in ("avian", "feline", "hominid", "draconic")}
    knap_after = 0
    for s in range(6):
        tt = TT.build(lines, None, None, seed=s, T=T)
        for lid, node in (("avian", 2000.0), ("feline", 2000.0), ("hominid", 1600.0), ("draconic", 5000.0)):
            pre[lid] |= {tid for tid, v in tt["known"][lid].items() if v[0] > node and v[1] in ("invented", "inherited")}  # (the cats inherit no found tools from the handed root)
        knap_after += "knapping" in tt["known"]["avian"] and "knapping" in tt["known"]["feline"]
    assert pre["avian"] and pre["avian"] <= {"found_tools", "hooked_tools"} and "hooked_tools" in pre["avian"]
    assert not pre["feline"] and not {t for t in pre["draconic"] if T["techs"][t]["track"] == "tools"}  # (the dragons' kit, innate magic, is body)
    assert "knapping" in pre["hominid"] and "hooked_tools" not in pre["hominid"] and "found_tools" in tt["known"]["mammalian"]
    assert knap_after >= 3  # (hands with the node)


def test_language_spreads_by_contact_to_peoples_under_a_node():
    lines = [line("talker", at=3000.0), line("stem", at=1500.0, sapient_kyr=1000.0),
             line("modern", "split", at=900.0, parents=["stem"])]
    talk = {"pairs": [{"a": "talker", "b": "modern", "first_contact_kyr": 800.0, "in_contact_now": True,
                       "series": [[800.0, 3000, 0.0], [0.0, 3000, 0.0]]}]}
    hit = 0
    for s in range(6):
        tt = TT.build(lines, talk, None, seed=s, T=T)
        k = tt["known"]["modern"]
        lang = k.get("language")
        if lang and lang[1] == "contact":
            hit += 1
            assert lang[0] <= 800.0 and "gesture" in k  # (the roots come along)
    assert hit >= 1


def _taker_on_an_inventors_date(tt_known, firsts):
    """The techs whose first is a taker (contact, shared, inherited) although some people invented it on that date."""
    return [tid for tid, v in firsts.items() if v["how"] in ("contact", "shared", "inherited")
            and any(kn.get(tid, [None, ""])[0] == v["ago_kyr"] and kn[tid][1] == "invented" for kn in tt_known.values())]


def test_firsts_tie_credits_the_inventor_not_the_taker():  # PW-1012
    # (run 3097e3: firbolgs took pottery from halflings by contact on the grid step halflings invented it, and came
    # first in the lines, so they were credited as the first)
    known = {"firbolg": {"pottery": [18.782, "contact", "halfling"], "herding": [9.0, "shared", "x"]},
             "halfling": {"pottery": [18.782, "invented", None]},
             "orc": {"pottery": [16.862, "contact", "bugbear"], "herding": [9.0, "tamed", None]},
             "elf": {"knapping": [900.0, "inherited", "stem"]}, "stem": {"knapping": [900.0, "kit", None]}}
    f = TT.firsts_of(known)
    assert f["pottery"] == {"line": "halfling", "ago_kyr": 18.782, "how": "invented"}
    assert f["herding"]["line"] == "orc"  # (a taming beats a share on the same date)
    assert f["knapping"]["line"] == "stem"  # (a kit beats an inheritance)
    assert TT.firsts_of(dict(reversed(list(known.items())))) == f  # (the order of the lines no longer matters)
    assert not _taker_on_an_inventors_date(known, f)


def test_build_firsts_never_a_taker_on_an_inventors_date():  # PW-1012, on whole builds
    lines = [line("a", at=60.0), line("b", at=60.0), line("c", at=60.0)]
    pairs = [{"a": x, "b": y, "first_contact_kyr": 60.0, "in_contact_now": True, "series": [[60.0, 3000, 0.0], [0.0, 3000, 0.0]]}
             for x, y in (("a", "b"), ("b", "c"), ("a", "c"))]
    for s in range(4):
        tt = TT.build(lines, {"pairs": pairs}, None, seed=s, T=T)
        assert not _taker_on_an_inventors_date(tt["known"], tt["firsts"]), s


def test_kind_rules_take_several_ids_and_warn_on_none():  # PW-1041
    """A [[kind]] of may list several ids (Seven Meals' giants stem `giant` is an elder kind, as the D&D tree's
    true_giant); a rule that names no line of the tree warns."""
    import pytest
    gk = next(k for k in T["kind"] if "true_giant" in k["of"])
    assert gk.get("elder") and "giant" in gk["of"]
    lines = [line("giant", at=3000.0), line("hill_giant", origin="split", at=1000.0, parents=["giant"])]
    assert TT._kind(T, lines[1], {l["id"]: l for l in lines}) is gk
    with pytest.warns(UserWarning, match="name no line of this tree: .*draconic") as got:
        TT.build(lines, None, None, seed=1, T=T)
    assert "giant" not in str(got[0].message)  # (a rule with one id present is not reported for its other ids)


# ---- the invention model (PW-675 v1, lane 64) ------------------------------------------------------------------------------

def _pop(n, area_mkm2=1.0, at=60.0):
    """A track at a constant population: [ago, lat, lon, area Mkm2, population] at the start and the present."""
    return [[at, 0.0, 0.0, area_mkm2, n], [0.0, 0.0, 0.0, area_mkm2, n]]


def test_every_tech_has_domains_and_the_culture_table_is_checked():
    for t in T["techs"].values():
        assert TT.domains_of(t) and set(TT.domains_of(t)) <= set(TT.DOMAINS), t["id"]
        assert TT.pool_of(t) in TT.POOLS
    import copy
    import pytest
    bad = copy.deepcopy(T)
    raw = {"defaults": bad["defaults"], "track": bad["track"], "tech": list(bad["techs"].values()), "kind": bad["kind"],
           "culture": {"aggressive": {"warfare": 1.5}}}
    with pytest.raises(ValueError):
        TT.load_raw(raw)


def test_strength_is_henrichs_log_with_a_threshold():
    D = T["defaults"]
    assert TT.strength(D["pool_threshold"], D) == 0.0 and TT.strength(10, D) == 0.0
    assert abs(TT.strength(D["pool_ref"], D) - 1.0) < 1e-9
    a, b, c = (TT.strength(n, D) for n in (1e4, 1e5, 1e6))
    assert abs((c - b) - (b - a)) < 1e-9  # (each tenfold adds the same: ln N)
    assert TT.strength(1e15, D) == D["pool_max"]


def test_specialist_ladder_and_learners():
    D = T["defaults"]
    assert TT.specialist_share(T, set()) == D["specialists_base"]
    assert TT.specialist_share(T, {"cultivation", "villages"}) == 0.02
    assert TT.specialist_share(T, {"cultivation", "villages", "towns", "cities"}) == 0.10
    assert TT.learners_x(25, D) == 1.0 and TT.learners_x(50, D) == 2.0  # (elves)
    assert abs(TT.learners_x(430, D) - 17.2) < 1e-9  # (dragons: 430-yr generations)
    assert TT.learners_x(5000, D) == D["learners_max"] and TT.learners_x(5, D) == D["learners_min"]
    assert TT.density_x(D["dens_ref"], D) == 1.0 and TT.density_x(1e6, D) == D["dens_x_max"]


def test_culture_matches_domains_capped_best_of():
    inv, take = TT.culture_of(T, {"traits": ["aggressive", "nomadic"], "way": "pastoral_nomad"})
    assert inv["war"] == 1.5 and inv["move"] == 1.3 and take["war"] == 2.0  # (the best per domain, not the product)
    assert TT.domain_x(inv, T["techs"]["war_chariot"]) == 1.5 and TT.domain_x(inv, T["techs"]["writing"]) == 1.0
    assert TT.domain_x(inv, T["techs"]["riding"]) == 1.5  # (move and war: the best of its domains)
    assert all(x <= T["defaults"]["culture_cap"] for x in inv.values())


def test_floors_only_for_the_gated_techs_and_anchor_rates():
    assert TT.floor_of(T, "cultivation") is None and TT.floor_of(T, "storage") == 11.5  # (storage came 48 kyr after containers)
    assert TT.floor_of(T, "villages") == 14.3 and TT.floor_of(T, "bow") == 64  # (the Pleistocene: hard)
    assert TT.floor_of(T, "writing") is None and TT.floor_of(T, "copper") is None  # (the Holocene chain: soft)
    assert TT.floor_of(T, "sledges") == 10  # (Earth took 390 kyr after its prerequisites: the tree lacks the real one, so floored)
    assert TT.floor_of(T, "salting") is None  # (PW-1122: its real precondition, brine boiled in pots by villagers, made it soft)
    assert abs(TT.anchor_lag(T, "writing") - 3.3) < 1e-9  # (5.3 kyr after proto-writing at 8.6)
    assert abs(TT.anchor_lag(T, "kilns") - 3.6) < 1e-9  # (from the glacial gate, 11.6, not from villages at 14.5)
    assert T["techs"]["writing"]["needs"] == ["tokens", "towns", "proto_writing"]


def test_anchor_check_meets_earths_lag():
    got = TT.anchor_check(["towns", "copper", "writing"], seeds=31, T=T)
    for tid, (lag, earth, share) in got.items():
        assert 0.6 * earth <= lag <= 1.6 * earth, (tid, lag, earth)
        assert share >= 0.8


def test_small_peoples_rarely_invent_the_specialist_techs():
    """Writing, the specialists' tech: a big town people finds it, a band of a thousand never does on its own (Childe; Henrich's
    threshold), though both can take it up by contact."""
    kit = ["language", "counting", "marks", "tallies", "fire_control", "containers", "cordage", "knapping", "huts", "storage",
           "pottery", "villages", "grinding", "cultivation", "mudbrick", "towns", "tokens"]
    T2 = {**T, "kind": [{"of": ["big", "band"], "kit": kit}]}
    big = band = 0
    for s in range(12):
        # (16 kyr, was 8: lane 70's first-of-anchor_peers rates make one isolated people slower than Earth's first finder)
        lines = [line("big", at=16.0, track=_pop(5e7, 5.0, 16.0)), line("band", at=16.0, track=_pop(1000, 0.1, 16.0))]
        tt = TT.build(lines, None, None, seed=s, T=T2)
        big += "writing" in tt["known"]["big"]
        band += "writing" in tt["known"]["band"]
        assert tt["drivers"]["band"]["strength_specialists"] == 0.0
    assert big >= 8 and band == 0


def test_population_is_read_through_time():
    """The size that counts is the people's at the time (its track), not today's: a people of a hundred until the last kyr
    invents nothing of the specialists' before then."""
    kit = ["language", "counting", "marks", "tallies", "fire_control", "containers", "cordage", "knapping", "huts", "storage",
           "pottery", "villages", "grinding", "cultivation", "mudbrick", "towns", "tokens"]
    T2 = {**T, "kind": [{"of": ["late"], "kit": kit}]}
    track = [[8.0, 0, 0, 0.01, 100], [1.0, 0, 0, 0.01, 100], [0.9, 0, 0, 5.0, 5e7], [0.0, 0, 0, 5.0, 5e7]]
    for s in range(6):
        tt = TT.build([line("late", at=8.0, track=track)], None, None, seed=s, T=T2)
        w = tt["known"]["late"].get("writing")
        assert w is None or w[0] <= 1.0


def test_long_lived_kinds_count_as_more_learners():
    lines = [line("wyrm", at=100.0, generation_yr=430.0, track=_pop(200, 1.0, 100.0)),
             line("folk", at=100.0, track=_pop(200, 1.0, 100.0))]
    tt = TT.build(lines, None, None, seed=1, T=T)
    assert tt["drivers"]["folk"]["strength_all"] == 0.0  # (200 people: under the threshold)
    assert tt["drivers"]["wyrm"]["strength_all"] > 0.3  # (200 dragons hand on their skills 17 times less often)
    assert TT._gen(line("x", "split", 10.0, ["wyrm"]), {l["id"]: l for l in lines}) == 430.0  # (inherited down the tree)


def test_aggressive_peoples_take_up_war_techs_faster():
    con = {"pairs": [{"a": "src", "b": "y", "first_contact_kyr": 3.0, "in_contact_now": True,
                      "series": [[3.0, 400, 0.0], [0.0, 400, 0.0]]}]}
    kit = ["wheel", "pack_animals", "war_chariot", "riding"]
    T2 = {**T, "kind": [{"of": ["src"], "kit": kit}, {"of": ["y"], "kit": ["wheel", "pack_animals", "riding"]}]}
    when = {}
    for traits in ([], ["aggressive"]):
        got = 0
        for s in range(30):
            lines = [line("src", at=3.0, track=_pop(100, 0.1, 3.0)),
                     line("y", at=3.0, traits=traits, track=_pop(100, 0.1, 3.0))]
            tt = TT.build(lines, con, None, seed=s, T=T2)
            got += (tt["known"]["y"].get("war_chariot") or [0, ""])[1] == "contact"
        when[bool(traits)] = got
    assert when[True] > when[False]


def test_catalogue_ingested_with_domains_origins_and_honest_sources():
    """PW-1122: the tech catalogue folded in: ~550 techs, every one with domains and a source; the catalogue rows carry Earth's
    independent origins; a row the hunt did not verify says so."""
    assert len(T["techs"]) >= 500
    cat = [t for t in T["techs"].values() if "earth_origins" in t]
    assert len(cat) >= 450 and all(t["earth_origins"] >= 1 for t in cat)
    assert T["techs"]["copper"]["earth_origins"] == 4 and T["techs"]["writing"]["earth_origins"] == 5
    for t in T["techs"].values():
        assert TT.domains_of(t) and t.get("source")
    assert "unverified" in T["techs"]["sling"]["source"]  # (the hunt looked and could not confirm it)
    assert T["techs"]["copper"]["earliest_kyr"] == 6.95  # (the hunt's verified date for an existing tech)
    # the food chains reach the history's own crops and herds
    assert "crop_vine" in T["techs"]["wine"]["needs"] and "animal_cattle" in T["techs"]["ox_traction"]["needs"]


def test_stock_techs_come_only_from_the_history():
    """PW-1122: crop_<id> and animal_<id> are known from the history's first cultivation or take-up of that stock, never invented
    or passed on by the tree; the generic cultivation still comes with any crop."""
    lines = [line("human", at=200.0), line("orc", at=200.0)]
    pres = {"crops": {"stocks": {"vine": {"tamed": [{"line": "human", "ago_kyr": 8.0}], "took_up_kyr": {"orc": 6.0}},
                                 "rice": {"tamed": []}}}}
    for s in range(3):
        tt = TT.build(lines, None, pres, seed=s, T=T)
        h, o = tt["known"]["human"], tt["known"]["orc"]
        assert h["crop_vine"][:2] == [8.0, "tamed"] and h["cultivation"][0] == 8.0
        assert o["crop_vine"][:2] == [6.0, "tamed"]
        assert "crop_rice" not in h and "crop_rice" not in o  # (rate 0: no people invents a crop the history did not give it)
        assert "wine" not in o or o["wine"][0] <= 6.0  # (wine waits for the vine)


def test_needs_any_one_of_them():
    """PW-1122: riding needs a mount (horse, great elk or riding lizard): one will do, none blocks it."""
    assert "animal_horse" in T["techs"]["riding"]["needs_any"]
    for mount, ok in (([], False), (["animal_horse"], True), (["animal_riding_lizard"], True)):
        got = 0
        for s in range(6):
            T2 = {**T, "kind": [{"of": ["x"], "kit": ["pack_animals"] + mount}]}
            tt = TT.build([line("x", at=6.0, track=_pop(1e7, 1.0, 6.0))], None, None, seed=s, T=T2)
            got += "riding" in tt["known"]["x"]
        assert (got >= 5) if ok else got == 0, (mount, got)
    assert TT._earth_ready(T, "riding") == T["techs"]["animal_horse"]["earliest_kyr"]  # (Earth's: the horse, not a fantasy mount)


def test_contact_is_a_front_at_the_neolithic_speed():
    """Lane 70 (PW-1137): a neighbour takes a tech up at 2 ln 2 v / width per kyr (half its people have it once a front at
    contact_speed_km_yr has gone half its width): a 1 Mkm2 people at ~1.4 a kyr, a 9 Mkm2 one at a third of that."""
    D = T["defaults"]
    assert D["contact_speed_km_yr"] == 1.0  # (the Neolithic wave of advance, 0.6-1.3 km/yr: Pinhasi et al. 2005)
    assert abs(TT.contact_rate(1.0, D) - 2 * math.log(2)) < 1e-9
    assert abs(TT.contact_rate(9.0, D) - 2 * math.log(2) / 3) < 1e-9
    assert TT.contact_rate(1e-6, D) == TT.contact_rate(1e-4, D)  # (at least contact_width_min_km wide)
    assert TT.contact_rate(None, D) == TT.contact_rate(D["anchor_pop"] / D["anchor_dens"] / 1e6, D)
    assert abs(TT.ramp_first(1) - TT.RAMP_MEDIAN) < 0.01 and TT.ramp_first(4) < TT.ramp_first(1) / 2


def test_a_package_travels_together():
    """Lane 70 (PW-1137): a people that gets a tech's prerequisites from a neighbour who has long known the tech takes the tech
    with them (the front has already crossed its country), instead of inventing it itself at the soft anchor's quick rate."""
    have = TT.closure(T, ["copper"])
    kit_y = sorted(have - {"kilns", "copper"})
    T2 = {**T, "kind": [{"of": ["src"], "kit": sorted(have)}, {"of": ["y"], "kit": kit_y}]}
    con = {"pairs": [{"a": "src", "b": "y", "first_contact_kyr": 10.0, "in_contact_now": True,
                      "series": [[10.0, 3000, 0.0], [0.0, 3000, 0.0]]}]}
    took = together = 0
    for s in range(20):
        lines = [line("src", at=10.0, track=_pop(1e7, 1.0, 10.0)), line("y", at=10.0, track=_pop(1e7, 1.0, 10.0))]
        tt = TT.build(lines, con, None, seed=s, T=T2)
        ky = tt["known"]["y"]
        assert "kilns" in ky and "copper" in ky
        took += ky["copper"][1] == "contact"
        together += ky["copper"][1] == "contact" and ky["kilns"][0] - ky["copper"][0] < 0.3
    assert took >= 16 and together >= 12, (took, together)


def test_pleistocene_techs_take_their_band():
    """PW-1138: a floored tech with two or more dated origins (origins_kyr, the catalogue's) has the band's rate: the anchor
    people waits, at the median, the median origin's date less the floor; one dated origin (bread) keeps its track's rate,
    and so does a row whose catalogue origins all postdate the tree's date (cordage: 500 kyr, origins 52 and 40)."""
    assert TT.band_wait(T, "pottery") == 9.0 and "rate" not in T["techs"]["pottery"]  # (20 kyr; origins 20 to 5, median 11)
    assert abs(TT.rate_of(T, "pottery") - 0.091) < 0.002  # (lane 69's hand rate, 0.09, now from the rule)
    assert TT.band_wait(T, "beer") == 4.0 and TT.rate_of(T, "beer") > 5 * T["defaults"]["track_rate"]["food"]
    assert TT.band_wait(T, "bread") is None and TT.rate_of(T, "bread") == T["defaults"]["track_rate"]["fire"]
    assert TT.band_wait(T, "cordage") is None
    assert TT.band_wait(T, "writing") is None  # (a soft tech: its lag after its prerequisites sets it)


def test_faith_nodes_and_gods_mode():
    """PW-1304: the moralizing high god sits on the social track behind temples + kingship; divine magic on the arcane track behind
    temples, and exists only when gods_mode is faith_made or absolute (belief-only worlds keep the faith steps)."""
    mg, dm = T["techs"]["moralizing_high_god"], T["techs"]["divine_magic"]
    assert mg["track"] == "social" and set(mg["needs"]) == {"temples", "kingship"} and "Norenzayan" in mg["source"]
    assert "retracted" in mg["source"]  # (the contested Whitehouse 2019 result is flagged, not leaned on)
    assert dm["track"] == "arcane" and dm["needs"] == ["temples"] and dm["gods"]
    lines = [line("human", at=200.0, track=_pop(100000, 5.0, 200.0))]

    def ids(m, **kw):
        return {t["id"] for t in TT.build(lines, None, None, seed=1, T=T, gods_mode=m, **kw)["techs"]}
    for m in ("faith_made", "absolute"):
        assert {"divine_magic", "moralizing_high_god"} <= ids(m)
    b = ids("belief_only")
    assert "divine_magic" not in b and "moralizing_high_god" in b
    real = ids("faith_made", mode="real")
    assert "divine_magic" not in real and "moralizing_high_god" in real
