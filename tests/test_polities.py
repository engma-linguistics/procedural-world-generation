"""Polities v0 (planet/lineages/polities.py, PW-1431): the claim kernel, the war seam, the doc's views and the culture uids."""

import re
from pathlib import Path

import numpy as np

from planet.grid import shared_grid
from planet.lineages import cultures as CU
from planet.lineages import polities as PO


def _setup(level=4):
    g = shared_grid(level)
    c, src, dst = np.asarray(g.centers, float), np.asarray(g.nbr_src), np.asarray(g.nbr_idx)
    ekm = np.linalg.norm(c[dst] - c[src], axis=1) * PO.R_EARTH_KM
    return g, ekm, np.asarray(g.nbr_off, np.int64), np.asarray(g.nbr_idx, np.int64)


def _claim(g, ekm, off, idx, seed, budget, owner, pid, sea=None, sea_x=-1.0, edz=None):
    n = g.n
    sea = np.zeros(n, bool) if sea is None else sea
    edz = np.zeros(len(ekm)) if edz is None else edz
    return PO._claim(seed, budget, 1.0, sea_x, PO.CLIMB_M, off, idx, ekm, edz, sea, np.zeros(n, bool), np.ones(n, bool), owner, pid,
                     np.full(n, np.inf), np.zeros(n, np.int64), np.zeros(n, np.int64))


def test_a_claim_reaches_its_budget_and_no_further():
    g, ekm, off, idx = _setup()
    owner = np.full(g.n, -1, np.int64)
    step = float(np.median(ekm))
    got = _claim(g, ekm, off, idx, 0, 0.5 * step, owner, 0)
    assert got == 1 and owner[0] == 0 and (owner >= 0).sum() == 1  # (a chiefdom's reach: its own cell)
    owner[:] = -1
    got = _claim(g, ekm, off, idx, 0, 1.2 * step, owner, 0)
    assert got == 1 + len(idx[off[0]:off[1]])  # (one ring)


def test_claimed_land_is_a_border_and_the_sea_needs_boats():
    g, ekm, off, idx = _setup()
    step = float(np.median(ekm))
    owner = np.full(g.n, -1, np.int64)
    ring = idx[off[0]:off[1]]
    owner[ring] = 7  # (someone else holds the ring around cell 0)
    assert _claim(g, ekm, off, idx, 0, 10 * step, owner, 0) == 1
    owner[:] = -1
    sea = np.zeros(g.n, bool)
    sea[ring] = True
    assert _claim(g, ekm, off, idx, 0, 3 * step, owner, 0, sea=sea) == 1  # (no boats: walled in by the sea)
    owner[:] = -1
    assert _claim(g, ekm, off, idx, 0, 3 * step, owner, 0, sea=sea, sea_x=PO.SAIL_X) > 1 + len(ring)  # (sails cross it)


def test_climbing_costs_reach():
    g, ekm, off, idx = _setup()
    step = float(np.median(ekm))
    flat = np.full(g.n, -1, np.int64)
    a = _claim(g, ekm, off, idx, 0, 4 * step, flat, 0)
    hilly = np.full(g.n, -1, np.int64)
    b = _claim(g, ekm, off, idx, 0, 4 * step, hilly, 0, edz=np.full(len(ekm), PO.CLIMB_M))
    assert b < a


def test_borders_and_the_war_seam():
    g, ekm, off, idx = _setup()
    owner = np.full(g.n, -1, np.int64)
    owner[0] = 0
    owner[idx[off[0]]] = 1
    assert PO.borders(owner, g) == {(0, 1): 1}
    assert PO.no_war(owner.copy(), {}).tolist() == owner.tolist() and PO.WAR is PO.war_v0


def test_pack_round_trips_and_step_view_picks_the_nearest_step():
    cells = np.array([5, 6, 7, 20, 22, 23])
    runs = PO._pack(cells)
    assert runs == [5, 3, 20, 1, 22, 2]
    assert PO._unpack(runs).tolist() == cells.tolist()
    doc = {"tiers": list(PO.TIERS), "steps": [{"ago": 0.2}, {"ago": 0.1}, {"ago": 0.0}],
           "maps": [[], [[3, 1, runs, {"u": 10}, 500]], []]}
    v = PO.step_view(doc, 0.12)
    assert v["step"] == 1 and v["polities"][0] == {"id": 3, "tier": "state", "cells": cells.tolist(), "subjects": {"u": 10}, "people": 500, "provinces": {}}
    assert "maps" not in PO.summary(doc)


def test_every_number_is_sourced_or_a_judgement():
    src = Path(PO.__file__).read_text().splitlines()
    for line in src:
        m = re.match(r"^([A-Z][A-Z_]+(?:, [A-Z_]+)*) = [-\d]", line)
        if m and m.group(1) not in ("FORMAT", "VERSION", "R_EARTH_KM"):
            assert "judgement" in line or "sourced" in line or "(any of" in line, line
    assert {"CHIEF_KM", "STATE_KM", "DRAGON_KM", "SUBJECT_SHARE"} <= set(PO.constants())


def test_culture_uids_are_kept_or_rebuilt_as_derive_builds_them():
    demes = {"demes": [{"lat": 10.04, "lon": -3.0}, {"lat": 1.0, "lon": 2.0}]}
    old = {"cultures": [{"people": "dwarf", "how": "founding", "born_kyr": 300.0, "demes": [0]},
                        {"people": "dwarf", "how": "founding", "born_kyr": 300.0, "demes": [0]}]}
    assert CU.uids(old, demes) == ["dwarf:founding:300.000:10.0:-3.0", "dwarf:founding:300.000:10.0:-3.0+"]
    new = {"cultures": [dict(old["cultures"][0], uid="kept")]}
    assert CU.uids(new, demes) == ["kept"]


def test_server_needs_a_run():
    from planet import server
    body, code = server.polities("")
    assert code == 400 and "run" in body["error"]


def _war_ctx(g, owner, S, people=("human", "orc"), ago=1.0, invasions=()):
    seats = [{"key": f"s{i}", "tier": "state", "people": p} for i, p in enumerate(people)]
    return {"seats": seats, "strength": list(S), "eligible": lambda p: True, "borders": lambda: PO.borders(owner, g),
            "run": "test", "step": 3, "ago": ago, "invasions": list(invasions)}


def test_war_v0_takes_a_weaker_neighbour_whole(monkeypatch):
    g, ekm, off, idx = _setup()
    owner = np.full(g.n, -1, np.int64)
    owner[0] = 0
    ring = idx[off[0]:off[1]]
    owner[ring] = 1
    monkeypatch.setattr(PO, "WAR_P", 1.0)
    ctx = _war_ctx(g, owner, (3.0, 1.0))
    out = PO.war_v0(owner.copy(), ctx)
    assert ctx["taken"] == [(0, 1, "war")] and (out[ring] == 0).all() and out[0] == 0  # (all its cells change hands)
    ctx = _war_ctx(g, owner, (1.2, 1.0))  # (not WAR_ODDS times stronger: no war)
    assert PO.war_v0(owner.copy(), ctx).tolist() == owner.tolist() and ctx["taken"] == []
    monkeypatch.setattr(PO, "WAR_P", 0.0)
    ctx = _war_ctx(g, owner, (3.0, 1.0))
    assert PO.war_v0(owner.copy(), ctx).tolist() == owner.tolist()


def test_an_authored_invasion_raises_the_chance_and_a_strong_one_waives_the_odds(monkeypatch):
    g, ekm, off, idx = _setup()
    owner = np.full(g.n, -1, np.int64)
    owner[0] = 0
    owner[idx[off[0]:off[1]]] = 1
    monkeypatch.setattr(PO, "WAR_P", 0.25)
    row = {"who": "human", "whom": "orc", "from_kyr": 1.2, "to_kyr": 0.8, "strength": "strong"}
    ctx = _war_ctx(g, owner, (1.0, 1.0), invasions=[row])  # (equal strength; a strong invasion: chance 1.0, odds waived)
    PO.war_v0(owner.copy(), ctx)
    assert ctx["taken"] == [(0, 1, "invasion")]
    ctx = _war_ctx(g, owner, (1.0, 1.0), ago=2.0, invasions=[row])  # (outside its window: nothing)
    PO.war_v0(owner.copy(), ctx)
    assert ctx["taken"] == []


def test_draws_are_seeded_and_strength_counts_military_edges():
    a = PO.draw("r", "s1", 4, "fall")
    assert a == PO.draw("r", "s1", 4, "fall") and 0 <= a < 1 and a != PO.draw("r", "s1", 5, "fall")
    knows = lambda p, t, ago: t in ("iron", "riding")
    assert PO.strength(1000.0, "human", knows, 0.0) == 1000.0 * PO.MIL_X ** 2


def test_lifetimes_read_founding_to_fall_and_time_at_half_peak():
    doc = {"step_kyr": 0.1, "polities": [
        {"id": 0, "tier_peak": "state", "founded_kyr": 0.5, "fell_kyr": 0.2, "fell_how": "conquered"},
        {"id": 1, "tier_peak": "empire", "founded_kyr": 0.3, "fell_kyr": None, "fell_how": None}],
        "maps": [[[0, 1, [0, 10], {}, 5]], [[0, 1, [0, 4], {}, 5], [1, 2, [20, 2], {}, 5]], [[0, 1, [0, 6], {}, 5], [1, 2, [20, 2], {}, 5]]]}
    L = PO.lifetimes(doc)["states and empires"]
    assert L["fell"] == [300] and L["half"] == [200, 200] and L["standing"] == 1 and L["how"]["conquered"] == 1


def test_a_confederation_needs_a_citys_people_in_reach_and_a_foreign_state_beside_it():
    """PW-785, step 1b: villages of a people with kings but no city band together only beside a foreign power."""
    g, ekm, off, idx = _setup(6)
    c0 = 100
    ring = [int(b) for b in idx[off[c0]:off[c0 + 1]]]
    lines = [{"id": "herd"}, {"id": "farm"}]

    class R:
        pass
    R.g, R.lines, R.ekm, R.uids = g, lines, ekm, ["u0"]
    R.knows = staticmethod(lambda p, t, ago: p == "herd" and t in ("chiefdoms", "kingship", "law", "bureaucracy", "writing"))
    F = {"edz": np.zeros(len(ekm)), "sea": np.zeros(g.n, bool), "ice": np.zeros(g.n, bool), "peopled": np.ones(g.n, bool)}
    cells = [c0] + ring[:4]
    sites = [{"id": j, "kind": "chief", "cell": c} for j, c in enumerate(cells)]
    popk = np.array([500.0] + [3000.0] * 4)

    def run(prev_owner, city_min=10000.0):
        return PO._confederations(R, F, [], sites, popk, np.arange(len(sites)), lambda s, a: "herd", np.array(cells), 0.0, 5, prev_owner,
                                  {0: ("state", "farm")}, {}, {}, city_min, {c: {0} for c in cells}, {}, off, idx,
                                  np.full(g.n, np.inf), np.zeros(g.n, np.int64), np.zeros(g.n, np.int64))
    beside = np.full(g.n, -1, np.int64)
    beside[ring[5]] = 0  # (a foreign state held a cell beside them last step)
    out = run(beside)
    assert len(out) == 1 and out[0]["confed"] and out[0]["tier"] == "state" and out[0]["heads"] >= 10000 and out[0]["people"] == "herd"
    assert run(np.full(g.n, -1, np.int64)) == []  # (no foreign state: nothing to band together against)
    assert run(beside, city_min=20000.0) == []  # (too few of them within reach)


def test_a_city_states_reach_stays_in_spencers_band_unless_conquest_or_the_frontier_widens_it():
    """PW-1449: law, distance, riding and roads move a city-state's reach inside Spencer's 50-250 km and never past it; a polity holding
    a conquered state, or a confederation (WIDE_BY), keeps the stacked reach."""
    class R:
        knows = staticmethod(lambda p, t, ago: t in ("law", "bureaucracy", "riding", "roads", "sails"))
    s = {"people": "x", "tier": "state"}
    b, lx, sx = PO._reach(R, s, 0.0)
    assert abs(b / lx - PO.STATE_MAX_KM) < 1e-6 and b / sx <= PO.STATE_MAX_KM + 1e-6  # (flat land and sea: at most the cap)
    wb, wlx, wsx = PO._reach(R, s, 0.0, wide=True)
    assert wb / wlx > 3 * PO.STATE_MAX_KM and wsx == PO.SAIL_X  # (150 x 4/3 x 2 / (2/3)^2 = 900 km: the stacked reach)
    R.knows = staticmethod(lambda p, t, ago: False)
    assert PO._reach(R, s, 0.0) == (PO.STATE_KM, 1.0, -1.0)  # (a bare state: the middle of the band, untouched)
    assert PO._reach(R, {"people": "x", "tier": "chiefdom"}, 0.0)[0] == PO.CHIEF_KM


def test_a_polity_is_named_for_the_people_holding_its_capital_then():
    """PW-1451: a capital another people took renames the polity from then on; 'founded by' stays the first people."""
    class R:
        lname = {"cervid_folk": "cervid-kin", "human": "humans"}
    rec = {"kind": "town", "people": "cervid_folk", "capital": {"place": "south-east of Razukum", "cell": 7}}
    assert PO._name(R, rec) == "South-east of Razukum (cervid-kin)"
    assert PO._name(R, rec, "human") == "South-east of Razukum (humans)"
    rec["names"] = [[8.2, "South-east of Razukum (cervid-kin)"], [6.2, "South-east of Razukum (humans)"]]
    assert PO.name_at(rec, 9.0) == PO.name_at(rec, 7.0) == "South-east of Razukum (cervid-kin)"
    assert PO.name_at(rec, 6.2) == PO.name_at(rec, 0.0) == "South-east of Razukum (humans)"
    assert PO._at([[8.2, "a"], [6.2, "b"]], 6.25)[1] == "a"
