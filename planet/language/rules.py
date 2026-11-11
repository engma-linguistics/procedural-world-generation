"""Sound change: rules over the percept space (architecture.md section 5).

A rule rewrites a *focus* segment (optionally followed by a short span of further segments) in an environment. Every rule
carries its physical cause and what it needs (articulators or hear axes); a species keeps only the rules whose needs it
has, weighted by its make costs (``catalogue``). Contrast maintenance is built in: ``pick_rule`` vetoes a drawn rule with a
probability that rises with its functional load (Wedel), and a vetoed vowel merger offers a dispersion step instead (the
crowded vowel moves away: a push-chain step).

Application is left to right and iterative: the left context is read from the output built so far and the right context
from the input, so a spreading rule (harmony) spreads and syncope alternates (VCVCVCV loses every other vowel, not all).
Matching ignores tone (a toned vowel is still an e for "e > i"); everything else must match.

The compact notation (``parse_rule``) is the one of ``data/sound_changes.tsv``: ``input > output / environment`` with IPA
and the classes V C N P(stop) T(voiceless stop) D(voiced stop) F(fricative) S(sibilant) L/R(liquid) G(glide), ``#`` word
edge, ``_`` the focus, ``∅`` zero, ``(X)`` optional, ``X*`` any number, ``{a, b}`` either, brackets ``[+front V]``,
``[−voice]``, ``[αplace]`` (assimilation), ``[−stress]``, ``[axis=v]``, ``[axis=lo..hi]``, and the house flags
``[coda]``, ``[onset]``, ``[final]``, ``[nonfinal]``, ``[open]``, ``[closed]``, and ``X`` any segment (``_X*r``: an r
later in the word, for dissimilation and harmony at a distance). Comma lists are parallel changes; a parallel list of
clusters ("pl, kl > pj, kj") becomes a staged rule, a step per pair (refused when a step would feed a later one); a chain
``a > b > c`` is staged, a > b then b > c (a drag chain is written in drag order with "then"). What the parser cannot express it refuses with a reason, never by raising.
"""

from __future__ import annotations

import bisect
import csv
import unicodedata
import math
import re
from dataclasses import dataclass, field
from .percepts import replace  # (PW-1555: the interned Segment's fast path; dataclasses.replace otherwise)
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable, Sequence

from planet.language.percepts import AXES, from_ipa, is_glide, is_liquid, to_ipa

Word = tuple  # tuple[Segment, ...]

CAUSES = ("coarticulation", "effort", "perception", "prosody", "tonogenesis", "dispersion", "analogy")
SCOPES = ("regular", "diffusing")
DATA = Path(__file__).parent / "data" / "sound_changes.tsv"

FL_K = 15.0  # veto probability = 1 - exp(-FL_K * load); load 0.05 (1 form in 20 merges) -> 53 % veto
DEFAULT_STRESS = "penult"
EPENTHETIC = "ə"  # vowel inserted by a class-V insertion ("∅ > V")

# The tsv's needs vocabulary mapped onto the profile vocabulary (architecture §3). Articulators are plain names
# (profile.articulators); heard axes live in their own namespace, "hear:<axis>" (resolution > 0 in profile.hear), because
# some axis names are also articulator names (larynx). Legacy tsv tokens: pitch_ear = hear:tone, timing = hear:length.
# "stress" and "none" need nothing a spoken species could lack.
NEEDS_ALIAS = {"tongue_blade": "tongue_tip", "pitch_ear": "hear:tone", "timing": "hear:length", "stress": None,
               "none": None, "": None}
HEAR_PREFIX = "hear:"
TONE_LETTERS = "˥˦˧˨˩"

_V_QUALITY = ("height", "back", "round")
_C_QUALITY = ("manner", "voice", "larynx", "phonation", "secondary", "sibilant", "lateral", "prenasal")  # a class rewritten to a literal keeps place


# --------------------------------------------------------------------------------------------------------------- patterns

class Pattern:
    """A natural-class predicate over Segment (memoized per segment). It is built from a picklable ``spec`` (rules travel to
    spawned workers): ("b", kind, ((axis, lo, hi), ...)) | ("lit", segment) | ("keys", frozenset of segments) |
    ("named", name in NAMED) | ("and", spec, spec) | ("or", spec, spec). ``seg`` is set for a literal (one exact segment,
    tone ignored); ``words`` is the plain-words name for ``describe``."""

    __slots__ = ("label", "spec", "words", "seg", "fn", "_memo")

    def __init__(self, label: str, spec: tuple, words: str = "", seg=None):
        self.label, self.spec, self.words, self.seg = label, spec, words, seg
        self.fn = _compile(spec)
        self._memo: dict = {}

    def __call__(self, seg) -> bool:
        r = self._memo.get(seg)
        if r is None:
            r = self._memo[seg] = bool(self.fn(seg))
        return r

    def __reduce__(self):
        return (Pattern, (self.label, self.spec, self.words, self.seg))

    def __and__(self, other: "Pattern") -> "Pattern":
        return Pattern(f"{self.label}&{other.label}", ("and", self.spec, other.spec), _join_words(other.words, self.words))

    def __or__(self, other: "Pattern") -> "Pattern":
        return Pattern(f"{self.label}|{other.label}", ("or", self.spec, other.spec), f"{self.words} or {other.words}")

    def __repr__(self) -> str:
        return f"Pattern({self.label})"


NAMED: dict[str, Callable] = {
    "liquid": is_liquid,
    "glide": is_glide,
    "son": lambda s: s.kind == "V" or (s.kind == "C" and 3 <= s.manner <= 7),
    "obs": lambda s: s.kind == "C" and s.manner in (0, 1, 2, 8, 9),
    "nonfront": lambda s: s.kind == "V" and (s.back >= 2 or s.height <= 1),
    "nasal": lambda s: (s.kind == "C" and s.manner == 3) or bool(s.nasal),
    "nonpharyngeal": lambda s: s.kind != "C" or s.place != 7,
    "nonglide": lambda s: not is_glide(s),
}


def _compile(spec) -> Callable:
    op = spec[0]
    if op == "b":
        _, kind, conds = spec

        def fn(s):
            if kind is not None and s.kind != kind:
                return False
            for ax, lo, hi in conds:
                v = getattr(s, ax)
                if v < lo or v > hi:
                    return False
            return True
        return fn
    if op == "lit":
        key = spec[1]
        return lambda s: _tonekey(s) == key
    if op == "keys":
        keys = spec[1]
        return lambda s: _tonekey(s) in keys
    if op == "named":
        return NAMED[spec[1]]
    if op in ("and", "or"):
        a, b = _compile(spec[1]), _compile(spec[2])
        return (lambda s: a(s) and b(s)) if op == "and" else (lambda s: a(s) or b(s))
    raise ValueError(f"bad pattern spec {spec!r}")


def _join_words(adj: str, noun: str) -> str:
    if not adj:
        return noun
    if not noun:
        return adj
    if re.match(r"an? ", adj) and not re.match(r"an? ", noun):
        adj, noun = noun, adj
    noun = re.sub(r"^an? ", "", noun)
    adj = re.sub(r"^an? ", "", adj)
    return _article(f"{adj} {noun}")


def _article(s: str) -> str:
    return ("an " if s[:1] in "aeiou" else "a ") + s


def cls(label: str, kind=None, words: str = "", **bounds) -> Pattern:
    conds = tuple((ax, *(b if isinstance(b, tuple) else (b, b))) for ax, b in bounds.items())
    return Pattern(label, ("b", kind, conds), words)


def lit(seg) -> Pattern:
    """Exactly this segment (tone ignored)."""
    key = _tonekey(seg)
    ipa = to_ipa(key)
    return Pattern(ipa, ("lit", key), ipa, seg=key)


V = cls("V", "V", "a vowel")
C = cls("C", "C", "a consonant")
N = cls("N", "C", "a nasal", manner=3)
P = cls("P", "C", "a stop", manner=0)
T = cls("T", "C", "a voiceless stop", manner=0, voice=0)
D = cls("D", "C", "a voiced stop", manner=0, voice=1)
F = cls("F", "C", "a fricative", manner=2)
S = cls("S", "C", "a sibilant", sibilant=1)
L = Pattern("L", ("named", "liquid"), "a liquid")
G = Pattern("G", ("named", "glide"), "a glide")
SON = Pattern("[+son]", ("named", "son"), "a sonorant")
OBS = Pattern("[-son]", ("named", "obs"), "an obstruent")
X = cls("X", None, "any segment")  # any segment: X* bridges to a non-adjacent context (dissimilation, harmony at a distance)
CLASSES = {"V": V, "C": C, "N": N, "P": P, "T": T, "D": D, "F": F, "S": S, "L": L, "R": L, "G": G, "X": X}
CLASS_SETS = {"T": {"manner": 0, "voice": 0}, "D": {"manner": 0, "voice": 1}, "P": {"manner": 0}, "N": {"manner": 3},
              "F": {"manner": 2}}

# feature -> (pattern if +, pattern if -, sets if +, sets if -)
FEATURES = {
    "voice": (cls("+voice", None, "voiced", voice=1), cls("-voice", "C", "voiceless", voice=0), {"voice": 1}, {"voice": 0}),
    "son": (SON, OBS, None, None),
    # low vowels count as non-front (a in a five-vowel system is [-front -back]): k > tʃ before i, e but not a
    "front": (cls("+front", "V", "front", back=(0, 1), height=(2, 6)),
              Pattern("-front", ("named", "nonfront"), "non-front"),
              {"back": 0}, {"back": 4}),
    "back": (cls("+back", "V", "back", back=(3, 4)), cls("-back", "V", "non-back", back=(0, 2)), {"back": 4}, {"back": 0}),
    "high": (cls("+high", "V", "high", height=(5, 6)), cls("-high", "V", "non-high", height=(0, 4)), {"height": 6}, {"height": 4}),
    "low": (cls("+low", "V", "low", height=(0, 1)), cls("-low", "V", "non-low", height=(2, 6)), {"height": 0}, {"height": 3}),
    "round": (cls("+round", None, "rounded", round=1), cls("-round", None, "unrounded", round=0), {"round": 1}, {"round": 0}),
    "nasal": (Pattern("+nasal", ("named", "nasal"), "nasal"),
              cls("-nasal", None, "oral", nasal=0),
              {"nasal": 1}, {"nasal": 0}),
    "long": (cls("+long", None, "long", length=1), cls("-long", None, "short", length=0), {"length": 1}, {"length": 0}),
    "fricative": (F, None, None, None),
    "stop": (P, None, None, None),
    "sibilant": (S, None, None, None),
    "syllabic": (V, C, None, None),
    "cons": (C, V, None, None),
    # exclusion features (input only); the minus sides carry no words so descriptions stay plain
    "glottal": (cls("+glottal", "C", "glottal", place=8), cls("-glottal", None, "", place=(0, 7)), None, None),
    "pharyngeal": (cls("+pharyngeal", "C", "pharyngeal", place=7), Pattern("-pharyngeal", ("named", "nonpharyngeal"), ""),
                   None, None),
    "labial": (cls("+labial", "C", "labial", place=0), cls("-labial", None, "", place=(1, 8)), None, None),
    "pulmonic": (cls("+pulmonic", None, "", larynx=(0, 1)), cls("-pulmonic", "C", "glottalic", larynx=(2, 3)), None, None),
    "glide": (G, Pattern("-glide", ("named", "nonglide"), ""), None, None),
    "breathy": (cls("+breathy", None, "breathy", phonation=1), cls("-breathy", None, "modal", phonation=0),
                {"phonation": 1}, {"phonation": 0}),
    "aspirated": (cls("+aspirated", None, "aspirated", larynx=1), cls("-aspirated", None, "unaspirated", larynx=0),
                  {"larynx": 1}, {"larynx": 0}),
}
# place is more than the place axis: assimilating to a retroflex, a labiodental or a labial-velar takes those axes too
# (n + ʈ > ɳʈ, n + f > ɱf; ɳ + p > mp, never a retroflex labial m{retroflex=1})
_PLACE_AXES = ("retroflex", "labiodental", "double")
ALPHA_AXES = {"place": ("place",), "back": ("back",), "round": ("round",), "voice": ("voice",), "front": ("back",),
              "high": ("height",), "nasal": ("nasal",), "height": ("height",)}
SYLL_FLAGS = ("coda", "onset", "final", "nonfinal", "open", "closed")
DIACRITICS = {"ː": ("length", 1), "̃": ("nasal", 1), "ʰ": ("larynx", 1), "ʼ": ("larynx", 2), "ʷ": ("secondary", 1),
              "ʲ": ("secondary", 2), "ˠ": ("secondary", 3), "ˤ": ("secondary", 4), "̤": ("phonation", 1),
              "̰": ("phonation", 2)}
STRESS_MARK = "́"
SOURCE2_MARK = "ᴖ"


# ------------------------------------------------------------------------------------------------------------- the rule

@dataclass(frozen=True)
class Change:
    """What happens to the matched span.

    kind: ``set`` (axes on the focus), ``map`` (parallel: each listed input segment has its own output), ``delete``,
    ``insert`` (a segment at a gap; the rule has no focus), ``split`` (focus becomes two segments), ``metathesis`` (focus
    swaps with its right neighbour), ``rewrite`` (a cluster becomes another), ``assimilate`` (copy ``axes`` from
    ``source``: left | right | prev_vowel | first_vowel).
    ``items``: the output as (ref, literal, sets) triples: ref = index into the matched span (-1 for a literal), sets =
    ((axis, value), ...) applied on top. ``pairs`` for ``map``: ((input segment without tone, items), ...).
    ``left_set``: axes set on the segment just before the span when it is a vowel (compensatory lengthening, tonogenesis).
    """

    kind: str
    items: tuple = ()
    pairs: tuple = ()
    axes: tuple = ()
    source: str = ""
    left_set: tuple = ()
    out_text: str = ""  # the output as written (for describe)

    @staticmethod
    def set(**values) -> "Change":
        return Change("set", items=((0, None, tuple(values.items())),))

    @staticmethod
    def delete(**left_set) -> "Change":
        return Change("delete", left_set=tuple(left_set.items()))

    @staticmethod
    def insert(seg) -> "Change":
        return Change("insert", items=((-1, seg, ()),))


@dataclass(frozen=True)
class Env:
    """Left and right contexts. ``alts``: ((left tokens, right tokens), ...), any may match. Tokens: ("#",),
    ("p", Pattern), ("ps", Pattern, stressed | unstressed) (a context segment under a stress condition, V́),
    ("opt", Pattern), ("star", Pattern). ``stress``: None | stressed | unstressed (the focus vowel).
    ``syll``: frozenset of SYLL_FLAGS on the focus. ``ctx_stress``: some context token is an "ps"."""

    alts: tuple = (((), ()),)
    stress: str | None = None
    syll: frozenset = frozenset()
    ctx_stress: bool = False


ANYWHERE = Env()


@dataclass(frozen=True)
class Rule:
    id: str
    target: Pattern | None          # focus predicate; None for an insertion
    change: Change
    env: Env = ANYWHERE
    cause: str = "effort"
    needs: frozenset = frozenset()
    weight: float = 3.0
    scope: str = "regular"
    example: str = ""
    span: tuple = ()                # further patterns the match covers after the focus (clusters)
    family: str = ""
    notation: str = ""
    then: tuple = ()                # a staged change: further Rules run, in order, on this rule's output

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Rule) and self.id == other.id and self.notation == other.notation \
            and self.weight == other.weight


# ------------------------------------------------------------------------------------------------------- application

def stressed_vowel(word: Sequence, pattern: str | None = DEFAULT_STRESS) -> int | None:
    """Index of the stressed vowel under a stress pattern (initial | final | penult | antepenult | weight | none)."""
    vs = [i for i, s in enumerate(word) if s.kind == "V"]
    if not vs or pattern in (None, "none"):
        return None
    if pattern == "initial":
        return vs[0]
    if pattern == "final":
        return vs[-1]
    if pattern == "penult":
        return vs[-2] if len(vs) >= 2 else vs[0]
    if pattern == "antepenult":
        return vs[-3] if len(vs) >= 3 else vs[0]
    if pattern == "weight":
        return weight_stress(word, vs)
    raise ValueError(f"unknown stress pattern {pattern!r}")


def heavy(word: Sequence, k: int, vs: Sequence[int]) -> bool:
    """Is the syllable on vowel index vs[k] heavy: a long vowel, a diphthong's first half, or closed (two or more
    consonants before the next vowel, or one or more at the end of the word)?"""
    i = vs[k]
    if word[i].length:
        return True
    nxt = vs[k + 1] if k + 1 < len(vs) else len(word)
    if nxt == i + 1:
        return k + 1 < len(vs) and word[nxt].kind == "V" and word[nxt].height > word[i].height + 2  # (a falling diphthong)
    ncons = sum(1 for s in word[i + 1:nxt] if s.kind == "C") + sum(1 for s in word[i + 1:nxt] if s.kind == "C" and s.length)
    return ncons >= (1 if k + 1 == len(vs) else 2)


def weight_stress(word: Sequence, vs: Sequence[int] | None = None) -> int | None:
    """Quantity-sensitive stress, the Latin rule (one of the commonest weight-sensitive systems; Hayes 1995, Metrical Stress
    Theory, ch. 4): in a word of three or more syllables the penult if it is heavy, else the antepenult; otherwise the
    first syllable. The stress of a WALS 14A 'no fixed stress' lect that has stress at all (stress pattern "weight")."""
    if vs is None:
        vs = [i for i, s in enumerate(word) if s.kind == "V"]
    if not vs:
        return None
    if len(vs) < 3:
        return vs[0]
    return vs[-2] if heavy(word, len(vs) - 2, vs) else vs[-3]


def _stress_of(word, stress_index) -> int | None:
    if stress_index is None:
        return stressed_vowel(word, DEFAULT_STRESS)
    if isinstance(stress_index, str):
        return stressed_vowel(word, stress_index)
    if callable(stress_index):
        return stress_index(word)
    pat = getattr(stress_index, "stress", None)  # an Inventory
    return stressed_vowel(word, pat)


def _m(tokens, k, w, j, step, sat=None) -> bool:
    """Match context tokens from position j in direction step. ``sat(j)``: is position j the stressed vowel (None: the
    word has no stress, so no stress-conditioned token matches)."""
    n = len(w)
    while k < len(tokens):
        t = tokens[k]
        typ = t[0]
        if typ == "#":
            if j != (n if step > 0 else -1):
                return False
            k += 1
            continue
        inside = 0 <= j < n
        if typ == "p":
            if not (inside and t[1](w[j])):
                return False
            k += 1
            j += step
            continue
        if typ == "ps":
            if not (inside and t[1](w[j]) and sat is not None and sat(j) == (t[2] == "stressed")):
                return False
            k += 1
            j += step
            continue
        if typ == "opt":
            if inside and t[1](w[j]) and _m(tokens, k + 1, w, j + step, step, sat):
                return True
            k += 1
            continue
        if typ == "star":
            jj = j
            while True:
                if _m(tokens, k + 1, w, jj, step, sat):
                    return True
                if 0 <= jj < n and t[1](w[jj]):
                    jj += step
                else:
                    return False
        raise ValueError(typ)
    return True


def _env_ok(env: Env, out: list, w, j_right: int, sat_left=None, sat_right=None) -> bool:
    """Left tokens (stored reversed) against the output so far, right tokens against the input from j_right."""
    for left_rev, right in env.alts:
        if left_rev and not _m(left_rev, 0, out, len(out) - 1, -1, sat_left):
            continue
        if right and not _m(right, 0, w, j_right, 1, sat_right):
            continue
        return True
    return False


def _final_start(w) -> int:
    vs = [i for i, s in enumerate(w) if s.kind == "V"]
    if not vs:
        return 0
    last = vs[-1]
    return last - 1 if last >= 1 and w[last - 1].kind != "V" else last


def _syll_ok(flags, w, i, end) -> bool:
    n = len(w)
    for f in flags:
        if f == "coda":
            if w[i].kind == "V" or (end < n and w[end].kind == "V") or not any(s.kind == "V" for s in w[:i]):
                return False
        elif f == "onset":
            if not (end < n and w[end].kind == "V"):
                return False
        elif f in ("final", "nonfinal"):
            fin = i >= _final_start(w)
            if fin != (f == "final"):
                return False
        elif f in ("open", "closed"):
            op = end == n or w[end].kind == "V" or (end + 1 < n and w[end + 1].kind == "V")
            if op != (f == "open"):
                return False
    return True


def impossible(seg) -> bool:
    """A segment no mouth makes (cold review 2026-11-08, R2): an ejective (larynx 2) that is voiced or prenasalised. An
    ejective is made with the glottis closed (the larynx is the piston), so the folds cannot vibrate and no nasal airflow
    can lead it in; voiced ejective clicks (ʘ̬ʼ) and ᵑɡʼ came from intervocalic and postnasal voicing and prenasalisation
    reaching glottalic stops. A rule's output segment that is impossible where its input was not is not made: the rule
    does not act there (`_apply_one`, `_single`), as real voicing lenitions leave ejectives alone (Georgian, Quechua)."""
    return getattr(seg, "kind", None) == "C" and seg.larynx == 2 and (seg.voice == 1 or seg.prenasal != 0)


def _makes_impossible(produced, matched) -> bool:
    return any(impossible(x) for x in produced) and not any(impossible(x) for x in matched)


def _make(items, matched, focus_seg):
    res = []
    for ref, literal, sets in items:
        base = matched[ref] if ref >= 0 else literal
        res.append(replace(base, **dict(sets)) if sets else base)
    return res


def _tonekey(seg):
    return replace(seg, tone=0) if seg.tone else seg


def apply(rule: Rule, word, stress_index=None, stem_index=None, inventory=None) -> tuple:
    """Apply a rule once, regularly, left to right (a staged rule runs its steps in order). ``stress_index``: a stress
    pattern name, an Inventory (its ``.stress``), or a callable word -> stressed vowel index; default penult.
    ``stem_index``: where the root starts in the form (an int, or a callable form -> int), for root-controlled harmony;
    None takes the first vowel of the form (the root of a suffixing word). ``inventory``: the lect's inventory; an
    epenthesis rule (family "epenthesis", inserting a vowel) then inserts its epenthetic vowel
    (``inventory.epenthetic_vowel``) instead of the catalogue's ə. Every segment of a changed output that the symbol table
    cannot write (a feature brace, a doubled diacritic, ʰʱ) is snapped to the nearest table segment (``snap``)."""
    w = word if isinstance(word, tuple) else tuple(word)
    if inventory is not None:
        rule = epenthesis_for(rule, inventory)
    out = _apply_one(rule, w, stress_index, stem_index)
    for step in rule.then:
        if inventory is not None:
            step = epenthesis_for(step, inventory)
        out = _apply_one(step, out, stress_index, stem_index)
    if out is not w and out != w:
        out = snap_word(out)
        if inventory is not None and rule.family == "harmony":
            out = harmony_onto(w, out, inventory)
    return out


HARMONY_SNAP_MAX = 2.3   # furthest an inventory vowel may lie from harmony's target quality to stand in for it ((height,
#                          back x1.5, round) units, as inventory.vowel_distance): e > ɑ may become ɔ, never o


def _vq(v) -> tuple:
    return (v.height, v.back * 1.5, v.round)


def _side(v) -> int:
    return 0 if v.back < 2 else 1 if v.back == 2 else 2


def harmony_onto(before: tuple, after: tuple, inventory) -> tuple:
    """Harmony is structure-preserving: an affix vowel alternates between vowels the language already has (Turkish e/a,
    i/ı/ü/u; Finnish ä/a, ö/o, y/u). A harmonized vowel whose quality is not among the inventory's vowels takes the
    nearest vowel quality the inventory has on the same backness side (front, central, back); with none there it stays as
    it was. Before this (sound lane pass 2) harmony made new vowels, e > ɑ or o > ɤ, which then spread through whole
    families (ɑ in 26% of living lects, PHOIBLE 7%)."""
    if len(before) != len(after):
        return after
    quals = {replace(v, length=0, nasal=0, tone=0, phonation=0, source2=0, tone2=0)
             for v in getattr(inventory, "vowels", ()) if v.kind == "V"}
    if not quals:
        return after
    out = list(after)
    for i, (a, b) in enumerate(zip(before, after)):
        if b == a or b.kind != "V":
            continue
        q = replace(b, length=0, nasal=0, tone=0, phonation=0, source2=0, tone2=0)
        if q in quals:
            continue
        t = _vq(q)
        side = [(sum((p - r) ** 2 for p, r in zip(_vq(x), t)) ** 0.5, to_ipa(x), x) for x in quals if _side(x) == _side(q)]
        best = min(side, default=None)
        if best is None or best[0] > HARMONY_SNAP_MAX:
            out[i] = a   # (no partner near enough: the vowel is neutral, as Finnish e and i are)
            continue
        x = best[2]
        out[i] = replace(b, height=x.height, back=x.back, round=x.round)
    return tuple(out)


# ---------------------------------------------------------------------------------------------- output hygiene

_TABLE_SEGS: dict = {}


def _table_segments(kind: str) -> list:
    """The segments of percepts.symbols() of a kind, tone-free (the only snap targets)."""
    if not _TABLE_SEGS:
        from planet.language.percepts import symbols
        for k in ("C", "V"):
            _TABLE_SEGS[k] = sorted({replace(x.seg, tone=0) for x in symbols() if x.seg.kind == k},
                                    key=lambda q: (to_ipa(q), repr(q)))
    return _TABLE_SEGS.get(kind, [])


def writable(seg) -> bool:
    """Can the house notation write `seg` from the symbol table and the standard diacritics (no feature brace such as
    m{retroflex=1}, no doubled diacritic such as ʊ̞̞, not aspirated and breathy at once)?"""
    if getattr(seg, "kind", None) not in ("C", "V"):
        return True
    t = unicodedata.normalize("NFD", to_ipa(replace(seg, tone=0) if seg.tone else seg))
    if "{" in t or "ʰʱ" in t:
        return False
    return not any(a == b and unicodedata.combining(a) for a, b in zip(t, t[1:]))


@lru_cache(maxsize=16384)
def snap(seg):
    """`seg` itself when `writable`, else the nearest symbol-table segment of its kind (percepts.distance), a vowel
    keeping its tone."""
    if writable(seg):
        return seg
    from planet.language.percepts import distance
    unit = replace(seg, tone=0) if seg.kind == "V" and seg.tone else seg
    best = min(_table_segments(seg.kind), key=lambda q: (distance(unit, q), to_ipa(q), repr(q)), default=None)
    if best is None:
        return seg
    return replace(best, tone=seg.tone) if seg.kind == "V" and seg.tone else best


def snap_word(word) -> tuple:
    """`snap` over a form."""
    out = tuple(snap(x) for x in word)
    return out if out != tuple(word) else tuple(word)


_EPENTHESIS_CACHE: dict = {}


def epenthesis_for(rule: Rule, inventory) -> Rule:
    """An epenthesis insertion (family "epenthesis", a literal vowel inserted) re-pointed at `inventory`'s epenthetic
    vowel (inventory.epenthetic_vowel: its commonest high vowel); any other rule unchanged."""
    ch = rule.change
    if ch.kind != "insert" or rule.family != "epenthesis" or not ch.items:
        return rule
    if not all(lit is not None and getattr(lit, "kind", "") == "V" for _r, lit, _s in ch.items):
        return rule
    try:
        from planet.language.inventory import epenthetic_vowel
        v = epenthetic_vowel(inventory)
    except (ValueError, AttributeError, TypeError):
        return rule
    key = (rule.id, rule.notation, v)
    got = _EPENTHESIS_CACHE.get(key)
    if got is None:
        if all(lit == v for _r, lit, _s in ch.items):
            got = rule
        else:
            items = tuple((ref, v, sets) for ref, _lit, sets in ch.items)
            got = replace(rule, change=replace(ch, items=items, out_text=to_ipa(v)))
        if len(_EPENTHESIS_CACHE) > 4096:
            _EPENTHESIS_CACHE.clear()
        _EPENTHESIS_CACHE[key] = got
    return got


def _harmony_trigger(w, stem_index) -> int | None:
    """Index of the vowel that controls harmony: the first vowel of the root."""
    start = stem_index(w) if callable(stem_index) else (stem_index or 0)
    vs = [i for i, s in enumerate(w) if s.kind == "V"]
    if not vs:
        return None
    return next((i for i in vs if i >= start), vs[-1])


def _sat_fns(s_idx, src):
    """Stress tests for context tokens: left reads the output (``src`` maps output positions to input ones)."""
    if s_idx is None:
        return None, None
    return (lambda j: src[j] == s_idx), (lambda j: j == s_idx)


def _apply_one(rule: Rule, w: tuple, stress_index, stem_index) -> tuple:
    ch = rule.change
    env = rule.env
    target = rule.target
    if target is None:
        return _apply_insert(rule, w, stress_index)
    tm = target._memo   # (the class memo read inline: this loop is the pass's hottest; PW-1555)
    for s in w:
        r = tm.get(s)
        if r is None:
            r = target(s)
        if r:
            break
    else:
        return w
    n = len(w)
    k = len(rule.span)
    need_stress = env.stress is not None
    ctx = env.ctx_stress
    s_idx = _stress_of(w, stress_index) if (need_stress or ctx) else None
    src: list = []  # input index of each output segment (only kept for stressed contexts)
    sat_l, sat_r = _sat_fns(s_idx, src) if ctx else (None, None)
    trig = _harmony_trigger(w, stem_index) if ch.kind == "assimilate" and ch.source == "first_vowel" else None
    out: list = []
    i = 0
    changed = False
    while i < n:
        seg = w[i]
        end = i + 1 + k
        r = tm.get(seg)
        if r is None:
            r = target(seg)
        if r and end <= n and all(p(w[i + 1 + q]) for q, p in enumerate(rule.span)) \
                and (not need_stress or _stress_ok(env.stress, s_idx, i, seg)) \
                and (not env.syll or _syll_ok(env.syll, w, i, end)) \
                and _env_ok(env, out, w, end, sat_l, sat_r):
            produced = _produce(ch, w, i, end, out, trig)
            if produced is not None and _makes_impossible(produced, w[i:end]):
                produced = None   # (no voiced or prenasalised ejective: `impossible`)
            if produced is not None:
                before = len(out)
                if ch.left_set and before and out[-1].kind == "V":
                    out[-1] = replace(out[-1], **dict(ch.left_set))
                out.extend(produced)
                if ctx:
                    src.extend([i] * len(produced))
                changed = changed or tuple(produced) != w[i:end] or (ch.left_set and before > 0)
                i = end
                continue
        out.append(seg)
        if ctx:
            src.append(i)
        i += 1
    return tuple(out) if changed else w


def _stress_ok(want, s_idx, i, seg) -> bool:
    if s_idx is None or seg.kind != "V":
        return False
    return (i == s_idx) == (want == "stressed")


def _produce(ch: Change, w, i, end, out, trig=None):
    kind = ch.kind
    if kind == "map":
        key = _tonekey(w[i])
        for inp, items in ch.pairs:
            if inp == key:
                return _make(items, w[i:end], w[i])
        return None
    if kind == "assimilate":
        src = None
        if ch.source == "right":
            src = w[end] if end < len(w) else None
        elif ch.source == "left":
            src = out[-1] if out else None
        elif ch.source == "prev_vowel":
            src = next((s for s in reversed(out) if s.kind == "V"), None)
        elif ch.source == "first_vowel":  # the root's first vowel (trig), read from the input
            src = w[trig] if trig is not None else None
        if src is None:
            return None
        axes = ch.axes + _PLACE_AXES if "place" in ch.axes else ch.axes
        if ch.source == "first_vowel" and "round" in axes and w[i].kind == "V" and w[i].height < 5:
            # (rounding harmony spreads rounding to the high vowels only, as in Turkish: göz-ün, kız-ın, but göz-ler, not
            # *göz-lör; a non-high vowel takes the root's backness and may lose its rounding after an unrounded root,
            # never gain it. Before 2026-11-07 a > ɒ here made ɒ a living vowel in a sixth of all lects)
            # (lexcon pass 2, 2026-11-08: going back, a front unrounded mid vowel opens to the low back vowel, as Turkish
            # -ler/-lar and Hungarian -nek/-nak pair e with a, and a rounded one keeps its rounding; a central one (ə, ɐ)
            # is neutral. Before, e > ɤ and o > ɤ (unrounded after a back unrounded root) made ɤ a living vowel in 12% of
            # all lects, 5x PHOIBLE's share. Going front, a rounded vowel still unrounds after an unrounded root.)
            if w[i].back == 2:
                return [w[i]]
            new = replace(w[i], back=src.back)
            if src.back >= 3:
                if not w[i].round and w[i].back < 2 and w[i].height >= 1:
                    new = replace(new, height=0)
            elif not src.round and w[i].round:
                new = replace(new, round=0)
            return [new]
        return [replace(w[i], **{a: getattr(src, a) for a in axes})]
    return _make(ch.items, w[i:end], w[i])


def _apply_insert(rule: Rule, w, stress_index=None) -> tuple:
    env = rule.env
    out: list = []
    src: list = []
    sat_l = sat_r = None
    if env.ctx_stress:
        sat_l, sat_r = _sat_fns(_stress_of(w, stress_index), src)
    changed = False
    lit_seg = rule.change.items[0][1]
    for g in range(len(w) + 1):
        if _env_ok(env, out, w, g, sat_l, sat_r) and (not out or out[-1] != lit_seg):
            out.append(lit_seg)
            src.append(-1)
            changed = True
        if g < len(w):
            out.append(w[g])
            src.append(g)
    return tuple(out) if changed else w


def applies(rule: Rule, segments: Iterable) -> bool:
    """True when the lect has a segment the rule can act on (an insertion always can); a staged rule when any of its steps
    can."""
    if rule.target is None:
        return True
    if rule.then:
        segs = list(segments)
        return any(applies(r, segs) for r in (replace(rule, then=()),) + tuple(rule.then))
    return any(rule.target(s) for s in segments)


def apply_all(rule: Rule, forms: Sequence, stress_index=None, stem_index=None) -> list:
    return [apply(rule, f, stress_index, stem_index) for f in forms]


# ---------------------------------------------------------------------------------------------- functional load + pick

def functional_load(rule: Rule, lexicon_forms: Sequence, stress_index=None, outputs: Sequence | None = None) -> float:
    """Wedel-style contrast load: the fraction of forms that lose a contrast to the rule. A form counts when (a) it is in a
    segment-level minimal pair the rule's segment mapping merges (the two forms differ at one position only, and the rule
    maps one side's segment onto the other's, or both onto one output, or deletes the segment that is the only
    difference), whether or not that pair stands in the rule's environment (the load is the contrast's, Wedel et al.
    2013); or (b) applying the rule makes it a homophone of a form it was distinct from. A deletion is the exception to the
    context-free reading: two segments it deletes, or a segment and zero, merge only in the forms it actually changes
    (apocope does not merge kata and kita; counted context-free, it was vetoed ~90% while paragoge, merging nothing, never
    was, and lects drifted to no final consonants; sound lane pass 3). ``outputs``: the forms after the rule, if already
    computed."""
    forms = list(dict.fromkeys(tuple(f) for f in lexicon_forms))
    if not forms:
        return 0.0
    hit: set = set()
    # (b) homophones actually created
    outs = [tuple(o) for o in outputs] if outputs is not None and len(outputs) == len(lexicon_forms) else None
    if outs is not None:
        pairs = dict(zip((tuple(f) for f in lexicon_forms), outs))
    else:
        pairs = {f: apply(rule, f, stress_index) for f in forms}
    groups: dict = {}
    for f in forms:
        groups.setdefault(pairs[f], []).append(f)
    for g in groups.values():
        if len(g) > 1:
            hit.update(g)
    # (a) minimal pairs whose contrast the rule's segment mapping removes
    memo: dict = {}

    def m(seg):
        r = memo.get(seg, 0)
        if r == 0:
            o = _single(rule, seg) if rule.target is not None and rule.target(seg) else None
            r = memo[seg] = None if o is None else tuple(_tonekey(x) for x in o)
        return r

    buckets: dict = {}
    fset = set(forms)
    for f in forms:
        for i, seg in enumerate(f):
            buckets.setdefault((f[:i], f[i + 1:]), []).append((_tonekey(seg), f))
            if m(seg) == () and pairs[f] != f and (f[:i] + f[i + 1:]) in fset:  # deleting the one difference
                hit.add(f)
                hit.add(f[:i] + f[i + 1:])
    for members in buckets.values():
        if len(members) < 2:
            continue
        for a in range(len(members)):
            xa, fa = members[a]
            ma = m(xa)
            for b in range(a + 1, len(members)):
                xb, fb = members[b]
                if xa == xb:
                    continue
                mb = m(xb)
                if ma == mb == ():
                    continue  # (two segments a deletion removes merge only where it removes them: homophones, (b) above)
                if (ma is not None and (ma == (xb,) or ma == mb)) or (mb is not None and mb == (xa,)):
                    hit.add(fa)
                    hit.add(fb)
    return len(hit) / len(forms)


def veto_probability(load: float) -> float:
    return 1.0 - math.exp(-FL_K * load)


PICK_STATS = {"picks": 0, "noop_draws": 0, "vetoed": 0}  # diagnostics, per process


def cumulative_weights(rules: Sequence[Rule]) -> list:
    """Running sums of the rules' weights (pick_rule draws on them by bisection)."""
    out, acc = [], 0.0
    for r in rules:
        acc += max(0.0, r.weight)
        out.append(acc)
    return out


def pick_rule(rng, rules: Sequence[Rule], lexicon_forms: Sequence, inventory_segments: Iterable,
              stress_index=None, mass: float | None = None, cum: list | None = None, memo: dict | None = None) -> Rule | None:
    """Draw one rule by weight, once (PW-1551, owner ruling 11-08: no redraw). A draw that lands on a rule whose input the
    inventory lacks, or that would change none of ``lexicon_forms`` (its environment never met), fires nothing (counted
    in ``PICK_STATS["noop_draws"]``), so each rule fires in proportion to its weight wherever it applies and the
    catalogue's naturalness sets how often it fires. ``mass`` is the total weight the draw is made against when the
    caller has set some rules aside (lect.Lect.rule_pool: rows waiting out their re-fire memory); a draw landing in that
    set-aside mass also fires nothing, so a row being blocked does not make the others commoner. Then veto the rule with
    probability ``1 - exp(-FL_K * functional_load)``. A vetoed vowel merger offers a dispersion rule that moves the crowded
    vowel away instead (itself subject to the veto). Returns None when nothing fires this time. ``rng`` is a
    ``numpy.random.Generator`` or ``random.Random`` (only ``.random()`` is used). ``cum``: the rules' cumulative weights
    (cumulative_weights), when the caller draws many times from one pool (most draws fire nothing, so the draw itself is
    the cost).

    (Until PW-1551 a no-op draw was set aside and redrawn up to 16 times: the draw was then among the few rules that
    applied now, and nearly every one fired as soon as its re-fire wait allowed, whatever its weight.)

    ``memo``: a dict the caller keeps while ``lexicon_forms``, ``inventory_segments`` and ``stress_index`` stay the same
    (PW-1555): a rule drawn again is not run over the forms again (whether it applies, changes any form, and its
    functional load are worked out once). The draws and the veto use the rng exactly as without it."""
    PICK_STATS["picks"] += 1
    if cum is None:
        cum = cumulative_weights(rules)
    tot = cum[-1] if cum else 0.0
    x = rng.random() * max(tot, mass or 0.0)
    if x >= tot:  # (the set-aside mass, or nothing to draw)
        PICK_STATS["noop_draws"] += 1
        return None
    rule = rules[min(bisect.bisect_right(cum, x), len(rules) - 1)]
    if rule is None:
        PICK_STATS["noop_draws"] += 1
        return None
    got = memo.get(id(rule)) if memo is not None else None
    if got is None or got[0] is not rule:
        load = _pick_load(rule, lexicon_forms, inventory_segments, stress_index)
        if memo is not None:
            memo[id(rule)] = got = (rule, load)
    else:
        load = got[1]
    if load is None:   # (no input in the inventory, or no form changed)
        PICK_STATS["noop_draws"] += 1
        return None
    if rng.random() >= veto_probability(load):
        return rule
    PICK_STATS["vetoed"] += 1
    key = ("push", id(rule))
    pg = memo.get(key) if memo is not None else None
    if pg is None or pg[0] is not rule:
        inv = list(inventory_segments)
        push = dispersion_rule(rule, inv)
        pl = None if push is None else functional_load(push, [tuple(f) for f in lexicon_forms], stress_index)
        pg = (rule, push, pl)
        if memo is not None:
            memo[key] = pg
    _r, push, pl = pg
    if push is None:
        return None
    if rng.random() >= veto_probability(pl):
        return push
    return None


def _pick_load(rule: Rule, lexicon_forms: Sequence, inventory_segments: Iterable, stress_index) -> float | None:
    """pick_rule's deterministic part for one rule: None when it fires nothing (its input is not in the inventory, or it
    changes none of the forms), else its functional load over the forms."""
    if not applies(rule, list(inventory_segments)):
        return None
    forms = [tuple(f) for f in lexicon_forms]
    outs = apply_all(rule, forms, stress_index)
    if forms and all(a == b for a, b in zip(outs, forms)):
        return None
    return functional_load(rule, forms, stress_index, outputs=outs)


def dispersion_rule(rule: Rule, inventory_segments: Iterable) -> Rule | None:
    """For a vowel rule that would merge vowel v into an existing vowel o, the push-chain step: o moves on in the same
    direction (or, at the edge of the space, centralizes), so v can follow later without a merger."""
    inv = [s for s in inventory_segments if s.kind == "V"]
    keys = {_tonekey(s): s for s in inv}
    if rule.target is None or rule.change.kind in ("delete", "insert", "rewrite", "metathesis") or rule.span:
        return None
    for v in inv:
        if not rule.target(v):
            continue
        outs = _single(rule, v)
        if not outs or len(outs) != 1 or outs[0].kind != "V":
            continue
        o = keys.get(_tonekey(outs[0]))
        if o is None or _tonekey(o) == _tonekey(v):
            continue
        dh = (o.height > v.height) - (o.height < v.height)
        db = (o.back > v.back) - (o.back < v.back)
        moved = replace(o, height=min(6, max(0, o.height + dh)), back=min(4, max(0, o.back + db)))
        if _tonekey(moved) == _tonekey(o):  # at the edge: a central vowel lowers; a peripheral one has nowhere to go (no push:
            # centralizing i > ɨ, u > ʉ here, drawn in every lect, made ɨ three of the four commonest vowels of the run)
            if o.back != 2:
                continue
            moved = replace(o, height=max(0, o.height - 1))
        if _tonekey(moved) == _tonekey(o):
            continue
        if dh and moved.back in (0, 4) and moved.height in (1, 3, 5):  # (a front or back vowel stepping onto an in-between
            # height, i̞ e̞ o̞ ɛ̞, goes on to the next full one, as a push chain moves e to i, not to a raised e (PW-1566:
            # one-step pushes put i̞ in 10% and e̞ in 16% of living lects, PHOIBLE 0.2% and 2%); where that one is taken it
            # would merge, so no push)
            moved = replace(moved, height=min(6, max(0, moved.height + dh)))
            if _tonekey(moved) in keys:
                continue
        sets = tuple((a, getattr(moved, a)) for a in ("height", "back") if getattr(moved, a) != getattr(o, a))
        tgt = lit(_tonekey(o))
        return Rule(
            id=f"dispersion.push.{to_ipa(_tonekey(o))}", target=tgt, change=Change("set", items=((0, None, sets),)),
            cause="dispersion", needs=frozenset({"tongue_body"}), weight=rule.weight, family="chain_shift",
            example="Great Vowel Shift: as eː rose, iː moved out of its way (iː > əɪ)",
            notation=f"{to_ipa(o)} > {to_ipa(moved)} (push chain from {rule.id})",
        )
    return None


def _single(rule: Rule, seg):
    """The rule's output for a lone segment (context ignored), or None when it does not act on it. A staged rule runs its
    steps in order on the lone segment (a chain shift in drag order: p > f, then b > p leaves b as p, not f)."""
    if rule.then:
        cur, hit = [seg], False
        for st in (replace(rule, then=()),) + tuple(rule.then):
            if len(cur) != 1:
                break
            o = _single(st, cur[0])
            if o is not None:
                hit = hit or list(o) != cur
                cur = list(o)
        return cur if hit else None
    ch = rule.change
    if rule.target is None or not rule.target(seg):
        return None
    if ch.kind == "map":
        key = _tonekey(seg)
        for inp, items in ch.pairs:
            if inp == key:
                o = _make(items, (seg,), seg)
                return None if _makes_impossible(o, (seg,)) else o
        return None
    if ch.kind == "assimilate":
        return [seg]
    if rule.span:
        return None
    o = _make(ch.items, (seg,), seg)
    return None if _makes_impossible(o, (seg,)) else o


# ------------------------------------------------------------------------------------------------------- catalogue

def profile_capabilities(profile) -> frozenset:
    """The profile's articulators (plain names, ``profile.articulators`` only) plus "hear:<axis>" for every heard axis
    (resolution > 0; an axis missing from ``hear`` counts as heard). The namespaces are kept apart because ``larynx`` is
    both an articulator and a percept axis: a syrinx-voiced bird hears laryngeal contrasts but has no larynx."""
    caps = set(getattr(profile, "articulators", ()) or ())
    if "syrinx" in caps:
        caps.add("larynx")  # a rule's "larynx" need means a voice source: a syrinx-voiced bird has one (voicing is made there)
    hear = getattr(profile, "hear", None) or {}
    for ax in AXES:
        if hear.get(ax, 1.0) > 0:
            caps.add(HEAR_PREFIX + ax)
    return frozenset(caps)


def _need(token: str) -> str | None:
    x = token.strip()
    return NEEDS_ALIAS.get(x, x)


@lru_cache(maxsize=1)
def _protos() -> tuple:
    out = []
    for s in "p t k q ʔ b d g f v θ ð s z ʃ x ɣ χ h m n ŋ l r ɾ j w ts tʃ dʒ kʷ pʰ ɓ i e ɛ a ɑ o ɔ u y ə ɨ iː aː uː ã".split():
        try:
            segs = from_ipa(s)
        except Exception:  # noqa: BLE001 - a symbol the table lacks
            continue
        if len(segs) == 1:
            out.append(segs[0])
    return tuple(out)


def _mult(profile, seg) -> float:
    """The species' make-cost multiplier for a segment relative to humans (1 = human)."""
    from planet.language import profiles as _p

    fn = getattr(_p, "make_multiplier", None)
    if fn is not None:
        return float(fn(profile, seg))
    keys = _p.keys_of(seg) if hasattr(_p, "keys_of") else ()
    m = 1.0
    mc = getattr(profile, "make_cost", {}) or {}
    for k in keys:
        m *= mc.get(k, 1.0)
    return m


def cost_factor(rule: Rule, profile) -> float:
    """Weight multiplier from the species' make costs: geometric mean over prototype segments of
    sqrt(cost of what the rule removes / cost of what it produces), clamped to [0.2, 5]. 0 if every output is
    impossible for the species."""
    logs = []
    impossible = 0
    if rule.target is None:
        m = _mult(profile, rule.change.items[0][1])
        return 0.0 if math.isinf(m) else max(0.2, min(5.0, 1.0 / math.sqrt(max(m, 1e-6))))
    for seg in _protos():
        outs = _single(rule, seg)
        if outs is None:
            if rule.span and rule.target(seg):
                outs = []  # cluster rule: score the focus as removed
            else:
                continue
        m_in = _mult(profile, seg)
        if math.isinf(m_in):
            continue
        m_out = 1.0
        for o in outs:
            m_out *= _mult(profile, o)
        if math.isinf(m_out):
            impossible += 1
            continue
        logs.append(0.5 * (math.log(max(m_in, 1e-6)) - math.log(max(m_out, 1e-6))))
    if not logs:
        return 0.0 if impossible else 1.0
    return max(0.2, min(5.0, math.exp(sum(logs) / len(logs))))


# catalogue rows whose table weight or scope the review of run a24559 overturned: ʔ-prothesis before every initial vowel
# fired 8,685 times and made 33% of core words ʔ-initial (rare, word-by-word in the record: Blevins 2004 on prothetic ʔ)
ROW_OVERRIDES = {"S042": {"naturalness": "1", "scope": "diffusing"}}


def load_tsv(path: Path | str = DATA) -> tuple[list[Rule], list[tuple[str, str, str]]]:
    """Parse the sound-change table. Returns (rules, failures as (id, notation, reason))."""
    rules, failures = [], []
    with open(path, encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.startswith("#") and ln.strip()]
    for row in csv.DictReader(lines, delimiter="\t"):
        row = {**row, **ROW_OVERRIDES.get(row.get("id", ""), {})}
        got, why = parse_rows(row)
        if not got:
            failures.append((row.get("id", ""), row.get("rule", ""), why))
        rules += got
    return rules, failures


def parse_rows(row: dict) -> tuple[list[Rule], str]:
    """Like parse_rule, but a row holding several rules ("mb > mm, nd > nn"; "æ > eə ; ɑ > a") becomes sub-rules with ids
    S081a, S081b, ... (an environment written once at the end applies to all of them). Parts that fail are skipped."""
    r, why = parse_rule(row)
    if r is not None:
        return [r], ""
    if why not in ("several rules in one row", "several changes in one row"):
        return [], why
    text = re.sub(r"\(([^()]*)\)", lambda m: "" if " " in m.group(1) else m.group(0), row.get("rule", ""))
    parts = [p.strip() for p in text.split(";")] if ";" in text else _split_top(text)
    parts = [p for p in parts if ">" in p]
    envs = [re.split(r"\s/\s", p, maxsplit=1)[1] for p in parts if re.search(r"\s/\s", p)]
    if len(envs) == 1 and not re.search(r"\s/\s", parts[0]):
        parts = [p if re.search(r"\s/\s", p) else f"{p} / {envs[0]}" for p in parts]
    out, reasons = [], []
    for k, part in enumerate(parts):
        sub, w = parse_rule(dict(row, id=f"{row.get('id', '')}{'abcdefgh'[k]}", rule=part))
        if sub is None:
            reasons.append(w)
        else:
            out.append(sub)
    return out, "; ".join(reasons)


@lru_cache(maxsize=4)
def _tsv_cached(path: str):
    return load_tsv(path)


def _tok_key(t):
    return (t[0], t[1].spec, *t[2:]) if len(t) > 1 else t


def rule_key(rule: Rule) -> tuple:
    """A structural key: two rules with the same key make the same change in the same places (ids, weights, examples
    and wording aside)."""
    env = rule.env
    alts = tuple((tuple(_tok_key(t) for t in l), tuple(_tok_key(t) for t in r)) for l, r in env.alts)
    return (None if rule.target is None else rule.target.spec, tuple(p.spec for p in rule.span),
            replace(rule.change, out_text=""), alts, env.stress, env.syll, tuple(rule_key(s) for s in rule.then))


# Rules whose tsv twin is written differently (the structural key does not catch it): the key's rule is kept, the listed
# ids are dropped.
SAME_AS = {
    "nasal.nasal_loss": ("S140",),
    "rhotic.l_vocalization": ("S151",),
    "tone.onset_voicing_split": ("S166",),
    "tone.glottal_coda_rising": ("S167",),
    "tone.h_coda_falling": ("S168",),
    # (sinks round, 2026-11-04: single-stop rows that repeat part of a demo rule or of another row; drawn beside it they
    # doubled the weight of that change for p, t, k and the voiced stops)
    "lenition.intervocalic_voicing": ("S010", "S011", "S012"),  # p, t, k > b, d, g / V_V (Spanish lobo, vida, agudo)
    "lenition.spirantization": ("S005", "S006", "S007"),  # b, d, g > β, ð, ɣ / V_V (Spanish lobo, nada, lago)
    "S037": ("S036",),  # k > ʔ / _# (Malay budak) is S037's k > ʔ again, the commonest ʔ source
    "umlaut.i": ("S135",),  # (sound lane pass 3: the same i-umlaut twice; once apocope ran again, y was in 21% of living lects)
}


def deduplicated(pool: Sequence[Rule]) -> list[Rule]:
    """Drop a rule that repeats an earlier one (same ``rule_key``, or listed in ``SAME_AS``), so a change written twice
    does not draw at double weight. The first is kept (demo rules come first), except that between two later twins the
    heavier is kept."""
    drop = {x for xs in SAME_AS.values() for x in xs}
    out: list[Rule] = []
    seen: dict = {}
    for r in pool:
        if r.id in drop:
            continue
        k = rule_key(r)
        j = seen.get(k)
        if j is None:
            seen[k] = len(out)
            out.append(r)
        elif out[j].id not in DEMO_IDS and r.weight > out[j].weight:
            out[j] = r
    return out


# PW-1551 (owner ruling 11-08, option A): the naturalness column (1 rare, needs special conditions .. 5 extremely common) is
# an ordinal judgement; the draw reads it as a log scale, each step NATURAL_BASE times as often as the one below (weight
# NATURAL_BASE ** (n - 3): 1 -> 0.11, 2 -> 0.33, 3 -> 1, 4 -> 3, 5 -> 9). Read linearly, 1 .. 5 spans only 5x, less than
# one standard deviation of the line drift (lect.LINE_ROW_SIGMA x LINE_FAMILY_SIGMA, combined sigma 1.2, x3.4), and a row
# whose input is there fires within a kyr or so either way, so rare changes ran on most lines. Isolated-lect harness
# (calibration.md, PW-1551 lane): firings a line, naturalness 1 vs 5 rows, 0.55 vs 1.59 before (2.9x), 0.20 vs 2.08 now.
NATURAL_BASE = 3.0


def natural_weight(n: float) -> float:
    """The draw weight of a row of naturalness ``n`` (NATURAL_BASE ** (n - 3); 0 for 0)."""
    return NATURAL_BASE ** (float(n) - 3.0) if n > 0 else 0.0


# PW-1545: the make-cost keys (profiles.keys_of) a segment carries because of an articulator. A row's ``needs`` names the
# parts of the mouth its change involves; a voice lacking one keeps the row when the change only takes that gesture away
# (``exit_only``): a lipless people still has costly stand-ins for w, kʷ, m and rounded vowels (its proto-inventory is
# drawn with their costs), and losing them (kʷ > k, w > ∅, m > ∅ / _#, Ṽ > V) asks nothing of lips or a velum. Articulators
# with no key here (tongue root, pharynx, beak, syrinx) are never excused.
ARTICULATOR_KEYS = {"lips": frozenset({"labial", "round_vowel", "labialized", "labiodental", "double"}),
                    "velum": frozenset({"nasal", "nasal_vowel", "prenasal"}),
                    "teeth": frozenset({"labiodental"})}
_EXIT_EXTRA = "tʷ dʷ nʷ sʷ lʷ rʷ gʷ ŋʷ xʷ ᵐb ⁿd ᵑɡ pf ẽ õ ĩ ũ ɔ̃ ɛ̃ ø œ ʏ ʊ β ɸ ʋ ɱ k͡p ɡ͡b ŋ͡m".split()


@lru_cache(maxsize=1)
def _exit_probes() -> tuple:
    """Probe words for ``exit_only``: each probe segment alone, word-initial, word-final and between vowels (a i u o),
    and every pair of probe consonants between a's (cluster rows)."""
    segs = list(_protos())
    for s in _EXIT_EXTRA:
        try:
            x = from_ipa(s)
        except Exception:  # noqa: BLE001 - a symbol the table lacks
            continue
        segs += [y for y in x if y not in segs]
    vs = [from_ipa(v)[0] for v in "aiuo"]
    a = vs[0]
    words = []
    for s in segs:
        words += [(s,), (s, a), (a, s), (a, s, a, a)]
        words += [(v1, s, v2) for v1 in vs for v2 in vs]
    cs = [s for s in segs if s.kind == "C"]
    words += [(a, s, t, a) for s in cs for t in cs] + [(s, t, a) for s in cs for t in cs] + [(a, s, t) for s in cs for t in cs]
    words += [(a, v, c) for v in segs if v.kind == "V" for c in cs]
    return tuple(words)


def _gestures(word, keys: frozenset) -> int:
    """How many of the ``keys`` (make-cost keys of the missing articulators) the segments of ``word`` carry, summed."""
    from planet.language import profiles as _p
    return sum(len(_p.keys_of(s) & keys) for s in word)


@lru_cache(maxsize=4096)
def exit_only(rule: Rule, missing: frozenset) -> bool:
    """True when ``rule`` never adds a gesture of a ``missing`` articulator on a probe word, and either takes one away
    somewhere or never touches one (gestures counted as that articulator's make-cost keys per segment: v carries labial
    + labiodental, b labial only, so v > b takes one away; kʷ > p and p > ɸ trade one for one and stay barred; the j part
    of a row "∅ > j / i_V, ∅ > w / u_V" listed under the row's lips need never uses lips). False when a missing need has
    no make-cost keys (``ARTICULATOR_KEYS``) or the rule changes no probe."""
    if any(m not in ARTICULATOR_KEYS for m in missing):
        return False
    from planet.language import profiles as _p
    keys = frozenset().union(*(ARTICULATOR_KEYS[m] for m in missing))
    fewer = touched = acted = False
    for w in _exit_probes():
        try:
            o = tuple(apply(rule, w))
        except Exception:  # noqa: BLE001 - a probe the rule cannot read
            continue
        if o == w:
            continue
        acted = True
        gi, go = _gestures(w, keys), _gestures(o, keys)
        if go > gi:
            return False
        fewer = fewer or go < gi
        if not touched:
            rest = list(w)
            for x in o:
                if x in rest:
                    rest.remove(x)
                elif _p.keys_of(x) & keys:
                    touched = True   # (a new segment that carries the gesture: a lip-to-lip change, p > ɸ)
                    break
    return acted and (fewer or not touched)


def catalogue(profile, include_tsv: bool = True, path: Path | str = DATA) -> list[Rule]:
    """DEMO_RULES plus the parsed tsv rules that the species can run (``needs`` within its articulators and heard axes,
    or a missing articulator that the change only takes away: ``exit_only``, PW-1545), deduplicated, with ``weight`` the
    row's naturalness read as a log scale (natural_weight) and scaled by ``cost_factor``. Rules whose every output the
    species cannot make are dropped."""
    caps = profile_capabilities(profile)
    pool = list(DEMO_RULES)
    if include_tsv and Path(path).exists():
        pool += _tsv_cached(str(path))[0]
    out = []
    for r in deduplicated(pool):
        if not r.needs <= caps and not exit_only(r, frozenset(r.needs - caps)):
            continue
        f = cost_factor(r, profile)
        if f <= 0:
            continue
        out.append(replace(r, weight=natural_weight(r.weight) * f))
    return out


# ----------------------------------------------------------------------------------------------------------- parser

_SPECIAL = set(" #()[]{}*_,∅") | set(CLASSES)
_BLOCK = (("...", "a long-distance (non-adjacent) change"), ("…", "a long-distance (non-adjacent) change"),
          ("then", "a staged change (several steps in one row)"), (";", "several changes in one row"),
          ("same", "needs identity between segments"), ("paradigm", "analogy, not a sound change"),
          ("analogical", "analogy, not a sound change"), ("tone", "a tone system rule"),
          ("suffix", "morphology-conditioned"), ("ATR", "the ATR axis does not exist in the percept space"),
          ("V1", "indexed segments"), ("H ", "tone letters"), ("contour", "a prosody-system rule"))
_LENGTHEN = re.compile(r"(compensatory|vowel) lengthening")


@dataclass
class _Tok:
    typ: str                 # lit | cls | edge | null | flag
    text: str = ""
    pat: Pattern | None = None
    seg: object = None
    sets: dict = field(default_factory=dict)
    opt: bool = False
    star: bool = False
    stress: str | None = None
    alpha: str | None = None
    flag: str | None = None
    base: str = ""


class ParseError(ValueError):
    pass


def _axis_words(ax: str, lo: int, hi: int) -> str:
    """Plain words for an [axis=v] bracket (the second voice's; others as 'axis v')."""
    if ax == "source2" and lo == hi:
        return "second-voice" if lo else "one-voice"
    if ax == "tone2":
        if lo == hi == 0:
            return "parallel second voice"
        if lo == hi:
            return f"{_TONE_WORDS.get(lo, lo)} second voice"
        if (lo, hi) == (4, 5):
            return "rising or falling second voice"
        return "own-tone second voice"
    return f"{ax} {lo}" + (f"..{hi}" if hi != lo else "")


def _bracket(body: str) -> _Tok:
    """Contents of [...]: features (+voice, −son, αplace), class letters, axis=v / axis=lo..hi, stress, house flags."""
    tok = _Tok("cls", text=f"[{body}]")
    pat = None
    for item in body.replace("−", "-").split():
        if item in CLASSES:
            p = CLASSES[item]
            tok.base = tok.base or item
        elif item in SYLL_FLAGS:
            tok.typ, tok.flag = "flag", item
            continue
        elif item in ("+stress", "-stress"):
            tok.stress = "stressed" if item[0] == "+" else "unstressed"
            continue
        elif item[0] == "α":
            ax = item[1:]
            if ax not in ALPHA_AXES:
                raise ParseError(f"cannot agree in {ax!r}")
            tok.alpha = ax
            continue
        elif "=" in item:
            ax, val = item.split("=", 1)
            lo, hi = (int(x) for x in val.split("..")) if ".." in val else (int(val),) * 2
            if ax not in AXES:
                raise ParseError(f"unknown axis {ax!r}")
            p = Pattern(f"[{item}]", ("b", None, ((ax, lo, hi),)), _axis_words(ax, lo, hi))
            if lo == hi:
                tok.sets[ax] = lo
        elif item in FEATURES or (item[0] in "+-" and item[1:] in FEATURES):
            if item[0] not in "+-":
                item = "+" + item
            pos, neg, sp, sn = FEATURES[item[1:]]
            p = pos if item[0] == "+" else neg
            sets = sp if item[0] == "+" else sn
            if p is None:
                raise ParseError(f"no class for {item!r}")
            if sets:
                tok.sets.update(sets)
            else:
                tok.sets["__unsettable__"] = item
        else:
            raise ParseError(f"unknown feature {item!r}")
        pat = p if pat is None else (pat & p)
    if tok.typ == "flag" and pat is None and tok.stress is None:
        return tok
    if pat is None and tok.stress is not None and tok.alpha is None and not tok.sets:
        tok.typ = "flag"
        return tok
    tok.pat = pat
    return tok


def _tokens(s: str) -> list[_Tok]:
    toks: list[_Tok] = []
    i, n = 0, len(s)
    glue = None  # a stress flag written straight before a segment ([−stress]V): it belongs to that segment
    while i < n:
        c = s[i]
        start = len(toks)
        if c.isspace():
            glue = None
            i += 1
            continue
        if c == "#":
            toks.append(_Tok("edge", "#"))
            i += 1
        elif c == "∅":
            toks.append(_Tok("null", "∅"))
            i += 1
        elif c == "*":
            if not toks:
                raise ParseError("* with nothing before it")
            toks[-1].star = True
            i += 1
        elif c == "(":
            j = s.find(")", i)
            if j < 0:
                raise ParseError("unclosed (")
            inner = _tokens(s[i + 1:j])
            if len(inner) != 1:
                raise ParseError("optional group must hold one segment")
            inner[0].opt = True
            toks.append(inner[0])
            i = j + 1
        elif c == "[":
            j = s.find("]", i)
            if j < 0:
                raise ParseError("unclosed [")
            b = _bracket(s[i + 1:j])
            prev = toks[-1] if toks else None
            glued_left = prev is not None and i > 0 and not s[i - 1].isspace() and prev.typ in ("cls", "lit")
            if glued_left and b.typ != "flag":
                _merge(prev, b)  # V[+back], C[αplace]
            elif glued_left and b.typ == "flag" and b.stress:
                prev.stress = b.stress
            elif b.typ == "flag" and b.stress and not b.flag and j + 1 < n and (s[j + 1] in CLASSES or
                                                                               s[j + 1] not in _SPECIAL):
                i = j + 1
                glue = b.stress
                continue
            else:
                toks.append(b)
            i = j + 1
        elif c in CLASSES:
            t = _Tok("cls", c, pat=CLASSES[c], base=c)
            i += 1
            i = _diacritics(s, i, t)
            toks.append(t)
        else:
            j = i
            while j < n and s[j] not in _SPECIAL and not (s[j] in "ː̃́" and j == i):
                j += 1
            run = s[i:j]
            if not run:
                raise ParseError(f"unexpected {c!r}")
            for seg in _ipa(run):
                toks.append(_Tok("lit", to_ipa(seg), pat=lit(seg), seg=seg, base=to_ipa(replace(seg, length=0))))
            i = j
        if glue is not None:
            if len(toks) > start and toks[start].typ in ("cls", "lit"):
                toks[start].stress = glue
            glue = None
    return toks


def _ipa(run: str):
    if re.search(r"[A-Za-z]{3,}", run) and not re.fullmatch(r"[a-z]{3}", run):
        raise ParseError(f"free text {run!r}")
    if run[0] in "ʰʼʷʲˠˤːᴺ" or unicodedata.combining(run[0]):
        raise ParseError(f"modifier with no segment in {run!r}")
    try:
        segs = from_ipa(run, strict=True)
    except ValueError as e:
        raise ParseError(f"unknown symbol in {run!r}") from e
    if not segs:
        raise ParseError(f"no segments in {run!r}")
    return segs


def _diacritics(s: str, i: int, t: _Tok) -> int:
    s2 = False  # just after ᴖ: tone letters are the second voice's (Vᴖ˨˦, as percepts.from_ipa reads them)
    while i < len(s) and (s[i] in DIACRITICS or s[i] == STRESS_MARK or s[i] in TONE_LETTERS or s[i] == SOURCE2_MARK):
        if s[i] == SOURCE2_MARK:  # Vᴖ: a second-voice vowel (syrinx lane, 2026-11-08)
            t.sets["source2"] = 1
            t.pat = t.pat & cls("ᴖ", None, "second-voice", source2=1)
            s2 = True
            i += 1
            continue
        if s[i] in TONE_LETTERS:  # V˨: a vowel with that tone (Chao letters, as percepts.from_ipa reads them)
            j = i
            while j < len(s) and s[j] in TONE_LETTERS:
                j += 1
            tone = from_ipa("a" + s[i:j])[0].tone
            ax = "tone2" if s2 else "tone"
            t.sets[ax] = tone
            t.pat = t.pat & cls(s[i:j], None, f"{_TONE_WORDS.get(tone, tone)}-toned" + (" second voice" if s2 else ""),
                                **{ax: tone})
            s2 = False
            i = j
            continue
        if s[i] == STRESS_MARK:
            t.stress = "stressed"
        else:
            ax, v = DIACRITICS[s[i]]
            t.sets[ax] = v
            t.pat = t.pat & cls(s[i], None, {"length": "long", "nasal": "nasal", "larynx": "aspirated" if v == 1 else
                                             "ejective", "secondary": "secondary-articulated",
                                             "phonation": "breathy" if v == 1 else "creaky"}[ax], **{ax: v})
        i += 1
    return i


def _merge(prev: _Tok, b: _Tok):
    prev.text += b.text
    if b.pat is not None:
        prev.pat = prev.pat & b.pat
    prev.sets.update(b.sets)
    prev.alpha = b.alpha or prev.alpha
    prev.stress = b.stress or prev.stress


def _split_top(s: str, sep: str = ",") -> list[str]:
    parts, depth, cur = [], 0, ""
    for c in s:
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        if c == sep and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += c
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def _expand_braces(s: str) -> list[str]:
    m = re.search(r"\{([^{}]*)\}", s)
    if not m:
        return [s]
    out = []
    for choice in _split_top(m.group(1)):
        out += _expand_braces(s[:m.start()] + choice + s[m.end():])
    return out


def _env_token(t: _Tok):
    if t.typ == "edge":
        return ("#",)
    if t.typ not in ("cls", "lit") or t.pat is None:
        raise ParseError(f"cannot use {t.text!r} in an environment")
    if t.stress:
        if t.star or t.opt:
            raise ParseError("stress condition on an optional context")
        return ("ps", t.pat, t.stress)
    if t.star:
        return ("star", t.pat)
    return ("opt", t.pat) if t.opt else ("p", t.pat)


def _parse_env(text: str):
    """-> (alts, stress, syll flags, alpha side or None). A stressed context segment (V́, [−stress]V) becomes an "ps"
    token; ``Env.ctx_stress`` is derived from the alts."""
    stress, syll, alpha = None, set(), None
    text = text.strip()
    if "open syllable" in text:
        syll.add("open")
        text = text.replace("open syllable", "")
    if "closed syllable" in text:
        syll.add("closed")
        text = text.replace("closed syllable", "")
    alts, prev_side = [], None
    raw_alts = _split_top(text)
    if not raw_alts:
        return (((), ()),), stress, frozenset(syll), alpha
    for a in raw_alts:
        if "_" not in a:
            only = _tokens(a)
            if all(t.typ == "flag" for t in only):
                for t in only:
                    stress = t.stress or stress
                    if t.flag:
                        syll.add(t.flag)
                continue
            if prev_side == "right":
                a = "_" + a
            elif prev_side == "left":
                a = a + "_"
            else:
                raise ParseError(f"environment {a!r} has no _")
        for e in _expand_braces(a):
            if e.count("_") != 1:
                raise ParseError(f"environment {e!r} needs exactly one _")
            ls, rs = e.split("_")
            lt, rt = [], []
            for side, toks, dest in (("left", _tokens(ls), lt), ("right", _tokens(rs), rt)):
                for t in toks:
                    if t.typ == "flag":
                        stress = t.stress or stress
                        if t.flag:
                            syll.add(t.flag)
                        continue
                    if t.alpha:
                        alpha = side
                    dest.append(_env_token(t))
            alts.append((tuple(reversed(lt)), tuple(rt)))
            prev_side = "right" if rt and not lt else ("left" if lt and not rt else prev_side)
    if not alts:
        alts = [((), ())]
    return tuple(alts), stress, frozenset(syll), alpha


def _side_items(s: str) -> list[str]:
    s = s.strip()
    if "," in s:
        return _split_top(s)
    parts = _split_top(re.sub(r"\s+", " ", s), " ")
    return parts if len(parts) > 1 else [s]


def _merge_gem(toks: list[_Tok], other) -> list[_Tok]:
    """Two identical literal neighbours are one long segment (tt -> tː). Two identical class letters are one long segment
    only against a single one on the other side (C > CC, CC > C); CCC > CC stays a cluster rule."""
    other = list(other)
    out: list[_Tok] = []
    for t in toks:
        if out and t.typ in ("lit", "cls") and out[-1].typ == t.typ and out[-1].text == t.text \
                and not out[-1].sets.get("length") and not t.opt and not t.star:
            if t.typ == "cls" and not (len(toks) == 2 and len(other) == 1 and other[0].text == t.text):
                out.append(t)
                continue
            prev = out[-1]
            prev.sets = dict(prev.sets, length=1)
            if prev.typ == "lit":
                prev.seg = replace(prev.seg, length=1)
                prev.pat = lit(prev.seg)
            else:
                prev.pat = prev.pat & cls("ː", None, "long", length=1)
            prev.text += t.text
            continue
        out.append(t)
    return out


def _out_items(ins: list[_Tok], outs: list[_Tok]):
    texts = {t.text for t in ins} | {t.text for t in outs}
    if len(texts) == 1 and ins[0].typ == "cls" and len(outs) < len(ins):  # CCC > CC: the middle goes
        refs = list(range(len(outs) - 1)) + [len(ins) - 1]
        return tuple((j, None, ()) for j in refs)
    items, used = [], set()
    for pos, o in enumerate(outs):
        if o.typ not in ("lit", "cls"):
            raise ParseError(f"cannot produce {o.text!r}")
        if "__unsettable__" in o.sets:
            raise ParseError(f"cannot set {o.sets['__unsettable__']}")
        j = next((j for j, t in enumerate(ins) if j not in used and t.base and t.base == o.base), None)
        if j is None:
            j = next((j for j, t in enumerate(ins) if t.base and t.base == o.base), None)
        if j is not None:
            used.add(j)
            sets = {}
            if o.typ == "lit":
                sets = _diff(ins[j], o.seg)
            else:
                for ax in ins[j].sets:
                    if ax != "__unsettable__":
                        sets[ax] = 0
                sets.update(o.sets)
            items.append((j, None, tuple(sets.items())))
            continue
        if o.typ == "lit":
            jpos = pos if pos < len(ins) and pos not in used else None
            if jpos is not None and len(outs) == len(ins) and _kind_of(ins[jpos]) == o.seg.kind:
                used.add(jpos)
                items.append((jpos, None, tuple(_diff(ins[jpos], o.seg).items())))
            elif len(ins) == 1 and len(outs) > 1 and 0 not in used and _kind_of(ins[0]) == o.seg.kind:
                used.add(0)
                items.append((0, None, tuple(_diff(ins[0], o.seg).items())))
            else:
                items.append((-1, o.seg, ()))
            continue
        # a bare feature bundle ([−voice]) or another class letter (T > D) on the positional input
        if o.base:
            if o.base not in CLASS_SETS:
                raise ParseError(f"cannot produce the class {o.text!r}")
            o = replace(o, sets={**CLASS_SETS[o.base], **o.sets})
        jpos = pos if pos < len(ins) else None
        if jpos is None:
            raise ParseError(f"no input for {o.text!r}")
        used.add(jpos)
        items.append((jpos, None, tuple(o.sets.items())))
    return tuple(items)


def _kind_of(t: _Tok):
    if t.typ == "lit":
        return t.seg.kind
    return {"V": "V"}.get(t.base, "C" if t.base else None)


def _diff(intok: _Tok, out_seg) -> dict:
    """Axes to set so the input becomes the output literal."""
    if intok.typ == "lit":
        from dataclasses import fields as _f

        return {f.name: getattr(out_seg, f.name) for f in _f(out_seg)
                if f.init and f.name not in ("kind", "tone") and getattr(out_seg, f.name) != getattr(intok.seg, f.name)}
    axes = _V_QUALITY + ("nasal",) if out_seg.kind == "V" else _C_QUALITY
    d = {a: getattr(out_seg, a) for a in axes}
    if out_seg.length:
        d["length"] = 1
    return d


def parse_rule(line_or_row, **meta) -> tuple[Rule | None, str]:
    """Parse one rule. Accepts a notation string, a tsv row dict (id, family, rule, cause, articulators_or_axes_needed,
    naturalness, example) or a list in that column order. Returns (Rule, "") or (None, reason); never raises."""
    try:
        return _parse(line_or_row, **meta), ""
    except ParseError as e:
        return None, str(e)
    except Exception as e:  # noqa: BLE001 - the contract is "report, don't raise"
        return None, f"{type(e).__name__}: {e}"


_COLS = ("id", "family", "rule", "cause", "articulators_or_axes_needed", "naturalness", "example")


def _strip_comments(text: str) -> str:
    """Drop parenthesized comments: text with a space or a word in it ("(C)" stays)."""
    return re.sub(r"\(([^()]*)\)", lambda m: "" if (" " in m.group(1) or re.search(r"[A-Za-z]{3,}", m.group(1)))
                  else m.group(0), text)


def _parse(src, **meta) -> Rule:
    if isinstance(src, str):
        row = {"rule": src}
    elif isinstance(src, dict):
        row = dict(src)
    else:
        row = dict(zip(_COLS, src))
    row.update(meta)
    text = unicodedata.normalize("NFD", (row.get("rule") or "").strip())
    rid = row.get("id") or text
    bare = _strip_comments(text)
    if re.search(r"\bthen\b", bare):  # a staged change: "step ; step ; then step", each run on the last one's output
        steps = [p.strip() for p in re.split(r";|\bthen\b", bare) if p.strip()]
        if len(steps) < 2:
            raise ParseError("a staged change with one step")
        parsed = [_parse(dict(row, id=f"{rid}~{k + 1}", rule=st)) for k, st in enumerate(steps)]
        return replace(parsed[0], id=rid, then=tuple(parsed[1:]), notation=(row.get("rule") or "").strip())
    for marker, why in _BLOCK:
        if (re.search(rf"\b{marker}\b", text) if marker.isalpha() else marker in text):
            raise ParseError(why)
    lengthen = bool(_LENGTHEN.search(text))
    notes = []
    text = _strip_comments(text)
    text = _LENGTHEN.sub("", re.sub(r"\bwith\b", "", text)).strip()
    m = re.split(r"\s/\s", text, maxsplit=1)
    main, envtxt = (m[0], m[1]) if len(m) == 2 else (m[0], "")
    if "/" in main:
        raise ParseError("alternative outputs (a/b)")
    parts = [p.strip() for p in main.split(">")]
    if len(parts) < 2:
        raise ParseError("no '>'")
    if len(parts) > 2:
        if any("," in p for p in parts[1:-1]) and "," not in parts[0]:
            raise ParseError("several rules in one row")
        # a chain "a > b > c" is staged: a > b, then b > c (feeding: a ends as c, and an old b goes with it); every step
        # takes the environment. A chain that must not merge is written in drag order by hand ("b > c ; then a > b").
        env = f" / {envtxt}" if envtxt.strip() else ""
        steps = [_parse(dict(row, id=f"{rid}~{k + 1}", rule=f"{a} > {b}{env}"))
                 for k, (a, b) in enumerate(zip(parts, parts[1:]))]
        return replace(steps[0], id=rid, then=tuple(steps[1:]), notation=(row.get("rule") or "").strip())
    lhs, rhs = parts[0], parts[1]
    if not lhs or not rhs:
        raise ParseError("empty side")
    if ">" in envtxt:
        raise ParseError("several rules in one row")
    for phrase, flag in (("open syllable", "[open]"), ("closed syllable", "[closed]")):
        envtxt = envtxt.replace(phrase, flag)
    if re.search(r"[a-z]{3,}", re.sub(r"\[[^\]]*\]", "", " ".join((lhs, rhs, envtxt)))):
        raise ParseError("free text in the rule")
    in_items, out_items = _side_items(lhs), _side_items(rhs)
    alts, stress, syll, alpha = _parse_env(envtxt)

    in_toks = [_tokens(x) for x in in_items]
    out_toks = [_tokens(x) for x in out_items]
    if len(in_toks) > 1 and any(len(t) > 1 for t in in_toks):  # parallel clusters ("pl, kl > pj, kj"): one step each
        return _parallel_clusters(row, rid, in_items, out_items, envtxt, notes)
    if len(in_toks) == len(out_toks) == 1:
        in_toks, out_toks = [_merge_gem(in_toks[0], out_toks[0])], [_merge_gem(out_toks[0], in_toks[0])]
    else:
        in_toks = [_merge_gem(t, ()) for t in in_toks]
        out_toks = [_merge_gem(t, ()) for t in out_toks]
    for toks in in_toks:  # stress / flags attached to the input token (V[−stress], V́)
        for t in toks:
            if t.stress:
                stress = stress or t.stress
            if t.typ == "flag" and t.flag:
                syll = syll | {t.flag}
    in_toks = [[t for t in toks if t.typ != "flag"] for toks in in_toks]
    if stress and not all(_kind_of(t[0]) == "V" for t in in_toks if t):
        stress_on_vowel = all(t and t[0].typ == "null" for t in in_toks)
        if not stress_on_vowel:
            raise ParseError("stress condition on a consonant")
    if len(in_toks) > 1 and len(out_toks) == 1:  # "χ, x > h": every input to the one output
        out_toks = [[replace(t, sets=dict(t.sets)) for t in out_toks[0]] for _ in in_toks]
    if len(in_toks) == 1 and len(out_toks) > 1:
        notes.append("first of several outputs")
        out_toks = out_toks[:1]
    if len(in_toks) != len(out_toks):
        raise ParseError("input and output lists differ in length")

    ctx = any(t[0] == "ps" for alt in alts for side in alt for t in side)
    env = Env(alts=alts, stress=stress, syll=syll, ctx_stress=ctx)
    focus_kind = _kind_of(in_toks[0][0]) if in_toks and in_toks[0] else None
    left_set = (("length", 1),) if lengthen and focus_kind == "C" else ()
    target, span = None, ()
    if len(in_toks) == 1:
        ins, outs = in_toks[0], out_toks[0]
        if any(t.typ in ("edge",) or t.opt or t.star for t in ins):
            raise ParseError("edge or optional element in the input")
        if len(ins) == 1 and ins[0].typ == "null":  # insertion
            if len(outs) != 1:
                raise ParseError("insertion of several segments")
            o = outs[0]
            if o.typ == "lit":
                seg = o.seg
            elif o.base == "V" and not o.sets:
                seg = from_ipa(EPENTHETIC)[0]
                notes.append(f"class V inserted as {EPENTHETIC}")
            else:
                raise ParseError(f"cannot insert {o.text!r}")
            change = Change.insert(seg)
        else:
            if any(t.typ != "cls" and t.typ != "lit" for t in ins):
                raise ParseError("odd input")
            target, span = ins[0].pat, tuple(t.pat for t in ins[1:])
            if len(outs) == 1 and outs[0].typ == "null":
                change = Change("delete", items=(), left_set=left_set)
            elif len(outs) == 1 and outs[0].alpha:
                if alpha is None or len(ins) != 1:
                    raise ParseError("agreement without a source")
                change = Change("assimilate", axes=ALPHA_AXES[outs[0].alpha], source=alpha)
            else:
                items = _out_items(ins, outs)
                kind = "set" if len(ins) == 1 and len(items) == 1 and items[0][0] == 0 else \
                    "split" if len(ins) == 1 and len(items) == 2 else \
                    "metathesis" if len(ins) == 2 and [x[0] for x in items] == [1, 0] else "rewrite"
                if any(t.typ == "lit" for t in outs) and all(t.typ == "lit" for t in ins):
                    out_text = out_items[0].strip()
                elif len(outs) == 1 and outs[0].base in CLASS_SETS and outs[0].base != ins[0].base and not outs[0].sets:
                    out_text = CLASSES[outs[0].base].words
                else:
                    out_text = ""
                change = Change(kind, items=items, left_set=left_set, out_text=out_text)
    else:  # parallel lists: map
        pairs, pats = [], []
        for ins, outs in zip(in_toks, out_toks):
            if len(ins) != 1 or ins[0].typ != "lit":
                raise ParseError("parallel lists need single literal inputs")
            if len(outs) == 1 and outs[0].typ == "null":
                items = ()
            else:
                items = _out_items(ins, outs)
            pairs.append((_tonekey(ins[0].seg), items))
            pats.append(ins[0].pat)
        keys = frozenset(p.seg for p in pats)
        target = Pattern(",".join(p.label for p in pats), ("keys", keys),
                         " or ".join(p.words for p in pats))
        change = Change("map", pairs=tuple(pairs), left_set=left_set)

    cause = (row.get("cause") or "effort").strip()
    if cause not in CAUSES:
        raise ParseError(f"unknown cause {cause!r}")
    needs = set()
    for x in (row.get("articulators_or_axes_needed") or row.get("needs") or "").replace(";", ",").split(","):
        x = _need(x)
        if x:
            needs.add(x)
    weight = float(row.get("naturalness") or row.get("weight") or 3)
    family = (row.get("family") or "").strip()
    scope = row.get("scope") or ("diffusing" if family in DIFFUSING_FAMILIES else "regular")
    return Rule(id=rid, target=target, change=change, env=env, cause=cause, needs=frozenset(needs), weight=weight,
                scope=scope, example=(row.get("example") or "").strip(), span=span, family=family,
                notation=(row.get("rule") or "").strip() + (f"  [{'; '.join(notes)}]" if notes else ""))


def _parallel_clusters(row: dict, rid: str, in_items: list, out_items: list, envtxt: str, notes: list) -> Rule:
    """A parallel list whose inputs are clusters ("pl, kl, fl > pj, kj, fj"; "ps, pt > s, t / #_") as one staged rule, a
    step per pair in the written order. That equals the parallel change only when no step's output holds a later step's
    input (no feeding), so such a row is refused."""
    if len(out_items) == 1:
        out_items = out_items * len(in_items)
    if len(out_items) != len(in_items):
        raise ParseError("input and output lists differ in length")
    for k, inp in enumerate(in_items):
        if any(inp.strip() in o for o in out_items[:k]):
            raise ParseError("parallel clusters that feed each other")
    env = f" / {envtxt}" if envtxt.strip() else ""
    parsed = [_parse(dict(row, id=f"{rid}~{k + 1}", rule=f"{i} > {o}{env}")) for k, (i, o) in
              enumerate(zip(in_items, out_items))]
    note = f"  [{'; '.join(notes)}]" if notes else ""
    return replace(parsed[0], id=rid, then=tuple(parsed[1:]), notation=(row.get("rule") or "").strip() + note)


# Lexical diffusion is the minority: metathesis and dissimilation spread word by word in the record (Wang 1969; Hock
# 1991 ch. 9: Latin peregrinus > pellegrino and arborem > árbol, but most r...r and n...n words kept both). A diffusing
# change reaches about DIFFUSE_REACH of the words it fits (lect.Lect._apply_rule; PW-1686). Until PW-1686 the scope was
# set but never read, so a dissimilation ran as a regular law: n > l before a later nasal (S094) and r > l before a later
# r (S091) turned every such word, and were a third of the l- that made l the commonest word start on a24559. (The rare
# rows, weight 1, were diffusing by default too; their examples are regular laws, Hawaiian t > k and k > ʔ, uvular r, so
# they stay regular.)
DIFFUSING_FAMILIES = frozenset({"metathesis", "dissimilation"})
DIFFUSE_REACH = 0.3


# ----------------------------------------------------------------------------------------------------------- describe

def _tok_words(t) -> str:
    if t[0] == "#":
        return "#"
    w = t[1].words or t[1].label
    if t[0] == "ps":
        return _join_words(t[2], w)
    return f"optionally {w}" if t[0] == "opt" else (f"any number of {w}" if t[0] == "star" else w)


def _env_words(env: Env) -> str:
    bits = []
    for left_rev, right in env.alts:
        left = list(reversed(left_rev))
        far_l = any(t[0] == "star" and t[1].label == "X" for t in left)  # X*: anywhere earlier / later in the word
        far_r = any(t[0] == "star" and t[1].label == "X" for t in right)
        lw = [_tok_words(t) for t in left if not (t[0] == "star" and t[1].label == "X")]
        rw = [_tok_words(t) for t in right if not (t[0] == "star" and t[1].label == "X")]
        if far_l or far_r:
            part = []
            if lw:
                part.append("after " + " + ".join(x for x in lw if x != "#") + (" earlier in the word" if far_l else ""))
            if rw:
                part.append("before " + " + ".join(x for x in rw if x != "#") + (" later in the word" if far_r else ""))
            bits.append(" and ".join(part))
            continue
        if lw == ["a vowel"] and rw == ["a vowel"]:
            bits.append("between vowels")
            continue
        if lw in (["a consonant"], ["#", "a consonant"]) and rw in (["a consonant"], ["a consonant", "#"]):
            rest = rw[1:]
            bits.append(" + ".join(lw[:-1] + ["between consonants"] + rest).replace("# + ", "word-initially ")
                        .replace(" + #", " at the end of a word"))
            continue
        part = []
        if lw:
            part.append("at the start of a word" if lw == ["#"] else "after " + " + ".join(x for x in lw if x != "#")
                        + (" at the start of a word" if "#" in lw else ""))
        if rw:
            part.append("at the end of a word" if rw == ["#"] else "before " + " + ".join(x for x in rw if x != "#")
                        + (" at the end of a word" if "#" in rw else ""))
        if part:
            bits.append(" and ".join(part))
    s = " or ".join(bits)
    extra = []
    if env.stress:
        extra.append(f"in {env.stress} syllables")
    for f in sorted(env.syll):
        extra.append({"coda": "at the end of a syllable", "onset": "before a vowel", "final": "in the last syllable",
                      "nonfinal": "outside the last syllable", "open": "in open syllables",
                      "closed": "in closed syllables"}[f])
    return " ".join(x for x in [s] + extra if x)


_TONE_WORDS = {1: "low", 2: "mid", 3: "high", 4: "rising", 5: "falling", 6: "extra-high", 7: "extra-low"}


def describe(rule: Rule) -> str:
    """Plain words for the workbench: 'p became f between vowels (effort: lenition)'. A class rule names what it does to
    real segments ('..., e.g. p > b, t > d'); a staged rule lists its steps."""
    fam = rule.family or rule.id.split(".")[0]
    steps = "; then ".join(_describe_step(r) for r in (replace(rule, then=()),) + tuple(rule.then))
    return f"{steps} ({rule.cause}: {fam})"


def _examples(rule: Rule, k: int = 3) -> list[str]:
    """Up to k 'x > y' pairs over common segments the rule's target covers (context ignored)."""
    out = []
    for seg in _protos():
        o = _single(rule, seg)
        if o is None or tuple(o) == (seg,):
            continue
        out.append(f"{to_ipa(seg)} > {''.join(to_ipa(x) for x in o) or '∅'}")
        if len(out) == k:
            break
    return out


def _describe_step(rule: Rule) -> str:
    ch = rule.change
    tw = rule.target.words if rule.target is not None else ""
    if rule.span:
        tw = tw + " + " + " + ".join(p.words or p.label for p in rule.span)
    where = _env_words(rule.env)
    after = ""
    eg = []
    if ch.kind == "insert":
        what = f"{to_ipa(ch.items[0][1])} was inserted"
    elif ch.kind == "delete":
        what = f"{tw} was lost"
    elif ch.kind == "assimilate":
        src = {"right": "the next sound", "left": "the sound before", "prev_vowel": "the vowel before",
               "first_vowel": "the root's first vowel"}[ch.source]
        what = f"{tw} took the {'/'.join(ch.axes)} of {src}"
    elif ch.kind == "map":
        pairs = []
        for inp, items in ch.pairs:
            outs = _make(items, (inp,), inp) if items else []
            pairs.append(f"{to_ipa(inp)} > {''.join(to_ipa(o) for o in outs) or '∅'}")
        what = ", ".join(pairs)
    elif ch.kind == "metathesis":
        what = f"{tw} swapped places"
    else:
        res = ch.out_text or _describe_items(rule)
        what = f"{tw} changed" if res == "a new quality" else f"{tw} became {res}"
        if rule.target is not None and rule.target.seg is None and not rule.span:
            eg = _examples(rule)
    for ax, v in ch.left_set:
        if ax == "length":
            after = ", lengthening the vowel before"
        elif ax == "tone":
            after = f", leaving a {_TONE_WORDS.get(v, str(v))} tone on the vowel before"
    return f"{what}{' ' + where if where else ''}{after}{', e.g. ' + ', '.join(eg) if eg else ''}"


def _describe_items(rule: Rule) -> str:
    ch = rule.change
    seg = rule.target.seg if rule.target is not None else None
    if seg is not None and not rule.span:
        return "".join(to_ipa(o) for o in _make(ch.items, (seg,), seg))
    bits = []
    for ref, literal, sets in ch.items:
        if literal is not None:
            bits.append(to_ipa(literal))
        elif ref >= 0 and not sets:
            pats = (rule.target,) + rule.span
            bits.append(pats[ref].words or pats[ref].label)
        elif sets:
            bits.append(_sets_words(sets))
        else:
            bits.append("itself")
    return " + ".join(bits) or "nothing"


_SET_WORDS = {("voice", 1): "voiced", ("voice", 0): "voiceless", ("back", 0): "front", ("back", 4): "back",
              ("nasal", 1): "nasal", ("nasal", 0): "oral", ("length", 1): "long", ("length", 0): "short",
              ("round", 1): "rounded", ("round", 0): "unrounded", ("height", 6): "high", ("larynx", 2): "ejective",
              ("larynx", 3): "implosive", ("larynx", 1): "aspirated", ("phonation", 1): "breathy",
              ("phonation", 0): "modal-voiced", ("larynx", 0): "unaspirated",
              ("secondary", 1): "labialized", ("secondary", 2): "palatalized", ("prenasal", 1): "prenasalized",
              **{("tone", t): f"{w}-toned" for t, w in _TONE_WORDS.items()},
              ("source2", 1): "second-voiced", ("source2", 0): "one-voiced", ("tone2", 0): "with its second voice in parallel",
              **{("tone2", t): f"with a {w} second voice" for t, w in _TONE_WORDS.items()}}


def _sets_words(sets) -> str:
    if len(sets) > 3:
        return "a new quality"
    return " ".join(_SET_WORDS.get((a, v), f"{a} {v}") for a, v in sets)


# ---------------------------------------------------------------------------------------------------------- the demo set

def _demo(rid, notation, cause, needs, weight, example, scope="regular", **override) -> Rule:
    fam = rid.split(".")[0]
    if notation:
        r, why = parse_rule({"id": rid, "rule": notation, "cause": cause, "articulators_or_axes_needed": needs,
                             "naturalness": weight, "example": example, "family": fam, "scope": scope})
        if r is None:
            raise RuntimeError(f"demo rule {rid}: {why}")
        return replace(r, **override) if override else r
    return Rule(id=rid, cause=cause, needs=frozenset(n for n in map(_need, needs.split(",")) if n), weight=weight,
                example=example, scope=scope, family=fam, notation=override.pop("text", ""), **override)


_AFTER_V_CODA = Env(alts=(((("p", V),), ()),), syll=frozenset({"coda"}))


def _build_demo() -> tuple[Rule, ...]:
    return (
        # lenition chain p > f > h > 0, one link per rule
        _demo("lenition.p_f", "p > f / #_, V_", "effort", "lips", 3,
              "Grimm's law: Latin pater, English father (but spuere, spew: kept after s and other obstruents)"),
        _demo("lenition.f_h", "f > h / #_, V_V", "effort", "larynx", 3, "Latin facere > Old Spanish hazer > hacer"),
        _demo("lenition.h_loss", "h > ∅", "effort", "larynx", 5, "Spanish hacer [aθer]; Cockney 'ouse"),
        _demo("lenition.intervocalic_voicing", "[−voice −son −glottal +pulmonic] > [+voice] / V_V", "coarticulation", "larynx", 5,
              "Latin vitam > Spanish vida"),
        _demo("lenition.spirantization", "b, d, g > β, ð, ɣ / V_V", "effort", "lips, tongue_tip, tongue_body", 5,
              "Spanish lobo [loβo], nada [naða], lago [laɣo]"),
        _demo("devoicing.final", "[−son +pulmonic] > [−voice] / _#", "effort", "larynx", 5, "German Rad [ʁaːt] 'wheel'"),
        _demo("deletion.final_vowel", "V > ∅ / C_# [−stress]", "prosody", "stress", 4,
              "Latin lupum > Old French lou; Old English sunu > son"),
        _demo("reduction.unstressed_schwa", "V[−stress] > ə", "prosody", "tongue_body, stress", 4,
              "English photograph [ˈfoʊtəɡɹæf] vs photography [fəˈtɑɡɹəfi]"),
        _demo("reduction.syncope", "V[−stress] > ∅ / VC_CV", "prosody", "stress", 3,
              "Latin calidus > caldus > Italian caldo", "diffusing"),
        _demo("assimilation.nasal_place", "N > [αplace] / _C[αplace −glottal −pharyngeal]", "coarticulation", "velum", 5,
              "Latin in + possibilis > impossibilis"),
        _demo("palatalization.k_front", "k > tʃ / _[+front V]", "coarticulation", "tongue_body, tongue_tip", 5,
              "Old English cirice > church"),
        _demo("nasal.vowel_nasalization", "V > Ṽ / _N", "coarticulation", "velum", 5, "French bon [bɔ̃] < Latin bonum"),
        _demo("nasal.nasal_loss", "N > ∅ / Ṽ_[coda]", "effort", "velum", 4, "French vin [vɛ̃], the n gone"),
        _demo("debuccalization.s_h", "s > h / _C, _#", "effort", "tongue_tip, larynx", 5,
              "Andalusian Spanish los perros [loh pero]"),
        _demo("dental.theta_f", "θ > f", "perception", "tongue_tip, lips", 3, "Cockney think [fɪŋk]"),
        _demo("cluster.simplification", "CCC > CC", "effort", "timing", 3, "English Christmas [ˈkɹɪsməs] (t lost)",
              "diffusing"),
        _demo("harmony.back", "", "coarticulation", "tongue_body", 2,
              "Turkish ev-ler 'houses' vs at-lar 'horses' (suffix vowels agree in backness with the root)",
              target=V, change=Change("assimilate", axes=("back", "round"), source="first_vowel"),
              text="V > [αback] of the root's first vowel; [αround] for a high vowel; going back, e and ɛ open to ɑ (-ler/-lar) "
                   "and o keeps its rounding; going front, a non-high vowel only unrounds; ə and ɐ are neutral"),
        _demo("umlaut.i", "V[+back] > [−back] / _C(C)i", "coarticulation", "tongue_body", 4,
              "Proto-Germanic *mūsiz > Old English mȳs > mice"),
        _demo("rhotic.rhotacism", "s > r / V_V", "coarticulation", "tongue_tip", 3,
              "Old Latin honosis > honoris; flos, floris"),
        # tonogenesis, the two attested pathways: (i) register from onset voicing (Middle Chinese yin/yang, Tibetan,
        # Kammu): vowels after voiced obstruents go low, after voiceless ones high, then the voicing contrast is lost;
        # (ii) coda type (Vietnamese, Haudricourt 1954): final -ʔ leaves a rising tone (sắc/nặng), final -h < -s a
        # falling one (hỏi/ngã), and the coda goes.
        _demo("tone.onset_voicing_split",
              "V > V˨ / [+voice −son]_ ; V > V˦ / [−voice −son]_ ; then [+voice −son +pulmonic] > [−voice] / _V",
              "tonogenesis", "larynx, pitch_ear", 3,
              "Middle Chinese yin/yang split: voiced onsets gave the low register, voiceless the high, then devoiced"),
        _demo("tone.glottal_coda_rising", "", "tonogenesis", "larynx, pitch_ear", 3,
              "Vietnamese sắc/nặng tones from a lost final glottal stop (Haudricourt 1954)",
              target=lit(from_ipa("ʔ")[0]), change=Change.delete(tone=4), env=_AFTER_V_CODA,
              text="ʔ > ∅ / V_ [coda], vowel takes rising tone"),
        _demo("tone.h_coda_falling", "", "tonogenesis", "larynx, pitch_ear", 3,
              "Vietnamese hỏi/ngã tones from a lost final *-h < *-s (Haudricourt 1954)",
              target=lit(from_ipa("h")[0]), change=Change.delete(tone=5), env=_AFTER_V_CODA,
              text="h > ∅ / V_ [coda], vowel takes falling tone"),
        # second-voice tone (syrinx lane, 2026-11-08; docs/review/language/syrinx.md): the coda pathways again, the lost
        # consonant's pitch perturbation landing on the second voice; a phrase-final rise frozen onto it; and the ways
        # out: contours level, the low tone merges into parallel motion, all of it merges into parallel motion, and the
        # second voice itself is lost. Only syrinx-voiced peoples that hear the second voice's pitch have them.
        _demo("tone2.glottal_coda_rising", "[V source2=1 tone2=0]ʔ > Vᴖ˨˦ / _{C, #}", "tonogenesis",
              "syrinx, hear:tone2", 3, "after Vietnamese sắc/nặng from a lost final glottal stop (Haudricourt 1954), "
              "the rise taken up by the second voice (fantasy analogue)", family="tone"),
        _demo("tone2.h_coda_falling", "[V source2=1 tone2=0]h > Vᴖ˦˨ / _{C, #}", "tonogenesis",
              "syrinx, hear:tone2", 3, "after Vietnamese hỏi/ngã from a lost final *-h (Haudricourt 1954), the fall "
              "taken up by the second voice (fantasy analogue)", family="tone"),
        _demo("tone2.final_rise", "[V source2=1 tone2=0] > Vᴖ˨˦ / _C*#", "prosody", "syrinx, hear:tone2", 1,
              "a phrase-final rise frozen onto the second voice of the last syllable, as Swedish accent 2 grew out of "
              "word prosody (fantasy analogue)", family="tone"),
        # (weight 1, not S227's 3: the duration argument for levelling short contours (Zhang 2002) is weaker for a voice
        # that sweeps an octave in tens of milliseconds, as a syrinx does; at 2 it was the commonest second-voice change
        # of pass B, 18 firings, and the drawn contour sets levelled to all-high and were stripped)
        _demo("tone2.contour_level", "[V source2=1 tone2=4..5] > [tone2=3]", "perception", "syrinx, hear:tone2", 1,
              "as S227/S228 for the first voice: a contour simplifies to its high end (Yip 2002, ch. 2)", family="tone"),
        _demo("tone2.low_parallel", "Vᴖ˨ > [tone2=0]", "perception", "syrinx, hear:tone2", 2,
              "a category merger (as S230): the low second voice falls in with parallel motion", family="tone"),
        _demo("tone2.parallel", "[V source2=1 tone2=1..7] > [tone2=0]", "perception", "syrinx, hear:tone2", 1,
              "the second voice stops moving on its own and follows the first again (a whole tier lost, as Swahili "
              "lost Proto-Bantu tone)", family="tone"),
        # (unstressed syllables only, word by word: as written first, for every second-voice vowel at once, it fired in
        # 23 aarakocra and kenku lines of pass A and left one living lect of 52 with a second voice; 22 kept it before)
        _demo("voice2.loss", "[V source2=1 −stress] > [source2=0 tone2=0]", "effort", "syrinx", 1,
              "the two voices merge onto one in weak syllables first, word by word, as reduction spreads through the "
              "lexicon (Wang 1969 on lexical diffusion)", "diffusing"),
        _demo("chain_shift.raise_mid", "e, o > i, u / [+stress]", "dispersion", "tongue_body", 2,
              "Great Vowel Shift: Middle English feet [feːt] > [fiːt]"),
        _demo("metathesis.cc", "sk > ks", "perception", "tongue_tip, tongue_body", 2, "Old English ascian > dialectal ax",
              "diffusing"),
        _demo("epenthesis.cluster", "∅ > ə / C_C#, #C_C", "perception", "", 3,
              "Latin pōclum > pōculum 'cup'; Irish English film [ˈfɪləm]; Iraqi Arabic kalb > kalib (anaptyxis)"),
        _demo("labial.w_v", "w > v", "perception", "lips, teeth", 3, "Latin vinum [w] > Italian vino [v]"),
        _demo("rhotic.l_vocalization", "l > w / _C, _#", "effort", "tongue_tip, tongue_body", 3,
              "Old French chevals > chevaus; London milk [mɪwk]"),
        _demo("debuccalization.uvular", "q > ʔ", "effort", "tongue_body, larynx", 3,
              "Cairene Arabic qalb > ʔalb 'heart'"),
        _demo("debuccalization.uvular_pharyngeal", "χ > ħ", "perception", "pharynx", 2,
              "Some Semitic and Caucasian lects: χ > ħ"),
    )


DEMO_RULES: tuple[Rule, ...] = _build_demo()
DEMO_IDS = frozenset(r.id for r in DEMO_RULES)
