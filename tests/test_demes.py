"""Demes (planet/lineages/demes.py, PW-981): a people's cells cut into regional populations and followed through frames."""

import numpy as np

from planet.grid import shared_grid
from planet.lineages import demes as DM

LINES = [{"index": 0, "id": "stem", "color": "#336699", "parents": []},
         {"index": 1, "id": "folk", "color": "#cc5500", "parents": ["stem"]}]


def _g():
    return shared_grid(5)


def _cap(g, lat, lon, deg):
    """Cells within deg of (lat, lon)."""
    la, lo = np.radians(lat), np.radians(lon)
    c = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    return g.centers @ c >= np.cos(np.radians(deg))


def _frame(dm, ago, masks, land):
    """One frame: masks {line: occupied}; every cell costs 1 (an even coast), the lead is the people itself."""
    n = dm.g.n
    lead = np.full(n, -1, np.int64)
    for k, o in masks.items():
        lead[o] = k
    return dm.update(ago, masks, np.ones(n), land, lead, np.full(n, -1, np.int64))


def _alive(dm, line=None):
    return [d for d in dm.demes if d.ended is None and (line is None or d.line == line)]


def test_sea_gap_cuts_a_people_and_a_bridge_does_not():
    g = _g()
    land = _cap(g, 0, 0, 12) | _cap(g, 0, 40, 12)  # two landmasses ~16 degrees of sea apart
    dm = DM.Demes(g, LINES, 120.0)
    _frame(dm, 10.0, {1: land.copy()}, land)
    assert len(_alive(dm, 1)) == 2  # (one population per landmass)
    land2 = land | (_cap(g, 0, 20, 9) & (np.abs(g.lat) < 3))  # a land bridge
    dm2 = DM.Demes(g, LINES, 120.0)
    _frame(dm2, 10.0, {1: land2.copy()}, land2)
    assert len(_alive(dm2, 1)) == 1


def test_split_along_a_gap_keeps_the_larger_piece_and_dates_it():
    g = _g()
    big, small = _cap(g, 0, 0, 14), _cap(g, 0, 32, 10)
    bridge = _cap(g, 0, 16, 8) & (np.abs(g.lat) < 3)
    land = big | small | bridge
    dm = DM.Demes(g, LINES, 120.0)
    _frame(dm, 20.0, {1: land.copy()}, land)
    assert len(_alive(dm, 1)) == 1
    first = _alive(dm, 1)[0].id
    land_hi = big | small  # (the sea rises over the bridge)
    for i in range(DM.PERSIST):  # (a split counts once it has held PERSIST frames, dated when it began)
        assert len(_alive(dm, 1)) == 1
        lab = _frame(dm, 10.0 - i, {1: land_hi.copy()}, land_hi)
    alive = _alive(dm, 1)
    assert len(alive) == 2
    assert lab[np.flatnonzero(big)[0]] == first  # (the larger piece keeps its id)
    new = [d for d in alive if d.id != first][0]
    assert new.parent == first and new.how == "split_gap" and new.born == 10.0 and new.settled == 20.0
    assert any(e["kind"] == "split_gap" and e["deme"] == new.id and e["ago_kyr"] == 10.0 and e["confirmed_kyr"] == 11.0 - DM.PERSIST for e in dm.events)


def test_a_brief_gap_does_not_split():
    g = _g()
    big, small = _cap(g, 0, 0, 14), _cap(g, 0, 32, 10)
    land = big | small | (_cap(g, 0, 16, 8) & (np.abs(g.lat) < 3))
    dm = DM.Demes(g, LINES, 120.0)
    _frame(dm, 20.0, {1: land.copy()}, land)
    for i in range(DM.PERSIST - 1):
        _frame(dm, 19.0 - i, {1: big | small}, big | small)
    _frame(dm, 10.0, {1: land.copy()}, land)  # (the bridge back before the split held)
    assert len(dm.demes) == 1 and not dm.apart


def test_a_wide_range_becomes_a_chain_of_demes():
    g = _g()
    band = np.abs(g.lat) < 8  # a land ring round the equator: ~40,000 km long
    dm = DM.Demes(g, LINES, 240.0)
    _frame(dm, 5.0, {1: band.copy()}, band)
    alive = _alive(dm, 1)
    assert len(alive) >= 3
    assert sum(d.how == "split_distance" for d in alive) >= 2
    assert all(dm.diam[d.id] <= DM.SPLIT_KM for d in alive)


def test_founder_chain_extinction_and_new_people_parent():
    g = _g()
    land = _cap(g, 0, 0, 25)
    home = _cap(g, 0, 0, 6)
    dm = DM.Demes(g, LINES, 240.0)
    _frame(dm, 30.0, {0: home.copy()}, land)
    stem = _alive(dm, 0)[0].id
    _frame(dm, 29.0, {0: _cap(g, 0, 0, 9)}, land)  # (the front spreads: the same deme)
    assert [d.id for d in _alive(dm, 0)] == [stem]
    _frame(dm, 28.0, {1: _cap(g, 0, 0, 9)}, land)  # the stem gives way to its child people
    assert dm.demes[stem].ended == 28.0 and dm.demes[stem].end_how == "extinct"
    child = _alive(dm, 1)
    assert len(child) == 1 and child[0].parent == stem and child[0].how == "from_people"
    _frame(dm, 27.0, {}, land)
    assert not _alive(dm)


def test_two_small_demes_fuse_when_they_touch():
    g = _g()
    a, b = _cap(g, 0, -12, 9), _cap(g, 0, 12, 9)
    land = _cap(g, 0, 0, 40)
    dm = DM.Demes(g, LINES, 120.0)  # (land cut between them, not sea: two demes until they touch)
    _frame(dm, 10.0, {1: a | b}, land)
    assert len(_alive(dm, 1)) == 2
    for i in range(DM.PERSIST):
        _frame(dm, 9.0 - i, {1: a | b | (_cap(g, 0, 0, 6) & (np.abs(g.lat) < 3))}, land)
    alive = _alive(dm, 1)
    assert len(alive) == 1
    assert any(d.end_how == "fused" and d.into == alive[0].id for d in dm.demes)


def test_document_names_and_contacts():
    g = _g()
    land = _cap(g, 0, 0, 30)
    dm = DM.Demes(g, LINES, 240.0)
    a, b = _cap(g, 0, -10, 10), _cap(g, 0, 10, 10) & ~_cap(g, 0, -10, 10)
    n = g.n
    lead = np.full(n, -1, np.int64)
    lead[a], lead[b] = 0, 1
    dm.update(1.0, {0: a, 1: b}, np.ones(n), land, lead, np.full(n, -1, np.int64))
    doc = DM._document(dm, {"lineages": LINES, "present": {"landmasses": []}}, g, 1.0, 0.0)
    assert [d["short"] for d in doc["doc"]["demes"]] == ["stem 1", "folk 1"]
    assert len(doc["doc"]["pairs"]) == 1 and doc["doc"]["pairs"][0]["peak"] > 0 and not doc["doc"]["pairs"][0]["same_people"]
    assert doc["summary"]["alive"] == 2
    assert all(c.startswith("#") and len(c) == 7 for c in (d["color"] for d in doc["doc"]["demes"]))


def test_derive_overrides_leave_defaults_unchanged(monkeypatch):
    seen = []

    def fake(run_dir, window_kyr):
        seen.append((DM.SPLIT_KM, DM.FUSE_KM))
        return {}

    monkeypatch.setattr(DM, "_derive", fake)
    s0, f0 = DM.SPLIT_KM, DM.FUSE_KM
    DM.derive("x")
    DM.derive("x", split_km=3000, fuse_km=1500)
    assert seen == [(s0, f0), (3000.0, 1500.0)]
    assert (DM.SPLIT_KM, DM.FUSE_KM) == (s0, f0) == (7000.0, 4000.0)


def test_reach_by_kind_a_dragon_kind_is_one_population_over_a_sea_that_cuts_walkers():
    from planet.lineages.history.megafauna import LINK_KM
    from planet.lineages.history.params import JUMP_KM
    g = _g()
    land = _cap(g, 0, 0, 12) | _cap(g, 0, 40, 12)  # (two landmasses ~16 degrees of sea apart)
    lines = LINES + [{"index": 2, "id": "wyrm", "color": "#aa0000", "parents": ["stem"], "traits": ["flies"]}]
    dm = DM.Demes(g, lines, 120.0, mega={"wyrm"})
    _frame(dm, 10.0, {1: land.copy(), 2: land.copy()}, land)
    assert len(_alive(dm, 1)) == 2 and len(_alive(dm, 2)) == 1  # (the walkers cut by the sea; LINK_KM flies over it)
    s, sea, neck, free = dm.mobility(2, 10.0)
    assert free and sea == neck == LINK_KM and s == LINK_KM / JUMP_KM
    assert dm.mobility(1, 10.0) == (1.0, DM.SEA_KM, DM.NECK_KM, False)  # (a walker: the thresholds as they were)


def test_a_seafaring_people_crosses_wider_sea_with_its_craft():
    sea = [{"index": 0, "id": "sailors", "color": "#0055aa", "parents": [], "demography": {"sea_share": 0.6}}]
    dm = DM.Demes(_g(), sea, 120.0)
    assert dm.mobility(0, 150.0)[1] == DM.SEA_KM  # (before rafts: none)
    assert dm.mobility(0, 30.0)[1] == 300.0  # (canoes and outriggers since 60 kyr)
    assert dm.mobility(0, 1.0)[1] == 2500.0  # (sailing ships, at a full sea share)
