"""Settlements v0 (planet/lineages/settlements.py, PW-1011): the ledger's lifecycle on a small synthetic peoples run."""

import json

import numpy as np

from planet import store as S
from planet.grid import shared_grid
from planet.lineages import landuse as LU
from planet.lineages import output as O
from planet.lineages import settlements as ST

LEVEL = 3


def _run(tmp_path, dens, farm, elev, rain=None, lead=None, tech=None, overlay=None, lines=None, second=None, second_share=0.0):
    """A peoples run directory with only what settlements.derive reads. dens, farm, elev: (frames, cells), the frames from
    12 kyr ago to the present every 1 kyr; lead: the people with most heads (index; 255 none)."""
    g = shared_grid(LEVEL)
    F, n = dens.shape
    ago = np.linspace(12, 0, F)
    lead = np.zeros((F, n), np.uint8) if lead is None else lead
    second = np.full((F, n), 255, np.uint8) if second is None else second
    lead_share = np.where(lead < 255, np.where(second < 255, 100 - second_share, 100), 0)
    arrays = {"elevation": elev, "ice": np.zeros((F, n)), "precipitation": np.full((F, n), 800.0) if rain is None else rain,
              "mix_lead": lead, "mix_lead_share": lead_share, "mix_second": second,
              "mix_second_share": np.where(second < 255, second_share, 0.0) * np.ones((F, n)), "mix_other_share": np.zeros((F, n)),
              "peoples_overlay": np.full((F, n), 255) if overlay is None else overlay}
    specs = {**O.TERRAIN, **O.PEOPLE_LAYERS}
    enc = {k: (np.stack([S.encode(v[j], specs[k]) for j in range(F)]) if k in O.TERRAIN else v) for k, v in arrays.items()}
    out = tmp_path / "run"
    layers = S.write_layers(out, enc, specs)
    q = {"dens": np.clip(np.rint(np.log2(1 + dens) / LU.PEOPLE_SCALE), 0, 255).astype(np.uint8), "farm": np.rint(100 * farm).astype(np.uint8)}
    eraq = {"frames": list(range(F)), "ago_kyr": [float(a) for a in ago], "keys": ["dens", "farm"], "layers": {}}
    for k, v in q.items():
        (out / "layers" / f"eraq_{k}.bin").write_bytes(v.tobytes())
        eraq["layers"][k] = {"file": f"layers/eraq_{k}.bin", "dtype": "uint8", "shape": [F, n]}
    lines = lines or [{"index": 0, "id": "a", "group_of": None, "cities": False}]
    tech = tech or {"a": {"villages": [11.0, "invented"], "towns": [6.0, "invented"]}}
    run = {"layers": layers, "frames": [{"t": -float(a)} for a in ago],
           "meta": {"level": LEVEL, "cells": g.n, "world": None, "lineages": lines, "techtree": {"known": tech}, "eraq": eraq,
                    "try_seed": 1, "present": {"landmasses": []}}}
    (out / "run.json").write_text(json.dumps(run))
    return out, g


def _flat(g, F, v):
    return np.full((F, g.n), float(v))


def test_sites_wait_for_the_technology_and_stay_under_its_tier(tmp_path):
    g = shared_grid(LEVEL)
    F = 13
    out, _ = _run(tmp_path, _flat(g, F, 40), _flat(g, F, 1.0), _flat(g, F, 200))
    d = ST.derive(out)
    sites = d["doc"]["sites"]
    assert sites, "a dense farming people with the 'villages' tech founds sites"
    assert min(s["founded_kyr"] for s in sites) <= 11.0 + 1e-9  # (not before its villages)
    assert max(s["founded_kyr"] for s in sites) <= 11.0 + 1e-9
    assert d["summary"]["now"]["city"] == 0  # (no 'cities' tech: towns at most)
    assert d["summary"]["now"]["town"] > 0
    assert all(s["pop_now"] < ST.CONST["CITY_MIN"] for s in sites)
    towns = [s for s in sites if s["tier_now"] == "town"]
    for a in towns:  # (central places: no two towns side by side)
        nb = set(g.nbr_idx[g.nbr_off[a["cell"]]:g.nbr_off[a["cell"] + 1]].tolist())
        assert not any(b["cell"] in nb for b in towns)


def test_a_people_without_villages_builds_nothing(tmp_path):
    g = shared_grid(LEVEL)
    out, _ = _run(tmp_path, _flat(g, 13, 40), _flat(g, 13, 1.0), _flat(g, 13, 200), tech={"a": {}})
    assert ST.derive(out)["summary"]["founded"] == 0


def test_sea_drought_and_leaving_make_ruins_and_a_ruin_is_resettled(tmp_path):
    g = shared_grid(LEVEL)
    F = 13
    dens, farm, elev, rain = _flat(g, F, 40), _flat(g, F, 1.0), _flat(g, F, 200), _flat(g, F, 800)
    c_sea, c_dry, c_left = 0, 1, 2
    elev[7:, c_sea] = -50  # (the sea over it 5 kyr ago)
    dens[6:, c_dry] = 0.0  # (rain fails and its people go 6 kyr ago)
    rain[6:, c_dry] = 300
    dens[5:8, c_left] = 0.0  # (its people leave 7-5 kyr ago and come back)
    out, _ = _run(tmp_path, dens, farm, elev, rain)
    sites = ST.derive(out, RIVER_SHIFT=0.0)["doc"]["sites"]
    at = {}
    for s in sites:
        at.setdefault(s["cell"], []).append(s)
    assert at[c_sea][0]["why"] == "the sea rose over it" and len(at[c_sea]) == 1
    assert at[c_dry][0]["why"] == "drought"
    first, second = at[c_left][0], at[c_left][1]
    assert first["why"] == "its people left" and first["resettled_as"] == second["id"] and second["ruin_of"] == first["id"]
    assert second["abandoned_kyr"] is None


def test_a_change_of_hands_is_recorded_and_a_people_without_villages_drives_out(tmp_path):
    g = shared_grid(LEVEL)
    F = 13
    lead = np.zeros((F, g.n), np.uint8)
    lead[6:, 0] = 1  # (people b takes cell 0 six kyr ago; b keeps no sites)
    lead[6:, 1] = 2  # (people c takes cell 1 and keeps it as a town)
    lines = [{"index": 0, "id": "a", "group_of": None}, {"index": 1, "id": "b", "name": "bees (from the hive)", "group_of": None}, {"index": 2, "id": "c", "group_of": None}]
    tech = {"a": {"villages": [11.0, "x"], "towns": [6.0, "x"]}, "b": {}, "c": {"villages": [11.0, "x"]}}
    out, _ = _run(tmp_path, _flat(g, F, 40), _flat(g, F, 1.0), _flat(g, F, 200), lead=lead, lines=lines, tech=tech)
    sites = {s["cell"]: s for s in ST.derive(out, RIVER_SHIFT=0.0)["doc"]["sites"] if s["ruin_of"] is None}
    assert sites[0]["why"] == "driven out by the bees"  # (the plural name, without its note: PW-1106)
    assert sites[1]["abandoned_kyr"] is None and sites[1]["holder"] == "c" and [h for _, h in sites[1]["holders"]] == ["a", "c"]


def test_city_minorities_are_quarters_of_towns(tmp_path):
    g = shared_grid(LEVEL)
    F = 13
    overlay = np.full((F, g.n), 1, np.uint8)  # (the city group is everywhere)
    lines = [{"index": 0, "id": "a", "group_of": None}, {"index": 1, "id": "city_k", "group_of": "k", "cities": True}]
    out, _ = _run(tmp_path, _flat(g, F, 40), _flat(g, F, 1.0), _flat(g, F, 200), overlay=overlay, lines=lines)
    sites = ST.derive(out)["doc"]["sites"]
    assert any(s["quarters"] and s["quarters"][0]["group"] == "city_k" for s in sites if s["tier_now"] == "town")
    assert not any(s["quarters"] for s in sites if s["tier_now"] == "village")


def test_write_adds_the_ledger_and_meta(tmp_path):
    g = shared_grid(LEVEL)
    out, _ = _run(tmp_path, _flat(g, 13, 40), _flat(g, 13, 1.0), _flat(g, 13, 200))
    sm = ST.write(out, report=False)
    assert (out / "settlements.json").exists()
    assert json.loads((out / "run.json").read_text())["meta"]["settlements"]["founded"] == sm["founded"] > 0


def _two_peoples(tmp_path, share, dens=40):
    g = shared_grid(LEVEL)
    F = 13
    lines = [{"index": 0, "id": "a", "group_of": None}, {"index": 1, "id": "d", "name": "dwarves", "group_of": None, "traits": ["miner"]}]
    tech = {"a": {"villages": [11.0, "x"], "towns": [6.0, "x"]}, "d": {"villages": [11.0, "x"], "mines": [30.0, "x"]}}
    out, _ = _run(tmp_path, _flat(g, F, dens), _flat(g, F, 0.5), _flat(g, F, 200), lines=lines, tech=tech,
                  second=np.full((F, g.n), 1, np.uint8), second_share=share)
    return out, g


def test_a_second_people_has_its_own_place_amid_another(tmp_path):
    out, g = _two_peoples(tmp_path, 20.0)
    sites = ST.derive(out, RIVER_SHIFT=0.0)["doc"]["sites"]
    own = [s for s in sites if s["kind"] == "minority" and s["abandoned_kyr"] is None]
    chief = {s["cell"] for s in sites if s["kind"] == "chief" and s["abandoned_kyr"] is None}
    assert len(own) > g.n // 2 and all(s["holder"] == "d" and s["who"] == {"d": 100} for s in own)
    assert {s["cell"] for s in own} & chief  # (beside the humans' place in the same cell)
    assert all(s["tier_now"] in ("village", "town") for s in own)


def test_a_small_minority_has_no_place_of_its_own(tmp_path):
    out, _ = _two_peoples(tmp_path, 2.0)
    assert not [s for s in ST.derive(out)["doc"]["sites"] if s["kind"] == "minority"]


def test_mines_on_deposits_for_a_people_that_knows_mines(tmp_path, monkeypatch):
    out, g = _two_peoples(tmp_path, 20.0, dens=400)
    dep = np.zeros((2, g.n), bool)
    dep[1, : g.n // 4] = True  # (rock salt in a quarter of the cells: 'mines' is enough; ore would want 'copper')
    dep[0, g.n // 4: g.n // 2] = True
    monkeypatch.setattr(ST, "_deposits", lambda world, n: dep)
    sites = ST.derive(out, RIVER_SHIFT=0.0)["doc"]["sites"]
    mines = [s for s in sites if s["kind"] == "mine"]
    assert mines and all(s["cell"] < g.n // 4 and s["holder"] == "d" and s["tier_now"] == "mine" for s in mines)


def test_the_brief_reads_the_ledger(tmp_path):
    from types import SimpleNamespace

    from planet.lineages import brief as B
    out, g = _two_peoples(tmp_path, 20.0)
    ST.write(out, report=False)
    meta = json.loads((out / "run.json").read_text())["meta"]
    ctx = SimpleNamespace(meta=meta, dir=out, lines=[{**l, "name": l.get("name", l["id"])} for l in meta["lineages"]],
                          idx={l["id"]: l["index"] for l in meta["lineages"]})
    st = B._settlements(ctx, np.ones(g.n, bool), 0.0, "d")
    alive = [x for x in json.loads((out / "settlements.json").read_text())["sites"] if x["abandoned_kyr"] is None]
    assert sum(st["counts"].values()) == len(alive)
    assert st["own_places_of_second_peoples"]["d"] == sum(x["kind"] == "minority" for x in alive)
    assert st["people"]["own_places_among_others"] == st["own_places_of_second_peoples"]["d"]
    md = "\n".join(B._settlements_md(st))
    assert "## Towns and cities" in md and "The dwarves world-wide" in md
    past = B._settlements(ctx, np.ones(g.n, bool), 13.0, None)  # (before any place was founded)
    assert past["counts"] == {} and past["largest"] == []
