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
    # (d0 may replace its own word after taming and lend the new one: the taming route then has no hops and the hops go
    # with an "inherited by the donor" route from d0)
    first = [r for r in route if r["origin_deme"] == 0 and r["hops"]]
    assert len(first) == 1 and [h["deme"] for h in first[0]["hops"]][:1] == [3]
    if [h["deme"] for h in first[0]["hops"]] != [3, 4]:
        # d3 replaced its loan before lending it on (`now: replaced`): the second hop starts a route of its own from d3
        assert first[0]["hops"][0]["now"] == "replaced"
        assert [[h["deme"] for h in r["hops"]] for r in route if r["origin_deme"] == 3] == [[4]]
    # each hop says whether the receiver's own etymology still holds it (one source of truth: the receiver's word)
    for hp in (h for r in route for h in r["hops"]):
        assert hp["now"] in ("kept", "replaced", "lost")
        lw = L[hp["lect"]].lexicon.get("crop:wheat")
        held = lw is not None and any(st.process == f"borrow:{hp['from_lect']}" and st.lect == hp["lect"] for st in lw.etym)
        assert (hp["now"] == "kept") == (held and hp["by"] is None)


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


def test_hiatus_is_repaired_after_a_change():
    """A change that leaves hiatus (h > ∅) is followed by the line's hiatus repair (lect.resolve_hiatus): the words end
    with no more hiatus than before it, identical vowels fused (normalize), the repair a recorded change of the hiatus
    family outside the re-fire memory; a daughter keeps the line's preference."""
    from planet.language import lect as LC, rules as RU, profiles as PR
    from planet.language import lexicon as LX
    from planet.language import inventory as INV
    from planet.language.percepts import from_ipa
    forms = ["kaho", "tihe", "puha", "maha", "sohe", "neha", "lihu", "kahi", "tuhe", "sahi"] * 3
    lex = LX.Lexicon("x", {}, {}, True)
    for k, f in enumerate(forms):
        lex.words[f"W{k}"] = LX.Word(f"W{k}", tuple(from_ipa(f)), "N", 3, (), 0.0)
    segs = sorted({x for f in forms for x in from_ipa(f)}, key=repr)
    inv = INV.Inventory(consonants=[x for x in segs if x.kind == "C"] + list(from_ipa("jw")),
                        vowels=[x for x in segs if x.kind == "V"], shapes={"CV": 1.0}, stress="initial")
    l = LC.Lect(id="x", deme=0, people="human", parent=None, how="proto", born_kyr=1.0, lexicon=lex, inventory=inv,
                profile=PR.HUMAN, profile_key="human")
    h_loss = next(r for r in RU.DEMO_RULES if r.id == "lenition.h_loss")
    assert LC.hiatus_count(w.form for w in lex.words.values()) == 0
    made = LC.hiatus_count(LC.normalize(RU.apply(h_loss, w.form), False) for w in lex.words.values())
    assert l.apply_rule(h_loss, 0.5) > 0
    after = [w.form for w in lex.words.values()]
    assert made >= LC.HIATUS_MIN and LC.hiatus_count(after) < made
    assert any(tuple(f) == tuple(from_ipa("ma")) for f in after)  # maha > maa > ma: fused, short (no long vowels here)
    reps = [c["rule"] for c in l.changes[1:]]
    cat = {r.id: r for r in LC.catalogue_for(PR.HUMAN, "human")}
    assert reps and all(cat[LC.base_id(r)].family == "hiatus" for r in reps)
    assert set(l.fired) == {"lenition.h_loss"}
    d = l.copy("y", 0, 0.4, "bud")
    assert d.hiatus_key == "x" and d.hiatus_pref(cat["S126"]) == l.hiatus_pref(cat["S126"])
    # line drift: a daughter keeps its line's family and row preferences, up to its own small budding jitter
    r = cat["S001"]
    ratio = d.line_pref(r) / l.line_pref(r)
    assert ratio == pytest.approx(LC._lognormal(f"y|bud|{r.id}", LC.LINE_BUD_SIGMA))
    assert len({round(LC.Lect(id=f"q{k}", deme=None, people="human", parent=None, how="first", born_kyr=1.0, rate=1.0,
                              inventory=None, lexicon=None).line_pref(r), 6) for k in range(5)}) == 5
    # a one-off row (a chain shift) fires once a line; an ordinary row again after REFIRE_KYR
    grimm = cat["S177"]
    assert LC.one_off(grimm) and not LC.one_off(r)
    d.fired = {grimm.id: [9.0], r.id: [9.0]}
    assert not d.may_fire(grimm, 0.0) and d.may_fire(r, 9.0 - LC.REFIRE_KYR)


def test_normalize_simplifies_initial_geminates():
    from planet.language import lect as LC
    from planet.language.percepts import from_ipa, word_ipa
    assert word_ipa(LC.normalize(tuple(from_ipa("ppata")))) == "pata"
    assert word_ipa(LC.normalize(tuple(from_ipa("nːata")))) == "nata"
    assert word_ipa(LC.normalize(tuple(from_ipa("tapːa")))) == "tapːa"


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


def test_stop_steer_leans_against_stop_loss():
    """The stop steer (lect.STOP_*): with few oral stops in its words a human-voiced lect draws a lenition of stops less
    and a fortition to stops more; at the norm, or for another voice, it does nothing; ʔ is not an oral stop."""
    from planet.language import lect as LC, rules as RU
    from planet.language.percepts import from_ipa
    pf, _ = RU.parse_rule({"id": "a", "rule": "p > f", "cause": "effort", "articulators_or_axes_needed": "lips",
                           "naturalness": "3", "example": "", "family": "lenition"})
    fp, _ = RU.parse_rule({"id": "b", "rule": "f > p", "cause": "effort", "articulators_or_axes_needed": "lips",
                           "naturalness": "3", "example": "", "family": "fortition"})
    segs = frozenset(from_ipa("ptkbdgfvszʃmnŋlrjwhʔaeiou"))
    units = frozenset(LC._unit(x) for x in segs)
    low = LC.stop_bin(0.08)
    assert low < 0 and LC.stop_bin(LC.STOP_NORM) == 0
    base = [LC.rule_factor(r, segs, units, True) for r in (pf, fp)]
    few = [LC.rule_factor(r, segs, units, True, sbin=low) for r in (pf, fp)]
    assert few[0] < base[0] * 0.5 and few[1] > base[1] * 2
    assert [LC.rule_factor(r, segs, units, True, sbin=0) for r in (pf, fp)] == base
    assert [LC.rule_factor(r, segs, units, False, sbin=low) for r in (pf, fp)] == [LC.rule_factor(r, segs, units, False) for r in (pf, fp)]
    assert LC.stop_share([tuple(from_ipa("ʔapa")), tuple(from_ipa("mana"))]) == 1 / 3


def test_keep_steer_damps_losing_a_near_universal_phoneme():
    """The keep steer (lect.KEEP_*): a rule that would leave no p (PHOIBLE 85%) in the lect's words is damped; one that
    leaves some p (a split), or takes a rare sound, is not."""
    from planet.language import lect as LC, rules as RU
    from planet.language.percepts import from_ipa

    def rule(notation):
        r, _ = RU.parse_rule({"id": "x", "rule": notation, "cause": "effort", "articulators_or_axes_needed": "lips",
                              "naturalness": "3", "example": "", "family": "lenition"})
        return r
    forms = [tuple(from_ipa(w)) for w in ("papa", "tapi", "aspa", "θamu")]
    segs = frozenset(x for f in forms for x in f)
    assert LC.keep_part(rule("p > f"), segs, forms) == LC.KEEP_FACTOR
    assert LC.keep_part(rule("p > f / #_, V_"), segs, forms) == 1.0   # aspa keeps its p
    assert LC.keep_part(rule("θ > f"), segs, forms) == 1.0             # θ is no near-universal sound
    assert LC.common(from_ipa("k")[0]) and not LC.common(from_ipa("ʔ")[0])


# ------------------------------------------------------------------------------------------- driver fixes (review 2026-11-04)
_NOT_RULES = ("simplification", "koine", "koine.level")


def test_rules_do_not_refire(result):
    """The re-fire memory: no rule more than MAX_FIRES times in a lect's line (harmony once), never twice within REFIRE_KYR.
    Hiatus repairs (family "hiatus", fired after a change that leaves hiatus: lect.resolve_hiatus) are outside it."""
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
            if LC.base_id(rid) in cat and cat[LC.base_id(rid)].family == "hiatus":
                continue
            line.setdefault(LC.base_id(rid), []).append(c["kyr"])
        for b, ks in line.items():
            cap = LC.HARMONY_MAX if b in cat and cat[b].family == "harmony" else LC.MAX_FIRES
            if b in cat and LC.one_off(cat[b]):
                cap = LC.ONE_OFF_MAX
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


def test_root_families_in_the_document(result):
    """Every stored word names its roots; the document's root table has each main root with the etymology node its root
    starts at (a step of the word's chain: lexicon.root_step), and sister lects of one proto share root ids (the families
    are inherited)."""
    _, doc, _ = result
    roots = doc["roots"]
    seen = 0
    for l in doc["lects"]:
        for c, w in l["lexicon"].items():
            assert w["roots"], (l["id"], c)
            r = roots[w["roots"][0]]
            assert {"node", "lect", "kyr", "concept", "gloss", "ipa", "pos"} <= set(r)
            if r["node"] is not None:
                node = doc["etym_nodes"][r["node"]]
                assert (node[3], r["ipa"]) in {(s[2], s[3]) for s in OU.etym_steps(doc, w["etym"])}
                seen += 1
    assert seen > 100
    by = {l["id"]: l for l in doc["lects"]}
    sis = [(a, b) for a in by.values() for b in by.values() if a["id"] < b["id"] and a["family_true"] == b["family_true"]
           and a["died_kyr"] is None and b["died_kyr"] is None and a["deme"] is not None and b["deme"] is not None]
    assert sis and any(len({w["roots"][0] for w in by[a]["lexicon"].values()} & {w["roots"][0] for w in by[b]["lexicon"].values()}) > 20
                       for a, b in ((x["id"], y["id"]) for x, y in sis))


def test_living_lects_get_sentences_and_grammar_notes(result):
    _, doc, _ = result
    living = [l for l in doc["lects"] if l["died_kyr"] is None and l["deme"] is not None]
    assert living
    for l in living:
        assert isinstance(l.get("sentences"), list) and isinstance(l.get("grammar_notes"), list)
        for s in l["sentences"]:
            assert s["ipa"] and s["en"] and all(len(w) == 2 for w in s["w"])
    assert any(l["sentences"] for l in living)
    dead = [l for l in doc["lects"] if l["died_kyr"] is not None]
    assert all("sentences" not in l for l in dead)


def test_generation_softening():
    """Owner 11-07: per generation (exponent 1) from 28-yr generations up; below, rate x (28 / generation) ** 0.7 per
    year."""
    assert H.change_generations(1000.0, 28.0) == pytest.approx(1000.0 / 28.0)
    assert H.change_generations(1000.0, 56.0) == pytest.approx(1000.0 / 56.0)
    kob = H.change_generations(1000.0, 11.7) / H.change_generations(1000.0, 28.0)
    assert kob == pytest.approx((28.0 / 11.7) ** 0.7) and kob < 28.0 / 11.7


def test_tone_phonemic_once_per_line(result):
    """'tone became phonemic' is recorded only when a lect becomes tonal, never while it already is (a toneless vowel
    in a tone language takes the default tone silently)."""
    res, _, _ = result
    by = _lects(res)
    for l in res["lects"]:
        line, cur, until = [], l, 0.0
        while cur is not None:
            line += [c for c in cur.changes if c["kyr"] >= until - 1e-9 and (c["rule"].startswith("tone.")
                     or str(c.get("merged", "")).startswith("tone marks dropped"))]
            until = cur.born_kyr
            cur = by.get(cur.parent)
        line.sort(key=lambda c: -c["kyr"])
        assert not any(a["rule"].startswith("tone.phonemic") and b["rule"].startswith("tone.phonemic") for a, b in zip(line, line[1:])), l.id


def test_overuse_check_counts_every_lect_but_respects_the_voice():
    """The all-lect overuse check fails a segment in most lects far above PHOIBLE (ɹ), and passes it when the lects' own
    voice profile favours it."""
    from types import SimpleNamespace as NS
    from planet.language import checks as CK, inventory as INV, profiles as PR
    from planet.language.percepts import from_ipa
    cons = [from_ipa(x)[0] for x in "ptkmnl"]
    vows = [from_ipa(x)[0] for x in "aiu"]
    rr = from_ipa("ɹ")[0]

    def lects(prof):
        return [NS(alive=True, deme=i, profile=prof,
                   inventory=INV.Inventory(consonants=cons + ([rr] if i % 2 else []), vowels=vows, shapes={"CV": 1.0}))
                for i in range(20)]
    human = PR.HUMAN
    bad = CK.living_overuse({"lects": lects(human)})
    assert not bad["pass"] and "ɹ" in bad["value"]["overused"]
    import dataclasses
    fond = dataclasses.replace(human, make_cost={**human.make_cost, "approximant": 0.7})
    assert CK.living_overuse({"lects": lects(fond)})["pass"]


_SEED_RUN = """
import hashlib, json, sys
sys.path.insert(0, "tests")
import test_language_history as T
from planet.language import history as H, output as OU
H.RATE_SCALE, H.SHIFT_K, H.WORKERS = 8.0, 1.0, 1
doc = OU.document(H.generate(None, run=T.TinyRun()))
doc.pop("timing", None)
print(hashlib.sha256(json.dumps(doc, sort_keys=True).encode()).hexdigest())
"""


@pytest.mark.slow
def test_deterministic_across_hash_seeds():
    """Two processes with different str hash seeds give the same document: nothing may depend on the iteration order
    of a set or frozenset of strings (a run.json and its rerun differed by shift_paths' order until 2026-11-08)."""
    import os
    import subprocess
    import sys
    out = []
    for seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        r = subprocess.run([sys.executable, "-c", _SEED_RUN], env=env, capture_output=True, text=True, check=True)
        out.append(r.stdout.strip().splitlines()[-1])
    assert out[0] == out[1]
