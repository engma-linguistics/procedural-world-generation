"""The technology tree, v0 (planet/lineages/techtree.py, PW-675): the data file, acquisition, kits, inheritance, diffusion."""

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
                if tid in ("knapping", "handaxes"):
                    saw_bare_early |= ago > 1500.0
                else:
                    assert ago <= 1500.0, (s, lid, tid, ago)  # (nothing else before the node)
    assert saw_bare_early


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
