"""Lexicon: concept list, proto words, calibrated replacement, etymology chains, borrowing, substrate, json."""

import collections
from dataclasses import replace

import numpy as np
import pytest

from planet.language import inventory as I
from planet.language import lexicon as L
from planet.language.percepts import from_ipa

GEN = L.GEN_YR_HUMAN


@pytest.fixture(scope="module")
def concepts():
    return L.concepts()


def _proto(seed, concepts, lect="L", size_hint=None):
    rng = np.random.default_rng(seed)
    inv = I.draw_inventory(rng, size_hint=size_hint)
    return rng, inv, L.proto_lexicon(rng, inv, concepts, 20.0, lect)


def test_concept_list(concepts):
    ids = [c.id for c in concepts]
    assert len(ids) == len(set(ids))
    assert 300 <= len(ids) <= 500
    have = set(ids)
    assert L.CORE100 <= have and len(L.CORE100) == 100
    from planet.lineages import animal_defs, crop_defs, fuels, gods
    for a in crop_defs.TABLE:
        assert f"crop:{a.id}" in have
    for a in animal_defs.TABLE:
        assert L.resolve(f"animal:{a.id}") in have
    for f in fuels.FUELS:
        assert L.resolve(f"fuel:{f}") in have
    for d in gods.DOMAINS:
        assert L.GOD_DOMAIN_CONCEPT[d] in have
    for x in ("ONE", "TEN", "MOTHER", "UNCLE", "NORTH", "UPSTREAM", "STRANGER", "REAL", "MUTE", "SOUR", "BOIL", "MARSH"):
        assert x in have, x
    by = {c.id: c for c in concepts}
    assert all(1 <= c.freq_class <= 5 for c in concepts)
    assert by["SIX"].freq_class <= 2 and by["crop:wheat"].freq_class in (3, 4) and by["FLOOD"].freq_class == 3
    assert not by["crop:wheat"].proto and by["animal:horse"].taboo and by["RIVER"].local


def test_concepts_limited_by_run_meta():
    meta = {"crops": {"stocks": {"wheat": {}, "rice": {}}}, "animals": {"stocks": {"horse": {}}}}
    ids = {c.id for c in L.concepts(meta)}
    assert "crop:wheat" in ids and "crop:maize" not in ids and "animal:horse" in ids and "animal:cattle" not in ids
    assert "DOG" in ids   # a core concept stays


def test_proto_lexicon_shape(concepts):
    syl = collections.defaultdict(list)
    colex = collections.Counter()
    for seed in range(8):
        rng, inv, lex = _proto(seed, concepts)
        assert "crop:wheat" not in lex and "WATER" in lex
        for w in lex.words.values():
            assert I.legal(w.form, inv)
            assert w.etym[0].process == "proto" and w.born_kyr == 20.0
            syl[w.freq_class].append(L._nsyl(w.form))
        for f, cs in lex.homophones().items():
            colex.update(cs)
    assert np.mean(syl[1]) < np.mean(syl[5]) - 0.3   # frequent words shorter
    assert colex["WOOD"] + colex["TREE"] > 0           # TREE/WOOD, the strongest CLICS edge, colexified in some protos


def test_calibration_constant():
    assert abs(L.BASE_REPLACE / L.calibrate_base_replace() - 1) < 0.01
    assert L.RATE_BY_FREQ[5] / L.RATE_BY_FREQ[1] == pytest.approx(10.0)


def test_replacement_rate_matches_calibration(concepts):
    """Swadesh-100 retention over 1000 simulated years at 27.7-yr generations is 86% (replacement 14% within 10%)."""
    n_gen = 1000 / GEN
    kept = total = 0
    by_class = collections.defaultdict(lambda: [0, 0])
    for seed in range(60):
        rng, inv, lex = _proto(100 + seed, concepts, f"L{seed}")
        orig = dict(lex.words)
        # two 500-yr intervals, as the driver batches frame intervals
        for t in (20.0, 19.5):
            L.step(rng, lex, n_gen / 2, inv, kyr=t)
        for c in L.CORE100:
            same = lex.words[c] is orig[c]
            kept += same
            total += 1
            by_class[orig[c].freq_class][0] += same
            by_class[orig[c].freq_class][1] += 1
    replaced = 1 - kept / total
    assert abs(replaced / (1 - L.SWADESH_RETENTION_1KYR) - 1) < 0.10, replaced
    r1 = 1 - by_class[1][0] / by_class[1][1]
    r5 = 1 - by_class[5][0] / by_class[5][1]
    assert r5 > 4 * r1, (r1, r5)   # rare words go much faster (10x in hazard)


def _dummy_rule(form):
    """A visible sound change: voiceless stops voice between vowels."""
    out = list(form)
    for i in range(1, len(out) - 1):
        s = out[i]
        if s.kind == "C" and s.manner == 0 and not s.voice and out[i - 1].kind == "V" and out[i + 1].kind == "V":
            out[i] = replace(s, voice=1)
    return tuple(out)


def _final_vowel_loss(form):
    return form[:-1] if len(form) > 2 and form[-1].kind == "V" and form[-2].kind == "C" else form


def test_etymology_append_only_oldest_first(concepts):
    rng, inv, lex = _proto(7, concepts)
    other = _proto(8, concepts, "M")[2]
    kyr = 20.0
    events = collections.Counter()
    for it in range(30):
        before = dict(lex.words)
        kyr = round(kyr - 0.5, 3)
        events += collections.Counter(p.split(":")[0] for _, p in L.step(rng, lex, 18, inv, contact_words={"M": other}, kyr=kyr, niche_weights={"herder": 1.0, "coast": 0.8}))
        replaced = {k for k in before if lex.words[k] is not before[k]}
        L.apply_rule_to_lexicon(lex, _dummy_rule, "lenition.voicing", kyr)
        L.apply_rule_to_lexicon(lex, _final_vowel_loss, "apocope", kyr)
        for k, old in before.items():
            new = lex.words[k]
            if k in replaced:
                assert new.etym[-1].kyr == kyr or new.etym[-1].process.startswith("sound_change:")
                continue
            # append-only: the old chain is a prefix (the last step may only absorb this interval's sound changes)
            assert new.etym[:len(old.etym) - 1] == old.etym[:-1]
            if new.etym[len(old.etym) - 1] != old.etym[-1]:   # absorbed: same interval, or the end of a long run
                assert old.etym[-1].process.startswith("sound_change:")
                assert new.etym[len(old.etym) - 1].process.startswith("sound_change:")
    n_changed = 0
    for w in lex.words.values():
        ks = [s.kyr for s in w.etym]
        assert ks == sorted(ks, reverse=True), (w.concept, ks)   # kyr ago: oldest first
        assert w.etym[-1].form == w.ipa
        n_changed += any(s.process.startswith("sound_change:") for s in w.etym)
        # one sound-change step per interval at most, and no run longer than MAX_SOUND_RUN
        sc = [(s.kyr, s.lect) for s in w.etym if s.process.startswith("sound_change:")]
        assert len(sc) == len(set(sc))
        run = 0
        for s in w.etym:
            run = run + 1 if s.process.startswith("sound_change:") else 0
            assert run <= L.MAX_SOUND_RUN
    assert n_changed > 20
    procs = collections.Counter(s.process.split(":")[0] for w in lex.words.values() for s in w.etym)
    for p in ("proto", "derive", "compound", "shift", "borrow", "sound_change"):
        assert procs[p] > 0, (p, procs)
    for p in ("derive", "compound", "shift", "borrow", "taboo", "elaborate"):
        assert events[p] > 0, (p, events)
    assert events["derive"] > events["compound"] > events["taboo"] and events["derive"] > events["borrow"] > events["taboo"]
    assert events["coin"] > 0
    assert "MILK (SOURED)" in lex and "FISH (SEA)" in lex


def test_borrowing_nativizes_foreign_segment(concepts):
    rng, inv, lex = _proto(21, concepts, "R", size_hint=(10, 3))
    donor_rng, donor_inv, donor = _proto(22, concepts, "D")
    # a donor word with a segment the receiver lacks
    foreign = tuple(from_ipa("qʼaɬtʃ"))
    assert any(s not in inv.consonants for s in foreign if s.kind == "C")
    word = replace(donor["DOG"], form=foreign)
    w = L.borrow(word, "D", lex, None, inv, 9.0, "trade")
    assert lex["DOG"] is w
    assert I.legal(w.form, inv)
    assert all(s in inv.consonants or I._strip_tone(s) in inv.vowels for s in w.form)
    assert w.etym[-1].process == "borrow:D" and w.etym[-1].lect == "R" and w.etym[:-1] == word.etym


def test_substrate_keeps_river_word(concepts):
    _, inv_old, old = _proto(31, concepts, "OLD")
    _, inv_new, new = _proto(32, concepts, "NEW")
    river, me = old["RIVER"], new["I"]
    kept = L.substrate_transfer(old, new, kyr=4.0)
    assert "RIVER" in kept and "I" not in kept
    assert new["RIVER"].form == river.form and new["RIVER"].etym[-1].process == "substrate:OLD"
    assert new["I"] is me
    # heard through the new inventory: still a river word from the old lect, now legal in the new one
    new2 = L.proto_lexicon(np.random.default_rng(33), inv_new, concepts, 20.0, "NEW2")
    L.substrate_transfer(old, new2, ["RIVER"], kyr=4.0, inv=inv_new)
    assert I.legal(new2["RIVER"].form, inv_new) and new2["RIVER"].etym[-2] == river.etym[-1]


def test_taboo_and_coin(concepts):
    rng, inv, lex = _proto(41, concepts)
    w = L.taboo_word(rng, lex, "BEAR", inv, 5.0)
    assert w.etym[-1].process == "taboo" and "one" in w.etym[-1].note
    c = L.coin(rng, lex, "crop:wheat", inv, 9.0)
    assert lex["crop:wheat"] is c and I.legal(c.form, inv)
    assert c.etym[-1].process.split(":")[0] in ("derive", "compound", "coin")


def test_aliases_and_copy(concepts):
    _, inv, lex = _proto(51, concepts)
    assert lex["fuel:wood"] is lex["WOOD"] and "good:salt" in lex
    cp = lex.copy("C2")
    L.apply_rule_to_lexicon(cp, _final_vowel_loss, "apocope", 10.0)
    assert any(cp.words[k].form != lex.words[k].form for k in lex.words)
    assert all(not any(s.process.startswith("sound_change") for s in w.etym) for w in lex.words.values())


def test_json_round_trip(concepts):
    rng, inv, lex = _proto(61, concepts)
    L.step(rng, lex, 40, inv, kyr=19.0)
    back = L.from_json(L.to_json(lex))
    assert back.words.keys() == lex.words.keys()
    for k, w in lex.words.items():
        assert back[k].form == w.form and back[k].etym == w.etym and back[k].freq_class == w.freq_class
    assert back.affixes == lex.affixes and back.head_first == lex.head_first
    small = L.to_json(lex, full=False)["words"]
    assert set(small) == set(L.CORE100) & set(lex.words)


def test_proto_lexicon_robust_over_seeds(concepts):
    """50 seeds, on the full list and on random partial lists (colexification sources missing): no error, every concept
    worded, colexified words share an existing word; head_first stays writable (grammar.step sets it)."""
    for seed in range(50):
        rng = np.random.default_rng(1000 + seed)
        inv = I.draw_inventory(rng)
        cl = concepts if seed % 2 == 0 else [c for c in concepts if rng.random() < 0.6]
        lex = L.proto_lexicon(rng, inv, cl, 20.0, f"P{seed}")
        assert {c.id for c in cl if c.proto} == set(lex.words)
        forms = {}
        for w in lex.words.values():
            forms.setdefault(w.form, []).append(w.concept)
            note = w.etym[0].note
            if note.startswith("colexified with "):
                assert w.form == lex.words[note[len("colexified with "):]].form
        lex.head_first = not lex.head_first
        assert lex.copy().head_first == lex.head_first


# --- review fixes: length, compound semantics, deletion, homophony, shift chains -----------------------------------------

def _run(seed, concepts, gens=700):
    rng, inv, lex = _proto(seed, concepts)
    other = _proto(seed + 50, concepts, "M")[2]
    kyr, done = 20.0, 0.0
    while done < gens:
        n = min(18.0, gens - done)
        done += n
        kyr = round(kyr - 0.5, 3)
        L.step(rng, lex, n, inv, contact_words={"M": other}, kyr=kyr, niche_weights={"herder": 1.0})
    return lex


@pytest.fixture(scope="module")
def long_runs(concepts):
    return [_run(s, concepts) for s in (1, 2, 3)]


def test_word_length_stays_bounded(long_runs):
    """700 generations (about 20 kyr of human history): replacement no longer grows words (derive/compound clip their
    bases, prefer short ones, refuse a base that already has the affix; fresh roots have a share)."""
    for lex in long_runs:
        st = L.stats(lex)
        assert 4.0 <= st["mean_segments"] <= 7.0, st
        assert st["max_segments"] <= 12, st
        assert st["latest"].get("coin", 0) > 0
        for w in lex.words.values():
            ds = collections.Counter(s.process for s in w.etym if s.process.startswith("derive:"))
            assert all(v == 1 for v in ds.values()), (w.concept, ds)   # the same affix never stacks
    notes = [s.note for lex in long_runs for w in lex.words.values() for s in w.etym]
    assert any("(clip " in n for n in notes)


def test_homophone_share_low(long_runs):
    """Repair by renewal and redraws keep homophones (colexifications included) under 10% of concepts."""
    for lex in long_runs:
        assert L.stats(lex)["homophone_share"] < 0.10
        assert all(len(v) <= 3 for v in lex.homophones().values())


def test_compounds_are_plausible(concepts):
    """200 compounds: no verb ever compounds or pairs with a colour, kin terms and animals take their class head."""
    rng, inv, lex = _proto(71, concepts)
    ks = sorted(lex.words)
    made = []
    while len(made) < 200:
        k = ks[int(rng.integers(len(ks)))]
        w = L.compound(rng, lex, k, inv, 10.0)
        if w is None:
            continue
        head, mod = w.etym[-1].process[len("compound:"):].split("+")
        made.append((k, head, mod, w))
    for k, head, mod, w in made:
        parts = {L.sem_class(x) for x in (k, head, mod)}
        assert not ("verb" in parts and "colour" in parts), (k, head, mod)
        assert L.concept_info(k).pos == "N"
        assert L.syllables(w.form) <= L.MAX_SYLL_COMPOUND + 1 and len(w.form) <= L.MAX_SEG
        if L.sem_class(k) == "animal" and "ANIMAL" in lex and k != "ANIMAL":
            assert head in ("ANIMAL", *L.concept_info(k).base), (k, head)
        if L.sem_class(k) == "kin":
            assert head in ("PERSON", "MAN", "WOMAN", "MALE PERSON", *L.concept_info(k).base), (k, head)
    assert L.compound(rng, lex, "HUNT", inv, 10.0) is None and L.compound(rng, lex, "RED", inv, 10.0) is None
    w = L.compound(rng, lex, "MILK (SOURED)", inv, 10.0, head="MILK", modifier="SOUR")   # explicit parts still work
    assert w is not None and w.etym[-1].process == "compound:MILK+SOUR"


def test_derive_clips_long_base(concepts):
    rng, inv, lex = _proto(72, concepts)
    long = tuple(from_ipa("katupamilo"))
    lex.set(replace(lex["DOG"], form=long))
    w = L.derive(rng, lex, "WOLF", inv, 9.0, base="DOG", meaning="little")
    assert w is not None and L.syllables(w.form) <= L.MAX_SYLL and "(clip " in w.etym[-1].note
    lex.set(w)
    assert L.derive(rng, lex, "BEAR", inv, 9.0, base="WOLF", meaning="little") is None   # already carries 'little'


def test_shift_at_most_once_per_gap(concepts):
    rng, inv, lex = _proto(73, concepts)
    k = next(c for c in sorted(lex.words) if lex[c].pos == "N"
             and any(n in lex.words and lex[n].pos == "N" for n, _ in L.clics_neighbours(c, L.BUILD_MIN_FAMILIES)))
    lex.gen = 100.0
    old = lex[k]
    w = L.shift_word(rng, lex, k, 5.0)
    assert w is not None and w.etym[-1].process.startswith("shift:")
    lex.set(w)
    assert L.shift_word(rng, lex, k, 5.0) is None          # not again within SHIFT_GAP generations
    lex.set(old)                                           # (and not onto a word already doing double duty)
    assert L.shift_word(rng, lex, k, 5.0) is None
    lex.gen += L.SHIFT_GAP
    assert L.shift_word(rng, lex, k, 4.0) is not None


def test_deleted_word_kept_minimal_and_affix_renewed(concepts):
    rng, inv, lex = _proto(74, concepts)
    w0 = lex["WATER"]
    n = L.apply_rule_to_lexicon(lex, lambda f: (), "wipe", 8.0)
    assert n > 0
    w = lex["WATER"]
    assert len(w.form) == 1 and w.etym[-1].note == "kept minimal" and w.form[0] in w0.form
    assert all(w.form for w in lex.words.values())
    assert all(not af for af, _ in lex.affixes.values()) and any("worn to nothing" in t for _, t in lex.notes)
    assert L.derive(rng, lex, "WOLF", inv, 8.0, base="DOG", meaning="little") is None
    L.step(rng, lex, 2000, inv, kyr=7.0)
    assert all(af for af, _ in lex.affixes.values()) and any("renewed" in t for _, t in lex.notes)


def test_stats_and_state_round_trip(concepts):
    rng, inv, lex = _proto(75, concepts)
    L.step(rng, lex, 200, inv, kyr=19.0)
    st = L.stats(lex)
    assert st["words"] == len(lex) and st["processes"]["proto"] > 0 and 0 <= st["homophone_share"] < 1
    back = L.from_json(L.to_json(lex))
    assert back.gen == lex.gen == 200 and back.shifted == lex.shifted
