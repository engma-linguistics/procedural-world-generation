"""Bought-in foods in the culinary brief (PW-1505, bought_in.py): read from a hand-made exchange doc, no run needed."""

from types import SimpleNamespace as NS

import pytest

from planet.lineages import bought_in as BI
from planet.lineages import cuisine as CZ
from planet.lineages import spec as SP

CULT = [{"name": "herders of the steppe", "people": "human", "end": None, "into": None, "ended_kyr": None, "born_kyr": 12.0},
        {"name": "farmers of the river", "people": "human", "end": None, "into": None, "ended_kyr": None, "born_kyr": 12.0},
        {"name": "dwarves of the hills", "people": "dwarf", "end": None, "into": None, "ended_kyr": None, "born_kyr": 12.0},
        {"name": "vintners of the coast", "people": "elf", "end": None, "into": None, "ended_kyr": None, "born_kyr": 12.0},
        {"name": "red dragons of the peak", "people": "red_dragon", "end": None, "into": None, "ended_kyr": None, "born_kyr": 12.0},
        {"name": "aarakocra of the cliffs", "people": "aarakocra", "end": None, "into": None, "ended_kyr": None, "born_kyr": 12.0}]
LINES = [{"id": p, "name": p + "s"} for p in ("human", "dwarf", "elf", "red_dragon", "aarakocra")]


def _ctx():
    return NS(cultures=lambda: {"cultures": CULT}, lines=LINES, idx={x["id"]: k for k, x in enumerate(LINES)},
              meta={"crops": {"stocks": {"vine": {"label": "grapes and vines"}, "wheat": {"label": "wheat and barley"}}}})


def _doc():
    # flows: [giver, taker, good, share of the taker's people, people, km, cost-km, mode, kind, via]
    f0 = {"frame": 5, "ago_kyr": 0.0, "home": {"0": {"grain": 0.03}}, "unmet": {"0": {"grain": 0.2}},
          "flows": [[1, 0, "grain", 0.30, 3000, 240, 300, "river", "market", None],
                    [2, 0, "salt", 0.12, 1200, 420, 500, "land", "merchant", None],
                    [3, 0, "oil_wine", 0.08, 800, 900, 400, "sea", "merchant", None],
                    [3, 0, "gold", 0.40, 4000, 900, 400, "sea", "merchant", None],  # (not a food: left out)
                    [1, 0, "grain", 0.005, 50, 900, 400, "sea", "market", None],  # (under SHOW_MIN: not named)
                    [0, 1, "livestock", 0.10, 900, 300, 100, "land", "barter", None],
                    [1, 4, "grain", 0.25, 10, 0, 0, "local", "tribute", None],
                    [1, 0, "firewood", 0.06, 600, 80, 90, "river", "market", None]],
          "flyer_foods": [{"culture": 5, "crop": "vine", "from": "wild", "cells": [1, 2], "to": [[0, 2]]}]}
    f1 = {**f0, "frame": 4, "ago_kyr": 0.5}
    return {"cultures": [{"name": c["name"], "people": c["people"]} for c in CULT], "frames": [f1, f0]}


@pytest.fixture(autouse=True)
def _crops(monkeypatch):
    grows = {3: {"olive": 0.6, "vine": 0.4, "date_palm": 0.1}, 1: {"wheat": 0.9}}
    monkeypatch.setattr(BI, "_giver_crops", lambda ctx, frame, era, giver, cache: grows.get(giver, {}))


def test_foods_givers_and_roads_from_the_exchange():
    """Only foods (and firewood for the fuel line); most people supplied first; each giver with its km and the road a cook would name:
    river, a caravan (merchants over land), droves (herd animals walk), tribute; a giver under SHOW_MIN is not named."""
    r = BI.of_culture(_ctx(), _doc(), 0, 0.0)
    goods = [fd["good"] for fd in r["foods"]]
    assert goods == ["grain", "salt", "oil_wine"] and "gold" not in goods
    gr = r["foods"][0]
    assert gr["share"] == pytest.approx(0.305) and gr["unmet"] == 0.2 and gr["home"] == 0.03
    assert len(gr["givers"]) == 1 and gr["givers"][0]["name"] == "farmers of the river" and gr["givers"][0]["road"] == "river"
    assert r["foods"][1]["givers"][0]["road"] == "caravan"
    assert [x["good"] for x in r["fuel"]] == ["firewood"]
    assert "farmers of the river (240 km by river, 30%)" in r["text"] and "20% go without" in r["text"]
    assert "salt from dwarves of the hills (420 km by caravan, 12%)" in r["text"]
    farmers = BI.of_culture(_ctx(), _doc(), 1, 0.0)
    assert farmers["foods"][0]["givers"][0]["road"] == "droves"
    dragons = BI.of_culture(_ctx(), _doc(), 4, 0.0)
    assert dragons["foods"][0]["givers"][0]["road"] == "tribute" and dragons["text"].startswith("takes as tribute grain from farmers of the river")
    assert BI.of_culture(_ctx(), _doc(), 0, 3.0) is None  # (outside the land-use window)
    assert BI.of_culture(_ctx(), None, 0, 0.0) is None
    assert BI.frame_of(_doc(), 0.4)["ago_kyr"] == 0.5


def test_the_givers_fields_name_the_crop_good_and_the_drink():
    """Oil and wine from a giver that grows the vine and olives is "olive oil and wine"; wine enters the drink line only where the culture
    does not grow the vine itself; herders' grain enters the staple line; flyers' crops are flown in."""
    r = BI.of_culture(_ctx(), _doc(), 0, 0.0)
    ow = next(fd for fd in r["foods"] if fd["good"] == "oil_wine")
    assert ow["givers"][0]["what"] == ["olive oil", "wine"] and "olive oil and wine from vintners of the coast (900 km by sea, 8%)" in r["text"]
    assert BI.drink_note(r, set()) == ["wine bought in from vintners of the coast (900 km by sea, 8%)",
                                       "date wine bought in from vintners of the coast (900 km by sea, 8%)"]  # (the giver's main crop first)
    assert BI.drink_note(r, {"vine", "date_palm"}) == []
    assert BI.staple_note(r).startswith("grain bought in from farmers of the river")
    assert "firewood and charcoal bought in from farmers of the river (80 km by river, 6%)" == BI.fuel_note(r)
    assert r["flown_in"][0]["by_name"] == "aarakocra of the cliffs" and "grapes and vines (not grown here), flown in by aarakocra" in r["text"]


def test_the_sheet_carries_the_bought_in_line():
    """The cuisine sheet's staple, drink and fuel lines and its markdown read the brief's trade_reach."""
    r = BI.of_culture(_ctx(), _doc(), 0, 0.0)
    p = {"id": 0, "name": "herders", "people": "human", "people_name": "humans", "body": dict(SP.BODY_DEFAULT),
         "ways": {"farm": 0.0, "herd": 0.8, "forage": 0.2, "density_km2": 1.0}, "know": {"fermentation"}, "crops": {}, "staple_crops": [],
         "herds": {"horse": 0.5}, "dairy": None, "fuel": "dung", "faith": None, "taboos": [], "food_taboos": [], "forbidden": [], "cells": 10,
         "traits": {}, "off_ladder": False, "coastal": False}
    ctx = NS(meta={"techtree": {"techs": [{"id": "fermentation"}]}, "animals": {"stocks": {"horse": {"label": "horses"}}}, "crops": {"stocks": {}}})
    st = CZ.staple(ctx, {"fish": {}}, p, r)
    assert "grain bought in from farmers of the river" in st["text"] and st["parts"][-1]["kind"] == "bought"
    assert "wine bought in" in CZ.drink(ctx, {"land": {"koppen": {}}}, p, r)["text"]
    assert "firewood and charcoal bought in" in CZ.fuel(ctx, {"fuels": {"lead": {"dung": 0.8}}}, p, r)["text"]
    assert "bought in" not in CZ.staple(ctx, {"fish": {}}, p)["text"]  # (no exchange: no note)
    assert CZ.bought_in(r)["text"] == r["text"] and CZ.bought_in(None) is None
