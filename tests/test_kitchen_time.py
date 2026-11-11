"""A culture's kitchen through time (kitchen_time.py, PW-1714): the changes read from hand-made frames, no run needed."""

from planet.lineages import keeping as KP
from planet.lineages import kitchen_time as KT

MT = {m[0]: (m[1], m[2]) for m in KP.METHODS}


def _e(ago, crops=(), herds=(), farm=0.0, herd=0.0, fuel="wood", bought=None, top=("herbal", "salty"), dairy=False):
    b = bought or {}
    return {"ago_kyr": ago, "crops": sorted(crops), "herds": sorted(herds), "ways": {"farm": farm, "herd": herd, "forage": 1 - farm - herd},
            "fuel": fuel, "dairy": dairy, "cheese": False, "bought": dict(b), "bought_label": {g: f"{g} (from the river people)" for g in b},
            "methods": ["drying"], "kept": 0.2, "flavour": {a: 0.1 for a in KP.AXES}, "top": list(top),
            "descriptor": ", ".join(top) + ": a temperate farming drying kitchen"}


def _texts(ev, kind=None):
    return [r["text"] for r in ev if kind is None or r["kind"] == kind]


def test_crops_herds_and_ways_arrive_with_their_dates_and_givers():
    ep = [_e(6.0), _e(5.5), _e(4.0, crops=("wheat",), herds=("caprine",), farm=0.5, herd=0.2), _e(3.5, crops=("wheat",), herds=("caprine",), farm=0.5, herd=0.2)]
    known = {"crop_wheat": [4.2, "contact", "human"], "animal_caprine": [4.5, "tamed", None]}
    ev = KT.events(ep, known, born=6.0, names={"human": "humans"}, method_techs=MT)
    assert {(r["kind"], r["ago_kyr"]) for r in ev} >= {("crop", 4.0), ("herd", 4.0), ("way", 4.0)}
    assert "taken up from humans" in _texts(ev, "crop")[0] and "its people had tamed it" in _texts(ev, "herd")[0]
    ls = KT.lines(ep, ev, 6.0, known, MT, lambda k, x: x)
    assert ls[0]["text"].startswith("founded:") and "wheat" in ls[1]["text"] and "arrive" in ls[1]["text"]


def test_a_crop_on_its_land_before_its_people_knew_it_is_named_as_anothers():
    ep = [_e(3.0), _e(2.0, crops=("rice",)), _e(1.5, crops=("rice",))]
    ev = KT.events(ep, {"crop_rice": [0.5, "tamed", None]}, born=3.0, method_techs=MT)
    assert "another people's, on its land" in _texts(ev, "crop")[0]


def test_flicker_is_not_reported_and_a_steady_loss_is():
    ep = [_e(5, crops=("wheat",)), _e(4.5), _e(4, crops=("wheat",)), _e(3.5), _e(3), _e(2.5)]
    ev = KT.events(ep, {}, born=5.0, method_techs=MT)
    assert [r["ago_kyr"] for r in ev if r["kind"] == "crop_lost"] == [3.5]
    assert not [r for r in ev if r["kind"] == "crop"]


def test_keeping_methods_are_dated_by_the_tech_and_founding_knowledge_is_not_an_event():
    ep = [_e(5.0), _e(0.0)]
    known = {"salting": [2.46, "contact", "dwarf"], "smoking_drying": [30.0, "invented", None], "cellaring": [None, None, None]}
    ev = KT.events(ep, known, born=5.0, names={"dwarf": "dwarves"}, method_techs=MT, tree={"salting", "smoking_drying", "cellaring"})
    kp = [r for r in ev if r["kind"] == "keeping"]
    assert [(r["item"], r["ago_kyr"]) for r in kp] == [("salting", 2.5)] and "taken up from dwarves" in kp[0]["text"]


def test_bought_in_food_and_flavour_shifts():
    ep = [_e(3.0), _e(2.5), _e(1.0, bought={"spices": 0.05}, top=("hot", "salty")), _e(0.5, bought={"spices": 0.05}, top=("salty", "hot"))]
    ev = KT.events(ep, {}, born=3.0, method_techs=MT)
    assert _texts(ev, "bought") == ["spices (from the river people) bought in"]
    fl = [r for r in ev if r["kind"] == "flavour"]
    assert len(fl) == 1 and fl[0]["ago_kyr"] == 1.0 and fl[0]["text"] == "the kitchen turns hot and salty (was herbal and salty)"  # (hot+salty then salty+hot: one shift)


def test_markdown_lists_the_lines():
    t = {"lines": [{"when": "4,000 years ago", "text": "wheat arrives"}]}
    assert KT.markdown(t) == ["- Kitchen through time:", "  - 4,000 years ago: wheat arrives"] and KT.markdown(None) == []


def test_the_lead_fuel_must_hold_three_frames_to_count():
    ep = [_e(5, fuel="wood"), _e(4.5, fuel="peat"), _e(4, fuel="wood"), _e(3.5, fuel="dung"), _e(3, fuel="dung"), _e(2.5, fuel="dung")]
    ev = KT.events(ep, {}, born=5.0, method_techs=MT)
    assert _texts(ev, "fuel") == ["cooks mostly on dung (was wood)"]
