"""PW-905 food fit per body and PW-835 the new herd animals."""

import numpy as np

from planet.lineages import animal_defs as AD
from planet.lineages import food_fit as FF
from planet.lineages import spec as SP


def test_fit_levels_follow_the_body():
    human = FF.fit({})
    assert human["fresh_milk"]["level"] == "poor" and human["soured_dairy"]["level"] == "tolerates"
    assert human["alcohol"]["level"] == "tolerates" and human["alliums"]["level"] == "tolerates"
    assert FF.fit({"milk": True})["fresh_milk"]["level"] == "thrives"
    assert FF.fit({"milk": 0.3})["fresh_milk"]["level"] == "tolerates"
    cat = FF.fit({"sweet": False, "diet": "obligate_carnivore", "raw_meat": True, "toxic": ["alliums", "theobromine"]})
    assert cat["sweet"]["level"] == "poor" and cat["raw_meat"]["level"] == "thrives"
    assert cat["alliums"]["level"] == cat["cacao"]["level"] == "harmful" and cat["alcohol"]["level"] == "poor"
    bird = FF.fit({"capsaicin": False, "toxic": ["alliums", "theobromine"]})
    assert bird["chili"]["level"] == "thrives"  # (some species love what poisons others: the owner's 10-26 ask)
    deer = FF.fit({"diet": "herbivore", "gut": "foregut", "cellulose": True, "grain": "moderate"})
    assert deer["browse"]["level"] == "thrives" and deer["cooked_meat"]["level"] == "poor" and deer["grain"]["level"] == "tolerates"
    for rows in (human, cat, bird, deer):
        assert set(rows) == {k for k, _, _ in FF.FOODS}
        assert all(r["level"] in FF.LEVELS and (r["src"] is None or r["src"] in FF.SOURCES) for r in rows.values())


def test_line_marks_grown_foods_and_fantasy_bodies():
    cat = {"sweet": False, "diet": "obligate_carnivore", "toxic": ["alliums"]}
    s = FF.line(cat, ["alliums", "wheat"])
    assert "onion and garlic (grown here)" in s and "JUDGEMENT" in s
    assert "JUDGEMENT" not in FF.line({}) and "thrives on cooked meat" not in FF.line({})  # (the baseline's strengths go unsaid)


def test_every_preset_body_has_a_fit():
    for name in ("dnd", "seven_meals"):
        t = SP.load(f"planet/lineages/samples/{name}.toml")
        for ln in t.lines.values():
            assert FF.line(ln.body)


def test_new_herd_animals():
    ids = [a.id for a in AD.TABLE]
    assert {"pig", "reindeer", "camel", "llama", "buffalo", "yak"} <= set(AD.REAL_IDS)
    assert sorted(a.bit for a in AD.TABLE) == list(range(len(AD.TABLE))) and len(ids) <= 16  # (uint16 layers)
    assert AD.BY_ID["fowl"].anchor_kyr == 3.5 and AD.BY_ID["horse"].anchor_kyr == 4.2  # (Peters 2022, Librado 2021)
    n = 6
    env = {"temperature": np.array([-10.0, 27.0, 2.0, 25.0, -8.0, 12.0]), "precipitation": np.array([400.0, 2000.0, 400.0, 100.0, 300.0, 800.0]),
           "elevation": np.array([200.0, 50.0, 4000.0, 300.0, 4500.0, 300.0]), "ice": np.zeros(n), "tree_cover": np.array([30.0, 20.0, 5.0, 2.0, 5.0, 50.0])}
    tags = {k: np.zeros(n, bool) for k in ("hills", "mountain", "wetland")}
    land = np.ones(n, bool)
    want = {"reindeer": 0, "buffalo": 1, "llama": 2, "camel": 3, "yak": 4, "pig": 5}  # (each one's cell: taiga, monsoon lowland, puna, desert, plateau, woodland)
    for aid, cell in want.items():
        w = AD.BY_ID[aid].wild(env, tags, land)
        assert w[cell] > 0.5, aid
        assert w[cell] == w.max(), aid  # (yak and llama share the cold high grassland: ties allowed)


def test_authored_fit_flush_and_canid_marker():
    """PW-1607: a preset authors a fit, a flush share and a canid body; the fit table merges down the tree."""
    assert FF.fit({})["alcohol"]["level"] == "tolerates" and FF.fit({})["grapes"]["level"] == "tolerates"
    f = FF.fit({"alcohol_flush": 0.5})["alcohol"]  # (about half of East Asians: ALDH2*2, Wikipedia)
    assert f["level"] == "poor" and f["src"] == "aldh2" and "50%" in f["why"]
    assert FF.fit({"alcohol_flush": 0.36})["alcohol"]["level"] == "tolerates"
    dog = FF.fit({"toxic": ["alliums", "theobromine", "grapes"]})
    assert dog["grapes"]["level"] == "harmful" and dog["grapes"]["src"] == "grapes" and dog["alcohol"]["level"] == "poor"
    row = FF.fit({"toxic": ["alliums"], "fit": {"alcohol": {"level": "tolerates", "why": "canon"}, "chili": "thrives"}})
    assert row["alcohol"] == {"level": "tolerates", "why": "canon", "basis": "authored", "src": None}
    assert row["chili"]["level"] == "thrives" and row["chili"]["basis"] == "authored"
    assert all(r["src"] is None or r["src"] in FF.SOURCES for r in FF.fit({"toxic": ["grapes"], "alcohol_flush": 0.4}).values())


def test_body_fit_parses_and_inherits():
    import pytest
    assert SP.parse_body({"fit": {"alcohol": "poor"}, "alcohol_flush": 0.5}) == {"fit": {"alcohol": "poor"}, "alcohol_flush": 0.5}
    for bad in ({"fit": {"gravy": "poor"}}, {"fit": {"alcohol": "meh"}}, {"alcohol_flush": 1.5}, {"alcohol_flush": True}, {"toxic": ["lead"]}):
        with pytest.raises(ValueError):
            SP.parse_body(bad)
    t = SP.load("planet/lineages/samples/dnd.toml")
    for lid in ("feline", "tabaxi", "leonin"):  # (the owner's canon: cat peoples barely drink; inherited down the tree)
        assert t.lines[lid].body["fit"]["alcohol"]["level"] == "poor", lid
        assert FF.fit(t.lines[lid].body)["alcohol"]["basis"] == "authored"
    assert t.lines["leonin"].body_given == {} and t.lines["feline"].body_given["fit"]
    sv = SP.load("planet/lineages/samples/seven_meals.toml")  # (frozen: no preset line authors a fit, flush or canid marker)
    assert not any(ln.body["fit"] or ln.body["alcohol_flush"] or "grapes" in ln.body["toxic"] for ln in sv.lines.values())
    assert not any(ln.body["alcohol_flush"] or "grapes" in ln.body["toxic"] for ln in t.lines.values())
