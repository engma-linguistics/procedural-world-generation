"""The house romanization "house/1" (architecture.md section 12): IPA -> a deterministic spelling, ASCII first, digraphs
next, diacritics last, from data/romanization.tsv (base sounds) plus composition rules for modifiers (see the table header).

Contrast-dependent choices take a set of contrast names (contrasts_of builds it from a lect's segments):
- "aspiration": aspirated and breathy consonants are written with h, and the fricative digraphs that would then read as
  aspirates switch to their single-letter forms (θ þ, ð ð, x x, ɣ ğ, ʃ š, ʒ ž, tʃ č, χ x̣); without it aspiration is not written;
- "schwa": ə is ë when the lect also has e, otherwise e;
- "dental": dentals are marked with the IPA bridge (t̪) only when the lect also has the alveolar.
Within one word a hyphen goes between two spellings that would otherwise read as one (n-g vs ng, t-s vs ts, k-' vs k').
The contract's n'g is written n-g here, because ' is the glottal stop.
"""
from __future__ import annotations

import unicodedata
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from planet.language.percepts import Segment, core, from_ipa, symbols, to_ipa

DATA = Path(__file__).parent / "data"
ROMANIZATION = "house/1"
ALL_CONTRASTS = frozenset(("aspiration", "schwa", "dental"))
# documented mergers: sounds that share a spelling on purpose (near-identical as heard, or a contrast almost no language makes)
MERGES = [frozenset(x) for x in (
    ("ɹ", "ɾ", "r"),  # the approximant and the tap share r; a long tap is the trill rr
    ("ɱ", "m"), ("ʋ", "v"), ("ɬ", "l̥"), ("ʍ", "hʷ"),
    ("c", "kʲ"), ("ɟ", "ɡʲ"), ("ɲ", "nʲ"), ("ʎ", "lʲ"), ("ç", "hʲ", "j̊"),  # palatal = palatalized, as heard
    ("ʏ", "y"), ("ɘ", "ə", "ɜ"), ("ɵ", "ø", "ɞ"), ("e̞", "e"), ("o̞", "o"), ("ɐ", "a", "ä"), ("ɶ", "œ"), ("ɒ", "ɔ"))]
# also merged, by rule rather than by pair: a voiced aspirate and a breathy-voiced stop (both C+h, as Indology writes them);
# a mid tone and no tone (mid is unmarked, Yoruba-style; a tonal lect has no toneless vowels); length (it never decides).


def merged(a: str, b: str) -> bool:
    """Do two IPA spellings share a house spelling on purpose (MERGES, ignoring length)?"""
    def bare(x: str) -> str:
        for m in "ːʰʼʱ":
            x = x.replace(m, "")
        return x
    a, b = bare(a), bare(b)
    return a == b or any(a in m and b in m for m in MERGES)


_TONE = {1: "̀", 2: "", 3: "́", 4: "̌", 5: "̂", 6: "̋", 7: "̏"}
_PREN = {0: "m", 5: "ng", 6: "ng"}
_SEC = {1: "w", 2: "y", 3: "ˠ", 4: "ˤ"}


@lru_cache(maxsize=1)
def table() -> dict[str, tuple[str, str]]:
    """IPA (NFC) -> (spelling, spelling when aspiration is written)."""
    out = {}
    head = None
    for line in (DATA / "romanization.tsv").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if head is None:
            head = cols
            continue
        r = dict(zip(head, cols + [""] * (len(head) - len(cols))))
        sp = unicodedata.normalize("NFC", r["spelling"])
        out[unicodedata.normalize("NFC", r["ipa"])] = (sp, unicodedata.normalize("NFC", r["alt"]) or sp)
    return out


def contrasts_of(segments: Iterable[Segment]) -> set[str]:
    """The contrast names a lect's segment set calls for (see the module docstring)."""
    segs = set(segments)
    out = set()
    plain = {replace(s, larynx=0, phonation=0) for s in segs if s.kind == "C"}
    if any(s.kind == "C" and (s.larynx == 1 or s.phonation == 1) and replace(s, larynx=0, phonation=0) in segs for s in segs):
        out.add("aspiration")
    if any(s.kind == "V" and s.height == 3 and s.back == 2 and not s.round for s in segs) and \
            any(s.kind == "V" and s.height in (3, 4) and s.back == 0 and not s.round for s in segs):
        out.add("schwa")
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


def _double_first(sp: str) -> str:
    g = _graphemes(sp)
    for i, x in enumerate(g):
        if x[0].isalpha():
            g.insert(i, x)
            return unicodedata.normalize("NFC", "".join(g))
    return sp + ":"


def spell(seg: Segment, contrasts: set[str] | frozenset = ALL_CONTRASTS) -> str:
    """One segment's house spelling under a contrast set."""
    if seg.kind == "T":
        return ""
    asp = "aspiration" in contrasts
    c = core(seg)
    if seg.kind == "V":
        sp = _base_spelling(c, asp, contrasts)
        if to_ipa(c) == "ə" and "schwa" not in contrasts:
            sp = "e"
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
        keep = replace(c, secondary=seg.secondary)  # a base letter that has the secondary built in (ɕ ȶ ɥ ɫ)
        if seg.secondary and unicodedata.normalize("NFC", to_ipa(keep)) in table():
            c, sec = keep, 0
        else:
            sec = seg.secondary
        sp = _base_spelling(c, asp, contrasts)
        pre = ("n" if seg.manner == 8 else _PREN.get(seg.place, "n")) if seg.prenasal else ""
        if seg.length and pre:
            pre = pre[0] + pre  # a long prenasal stop doubles its nasal (nnd), not its stop
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
    # non-human percepts keep the symbols.tsv marks
    if seg.phonation == 3:
        sp += "‼"
    elif seg.phonation == 4:
        sp += "ᵣ"
    if seg.source2:
        sp += "ᴖ"
    if seg.register:
        sp += "˯" if seg.register < 0 else "˰"
    return unicodedata.normalize("NFC", sp)


@lru_cache(maxsize=256)
def _tokens(contrasts: frozenset, segs: frozenset | None) -> frozenset[str]:
    """The multi-character spellings that could be misread across a boundary: those of the given segments (a lect's
    inventory), or of every symbol-table sound and its long form when no inventory is given."""
    out = set()
    if segs is None:
        pool = [s for row in symbols() for s in (row.seg, replace(row.seg, length=1))]
        for s in pool:
            for cs in (contrasts, contrasts | {"aspiration"}):
                sp = spell(s, cs)
                if len(_graphemes(sp)) >= 2:
                    out.add(sp)
    else:
        for s in segs:
            sp = spell(s, contrasts)
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


def romanize_word(word: Iterable[Segment], contrasts: set[str] | None = None, inventory: Iterable[Segment] | None = None) -> str:
    """Segments -> house spelling. contrasts: the lect's contrast set; inventory: the lect's segments (decides where a hyphen
    is needed: n-g only if the lect has ŋ). Both None: derived from the word itself. With contrasts but no inventory, every
    possible digraph is guarded (hyphens where any lect could misread)."""
    segs = [s for s in word]
    inv = None if inventory is None else frozenset(inventory)
    if contrasts is None and inventory is None:
        inv = frozenset(segs)
    cs = frozenset(contrasts_of(inv if inv is not None else segs) if contrasts is None else contrasts)
    return _join([spell(s, cs) for s in segs], _tokens(cs, inv))


def romanize(ipa: str, contrasts: set[str] | None = None, inventory: Iterable[Segment] | None = None) -> str:
    """IPA string -> house spelling (see romanize_word)."""
    return romanize_word(from_ipa(ipa), contrasts, inventory)


def title_name(s: str) -> str:
    """A proper name: the first letter capitalized ('aba -> 'Aba, !xu -> !Xu)."""
    g = _graphemes(unicodedata.normalize("NFC", s))
    for i, x in enumerate(g):
        if x[0].isalpha():
            g[i] = x[0].upper() + x[1:]
            break
    return unicodedata.normalize("NFC", "".join(g))
