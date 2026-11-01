"""Emergent cultures (planet/lineages/cultures.py, PW-670): demes that adapt or live apart become cultures, inherit, drift, merge."""

import numpy as np

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


def _setup():
    g = shared_grid(5)
    lon = g.lon
    west, east = (lon < 0) & (np.abs(g.lat) < 40), (lon >= 0) & (np.abs(g.lat) < 40)
    D = [_deme(0, None, "first", 6.0), _deme(1, 0, "split_gap", 5.0)]
    return g, west, east, D


def _frames(g, west, east, D, known, coast_east, steps=(6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0), biome_east=4, cell_km2=1000.0):
    C, dc = CU.assign(D)
    dr = CU.Drift(C, dc, LINES, g.nbr_off, g.nbr_idx, cell_km2, known, BIOMES)
    for a in steps:
        dem = np.full(g.n, CU.NONE, np.uint16)
        dem[west] = 0
        if a <= 5.0:
            dem[east] = 1
        coast = west.copy() if coast_east is None else west | (east & coast_east)
        biome = np.where(west | east, 4, -1)
        biome[east] = biome_east
        dr.frame(a, dem, np.full(g.n, 255, np.uint8), coast, biome)
    CU.finish(C, dc, D)
    return C, dr


def test_an_inland_daughter_loses_the_sea_craft_and_the_coast_keeps_it():
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


def test_a_skill_is_gained_only_with_the_technology_for_it():
    g, west, east, D = _setup()
    open_ = dict(coast_east=np.zeros(g.n, bool), biome_east=BIOMES.index("steppe"))
    C, _ = _frames(g, west, east, D, {"folk": {}}, **open_)
    assert C[1].open < 0.01  # (no herds known: no herding lore however open the country)
    C, _ = _frames(g, west, east, D, {"folk": {"herding": [10.0, "invented", None]}}, **open_)
    assert C[1].open > 0.7  # (herds known: it comes, slowly, TAU_GAIN 3 kyr)


def test_sister_cultures_merge_only_under_a_state_that_can_hold_both():
    g, west, east, D = _setup()
    C, dr = _frames(g, west, east, D, {"folk": {}}, coast_east=None)
    assert not dr.merges and C[1].end is None  # (no cities: they stay two)
    cities = {"folk": {"cities": [3.0, "invented", None]}}
    C, dr = _frames(g, west, east, D, cities, coast_east=None)  # (6.6 Mkm2 together: more than a city state holds)
    assert (west.sum() + east.sum()) * 1000.0 / 1e6 > dict(CU.REACH_MKM2)["cities"] and not dr.merges
    C, dr = _frames(g, west, east, D, cities, coast_east=None, cell_km2=100.0)  # (0.66 Mkm2: one state can hold both)
    assert len(dr.merges) == 1 and C[1].end == "merged" and C[1].into == 0
    assert dr.merges[0]["ago_kyr"] == 3.0 - CU.MERGE_KYR  # (after MERGE_KYR in contact under the reach)
    assert C[0].end is None


def test_a_culture_whose_last_deme_fused_merged_into_the_other():
    D = [_deme(0, None, "first", 9.0), _deme(1, 0, "crossing", 8.0, ended=2.0, end="fused", into=0)]
    C, dc = CU.assign(D)
    CU.finish(C, dc, D)
    assert C[1].end == "merged" and C[1].into == 0 and C[1].ended == 2.0


def test_each_dragon_kind_is_one_culture_and_its_daughter_peoples_descend_from_it():
    lines = [{"id": "red_dragon", "traits": ["flies", "hardy"]}, {"id": "storm_giant", "traits": ["swims"]}, LINES[0]]
    tree = {"lineage": [{"id": "red_dragon", "megafauna": True}, {"id": "storm_giant", "megafauna": True}, {"id": "folk"}]}
    whole = CU.one_culture(tree, lines)
    assert whole == {"red_dragon"}  # (the giants fragment like peoples)
    D = [dict(_deme(0, None, "first", 30.0), people="red_dragon"), dict(_deme(1, 0, "split_gap", 20.0), people="red_dragon"),
         _deme(2, 0, "from_people", 10.0)]  # (a people born of a dragon population: kobolds, dragonborn)
    C, dc = CU.assign(D, whole)
    assert len(C) == 2 and dc.tolist() == [0, 0, 1] and C[0].people == "red_dragon" and C[1].people == "folk" and C[1].parent == 0


def test_fliers_have_no_sea_craft():
    g, west, east, D = _setup()
    lines = [dict(LINES[0], traits=["flies"]), LINES[1]]
    C, dc = CU.assign(D)
    dr = CU.Drift(C, dc, lines, g.nbr_off, g.nbr_idx, 1000.0, {}, BIOMES)
    dem = np.full(g.n, CU.NONE, np.uint16)
    dem[west] = 0
    dr.frame(1.0, dem, np.full(g.n, 255, np.uint8), west, np.where(west, 4, -1))
    assert C[0].sea is None
