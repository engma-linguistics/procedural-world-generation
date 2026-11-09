"""The names slot (PW-1436, nameslot.py; gloss names PW-1249) and the calendars cultures found (PW-1435, calendars.py; years.in_calendar;
numfmt.js calendars), on small hand-made docs."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from planet.lineages import calendars as CA
from planet.lineages import nameslot as NS
from planet.lineages.years import calendar_date, in_calendar, years_ago

VIEWER = Path(__file__).resolve().parent.parent / "viewer"
LINES = [{"id": "human", "name": "humans (Homo sapiens)"}, {"id": "elf", "name": "elves"}]


def _c(i, people="human", place="the south of Gugiki", born=12.0, how="apart", adapted="temperate", lon=10.0, end=None, demes=(), way=None):
    return {"id": i, "people": people, "place": place, "born_kyr": born, "how": how, "adapted": adapted, "lat": 5.0, "lon": lon,
            "end": end, "ended_kyr": None if end is None else 1.0, "demes": list(demes), "traits": {"ways_now": {way: 1.0} if way else {}}}


def test_gloss_names_distinct_without_numbers():
    C = [_c(0, born=12.0), _c(1, born=12.0, lon=20.0), _c(2, born=8.5), _c(3, place="Ratal"), _c(4, born=12.0, lon=30.0, way="herders")]
    out = NS.gloss_names(C, NS.people_short(LINES))
    assert len(set(out)) == len(out)
    assert not any("(" in n for n in out)
    assert out[3] == "temperate humans of Ratal"  # (a name used once stays as it was)
    assert out[2] == "temperate humans of the south of Gugiki, founded 8,500 years ago"
    assert out[4].endswith(", herders")
    assert {out[0].rsplit(", ", 1)[1], out[1].rsplit(", ", 1)[1]} == {"western", "eastern"}


def test_gloss_names_ignore_the_calendar():
    C = [_c(0), _c(1, born=9.0)]
    with in_calendar({"name": "the Flood of Iligya", "epoch_kyr": 2.0}):
        out = NS.gloss_names(C, NS.people_short(LINES))
    assert out[1].endswith("founded 9,000 years ago")


def _lang():
    return {"names": {"demes": {
        "1": {"name": {"roman": "Mupikp"}, "people": "human", "places": [{"kind": "river", "roman": "Gyerrihigyu"}],
              "settlements": [{"site": 7, "roman": "Iligya"}]},
        "2": {"name": {"roman": "Mupikp"}, "people": "human", "places": [{"kind": "lake", "roman": "Oba"}]},
        "3": {"name": {"roman": "Taliwiw"}, "people": "human", "places": []}}}}


def test_apply_cultures_languages_first_gloss_fallback():
    doc = {"cultures": [_c(0, demes=[1]), _c(1, demes=[2], born=3.0), _c(2, demes=[3, 9], born=4.0), _c(3, demes=[5], born=5.0),
                        _c(4, demes=[3], end="died out", born=6.0)],
           "merges": [{"culture": 4, "into": 2, "text": "x merged into y (side by side 1 kyr)"}]}
    NS.apply_cultures(doc, LINES, _lang(), {1: 10, 2: 5, 3: 1})
    C = doc["cultures"]
    assert [c["name"] for c in C[:3]] == ["Mupikp of Gyerrihigyu", "Mupikp of Oba", "Taliwiw"]
    assert [c["name_from"] for c in C] == ["language", "language", "language", "gloss", "gloss"]
    assert C[3]["name"] == C[3]["gloss_name"] and C[4]["name"] == C[4]["gloss_name"]  # (no living deme with a name: the gloss)
    assert doc["merges"][0]["text"] == f"{C[4]['name']} merged into Taliwiw (side by side 1 kyr)"
    again = json.loads(json.dumps(doc))
    assert NS.apply_cultures(again, LINES, _lang(), {1: 10, 2: 5, 3: 1}) == doc  # (applying twice changes nothing)


def test_faiths_and_states_take_the_slot():
    doc = {"cultures": [_c(0, demes=[3]), _c(1, born=3.0)]}
    NS.apply_cultures(doc, LINES, _lang())
    gd = {"faiths": {"list": [{"id": 0, "name": "old", "core": "sky", "how": "founded", "origin_culture": 0, "authored": None},
                              {"id": 1, "name": "the Forge", "core": "fire", "how": "founded", "origin_culture": 1, "authored": "f1"},
                              {"id": 2, "name": "old", "core": "sea", "how": "schism", "origin_culture": 1, "authored": None}]}}
    NS.apply_faiths(gd, doc["cultures"])
    F = gd["faiths"]["list"]
    assert F[0]["name"] == "the sky faith of Taliwiw" and F[0]["name_from"] == "language"
    assert F[1]["name"] == "the Forge" and F[1]["name_from"] == "authored"
    assert F[2]["name"] == f"the sea schism of {doc['cultures'][1]['gloss_name']}" and F[2]["name_from"] == "gloss"
    pd = {"polities": [{"id": 0, "kind": "town", "capital": {"site": 7}, "tier_peak": "chiefdom", "peak_kyr": 1.0,
                        "peoples": [[2.0, "human", "humans"], [1.0, "elf", "elves"]], "names": [[2.0, "South (humans)"], [1.0, "South (elves)"]], "name": "South (elves)"},
                       {"id": 1, "kind": "town", "capital": {"site": 8}, "tier_peak": "state", "peak_kyr": 1.0,
                        "peoples": [[2.0, "human", "humans"]], "names": [[2.0, "North (humans)"]], "name": "North (humans)"}]}
    NS.apply_polities(pd, _lang())
    P = pd["polities"]
    assert P[0]["names"] == [[2.0, "Chiefdom in Iligya (humans)"], [1.0, "Chiefdom in Iligya (elves)"]] and P[0]["name"] == "Chiefdom in Iligya (elves)"
    assert P[0]["gloss_name"] == "South (elves)" and P[1]["name"] == "North (humans)" and P[1]["name_from"] == "gloss"
    NS.apply_polities(pd, _lang())
    assert P[0]["gloss_names"] == [[2.0, "South (humans)"], [1.0, "South (elves)"]]


def test_calendar_dates_and_context():
    cal = {"name": "the Founding of Iligya", "epoch_kyr": 0.212}
    assert calendar_date(0.0, cal) == "year 213 of the Founding of Iligya"
    assert calendar_date(0.212, cal) == "year 1 of the Founding of Iligya"  # (the event's own year is year 1)
    assert calendar_date(1.212, cal) == "1,000 years before the Founding of Iligya"
    assert years_ago(1.0) == "1,000 years ago"
    with in_calendar(cal):
        assert years_ago(0.112) == "year 101 of the Founding of Iligya"
        assert years_ago(0.112, calendar=False) == "112 years ago"
    assert years_ago(0.0) == "the present"


def _run():
    C = [dict(_c(0, born=20.0), name="A", uid="a"), dict(_c(1, born=20.0, lon=40.0), name="B", uid="b"),
         dict(_c(2, people="elf", born=20.0), name="E", uid="e")]
    meta = {"seed": 7, "lineages": LINES, "techtree": {"known": {"human": {"writing": [5.0, "invented", None]}}},
            "contacts": {"incursions": [{"by": "elf", "over": "human", "kind": "settled_among", "ago_kyr": 1.0, "lat": 5.0, "lon": 11.0}]}}
    gods = {"faiths": {"list": [{"id": 0, "name": "the sky faith of A", "how": "founded", "core": "sky", "origin_culture": 0, "founded_kyr": 2.0,
                                 "ended_kyr": None, "cultures_ever": list(range(8))},
                                {"id": 1, "name": "the sea faith of E", "how": "founded", "core": "sea", "origin_culture": 2, "founded_kyr": 2.0,
                                 "ended_kyr": None, "cultures_ever": [2] * 8}]},
            "cultures": {"0": {"faiths": [[20.0, 9], [2.0, 0]]}, "1": {"faiths": [[1.5, 0]]}}}
    pol = {"cultures": {"a": {"id": 0}, "b": {"id": 1}, "e": {"id": 2}},
           "polities": [{"id": 0, "name": "Iligya (humans)", "founded_kyr": 1.5, "tiers": [[1.5, "chiefdom"], [1.2, "empire"]], "tier_peak": "empire",
                         "rulers": [[1.5, "a"]], "subjects": ["b"], "fell_kyr": None, "fell_how": None, "fell_by": None},
                        {"id": 1, "name": "West of Oba (humans)", "founded_kyr": 1.0, "tiers": [[1.0, "state"]], "tier_peak": "state",
                         "rulers": [[1.0, "b"]], "subjects": [], "fell_kyr": 0.4, "fell_how": "conquered", "fell_by": 0}]}
    return C, meta, gods, pol


def test_calendars_from_events(monkeypatch):
    C, meta, gods, pol = _run()
    for k in ("P_FAITH", "P_CONQUEST", "P_INCURSION"):
        monkeypatch.setattr(CA, k, 1.0)
    monkeypatch.setattr(CA, "P_STATE", {"state": 1.0, "empire": 1.0, "dragon realm": 1.0})
    doc = CA.derive(C, meta, gods=gods, polities=pol)
    by = {x["kind"]: x for x in doc["calendars"]}
    assert set(by) == {"faith", "state", "conquest", "incursion"}  # (the elves' faith: no writing, no count)
    f = by["faith"]
    assert f["name"] == "the Sky Faith" and f["epoch_kyr"] == 2.0 and f["culture"] == 0 and f["alive"]
    assert f["holders"][0] == {"culture": 0, "from_kyr": 2.0, "to_kyr": None}
    st = sorted((x["name"], x["epoch_kyr"]) for x in doc["calendars"] if x["kind"] == "state")
    assert st == [("the Founding of the west of Oba", 1.0), ("the Rise of Iligya", 1.2)]  # (a rise from a chiefdom to an empire)
    assert by["conquest"]["name"] == "the Conquest of the west of Oba" and by["conquest"]["epoch_kyr"] == 0.4
    assert by["incursion"]["name"] == "the Coming of the elves" and by["incursion"]["culture"] == 0  # (the nearest human culture)
    assert doc["by_culture"]["0"] and CA.calendar_of(doc, f["id"]) is f and CA.calendar_of(doc, "x") is None
    assert CA.derive(C, meta, gods=gods, polities=pol) == doc  # (deterministic)


def test_no_writing_no_calendars():
    C, meta, gods, pol = _run()
    meta["techtree"]["known"] = {}
    assert CA.derive(C, meta, gods=gods, polities=pol)["calendars"] == []


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_numfmt_calendar():
    js = r"""
const store = {};
globalThis.localStorage = { getItem: (k) => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: (k) => { delete store[k]; } };
(0, eval)(require('fs').readFileSync(process.argv[1], 'utf8'));
const N = NumFmt, out = {};
N.run = 'r1'; N.setPresent(1400);
N.setCalendar({ id: 3, name: 'the Founding of Iligya', epoch_kyr: 0.212 });
out.cal = [N.ago(0), N.ago(0.212), N.ago(1.212), N.ago(0.5, null)];
out.other = N.calendar('r2');
N.setCalendar(null); out.cleared = N.ago(0.3);
console.log(JSON.stringify(out));
"""
    r = subprocess.run(["node", "-e", js, str(VIEWER / "numfmt.js")], capture_output=True, text=True, check=True)
    o = json.loads(r.stdout)
    assert o["cal"] == ["year 213 of the Founding of Iligya", "year 1 of the Founding of Iligya", "1,000 years before the Founding of Iligya",
                        "500 years ago"]
    assert o["other"] is None and o["cleared"] == "year 1100"
