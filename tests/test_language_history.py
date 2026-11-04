"""The language driver end to end on a synthetic tiny run (PW-986): 3 peoples, 6 demes, 5 frames, hand-made contacts, one
takeover and one crop spreading over two hops. No stored run is read."""
from __future__ import annotations

import json

import numpy as np
import pytest

from planet.grid import shared_grid
from planet.language import history as H
from planet.language import inputs as I
from planet.language import output as OU

FRAMES = [2.0, 1.5, 1.0, 0.5, 0.0]


def _deme(i, people, born, parent=None, parent_people=None, how="first"):
    return {"id": i, "people": people, "n": i + 1, "name": f"{people} {i}", "short": f"{people} {i}", "place": "the west of Testa",
            "parent": parent, "parent_people": parent_people, "born_kyr": born, "how": how, "ended_kyr": None, "end": None,
            "into": None}


class TinyRun(I.Run):
    """inputs.Run with everything held in memory."""

    def __init__(self):
        g = shared_grid(2)
        self.g, self.n, self.level = g, g.n, 2
        self.cell_km2 = 4 * np.pi * I.R_KM ** 2 / g.n
        self.dir = None
        self.id, self.seed = "tiny", 5
        lines = []
        for k, (lid, origin, gen) in enumerate((("human", "root", 25.0), ("orc", "root", 20.0), ("elf", "arrival", 140.0))):
            lines.append({"id": lid, "index": k, "origin": origin, "parents": [], "group_of": None, "generation_yr": gen,
                          "demography": {"density": 1.0}, "traits": [], "way": None})
        self.meta = {"seed": 5, "lineages": lines, "crops": {"stocks": {"wheat": {"bit": 0, "label": "wheat and barley", "tamed": []}}},
                     "animals": {"stocks": {}}, "present": {"lines": {l["id"]: {"population": 1e6, "area_mkm2": 1.0} for l in lines}},
                     "techtree": {"known": {}}}
        self.run = {"meta": self.meta, "frames": [{"t": -k} for k in FRAMES]}
        self.lines = {l["id"]: l for l in lines}
        self.line_index = {l["id"]: l["index"] for l in lines}
        self.index_line = {l["index"]: l["id"] for l in lines}
        self.demes = [_deme(0, "human", 2.0), _deme(1, "human", 2.0), _deme(2, "orc", 2.0),
                      _deme(3, "human", 1.0, 0, "human", "split_distance"), _deme(4, "orc", 2.0),
                      _deme(5, "elf", 1.5, 2, "orc", "from_people")]
        self.demes_doc = {"demes": self.demes}
        self.cultures_doc = None
        self._settlements = {"sites": [], "tiers": {}}
        self.frames_kyr = list(FRAMES)
        self.run_frame = list(range(len(FRAMES)))
        self._world_layers, self._load_world = None, False
        nf = len(FRAMES)
        self._lead = {"crop_known": np.zeros((nf, g.n), np.uint64), "animal_known": np.zeros((nf, g.n), np.uint8)}
        cells = {0: [0, 1, 2, 3], 1: [3, 4, 5, 6], 2: [6, 7, 8, 9], 3: [10, 11, 12], 4: [12, 13, 14], 5: [30, 31, 32]}
        born_frame = {3: 2, 5: 1}
        pairs_at = {(0, 1): range(nf), (1, 2): range(nf), (0, 3): range(2, nf), (3, 4): range(3, nf)}
        self._frames = []
        for i, k in enumerate(FRAMES):
            fr = I.Frame(k, i)
            for d, cs in cells.items():
                if i >= born_frame.get(d, 0):
                    fr.cells[d] = np.array(cs, np.int64)
                    fr.shares[d] = np.full(len(cs), 60.0)
            fr.pairs = {p: [2, 2, 120.0, 120.0] for p, r in pairs_at.items() if i in r}
            self._frames.append(fr)
        self.__dict__["triggers"] = [I.Trigger("elite", 2, 1, 1.5, 0.0, 1.0, "test: the orcs rule the second human deme")]
        self.__dict__["_arrivals"] = [[], [], [(0, "crop:wheat", None, True)], [(3, "crop:wheat", 0, False)], [(4, "crop:wheat", 3, False)]]
        self.__dict__["_river_data"] = {"id": np.full(g.n, -1), "rivers": {}}
        self.__dict__["_lake_data"] = {"id": np.full(g.n, -1), "lakes": {}}
        self.__dict__["_site_tiers"] = [dict() for _ in FRAMES]


@pytest.fixture(scope="module")
def result():
    old = (H.RATE_SCALE, H.SHIFT_K, H.WORKERS)
    H.RATE_SCALE, H.SHIFT_K, H.WORKERS = 8.0, 1.0, 1
    try:
        res = H.generate(None, run=TinyRun())
        doc = OU.document(res)
        res2 = H.generate(None, run=TinyRun())
        doc2 = OU.document(res2)
    finally:
        H.RATE_SCALE, H.SHIFT_K, H.WORKERS = old
    return res, doc, doc2


def _lects(res):
    return {l.id: l for l in res["lects"]}


def test_buds_inherit(result):
    res, _, _ = result
    L = _lects(res)
    bud = L["d3"]
    assert bud.how == "bud" and bud.parent == "d0"
    # (the bud's oldest words come from the same proto-language as its parent's)
    w = next(iter(bud.lexicon.words))
    assert bud.lexicon.words[w].etym[0].lect == L["d0"].lexicon.words[w].etym[0].lect
    assert L["d5"].how == "arrival" and L[L["d5"].parent].deme is None  # (an arrival's deme parent is ignored)


def test_wave_reaches_contacts_only(result):
    res, _, _ = result
    L = _lects(res)
    deme1 = [l for l in L.values() if l.deme == 1]
    assert any(c["origin_lect"] == "d0" for l in deme1 for c in l.changes), "a rule fired in d0 should spread to its contact"
    for l in L.values():
        if l.deme in (2, 4, 5):
            assert not any(c["origin_lect"] == "d0" for c in l.changes), f"{l.id} never touched d0"


def test_shift_leaves_substrate(result):
    res, _, _ = result
    L = _lects(res)
    sh = [s for s in res["shifts"] if s["deme"] == 1]
    assert sh, "the takeover should shift deme 1"
    s = sh[0]
    new = L[s["to_lect"]]
    assert new.how == "shift" and new.substrate == "d1" and new.parent == L["d2"].id
    assert s["substrate_words"]
    assert any(st.process == "substrate:d1" for w in new.lexicon.words.values() for st in w.etym)


def test_crop_two_hops(result):
    res, doc, _ = result
    L = _lects(res)
    w = L["d4"].lexicon.get("crop:wheat")
    assert w is not None
    borrows = [st.process for st in w.etym if st.process.startswith("borrow:")]
    assert borrows[-1] == "borrow:d3"  # (d3 may renew its loan from d0 before lending it on; the route still links them)
    route = [r for r in doc["food_routes"] if r["concept"] == "crop:wheat"]
    assert len(route) == 1 and route[0]["origin_deme"] == 0 and [h["deme"] for h in route[0]["hops"]] == [3, 4]


def test_schema(result):
    _, doc, _ = result
    for k in ("format", "run", "seed", "start_kyr", "profiles", "lects", "names", "shifts", "food_routes", "families", "checks",
              "romanization", "etym_nodes", "intelligibility", "continua", "snapshot_concepts"):
        assert k in doc, k
    for l in doc["lects"]:
        for k in ("id", "deme", "people", "parent", "how", "substrate", "born_kyr", "died_kyr", "rate", "language", "family_true",
                  "family_scholars", "inventory", "typology", "grams", "paradigms", "lexicon", "changes", "complexity",
                  "shares_history", "snapshots"):
            assert k in l, k
    living = [l for l in doc["lects"] if l["died_kyr"] is None and l["deme"] is not None]
    assert all(l["snapshots"] and not l["snapshots"][0][1].get("d") for l in living)
    w = next(iter(living[0]["lexicon"].values()))
    assert OU.etym_steps(doc, w["etym"])[-1][3] == w["ipa"]
    assert {c["name"] for c in doc["checks"]} and all({"name", "value", "target", "pass", "note"} <= set(c) for c in doc["checks"])
    assert set(doc["families"]) >= {"true", "scholars", "horizon_kyr"}
    json.dumps(doc)


def test_intelligibility(result):
    _, doc, _ = result
    from planet.language import families as FA
    from planet.language.history import snapshot_full
    lj = {l["id"]: l for l in doc["lects"]}
    a = snapshot_full(lj["d0"]["snapshots"])[-1][1]
    assert FA.intelligibility(a, a) == pytest.approx(1.0)
    pair = [p for p in doc["intelligibility"]["pairs"] if p[:2] == ["d0", "d3"]]
    v = pair[0][2]
    assert v[:2] == [None, None] and v[2] > 0.2 and v[2] >= v[4]  # (from the bud on, and drifting apart at 8x the rate)
    cross = [p for p in doc["intelligibility"]["pairs"] if p[:2] == ["d1", "d2"]]
    assert cross and max(x for x in cross[0][2] if x is not None) < 0.2  # (unrelated lects in contact)


def test_deterministic(result):
    _, doc, doc2 = result
    for d in (doc, doc2):
        d.pop("timing", None)
    assert json.dumps(doc, sort_keys=True) == json.dumps(doc2, sort_keys=True)


def test_rules_and_roman(result):
    _, doc, _ = result
    from planet.language.history import snapshot_full
    used = {c[1] for l in doc["lects"] for c in l["changes"]}
    assert used <= set(doc["rules"]) and all(isinstance(v, str) and v for v in doc["rules"].values())
    l = next(l for l in doc["lects"] if l["died_kyr"] is None and l["deme"] is not None)
    for _k, sn in snapshot_full(l["snapshots"]):
        assert len(sn["core_roman"]) == len(sn["core"])
        assert all((a is None) == (b is None) for a, b in zip(sn["core"], sn["core_roman"]))


def test_inventory_cap():
    from planet.language import lect as LC
    from planet.language.percepts import from_ipa
    from planet.language import lexicon as LX
    base = from_ipa("ptkmnsla")
    lex = LX.Lexicon("x", {}, {}, True)
    extra = from_ipa("pʰtʰkʰbdgɓɗqχʁħʕɬɮ")
    forms = [(b, v) for b in base for v in from_ipa("a")] + [(e, from_ipa("a")[0]) for e in extra]
    for k, f in enumerate(forms):
        lex.words[f"W{k}"] = LX.Word(f"W{k}", tuple(f), "N", 3, (), 0.0)
    l = LC.Lect(id="x", deme=0, people="human", parent=None, how="proto", born_kyr=1.0, lexicon=lex,
                base_segs=frozenset(LC._unit(x) for x in base))
    n = l.cap_inventory(0.5)
    cons = {x for w in lex.words.values() for x in w.form if x.kind == "C"}
    assert n > 0 and len(cons) <= max(int(LC.INV_CAP_RATIO * 8), 10)
    assert {x for x in base if x.kind == "C"} <= cons and l.changes[-1]["cause"] == "dispersion" and l.changes[-1]["rule"] == "simplification" and " > " in l.changes[-1]["merged"]
