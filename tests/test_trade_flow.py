"""Trade step 2 (PW-1503): goods move between neighbours. Each rule on a hand-made line of six cells (test_trade's world), no run needed."""

from types import SimpleNamespace as NS

import numpy as np
import pytest

from planet.geo import R_KM
from planet.lineages import trade as TR
from planet.lineages import trade_flow as TF
from tests.test_trade import N, _ctx

HOP_KM = 50.0  # (a step between the line's cells: 50 path-km)


def _line_ctx(tmp_path, nav=None, elev=None, **kw):
    """test_trade's six cells (herders 0-1, farmers 2-3, foragers 4-5) strung on a line 0-1-2-3-4-5, with rivers and a world."""
    ctx = _ctx(tmp_path, **kw)
    off, idx = [0], []
    for i in range(N):
        idx += [j for j in (i - 1, i + 1) if 0 <= j < N]
        off.append(len(idx))
    ctx.g = NS(n=N, nbr_off=np.array(off, np.int64), nbr_idx=np.array(idx, np.int64), spacing=HOP_KM / (R_KM * TF.ROUTE))
    e = np.asarray(elev if elev is not None else [100.0] * N, float)
    arrs = {"elevation": e, "ice": np.zeros(N), "crop_known": np.array([0, 0, 1, 1, 1, 0]), "animal_known": np.array([2, 2, 2, 2, 0, 0])}
    ctx.f = lambda name, i: arrs[name]
    ctx.world = {"river_nav": np.asarray(nav if nav is not None else [0] * N), "flow": np.zeros(N)}
    ctx.meta["era"] = "bronze age"
    ctx._arrs = arrs
    return ctx


def _flows(ctx, **kw):
    return TF.flows_at(ctx, 0, **kw)["flows"]


def _get(fl, giver, taker, good):
    return next((x for x in fl if (x[0], x[1], x[2]) == (giver, taker, good)), None)


def test_herders_get_grain_from_the_farmers_next_door(tmp_path):
    """Khazanov: herders are not self-sufficient; their grain comes from the farmers beside them, overland, by barter."""
    fl = _flows(_line_ctx(tmp_path))
    x = _get(fl, 1, 0, "grain")
    assert x is not None and x[3] > 0.1 and x[5] > 0 and x[7] == "land" and x[8] == "barter"
    assert _get(fl, 0, 1, "salt") is not None  # (the salt bed in the herders' cell 0 goes to the farmers, whose cell 3 is far from salt)


def test_supply_falls_off_with_the_cost_of_carrying_it(tmp_path):
    """Renfrew: exp(-cost / L) beyond the source; bulk falls faster than precious goods over the same ground."""
    fr = TF._Frame(_line_ctx(tmp_path), 0, None, None)
    sup, org, km, *_ = fr.walk("grain")
    assert sup[1] > sup[0] > 0 and km[0] > km[1]  # (grain from cell 2: 50 km to cell 1, 100 km to cell 0)
    bulk, prec = fr.cost("bulk")[0], fr.cost("precious")[0]
    inside = ~fr.e["bord"]
    assert np.allclose(bulk[inside], prec[inside])  # (the same ground ...; a border's toll is a share of the value, so it costs L x ...)
    toll = fr.e["bord"]
    assert np.allclose(np.exp(-(bulk[toll] - fr.e["hop"] * fr.e["fac"][toll]) / TF.FALL_KM["bulk"]),
                       np.exp(-(prec[toll] - fr.e["hop"] * fr.e["fac"][toll]) / TF.FALL_KM["precious"]))
    assert TF.FALL_KM["bulk"] < TF.FALL_KM["middling"] < TF.FALL_KM["precious"]  # (... but the light goods fall off slower)


def test_rivers_carry_cheaper_downstream_once_canoes_are_known(tmp_path):
    know = {"herder": ["herding", "animal_cattle", "salting", "copper", "native_copper", "bronze", "quarrying", "canoes"],
            "farmer": ["cultivation", "crop_wheat", "salting", "copper", "native_copper", "bronze", "quarrying", "canoes"], "forager": ["ornament"]}
    ctx = _line_ctx(tmp_path, nav=[1] * N, elev=[10.0, 20.0, 30.0, 40.0, 50.0, 60.0], know=know)  # (the river runs down to cell 0)
    c, mode, _ = TF._Frame(ctx, 0, None, None).cost("bulk")
    a = np.repeat(np.arange(N), np.diff(ctx.g.nbr_off))
    b = ctx.g.nbr_idx
    down = c[(a == 2) & (b == 1)][0]
    up = c[(a == 1) & (b == 2)][0]
    foot = TF._Frame(_line_ctx(tmp_path), 0, None, None).cost("bulk")[0][(a == 2) & (b == 1)][0]
    assert down < up < foot and mode[(a == 2) & (b == 1)][0] == 1
    x = _get(TF.flows_at(ctx, 0)["flows"], 1, 0, "grain")
    assert x[7] == "river"


def test_a_war_closes_the_border_and_tolerance_lowers_the_toll(tmp_path):
    ctx = _line_ctx(tmp_path)
    pol = {"step_kyr": 0.1, "steps": [{"ago": 0.1}, {"ago": 0.0}], "cultures": {},
           "polities": [{"id": 0, "took": [[0.0, 1, "war"]], "rulers": []}, {"id": 1, "took": [], "rulers": []}],
           "maps": [[[0, 0, [0, 2], {}, 0], [1, 0, [2, 4], {}, 0]], [[0, 0, [0, 2], {}, 0], [1, 0, [2, 4], {}, 0]]]}
    fl = _flows(ctx, pol=pol)
    assert _get(fl, 1, 0, "grain") is None  # (the herders' polity is at war with the farmers': no grain crosses)
    ctx = _line_ctx(tmp_path)
    fr_lo = TF._Frame(ctx, 0, None, {"cultures": {"0": {"now": [0.1, 0]}, "1": {"now": [0.1, 0]}, "2": {"now": [0.1, 0]}}})
    fr_hi = TF._Frame(ctx, 0, None, {"cultures": {"0": {"now": [0.9, 0]}, "1": {"now": [0.9, 0]}, "2": {"now": [0.9, 0]}}})
    assert fr_hi.walk("grain")[0][0] > fr_lo.walk("grain")[0][0]


def test_supply_is_shared_not_copied(tmp_path):
    """A source gives at most its surplus: the takers' imports (in people) never sum to more than the givers' surplus (in people)."""
    ctx = _line_ctx(tmp_path)
    fl = _flows(ctx)
    P = TR.pairs_at(ctx, 0)
    X = TR.cells_at(ctx, 0)
    for good in ("grain", "copper", "livestock"):
        given = sum(x[3] * P["wsum"][x[1]] for x in fl if x[2] == good)
        have = float((P["surplus"][good] * X["heads"][P["cell"]]).sum())
        assert given <= have * (1 + 1e-6)


def test_flyers_carry_light_goods_over_anything_but_not_grain(tmp_path, monkeypatch):
    """D65 A: a flying people pays a flat cost over any ground or sea, for light (precious) goods only."""
    ctx = _line_ctx(tmp_path, extra_lines=("aarakocra",))
    ctx.lines[3]["traits"] = ["flies"]
    ctx.cultures()["deme_culture"] = [0, 1, 2, 3]
    ctx.arr["demes"] = [np.array([0, 0, 1, 1, 3, 2], np.uint16)]  # (the flyers hold cell 4)
    ctx._arrs["ice"] = np.array([0.0, 0.0, 0.0, 1.0, 0.0, 0.0])  # (cell 3 is under ice: no one walks it)
    fr = TF._Frame(ctx, 0, None, None)
    a = np.repeat(np.arange(N), np.diff(ctx.g.nbr_off))
    b = ctx.g.nbr_idx
    e = (a == 3) & (b == 4)
    assert fr.cost("bulk")[0][e][0] < 0 and fr.cost("precious")[0][e][0] > 0 and fr.cost("precious")[1][e][0] == 3


def test_dragons_take_tribute_and_their_kobolds_trade_for_them(tmp_path):
    """D65: a dragon realm takes food and its hoard from the peoples on its land (tribute); its own surplus goes out via its kobolds."""
    ctx = _line_ctx(tmp_path, extra_lines=("red_dragon",), present={"megafauna": {"red_dragon": {}}},
                    goods={"salt": np.array([1.0, 0.0, 0.0, 0.0, 0.0, 1.0])}, know={"herder": ["herding", "salting"], "farmer": ["cultivation", "crop_wheat", "gold_silver"], "forager": ["ornament"], "red_dragon": ["salting"]})
    ctx.cultures()["deme_culture"] = [0, 1, 2, 3]
    cells = np.array([0, 1, 2, 3, 4, 5, 2, 3, 5], np.int64)
    dem = np.array([0, 0, 1, 1, 2, 2, 3, 3, 3], np.uint16)  # (the dragon over the farmers' cells 2-3 and the salt of cell 5)
    ctx.overlap = lambda: ({"offsets": np.array([[0, len(cells)]]), "cells": cells}, dem)
    fl = _flows(ctx)
    t = _get(fl, 1, 3, "grain")
    assert t is not None and t[8] == "tribute" and t[7] == "local"
    out = [x for x in fl if x[0] == 3]
    assert out and all(x[9] == "kobolds" for x in out)


def test_flyers_record_the_foods_they_carry_where_they_are_not_grown(tmp_path):
    """Daniel (D65): flyers carry foods to new regions, as birds have; recorded for step 4a and the crop spread, nothing is spread."""
    know = {"herder": ["herding"], "farmer": ["cultivation", "crop_wheat"], "forager": ["ornament"], "aarakocra": ["crop_wheat", "cultivation"]}
    ctx = _line_ctx(tmp_path, extra_lines=("aarakocra",), know=know)
    ctx.lines[3]["traits"] = ["flies"]
    ctx.cultures()["deme_culture"] = [0, 1, 2, 3]
    cells = np.array([0, 1, 2, 3, 4, 5, 5], np.int64)
    dem = np.array([0, 0, 1, 1, 2, 2, 3], np.uint16)  # (the flyers live in cell 5; wheat is not known in cells 0, 1 and 5)
    ctx.overlap = lambda: ({"offsets": np.array([[0, len(cells)]]), "cells": cells}, dem)
    ctx._arrs["crop_known"] = np.array([0, 0, 1, 1, 0, 0])
    ff = TF.flows_at(ctx, 0)["flyer_foods"]
    rec = next(r for r in ff if r["crop"] == "wheat")
    assert rec["culture"] == 3 and 4 in rec["cells"] and 0 not in rec["cells"]  # (cell 4 is next to the flyers and farmed by foragers' neighbours)


def test_derive_views_and_food_bought(tmp_path):
    ctx = _line_ctx(tmp_path)
    ctx.meta["eraq"]["frames"] = [0]
    ctx.dir = tmp_path
    doc = TF.derive(tmp_path, ctx)
    assert doc["frames"] and doc["format"] == TF.FORMAT
    assert 0 < TF.food_bought(doc, 0, 0.0) <= 1
    C = [{"name": "a", "end": None, "into": None, "ended_kyr": None, "born_kyr": 100.0}] * 3
    rows = TF.culture_view(doc, 0, C)
    assert rows[0]["from"]["grain"][0][0] == 1 and rows[0]["partners"][0][0] == 1


def test_constants_are_the_sourced_ratios():
    """R§6 (ORBIS): sea : river down : river up : pack : wagon = 1 : 3.4 : 6.8 : 28 : 35."""
    assert TF.SEA * 28 == pytest.approx(1.0) and TF.RIVER_DOWN * 28 == pytest.approx(3.4) and TF.RIVER_UP * 28 == pytest.approx(6.8)
    assert TF.CART * 28 == pytest.approx(35) and TF.HILL == pytest.approx(2.12, abs=0.01)
    assert 250 < TF.FALL_KM["bulk"] < 330 and 400 < TF.FALL_KM["middling"] < 470
