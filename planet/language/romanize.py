"""The house romanization "house/2" (architecture.md section 12): IPA -> a deterministic spelling, ASCII first, digraphs
next, diacritics last, from data/romanization.tsv (base sounds) plus composition rules for modifiers (see the table header).

Contrast-dependent choices take a set of contrast names (contrasts_of builds it from a lect's segments):
- "aspiration": aspirated and breathy consonants are written with h, and the fricative digraphs that would then read as
  aspirates switch to their single-letter forms (θ þ, ð ð, x x, ɣ ğ, ʃ š, ʒ ž, tʃ č, χ x̣); without it aspiration is not written;
- "schwa": ə (and ɘ ɜ) is ë when the lect also has e and a; "schwa_a": a when it has e but nothing spelled a; otherwise e;
- "dental": dentals are marked with the IPA bridge (t̪) only when the lect also has the alveolar;
- "open_e" "open_o" "back_a" "lax_i" "lax_u" "dark_l" "beta" "breathy_h": ɛ ɔ ɑ/ɒ ɪ ʊ ɫ β ɦ are written plainly (e o a i u l
  v h) unless the lect also has the sound they would be confused with; then è ò å ì ù ll bh hh (the table's `marked` column);
- "tone": the lect is tonal, so the marked vowels use a dot below (ẹ ọ ị ụ, Yoruba and Igbo) instead of a grave.
Non-human percepts are written in ASCII letters (growl rh, purr rr, second voice wh, sub-bass mh, ultra ih; table header).
Within one word a hyphen goes between two spellings that would otherwise read as one (n-g vs ng, t-s vs ts, k-' vs k').
The contract's n'g is written n-g here, because ' is the glottal stop.

Book mode (`book=True` on spell, romanize_word, romanize): the spelling a book prints, for a reader who has to say the name.
Display only (the IPA keeps every sound; a heavy cluster stays heavy) and lossy on purpose: the workbench shows the full
spelling. Rules, in order: no tone marks (the IPA keeps tone); a nasal vowel is the plain vowel + n, or the plain vowel before
a nasal consonant (an + na would read as a long n), never a tilde; a long vowel is doubled (aa) only once per word, later long
vowels are written short; a long consonant is doubled (ll, no Catalan dot); ə ɘ ɜ (and the other mid-central vowels) are e,
no diaeresis; front rounded vowels are ü (y ʏ) and ö (ø œ ɵ ɞ ɶ) only when the lect contrasts them with i and e ("round_i",
"round_e"), else u and o; ɛ ɔ ɪ ʊ ɑ ɒ are always plain e o i u a; æ is ae; ʔ is ' but not word-initially; breathy and creaky
marks, velarization and pharyngealization are not written; a sound with no house letter is folded to the nearest one (ɲ̟ ny,
ʊ̞ u); the IPA-kept affricates take their stop's letter (ɟʝ gy, cç ky: the table's `book` column) and ɹ is r. Finally at most one letter with a diacritic per word: the first is kept, later ones lose their marks (š s, ṭ t, ð dh,
þ th), except the uvular ġ and x̣, which keep their own spelling (velar and uvular never share one).
"""
from __future__ import annotations

import unicodedata
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from planet.language.percepts import Segment, core, from_ipa, is_nonhuman, symbols, to_ipa

DATA = Path(__file__).parent / "data"
ROMANIZATION = "house/2"
# the sounds whose presence makes a marked spelling necessary (contrast -> rivals, as IPA of the base sound)
RIVALS = {"open_e": ("e", "e̞"), "open_o": ("o", "o̞"), "back_a": ("a", "ä", "ɐ"), "lax_i": ("i",), "lax_u": ("u",),
          "dark_l": ("l",), "beta": ("v", "ʋ"), "breathy_h": ("h",)}
ALL_CONTRASTS = frozenset(("aspiration", "schwa", "dental", "tone", "round_i", "round_e", "central_i") + tuple(RIVALS))
# documented mergers: sounds that share a spelling on purpose (near-identical as heard, or a contrast almost no language makes)
MERGES = [frozenset(x) for x in (
    ("ɾ", "r"),  # a long tap is the trill rr (the approximant ɹ has its own ř, owner 11-04)
    ("ɱ", "m"), ("ʋ", "v"), ("ɬ", "l̥"), ("ʍ", "hʷ"),
    ("c", "kʲ"), ("ɟ", "ɡʲ"), ("ɲ", "nʲ"), ("ʎ", "lʲ"), ("ç", "hʲ", "j̊"),  # palatal = palatalized, as heard
    ("ʏ", "y"), ("ɘ", "ə", "ɜ"), ("ɵ", "ø", "ɞ"), ("e̞", "e"), ("o̞", "o"), ("ɐ", "a", "ä"), ("ɶ", "œ"), ("ɑ", "ɒ"))]
# also merged, by rule rather than by pair: a voiced aspirate and a breathy-voiced stop (both C+h, as Indology writes them);
# a mid tone and no tone (mid is unmarked, Yoruba-style; a tonal lect has no toneless vowels); length (it never decides);
# and, in a lect that lacks the contrast, each marked sound and its rivals (ɛ = e when there is no e: CONTRAST_MERGES).
# Non-human spellings drop the base letter's diacritics (ġ g, ò o): growled ʁ and a growled ɡ would share grh.


def merged(a: str, b: str, contrasts: Iterable[str] | None = None) -> bool:
    """Do two IPA spellings share a house spelling on purpose (MERGES, ignoring length)? With `contrasts`, also the sounds that
    contrast set leaves unmarked (ɛ and e without "open_e", ɛ̃ and ẽ, βʲ and vʲ): compared after each base sound is replaced
    by its merger's representative."""
    def bare(x: str) -> str:
        for m in "ːʰʼʱ":
            x = x.replace(m, "")
        return x
    a, b = bare(a), bare(b)
    if a == b or any(a in m and b in m for m in MERGES):
        return True
    if contrasts is None:
        return False
    return _canonical(a, frozenset(contrasts)) == _canonical(b, frozenset(contrasts))


def _canonical(ipa: str, contrasts: frozenset) -> tuple:
    rep: dict[str, str] = {}
    for m in MERGES:
        for x in m:
            rep[x] = min(m)
    for c, group in contrast_merges().items():
        if c not in contrasts:
            r = min(rep.get(x, x) for x in group)
            for x in group:
                for y in [x] + [k for k, v in rep.items() if v == rep.get(x, x)]:
                    rep[y] = r
    out = []
    quality = ("place", "manner", "voice", "height", "back", "round", "sibilant", "retroflex", "labiodental", "lateral", "double")
    for seg in from_ipa(ipa):
        k = _base_key(seg)
        built_in = seg.kind == "C" and seg.secondary and k != unicodedata.normalize("NFC", to_ipa(core(seg)))
        mods = replace(seg, **{a: 0 for a in quality}, **({"secondary": 0} if built_in else {}))
        out.append((rep.get(k, k), mods))
    return tuple(out)


@lru_cache(maxsize=1)
def contrast_merges() -> dict[str, frozenset]:
    """contrast -> the IPA that share a spelling when the lect lacks it (marked sounds + rivals; ə ɘ ɜ with e)."""
    out: dict[str, set] = {}
    for ipa, (c, *_r) in marked().items():
        out.setdefault(c, set()).add(ipa)
    for c, r in RIVALS.items():
        out.setdefault(c, set()).update(r)
    out.setdefault("schwa", set()).add("e")
    return {c: frozenset(v) for c, v in out.items()}


_TONE = {1: "̀", 2: "", 3: "́", 4: "̌", 5: "̂", 6: "̋", 7: "̏"}
_PREN = {0: "m", 5: "ng", 6: "ng"}
_SEC = {1: "w", 2: "y", 3: "ˠ", 4: "ˤ"}


@lru_cache(maxsize=1)
def _rows() -> tuple[dict, ...]:
    out = []
    head = None
    for line in (DATA / "romanization.tsv").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if head is None:
            head = cols
            continue
        r = dict(zip(head, cols + [""] * (len(head) - len(cols))))
        out.append({k: unicodedata.normalize("NFC", v) for k, v in r.items()})
    return tuple(out)


@lru_cache(maxsize=1)
def table() -> dict[str, tuple[str, str]]:
    """IPA (NFC) -> (spelling, spelling when aspiration is written): the unmarked spellings."""
    return {r["ipa"]: (r["spelling"], r["alt"] or r["spelling"]) for r in _rows()}


@lru_cache(maxsize=1)
def book_table() -> dict[str, str]:
    """IPA (NFC) -> the book-mode spelling of the base sounds whose full spelling folds badly letter by letter (the table's
    `book` column: ɟʝ gy, not gyyh; ɹ r)."""
    return {r["ipa"]: r["book"] for r in _rows() if r.get("book")}


@lru_cache(maxsize=1)
def marked() -> dict[str, tuple[str, str, str, str]]:
    """IPA -> (contrast, marked, marked when aspiration is written, marked in a tonal lect) for the contrast-dependent rows
    ("" where the row gives no variant)."""
    return {r["ipa"]: (r["contrast"], r["marked"], r["marked_alt"], r["marked_tonal"]) for r in _rows() if r.get("contrast")}


def _base_key(seg: Segment) -> str:
    """The IPA of the table row a segment is spelled from (its core; a consonant keeps a secondary its letter has built in)."""
    c = core(seg)
    if seg.kind == "C" and seg.secondary:
        keep = unicodedata.normalize("NFC", to_ipa(replace(c, secondary=seg.secondary)))
        if keep in table():
            return keep
    return unicodedata.normalize("NFC", to_ipa(c))


def contrasts_of(segments: Iterable[Segment]) -> set[str]:
    """The contrast names a lect's segment set calls for (see the module docstring)."""
    segs = set(segments)
    out = set()
    plain = {replace(s, larynx=0, phonation=0) for s in segs if s.kind == "C"}
    if any(s.kind == "C" and (s.larynx == 1 or s.phonation == 1) and replace(s, larynx=0, phonation=0) in segs for s in segs):
        out.add("aspiration")
    keys = {_base_key(s) for s in segs if s.kind != "T"}
    if keys & {"ə", "ɘ", "ɜ"} and keys & {"e", "e̞"}:
        out.add("schwa" if keys & {"a", "ä", "ɐ", "ɑ", "ɒ"} else "schwa_a")
    for ipa, (c, *_r) in marked().items():
        if c in RIVALS and ipa in keys and keys & set(RIVALS[c]):
            out.add(c)
    if any(s.tone or s.kind == "T" for s in segs):
        out.add("tone")
    vows = [s for s in segs if s.kind == "V"]
    if any(s.round and s.back <= 1 and s.height >= 5 for s in vows) and "i" in keys:
        out.add("round_i")  # (book mode: ü only beside i)
    if any(s.round and s.back <= 2 and s.height < 5 for s in vows) and keys & {"e", "e̞"}:
        out.add("round_e")  # (book mode: ö only beside e)
    if any(not s.round and s.back == 2 and s.height >= 5 for s in vows) and "i" in keys:
        out.add("central_i")  # (book mode: ï only beside i)
    if any(s.kind == "C" and s.place == 1 and to_ipa(core(s)) not in table() and replace(core(s), place=2) in
           {core(x) for x in plain} for s in segs):
        out.add("dental")
    return out


def _graphemes(s: str) -> list[str]:
    d = unicodedata.normalize("NFD", s)
    out: list[str] = []
    for ch in d:
        if out and unicodedata.combining(ch):
            out[-1] += ch
        else:
            out.append(ch)
    return out


def _mark_first_letter(sp: str, mark: str) -> str:
    if not mark:
        return sp
    g = _graphemes(sp)
    for i, x in enumerate(g):
        if x[0].isalpha():
            g[i] = x + mark
            break
    return unicodedata.normalize("NFC", "".join(g))


def _base_spelling(c: Segment, asp: bool, contrasts: set[str]) -> str:
    t = table()
    ipa = unicodedata.normalize("NFC", to_ipa(c))
    m = marked().get(ipa)
    if m is not None:
        con, sp, sp_alt, sp_tonal = m
        if con == "schwa" and "schwa_a" in contrasts:
            return "a"
        if con in contrasts:
            if asp and sp_alt:
                return sp_alt
            return sp_tonal if ("tone" in contrasts and sp_tonal) else sp
    if ipa in t:
        return t[ipa][1 if asp else 0]
    if c.kind == "C":
        if c.place == 1:  # dental of an alveolar letter (t̪ n̪ l̪ s̪)
            alv = unicodedata.normalize("NFC", to_ipa(replace(c, place=2)))
            if alv in t:
                return _mark_first_letter(t[alv][1 if asp else 0], "̪" if "dental" in contrasts else "")
        flip = replace(c, voice=1 - c.voice)
        fi = unicodedata.normalize("NFC", to_ipa(flip))
        if fi in t:
            sp = t[fi][1 if asp else 0]
            if c.manner == 8:
                return ("g" + sp) if c.voice else sp
            if not c.voice:  # voiceless sonorant: h before (Old English hl, hn, hw; Icelandic)
                return "h" + sp
            return _mark_first_letter(sp, "̬")
        if c.place == 1:
            alv = replace(flip, place=2)
            ai = unicodedata.normalize("NFC", to_ipa(alv))
            if ai in t:
                return ("h" if not c.voice else "") + _mark_first_letter(t[ai][1 if asp else 0], "̪" if "dental" in contrasts else "")
    return ipa  # no house spelling: the IPA itself (non-human and very rare sounds)


# where a doubled letter spells a sound of its own (ll = ɫ, hh = ɦ), the long single letter takes a middle dot (Catalan l·l)
_DOUBLED_TAKEN = {"dark_l": "l", "breathy_h": "h"}
# non-human percepts (table header): ASCII marks after the sound
_NH_PHONATION = {3: "rh", 4: "rr"}
_NH_SOURCE2, _NH_SUB, _NH_ULTRA = "wh", "mh", "ih"
_ASCII_FOLD = {"æ": "ae", "œ": "oe", "ð": "dh", "þ": "th", "ı": "i", "ʉ": "u", "ł": "l", "ƒ": "f", "ʋ": "v", "ŋ": "ng"}


def _ascii(sp: str) -> str:
    """A spelling in plain ASCII letters (diacritics dropped, ligatures spelled out, marks like ' and ʿ removed)."""
    d = unicodedata.normalize("NFD", "".join(_ASCII_FOLD.get(ch, ch) for ch in unicodedata.normalize("NFC", sp)))
    return "".join(ch for ch in d if ch.isascii() and ch.isalpha())


def _double_first(sp: str) -> str:
    g = _graphemes(sp)
    for i, x in enumerate(g):
        if x[0].isalpha():
            g.insert(i, x)
            return unicodedata.normalize("NFC", "".join(g))
    return sp + ":"


# book mode: IPA letters that have no house letter of their own (fallback spellings), folded to the nearest book letter
_BOOK_FOLD = {"ə": "e", "ɘ": "e", "ɜ": "e", "ɛ": "e", "ɔ": "o", "ɪ": "i", "ʊ": "u", "ɑ": "a", "ɒ": "a", "ɐ": "a", "ʉ": "u",
              "ɵ": "o", "ɞ": "o", "ʏ": "u", "ø": "o", "œ": "o", "ɶ": "o", "æ": "ae", "ɤ": "o", "ɯ": "eu",
              "ʌ": "eo", "ɨ": "i", "ɲ": "ny", "ŋ": "ng", "ʎ": "ly", "ʟ": "l", "ɫ": "l", "ʙ": "b", "ɺ": "l", "ⱱ": "v", "ɾ": "r",
              "ɹ": "r", "ɻ": "r", "ɽ": "r", "ʀ": "rq", "ʁ": "ġ", "χ": "qh", "ɣ": "gh", "ʝ": "yh", "ɟ": "gy", "ɮ": "dl",
              "ç": "hy", "ɬ": "hl", "ʋ": "v", "ɸ": "f", "β": "v", "θ": "th", "ʃ": "sh", "ʒ": "zh", "ɦ": "h", "ħ": "h",
              "ʡ": "'", "ɢ": "gq", "ɴ": "nq", "ɕ": "sy", "ʑ": "zy", "ɰ": "w", "ɭ": "l", "ɳ": "n", "ʈ": "t", "ɖ": "d",
              "ʂ": "s", "ʐ": "z", "ɓ": "'b", "ɗ": "'d", "ʄ": "'y", "ɠ": "'g", "ʛ": "'gq", "ʔ": "'", "ʕ": "ʿ", "ɡ": "g",
              "ɱ": "m", "ʍ": "hw", "ȶ": "ty", "ȡ": "dy", "ȵ": "ny", "ȴ": "ly", "ɧ": "x"}
BOOK_DIGRAPHS = frozenset(("ʃ", "ʒ", "tʃ"))  # book mode keeps their digraphs where the workbench writes š ž č
BOOK_KEEP = frozenset(("ġ", "x̣"))  # the uvular letters keep their dot in book mode (velar and uvular never share a spelling)
_BOOK_DROP = "·ˠˤ"  # the Catalan dot, velarized and pharyngealized
# the combining marks a book letter may carry (ṭ ġ č ś ḇ ü ğ ŵ ơ ç); every other mark (tone, nasal, phonation, dental, voicing,
# the IPA fallback's advanced/lowered/retracted) is dropped
_BOOK_MARKS = frozenset("̧̛̣̱̇̌́̈̆̂")


def _book_fold(sp: str) -> str:
    out = []
    for g in _graphemes(sp):
        if g[0] in _BOOK_FOLD:
            out.append(_BOOK_FOLD[g[0]])
        else:
            out.append("".join(ch for ch in g if ch not in _BOOK_DROP and (not unicodedata.combining(ch) or ch in _BOOK_MARKS)))
    return unicodedata.normalize("NFC", "".join(out))


def _book_vowel(c: Segment, asp: bool, contrasts) -> str:
    if c.round and c.back <= 2 and not (c.back == 2 and c.height >= 5):
        if c.height >= 5:
            return "ü" if "round_i" in contrasts else "u"
        return "ö" if "round_e" in contrasts else "o"
    if not c.round and c.back == 2 and 2 <= c.height <= 4:
        return "e"
    if not c.round and c.back == 2 and c.height >= 5:
        return "ï" if "central_i" in contrasts else "i"
    plain = frozenset(contrasts) - set(RIVALS) - {"schwa", "schwa_a"}
    return _book_fold(_base_spelling(c, asp, plain))


def is_diacritic_letter(g: str) -> bool:
    """A grapheme that is a letter with a diacritic (or a non-ASCII Latin letter: ð þ ƒ ŵ) for the book cap; ' ʿ | ! are not."""
    g = unicodedata.normalize("NFC", g)
    if g.isascii() or not unicodedata.category(g[0]).startswith("L") or unicodedata.category(g[0]) == "Lm":
        return False
    return g not in "ǀǁǃǂʘ"


def diacritics(sp: str) -> int:
    """How many letters with a diacritic a spelling has (the book-mode measure; a doubled one, üü, counts once, as in
    _book_cap)."""
    gs = [unicodedata.normalize("NFC", g) for g in _graphemes(sp)]
    return sum(is_diacritic_letter(g) for i, g in enumerate(gs) if i == 0 or gs[i - 1] != g)


def _book_cap(sp: str) -> str:
    """At most one diacritic letter per word (the first; a doubled one, üü, counts once); later ones are stripped to ASCII
    (a doubled one doubles its first letter: þþ tth), except the uvular ġ and x̣."""
    gs = [unicodedata.normalize("NFC", g) for g in _graphemes(sp)]
    out, seen, i = [], False, 0
    while i < len(gs):
        g = gs[i]
        n = 1
        while i + n < len(gs) and gs[i + n] == g:
            n += 1
        if is_diacritic_letter(g):
            if seen and g not in BOOK_KEEP and _ascii(g):
                a = _ascii(g)
                out.append(a if n == 1 else a[0] * (n - 1) + a)
            else:
                out.append(g * n)
            seen = True
        else:
            out.append(g * n)
        i += n
    return unicodedata.normalize("NFC", "".join(out))


def spell(seg: Segment, contrasts: set[str] | frozenset = ALL_CONTRASTS, book: bool = False) -> str:
    """One segment's house spelling under a contrast set (book: the book-mode spelling, see the module docstring; the
    word-level rules, one doubled vowel, no initial ', a nasal vowel before a nasal, the diacritic cap, are romanize_word's)."""
    if seg.kind == "T":
        return ""
    asp = "aspiration" in contrasts
    nh = is_nonhuman(seg)
    c = core(seg)
    if seg.kind == "V" and book:
        sp = _book_vowel(c, asp, contrasts)
        if nh:
            sp = _ascii(sp) or sp
        if seg.length:
            g = _graphemes(sp)
            sp = sp + g[-1]
        if seg.nasal:
            sp += "n"
    elif seg.kind == "V":
        sp = _base_spelling(c, asp, contrasts)
        if nh:
            sp = _ascii(sp) or sp  # (a vowel with no ASCII letter in its spelling, ə ɨ ɑ: keep it rather than spell nothing)
        if seg.nasal:
            sp = _mark_first_letter(sp, "̃")
        sp = _mark_first_letter(sp, _TONE.get(seg.tone, ""))
        if seg.length:
            g = _graphemes(sp)
            g.append(unicodedata.normalize("NFD", unicodedata.normalize("NFC", g[-1])))
            # a doubled vowel repeats the letter without the tone mark
            g[-1] = "".join(ch for ch in g[-1] if ch not in "̀́̌̂̋̏")
            sp = unicodedata.normalize("NFC", "".join(g))
        if seg.phonation in (1, 2):
            sp += "̤" if seg.phonation == 1 else "̰"
    else:
        # (book: sh zh ch even where aspiration is written; a rare sʰ reads the same, lossy on purpose)
        asp_letter = asp and not (book and unicodedata.normalize("NFC", to_ipa(c)) in BOOK_DIGRAPHS)
        keep = replace(c, secondary=seg.secondary)  # a base letter that has the secondary built in (ɕ ȶ ɥ ɫ)
        if seg.secondary and unicodedata.normalize("NFC", to_ipa(keep)) in table():
            c, sec = keep, 0
        else:
            sec = seg.secondary
        sp = _base_spelling(c, asp_letter, contrasts)
        if book:
            sp = book_table().get(unicodedata.normalize("NFC", to_ipa(c)), sp)
        if nh:
            sp = _ascii(sp)
        pre = ("n" if seg.manner == 8 else _PREN.get(seg.place, "n")) if seg.prenasal else ""
        if seg.length and pre:
            pre = pre[0] + pre  # a long prenasal stop doubles its nasal (nnd), not its stop
        elif seg.length and any(con in contrasts and sp == x for con, x in _DOUBLED_TAKEN.items()):
            sp = sp + "·" + sp
        elif seg.length:
            sp = _double_first(sp)
        sp = pre + sp
        if sec:
            sp += _SEC[sec]
        if asp and (seg.larynx == 1 or seg.phonation == 1):
            sp += "h"
        if seg.larynx == 2:
            sp += "'"
        if seg.phonation == 2:
            sp += "̰"
        if book:
            sp = _book_fold(sp)
    # non-human percepts: readable ASCII marks after the sound (romanization.tsv header)
    sp += _NH_PHONATION.get(seg.phonation, "")
    if seg.source2:
        sp += _NH_SOURCE2
    if seg.register:
        sp += _NH_SUB if seg.register < 0 else _NH_ULTRA
    return unicodedata.normalize("NFC", sp)


@lru_cache(maxsize=256)
def _tokens(contrasts: frozenset, segs: frozenset | None, book: bool = False) -> frozenset[str]:
    """The multi-character spellings that could be misread across a boundary: those of the given segments (a lect's
    inventory), or of every symbol-table sound and its long form when no inventory is given."""
    out = set()
    if book and segs is not None:  # (a book nasal vowel's n is lossy on purpose: guarding an would hyphenate every a + n)
        segs = frozenset(s if s.kind != "V" else replace(s, nasal=0) for s in segs)
    if segs is None:
        pool = [s for row in symbols() for s in (row.seg, replace(row.seg, length=1)) if not (book and s.kind == "V" and s.nasal)]
        for s in pool:
            for cs in (contrasts, contrasts | {"aspiration"}):
                sp = spell(s, cs, book)
                if len(_graphemes(sp)) >= 2:
                    out.add(sp)
    else:
        for s in segs:
            sp = spell(s, contrasts, book)
            if len(_graphemes(sp)) >= 2:
                out.add(sp)
    return frozenset(out)


def _join(parts: list[str], toks: frozenset) -> str:
    out = ""
    for p in parts:
        if not p:
            continue
        if out and any(out[-i:] + p[:j] in toks for i in range(1, min(4, len(out)) + 1) for j in range(1, min(4, len(p)) + 1)):
            out += "-"
        out += p
    return out


def romanize_word(word: Iterable[Segment], contrasts: set[str] | None = None, inventory: Iterable[Segment] | None = None,
                  book: bool = False) -> str:
    """Segments -> house spelling. contrasts: the lect's contrast set; inventory: the lect's segments (decides where a hyphen
    is needed: n-g only if the lect has ŋ). Both None: derived from the word itself. With contrasts but no inventory, every
    possible digraph is guarded (hyphens where any lect could misread). book: the book-mode spelling (module docstring)."""
    segs = [s for s in word]
    inv = None if inventory is None else frozenset(inventory)
    if contrasts is None and inventory is None:
        inv = frozenset(segs)
    cs = frozenset(contrasts_of(inv if inv is not None else segs) if contrasts is None else contrasts)
    if not book:
        return _join([spell(s, cs) for s in segs], _tokens(cs, inv))
    parts, doubled = [], False
    real = [i for i, s in enumerate(segs) if s.kind != "T"]
    for n, i in enumerate(real):
        s = segs[i]
        nxt = segs[real[n + 1]] if n + 1 < len(real) else None
        if s.kind == "V":
            if s.nasal and nxt is not None and nxt.kind == "C" and nxt.manner == 3:
                s = replace(s, nasal=0)
            if s.length:
                s = replace(s, length=0) if doubled else s
                doubled = True
        sp = spell(s, cs, book=True)
        if n == 0 and sp == "'":
            sp = ""  # (no glottal stop written word-initially)
        parts.append(sp)
    return _book_cap(_join(parts, _tokens(cs, inv, True)))


def romanize(ipa: str, contrasts: set[str] | None = None, inventory: Iterable[Segment] | None = None,
             book: bool = False) -> str:
    """IPA string -> house spelling (see romanize_word)."""
    return romanize_word(from_ipa(ipa), contrasts, inventory, book)


def title_name(s: str) -> str:
    """A proper name: the first letter capitalized ('aba -> 'Aba, !xu -> !Xu)."""
    g = _graphemes(unicodedata.normalize("NFC", s))
    for i, x in enumerate(g):
        if x[0].isalpha():
            g[i] = x[0].upper() + x[1:]
            break
    return unicodedata.normalize("NFC", "".join(g))
