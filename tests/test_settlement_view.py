"""The settlement view (PW-1659) and the trade goods map (PW-1508): each part on small hand-made docs, no run needed."""

import numpy as np
import pytest

from planet.lineages import settlement_view as SV
from planet.lineages import trade as TR
from planet.lineages.polities import _pack
from test_trade import _ctx

TIERS = {"city_min": 10000, "town_min_by_stage": [500, 1000]}


def _site(**kw):
    s = {"id": 3, "kind": "chief", "cell": 4, "lat": 1.0, "lon": 2.0, "place": "the east of Somewhere", "tier_peak": "town", "tier_now": "town",
         "founded_kyr": 5.0, "founded_by": "human", "holder": "elf", "holders": [[5.0, "human"], [2.0, "elf"]], "abandoned_kyr": None, "why": None,
         "ruin_of": 1, "resettled_as": None, "pop_now": 1500, "peak_pop": 1500, "peak_kyr": 0.0, "who": {"elf": 60, "human": 40}, "who_when": "now",
         "series": [[5.0, 100], [2.0, 800], [0.0, 1500]], "bands": [[5.0, 500.0, 10000.0]], "war": [[2.0, "taken", "elf"], [6.0, "raided", "orc"]],
         "walled_kyr": 1.0}
    s.update(kw)
    return s


def test_people_and_tier_follow_the_series_and_bands():
    s = _site()
    assert SV.pop_at(s, 0.0) == 1500 and SV.pop_at(s, 6.0) == 0
    assert SV.pop_at(s, 3.5) == pytest.approx(450)  # (halfway between 100 at 5 kyr and 800 at 2 kyr)
    assert SV.tier_at(s, TIERS, 0.0) == "town"  # (the band's 500 is in force, not the last stage's 1000)
    assert SV.tier_at(s, TIERS, 4.0) == "village"
    assert SV.tier_at(_site(abandoned_kyr=1.0, tier_now="ruin"), TIERS, 0.5) == "ruin"
    assert SV.holder_at(s, 3.0) == "human" and SV.holder_at(s, 1.0) == "elf"


def test_place_part_reads_the_ruins_under_it_and_keeps_only_what_happened_by_then():
    older = {"id": 1, "place": "old", "tier_peak": "village", "founded_kyr": 9.0, "abandoned_kyr": 6.0, "why": "drought", "founded_by": "orc", "ruin_of": None}
    s = _site()
    P = SV.place_part(s, {1: older, 3: s}, TIERS, 3.5)
    assert P["ruins_under"][0]["site"] == 1 and P["ruins_under"][0]["by"] == "orc"
    assert P["holders"] == [[5.0, "human"]]  # (the elves took it 2 kyr ago: after 3.5 kyr ago)
    assert [w[0] for w in P["war"]] == [6.0] and P["walled_kyr"] is None
    assert P["tier"] == "village" and P["people"] == 450
    H = SV.history(P, None, None, lambda p: p)
    assert H[0] == [9.0, "an older village of the orc founded here"] and [5.0, "founded by the human on older ruins"] in H
    assert all(a >= 3.0 - 1e-6 for a, _ in H)


def test_history_leaves_out_what_came_before_anyone_lived_there():
    P = SV.place_part(_site(ruin_of=None), {}, TIERS, 0.0)
    faith = {"changes": [[300.0, 0, "Ana", 1, "the sky faith"], [1.5, 0, "Ana", 2, "the sea faith"]]}
    H = SV.history(P, None, faith, lambda p: p)
    assert [1.5, "Ana hold the sea faith"] in H and not any(a > 5.0 for a, _ in H)
    assert [a for a, _ in H] == sorted((a for a, _ in H), reverse=True)


def test_cell_goods_and_good_map_read_the_ledger_pairs(tmp_path):
    ctx = _ctx(tmp_path)
    P = TR.pairs_at(ctx, 0)
    labels = {g: v[0] for g, v in TR.GOODS.items()}
    herd = SV.cell_goods(P, 0, labels)  # (herders' steppe on the salt bed: salt spare, grain lacking)
    assert "salt" in [g for g, _, _ in herd["spare"]] and herd["lacking"][0][0] == "grain"
    assert SV.cell_goods(P, 99, labels) == {"spare": [], "lacking": []} and SV.cell_goods(None, 0, labels) is None
    m = SV.good_map(P, "grain", 6)
    assert m["cells"] == [0, 1, 2, 3, 4, 5]
    assert m["lacking"][0] > 50 and m["spare"][2] > 50 and m["spare"][0] == 0  # (herders lack grain, farmers spare it)
    led = TR.ledger_at(ctx, 0)  # (the map's cells average to the culture's ledger number: the herders' two cells)
    assert np.mean(m["lacking"][:2]) == pytest.approx(100 * led[0]["lack"]["grain"], abs=1.0)
    with pytest.raises(ValueError):
        SV.good_map(P, "unobtainium", 6)


def test_eraq_frame_is_the_nearest_window_frame():
    meta = {"eraq": {"frames": [10, 11, 12], "ago_kyr": [-1.0, -0.5, 0.0]}}
    assert SV.eraq_frame(meta, 0.6) == 11 and SV.eraq_frame(meta, 9.0) == 10 and SV.eraq_frame({}, 0.0) is None


def test_rule_part_names_the_ruler_now_and_before():
    rec = lambda i, nm, tier: {"id": i, "kind": "town", "people": "elf", "people_name": "elves", "names": [[3.0, nm]], "name": nm,  # noqa: E731
                               "tiers": [[3.0, tier]], "rulers": [[3.0, "u1"]], "founded_kyr": 3.0, "fell_kyr": None, "capital": {"cell": 4, "place": "x"}}
    doc = {"steps": [{"ago": 2.0}, {"ago": 1.0}, {"ago": 0.0}], "polities": [rec(0, "Old Realm", "state"), rec(1, "New Realm", "empire")],
           "cultures": {"u1": {"name": "Ana"}},
           "maps": [[[0, 1, _pack([4, 5]), {}, 10]], [], [[1, 2, _pack([3, 4]), {}, 20]]]}
    T = SV.owner_table(doc, 8)
    assert T.tolist()[0][4] == 0 and T[1, 4] == -1 and T[2, 3] == 1
    R = SV.rule_part(doc, None, T, 4, 0.0)
    assert R["now"]["name"] == "New Realm" and R["now"]["ruler"] == "Ana" and R["now"]["capital"] is True
    assert [(a, c and c["name"]) for a, c in R["past"]] == [(2.0, "Old Realm"), (1.0, None), (0.0, "New Realm")]
    assert SV.rule_part(None, None, None, 4, 0.0) is None


def test_faith_and_tongues_of_the_cultures_here():
    gods = {"faiths": {"list": [{"id": 1, "name": "the sky faith", "core": "sky"}, {"id": 2, "name": "the sea faith", "core": "sea"}]},
            "cultures": {"0": {"faiths": [[10.0, 1], [1.0, 2]]}, "1": {"faiths": [[10.0, 1]]}}}
    F = SV.faith_part(gods, [0, 1], 0.0, {0: "Ana", 1: "Bo"})
    assert {f["name"]: [c[1] for c in f["cultures"]] for f in F["held"]} == {"the sea faith": ["Ana"], "the sky faith": ["Bo"]}
    assert F["changes"][-1][0] == 1.0 or F["changes"][0][0] == 10.0
    assert SV.faith_part(gods, [0], 5.0, {})["held"][0]["name"] == "the sky faith"
    assert SV.faith_part(None, [0], 0.0, {}) is None
    tg = {"cultures": [{"name": "Ana"}, {"name": "Bo"}], "frames": [{"ago_kyr": 0.0, "cultures": {"0": [[1, "neighbour", 0.3, "d1", "lang1", None]]},
                                                                  "trade_languages": [{"kind": "lingua franca", "tongue": 1, "towns": [3, 9]}]}]}
    T = SV.tongue_part(tg, [0], 3, 0.0, {0: "Ana"})
    assert T["others"][0]["name"] == "Bo" and T["others"][0]["share"] == 0.3 and T["trade"][0]["name"] == "Bo"
    assert SV.tongue_part(tg, [0], 4, 0.0, {0: "Ana"})["trade"] == []  # (not one of the network's towns)


def test_settlement_api_needs_a_site():
    body, code = SV.api("run=")
    assert code == 400 and "required" in body["error"]
