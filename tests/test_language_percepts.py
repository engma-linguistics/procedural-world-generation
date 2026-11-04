"""planet.language.percepts: the symbol table, parsing, distance, natural classes, syllables (not slow)."""
import pytest

from planet.language import percepts as P
from planet.language.percepts import from_ipa, to_ipa


def one(s):
    segs = from_ipa(s)
    assert len(segs) == 1, (s, segs)
    return segs[0]


def test_table_size_and_sources():
    rows = P.symbols()
    assert len(rows) >= 150
    assert {r.source for r in rows} <= {"ipa", "extipa", "voqs", "house"}
    syms = {r.symbol for r in rows}
    for s in ("ʘ", "ǀ", "ǃ", "ǁ", "ǂ", "ʬ", "ʭ", "ɓ", "kʼ", "kʰ", "kʷ", "tʲ", "aː", "ã", "˦", "ts", "tʃ", "k͡p", "ᵐb"):
        assert s in syms, s
    assert any(r.source == "house" for r in rows) and any(r.source == "extipa" for r in rows)


def test_axes_unique_per_row():
    seen = {}
    for r in P.symbols():
        assert r.seg not in seen, (r.symbol, seen.get(r.seg))
        seen[r.seg] = r.symbol


@pytest.mark.parametrize("row", P.symbols(), ids=lambda r: r.symbol)
def test_round_trip_every_row(row):
    assert from_ipa(row.symbol) == [row.seg]
    assert to_ipa(row.seg) == row.symbol
    # the diacritic rows equal their composition from the plain rows
    assert from_ipa(row.symbol, base_only=True) == [row.seg]


def test_parser_aliases_and_affricates():
    assert one("t͡s") == one("ts") == one("ʦ")
    assert one("t͡ʃ") == one("tʃ")
    assert one("g") == one("ɡ")
    assert one("k'") == one("kʼ")
    assert one("a:") == one("aː")
    assert from_ipa("t.s") == [one("t"), one("s")]
    assert one("kʰʷ") == one("kʷʰ")  # modifier order does not matter
    assert one("á").tone == 3 and one("à").tone == 1
    assert one("a˩˥").tone == 4 and one("a˥˩").tone == 5
    assert from_ipa("˦")[0].kind == "T"
    assert P.parse_segment("mb") == one("ᵐb") and P.parse_segment("kp") == one("k͡p")
    assert P.parse_segment("t̠ʃ") == one("tʃ") and P.parse_segment("ai") is None


def test_composed_segments_emit_and_reparse():
    for s in ("ʁʷː", "ts̪", "ɕː", "qʷʼ", "ŋ̊", "ɔ̃ː", "u˦˨", "ʔʷ", "ᵑɡ͡b", "ɣ‼", "aᴖ"):
        seg = one(s)
        assert from_ipa(to_ipa(seg)) == [seg], s


def test_word_ipa_round_trip():
    for w in ("tsat.sa", "ma.˦", "aŋɡa", "kʷʼaχt͡ɬʼ", "ǃxóõ"):
        word = tuple(from_ipa(w))
        assert tuple(from_ipa(P.word_ipa(word))) == word, w


def test_distance():
    segs = [r.seg for r in P.symbols()]
    for a in segs[::7]:
        assert P.distance(a, a) == 0
        for b in segs[::11]:
            assert P.distance(a, b) == pytest.approx(P.distance(b, a))
    p, t, k = one("p"), one("t"), one("k")
    assert P.distance(p, k) < P.distance(p, t)  # labial is nearer the other grave place
    assert P.distance(one("a"), one("p")) >= P.KIND_PENALTY
    assert P.distance(one("s"), one("ʃ"), {"place": 0}) == 0  # a weight of 0 ignores the axis
    assert P.distance(one("a˦"), one("a˥")) < P.distance(one("a˦"), one("a˨"))


def test_natural_classes():
    pc = P.parse_class
    p, b, s, m, a, l, j = (one(x) for x in "pbsmalj")
    assert pc("C")(p) and not pc("C")(a) and pc("V")(a)
    assert pc("P[-voice]")(p) and not pc("P[-voice]")(b) and pc("P & [+voice]")(b)
    assert pc("N")(m) and pc("S")(s) and pc("F")(s) and pc("L")(l) and pc("G")(j) and not pc("G")(l)
    assert pc("T")(p) and pc("D")(b)
    assert pc("[place=0..1]")(p) and not pc("[place=0..1]")(s) and pc("[manner=2]")(s)
    assert pc("[place!=0]")(s) and pc("N|S")(m) and pc("N|S")(s) and not pc("N|S")(p)
    assert pc("!V")(p) and pc("#")(None) and not pc("C")(None)
    assert pc("_") is P.FOCUS
    assert pc("Ṽ")(one("ã")) and not pc("Ṽ")(a)
    assert pc("[+voice,-nasal]")(b) and not pc("[+voice,-nasal]")(m)
    assert P.natural_class(kind="C", manner=0)(p)
    with pytest.raises(ValueError):
        pc("[wobble=1]")


def test_sonority_scale():
    son = P.SONORITY
    order = ["a", "j", "l", "n", "z", "s", "ts", "b", "p"]
    vals = [son(one(x)) for x in order]
    assert vals == [10, 8, 7, 6, 5, 4, 3, 2, 1]


def test_syllabify():
    def shapes(w):
        return [(P.word_ipa(s.onset), P.word_ipa(s.nucleus), P.word_ipa(s.coda)) for s in P.syllabify(from_ipa(w))]
    assert shapes("astrakanta") == [("", "a", "s"), ("tr", "a", ""), ("k", "a", "n"), ("t", "a", "")]
    assert shapes("pa") == [("p", "a", "")]
    assert shapes("aia") == [("", "a", ""), ("", "i", ""), ("", "a", "")]
    assert shapes("alpa") == [("", "a", "l"), ("p", "a", "")]
    assert [s.shape() for s in P.syllabify(from_ipa("ma˦ŋka"))] == ["CVC", "CV"]
    assert len(P.syllabify(from_ipa("mm̩"))) == 1  # no vowel: a sonority peak is the nucleus
