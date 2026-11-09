"""planet.language.romanize: the house spelling (not slow)."""
import collections
import itertools
from dataclasses import replace

import pytest

from planet.language import romanize as R
from planet.language.percepts import Segment, core, from_ipa, is_nonhuman, symbols, to_ipa


def test_table_rows_parse():
    for ipa in R.table():
        assert len(from_ipa(ipa)) == 1, ipa


def test_rulings():
    r = R.romanize
    assert r("ŋa") == "nga" and r("ʃa") == "sha" and r("tʃa") == "cha" and r("ʒa") == "zha" and r("dʒa") == "ja"
    assert r("θa") == "tha" and r("ða") == "dha" and r("xa") == "kha" and r("ɣa") == "gha"
    assert r("qa") == "qa" and r("χa") == "qha" and r("ʁa") == "ġa" and r("ɢa") == "gqa"
    assert r("ʔa") == "'a" and r("aː") == "aa" and r("kʼa") == "k'a"
    assert r("ǃa") == "ǃa" and r("ǀa") == "ǀa" and r("ǁa") == "ǁa" and r("ǃːa") == "ǃǃa"  # click letters U+01C0-01C3
    assert r("á") == "á" and r("à") == "à" and r("a˧") == "a"
    assert r("ənə", {"schwa"}) == "ënë" and r("ənə", set()) == "ene"
    assert r("pʰapa") == "paba" and r("pʰa") == "pa"  # aspiration written only where it contrasts (pinyin b/p: no voiced stops)
    assert r("pʰapaba") == "phapaba"
    assert r("θa", {"aspiration"}) == "þa" and r("χa", {"aspiration"}) == "x̣a"  # no clash with th, qh as aspirates


def test_velar_and_uvular_never_share():
    for cs in (set(), {"aspiration"}):
        for v, u in (("x", "χ"), ("ɣ", "ʁ"), ("k", "q"), ("ɡ", "ɢ"), ("ŋ", "ɴ")):
            assert R.romanize(v + "a", cs) != R.romanize(u + "a", cs)


def test_hyphen_where_a_digraph_would_mislead():
    assert R.romanize("nɡa", inventory=from_ipa("nŋɡa")) == "n-ga"
    assert R.romanize("nɡa", inventory=from_ipa("nɡa")) == "nga"  # no ŋ in the lect: nothing to misread
    assert R.romanize("tsa", inventory=from_ipa("tsa")) == "tsa"
    assert R.romanize("t.sa", inventory=from_ipa("tsa ts")) == "t-sa"
    assert R.romanize("kʔa", inventory=from_ipa("kʔakʼ")) == "k-'a"


def test_title_name():
    assert R.title_name("'aba") == "'Aba" and R.title_name("ǃxu") == "ǃXu" and R.title_name("ørn") == "Ørn"
    assert R.title_words(["hili", "kang"]) == "Hili Kang" and R.title_words(["opa'i", "e"]) == "Opa'i-e"
    assert R.title_words(["e", "iva"]) == "E-Iva" and R.title_words(["banu", "hashim"]) == "Banu Hashim"


def _pool():
    base = [r.seg for r in symbols() if r.seg.kind == "C" and not is_nonhuman(r.seg)]
    pool = set(base)
    for b in base:
        if b.manner in (0, 1, 2) and b.place != 8:
            pool.add(replace(b, phonation=1) if b.voice else replace(b, larynx=1))
            if not b.voice:
                pool.add(replace(b, larynx=2))
            pool.add(replace(b, secondary=1))
            if b.place != 4:
                pool.add(replace(b, secondary=2))
        pool.add(replace(b, length=1))
    return pool


CONTRAST_SETS = [frozenset(), frozenset({"aspiration"}), frozenset({"dark_l", "beta", "breathy_h"}),
                 frozenset({"aspiration", "dark_l", "beta", "breathy_h"}), R.ALL_CONTRASTS - {"tone"}, R.ALL_CONTRASTS]


@pytest.mark.parametrize("cs", CONTRAST_SETS, ids=lambda c: "+".join(sorted(c)) or "none")
def test_injective_over_consonants(cs):
    """No two distinct consonants share a spelling under one contrast set, except the documented MERGES (and the contrasts
    the set says the lect lacks: aspiration not written, dentals not marked)."""
    groups = collections.defaultdict(set)
    for s in _pool():
        if "aspiration" not in cs and (s.larynx == 1 or s.phonation == 1):
            continue
        if "dental" not in cs and s.place == 1 and to_ipa(core(s)) not in R.table():
            continue
        groups[R.spell(s, cs)].add(to_ipa(s))
    bad = {k: v for k, v in groups.items() if any(not R.merged(a, b, cs) for a, b in itertools.combinations(sorted(v), 2))}
    assert not bad, bad


VOWEL_SETS = [frozenset(), frozenset({"schwa"}), frozenset({"open_e", "open_o", "back_a", "lax_i", "lax_u"}),
              frozenset({"open_e", "open_o", "back_a", "lax_i", "lax_u", "tone"}), R.ALL_CONTRASTS - {"tone"}, R.ALL_CONTRASTS]


@pytest.mark.parametrize("cs", VOWEL_SETS, ids=lambda c: "+".join(sorted(c)) or "none")
def test_injective_over_vowels(cs):
    groups = collections.defaultdict(set)
    tones = (0, 1, 3) if "tone" in cs else (0,)
    for r in symbols():
        if r.seg.kind == "V" and not is_nonhuman(r.seg) and r.seg.tone == 0:
            for t in tones:
                groups[R.spell(replace(r.seg, tone=t), cs)].add(r.symbol + str(t))
    bad = {k: v for k, v in groups.items()
           if any(not R.merged(a[:-1], b[:-1], cs) or a[-1] != b[-1] for a, b in itertools.combinations(sorted(v), 2))}
    assert not bad, bad


def test_reader_spellings():
    """ASCII first: the open, back and lax vowels and the odd consonants are plain letters unless the lect contrasts them."""
    r = R.romanize
    assert r("ɛ") == "e" and r("ɔ") == "o" and r("ɑ") == "a" and r("ɒ") == "a" and r("ɪ") == "i" and r("ʊ") == "u"
    assert r("ɫa") == "la" and r("βa") == "va" and r("ɦa") == "ha"
    assert r("eɛ") == "eè" and r("oɔ") == "oò" and r("aɑ") == "aå" and r("iɪ") == "iì" and r("uʊ") == "uù"
    assert r("é ɛ̀ ɔ́ o") == "éẹ̀ọ́o"  # a tonal lect: dot below, so the grave stays a tone mark
    assert r("lalɫa") == "lal-lla" and r("lːaɫa") == "l·lalla"  # ll = ɫ; a long l takes the Catalan middle dot
    assert r("vaβa") == "vabha" and r("vaβapʰap", {"beta", "aspiration"}) == "vaḇaphap"
    assert r("hɦa") == "h-hha" and r("hːaɦa") == "h·hahha"
    assert r("ə") == "e" and r("eə") == "ea" and r("eəa") == "eëa"
    assert r("ã") == "ã"  # nasal vowels: always a tilde


def test_nonhuman_spellings_are_ascii_letters():
    """The book reader must be able to say a non-human sound: ASCII letters only, the exact symbol stays in the IPA."""
    seen = {}
    for row in symbols():
        if is_nonhuman(row.seg):
            sp = R.romanize(row.symbol)
            assert sp.isascii() and sp.isalpha(), (row.symbol, sp)
            assert sp not in seen, (row.symbol, seen.get(sp), sp)
            seen[sp] = row.symbol
    assert R.romanize("a‼") == "arh" and R.romanize("aᵣ") == "avr" and R.romanize("aᴖ") == "awh"
    assert R.romanize("a˯") == "amh" and R.romanize("i˰") == "iih" and R.romanize("ʞa") == "cka"
    assert R.romanize("ma‼") == "marh" and R.romanize("ʁ‼a") == "grha"
    assert R.romanize("ar", inventory=from_ipa("aᵣ a r")) == "arr" and R.romanize("aᵣ") != R.romanize("ar")  # purr is not the trill


def test_contrasts_of():
    assert R.contrasts_of(from_ipa("ppʰa")) == {"pinyin"} and R.contrasts_of(from_ipa("ppʰba")) == {"aspiration"}
    assert R.contrasts_of(from_ipa("eəa")) == {"schwa"} and R.contrasts_of(from_ipa("eə")) == {"schwa_a"}
    assert R.contrasts_of(from_ipa("eɛ")) == {"open_e"} and R.contrasts_of(from_ipa("ɛ")) == set()
    assert R.contrasts_of(from_ipa("lɫ")) == {"dark_l"} and R.contrasts_of(from_ipa("ɫ")) == set()
    assert R.contrasts_of(from_ipa("á")) == {"tone"}
    assert "dental" in R.contrasts_of(from_ipa("t̪t"))
    assert R.contrasts_of(from_ipa("pʰa")) == set()


# ---------------------------------------------------------------------------------------------- book mode
def test_book_mode_names_are_sayable():
    """The names a book reader choked on (full spelling Müdhœ̃̀œ̃'áĩ́ĩ, Pë̀ġàkìʿà, Sǘpũ̀vò) come out short and nearly ASCII."""
    b = lambda x: R.romanize(x, book=True)
    assert b("my˧dʱœ̃ː˨ʔa˦ĩː˦") == "mudoon'aiin"  # every long vowel doubled, nasal = +n, ü beside i folds (no u: lossless)
    assert b("pə˨ʁa˨ki˨ʕa˨") == "peġakiʿa"  # no tone, schwa e, the uvular ġ kept
    assert b("sy˦pũ˨vo˨") == "supunvo"  # no i in the word: y is u
    for x in ("my˧dʱœ̃ː˨ʔa˦ĩː˦", "pə˨ʁa˨ki˨ʕa˨", "sy˦pũ˨vo˨"):
        assert R.diacritics(b(x)) <= 1 and len(b(x)) <= len(R.romanize(x))


def test_book_mode_rules():
    b = lambda x, cs=None, inv=None: R.romanize(x, cs, inv, book=True)
    assert b("á à ǎ a˧") == "aaaa"  # no tone
    assert b("ãta") == "anta" and b("ãma") == "ama" and b("ãŋa") == "anga"  # nasal: + n, plain before a nasal
    assert "̃" not in b("ãẽĩõũ")
    assert b("aːtaː") == "aataa" and b("tːa") == "tta"  # every long vowel doubled; a long consonant doubled
    assert b("ənə") == "ene" and b("eəa") == "eea"  # schwa e, no diaeresis
    assert b("ɛɔɪʊɑ") == "eoiua" and b("eɛ oɔ iɪ") == "eeooii"  # the open/lax/back vowels always plain
    assert b("y") == "u" and b("iuy") == "iuü" and b("iy") == "iu" and b("ø") == "o" and b("eoø") == "eoö" and b("eoœ") == "eoö" and b("eø") == "eo"
    assert b("ʔaʔa") == "a'a"  # no word-initial glottal stop
    assert b("ʃaʈaʂa") == "shatasa"  # no t or s in the lect: ṭ and ṣ fold to t and s, merging nothing
    assert b("ʃaʈaʂa", None, from_ipa("ʃ ʈ ʂ t s a")) == "shaṭaṣa" and b("ʈata", None, from_ipa("ʈ ʂ t s a")) == "ṭata"  # one spelling per phoneme
    assert b("ʃa", {"aspiration"}) == "sha"  # (book: the digraph even where the workbench writes š)
    assert b("lːaɫa") == "llalla"  # no Catalan dot
    assert b("ɲ̟a") == "nya" and b("ʊ̞ta") == "uta"  # no house letter: folded


def test_book_mode_keeps_the_uvulars():
    b = lambda x, cs=None: R.romanize(x, cs, book=True)
    assert b("qa") == "qa" and b("χa") == "qha" and b("ʁa") == "ġa" and b("ɢa") == "gqa" and b("ɴa") == "nqa"
    assert b("χa", {"aspiration"}) == "x̣a" and b("ʃaʁa") == "shaġa" and b("ʈaʁaʁa", None) == "taġaġa"
    for cs in (set(), {"aspiration"}):
        for v, u in (("x", "χ"), ("ɣ", "ʁ"), ("k", "q"), ("ɡ", "ɢ"), ("ŋ", "ɴ")):
            assert b(v + "a", cs) != b(u + "a", cs)


def test_book_mode_diacritics_rare_on_generated_words():
    import numpy as np
    from planet.language import inventory as INV
    from planet.language import lexicon as LX
    from planet.language import profiles as PR
    full, book = [], []
    for seed in range(10):
        rng = np.random.default_rng(seed)
        inv = INV.draw_inventory(rng, PR.HUMAN)
        lex = LX.proto_lexicon(rng, inv, LX.concepts(None), 2.0, "d")
        segs = list(INV.segments(inv))
        cs = R.contrasts_of(segs)
        for w in list(lex.words.values())[:20]:
            full.append(R.romanize_word(tuple(w.form), cs, segs))
            book.append(R.romanize_word(tuple(w.form), cs, segs, book=True))
    assert len(book) == 200
    assert sum(map(R.diacritics, book)) / len(book) < 0.3
    assert all(R.diacritics(x) <= 2 * R.BOOK_DIACRITIC_BUDGET or any(g in R.BOOK_KEEP for g in R._graphemes(x)) for x in book)
    # (at most one outlier in 200: the palatal affricate ɟʝ spells 'gyyh' in book mode, šẽɟʝo > shen-gyyho, seen once
    # when word lengths started following the syllable space and the draws moved)
    assert sum(len(b) > len(f) + 4 for f, b in zip(full, book)) <= 1


def test_rhotics_and_book_affricates():
    """Full mode tells the approximant ɹ from the tap ɾ and the trill r (owner 11-04); book mode spells ɟʝ as gy, not gyyh."""
    full = {x: R.romanize("a" + x + "a") for x in ("ɹ", "ɾ", "r")}
    assert len(set(full.values())) == 3 and full["ɾ"] == "ara" and full["r"] == "arra" and full["ɹ"] == "ařa"
    assert not R.merged("ɹ", "ɾ") and R.merged("ɾː", "r")
    b = lambda x: R.romanize(x, book=True)
    assert b("aɟʝa") == "agya" and b("acça") == "akya" and b("aɹa") == "ara" and "gyyh" not in b("šẽɟʝo".replace("š", "ʃ"))


def _ipa_block(s: str) -> list[str]:
    return [ch for ch in s if ("ɐ" <= ch <= "ʯ" or "ᴀ" <= ch <= "ᶿ") and ch != "ʘ"]  # (ʘ: the click letter, like ǀ ǃ ǁ ǂ)


def _vowel_space():
    """Every vowel the percept space can produce: all height x back x round cells, plus every symbols.tsv vowel."""
    out = {Segment("V", voice=1, height=h, back=b, round=r) for h in range(7) for b in range(5) for r in (0, 1)}
    out |= {r.seg for r in symbols() if r.seg.kind == "V" and not is_nonhuman(r.seg) and r.seg.tone == 0}
    return sorted(out, key=to_ipa)


@pytest.mark.parametrize("cs", CONTRAST_SETS, ids=lambda c: "+".join(sorted(c)) or "none")
def test_no_ipa_letters_in_spellings(cs):
    """Every vowel (with its shift marks ̞ ̠ ̟, length, nasality) and every consonant the percept space makes has a Latin
    spelling in both modes: no IPA-block letter leaks into a book or a workbench spelling."""
    leaks = {}
    for s in itertools.chain(_vowel_space(), _pool(), (r.seg for r in symbols() if r.seg.kind == "C" and not is_nonhuman(r.seg))):
        for variant in (s, replace(s, length=1)) + ((replace(s, nasal=1),) if s.kind == "V" else ()):
            for book in (False, True):
                sp = R.spell(variant, cs, book=book)
                if _ipa_block(sp):
                    leaks[(to_ipa(variant), book)] = sp
    assert not leaks, sorted(leaks.items())


@pytest.mark.parametrize("cs", VOWEL_SETS, ids=lambda c: "+".join(sorted(c)) or "none")
def test_injective_over_the_whole_vowel_space(cs):
    """Full mode: two vowels share a spelling only by a documented merger (the shifted vowels keep their marks)."""
    groups = collections.defaultdict(set)
    for s in _vowel_space():
        groups[R.spell(s, cs)].add(to_ipa(s))
    bad = {k: v for k, v in groups.items() if any(not R.merged(a, b, cs) for a, b in itertools.combinations(sorted(v), 2))}
    assert not bad, bad


def test_book_one_spelling_per_phoneme_per_lect():
    """Book mode spells a phoneme the same way in every word of a lect: the diacritic budget is per lect, not per word."""
    inv = from_ipa("ʈ ʂ ʃ t s a i u y ħ h")
    cs = R.contrasts_of(inv)
    folds = R.book_folds(inv, cs, {from_ipa("ʈ")[0]: 50, from_ipa("ʂ")[0]: 40, from_ipa("ħ")[0]: 1, from_ipa("y")[0]: 30})
    kept = {g for g in ("ṭ", "ṣ", "ḥ", "ü") if g not in folds}
    assert len(kept) == R.BOOK_DIACRITIC_BUDGET and kept == {"ṭ", "ṣ"}  # the two commonest keep their marks
    sp = lambda x: R.romanize(x, cs, inv, book=True, folds=folds)
    assert sp("ʈaʈa") == "ṭaṭa" and sp("taʈa") == "taṭa" and sp("ħaħa") == "haha"
    o = R.Orthography(inv, counts={from_ipa("ʈ")[0]: 50, from_ipa("ʂ")[0]: 40})
    assert o.lossy and all(a for _g, a in o.lossy)


def test_spell_phonemes_not_allophones():
    """An allophone is spelled as its phoneme (Kunrei, Spanish b d g); an inserted glottal stop is not written."""
    k, gh = from_ipa("k")[0], from_ipa("ɣ")[0]
    glottal = from_ipa("ʔ")[0]
    o = R.Orthography(from_ipa("kɣaʔi"), allophones={gh: (k, "intervocalic"), glottal: (None, "glottal_onset")})
    assert o.word(from_ipa("aɣa")) == "aka" and o.word(from_ipa("ʔaka"), book=True) == "aka"
    assert gh not in o.inv and "aspiration" not in o.cs


def test_pinyin_aspiration_keeps_the_fricative_digraphs():
    """A lect that contrasts aspiration but has no voiced stops writes b/p (pinyin, Korean RR): one aspirate no longer flips
    sh th kh to š þ x across the lexicon."""
    inv = from_ipa("p pʰ t tʰ k ʃ θ x a")
    cs = R.contrasts_of(inv)
    assert "pinyin" in cs and "aspiration" not in cs
    r = lambda x: R.romanize(x, cs, inv)
    assert r("pʰa") == "pa" and r("pa") == "ba" and r("ʃa") == "sha" and r("θa") == "tha" and r("xa") == "kha"
    assert len({r(x) for x in ("pa", "pʰa", "ta", "tʰa", "ka")}) == 5
    assert "aspiration" in R.contrasts_of(from_ipa("ppʰba"))  # voiced stops too: aspiration is written with h


def test_nonhuman_marks_do_not_pile_up_in_book():
    """Book mode: one non-human mark per sound, once per run of marked sounds; a growled trill is rrh, not rrrh."""
    b = lambda x: R.romanize(x, book=True)
    assert b("a‼r‼a") == "arrha" and b("r‼a‼") == "rrarh" and b("aᴖ˯") == "awh"
    for x in ("tɛ‼r‼i", "ku‼ɾi‼si‼li‼k", "a‼r‼a‼r‼"):
        assert not __import__("re").search(r"(rh|vr|wh|mh|ih){2}|rrrh", b(x)), b(x)


IPA_MARKS = set("̠̪̞̟̝̹̜̥̬")


@pytest.mark.parametrize("cs", CONTRAST_SETS, ids=lambda c: "+".join(sorted(c)) or "none")
def test_no_ipa_marks_in_full_spellings(cs):
    """The workbench spelling is an orthography: no IPA diacritic (bridge, retracted, lowered, advanced...) in it."""
    import unicodedata
    leaks = {}
    for s in itertools.chain(_vowel_space(), _pool()):
        sp = unicodedata.normalize("NFD", R.spell(s, cs))
        if set(sp) & IPA_MARKS:
            leaks[to_ipa(s)] = sp
    for x in ("t̪a", "ɨ̠a", "e̞o", "ʌ̞", "ɑ̟"):
        sp = unicodedata.normalize("NFD", R.romanize(x, cs))
        if set(sp) & IPA_MARKS:
            leaks[x] = sp
    assert not leaks, sorted(leaks.items())


def test_no_placeholder_spellings():
    """No word is spelled like a software placeholder (null, none, undefined): kenku /nuɫ/ 'small' was 'null'."""
    from planet.language import romanize as RO
    from planet.language.percepts import from_ipa
    inv = from_ipa("nuɫlie")
    for ipa in ("nuɫ", "inuɫ"):
        sp = RO.romanize_word(from_ipa(ipa), inventory=inv, book=True)
        assert not any(sp.lower().endswith(t) for t in RO.RESERVED_SPELLINGS), sp
    assert RO._unreserve("none") == "non·e" and RO._unreserve("inull") == "inulh"


def test_offensive_substrings_are_caught_and_broken():
    """The blocklist (data/offensive_substrings.txt) is matched case-folded with diacritics stripped; the spelling guard
    breaks a match with a middle dot at a consonant-vowel boundary, never inside a digraph (ch·ink, not c·hink)."""
    from planet.language import romanize as RO
    assert RO.offensive("NÁZÍGÚLÚ") == "nazi" and RO.offensive("nïgi") == "nigi"
    assert RO.offensive("k'ik'e") is None   # (the apostrophe is a letter here: an ejective)
    assert RO.offensive("shitayoo'ï") is None   # plain swearing is not listed, only slurs
    assert RO.unoffend("chinkaa") == "ch·inkaa"
    for s in ("naziguluni", "nigiwu", "kunifago"):
        assert RO.offensive(RO.unoffend(s)) is None
    assert RO.offensive(RO.romanize("naziɡuluni", book=True)) is None
    assert RO.romanize("naziɡuluni", book=True, ) != "naziguluni"


def test_book_marks_a_non_human_voice_once_a_word():
    """PW-1537 R7: 'samhshunwanmhch'samhshun' could not be read; the book writes a non-human mark once a word."""
    from planet.language.percepts import from_ipa
    sp = R.romanize_word(from_ipa("sa˯ʃunwa˯nsa˯"), book=True)
    assert sp.count(R.NH_MARKS["sub"]) == 1, sp
