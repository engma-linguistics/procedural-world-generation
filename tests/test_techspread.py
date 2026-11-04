"""planet/lineages/techspread.py: the spread read-out of one tech, on a tiny hand-made run."""

import json

from planet.lineages import techspread as TS


def _site(i, cell, holder, pop, founded=1.0):
    return {"id": i, "kind": "chief", "cell": cell, "founded_kyr": founded, "abandoned_kyr": None, "holder": holder, "holders": [[founded, holder]],
            "series": [[founded, pop], [0.0, pop]], "bands": [[founded, 1000.0, 10000.0]]}


def _run(tmp_path):
    known = {"a": {"writing": [0.8, "invented", None], "towns": [1.0, "invented", None]},
             "b": {"writing": [0.3, "contact", "a"], "towns": [1.0, "invented", None]},
             "c": {"towns": [1.0, "invented", None]}}
    meta = {"techtree": {"known": known, "techs": [{"id": "writing", "name": "writing", "needs": ["towns"]}, {"id": "towns", "name": "towns", "needs": []}]},
            "settlements": {"file": "settlements.json"}, "cultures": {"file": "cultures.json"},
            "lineages": [{"id": x, "name": x.upper()} for x in "abc"],
            "contacts": {"pairs": [{"a": "a", "b": "b", "first_contact_kyr": 0.9, "in_contact_now": True, "series": []},
                                   {"a": "a", "b": "c", "first_contact_kyr": 0.5, "in_contact_now": True, "series": []}]}}
    S = {"from_kyr": 1.0, "step_kyr": 0.1, "tiers": {"town_min_by_stage": [1000], "city_min": 10000},
         "sites": [_site(0, 1, "a", 2000), _site(1, 2, "b", 2000), _site(2, 3, "c", 500)]}
    C = {"cultures": [{"id": 0, "people": "a", "name": "first a", "born_kyr": 1.0, "ended_kyr": None},
                      {"id": 1, "people": "b", "name": "late b", "born_kyr": 0.1, "ended_kyr": None}]}
    (tmp_path / "run.json").write_text(json.dumps({"meta": meta}))
    (tmp_path / "settlements.json").write_text(json.dumps(S))
    (tmp_path / "cultures.json").write_text(json.dumps(C))
    return tmp_path


def test_spread_shares_and_dates(tmp_path):
    doc = TS.derive(_run(tmp_path), "writing")
    s = doc["stats"]
    assert s["first_kyr"] == 0.8 and s["first_by"] == ["A"] and s["inventions"] == 1
    assert doc["steps"][0] == 1.0 and doc["steps"][-1] == 0.0
    assert doc["share_people"][0] == 0.0 and abs(doc["share_people"][-1] - 4000 / 4500) < 1e-3  # (a and b: 4,000 of 4,500 settled; c never)
    assert s["reach_kyr"]["0.25"] == 0.8 and s["reach_kyr"]["0.5"] == 0.3 and s["reach_kyr"]["0.9"] is None
    assert doc["share_towns"][-1] == 1.0  # (c's place is a village: two town cells, both know it)
    P = {p["id"]: p for p in doc["peoples"]}
    assert P["b"]["from_name"] == "A" and P["b"]["ready"] == 1.0 and P["b"]["touch"] == 0.8
    assert P["c"]["ago"] is None and P["c"]["touch"] == 0.5 and "C" in s["big_never"]
    cu = {c["name"]: c for c in doc["cultures"]}
    assert cu["first a"]["how"] == "invented" and cu["late b"]["how"] == "from its start" and cu["late b"]["ago"] == 0.1
    assert any("50% of settled people" in line for line in TS.report(doc))


def test_town_footprint_counts_each_peoples_town_cells(tmp_path):
    """D52's arms B and E (techtree.ARM_DEFAULTS) read each people's town cells per ledger step: a and b one each, c's village none."""
    d = _run(tmp_path)
    m = json.loads((d / "run.json").read_text())
    m["meta"]["settlements"]["cell_km2"] = 3000
    (d / "run.json").write_text(json.dumps(m))
    fp = TS.town_footprint(d)
    assert fp["_cell_km2"] == 3000.0 and "c" not in fp
    agos, n = fp["a"]
    assert agos[0] == 1.0 and agos[-1] == 0.0 and (n == 1).all()
