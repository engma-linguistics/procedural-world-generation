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
                     np.full(n, np.inf), np.zeros(n, np.int64))


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


def test_borders_and_the_war_seam_change_nothing_by_default():
    g, ekm, off, idx = _setup()
    owner = np.full(g.n, -1, np.int64)
    owner[0] = 0
    owner[idx[off[0]]] = 1
    assert PO.borders(owner, g) == {(0, 1): 1}
    assert PO.WAR(owner.copy(), {}).tolist() == owner.tolist()


def test_pack_round_trips_and_step_view_picks_the_nearest_step():
    cells = np.array([5, 6, 7, 20, 22, 23])
    runs = PO._pack(cells)
    assert runs == [5, 3, 20, 1, 22, 2]
    assert PO._unpack(runs).tolist() == cells.tolist()
    doc = {"tiers": list(PO.TIERS), "steps": [{"ago": 0.2}, {"ago": 0.1}, {"ago": 0.0}],
           "maps": [[], [[3, 1, runs, {"u": 10}, 500]], []]}
    v = PO.step_view(doc, 0.12)
    assert v["step"] == 1 and v["polities"][0] == {"id": 3, "tier": "state", "cells": cells.tolist(), "subjects": {"u": 10}, "people": 500}
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
