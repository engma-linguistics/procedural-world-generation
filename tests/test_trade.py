"""The goods ledger (trade step 1, PW-1502): each rule on a small hand-made world of six cells, no run needed."""

from types import SimpleNamespace as NS

import numpy as np
import pytest

from planet.lineages import trade as TR

N = 6
# cells 0-1: herders' steppe; 2-3: farmers' plain (3 is far from salt); 4-5: foragers' forest beside the farmers (4 has a few farmers)
FARM = [0, 0, 90, 90, 10, 0]
HERD = [90, 90, 5, 5, 0, 0]
WOOD = [0, 0, 5, 5, 30, 30]
TECHS = ["cultivation", "crop_wheat", "herding", "animal_cattle", "salting", "bronze", "copper", "native_copper", "ornament", "quarrying",
         "trapping", "knapping"]


def _ctx(tmp_path, goods=None, know=None, extra_lines=(), present=None):
    eq = {}
    for k, v in (("dens", [100] * N), ("farm", FARM), ("herd", HERD), ("wood", WOOD)):
        f = tmp_path / f"eraq_{k}.bin"
        f.write_bytes(np.array([v], np.uint8).tobytes())
        eq[k] = {"file": f.name, "dtype": "uint8", "shape": [1, N]}
    G = {"fertile": np.array([0.2, 0.2, 0.9, 0.9, 0.3, 0.3]), "grazing": np.array([0.9, 0.9, 0.4, 0.4, 0.1, 0.1]),
         "timber": np.array([0.0, 0.0, 0.1, 0.1, 0.9, 0.9]), "fuel": np.array([0.1, 0.1, 0.2, 0.2, 0.9, 0.9]),
         "salt": np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0]), "tin": np.zeros(N), "copper": np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0]),
         "_salt_km": np.array([0.0, 100.0, 200.0, 900.0, 900.0, 900.0]), "_temp": np.full(N, 10.0)}
    G.update(goods or {})
    known = know if know is not None else {"herder": ["herding", "animal_cattle", "salting", "copper", "native_copper", "bronze", "quarrying"],
                                           "farmer": ["cultivation", "crop_wheat", "salting", "copper", "native_copper", "bronze", "quarrying"],
                                           "forager": ["ornament", "trapping", "knapping"]}
    lines = [{"id": p, "index": k, "name": p, "traits": ["flies"] if "dragon" in p else [], "way": "pastoral_nomad" if p == "hill_giant" else None}
             for k, p in enumerate(["herder", "farmer", "forager", *extra_lines])]
    cult = [{"name": f"the {p}s", "people": p, "born_kyr": 100.0, "ended_kyr": None, "end": None, "into": None} for p in ["herder", "farmer", "forager", *extra_lines]]
    demes = np.array([0, 0, 1, 1, 2, 2], np.uint16)
    meta = {"eraq": {"frames": [0], "ago_kyr": [0.0], "layers": eq},
            "crops": {"stocks": {"wheat": {"bit": 0, "weight": 0.7}}}, "animals": {"stocks": {"cattle": {"bit": 1}, "dog": {"bit": 0}}},
            "techtree": {"techs": [{"id": t} for t in TECHS], "known": {p: {t: [50.0, "own", None] for t in ts} for p, ts in known.items()}},
            "present": present or {}}
    arrs = {"elevation": np.full(N, 100.0), "ice": np.zeros(N), "crop_known": np.array([0, 0, 1, 1, 1, 0]), "animal_known": np.array([2, 2, 2, 2, 0, 0])}
    doc = {"cultures": cult, "deme_culture": list(range(len(cult)))}
    ctx = NS(dir=tmp_path, meta=meta, goods=G, g=NS(n=N), ts=np.array([0.0]), idx={l["id"]: l["index"] for l in lines}, lines=lines,
             _frame_cache={}, arr={"crop_known": 1, "animal_known": 1, "demes": [demes]}, f=lambda name, i: arrs[name],
             cultures=lambda: doc, overlap=lambda: None)
    return ctx


def test_herders_lack_grain_farmers_have_it_and_salt_follows_the_walk(tmp_path):
    """Khazanov: herders are not self-sufficient in grain; farmers far from salt (beyond brief.SALT_TRADED_KM on foot) lack it."""
    led = TR.ledger_at(_ctx(tmp_path), 0)
    herd, farm, forage = led[0], led[1], led[2]
    assert herd["lack"]["grain"] > 0.5 and "grain" in herd["lacks"]
    assert farm["surplus"]["grain"] > 0.5 and "grain" not in farm["lack"]
    assert "livestock" in herd["surplus"] and "salt" in herd["surplus"]  # (the salt bed in cell 0, worked once salting is known)
    assert farm["lack"]["salt"] == pytest.approx(0.5, abs=0.02)  # (cell 3 is 900 km from salt: half the farmers, all of them needing it)
    assert herd["lack"].get("salt", 0) == 0  # (the steppe is within a walk of salt)
    assert forage["lack"]["ornaments"] > 0.9 and forage["lack"]["grain"] > 0  # (beads everywhere; starch only beside the farmers in cell 4)
    assert forage["lack"]["grain"] < 0.6  # (cell 5 has no farmers: no starch wanted there)


def test_tin_is_lacked_by_bronze_users_and_held_where_the_ore_is(tmp_path):
    led = TR.ledger_at(_ctx(tmp_path), 0)
    assert led[1]["lack"]["tin"] > 0.85 and led[0]["lack"]["tin"] > 0.85
    tin = TR.ledger_at(_ctx(tmp_path, goods={"tin": np.array([0.0, 0.0, 1.0, 1.0, 0.0, 0.0])}), 0)
    assert "tin" not in tin[1]["lack"] and tin[1]["surplus"]["tin"] > 0.0
    assert led[0]["surplus"]["copper"] > 0 and led[0]["lack"]["copper"] > 0  # (one steppe cell has copper, the other lacks it)


def test_know_gates_close_goods_and_wants_and_a_tech_outside_the_tree_is_no_gate(tmp_path):
    know = {"herder": ["herding", "animal_cattle"], "farmer": ["cultivation", "crop_wheat"], "forager": []}
    led = TR.ledger_at(_ctx(tmp_path, know=know), 0)
    assert "tin" not in led[1]["lack"] and "copper" not in led[0]["surplus"]  # (no bronze, no copper: no metal wanted or worked)
    assert "salt" not in led[0]["surplus"]  # (salt for trade needs salt works)
    assert "ornaments" not in led[2]["lack"]
    ctx = _ctx(tmp_path, know=know)
    ctx.meta["techtree"]["techs"] = [{"id": t} for t in TECHS if t not in ("salting",)]
    assert "salt" in TR.ledger_at(ctx, 0)[0]["surplus"]  # (a tree without salting: no gate)


def test_forager_culture_in_a_farmed_cell_does_not_farm(tmp_path):
    led = TR.ledger_at(_ctx(tmp_path), 0)
    assert led[2]["ways"]["farm"] == 0 and "grain" not in led[2]["surplus"]


def test_dragons_take_tribute_their_kobolds_trade_and_giants_go_by_kind(tmp_path, monkeypatch):
    """D65 (owner, PW-1501): a dragon realm keeps a row (mode tribute, via kobolds) so step 2 can trade its needs through its kobolds;
    an off-ladder kind with a way of its own (hill giants herd) trades, one without takes tribute; neither farms the land under it."""
    ctx = _ctx(tmp_path, extra_lines=("red_dragon", "hill_giant", "fire_giant"), present={"megafauna": {"red_dragon": {}, "hill_giant": {}, "fire_giant": {}}})
    ctx.cultures()["deme_culture"] = [0, 1, 2, 3, 4, 5]
    ctx.arr["demes"] = [np.array([0, 3, 1, 4, 2, 5], np.uint16)]
    led = TR.ledger_at(ctx, 0)
    assert led[3]["mode"] == "tribute" and led[3]["via"] == "kobolds" and led[3]["ways"]["farm"] == 0
    assert TR.line(led[3]).startswith("takes tribute, and its kobolds trade for it")
    assert led[4]["mode"] == "trade" and led[4]["ways"]["herd"] > 0 and led[5]["mode"] == "tribute" and led[5]["via"] is None
    s = TR.summary({"version": 1, "goods": {}, "frames": [{"frame": 0, "ago_kyr": 0.0, "cultures": {str(c): r for c, r in led.items()}}]})
    assert s["by_way"]["tribute"]["n"] == 2
    monkeypatch.setattr(TR, "TRIBUTE_ROWS", False)
    ctx._frame_cache.clear()
    led = TR.ledger_at(ctx, 0)
    assert 3 not in led and 5 not in led and 4 in led


def test_a_small_nudge_moves_the_ledger_a_little(tmp_path):
    a = TR.ledger_at(_ctx(tmp_path), 0)
    b = TR.ledger_at(_ctx(tmp_path, goods={"fertile": np.array([0.2, 0.2, 0.86, 0.9, 0.3, 0.3])}), 0)
    for c in a:
        for side in ("surplus", "lack"):
            for g in set(a[c][side]) | set(b[c][side]):
                assert abs(a[c][side].get(g, 0) - b[c][side].get(g, 0)) <= 0.03
        assert a[c]["lacks"] == b[c]["lacks"]


def test_line_view_and_summary(tmp_path):
    ctx = _ctx(tmp_path)
    led = TR.ledger_at(ctx, 0)
    assert TR.line(led[0]).startswith("has ") and "lacks grain" in TR.line(led[0])
    assert TR.line({"has": [], "lacks": [], "surplus": {}, "lack": {}}) == "has nothing to spare; lacks nothing it knows to want"
    doc = {"version": TR.VERSION, "goods": {}, "cultures": ctx.cultures()["cultures"],
           "frames": [{"frame": 0, "ago_kyr": 0.0, "cultures": {str(c): r for c, r in led.items()}}]}
    v = TR.culture_view(doc, 0)
    assert v["rows"][0]["line"] == TR.line(led[0])
    with pytest.raises(ValueError):
        TR.culture_view(doc, 9)
    s = TR.summary(doc)
    assert s["by_way"]["herd"]["lacks"]["grain"] == 1.0 and s["by_way"]["farm"]["n"] == 1


def test_every_good_has_a_class_and_every_rule_names_a_good():
    assert all(c in TR.CLASSES for _, c, _ in TR.GOODS.values())
    for table in (TR.GATE, TR.WORK, TR.NEED, TR.NEED_GATE, TR.CROPS):
        assert set(table) <= set(TR.GOODS)
    assert {"grain", "salt", "tin", "copper"} <= set(TR.NEED)


def test_server_needs_a_peoples_run():
    from planet import server
    body, code = server.trade("")
    assert code == 400 and "run=" in body["error"]
