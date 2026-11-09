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
