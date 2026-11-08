"""Trade step 3 (PW-1504): routes and trading towns; herders fetching grain (PW-1511 B); flyers carrying wild foods (PW-1510). Each rule on
test_trade_flow's hand-made line of six cells, no run needed."""

import json

import numpy as np

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


def test_a_town_on_a_route_is_a_trading_town_and_its_kind_follows_the_modes(tmp_path):
    """A ledger town on a route is a market town; on a river route a river port (review1.md section 5: central places)."""
    h = TF.flows_at(_with_town(_line_ctx(tmp_path), tmp_path), 0)["hubs"]
    assert len(h) == 1 and h[0]["cell"] == 2 and h[0]["kind"] == "market town" and h[0]["place"] == "the ford"
    know = {"herder": ["herding", "animal_cattle", "salting", "copper", "native_copper", "bronze", "quarrying", "canoes"],
            "farmer": ["cultivation", "crop_wheat", "salting", "copper", "native_copper", "bronze", "quarrying", "canoes"], "forager": ["ornament"]}
    ctx = _with_town(_line_ctx(tmp_path, nav=[1] * N, elev=[10.0, 20.0, 30.0, 40.0, 50.0, 60.0], know=know), tmp_path)
    h = TF.flows_at(ctx, 0)["hubs"]
    assert h and h[0]["kind"] == "river port" and "river" in h[0]["modes"]


def test_a_caravan_town_stands_where_pack_routes_leave_farmland_for_steppe(tmp_path):
    """review1.md section 4 (the Sahel towns, the Silk Road oases): pack animals, a farmed town, an unfarmed desert or steppe beyond."""
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


def test_a_merchant_quarter_lifts_its_border_toll_next_era(tmp_path):
    """Curtin's trade diasporas (review1.md section 5); design1.md step 2: a quarter of the giver's people in the taker's town removes the
    border's crossing cost."""
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
    monkeypatch.setattr(RT, "ROUTE_SHARE", s * 1.5)  # (now it sits between the two bars)
    key = min(a, b) * ctx.g.n + max(a, b)
    assert (min(a, b), max(a, b)) not in _edges(TF.flows_at(_line_ctx(tmp_path), 0)["routes"])
    assert (min(a, b), max(a, b)) in _edges(TF.flows_at(_line_ctx(tmp_path), 0, last_routes={key})["routes"])
    monkeypatch.setattr(RT, "ROUTE_SHARE", s * 2.5)  # (under the lower bar: last era's route does not hold it)
    assert (min(a, b), max(a, b)) not in _edges(TF.flows_at(_line_ctx(tmp_path), 0, last_routes={key})["routes"])


def test_a_route_is_judged_per_good_against_its_carried_volume(tmp_path):
    """PW-1515: a stretch's strength is its share of one good's volume that travels (not of its group's, not counting goods passed
    between cultures on one cell), so every stretch's strength is at most 1 and a lone good's only road carries all of it."""
    f = TF.flows_at(_line_ctx(tmp_path), 0)
    assert f["routes"] and max(r[2] for r in f["routes"]) <= 1 + 1e-9
    assert max(r[2] for r in f["routes"]) > 0.5  # (a six-cell line: one road carries the whole of some good)


def test_rewalk_matches_a_fresh_walk_without_the_dead_sources(tmp_path):
    """Grain's rounds (trade_flow.SEEK_GOODS) re-walk only the land of the emptied sources (_rewalk); the costs and origins must be those
    of a fresh walk from the live sources alone."""
    ctx = _line_ctx(tmp_path)
    fr = TF._Frame(ctx, 0, None, None)
    fr.walk("grain")
    src = np.unique(fr._last["org"][fr._last["org"] >= 0])
    dead = np.zeros(N, bool)
    dead[src[:1]] = True
    fr.rewalk("grain", dead, view=False)
    fr2 = TF._Frame(ctx, 0, None, None)
    fr2.walk("grain", live=~dead)
    for k in ("d", "org"):
        a, b = fr._last[k], fr2._last[k]
        assert np.array_equal(np.isfinite(a), np.isfinite(b)) and np.allclose(a[np.isfinite(a)], b[np.isfinite(b)])


def test_grain_takers_look_on_until_a_round_finds_no_more(tmp_path, monkeypatch):
    """Lane 216b: grain's allocation runs until no taker cut short reaches a live source (SEEK_GOODS); with it the grain still unmet is
    never more than with the old 3-round bound, and the rounds used are recorded."""
    f = TF.flows_at(_line_ctx(tmp_path), 0)
    assert f["rounds"]["grain"] >= 1
    monkeypatch.setattr(TF, "SEEK_GOODS", ())
    g = TF.flows_at(_line_ctx(tmp_path), 0)
    un = lambda x: sum(v.get("grain", 0.0) for v in x["unmet"].values())  # noqa: E731
    assert un(f) <= un(g) + 1e-9 and g["rounds"]["grain"] <= TF.ROUNDS


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
