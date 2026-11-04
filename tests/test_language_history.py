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
        self.__dict__["_arrivals"] = [[], [], [(0, "crop:wheat", None, True, "tamed")], [(3, "crop:wheat", 0, False, "land")],
                                     [(4, "crop:wheat", 3, False, "land")]]
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
    assert v[:2] == [None, None] and v[2] is not None  # (from the bud on)
    cross = [p for p in doc["intelligibility"]["pairs"] if p[:2] == ["d1", "d2"]]
    assert cross and max(x for x in cross[0][2] if x is not None) < 0.2  # (unrelated lects in contact)


INTEL_SEEDS = (1, 2, 3, 4, 5, 6)


def test_intelligibility_drifts_over_seeds():
    """A bud and its parent start close and drift apart at 8x the rate: in aggregate over several seeds (one seed is a coin
    flip at this size: 4 of 8 pass alone)."""
    old = (H.RATE_SCALE, H.SHIFT_K, H.WORKERS)
    H.RATE_SCALE, H.SHIFT_K, H.WORKERS = 8.0, 1.0, 1
    first, last = [], []
    try:
        for sd in INTEL_SEEDS:
            res = H.generate(None, run=TinyRun(), seed=sd, analyse=False)
            v = res["history"].intel[("d0", "d3")]
            first.append(v[2])
            last.append(v[4])
    finally:
        H.RATE_SCALE, H.SHIFT_K, H.WORKERS = old
    assert np.mean(first) > 0.2 and np.mean(first) >= np.mean(last), (first, last)


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
    """No hard cap any more (size is steered by the rule weights): the cap only folds rare new units one axis from a
    commoner unit (onto the cheaper, commoner neighbour) and units spelt alike; the proto's own units stay."""
    from planet.language import lect as LC
    from planet.language.percepts import from_ipa
    from planet.language import lexicon as LX
    base = from_ipa("ptkmnsla")
    lex = LX.Lexicon("x", {}, {}, True)
    extra = from_ipa("pʰtʰkʰbdgɓɗqχʁħʕɬɮ")
    forms = [(b, v) for b in base for v in from_ipa("a")] * 30 + [(e, from_ipa("a")[0]) for e in extra]
    for k, f in enumerate(forms):
        lex.words[f"W{k}"] = LX.Word(f"W{k}", tuple(f), "N", 3, (), 0.0)
    l = LC.Lect(id="x", deme=0, people="human", parent=None, how="proto", born_kyr=1.0, lexicon=lex,
                base_segs=frozenset(LC._unit(x) for x in base))
    n = l.cap_inventory(0.5)
    cons = {x for w in lex.words.values() for x in w.form if x.kind == "C"}
    assert n > 0 and len(cons) < 8 + len(extra)
    assert {x for x in base if x.kind == "C"} <= cons and l.changes[-1]["cause"] == "dispersion" and l.changes[-1]["rule"] == "simplification" and " > " in l.changes[-1]["merged"]
    ph, th = from_ipa("pʰ")[0], from_ipa("tʰ")[0]
    assert ph not in cons and th not in cons  # (rare aspirates folded into the plain stops, one axis away)


def test_size_steer_follows_phoible():
    """The size steer: growing a 21-consonant inventory is neutral-ish, growing a 70-consonant one is rare, shrinking a
    7-consonant one is rare; the anchor holds a line near its own proto size."""
    from planet.language import lect as LC
    assert 0.7 < LC.size_steer("consonants", 21, 1) < 1.3
    assert LC.size_steer("consonants", 70, 1) < LC.size_steer("consonants", 21, 1)
    assert LC.size_steer("consonants", 7, -1) < 0.8
    assert LC.size_steer("consonants", 60, -1, n0=60) < LC.size_steer("consonants", 60, -1)


def test_ease_drag_human_only():
    """The ease drag favours changes toward commoner sounds for a human voice (f > p over p > f) and leaves other voices to
    their own make costs."""
    from planet.language import lect as LC, rules as RU
    from planet.language.percepts import from_ipa
    pf, _ = RU.parse_rule({"id": "a", "rule": "p > f", "cause": "effort", "articulators_or_axes_needed": "lips",
                           "naturalness": "3", "example": "", "family": "lenition"})
    fp, _ = RU.parse_rule({"id": "b", "rule": "f > p", "cause": "effort", "articulators_or_axes_needed": "lips",
                           "naturalness": "3", "example": "", "family": "fortition"})
    segs = frozenset(from_ipa("ptkbdgfvszʃmnŋlrjwhʔaeiou"))
    units = frozenset(LC._unit(x) for x in segs)
    h = [LC.rule_factor(r, segs, units, True) for r in (pf, fp)]
    o = [LC.rule_factor(r, segs, units, False) for r in (pf, fp)]
    assert h[0] < 1.0 < h[1]
    assert o[0] == o[1]


# ------------------------------------------------------------------------------------------- driver fixes (review 2026-11-04)
_NOT_RULES = ("simplification", "koine", "koine.level")


def test_rules_do_not_refire(result):
    """The re-fire memory: no rule more than MAX_FIRES times in a lect's line (harmony once), never twice within REFIRE_KYR."""
    from planet.language import lect as LC
    res, _, _ = result
    cat = {}
    for l in res["lects"]:
        for r in LC.catalogue_for(res["history"].profile(l.profile_key), l.profile_key):
            cat.setdefault(r.id, r)
    for l in res["lects"]:
        line = {}
        for c in l.changes:
            rid = c["rule"]
            if rid in _NOT_RULES or rid.startswith(("accent:", "tone.phonemic")):
                continue
            line.setdefault(LC.base_id(rid), []).append(c["kyr"])
        for b, ks in line.items():
            cap = LC.HARMONY_MAX if b in cat and cat[b].family == "harmony" else LC.MAX_FIRES
            assert len(ks) <= cap, (l.id, b, ks)
            assert all(a - c >= LC.REFIRE_KYR - 1e-9 for a, c in zip(ks, ks[1:])), (l.id, b, ks)
        assert all(len(v) <= LC.MAX_FIRES for v in l.fired.values())


def test_epenthesis_uses_own_vowel():
    from planet.language import inventory as INV, lect as LC, profiles as PR, rules as RU
    inv = INV.draw_inventory(np.random.default_rng(3), PR.HUMAN)
    v = INV.epenthetic_vowel(inv)
    r = next(x for x in RU.catalogue(PR.HUMAN) if x.id == "S123")
    e = LC.epenthesis_variant(r, inv)
    assert e.change.items[0][1] == v and LC.base_id(e.id) == "S123" and v.height >= 5  # (a high vowel, not ə)
    assert LC.epenthesis_variant(next(x for x in RU.catalogue(PR.HUMAN) if x.id == "S042"), inv).id == "S042"


def test_tone_inventory_matches_marks(result):
    res, _, _ = result
    for l in res["lects"]:
        if not l.alive or l.deme is None:
            continue
        marks = {x.tone for w in l.lexicon.words.values() for x in w.form if x.kind == "V" and x.tone}
        assert marks <= set(l.inventory.tones), (l.id, marks, l.inventory.tones)
        assert len(l.inventory.tones) != 1, l.id  # (one tone is no contrast: stripped)


def test_tidy_segments():
    from planet.language import lect as LC
    from planet.language.percepts import from_ipa, to_ipa
    d = from_ipa("dʱ")[0]
    from dataclasses import replace
    assert LC.tidy_segment(replace(d, larynx=1)) == d  # (dʰʱ is the breathy-voiced stop)
    u = from_ipa("ʊ̞")[0]
    low = replace(u, height=max(0, u.height - 1))
    if LC.malformed(low):
        t = LC.tidy_segment(low)
        assert not LC.malformed(t) and t in set(LC.table_segments("V")), to_ipa(t)


def test_one_shift_per_language(result):
    """No re-shift into the language a deme already speaks; a deme's shifts are SHIFT_COOLDOWN_KYR apart."""
    res, _, _ = result
    h = res["history"]
    by: dict = {}
    for s in res["shifts"]:
        by.setdefault(s["deme"], []).append(s["kyr"])
        assert h.root(h.lects[s["from_lect"]]) != h.root(h.lects[s["ruler_lect"]]) or s["from_lect"] == s["ruler_lect"] is False
    for ks in by.values():
        assert all(a - b >= H.SHIFT_COOLDOWN_KYR - 1e-9 for a, b in zip(ks, ks[1:]))
    assert len(by.get(1, [])) == 1


def test_minority_lect_lives_on():
    """A shifted-away lect stays alive (minority speech) while its share holds, and dies when it falls under MINORITY_MIN."""
    run = TinyRun()
    h = H.History(run)
    h.start()
    h.observe(0)
    old, ruler = h.lect_of(1), h.lect_of(2)
    old.shares[ruler.id] = 0.6
    h.shift(1, old, ruler, None, 1)
    new = h.lect_of(1)
    assert new.id != old.id and old.alive and old.minority and new.shares[old.id] == pytest.approx(0.4)
    assert old in h.deme_speech(1)
    run.__dict__["triggers"] = []
    for i in (2, 3, 4):
        h.shift_step(i, run.demes_alive(i))
        if not old.alive:
            break
        assert new.shares[old.id] >= H.MINORITY_MIN
    new.shares[old.id] = 0.05
    h.shift_step(4, run.demes_alive(4))
    assert not old.alive and old.end == "shifted" and old.id not in h.minority.get(1, [])


def test_koine_levels_same_language():
    run = TinyRun()
    h = H.History(run)
    h.start()
    h.observe(0)
    a, b = h.lect_of(0), h.lect_of(1)
    assert h.same_language(a, b, 1)
    run.deme_at_cell = lambda people, cell, i: 0 if people == "human" else None
    old_level = H.KOINE_LEVEL
    H.KOINE_LEVEL = 1.0
    try:
        for c in H.CORE[:10]:  # (make some core words differ)
            w = a.lexicon.get(c)
            if w is not None:
                from dataclasses import replace
                a.lexicon.words[c] = replace(w, form=w.form + w.form[-1:])
        h.koine_level({"site": "s1", "cell": 3, "pop": 1000.0, "holder": "human", "holder_deme": 1,
                       "who": {"human": 0.6, "orc": 0.4}}, b, 1)
    finally:
        H.KOINE_LEVEL = old_level
    ch = [c for c in b.changes if c["rule"] == "koine.level"]
    assert ch and ch[-1]["merged"].startswith("levelled to d0") and ch[-1]["origin_lect"] == "d0"
    assert h.forced[("d0", "d1")] == 1.0
    assert any(st.process == "borrow:d0" for w in b.lexicon.words.values() for st in w.etym)


class CropRun(TinyRun):
    """TinyRun with real crop bits: wheat tamed by deme 0 at 1.0 kyr and known by its neighbour 1 the same frame (deme 3, budded
    from 0 then, inherits it), at 0.5 kyr by deme 4 (sharing a cell with 3), at 0.0 kyr by the out-of-contact elves of deme 5."""

    def __init__(self):
        super().__init__()
        del self.__dict__["_arrivals"]
        g = self.g
        lat, lon = float(np.degrees(np.arcsin(g.centers[1][2]))), float(np.degrees(np.arctan2(g.centers[1][1], g.centers[1][0])))
        self.meta["crops"]["stocks"]["wheat"]["tamed"] = [{"ago_kyr": 1.0, "lat": lat, "lon": lon, "line": "human", "first": True}]
        ck = self._lead["crop_known"]
        for i, cells in ((2, [0, 1, 2, 3, 4, 5]), (3, [12, 13, 14]), (4, [30, 31, 32])):
            ck[i:, cells] |= np.uint64(1)

    def deme_at_cell(self, people, cell, i):
        for d, cs in sorted(self.frame(i).cells.items()):
            if self.people_of(d) == people and cell in cs:
                return d
        return None


def test_crop_arrivals_from_taming_site():
    R = CropRun()
    got = {i: sorted((d, donor, origin, how) for d, c, donor, origin, how in R.crop_arrivals(i) if c == "crop:wheat")
           for i in range(1, 5)}
    assert got[2] == [(0, None, True, "tamed"), (1, 0, False, "land")]  # (the taming deme, and its neighbour from it)
    assert got[3] == [(4, 3, False, "land")]
    assert len(got[4]) == 1 and got[4][0][0] == 5 and got[4][0][3] == "sea" and got[4][0][1] in (0, 1, 3, 4)


def test_food_hop_borrows_current_form(result):
    _, doc, _ = result
    for r in doc["food_routes"]:
        seen = {r["origin_lect"]}
        for hp in sorted(r["hops"], key=lambda x: -x["kyr"]):
            assert hp["from_lect"] in seen or r["origin"] == "inherited by the donor", (r["concept"], hp)
            seen.add(hp["lect"])


def test_l2_share_varies():
    """The adult-L2 proxy: 0 with no other people on the deme's land, rising with their presence, capped at L2_MAX."""
    R = TinyRun()
    assert R.l2_share(0, 3) == 0.0  # (humans among humans only)
    v1, v2 = R.l2_share(1, 3), R.l2_share(2, 3)  # (human deme 1 and orc deme 2 share cells)
    assert 0.0 < v1 <= I.L2_MAX and v1 == pytest.approx(I.L2_SHARED * 1.2 / 4)
    assert v2 == pytest.approx(I.L2_SHARED * 1.2 / 4)
