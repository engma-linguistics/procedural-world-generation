"""The house romanization "house/2" (architecture.md section 12): IPA -> a deterministic spelling, ASCII first, digraphs
next, diacritics last, from data/romanization.tsv (base sounds) plus composition rules for modifiers (see the table header).

Contrast-dependent choices take a set of contrast names (contrasts_of builds it from a lect's phonemes):
- "aspiration": aspirated and breathy consonants are written with h, and the fricative digraphs that would then read as
  aspirates switch to their single-letter forms (θ þ, ð ð, x x, ɣ ğ, ʃ š, ʒ ž, tʃ č, χ x̣); without it aspiration is not written;
- "pinyin" (instead of "aspiration"): the lect contrasts aspiration only on voiceless stops and affricates and has no voiced
  ones, so the plain stops take the voiced letters (b d g j dz) and the aspirates the plain ones (p t k ch ts), as pinyin and
  Korean RR do; the fricative digraphs stay sh th kh, so one aspirate no longer changes the whole look of the language;
- "schwa": ə (and ɘ ɜ) is ë when the lect also has e and a; "schwa_a": a when it has e but nothing spelled a; otherwise e;
- "dental": a dental beside its alveolar takes a breve below (t̮ d̮ n̮ l̮); otherwise it is the plain letter;
- "shift": a vowel with a small IPA shift (ɨ̠ e̞ ɑ̟) is its base's letter, unless the lect has both: then raised/advanced take a
  breve and lowered/retracted a macron below; an IPA diacritic never reaches a spelling;
- "open_e" "open_o" "back_a" "lax_i" "lax_u" "dark_l" "beta" "breathy_h": ɛ ɔ ɑ/ɒ ɪ ʊ ɫ β ɦ are written plainly (e o a i u l
  v h) unless the lect also has the sound they would be confused with; then è ò å ì ù ll bh hh (the table's `marked` column);
- "tone": the lect is tonal, so the marked vowels use a dot below (ẹ ọ ị ụ, Yoruba and Igbo) instead of a grave.
Non-human percepts are written in ASCII letters (growl rh, purr vr, second voice wh, sub-bass mh, ultra ih: NH_MARKS); the
second voice's own tone (syrinx lane) is the first voice's tone mark on its w: a˦ᴖ˨˦ áw̌h, aᴖ˨ aẁh (book mode: awh).
Clicks are the letters ǀ ǁ ǃ ǂ (U+01C0-01C3; a long click doubles: ǃǃ). Within one word a hyphen goes between two
spellings that would otherwise read as one (n-g vs ng, t-s vs ts, k-' vs k').
The contract's n'g is written n-g here, because ' is the glottal stop.

**One lect, one spelling per phoneme** (`Orthography`): the spelling is built from the lect's phonemes; an allophone is
spelled as its phoneme (Kunrei, Spanish b d g for [β ð ɣ]; the IPA keeps the phonetics) and an inserted ʔ is not written.

Book mode (`book=True`): the spelling a book prints, for a reader who has to say the name. Display only (the IPA keeps every
sound) and lossy on purpose: the workbench shows the full spelling. Rules: no tone marks; a nasal vowel is the plain vowel + n,
or the plain vowel before a nasal consonant, never a tilde; every long vowel is doubled (aa); a long consonant is doubled (ll,
no Catalan dot); ə ɘ ɜ are e; front rounded vowels are ü (y ʏ) and ö (ø œ ɵ ɞ ɶ) only when the lect contrasts them with i and
e, else u and o; ɛ ɔ ɪ ʊ ɑ ɒ are plain e o i u a; æ is ae; ʔ is ' but not word-initially; breathy and creaky marks,
velarization and pharyngealization are not written; a sound with no house letter is folded to the nearest one; the IPA-kept
affricates take their stop's letter (ɟʝ gy, cç ky) and ɹ is r. Diacritics are planned **once per lect** (book_folds): a
diacritic letter whose ASCII fold merges none of the lect's phonemes is always folded (ṭ is t where there is no t); of the
rest, the BOOK_DIACRITIC_BUDGET commonest keep their mark and the others fold everywhere (merging; Orthography.lossy lists
them); the uvular ġ and x̣ always keep theirs. Non-human marks: one per word (the first sound's first mark), written once
after the first run of sounds that carry it (no rhrh, no samhshunwanmh), and a growled r is rrh, not rrrh.
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
ALL_CONTRASTS = frozenset(("aspiration", "schwa", "dental", "tone", "round_i", "round_e", "central_i", "shift") + tuple(RIVALS))
# (also "pinyin", never in ALL_CONTRASTS: a lect that contrasts aspiration on its stops but has no voiced stops writes the plain
# stops b d g and the aspirates p t k, pinyin and Korean RR style; contrasts_of gives it instead of "aspiration")
# Book mode: how many diacritic letters a lect keeps where folding them would merge two of its phonemes (the commonest by
# token count win; a diacritic letter whose fold merges nothing is always folded). A taste call for the owner.
BOOK_DIACRITIC_BUDGET = 2
# Non-human marks (ASCII, after the sound). Purr is not rr (the trill). Taste calls for the owner: one row each.
NH_MARKS = {"growl": "rh", "purr": "vr", "second": "wh", "sub": "mh", "ultra": "ih"}
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
    sa, sb = _split_shifts(a), _split_shifts(b)  # a shifted vowel: merged when the bases are and the shift classes agree
    if (sa[1] or sb[1]) and merged(sa[0], sb[0]):  # (no "shift" contrast: a shifted vowel is its base's letter)
        if (contrasts is not None and "shift" not in contrasts) or _shift_class(sa[1]) == _shift_class(sb[1]):
            return True
    if contrasts is None:
        return False
    return _canonical(a, frozenset(contrasts)) == _canonical(b, frozenset(contrasts))


def _split_shifts(ipa: str) -> tuple[str, str]:
    d = unicodedata.normalize("NFD", ipa)
    return (unicodedata.normalize("NFC", "".join(c for c in d if c not in _VOWEL_SHIFTS)),
            "".join(sorted(c for c in d if c in _VOWEL_SHIFTS)))


def _shift_class(marks: str) -> str:
    """The Latin mark a set of IPA shift marks is written with when the lect contrasts a shifted vowel with its base."""
    return "".join(sorted({_SHIFT_MARK.get(m, "") for m in marks}))


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
        kb, km = (k, "") if k in table() else _split_shifts(k)
        km = _shift_class(km) if "shift" in contrasts else ""
        out.append((rep.get(kb, kb) + km, mods))
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
        asp = [s for s in segs if s.kind == "C" and (s.larynx == 1 or s.phonation == 1)]
        voiced_stop = any(s.kind == "C" and s.manner in (0, 1) and s.voice and s.larynx == 0 for s in segs)
        prenasal = any(s.kind == "C" and s.prenasal for s in segs)
        if all(s.manner in (0, 1) and s.larynx == 1 and not s.voice and s.phonation == 0 and s.place in _PINYIN_PLACES
               for s in asp) and not voiced_stop and not prenasal:
            out.add("pinyin")
        else:
            out.add("aspiration")
    keys = {_base_key(s) for s in segs if s.kind != "T"}
    for k in keys:
        if k not in table():
            kb, km = _split_shifts(k)
            if km and kb in keys:
                out.add("shift")
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
                return _mark_first_letter(t[alv][1 if asp else 0], _DENTAL if "dental" in contrasts else "")
        flip = replace(c, voice=1 - c.voice)
        fi = unicodedata.normalize("NFC", to_ipa(flip))
        if fi in t:
            sp = t[fi][1 if asp else 0]
            if c.manner == 8:
                return ("g" + sp) if c.voice else sp
            if not c.voice:  # voiceless sonorant: h before (Old English hl, hn, hw; Icelandic)
                return "h" + sp
            return _mark_first_letter(sp, "̌")  # (a voiced sound with only a voiceless letter: a caron, as Czech ž of z-ish)
        if c.place == 1:
            alv = replace(flip, place=2)
            ai = unicodedata.normalize("NFC", to_ipa(alv))
            if ai in t:
                return ("h" if not c.voice else "") + _mark_first_letter(t[ai][1 if asp else 0], _DENTAL if "dental" in contrasts else "")
    if c.kind in "VC":  # a sound with an IPA mark for a small shift (ʌ̞ ɨ̠ ɑ̟ ɟ̟): the base sound's spelling, plain unless the lect
        # contrasts a shifted sound with its base ("shift"); then a Latin mark (breve raised/advanced, macron below
        # lowered/retracted), never the IPA mark
        base = "".join(ch for ch in unicodedata.normalize("NFD", ipa) if ch not in _VOWEL_SHIFTS)
        marks = "".join(ch for ch in unicodedata.normalize("NFD", ipa) if ch in _VOWEL_SHIFTS)
        if marks and base != ipa:
            segs = from_ipa(unicodedata.normalize("NFC", base))
            if len(segs) == 1 and segs[0].kind == c.kind:
                return _mark_first_letter(_base_spelling(segs[0], asp, contrasts),
                                          _shift_class(marks) if "shift" in contrasts else "")
    return ipa  # no house spelling: the IPA itself (non-human and very rare sounds)


# IPA marks that shift a vowel a little (raised lowered advanced retracted, more or less rounded, voiceless): not written
# unless the lect contrasts a shifted sound with its base; then raised/advanced take a breve, lowered/retracted a macron below
_VOWEL_SHIFTS = frozenset("̝̞̠̟̹̜̥")
_SHIFT_MARK = {"̝": "̆", "̟": "̆", "̞": "̱", "̠": "̱"}
_DENTAL = "̮"  # a dental beside its alveolar: breve below (t̮ d̮ n̮ l̮; macron below is taken, ḻ is ɻ); book drops it
_PINYIN_PLACES = frozenset((0, 1, 2, 3, 4, 5))  # (labial to velar: the places with a plain voiced letter)
# where a doubled letter spells a sound of its own (ll = ɫ, hh = ɦ), the long single letter takes a middle dot (Catalan l·l)
_DOUBLED_TAKEN = {"dark_l": "l", "breathy_h": "h"}
# non-human percepts (table header): ASCII marks after the sound
_NH_PHONATION = {3: NH_MARKS["growl"], 4: NH_MARKS["purr"]}
_NH_SOURCE2, _NH_SUB, _NH_ULTRA = NH_MARKS["second"], NH_MARKS["sub"], NH_MARKS["ultra"]
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


def nh_marks(seg: Segment, tone2: bool = False) -> list[str]:
    """A segment's non-human marks, in writing order (growl/purr, second voice, register). tone2: the second voice's own
    tone written as the first voice's tone mark on its w (high ẃh, low ẁh, rising w̌h, falling ŵh; mid unmarked)."""
    out = []
    if seg.phonation in _NH_PHONATION:
        out.append(_NH_PHONATION[seg.phonation])
    if seg.source2:
        mk = _NH_SOURCE2
        if tone2 and seg.tone2:
            mk = unicodedata.normalize("NFC", mk[0] + _TONE.get(seg.tone2, "") + mk[1:])
        out.append(mk)
    if seg.register:
        out.append(_NH_SUB if seg.register < 0 else _NH_ULTRA)
    return out


def spell(seg: Segment, contrasts: set[str] | frozenset = ALL_CONTRASTS, book: bool = False, marks: bool = True) -> str:
    """One segment's house spelling under a contrast set (book: the book-mode spelling, see the module docstring; the
    word-level rules, no initial ', a nasal vowel before a nasal, the lect's diacritic folds and the non-human mark runs, are
    romanize_word's). marks=False: without the non-human marks (nh_marks)."""
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
        if ("pinyin" in contrasts and c.manner in (0, 1) and c.place in _PINYIN_PLACES and not c.voice and seg.larynx == 0
                and not seg.prenasal and not nh):
            c = replace(c, voice=1)  # (pinyin: the plain stop takes the voiced letter, the aspirate the plain one)
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
    if marks:
        sp += "".join(nh_marks(seg, tone2=not book))
    return unicodedata.normalize("NFC", sp)


@lru_cache(maxsize=256)
def _tokens(contrasts: frozenset, segs: frozenset | None, book: bool = False, folds: frozenset = frozenset()) -> frozenset[str]:
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
        fd = dict(folds)
        for s in segs:
            sp = _apply_folds(spell(s, contrasts, book), fd) if fd else spell(s, contrasts, book)
            if len(_graphemes(sp)) >= 2:
                out.add(sp)
    return frozenset(out)


#: the separator that keeps two letters from reading as one (n-g where the lect has ŋ). The book register uses the
#: middle dot (Catalan l·l): a hyphen inside a root read as an affix break on the pages (demo read 4: irh-ll)
GUARD, BOOK_GUARD = "-", "·"


def _join(parts: list[str], toks: frozenset, sep: str = GUARD) -> str:
    out = ""
    for p in parts:
        if not p:
            continue
        if out and any(out[-i:] + p[:j] in toks for i in range(1, min(4, len(out)) + 1) for j in range(1, min(4, len(p)) + 1)):
            out += sep
        out += p
    return out


#: spellings a reader takes for a software placeholder (demo read 4: kenku 'small' /nuɫ/ spelled null, 'child' inull);
#: a word ending in one is re-spelled by `_unreserve`
RESERVED_SPELLINGS = ("null", "none", "undefined")


def _unreserve(sp: str) -> str:
    """A spelling that ends in a RESERVED_SPELLINGS token is re-spelled at that end: a doubled letter (ll for ɫ, hh for
    ɦ) as the letter + h (nulh), else a middle dot before the last letter (non·e)."""
    low = sp.lower()
    for tok in RESERVED_SPELLINGS:
        if low.endswith(tok):
            if len(sp) >= 2 and sp[-1] == sp[-2]:
                return sp[:-1] + "h"
            return sp[:-1] + BOOK_GUARD + sp[-1]
    return sp


@lru_cache(maxsize=1)
def blocklist() -> tuple[str, ...]:
    """The offensive English substrings (data/offensive_substrings.txt, cold review 2026-11-08)."""
    rows = (DATA / "offensive_substrings.txt").read_text(encoding="utf-8").splitlines()
    return tuple(r.strip().lower() for r in rows if r.strip() and not r.lstrip().startswith("#"))


def _plain(sp: str) -> tuple[str, list[int]]:
    """A spelling as a reader of English skims it: lower case, diacritics dropped; with each plain letter's index in
    NFD(sp)."""
    d = unicodedata.normalize("NFD", sp)
    out, idx = [], []
    for i, ch in enumerate(d):
        if unicodedata.combining(ch):
            continue
        out.append(ch.lower()[:1] or ch)
        idx.append(i)
    return "".join(out), idx


def offensive(sp: str) -> str | None:
    """The first blocklisted substring the spelling contains (case-folded, diacritics stripped), or None."""
    p, _ = _plain(sp)
    return next((b for b in blocklist() if b in p), None)


#: spellings respelled by `unoffend` since the counter was last read (the pass reports it; a guard, not a model count)
UNOFFEND_COUNT = [0]


def unoffend(sp: str) -> str:
    """The last resort for a spelling that reads as an English slur or obscenity and has no word to renew (an affixed or
    joined form, a gram, a name built at a join): the same phonemes with a middle dot inside the match (na·zi), as
    `_unreserve` does for null. Words are renewed at the source first (`lexicon.offense_repair`)."""
    for _ in range(4):
        b = offensive(sp)
        if b is None:
            return sp
        p, idx = _plain(sp)
        i0 = p.index(b)
        # the dot goes before a vowel letter that follows a consonant letter (a segment boundary: a consonant's
        # spelling never ends in a vowel letter, while sh, ng, an + nasal would be split inside), nearest the middle
        cut = [j for j in range(i0 + 1, i0 + len(b)) if p[j] in "aeiouy" and p[j - 1] not in "aeiouy"]
        at = min(cut, key=lambda j: (abs(j - (i0 + len(b) / 2)), -j)) if cut else i0 + len(b) // 2
        d = unicodedata.normalize("NFD", sp)
        sp = unicodedata.normalize("NFC", d[:idx[at]] + BOOK_GUARD + d[idx[at]:])
        UNOFFEND_COUNT[0] += 1
    return sp


def romanize_word(word: Iterable[Segment], contrasts: set[str] | None = None, inventory: Iterable[Segment] | None = None,
                  book: bool = False, folds: dict | None = None, guard: bool = True) -> str:
    """`_romanize_word`, with a reserved ending respelled and (guard) an offensive substring broken (`unoffend`)."""
    sp = _unreserve(_romanize_word(word, contrasts, inventory, book, folds))
    return unoffend(sp) if guard else sp


def _romanize_word(word: Iterable[Segment], contrasts: set[str] | None = None, inventory: Iterable[Segment] | None = None,
                   book: bool = False, folds: dict | None = None) -> str:
    """Segments -> house spelling. contrasts: the lect's contrast set; inventory: the lect's segments (decides where a hyphen
    is needed: n-g only if the lect has ŋ). Both None: derived from the word itself. With contrasts but no inventory, every
    possible digraph is guarded (hyphens where any lect could misread). book: the book-mode spelling (module docstring);
    folds: the lect's book folds (book_folds; default: planned over the inventory, else over the word itself)."""
    segs = [s for s in word]
    inv = None if inventory is None else frozenset(inventory)
    if contrasts is None and inventory is None:
        inv = frozenset(segs)
    cs = frozenset(contrasts_of(inv if inv is not None else segs) if contrasts is None else contrasts)
    if not book:
        return _join([spell(s, cs) for s in segs], _tokens(cs, inv))
    if folds is None:
        folds = book_folds(inv if inv is not None else frozenset(segs), cs)
    parts = []
    real = [i for i, s in enumerate(segs) if s.kind != "T"]
    marks = []
    for n, i in enumerate(real):
        s = segs[i]
        nxt = segs[real[n + 1]] if n + 1 < len(real) else None
        if s.kind == "V" and s.nasal and nxt is not None and nxt.kind == "C" and nxt.manner == 3:
            s = replace(s, nasal=0)
        sp = _apply_folds(spell(s, cs, book=True, marks=False), folds)
        if n == 0 and sp == "'":
            sp = ""  # (no glottal stop written word-initially)
        parts.append(sp)
        marks.append(nh_marks(s)[:1])  # (book: one non-human mark per sound, the first)
    for n in range(len(parts)):  # a run of sounds with the same mark writes it once, after the run (no rhrh)
        m = marks[n]
        if m and not (n + 1 < len(parts) and marks[n + 1] == m):
            marks[n + 1:] = [()] * (len(parts) - n - 1)   # (PW-1537 R7: one mark a word, after its first marked run;
            # 'samhshunwanmhch'samhshun' could not be read; the mark tells the reader the word's voice, not each sound's)
            mk = m[0]
            if mk == NH_MARKS["growl"] and parts[n].endswith("r"):
                mk = "h"  # (a growled r is rrh, not rrrh: Welsh rh)
            parts[n] += mk
    return _join(parts, _tokens(cs, inv, True, frozenset(folds.items())), BOOK_GUARD)


def _apply_folds(sp: str, folds: dict) -> str:
    if not folds:
        return sp
    return unicodedata.normalize("NFC", "".join(folds.get(unicodedata.normalize("NFC", g), g) for g in _graphemes(sp)))


@lru_cache(maxsize=4096)
def _book_folds(inv: frozenset, cs: frozenset, counts: tuple | None) -> tuple:
    w = dict(counts or ())
    spellings = {s: spell(s, cs, book=True, marks=False) for s in inv if s.kind != "T"}
    letters: dict = {}
    for s, sp in spellings.items():
        for g in {unicodedata.normalize("NFC", g) for g in _graphemes(sp)}:
            if is_diacritic_letter(g) and g not in BOOK_KEEP and _ascii(g):
                letters[g] = letters.get(g, 0.0) + float(w.get(s, 1.0))
    n0 = len(set(spellings.values()))

    def distinct(f):
        return len({_apply_folds(sp, f) for sp in spellings.values()}) == n0

    folds: dict = {}
    for g in sorted(letters, key=lambda g: (letters[g], g)):  # a fold that merges nothing: always
        if distinct({**folds, g: _ascii(g)}):
            folds[g] = _ascii(g)
    out = [(g, a, False) for g, a in folds.items()]
    rest = sorted((g for g in letters if g not in folds), key=lambda g: (-letters[g], g))
    out += [(g, _ascii(g), True) for g in rest[BOOK_DIACRITIC_BUDGET:]]  # past the budget: folded, merging
    return tuple(sorted(out))


def book_folds(inventory: Iterable[Segment], contrasts: Iterable[str], counts: dict | None = None) -> dict:
    """A lect's book plan, once for its whole lexicon: diacritic letter -> its ASCII fold. A diacritic letter whose fold merges
    none of the lect's phonemes is always folded (ṭ is t where there is no t); of the rest the BOOK_DIACRITIC_BUDGET commonest
    (by `counts`, segment -> tokens; else alphabetically) keep their mark and the others fold, merging (ṣ = s everywhere)."""
    cnt = None if counts is None else tuple(sorted(((s, float(v)) for s, v in counts.items()), key=lambda x: (to_ipa(x[0]), repr(x[0]))))
    return {g: a for g, a, _lossy in _book_folds(frozenset(inventory), frozenset(contrasts), cnt)}


class Orthography:
    """One lect's spelling (both registers): its contrasts and hyphen guards from its phonemes, an allophone spelled as its
    phoneme (Kunrei-style; the IPA keeps the phonetics; an inserted ʔ is not written), and its book folds.
    segments: the lect's surface segments (lect.segments()); allophones: inventory.allophones ({allophone: (phoneme | None,
    test)}); counts: segment -> tokens in the lexicon (ranks the book diacritics)."""

    def __init__(self, segments: Iterable[Segment], allophones: dict | None = None, counts: dict | None = None):
        self.allo = {x: p for x, (p, _t) in (allophones or {}).items()}
        phon = {self._phoneme(s) for s in segments}
        phon.discard(None)
        self.inv = frozenset(phon)
        self.cs = frozenset(contrasts_of(self.inv))
        if counts is not None:
            pc: dict = {}
            for s, v in counts.items():
                q = self._phoneme(s)
                if q is not None:
                    pc[q] = pc.get(q, 0.0) + float(v)
            counts = pc
        plan = _book_folds(self.inv, self.cs, None if counts is None else tuple(sorted(
            ((s, float(v)) for s, v in counts.items()), key=lambda x: (to_ipa(x[0]), repr(x[0])))))
        self.folds = {g: a for g, a, _l in plan}
        self.lossy = [[g, a] for g, a, lossy in plan if lossy]  # (the merging folds: the orthography line names them)

    def _phoneme(self, s: Segment):
        if not self.allo:
            return s
        if s.kind == "V":
            p = self.allo.get(replace(s, tone=0), s)
            return None if p is None else (replace(p, tone=s.tone) if p is not s else s)
        return self.allo.get(s, s)

    def phonemic(self, form) -> tuple:
        out = []
        for s in form:
            q = self._phoneme(s)
            if q is not None:
                out.append(q)
        return tuple(out)

    def word(self, form, book: bool = False, guard: bool = True) -> str:
        return romanize_word(self.phonemic(form), self.cs, self.inv, book=book, folds=self.folds if book else None,
                             guard=guard)

    def offends(self, form) -> str | None:
        """The blocklisted substring the form's raw spelling holds in either register (no `unoffend`), or None."""
        return offensive(self.word(form, guard=False)) or offensive(self.word(form, book=True, guard=False))


def romanize(ipa: str, contrasts: set[str] | None = None, inventory: Iterable[Segment] | None = None,
             book: bool = False, folds: dict | None = None) -> str:
    """IPA string -> house spelling (see romanize_word)."""
    return romanize_word(from_ipa(ipa), contrasts, inventory, book, folds)


def title_name(s: str) -> str:
    """A proper name: the first cased letter capitalized ('aba -> 'Aba, ǃxu -> ǃXu: a click letter has no capital)."""
    g = _graphemes(unicodedata.normalize("NFC", s))
    for i, x in enumerate(g):
        if x[0].isalpha() and x[0].upper() != x[0].lower():
            g[i] = x[0].upper() + x[1:]
            break
    return unicodedata.normalize("NFC", "".join(g))


def title_words(words: list[str]) -> str:
    """A multi-word name: each content word capitalized; a short particle (one or two letters) is joined to its neighbour with
    a hyphen and stays lower case unless it starts the name (Opa'i-e, E-Iva; as al-, Kel, Banu attach)."""
    words = [w for w in words if w]
    if not words:
        return ""
    short = [len(_ascii(w)) <= 2 and len(words) > 1 for w in words]
    out = ""
    for i, w in enumerate(words):
        piece = w if short[i] else title_name(w)
        if i == 0:
            out = title_name(piece)
        elif short[i] or short[i - 1]:
            out += "-" + piece
        else:
            out += " " + piece
    return out
