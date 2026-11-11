"""Preservation and flavour per culture (keeping.py, PW-744, PW-1715): each mechanism on small hand-made cultures, no run needed."""

from planet.lineages import keeping as KP
from planet.lineages import spec as SP

TREE = {"smoking_drying", "salting", "pickling", "fermentation", "fermented_dairy", "cheese", "fish_sauce", "cellaring", "lard_rendering",
        "storage", "plant_detox", "beer"}
ALL = set(TREE)


def _brief(koppen=None, cold=5.0, frost=0.0, grow=8.0, precip=700.0, fuel="wood", salt100=0.5, sea=0.0, coast_fish=0.0, tree=30.0):
    return {"land": {"koppen": koppen or {"Cfb oceanic": 1.0}, "coldest_month_c": cold, "frost_months_est": frost, "growing_months": grow,
                     "precipitation_mm": precip, "temperature_c": cold + 12, "elevation_m": {"mean": 200.0}, "tree_cover_pct": tree},
            "salt": {"within_100km_share": salt100, "source_share_of_land": {"sea": sea}, "km_to_salt": {"mean": 50 if salt100 > 0.5 else 400}},
            "fish": {"coast_fish": coast_fish}, "fuels": {"lead": {fuel: 0.6}}, "mining": None}


def _p(farm=0.0, herd=0.0, crops=(), know=ALL, body=None, dairy=None, traits=(), coastal=False):
    return {"ways": {"farm": farm, "herd": herd, "forage": round(1 - farm - herd, 3)}, "crops": {c: 0.5 for c in crops}, "herds": {},
            "know": set(know), "body": {**SP.BODY_DEFAULT, **(body or {})}, "dairy": dairy, "line_traits": list(traits), "coastal": coastal,
            "tree_techs": TREE, "fuel": None}


def _m(r):
    return {m["id"]: m["share"] for m in r["preservation"]["methods"]}


def test_cold_coast_fishers_smoke_and_salt_and_taste_of_it():
    r = KP.of(_brief(cold=-6, frost=5, grow=4, precip=1100, fuel="wood", salt100=1.0, sea=0.9, coast_fish=0.9), _p(coastal=True))
    m = _m(r)
    assert m["smoking"] > 0 and m["salting"] > 0 and max(m, key=m.get) in ("smoking", "salting", "fish_sauce")
    ax = r["flavour"]["axes"]
    assert ax["smoky"]["value"] >= 0.35 and ax["salty"]["value"] >= 0.6 and "coast" in r["flavour"]["descriptor"]
    assert all(v["reasons"] for v in ax.values() if v["value"] > 0)  # (every taste says why)


def test_steppe_dung_herders_sour_their_milk_and_hardly_smoke():
    """culinary-dnd's steppe herders: a dung fire does not smoke; low lactase makes dairy a fermentation culture."""
    d = {"animals": ["horse"], "lactase_share": 0.2, "fresh": False, "cheese": True}
    r = KP.of(_brief(koppen={"BSk cold steppe": 0.9}, cold=-12, frost=6, grow=4, precip=300, fuel="dung"), _p(herd=0.8, dairy=d))
    m = _m(r)
    assert m["ferment_dairy"] > 2 * m.get("smoking", 0.0)
    assert r["flavour"]["axes"]["sour"]["value"] > r["flavour"]["axes"]["smoky"]["value"]


def test_a_raw_meat_low_bitter_body_leans_to_ferments_and_funk():
    """The D&D tree's goblinoid body (raw_meat, bitter low): the same land and food, a ferment-and-raw kitchen."""
    b = _brief(precip=1300, koppen={"Af tropical rainforest": 1.0}, cold=20)
    plain = KP.of(b, _p(farm=0.4, crops=("roots", "greens")))
    gob = KP.of(b, _p(farm=0.4, crops=("roots", "greens"), body={"raw_meat": True, "bitter": "low"}))
    assert _m(gob)["ferment_veg"] > 1.5 * _m(plain)["ferment_veg"]
    assert gob["flavour"]["axes"]["funk"]["value"] > plain["flavour"]["axes"]["funk"]["value"]
    assert "raw-food" in gob["flavour"]["descriptor"]


def test_techs_gate_methods_and_a_tree_without_them_does_not():
    r = KP.of(_brief(salt100=1.0, coast_fish=0.8), _p(know=ALL - {"salting", "fish_sauce"}, coastal=True))
    assert "salting" not in _m(r) and {a["id"] for a in r["preservation"]["absent"]} >= {"salting", "fish_sauce"}
    p = _p(know=set(), coastal=True)
    p["tree_techs"] = None
    assert "salting" in _m(KP.of(_brief(salt100=1.0, coast_fish=0.8), p))


def test_the_body_shapes_taste():
    b = _brief()
    crops = ("cane", "tree_fruit", "chili")
    assert KP.of(b, _p(farm=0.6, crops=crops, body={"sweet": False}))["flavour"]["axes"]["sweet"]["value"] == 0.0
    hot = KP.of(b, _p(farm=0.6, crops=crops))["flavour"]["axes"]["hot"]["value"]
    assert KP.of(b, _p(farm=0.6, crops=crops, body={"capsaicin": False}))["flavour"]["axes"]["hot"]["value"] < hot
    nofire = KP.of(b, _p(body={"fire": False}))
    assert "smoking" not in _m(nofire)


def test_shares_are_of_all_food_and_bounded():
    for r in (KP.of(_brief(), _p()), KP.of(_brief(cold=-20, frost=8, grow=2), _p(herd=0.6)), KP.of(_brief(), _p(farm=0.9, crops=("wheat",)))):
        k = r["preservation"]
        assert 0.05 <= k["preserved_share"] <= 0.75 or not k["methods"]
        assert abs(sum(m["share"] for m in k["methods"]) - k["preserved_share"]) < 0.02
        assert all(0 <= v["value"] <= 1 for v in r["flavour"]["axes"].values())
    farm = KP.of(_brief(), _p(farm=0.9, crops=("wheat",)))
    assert "ferment_grain" in _m(farm) and "drying" in _m(farm)


def test_a_people_that_knows_no_keeping_eats_fresh_and_a_meat_eater_gathers_no_greens():
    p = _p(know=set(), body={"diet": "carnivore"})
    r = KP.of(_brief(tree=80.0), p)
    k = r["preservation"]
    assert not k["methods"] and k["preserved_share"] == 0.0 and "fresh" in k["text"]
    assert r["flavour"]["axes"]["herbal"]["value"] < KP.of(_brief(tree=80.0), _p(know=set()))["flavour"]["axes"]["herbal"]["value"]


# -- PW-1727: bought-in food reaches the profile ---------------------------------------------------------------------------------
def _bought(*goods, share=0.08, crops=()):
    return {"foods": [{"good": g, "label": g.replace("_", " "), "share": share, "unmet": 0.0, "home": 0.0,
                       "givers": [{"name": "the salt-sellers of the coast", "share": share, "road": "river", "crops": list(crops), "what": []}]}
                      for g in goods]}


def test_bought_salt_raises_salting_and_says_so():
    b = _brief(salt100=0.05, coast_fish=0.0)
    p = _p(herd=0.5, farm=0.3, crops=("wheat", "greens"))
    plain = KP.of(b, p)
    bought = KP.of({**b, "trade_reach": _bought("salt")}, p)
    assert bought["flavour"]["axes"]["salty"]["value"] > plain["flavour"]["axes"]["salty"]["value"]
    assert _m(bought)["salting"] > _m(plain)["salting"]
    sw = " ".join(bought["flavour"]["axes"]["salty"]["reasons"])
    assert "bought in from the salt-sellers of the coast" in sw and "salt far on its own land" in sw
    assert any("bought in" in r for r in next(m for m in bought["preservation"]["methods"] if m["id"] == "salting")["reasons"])
    assert "bought in" not in " ".join(plain["flavour"]["axes"]["salty"]["reasons"])


def test_bought_spice_sugar_and_oil_add_their_tastes_but_tribute_does_not():
    b, p = _brief(), _p(farm=0.6, crops=("wheat",))
    plain = KP.of(b, p)["flavour"]["axes"]
    r = KP.of({**b, "trade_reach": _bought("spices", "sugar", "oil_wine", crops=("spice_tree", "cane", "olive"))}, p)["flavour"]["axes"]
    assert r["hot"]["value"] > plain["hot"]["value"] and any("bought in" in x for x in r["hot"]["reasons"])
    assert r["sweet"]["value"] > plain["sweet"]["value"] and r["fatty"]["value"] > plain["fatty"]["value"]
    tr = _bought("spices")
    tr["foods"][0]["givers"][0]["road"] = "tribute"
    assert KP.of({**b, "trade_reach": tr}, p)["flavour"]["axes"]["hot"]["value"] == plain["hot"]["value"]
    tiny = KP.of({**b, "trade_reach": _bought("spices", share=0.005)}, p)["flavour"]["axes"]
    assert tiny["hot"]["value"] == plain["hot"]["value"]  # (below BOUGHT_MIN)


def test_bought_salt_stays_dearer_than_ones_own():
    r = KP.inputs({**_brief(salt100=0.0), "trade_reach": _bought("salt", share=0.9)}, _p())
    assert r["salt"] <= KP.BOUGHT_SALT_CAP and r["own_salt"] == 0.0


# -- PW-1728: a kind's authored leanings ------------------------------------------------------------------------------------------
def test_authored_leanings_scale_methods_and_the_kept_share_with_a_reason():
    b = _brief(cold=-2, frost=3, grow=6, precip=900)
    base = _p(farm=0.6, crops=("wheat", "greens", "tree_fruit"))
    plain = KP.of(b, base)
    elf = KP.of(b, {**base, "body": {**base["body"], "keeping": {"cellaring": 1.6, "kept": 1.25, "why": "ages things long"}}})
    hal = KP.of(b, {**base, "body": {**base["body"], "keeping": {"kept": 0.6}}})
    drg = KP.of(b, {**base, "body": {**base["body"], "keeping": {"smoking": 0.0, "why": "steams, never smokes"}}})
    pe, pp = elf["preservation"], plain["preservation"]
    assert pe["preserved_share"] > pp["preserved_share"] > hal["preservation"]["preserved_share"]
    assert _m(elf)["cellaring"] / pe["preserved_share"] > _m(plain)["cellaring"] / pp["preserved_share"]
    assert any("authored for this kind" in r and "ages things long" in r for r in next(m for m in pe["methods"] if m["id"] == "cellaring")["reasons"])
    assert "authored" in pe["preserved_why"]
    assert "smoking" in _m(plain) and "smoking" not in _m(drg)
    assert any(a["id"] == "smoking" and "steams, never smokes" in a["why"] for a in drg["preservation"]["absent"])


def test_a_leaning_never_opens_a_method_the_people_does_not_know():
    r = KP.of(_brief(salt100=1.0, coast_fish=0.8), _p(know=ALL - {"salting"}, coastal=True, body={"keeping": {"salting": 3.0}}))
    assert "salting" not in _m(r)
    assert next(a for a in r["preservation"]["absent"] if a["id"] == "salting")["why"].startswith("does not know")


def test_the_tree_parses_keeping_and_merges_it_down():
    import pytest
    assert SP.parse_body({"keeping": {"cellaring": 1.5, "kept": 0.6, "why": "x"}}) == {"keeping": {"cellaring": 1.5, "kept": 0.6, "why": "x"}}
    for bad in ({"pickles": 1.0}, {"smoking": -1}, {"smoking": 9}, {"smoking": True}, []):
        with pytest.raises(ValueError):
            SP.parse_body({"keeping": bad})
    t = SP.load("planet/lineages/samples/dnd.toml")
    assert t.lines["elf"].body["keeping"]["cellaring"] > 1 and t.lines["halfling"].body["keeping"]["kept"] < 1
    assert t.lines["dragonborn"].body["keeping"]["smoking"] == 0 and t.lines["human"].body["keeping"] == {}


def test_bought_tea_and_cacao_are_bitter_not_hot():
    b, p = _brief(), _p(farm=0.6, crops=("wheat",))
    plain = KP.of(b, p)["flavour"]["axes"]
    r = KP.of({**b, "trade_reach": _bought("spices", crops=("tea", "cacao"))}, p)["flavour"]["axes"]
    assert r["hot"]["value"] == plain["hot"]["value"] and r["bitter"]["value"] > plain["bitter"]["value"]
