"""Emergent cultures (planet/lineages/cultures.py, PW-670): demes that adapt or live apart become cultures, inherit, drift, merge."""

import numpy as np
import pytest

from planet.grid import shared_grid
from planet.lineages import cultures as CU

LINES = [{"index": 0, "id": "folk", "name": "folk (from afar)", "color": "#cc5500", "parents": [], "traits": ["seafaring", "hardy"],
          "demography": {"sea_share": 0.9}, "group_of": None},
         {"index": 1, "id": "folk_farmer", "name": "folk farmers", "color": "#aa4400", "parents": ["folk"], "traits": [], "group_of": "folk"}]
BIOMES = ("tropical wet", "savanna", "desert", "steppe", "temperate", "continental", "subarctic", "polar", "high mountain")


def _deme(i, parent, how, born, ended=None, end=None, into=None, adapted=None, cells_now=10):
    return {"id": i, "people": "folk", "parent": parent, "how": how, "born_kyr": born, "ended_kyr": ended, "end": end, "into": into,
            "adapted": adapted, "cells_now": 0 if ended is not None else cells_now, "peak_cells": 10, "place": f"place {i}", "lat": 0.0, "lon": 10.0 * i}


def test_assign_founding_adapted_apart_and_brief_split():
    D = [_deme(0, None, "first", 20.0), _deme(1, None, "first", 20.0),  # (two founding sites, one culture)
         _deme(2, 0, "split_adapted", 10.0, adapted="desert"),  # (took to new country: a culture at once)
         _deme(3, 0, "split_gap", 8.0),  # (apart 8 kyr to the present)
         _deme(4, 0, "split_gap", 6.0, ended=5.5, end="fused", into=0)]  # (apart 0.5 kyr only: stays its parent's)
    C, dc = CU.assign(D)
    assert [c.how for c in C] == ["founding", "adapted", "apart"]
    assert dc.tolist() == [0, 0, 1, 2, 0]
    assert C[1].adapted == "desert" and C[1].parent == 0 and C[2].parent == 0


@pytest.fixture
def apart(monkeypatch):
    """The two sisters never merge side by side (the drift tests follow both to the end)."""
    monkeypatch.setattr(CU, "MERGE_CONTACT_KYR", 100.0)


def _setup():
    g = shared_grid(5)
    lon = g.lon
    west, east = (lon < 0) & (np.abs(g.lat) < 40), (lon >= 0) & (np.abs(g.lat) < 40)
    D = [_deme(0, None, "first", 6.0), _deme(1, 0, "split_gap", 5.0)]
    return g, west, east, D


def _frames(g, west, east, D, known, coast_east, steps=(6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0), biome_east=4, cell_km2=1000.0, coh=None):
    C, dc = CU.assign(D)
    dr = CU.Drift(C, dc, LINES, g.nbr_off, g.nbr_idx, cell_km2, known, BIOMES, coh)
    for a in steps:
        dem = np.full(g.n, CU.NONE, np.uint16)
        dem[west] = 0
        if a <= 5.0:
            dem[east] = 1
        coast = west.copy() if coast_east is None else west | (east & coast_east)
        biome = np.where(west | east, 4, -1)
        biome[east] = biome_east
        dr.frame(a, np.arange(g.n), dem, np.full(g.n, 255, np.uint8), coast, biome)
    CU.finish(C, dc, D)
    return C, dr


def test_an_inland_daughter_loses_the_sea_craft_and_the_coast_keeps_it(apart):
    g, west, east, D = _setup()
    C, _ = _frames(g, west, east, D, {"folk": {"canoes": [50.0, "invented", None]}}, coast_east=np.zeros(g.n, bool))
    assert C[0].sea0 == 0.9 and C[0].sea > 0.85  # (the founders on the coast keep their boats)
    assert C[1].sea0 > 0.85  # (the daughter starts with its parent's craft)...
    assert C[1].sea < CU.LOST  # (...and after 5 kyr inland has lost it: TAU_LOSE 1 kyr)
    doc = CU.document(C, np.array([0, 1]), {"demes": D, "from_kyr": 6.0}, LINES, [], 1000.0)["doc"]
    x = doc["cultures"][1]
    assert x["traits"]["sea_craft"]["verdict"] == "lost" and any("lost the sea craft" in t for t in x["changes"])
    assert x["name"] == "folk of place 1" and doc["cultures"][0]["name"] == "first folk of place 0"
    assert x["traits"]["body"] == ["hardy"] and x["traits"]["cultural"] == ["seafaring"]
    uids = [c["uid"] for c in doc["cultures"]]  # (PW-1283: a stable string id, unique, and the same on a second pass)
    assert len(set(uids)) == len(uids) and all(isinstance(u, str) and u.startswith("folk:") for u in uids)
    assert uids == [c["uid"] for c in CU.document(C, np.array([0, 1]), {"demes": D, "from_kyr": 6.0}, LINES, [], 1000.0)["doc"]["cultures"]]


def test_a_skill_is_gained_only_with_the_technology_for_it(apart):
    g, west, east, D = _setup()
    open_ = dict(coast_east=np.zeros(g.n, bool), biome_east=BIOMES.index("steppe"))
    C, _ = _frames(g, west, east, D, {"folk": {}}, **open_)
    assert C[1].open < 0.01  # (no herds known: no herding lore however open the country)
    C, _ = _frames(g, west, east, D, {"folk": {"herding": [10.0, "invented", None]}}, **open_)
    assert C[1].open > 0.7  # (herds known: it comes, slowly, TAU_GAIN 3 kyr)


def test_sister_cultures_side_by_side_merge_sooner_the_more_cohesive_their_kind():
    g, west, east, D = _setup()
    C, dr = _frames(g, west, east, D, {"folk": {}}, coast_east=None)  # (touching from 5 kyr ago, no states)
    assert [(m["why"], m["ago_kyr"]) for m in dr.merges] == [("contact", 5.0 - CU.MERGE_CONTACT_KYR)] and C[1].into == 0
    C, dr = _frames(g, west, east, D, {"folk": {}}, coast_east=None, steps=(6.0, 5.0, 4.9, 4.8, 4.0), coh={"folk": 0.9})
    assert dr.merges[0]["ago_kyr"] == 4.9  # (cohesion 0.9: after a tenth of MERGE_CONTACT_KYR)


def test_sister_cultures_merge_under_a_state_that_can_hold_both(monkeypatch):
    monkeypatch.setattr(CU, "MERGE_CONTACT_KYR", 100.0)  # (the state rule alone)
    g, west, east, D = _setup()
    C, dr = _frames(g, west, east, D, {"folk": {}}, coast_east=None)
    assert not dr.merges and C[1].end is None  # (no cities: they stay two)
    cities = {"folk": {"cities": [3.0, "invented", None]}}
    C, dr = _frames(g, west, east, D, cities, coast_east=None)  # (6.6 Mkm2 together: more than a city state holds)
    assert (west.sum() + east.sum()) * 1000.0 / 1e6 > dict(CU.REACH_MKM2)["cities"] and not dr.merges
    C, dr = _frames(g, west, east, D, cities, coast_east=None, cell_km2=100.0)  # (0.66 Mkm2: one state can hold both)
    assert len(dr.merges) == 1 and C[1].end == "merged" and C[1].into == 0
    assert dr.merges[0]["ago_kyr"] == 3.0 and dr.merges[0]["why"] == "states"  # (touching MERGE_KYR already: merged once cities came)
    assert C[0].end is None


def test_a_culture_whose_last_deme_fused_merged_into_the_other():
    D = [_deme(0, None, "first", 9.0), _deme(1, 0, "crossing", 8.0, ended=2.0, end="fused", into=0)]
    C, dc = CU.assign(D)
    CU.finish(C, dc, D)
    assert C[1].end == "merged" and C[1].into == 0 and C[1].ended == 2.0


def test_a_kind_that_died_out_and_came_back_is_a_new_culture_and_its_daughter_peoples_descend_from_it():
    """Lane 109: full presence in the frames, so a dragon kind no longer drops out of sight; one that really died out is a new culture."""
    D = [dict(_deme(0, None, "first", 30.0, ended=25.0, end="extinct"), people="red_dragon"),
         dict(_deme(1, None, "from_people", 20.0), people="red_dragon"),
         _deme(2, 1, "from_people", 10.0)]  # (a people born of a dragon population: kobolds, dragonborn)
    C, dc = CU.assign(D)
    assert dc.tolist() == [0, 1, 2] and C[1].people == "red_dragon" and C[2].parent == 1


def test_cohesion_is_inherited_down_the_tree_and_old_runs_read_the_preset():
    tree = {"lineage": [{"id": "draconic"}, {"id": "chromatic", "parents": ["draconic"], "cohesion": 0.9},
                        {"id": "red", "parents": ["chromatic"]}, {"id": "dragonborn", "parents": ["draconic"]}]}
    assert CU.cohesion(tree) == {"draconic": 0.0, "chromatic": 0.9, "red": 0.9, "dragonborn": 0.0}
    import tomllib
    from pathlib import Path
    dnd = tomllib.loads((Path(CU.__file__).parent / "samples" / "dnd.toml").read_text())
    old = {"lineage": [{k: v for k, v in r.items() if k != "cohesion"} for r in dnd["lineage"]]}
    c = CU.cohesion(old, dnd["meta"]["name"])
    assert c["red_dragon"] == c["gold_dragon"] == 0.9 and c["storm_giant"] == 0.5 and c["human"] == 0.0 and c["dragonborn"] == 0.0


def test_time_apart_shortens_with_the_era():
    known = {"folk": {"a": [9.0, "invented", None], "b": [4.0, "invented", None]}}
    eras = CU.eras({"techs": [{"id": "a", "era": "stone age"}, {"id": "b", "era": "bronze age"}], "known": known})
    assert CU.t_apart(eras["folk"], 10.0) == CU.T_APART_KYR["stone age"]
    assert CU.t_apart(eras["folk"], 3.0) == CU.T_APART_KYR["bronze age"] < CU.T_APART_KYR["stone age"]
    D = [_deme(0, None, "first", 20.0), _deme(1, 0, "crossing", 12.0, ended=11.5, end="fused", into=0),  # (0.5 kyr apart, stone age)
         _deme(2, 0, "crossing", 3.0, ended=2.5, end="fused", into=0)]  # (0.5 kyr apart, bronze age: long enough now)
    C, dc = CU.assign(D, eras)
    assert dc.tolist() == [0, 0, 1] and C[1].how == "apart"


def test_cohesion_pulls_a_culture_toward_its_kind(apart):
    g, west, east, D = _setup()
    known = {"folk": {"canoes": [50.0, "invented", None]}}
    C, _ = _frames(g, west, east, D, known, coast_east=np.zeros(g.n, bool))
    C2, _ = _frames(g, west, east, D, known, coast_east=np.zeros(g.n, bool), coh={"folk": 0.9})
    assert C[1].sea < CU.LOST < 0.5 < C2[1].sea  # (inland, it keeps most of its craft when its kind holds together)


def test_fliers_have_no_sea_craft():
    g, west, east, D = _setup()
    lines = [dict(LINES[0], traits=["flies"]), LINES[1]]
    C, dc = CU.assign(D)
    dr = CU.Drift(C, dc, lines, g.nbr_off, g.nbr_idx, 1000.0, {}, BIOMES)
    dem = np.full(g.n, CU.NONE, np.uint16)
    dem[west] = 0
    dr.frame(1.0, np.arange(g.n), dem, np.full(g.n, 255, np.uint8), west, np.where(west, 4, -1))
    assert C[0].sea is None


def test_overlapping_cultures_count_every_cell_they_live_in_and_touch_only_their_own_people():
    """Lane 109: Drift.frame takes (cell, deme) pairs, so two peoples' cultures on the same cells are both counted there, and
    contact (for sister merges) is only between cultures of one people."""
    g, west, east, _ = _setup()
    D = [_deme(0, None, "first", 6.0), dict(_deme(1, None, "first", 6.0), people="hob")]
    lines = [LINES[0], dict(LINES[1], id="hob", index=1)]
    C, dc = CU.assign(D)
    dr = CU.Drift(C, dc, lines, g.nbr_off, g.nbr_idx, 1000.0, {}, BIOMES)
    cells = np.flatnonzero(west)
    cell = np.concatenate([cells, cells])
    deme = np.concatenate([np.zeros(len(cells), np.uint16), np.ones(len(cells), np.uint16)])
    dr.frame(1.0, cell, deme, np.full(g.n, 255, np.uint8), west, np.where(west, 4, -1))
    assert C[0].cells_now == C[1].cells_now == len(cells)
    assert dr._touching(cell.astype(np.int64), deme.astype(np.int64)) == set()  # (two peoples on the same land: no sister contact)
