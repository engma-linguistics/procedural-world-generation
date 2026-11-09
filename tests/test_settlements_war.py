"""PW-1108: sacked, razed, walled and raided places in the settlement ledger (planet/lineages/settlements.py, _War), on the small
synthetic peoples run of test_settlements."""

import json

import numpy as np

from planet.grid import shared_grid
from planet.lineages import settlements as ST
from tests.test_settlements import LEVEL, _flat, _run

F = 13


def _taken(tmp_path, keep_share=0.0, traits=("aggressive", "martial"), tech_a=None, tree_meta=None):
    """Cells 0..n/2 pass from people a to people c (the orcs) six kyr ago; a keeps `keep_share` % of the heads there as the second people."""
    g = shared_grid(LEVEL)
    lead = np.zeros((F, g.n), np.uint8)
    lead[6:, : g.n // 2] = 2
    second = np.full((F, g.n), 255, np.uint8)
    if keep_share:
        second[6:, : g.n // 2] = 0
    lines = [{"index": 0, "id": "a", "group_of": None}, {"index": 1, "id": "b", "group_of": None},
             {"index": 2, "id": "c", "name": "orcs", "group_of": None, "traits": list(traits)}]
    tech = {"a": {"villages": [11.0, "x"], "towns": [10.0, "x"], **(tech_a or {})}, "b": {}, "c": {"villages": [11.0, "x"], "towns": [10.0, "x"]}}
    out, _ = _run(tmp_path, _flat(g, F, 40), _flat(g, F, 1.0), _flat(g, F, 200), lead=lead, lines=lines, tech=tech,
                  second=second, second_share=keep_share)
    if tree_meta is not None:
        r = json.loads((out / "run.json").read_text())
        r["meta"]["tree"] = {"meta": tree_meta, "lineage": []}
        (out / "run.json").write_text(json.dumps(r))
    return out, g


def _first(sites, g):
    return [s for s in sites if s["kind"] == "chief" and s["ruin_of"] is None and s["cell"] < g.n // 2]


def test_a_place_taken_by_force_is_razed_by_a_martial_winner(tmp_path):
    out, g = _taken(tmp_path)
    d = ST.derive(out, RIVER_SHIFT=0.0, SACK=1.0, RAZE=1.0)
    hit = _first(d["doc"]["sites"], g)
    assert hit and all(s["why"] == "razed by the orcs" and s["war"][0][1:3] == ["razed", "c"] for s in hit)
    assert all(s["tier_now"] == "ruin" for s in hit)
    assert d["summary"]["why"]["razed"] == len(hit) and d["summary"]["war"]["razed"] >= len(hit)
    assert any(s["ruin_of"] is not None and s["holder"] == "c" for s in d["doc"]["sites"])  # (the cell is settled again on the ruins)


def test_a_sack_shrinks_the_place_and_it_stays(tmp_path):
    out, g = _taken(tmp_path)
    base = {s["cell"]: s for s in _first(ST.derive(out, RIVER_SHIFT=0.0, SACK=0.0)["doc"]["sites"], g)}
    hit = _first(ST.derive(out, RIVER_SHIFT=0.0, SACK=1.0, RAZE=0.0, SACK_LOSS=0.5)["doc"]["sites"], g)
    assert hit and all(s["war"][0][1] == "sacked" and s["abandoned_kyr"] is None for s in hit)
    for s in hit:  # (the series' point at the sack is under the same place's without war)
        a = s["war"][0][0]
        assert ST.pop_at(s, a) < ST.pop_at(base[s["cell"]], a)
    assert all(s["war"] and s["war"][0][1] == "taken" for s in base.values())  # (SACK 0: occupied only, still taken by force)


def test_a_people_that_stays_on_was_not_conquered(tmp_path):
    out, g = _taken(tmp_path, keep_share=40.0)  # (a keeps 40% of the heads: mixing, not a taking by force)
    hit = _first(ST.derive(out, RIVER_SHIFT=0.0, SACK=1.0, RAZE=1.0)["doc"]["sites"], g)
    assert hit and not any(s["war"] for s in hit)


def test_walls_and_the_war_dial_lower_the_chance(tmp_path):
    out, g = _taken(tmp_path, tech_a={"fortifications": [9.0, "x"]})
    m = json.loads((out / "run.json").read_text())["meta"]
    wr = ST._War(out, m, m["lineages"], {0: "a", 1: "b", 2: "c"}, g, {**ST.CONST, "SACK": 0.8, "RAZE": 0.0}, list(range(F)))
    assert wr.walled("a", 2, 5.0) and not wr.walled("a", 1, 5.0) and not wr.walled("a", 2, 9.5)  # (towns only, from its fortifications)
    assert wr.fate(0.7, "c", walls=False) == "sacked" and wr.fate(0.7, "c", walls=True) == "taken"  # (orcs, aggression 0.7: 0.8 x 1.4 -> 1, 0.56 behind walls)
    calm = ST.derive(_taken(tmp_path / "calm", tree_meta={"war": 0.0})[0], RIVER_SHIFT=0.0, SACK=1.0, RAZE=1.0)
    assert calm["summary"]["war"]["sacked"] == calm["summary"]["war"]["razed"] == 0  # (meta.war x0: no war)


def test_dragons_raid_towns_in_their_country_but_not_their_kin(tmp_path, monkeypatch):
    from planet.lineages import output as LO
    g = shared_grid(LEVEL)
    lead = np.zeros((F, g.n), np.uint8)
    lead[:, g.n // 2:] = 2  # (the kobolds, dragon kin, hold the other half)
    lines = [{"index": 0, "id": "a", "group_of": None},
             {"index": 1, "id": "red_dragon", "name": "red dragons (chromatic)", "group_of": None, "traits": ["flies", "insular"], "parents": ["draconic"]},
             {"index": 2, "id": "kobold", "group_of": None, "parents": ["draconic"]}, {"index": 3, "id": "draconic", "group_of": None}]
    tech = {k: {"villages": [11.0, "x"], "towns": [10.0, "x"]} for k in ("a", "kobold")}
    out, _ = _run(tmp_path, _flat(g, F, 40), _flat(g, F, 1.0), _flat(g, F, 200), lead=lead, lines=lines, tech=tech)
    r = json.loads((out / "run.json").read_text())
    r["meta"]["tree"] = {"meta": {"war": 1.0}, "lineage": [{"id": "draconic", "megafauna": True},
                                                         {"id": "red_dragon", "megafauna": True, "parents": ["draconic"]},
                                                         {"id": "kobold", "parents": ["draconic"]}]}
    r["meta"]["presence"] = {"stub": True}
    (out / "run.json").write_text(json.dumps(r))
    off = np.zeros((F, len(lines) + 1), np.uint32)  # (the red dragons, line 1, everywhere at full presence in every frame)
    off[:, 2:] = g.n
    tab = {"offsets": off, "cells": np.arange(g.n, dtype=np.uint32), "share": np.full(g.n, 100, np.uint8)}
    monkeypatch.setattr(LO, "read_presence", lambda d, m: tab)
    sites = ST.derive(out, RIVER_SHIFT=0.0, RAID=1.0)["doc"]["sites"]
    raided = [s for s in sites if any(w[1] == "raided" for w in s["war"])]
    assert raided and all(w[2] == "red_dragon" for s in raided for w in s["war"])
    assert all(s["holder"] == "a" for s in raided)  # (the kobolds, of the dragons' own stem, are never raided)
    assert all(s["tier_peak"] in ("town", "city") for s in raided)  # (towns and cities, not villages)
