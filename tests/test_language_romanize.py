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
    assert r("ǃa") == "!a" and r("ǀa") == "|a" and r("ǁa") == "||a"
    assert r("á") == "á" and r("à") == "à" and r("a˧") == "a"
    assert r("ənə", {"schwa"}) == "ënë" and r("ənə", set()) == "ene"
    assert r("pʰapa") == "phapa" and r("pʰa") == "pa"  # aspiration written only where it contrasts
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
    assert R.title_name("'aba") == "'Aba" and R.title_name("!xu") == "!Xu" and R.title_name("ørn") == "Ørn"


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
    assert R.romanize("a‼") == "arh" and R.romanize("aᵣ") == "arr" and R.romanize("aᴖ") == "awh"
    assert R.romanize("a˯") == "amh" and R.romanize("i˰") == "iih" and R.romanize("ʞa") == "cka"
    assert R.romanize("ma‼") == "marh" and R.romanize("ʁ‼a") == "grha"
    assert R.romanize("ar", inventory=from_ipa("aᵣ a r")) == "a-rr"  # a + trill is not the purred a


def test_contrasts_of():
    assert R.contrasts_of(from_ipa("ppʰa")) == {"aspiration"}
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
    assert b("my˧dʱœ̃ː˨ʔa˦ĩː˦") == "müdoon'ain"  # one doubled vowel, nasal = +n, ü beside i, one diacritic letter
    assert b("pə˨ʁa˨ki˨ʕa˨") == "peġakiʿa"  # no tone, schwa e, the uvular ġ kept
    assert b("sy˦pũ˨vo˨") == "supunvo"  # no i in the word: y is u
    for x in ("my˧dʱœ̃ː˨ʔa˦ĩː˦", "pə˨ʁa˨ki˨ʕa˨", "sy˦pũ˨vo˨"):
        assert R.diacritics(b(x)) <= 1 and len(b(x)) <= len(R.romanize(x))


def test_book_mode_rules():
    b = lambda x, cs=None, inv=None: R.romanize(x, cs, inv, book=True)
    assert b("á à ǎ a˧") == "aaaa"  # no tone
    assert b("ãta") == "anta" and b("ãma") == "ama" and b("ãŋa") == "anga"  # nasal: + n, plain before a nasal
    assert "̃" not in b("ãẽĩõũ")
    assert b("aːtaː") == "aata" and b("tːa") == "tta"  # one doubled vowel per word; a long consonant doubled
    assert b("ənə") == "ene" and b("eəa") == "eea"  # schwa e, no diaeresis
    assert b("ɛɔɪʊɑ") == "eoiua" and b("eɛ oɔ iɪ") == "eeooii"  # the open/lax/back vowels always plain
    assert b("y") == "u" and b("iy") == "iü" and b("ø") == "o" and b("eø") == "eö" and b("eœ") == "eö"
    assert b("ʔaʔa") == "a'a"  # no word-initial glottal stop
    assert b("ʃaʈaʂa") == "shaṭasa"  # one diacritic letter per word: the first
    assert b("ʃa", {"aspiration"}) == "sha"  # (book: the digraph even where the workbench writes š)
    assert b("lːaɫa") == "llalla"  # no Catalan dot
    assert b("ɲ̟a") == "nya" and b("ʊ̞ta") == "uta"  # no house letter: folded


def test_book_mode_keeps_the_uvulars():
    b = lambda x, cs=None: R.romanize(x, cs, book=True)
    assert b("qa") == "qa" and b("χa") == "qha" and b("ʁa") == "ġa" and b("ɢa") == "gqa" and b("ɴa") == "nqa"
    assert b("χa", {"aspiration"}) == "x̣a" and b("ʃaʁa") == "shaġa" and b("ṭaʁaʁa".replace("ṭ", "ʈ")) == "ṭaġaġa"
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
    assert all(R.diacritics(x) <= 1 or any(g in R.BOOK_KEEP for g in R._graphemes(x)) for x in book)
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
    return [ch for ch in s if "ɐ" <= ch <= "ʯ" or "ᴀ" <= ch <= "ᶿ"]


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
