"""Settlement size classes by era (PW-1114) and minority churn (PW-1117): planet/lineages/settlements.py."""

from planet.grid import shared_grid
from planet.lineages import settlements as ST

from test_settlements import LEVEL, _flat, _run, _two_peoples


def test_size_classes_follow_the_holders_techs(tmp_path):
    """A town is 1,000 people to a people with 'towns' and 2,000 once it has 'cities' and 'roads'; a place's bands say so."""
    g = shared_grid(LEVEL)
    F = 13
    tech = {"a": {"villages": [11.0, "x"], "towns": [10.0, "x"], "cities": [9.0, "x"], "roads": [4.0, "x"]}}
    out, _ = _run(tmp_path, _flat(g, F, 60), _flat(g, F, 1.0), _flat(g, F, 200), tech=tech)
    d = ST.derive(out)["doc"]
    assert d["tiers"]["town_min_by_stage"][3] == 1000 and d["tiers"]["town_min_by_stage"][4] == 2000
    mins = {tm for s in d["sites"] if s["kind"] == "chief" for _, tm, _ in s["bands"]}
    assert mins == {1000.0, 2000.0}  # (before and after 'roads')
    assert all(s["peak_pop"] <= d["constants"]["CITY_CAP"][4] for s in d["sites"])


def test_a_minority_waits_to_found_and_its_place_is_not_pinned_at_a_cap(tmp_path):
    """No own place until the second people has stood MINORITY_STEPS steps; holds are not all at the town cap."""
    out, g = _two_peoples(tmp_path, 20.0, dens=400)
    d = ST.derive(out, RIVER_SHIFT=0.0)
    own = [s for s in d["doc"]["sites"] if s["kind"] == "minority"]
    c = d["doc"]["constants"]
    assert own
    # the second people's earliest standing is the first step; founding needs MINORITY_STEPS more (and FOUND_STEPS)
    first = d["doc"]["from_kyr"]
    assert max(s["founded_kyr"] for s in own) <= first - c["MINORITY_STEPS"] * c["STEP_KYR"] + 1e-9
    sizes = [s["pop_now"] for s in own if s["abandoned_kyr"] is None]
    assert sizes and sum(1 for p in sizes if p >= c["TOWN_CAP"] - 1) < len(sizes) / 2
