"""Trade step 3 (PW-1504): routes and trading towns; herders fetching grain (PW-1511 B); flyers carrying wild foods (PW-1510). Each rule on
test_trade_flow's hand-made line of six cells, no run needed."""

import json

import numpy as np
import pytest

from planet.lineages import trade_flow as TF
from planet.lineages import trade_routes as RT
from tests.test_trade import N
from tests.test_trade_flow import _get, _line_ctx

A = np.repeat(np.arange(N), np.diff([0, 1, 3, 5, 7, 9, 10]))  # (the line's edge sources, as _line_ctx builds them)


def _with_town(ctx, tmp_path, cell=2, pop=5000):
    """A settlement-ledger town of `pop` people in `cell` (the farmers' plain by default)."""
    doc = {"tiers": {"town_min_by_stage": [1000, 1000, 1000, 1000, 2000], "city_min": 10000},
           "sites": [{"id": 7, "kind": "chief", "cell": cell, "place": "the ford", "founded_kyr": 10.0, "abandoned_kyr": None, "peak_pop": pop,
                      "series": [[10.0, pop], [0.0, pop]], "bands": []}]}
    (tmp_path / "settlements.json").write_text(json.dumps(doc))
    ctx.meta["settlements"] = {"file": "settlements.json"}
    return ctx


def _edges(routes):
    return {(min(a, b), max(a, b)) for a, b, *_ in routes}


def test_the_big_flows_become_routes_along_the_way_they_took(tmp_path):
    """design1.md step 3: a big flow between cultures is followed back along its least-cost way; its trunk is a route."""
    f = TF.flows_at(_line_ctx(tmp_path), 0)
    assert f["routes"]
    nbr = {(min(a, b), max(a, b)) for a, b in zip(A, _line_ctx(tmp_path).g.nbr_idx)}
    assert _edges(f["routes"]) <= nbr  # (every stretch joins two neighbouring cells)
    assert (1, 2) in _edges(f["routes"])  # (the farmers' grain to the herders crosses 2 -> 1)
    grain = [r for r in f["routes"] if (r[0], r[1]) in ((1, 2), (2, 1))]
    assert any(RT.GROUPS[r[3]] == "food" for r in grain) or grain[0][2] > 0
    assert all(0 < r[2] <= 1 + 1e-9 and RT.MODES[r[4]] == "land" for r in f["routes"])
    assert TF.flows_at(_line_ctx(tmp_path), 0, routes=False)["flows"] == f["flows"]  # (a read-out: tracing changes no flow)


def test_a_town_on_a_route_is_a_trading_town_and_its_kind_follows_the_modes(tmp_path, monkeypatch):
    """A ledger town on a route is a market town; on a river route a river port (review1.md section 5: central places)."""
    monkeypatch.setattr(RT, "LONG_KM", 0.0)  # (PW-1530: a trading town needs a long-haul route; on this short line every haul counts as one)
    h = TF.flows_at(_with_town(_line_ctx(tmp_path), tmp_path), 0)["hubs"]
    assert len(h) == 1 and h[0]["cell"] == 2 and h[0]["kind"] == "market town" and h[0]["place"] == "the ford"
    know = {"herder": ["herding", "animal_cattle", "salting", "copper", "native_copper", "bronze", "quarrying", "canoes"],
            "farmer": ["cultivation", "crop_wheat", "salting", "copper", "native_copper", "bronze", "quarrying", "canoes"], "forager": ["ornament"]}
    ctx = _with_town(_line_ctx(tmp_path, nav=[1] * N, elev=[10.0, 20.0, 30.0, 40.0, 50.0, 60.0], know=know), tmp_path)
    h = TF.flows_at(ctx, 0)["hubs"]
    assert h and h[0]["kind"] == "river port" and "river" in h[0]["modes"]


def test_a_caravan_town_stands_where_pack_routes_leave_farmland_for_steppe(tmp_path, monkeypatch):
    """review1.md section 4 (the Sahel towns, the Silk Road oases): pack animals, a farmed town, an unfarmed desert or steppe beyond."""
    monkeypatch.setattr(RT, "LONG_KM", 0.0)  # (PW-1530: a trading town needs a long-haul route; on this short line every haul counts as one)
    know = {"herder": ["herding", "animal_cattle", "salting", "pack_animals"], "farmer": ["cultivation", "crop_wheat", "salting", "pack_animals"],
            "forager": ["ornament"]}
    ctx = _with_town(_line_ctx(tmp_path, know=know), tmp_path)
    ctx._arrs["climate"] = np.array([6, 6, 7, 7, 7, 7])  # (cold steppe in the herders' cells 0-1)
    ctx.arr["climate"] = 1
    h = TF.flows_at(ctx, 0)["hubs"]
    assert h and h[0]["kind"] == "caravan town"
    know["farmer"].remove("pack_animals")
    ctx = _with_town(_line_ctx(tmp_path, know=know), tmp_path)
    ctx._arrs["climate"], ctx.arr["climate"] = np.array([6, 6, 7, 7, 7, 7]), 1
    assert TF.flows_at(ctx, 0)["hubs"][0]["kind"] == "market town"  # (no pack animals: no caravans)
    know["farmer"].append("pack_animals")
    ctx = _with_town(_line_ctx(tmp_path, know=know), tmp_path)
    ctx._arrs["climate"], ctx.arr["climate"] = np.array([6, 6, 6, 7, 7, 7]), 1  # (the town's own cell is dry and farmed, as an oasis: PW-1515)
    assert TF.flows_at(ctx, 0)["hubs"][0]["kind"] == "caravan town"


def test_a_merchant_quarter_lifts_its_border_toll_next_era(tmp_path, monkeypatch):
    """Curtin's trade diasporas (review1.md section 5); design1.md step 2: a quarter of the giver's people in the taker's town removes the
    border's crossing cost."""
    monkeypatch.setattr(RT, "LONG_KM", 0.0)  # (PW-1530: a trading town needs a long-haul route; on this short line every haul counts as one)
    ctx = _line_ctx(tmp_path)
    fr0 = TF._Frame(ctx, 0, None, None)
    fr1 = TF._Frame(ctx, 0, None, None, quarters={(0, 1)})  # (the farmers' merchants in a herders' town)
    a, b = fr0.e["a"], fr0.e["b"]
    into = (a == 2) & (b == 1)  # (farmers' land into the herders')
    assert fr0.e["toll"][into][0] > 0 and fr1.e["toll"][into][0] == 0 and fr1.quarter_edges == 1
    back = (a == 1) & (b == 2)
    assert fr1.e["toll"][back][0] == fr0.e["toll"][back][0]  # (only the border the merchants' goods cross into their host)
    assert fr1.walk("grain")[0][0] > fr0.walk("grain")[0][0]
    town = _with_town(_line_ctx(tmp_path), tmp_path, cell=1)  # (a herders' town that the others' goods pass on their way to cell 0)
    f = TF.flows_at(town, 0)
    q = f["hubs"][0]["quarters"]
    assert q and all(x[0] != 0 and x[2] >= RT.QUARTER_SHARE for x in q) and [[0, x[0]] for x in q] == f["quarters"]


def test_herders_fetch_grain_with_their_own_animals_as_a_switch(tmp_path):
    """PW-1511 B (Khazanov: nomads drove their own herds to the frontier markets): pack-animal cost on herders' land and the farmers' edge
    for grain, with or without the pack_animals tech; other goods keep their cost."""
    ctx = _line_ctx(tmp_path)
    a = TF._Frame(ctx, 0, None, None)
    b = TF._Frame(ctx, 0, None, None, fetch=True)
    e = (a.e["a"] == 1) & (a.e["b"] == 0)
    assert b.cost("bulk", True)[0][e][0] < a.cost("bulk")[0][e][0]
    assert np.array_equal(b.cost("bulk")[0], a.cost("bulk")[0])
    assert b.walk("grain")[0][0] > a.walk("grain")[0][0] and np.array_equal(b.walk("timber")[0], a.walk("timber")[0])
    ga, gb = _get(TF.flows_at(ctx, 0)["flows"], 1, 0, "grain"), _get(TF.flows_at(ctx, 0, fetch=True)["flows"], 1, 0, "grain")
    assert gb[3] >= ga[3]


def test_flyers_carry_the_wild_foods_of_their_range(tmp_path):
    """PW-1510: a flying people that knows no crop still carries the plants growing wild where it lives, to farmers where they don't grow."""
    know = {"herder": ["herding"], "farmer": ["cultivation", "crop_wheat"], "forager": ["ornament"], "aarakocra": []}
    ctx = _line_ctx(tmp_path, extra_lines=("aarakocra",), know=know)
    ctx.lines[3]["traits"] = ["flies"]
    ctx.cultures()["deme_culture"] = [0, 1, 2, 3]
    cells = np.array([0, 1, 2, 3, 4, 5, 5], np.int64)
    dem = np.array([0, 0, 1, 1, 2, 2, 3], np.uint16)
    ctx.overlap = lambda: ({"offsets": np.array([[0, len(cells)]]), "cells": cells}, dem)
    ctx._arrs["crop_known"] = np.array([0, 0, 1, 1, 0, 0])
    ctx._arrs["crop_wild"] = np.array([0, 0, 0, 0, 0, 1])  # (wheat grows wild in the flyers' cell 5 only)
    ctx.arr["crop_wild"] = 1
    ff = TF.flows_at(ctx, 0)["flyer_foods"]
    rec = next(r for r in ff if r["crop"] == "wheat")
    assert rec["from"] == "wild" and rec["culture"] == 3 and 4 in rec["cells"] and 5 not in rec["cells"]
    ctx._arrs["crop_wild"] = np.zeros(N, np.int64)
    assert not TF.flows_at(ctx, 0)["flyer_foods"]  # (nothing known, nothing wild: nothing carried)


def test_views_frame_and_culture_hubs(tmp_path):
    ctx = _with_town(_line_ctx(tmp_path), tmp_path)
    ctx.dir = tmp_path
    doc = TF.derive(tmp_path, ctx)
    v = RT.frame_view(doc, 0.2)
    assert v["ago_kyr"] == 0.0 and v["routes"] and v["hubs"][0]["kind"] == "market town"
    assert RT.frame_view(doc, 5.0)["ago_kyr"] is None  # (outside the window: nothing drawn)
    assert RT.culture_hubs(doc["frames"][0], 1)[0][:2] == ["the ford", "market town"]
    C = [{"name": "a", "end": None, "into": None, "ended_kyr": None, "born_kyr": 100.0}] * 3
    assert TF.culture_view(doc, 1, C)[0]["hubs"][0][1] == "market town"
    assert doc["constants"]["quarters"] is TF.QUARTERS and doc["constants"]["fetch"] is TF.FETCH


def test_last_eras_route_holds_down_to_the_lower_bar(tmp_path, monkeypatch):
    """PW-1514: a stretch between ROUTE_HOLD x ROUTE_SHARE and ROUTE_SHARE is a route only if it was one the era before (or continues a
    route, SPAN); one under the lower bar is never a route."""
    ctx = _line_ctx(tmp_path)
    r = TF.flows_at(ctx, 0)["routes"]
    a, b, s = r[-1][0], r[-1][1], r[-1][2]  # (the weakest route stretch)
    monkeypatch.setattr(RT, "SPAN", False)
    monkeypatch.setattr(RT, "LOCAL_SHARE", RT.ROUTE_SHARE)  # (one bar for both layers here)
    r = TF.flows_at(ctx, 0)["routes"]
    a, b, s = r[-1][0], r[-1][1], r[-1][2]  # (the weakest route stretch)
    monkeypatch.setattr(RT, "ROUTE_SHARE", s * 1.5)  # (now it sits between the two bars)
    monkeypatch.setattr(RT, "LOCAL_SHARE", s * 1.5)
    key = min(a, b) * ctx.g.n + max(a, b)
    assert (min(a, b), max(a, b)) not in _edges(TF.flows_at(_line_ctx(tmp_path), 0)["routes"])
    assert (min(a, b), max(a, b)) in _edges(TF.flows_at(_line_ctx(tmp_path), 0, last_routes={key})["routes"])
    monkeypatch.setattr(RT, "ROUTE_SHARE", s * 2.5)  # (under the lower bar: last era's route does not hold it)
    monkeypatch.setattr(RT, "LOCAL_SHARE", s * 2.5)
    assert (min(a, b), max(a, b)) not in _edges(TF.flows_at(_line_ctx(tmp_path), 0, last_routes={key})["routes"])


def test_a_route_is_judged_per_good_against_its_carried_volume(tmp_path):
    """PW-1515: a stretch's strength is its share of one good's volume that travels (not of its group's, not counting goods passed
    between cultures on one cell), so every stretch's strength is at most 1 and a lone good's only road carries all of it."""
    f = TF.flows_at(_line_ctx(tmp_path), 0)
    assert f["routes"] and max(r[2] for r in f["routes"]) <= 1 + 1e-9
    assert max(r[2] for r in f["routes"]) > 0.5  # (a six-cell line: one road carries the whole of some good)


def _seek_line(avail, ask=10.0, cap=400, taker=1):
    """trade_flow._seek on a bare line of five cells 0-1-2-3-4 (each step costs 1), sources at both ends with `avail` people's worth each,
    one taker at `taker` asking `ask`; every edge's mode land, no borders, no towns."""
    n = 5
    off, idx = [0], []
    for i in range(n):
        idx += [j for j in (i - 1, i + 1) if 0 <= j < n]
        off.append(len(idx))
    off, idx = np.array(off, np.int64), np.array(idx, np.int64)
    esrc = np.repeat(np.arange(n), np.diff(off)).astype(np.int64)
    ne = len(idx)
    src = np.array([0, 4], np.int64)
    S = np.zeros(n)
    S[src] = 1.0
    av = np.zeros(n)
    av[src] = avail
    tk_off = np.searchsorted(np.array([taker]), np.arange(n + 1)).astype(np.int64)
    rem = np.array([1.0])
    tr = RT.seek_dummy(n, ne)
    out = TF._seek(src, np.zeros(2), off, idx, np.ones(ne), np.full(ne, 50.0), np.zeros(ne, np.int64), np.zeros(ne, np.int32), esrc,
                   1e9, 1e9, tk_off, np.array([0], np.int64), rem, np.array([ask]), np.ones(1, np.bool_), cap, av, av.copy(), S,
                   np.zeros(0, np.int64), np.zeros(0, np.int64), np.zeros(0), np.array([0, -1, -1, -1, 1], np.int64), np.array([2], np.int64),
                   np.zeros(1), False, RT.LONG_KM, *tr)
    return out, rem, tr


def test_a_taker_looks_on_to_the_next_source_when_its_own_runs_dry():
    """PW-1519 (one shared walk): a taker takes from its nearest source; when that one runs dry it stops spreading, and the taker draws on
    the next best live source, along that source's own way, until its lack is met or no source is left."""
    (dp, do, dg, dkm, *_, mx, deaths, _), rem, tr = _seek_line(np.array([3.0, 100.0]))
    assert do.tolist() == [0, 4] and np.allclose(dg, [3.0, 7.0]) and abs(rem[0]) < 1e-9
    assert mx == 2 and deaths == 1
    assert np.allclose(dkm, [50.0, 150.0])  # (the second delivery came the long way, from cell 4)
    eall = tr[4]
    assert eall.sum() == pytest.approx(3.0 * 1 + 7.0 * 3)  # (each delivery traced over the edges it crossed when it was made)
    (dp, do, dg, *_), rem, _ = _seek_line(np.array([3.0, 4.0]))
    assert np.allclose(dg, [3.0, 4.0]) and rem[0] == pytest.approx(0.3)  # (both dry: what is left stays unmet)
    (dp, do, dg, *_, mx, _, capped), rem, _ = _seek_line(np.array([3.0, 100.0]), cap=1)
    assert len(dg) == 1 and mx == 1 and capped == 1  # (the safety cap: sources per taker)


def test_every_good_looks_on_until_none_is_left(tmp_path):
    """PW-1519: every good's allocation runs to the end in one shared walk; the most sources a taker drew from is recorded per good."""
    f = TF.flows_at(_line_ctx(tmp_path), 0)
    assert all(0 <= v <= TF.SEEK_CAP for v in f["rounds"].values()) and f["rounds"]["grain"] >= 1


def test_a_town_pools_its_hinterland_and_its_goods_leave_from_the_town(tmp_path, monkeypatch):
    """PW-1514 (D64: towns are the hubs): cells within POOL_HOPS spacings join their nearest town's market; inside the pool spare goods
    meet wants first, and what is left travels from the town. A pool ends at the cap."""
    ctx = _with_town(_line_ctx(tmp_path), tmp_path, cell=2)
    fr = TF._Frame(ctx, 0, None, None)
    po = fr.pools()
    assert po is not None and po["org"][2] == 2 and po["org"][1] == 2 and po["org"][3] == 2  # (the town and its neighbours)
    assert po["org"][5] == -1  # (three spacings away: beyond the cap)
    f = TF.flows_at(ctx, 0)
    monkeypatch.setattr(TF, "POOL", False)
    g = TF.flows_at(ctx, 0)
    vol = lambda x: sum(r[3] for r in x["flows"]) + sum(sum(v.values()) for v in x["home"].values())  # noqa: E731
    assert vol(f) > 0 and vol(g) > 0
    # goods from the pool that travel leave from the town: no route stretch inside the pool except those touching the town
    assert all(2 in (a, b) or max(a, b) > 3 or min(a, b) < 1 for a, b, *_ in f["routes"])


def test_a_worn_way_is_cheaper_on_land_for_every_good(tmp_path):
    """PW-1515 (Tobler 1993: off a path one walks at 3/5 of the pace on it; Helbing et al. 1997): a land stretch worn by traffic costs
    up to TRAIL less, for every class of goods, and rivers and seas are not worn."""
    fr = TF._Frame(_line_ctx(tmp_path), 0, None, None)
    c0 = {cl: fr.cost(cl)[0].copy() for cl in ("bulk", "middling", "precious")}
    fr.set_wear(np.full(len(fr.ukey), 1e6 * TF.WEAR_HALF))  # (saturated)
    for cl, c in c0.items():
        c1, mode, _ = fr.cost(cl)
        land = (c > 0) & (mode == 0) & ~fr.e["bord"]
        assert land.any() and np.allclose(c1[land], c[land] * (1 - TF.TRAIL), rtol=1e-4)
    fr.set_wear(None)
    assert np.array_equal(fr.cost("bulk")[0], c0["bulk"])


def test_the_walks_wear_the_ways_and_pass_the_wear_on(tmp_path, monkeypatch):
    """PW-1515 (switch TRUNK, off by default, step3c.md): a frame walks at most TRUNK_ITERS times, wearing the ways its goods took; its
    worn ways (as shares of its carried goods) reach the next era at WEAR_KEEP."""
    monkeypatch.setattr(TF, "TRUNK", True)
    ctx = _line_ctx(tmp_path)
    f = TF.flows_at(ctx, 0)
    k, v = f["_wear"]
    assert 1 <= f["walks"] <= TF.TRUNK_ITERS and len(k) and (v > 0).all() and v.max() <= 1 + 1e-9
    g = TF.flows_at(ctx, 0, last_wear=(k, v))
    assert g["routes"] and g["walks"] >= 1


def test_routes_split_into_long_haul_and_local(tmp_path, monkeypatch):
    """PW-1515 (Daniel 11-08: the dense web is real local exchange): the long-haul layer (precious goods, or goods carried LONG_KM or
    more) and the local one are each judged against their own volume; a stretch may be a route of either or both (layers 1, 2, 3)."""
    ctx = _with_town(_line_ctx(tmp_path), tmp_path, cell=2)
    f = TF.flows_at(ctx, 0)
    assert f["routes"] and all(len(r) == 10 and r[5] in (1, 2, 3) for r in f["routes"])
    assert all((r[6] > 0) == bool(r[5] & 1) and (r[8] > 0) == bool(r[5] & 2) and r[2] == max(r[6], r[8]) for r in f["routes"])
    monkeypatch.setattr(RT, "LONG_KM", 0.0)  # (everything carried is long-haul: no local layer)
    g = TF.flows_at(ctx, 0)
    assert g["routes"] and all(r[5] == 1 for r in g["routes"])
    monkeypatch.setattr(RT, "LONG_KM", 1e9)  # (only the precious goods are long-haul)
    h = TF.flows_at(ctx, 0)
    longs = {k for k in RT.GROUP_OF if RT.long_good(k)}
    assert all(not r[5] & 1 or any(RT.GROUP_OF[k] == r[7] for k in longs) for r in h["routes"])
    assert all(isinstance(x["long"], bool) for x in f["hubs"])
    for x in f["hubs"]:
        assert all(len(y) == 7 for y in RT.culture_hubs(f, x["culture"]))


def test_a_town_only_the_local_web_passes_is_a_market_town_without_quarters(tmp_path):
    """PW-1530 (ruling A): a trading town needs a long-haul route through it, and merchant quarters follow it; a town on local routes only
    stays a market town."""
    ctx = _line_ctx(tmp_path)
    town = _with_town(_line_ctx(tmp_path), tmp_path, cell=1)
    h = TF.flows_at(town, 0)["hubs"]
    assert h and all(not x["trading"] and x["kind"] == "market town" and not x["quarters"] for x in h)
    del ctx


def test_a_port_call_costs_loading_unloading_and_dues(tmp_path, monkeypatch):
    """PW-1529: where goods go from land onto the sea they pay LOAD_DAYS of a ship's time, where they come ashore UNLOAD_DAYS and the
    harbour's due; without HANDLE the per-km cost alone."""
    import planet.lineages.trade_flow as TF2
    from planet.lineages import trade as TR
    monkeypatch.setattr(TR, "is_land", lambda e, ice: (np.asarray(e) > 0) & ~np.asarray(ice))  # (six cells are no sphere grid)
    know = {"herder": ["herding", "animal_cattle", "salting", "sails"], "farmer": ["cultivation", "crop_wheat", "salting", "sails"],
            "forager": ["ornament", "sails"]}
    fr = TF._Frame(_line_ctx(tmp_path, elev=[100.0, 100.0, -200.0, 100.0, 100.0, 100.0], know=know), 0, None, None)  # (cell 2 is sea)
    e = fr.e
    assert not (e["load"] & e["unload"]).any()
    c1 = fr.cost("bulk")[0].copy()
    TF2.HANDLE = False
    try:
        fr.costs = {}
        c0 = fr.cost("bulk")[0]
    finally:
        TF2.HANDLE = True
    sea_e = (fr.cost("bulk")[1] == 2) & (c1 >= 0)
    ld, ul = sea_e & e["load"], sea_e & e["unload"]
    assert ld.any() and ul.any()
    if ld.any():
        assert np.allclose(c1[ld] - c0[ld], TF2.LOAD_DAYS * TF2.DAY_KM * TF2.SEA)
    if ul.any():
        assert np.allclose(c1[ul] - c0[ul], TF2.UNLOAD_DAYS * TF2.DAY_KM * TF2.SEA - fr.L["bulk"] * np.log1p(-TF2.HARBOUR_DUE))
    assert np.array_equal(c1[~(ld | ul)], c0[~(ld | ul)])


def test_a_made_good_is_made_in_towns_where_its_know_how_and_input_are(tmp_path):
    """PW-1522: silk is made by a town's people (the town share) from farmland, once silk is known; a town that does not know it lacks
    it once someone can make it, and land without a town makes none."""
    from planet.lineages import trade as TR
    know = {"herder": ["herding", "animal_cattle", "salting"], "farmer": ["cultivation", "crop_wheat", "salting", "silk", "weaving"],
            "forager": ["ornament"]}
    led = {}
    other = {**know, "farmer": ["cultivation", "crop_wheat", "salting"], "herder": know["herder"] + ["silk", "weaving"]}  # (silk known, not by the town)
    for k, kn in enumerate((know, other, {**know, "farmer": ["cultivation", "crop_wheat", "salting"]})):
        d = tmp_path / str(k)
        d.mkdir()
        ctx = _with_town(_line_ctx(d, know=kn), d, cell=2, pop=10 ** 9)  # (a town that is most of its cell)
        ctx.meta["techtree"]["techs"] += [{"id": "silk"}, {"id": "weaving"}]
        led[k] = TR.ledger_at(ctx, 0)
    assert led[0][1]["surplus"].get("silk", 0) > 0 and led[0][1]["lack"].get("silk", 0) == 0  # (the farmers' town makes it)
    assert led[0][0]["surplus"].get("silk", 0) == 0 and led[0][2]["surplus"].get("silk", 0) == 0  # (no town, no workshop)
    assert led[1][1]["surplus"].get("silk", 0) == 0 and led[1][1]["lack"].get("silk", 0) > 0  # (a town without the know-how wants it)
    assert led[2][1]["lack"].get("silk", 0) == 0  # (nobody can make it yet: nobody wants it)
