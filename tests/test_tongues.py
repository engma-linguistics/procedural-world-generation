"""Tongues ledger (PW-1526): who speaks which tongue besides its own. Each rule on hand-made eras, and the border reading on test_trade_flow's
line of six cells; no run needed."""

import numpy as np

from planet.lineages import tongues as TG
from tests.test_trade_flow import _line_ctx

C = [{"name": f"c{i}", "people": "p", "demes": [i]} for i in range(6)]
NOLANG = TG.LangIndex(None, C)


def _hub(site, cell, culture, strength, people=5000, quarters=()):
    return {"site": site, "cell": cell, "culture": culture, "strength": strength, "people": people, "place": f"town{site}", "trading": True,
            "long": True, "quarters": [[q, f"c{q}", v] for q, v in quarters]}


def _route(a, b, lay=1):
    return [a, b, 0.1, 0, 0, lay, 0.1, 0, 0.0, 0]


def _era(ago=1.0, **kw):
    inp = {"ago_kyr": ago, "people": {c: 10000.0 for c in range(6)}, "urban": {c: 0.1 for c in range(6)}, "border": {}, "rules": {},
           "faith": {}, "route_folk": {}, "routes": [], "hubs": []}
    inp.update(kw)
    return inp


def _rows(rows, c):
    return {(x[0], x[1]): x for x in rows.get(str(c), [])}


def test_border_folk_learn_the_bigger_neighbours_tongue_more():
    """Bilingual borderlands (Multilingualism: 'border regions with many cross-border contacts'); the higher-status, here the bigger,
    tongue spreads more (Language shift)."""
    inp = _era(people={0: 1000.0, 1: 9000.0}, border={(0, 1): 0.4, (1, 0): 0.05})
    rows, *_ = TG.era_rows(inp, [], {}, NOLANG)
    a = _rows(rows, 0)[(1, "neighbour")][2]
    assert abs(a - TG.NEIGHBOUR_UPTAKE * 0.4 * 2 * 0.9) < 1e-3
    assert (0, "neighbour") not in _rows(rows, 1)  # (5% of the big people on the border x a tenth: under the floor)


def test_subjects_speak_the_rulers_tongue_townsfolk_first_then_more_each_era():
    rows, _, nets, ruled = TG.era_rows(_era(rules={0: {1}}), [], {}, NOLANG)
    first = _rows(rows, 1)[(0, "ruler")][2]
    assert abs(first - 0.1) < 1e-6  # (the townsfolk)
    for _ in range(3):
        rows, _, nets, ruled = TG.era_rows(_era(rules={0: {1}}), nets, ruled, NOLANG)
    later = _rows(rows, 1)[(0, "ruler")][2]
    assert later > first and later <= TG.RULE_MAX
    assert not rows.get("0")  # (the rulers learn nothing from it here)


def test_a_dominant_trader_gives_the_network_its_lingua_franca():
    hubs = [_hub(1, 0, 0, 0.6), _hub(2, 2, 1, 0.2), _hub(3, 4, 2, 0.1)]
    rows, langs, *_ = TG.era_rows(_era(routes=[_route(0, 2), _route(2, 4)], hubs=hubs), [], {}, NOLANG)
    assert len(langs) == 1 and langs[0]["kind"] == "lingua franca" and langs[0]["tongue"] == 0 and langs[0]["source"] == "trade"
    assert (0, "lingua franca") in _rows(rows, 1) and (0, "lingua franca") in _rows(rows, 2)
    assert not rows.get("0")  # (its own tongue)


def test_no_clear_leader_makes_a_pidgin_on_the_busiest_traders_words():
    """Pidgin: between groups 'that do not have a language in common', 'most commonly ... trade', its superstrate the dominant one."""
    hubs = [_hub(1, 0, 0, 0.3), _hub(2, 2, 1, 0.25), _hub(3, 4, 2, 0.2)]
    rows, langs, *_ = TG.era_rows(_era(routes=[_route(0, 2), _route(2, 4)], hubs=hubs), [], {}, NOLANG)
    assert langs[0]["kind"] == "pidgin" and langs[0]["tongue"] == 0
    assert all((0, "pidgin") in _rows(rows, c) for c in (0, 1, 2))  # (everyone on the network, the word-giver's traders too)


def test_a_ruling_states_tongue_wins_the_network_it_holds():
    hubs = [_hub(1, 0, 0, 0.2), _hub(2, 2, 1, 0.35), _hub(3, 4, 2, 0.45)]  # (2 trades most, but 0 rules 1 and 2... rule 1 only: 0.55)
    _, langs, *_ = TG.era_rows(_era(routes=[_route(0, 2), _route(2, 4)], hubs=hubs, rules={0: {1}}), [], {}, NOLANG)
    assert langs[0]["tongue"] == 0 and langs[0]["source"] == "rule"


def test_a_lingua_franca_outlives_the_state_that_made_it_until_a_much_stronger_trader_comes():
    routes = [_route(0, 2), _route(2, 4)]
    hubs = [_hub(1, 0, 0, 0.2), _hub(2, 2, 1, 0.35), _hub(3, 4, 2, 0.45)]
    _, l1, nets, ruled = TG.era_rows(_era(2.0, routes=routes, hubs=hubs, rules={0: {1}}), [], {}, NOLANG)
    _, l2, nets, ruled = TG.era_rows(_era(1.5, routes=routes, hubs=hubs), nets, ruled, NOLANG)  # (the state is gone; 2 leads at 45%)
    assert l2[0]["tongue"] == 0 and l2[0]["source"] == "held" and l2[0]["id"] == l1[0]["id"] and l2[0]["since_kyr"] == 2.0
    big = [_hub(1, 0, 0, 0.02), _hub(2, 2, 1, 0.08), _hub(3, 4, 2, 0.9)]
    _, l3, *_ = TG.era_rows(_era(1.0, routes=routes, hubs=big), nets, ruled, NOLANG)
    assert l3[0]["tongue"] == 2 and l3[0]["id"] != l1[0]["id"]


def test_a_pidgin_gives_way_to_the_first_real_trade_language():
    routes = [_route(0, 2), _route(2, 4)]
    _, l1, nets, ruled = TG.era_rows(_era(2.0, routes=routes, hubs=[_hub(1, 0, 0, 0.3), _hub(2, 2, 1, 0.25), _hub(3, 4, 2, 0.2)]), [], {}, NOLANG)
    _, l2, *_ = TG.era_rows(_era(1.5, routes=routes, hubs=[_hub(1, 0, 0, 0.1), _hub(2, 2, 1, 0.1), _hub(3, 4, 2, 0.6)]), nets, ruled, NOLANG)
    assert l1[0]["kind"] == "pidgin" and l2[0]["kind"] == "lingua franca" and l2[0]["tongue"] == 2


def test_a_one_culture_network_needs_no_trade_language_but_a_merchant_quarter_makes_two():
    routes = [_route(0, 2)]
    _, langs, *_ = TG.era_rows(_era(routes=routes, hubs=[_hub(1, 0, 0, 0.5), _hub(2, 2, 0, 0.5)]), [], {}, NOLANG)
    assert langs == []
    rows, langs, *_ = TG.era_rows(_era(routes=routes, hubs=[_hub(1, 0, 0, 0.5, people=40000, quarters=[(3, 0.3)])]), [], {}, NOLANG)
    assert len(langs) == 1 and langs[0]["tongue"] == 0
    r3 = _rows(rows, 3)
    assert (0, "host") in r3 and abs(r3[(0, "host")][2] - TG.QUARTER_FOLK * 40000 / 10000) < 1e-3


def test_local_only_routes_carry_no_trade_language():
    _, langs, *_ = TG.era_rows(_era(routes=[_route(0, 2, lay=2)], hubs=[_hub(1, 0, 0, 0.6), _hub(2, 2, 1, 0.4)]), [], {}, NOLANG)
    assert langs == []


def test_route_folk_speak_it_thinly():
    hubs = [_hub(1, 0, 0, 0.6), _hub(2, 4, 1, 0.4)]
    rows, *_ = TG.era_rows(_era(routes=[_route(0, 2), _route(2, 4)], hubs=hubs, route_folk={2: {5: 0.5}}), [], {}, NOLANG)
    assert abs(_rows(rows, 5)[(0, "lingua franca")][2] - TG.ALONG * 0.5) < 1e-3


def test_same_language_is_no_second_tongue_and_lects_name_the_tongue():
    lang = {"lects": [{"id": "d0", "deme": 0, "language": "lang1", "born_kyr": 20.0, "died_kyr": None},
                      {"id": "d1", "deme": 1, "language": "lang1", "born_kyr": 20.0, "died_kyr": None},
                      {"id": "d2", "deme": 2, "language": "lang2", "born_kyr": 20.0, "died_kyr": None}], "faiths": {}}
    L = TG.LangIndex(lang, C)
    rows, *_ = TG.era_rows(_era(border={(0, 1): 0.5, (0, 2): 0.5}), [], {}, L)
    r = _rows(rows, 0)
    assert (1, "neighbour") not in r and r[(2, "neighbour")][3:5] == ["d2", "lang2"]


def test_clergy_learn_the_frozen_liturgy_of_their_faith():
    lang = {"lects": [{"id": "d0", "deme": 0, "language": "lang1", "born_kyr": 20.0, "died_kyr": None},
                      {"id": "d1", "deme": 1, "language": "lang2", "born_kyr": 20.0, "died_kyr": None}],
            "faiths": {"4": {"liturgy": {"lect_from": "d0", "deme": 0, "kyr": 5.0}}}}
    L = TG.LangIndex(lang, C)
    rows, *_ = TG.era_rows(_era(3.0, faith={0: 4, 1: 4}), [], {}, L)
    assert _rows(rows, 1)[(0, "liturgy")][3] == "d0"
    assert (0, "liturgy") in _rows(rows, 0)  # (2 kyr on, the seat's own clergy keep the canon as a second tongue)
    rows, *_ = TG.era_rows(_era(6.0, faith={0: 4, 1: 4}), [], {}, L)
    assert not rows  # (before the canon is fixed)


def test_shares_stay_in_range_on_random_eras():
    rng = np.random.default_rng(3)
    nets, ruled = [], {}
    for k in range(20):
        hubs = [_hub(s, int(rng.integers(0, 6)), int(rng.integers(0, 6)), float(rng.random()), people=int(rng.integers(0, 90000)),
                     quarters=[(int(rng.integers(0, 6)), 0.3)] if rng.random() < 0.3 else []) for s in range(5)]
        routes = [_route(int(a), int(b), int(rng.integers(1, 4))) for a, b in rng.integers(0, 6, (6, 2)) if a != b]
        inp = _era(10.0 - k * 0.5, people={c: float(rng.integers(0, 20000)) for c in range(6)}, routes=routes, hubs=hubs,
                   border={(int(a), int(b)): float(rng.random()) for a, b in rng.integers(0, 6, (8, 2)) if a != b},
                   rules={int(rng.integers(0, 6)): {int(rng.integers(0, 6))}}, route_folk={2: {1: 0.3}})
        rows, langs, nets, ruled = TG.era_rows(inp, nets, ruled, NOLANG)
        for rs in rows.values():
            for x in rs:
                assert (TG.MIN_SHARE <= x[2] or x[1] in TG.BY_HEADS) and 0 < x[2] <= 1.0 and x[1] in TG.KINDS
        assert all(x["kind"] in ("lingua franca", "pidgin") for x in langs)


def test_borders_read_from_a_run_frame(tmp_path):
    """frame_inputs on the six-cell line (herders 0-1, farmers 2-3, foragers 4-5): each pair of neighbours touches, the ends do not."""
    from planet.lineages import trade as TR
    ctx = _line_ctx(tmp_path)
    P = TR.pairs_at(ctx, 0)
    assert P is not None
    inp = TG.frame_inputs(ctx, 0, {"routes": [], "hubs": []}, None, None)
    cu = sorted(set(np.asarray(P["culture"]).tolist()))
    assert len(cu) == 3
    a, b, c = cu
    assert inp["border"].get((a, b), 0) > 0 and inp["border"].get((b, c), 0) > 0 and (a, c) not in inp["border"]
    assert all(0 < v <= 1 for v in inp["border"].values())
    rows, *_ = TG.era_rows(inp, [], {}, TG.LangIndex(None, ctx.cultures()["cultures"]))
    assert rows  # (borderlands make bilinguals on the line)


def test_a_state_ruling_only_its_own_people_gives_no_rule_tongue():
    hubs = [_hub(1, 0, 0, 0.3), _hub(2, 2, 1, 0.35), _hub(3, 4, 2, 0.35)]
    _, langs, *_ = TG.era_rows(_era(routes=[_route(0, 2), _route(2, 4)], hubs=hubs, rules={0: {0}, 1: {1, 4}}), [], {}, NOLANG)
    assert langs[0]["kind"] == "pidgin"  # (no state rules another trading people there; no trader leads)


def test_a_big_peoples_traders_count_by_heads_and_neighbours_are_capped():
    ppl = {c: 10000.0 for c in range(6)} | {1: 2_000_000.0}
    hubs = [_hub(1, 0, 0, 0.7), _hub(2, 2, 1, 0.3, people=3000)]
    inp = _era(people=ppl, routes=[_route(0, 2)], hubs=hubs, border={(0, b): 0.9 for b in range(1, 6)})
    rows, *_ = TG.era_rows(inp, [], {}, NOLANG)
    lf = _rows(rows, 1)[(0, "lingua franca")]
    assert lf[2] < TG.MIN_SHARE and lf[2] * 2_000_000 >= TG.MIN_HEADS
    assert sum(1 for x in rows["0"] if x[1] == "neighbour") == TG.TOP_PER_KIND and rows["0"][0][0] == 1  # (the biggest neighbour first)


def test_a_chiefdom_imposes_no_trade_language_a_state_does():
    hubs = [_hub(1, 0, 0, 0.2), _hub(2, 2, 1, 0.35), _hub(3, 4, 2, 0.45)]
    base = dict(routes=[_route(0, 2), _route(2, 4)], hubs=hubs, rules={0: {1}})
    _, langs, *_ = TG.era_rows(_era(**base, states=set()), [], {}, NOLANG)
    assert langs[0]["kind"] == "pidgin"
    _, langs, *_ = TG.era_rows(_era(**base, states={0}), [], {}, NOLANG)
    assert langs[0]["tongue"] == 0 and langs[0]["source"] == "rule"


def test_state_rulers_reads_the_polity_tiers():
    from planet.lineages.polities import _pack
    pol = {"steps": [{"ago": 1.0}], "tiers": ["chiefdom", "state", "empire", "dragon realm"], "cultures": {"u0": {"id": 0}, "u1": {"id": 1}},
           "polities": [{"id": 0, "rulers": [[2.0, "u0"]]}, {"id": 1, "rulers": [[2.0, "u1"]]}],
           "maps": [[[0, 0, _pack(np.array([0])), {"u0": 1}, 1], [1, 2, _pack(np.array([1])), {"u1": 1}, 1]]]}
    C2 = [{"end": None, "into": None, "ended_kyr": None}] * 2
    assert TG.state_rulers(pol, 1.0, C2) == {1}


def test_the_tongues_endpoint_asks_for_a_run():
    from planet import server as SV
    body, code = SV.tongues("")
    assert code == 400 and "run=" in body["error"]


def test_an_older_lingua_franca_is_harder_to_dislodge():
    net = {"weight": {0: 0.1, 1: 0.1, 2: 0.8}}  # (2 carries 0.8 of the trade; the incumbent 0 carries 0.1)
    young = {"kind": "lingua franca", "tongue": 0, "source": "rule", "eras": 1}
    old = {"kind": "lingua franca", "tongue": 0, "source": "rule", "eras": 20}
    assert TG.pick(net, {}, young)["tongue"] == 2  # 0.8 >= 2 x HELD (0.25)
    r = TG.pick(net, {}, old)  # HELD_MAX 0.45: 0.8 < 2 x 0.45
    assert r["tongue"] == 0 and r["source"] == "held" and r["eras"] == 21


def test_a_state_whose_own_people_barely_trade_does_not_win_the_network():
    net = {"weight": {0: 0.05, 1: 0.55, 2: 0.4}}  # (0 rules 2, but its own people carry 5%; 1 is the busiest trader)
    r = TG.pick(net, {0: {2}}, None, None)
    assert r["tongue"] == 1 and r["source"] == "trade"
    assert TG.pick({"weight": {0: 0.3, 1: 0.1, 2: 0.6}}, {0: {2}}, None, None)["source"] == "rule"
