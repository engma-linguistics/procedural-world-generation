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
    assert L.RATE_BY_FREQ[5] / L.RATE_BY_FREQ[1] == pytest.approx(L.FREQ_SPREAD) and 3 <= L.FREQ_SPREAD <= 10


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
    assert r5 > 2.5 * r1, (r1, r5)   # rare words go several times faster (FREQ_SPREAD in hazard)


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
    # (derivation and compounding about even: a derivation whose affix does not fit its base is refused, lexicon.affix_fits)
    assert min(events["derive"], events["compound"]) > events["taboo"] and events["derive"] > events["borrow"] > events["taboo"]
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
        assert 4.0 <= st["mean_segments"] <= 7.0 * max(1.0, lex.length_scale), st   # (longer in a small syllable space)
        assert st["max_segments"] <= round(L.MAX_SEG * max(1.0, lex.length_scale)), st   # (the cap follows the syllable space)
        assert st["latest"].get("coin", 0) > 0
        kyr = min(s.kyr for w in lex.words.values() for s in w.etym)
        for w in lex.words.values():
            aff, morph = L._transparent(lex, w, kyr)
            # the same affix never stacks while it is felt; at most MAX_AFFIXES / MAX_MORPHEMES transparent
            assert len(aff) == len(set(aff)) and len(aff) <= L.MAX_AFFIXES and morph <= L.MAX_MORPHEMES + 1, (w.concept, aff)
    notes = [s.note for lex in long_runs for w in lex.words.values() for s in w.etym]
    assert any("(clip " in n for n in notes)


def test_homophone_share_low(long_runs):
    """Repair by renewal and redraws keep homophones (colexifications included) under 12% of concepts on average (one run
    may reach 14%: the groups left after 700 generations are deliberate colexification shifts, whose count swings 8-14%
    between draws, not accidental mergers; 2026-11-04: 10% -> 12% with the shift fallback of the word-families round,
    which turns would-be coinages into CLICS-attested polysemies)."""
    sh = [L.stats(lex)["homophone_share"] for lex in long_runs]
    assert sum(sh) / len(sh) < 0.12 and max(sh) < 0.14, sh
    for lex in long_runs:
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
        # nouns compound; a function word only reinforced by another (THIS + HERE), data/derivations.tsv
        assert L.concept_info(k).pos == "N" or head == k and mod in dict(L.reinforcers()[k]), (k, head, mod)
        if L.sem_class(k) in ("person", "kin") and mod not in {L.resolve(b) for b in L.concept_info(k).base}:
            assert L.sem_class(mod) not in ("person", "kin"), (k, head, mod)   # no MAN + HUSBAND = 'person'
        if mod in L._QUALITY and mod not in dict(L._related(lex, k)):
            assert L.sem_class(k) in L.SPECIES, (k, head, mod)   # no 'green land' for 'stone' (CLICS or a hint may)
        _, msc, mseg = L.limits(inv)   # (the caps follow the syllable space)
        assert L.syllables(w.form) <= msc + 1 and len(w.form) <= mseg
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
    w = L.derive(rng, lex, "PUPPY", inv, 9.0, base="DOG", meaning="little")
    assert w is not None and L.syllables(w.form) <= L.MAX_SYLL and "(clip " in w.etym[-1].note
    lex.set(w)
    assert L.derive(rng, lex, "PUPPY", inv, 9.0, base="PUPPY", meaning="little") is None   # already carries 'little'
    assert L.derive(rng, lex, "WOLF", inv, 9.0, base="DOG", meaning="little") is None   # not a pair of the table


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
    assert L.derive(rng, lex, "PUPPY", inv, 8.0, base="DOG", meaning="little") is None
    L.step(rng, lex, 2000, inv, kyr=7.0)
    assert all(af for af, _ in lex.affixes.values()) and any("renewed" in t for _, t in lex.notes)


def test_stats_and_state_round_trip(concepts):
    rng, inv, lex = _proto(75, concepts)
    L.step(rng, lex, 200, inv, kyr=19.0)
    st = L.stats(lex)
    assert st["words"] == len(lex) and st["processes"]["proto"] > 0 and 0 <= st["homophone_share"] < 1
    back = L.from_json(L.to_json(lex))
    assert back.gen == lex.gen == 200 and back.shifted == lex.shifted


# --- review of run a24559: coinage swamped derivation; inherited core share -------------------------------------------

def test_coinage_does_not_swamp_derivation(long_runs):
    """A replacement falls back to the next plausible source (derive along the table, compound, colexification shift,
    the word's own diminutive or frequentative, a weaker CLICS shift, a loan when a contact lect has the word) before
    a fresh root: over 700 generations with a contact lect, coinage is well under 15% of the replacements (the review of
    run a24559 measured ~33%), and no affix stands on much more than AFFIX_CAP of the words (renewals aside)."""
    tot = collections.Counter()
    for lex in long_runs:
        tot.update(lex.counts)
        for m in lex.affixes:
            # (+0.04: the cap binds at derivation time; compounds, shifts and loans built on a derived word carry its
            # affix in their history too)
            assert L.affix_share(lex, m) <= L.AFFIX_CAP + 0.04, (m, L.affix_share(lex, m))
    n = sum(tot.values())
    assert 0.0 < tot["coin"] / n < 0.12, tot
    assert tot["borrow"] / n < 0.35, tot   # (loans fill gaps, not every gap: BORROW_FALLBACK)
    assert tot["derive"] + tot["renew"] + tot["compound"] + tot["shift"] > 3 * tot["coin"], tot


def test_derive_retry_avoids_homophone(concepts):
    rng, inv, lex = _proto(81, concepts)
    k = next(k for k in lex.words if L.concept_info(k).pos == "V"
             and sum(r.base in lex.words for r in L.derivation_sources(k) if r.base != k) >= 2)
    first = L.derive(rng, lex, k, inv, 19.0)
    base = first.etym[-1].note.split(" + '")[0]
    again = L.derive(rng, lex, k, inv, 19.0, exclude={base})
    assert again is None or again.etym[-1].note.split(" + '")[0] != base
    # a clash with every try leaves no derivation; the replacement then falls back, not straight to a coin
    c = L.concept_info(k)
    src, new = L._replace_word(rng, lex, k, c, "derive", {"derive": 1, "shift": 1, "coin": 1}, inv, 19.0, "L", None,
                               [], None, None)
    assert src in ("derive", "shift", "renew", "coin") and new.concept == k


def test_inherited_core_share(concepts):
    rng, inv, lex = _proto(82, concepts)
    assert L.stats(lex)["inherited_core_share"] == 1.0
    k = next(k for k in lex.words if k in L.CORE100)
    L.coin(rng, lex, k, inv, 19.0, how="root")
    st = L.stats(lex)
    n = sum(1 for c in lex.words if c in L.CORE100)
    assert st["inherited_core_share"] == pytest.approx((n - 1) / n)
    assert not L.inherited(lex.words[k])
    # sound change keeps a word inherited
    k2 = next(c for c in lex.words if c in L.CORE100 and c != k)
    L.apply_rule_to_lexicon(lex, _final_vowel_loss, "S999", 18.0, "L")
    assert L.inherited(lex.words[k2])


# --- word length follows the syllable space (Nettle 1995, 1998) -----------------------------------------------------------

def _shaped(seed, cons: str, vows: str, kind: str):
    """A drawn inventory with the given segments and syllable type ("simple" CV/V, or "moderate" (C)V(C))."""
    rng = np.random.default_rng(seed)
    inv = I.draw_inventory(rng)
    if kind == "simple":
        sh = dict(shapes={"CV": 0.85, "V": 0.15}, max_onset=1, max_coda=0, coda_class="any")
    else:
        sh = dict(shapes={"CV": 0.55, "CVC": 0.33, "V": 0.08, "VC": 0.04}, max_onset=1, max_coda=1, coda_class="any")
    c, v = list(from_ipa(cons)), list(from_ipa(vows))
    inv = replace(inv, consonants=c, vowels=v, tones=[], onset_required=False, **sh,
                  cost={s: 0.0 for s in c + v}, freq={s: 0.5 for s in c + v})
    return rng, inv


SMALL_CV = [("ptkbɾɡ", "aeiou"), ("ptkbsɡʔh", "aio"), ("ptkmnwj", "aeiou")]   # Rotokas-, Piraha-, Hawaiian-sized
BIG_CVC = "ptkbdɡmnŋfsʃvzhlrjwtʃdʒxɣcɲʔ"   # 25 consonants


def test_small_syllable_space_gives_longer_words(concepts):
    """A 6-8 consonant, 3-5 vowel CV language has clearly longer core words than a 25-consonant (C)V(C) one (both
    toneless), frequent words stay shorter than rare ones within each, and the caps grow with the scale."""
    small_syl, big_syl = [], []
    for seed, (c, v) in enumerate(SMALL_CV):
        rng, inv = _shaped(seed, c, v, "simple")
        assert L.syllable_space(inv) < 60 and L.length_scale(inv) > 1.4
        assert L.limits(inv)[0] > L.MAX_SYLL and L.limits(inv)[2] > L.MAX_SEG
        lex = L.proto_lexicon(rng, inv, concepts, 20.0, f"S{seed}")
        st = L.stats(lex)
        small_syl.append(st["core_mean_syllables"])
        f1 = np.mean([L.syllables(w.form) for w in lex.words.values() if w.freq_class == 1])
        f5 = np.mean([L.syllables(w.form) for w in lex.words.values() if w.freq_class == 5])
        assert f1 < f5 - 0.5, (f1, f5)
        assert st["syllable_space"] == pytest.approx(L.syllable_space(inv)) and st["length_scale"] > 1.4
    for seed in range(3):
        rng, inv = _shaped(10 + seed, BIG_CVC, "aeiouɛɔə", "moderate")
        assert L.syllable_space(inv) > 500 and 0.9 < L.length_scale(inv) < 1.15
        lex = L.proto_lexicon(rng, inv, concepts, 20.0, f"B{seed}")
        big_syl.append(L.stats(lex)["core_mean_syllables"])
    assert min(small_syl) > 1.4 * max(big_syl), (small_syl, big_syl)
    assert min(small_syl) > 2.8 and max(big_syl) < 2.3, (small_syl, big_syl)


def test_syllable_space_scale_is_monotone_and_bounded():
    """More consonants, vowels, tones or richer templates: a larger syllable space and a smaller length scale, within
    LENGTH_SCALE_RANGE at both ends (6 C + 3 V CV up to 80 consonants)."""
    sizes = [("ptkbsɡ", "aiu", "simple"), ("ptkbsɡmn", "aeiou", "simple"), ("ptkbsɡmn", "aeiou", "moderate"),
             (BIG_CVC, "aeiouɛɔə", "moderate")]
    sp = [L.syllable_space(_shaped(0, c, v, k)[1]) for c, v, k in sizes]
    sc = [L.length_scale(_shaped(0, c, v, k)[1]) for c, v, k in sizes]
    assert sp == sorted(sp) and sc == sorted(sc, reverse=True), (sp, sc)
    _, tonal = _shaped(0, "ptkbsɡmn", "aeiou", "simple")
    assert L.syllable_space(replace(tonal, tones=[1, 3])) > L.syllable_space(tonal)
    lo, hi = L.LENGTH_SCALE_RANGE
    assert all(lo <= x <= hi for x in sc)
    huge = I.draw_inventory(np.random.default_rng(5), size_hint=(80, 15))
    assert lo <= L.length_scale(huge) <= 1.0


def test_mergers_lengthen_new_words_over_time(concepts):
    """When the inventory shrinks (mergers) the replacement machinery makes longer words for that lect: the same proto
    stepped 700 generations on a merged-down CV inventory renews its words with more syllables than on the full one."""
    rng0, inv = _shaped(3, "ptkbdɡmnsl", "aeiou", "moderate")
    lex0 = L.proto_lexicon(rng0, inv, concepts, 20.0, "M")
    small = replace(inv, consonants=list(from_ipa("ptkm")), vowels=list(from_ipa("aiu")),
                    shapes={"CV": 0.85, "V": 0.15}, max_coda=0)
    assert L.length_scale(small) > L.length_scale(inv) + 0.4
    out = {}
    for name, iv in (("full", inv), ("merged", small)):
        lex = lex0.copy()
        rng = np.random.default_rng(9)
        kyr = 20.0
        for _ in range(39):
            kyr = round(kyr - 0.5, 3)
            L.step(rng, lex, 18.0, iv, kyr=kyr)
        new = [w for w in lex.words.values() if not L.inherited(w)]
        out[name] = np.mean([L.syllables(w.form) for w in new])
        assert lex.length_scale == pytest.approx(L.length_scale(iv))
    assert out["merged"] > out["full"] + 0.5, out


# --- word families and derivation semantics (2026-11-04) -------------------------------------------------------------------

def test_derivation_table_is_sound():
    """Every row of data/derivations.tsv names concepts on the list; agent nouns are persons, gods or animals; 'do' and
    'cause' make verbs, 'like' qualities; content words from function words are rare (three rows of weight 1)."""
    rows = L.derivation_rows()
    assert len(rows) >= 150
    for r in rows:
        t, b = L.concept_info(r.target), L.concept_info(r.base)
        if r.relation == "agent":
            assert L.sem_class(r.target) in ("person", "kin", "god", "animal"), r
        if r.relation in ("do", "cause"):
            assert t.pos == "V", r
        if r.relation == "like":
            assert t.pos in ("A", "FUNC"), r
        if r.relation == "cause":
            assert b.pos == "V", r
        if b.pos == "FUNC" and t.pos != "FUNC":
            assert r.weight < 2, r
    assert sum(1 for r in rows if L.concept_info(r.base).pos == "FUNC" and L.concept_info(r.target).pos != "FUNC") <= 3
    assert L.affix_fits("agent", "HUNTER", "HUNT") and L.affix_fits("little", "STREAM", "RIVER")
    assert L.affix_fits("place", "BED", "SLEEP") and L.affix_fits("thing", "KNIFE", "CUT")
    assert L.affix_fits("like", "RED", "BLOOD") and L.affix_fits("do", "SALT (FOOD)", "SALT")
    assert L.affix_fits("cause", "KILL", "DIE") and L.affix_fits("little", "SUN", "SUN")   # (the diminutive renewal)
    assert not L.affix_fits("agent", "MALE PERSON", "CARRY") and not L.affix_fits("do", "CARRY", "VOMIT")
    assert not L.affix_fits("agent", "HUNTER", "WITH") and not L.affix_fits("thing", "DAY (NOT NIGHT)", "THINK")


def test_derivations_follow_the_table_and_stack_at_most_twice(long_runs, concepts):
    """Every derivation in the long runs is a table pair or a renewal; no agent noun from a function word; a living word
    keeps at most MAX_AFFIXES transparent affixes; proto and daughters alike."""
    n = func = 0
    for lex in long_runs:
        kyr = min(s.kyr for w in lex.words.values() for s in w.etym)
        for w in lex.words.values():
            prev = None
            for st in w.etym:
                if st.process.startswith("derive:") and " + '" in st.note:
                    base = L.resolve(st.note.split(" + '")[0])
                    m = st.process.split(":", 1)[1]
                    n += 1
                    tgt = next(c.id for c in concepts if c.gloss == st.gloss) if not L.is_renewal(st) else base
                    assert L.is_renewal(st) or L.affix_fits(m, tgt, base) or "elaborate" in (prev or ""), (w.concept, st)
                    if L.concept_info(base).pos == "FUNC" and L.concept_info(tgt).pos != "FUNC":
                        func += 1
                        assert m != "agent" or base in ("OTHER",), (w.concept, st)
                if not st.process.startswith("sound_change:"):
                    prev = st.process
            assert L.word_layers(lex, w, kyr)[0] <= L.MAX_AFFIXES
    assert n > 300 and func / n < 0.01, (n, func)


def test_proto_root_families(concepts):
    """A proto grows from a root stock: 15-40% of its words are built from another proto word along the table (core
    Swadesh items mostly simple roots), every word records its root, and some roots carry families of 3+ words; a
    daughter inherits the families (same root ids) and builds new members on them."""
    shares, core_shares, big = [], [], 0
    for seed in range(6):
        rng, inv, lex = _proto(300 + seed, concepts, f"Q{seed}")
        assert all(w.roots and w.roots[0].startswith(f"Q{seed}:") for w in lex.words.values())
        built = [k for k, w in lex.words.items() if any(s.process.startswith("derive:") for s in w.etym)]
        shares.append(len(built) / len(lex.words))
        core_shares.append(sum(k in L.CORE100 for k in built) / len(L.CORE100))
        fam = collections.Counter(w.roots[0] for w in lex.words.values())
        big += sum(1 for v in fam.values() if v >= 3)
        for k in built:
            w = lex.words[k]
            assert w.etym[0].process == "proto" and w.roots[0] == f"Q{seed}:" + L.resolve(w.etym[0].note[len("colexified with "):]
                                                                                       if w.etym[0].note else next(c.id for c in concepts if c.gloss == w.etym[0].gloss))
            assert L.inherited(w)
    assert 0.15 <= np.mean(shares) <= 0.40, shares
    assert np.mean(core_shares) < np.mean(shares) - 0.05, (core_shares, shares)
    assert big >= 6, big
    # daughters inherit the families and add to them
    rng, inv, lex = _proto(310, concepts, "R")
    d = lex.copy("R.1")
    kyr = 20.0
    for _ in range(10):
        kyr = round(kyr - 0.5, 3)
        L.step(rng, d, 18.0, inv, kyr=kyr)
    shared = [k for k in lex.words if d.words[k].roots[:1] == lex.words[k].roots[:1]]
    assert len(shared) > 0.4 * len(lex.words), len(shared)
    new_members = [w for k, w in d.words.items() if w.roots and w.roots[0].startswith("R:") and not L.inherited(w)
                   and any(s.process.startswith("derive:") and s.lect == "R.1" for s in w.etym)]
    assert len(new_members) >= 5, len(new_members)
    back = L.from_json(L.to_json(d))
    assert all(back.words[k].roots == w.roots for k, w in d.words.items())


def test_no_round_trips(long_runs):
    """A word never derives, compounds or shifts back into a meaning it had before (SING > SONG > SING, LEG + CLAW = FOOT >
    FOOT + CLAW = LEG, PUSH > GRIND > PUSH): `lexicon._worn`. Renewals and reinforcements keep the meaning they had."""
    for lex in long_runs:
        for w in lex.words.values():
            steps = [s for s in w.etym if not s.process.startswith("sound_change")]
            for i, s in enumerate(steps):
                if s.process.split(":")[0] in ("derive", "compound", "shift") and i and steps[i - 1].gloss != s.gloss:
                    assert s.gloss not in {t.gloss for t in steps[:i]}, (w.concept, [(t.process, t.gloss) for t in steps])
