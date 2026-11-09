"""Grammar: typology features and grams on the grammaticalization ladder (architecture.md section 7).

Two layers.

1. **Typology** (`Typology`, a dict feature -> value): ~40 Grambank/WALS-style features drawn in a fixed order, each
   conditional on what was drawn before (WALS cross-tabulations on basic order for the Dryer harmonies; Grambank pairwise
   lifts for the rest). Features drift at a rate set by their stability class, and a flip re-draws the feature conditional on
   everything else (so a word-order flip pulls the harmonic orders after it over time). Typology features are the speech
   community's *propensities* (which categories it likes to mark, where modifiers go); what is actually marked, and how
   tightly, lives in layer 2 and is measured from it.

2. **Grams** (`Gram`): real markers with forms, recruited from lexical words along Heine & Kuteva paths, moving down the
   ladder free word (0) -> clitic (1) -> affix (2) -> fused (3) -> lost (4). From level 2 a gram is written into the
   paradigm exemplars' cells (`Exemplar.cells`), and every sound change runs over those inflected forms as well as over the
   stems and the gram forms (`apply_rule_to_grammar`), so alternations arise by themselves; analogy rebuilds some cells.

Complexity is never stored: population, adult-L2 share and isolation push on the recruit, fusion, loss and analogy hazards
in `step`, and `complexity(g)` measures what came out.

Everything is deterministic given the numpy Generator passed in. Segments are duck-typed: anything with a `kind` attribute
("C" | "V" | "T") works; percepts.Segment is the real one.
"""

from __future__ import annotations

import copy as _copy
import csv
import dataclasses
import math
import zlib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np

DATA = Path(__file__).parent / "data"

LEVELS = ("free word", "clitic", "affix", "fused", "lost")
FREE, CLITIC, AFFIX, FUSED, LOST = range(5)

Form = tuple  # tuple[Segment, ...]

# --------------------------------------------------------------------------------------------------------------------
# Hazards (per generation). Chosen by hand; see the module report for the reasoning. Calibrate against checks, not taste.
# --------------------------------------------------------------------------------------------------------------------

RECRUIT = 0.025        # new periphrasis per generation, before social factors (~1 per 40 gens ~ 1.1 kyr at 25 yr). Raised
                       # from 0.015 after run a24559 (median 2 live grams): over 700 generations with the driver's sound
                       # change, 30 human lects hold a median 5 live grams at l2 0.5 / 160k speakers, 7.5 at l2 0.3, 12 at
                       # l2 0.1 / 20k speakers
FUSE = 0.02            # one step down the ladder per generation for an average gram (~50 gens ~ 1.4 kyr per step).
                       # Synthesis lane (2026-11-08): raised from 0.012 with the L2 damping of fusion made linear and
                       # adult-learner stripping cubed (`social_factors`); 58% of living lects bound 0-1 verb categories
                       # against WALS 22A's ~3%, because grams were recruited but stayed free or were stripped in the
                       # median lect (adult-L2 proxy 0.54, 31% at the 0.7 ceiling). calibration.md "Synthesis lane"
FUSE_LEVEL = (1.0, 0.7, 0.06)   # multiplier for 0->1, 1->2, 2->3 (binding is fast; true fusion with the stem is slow)
PRE_FUSE = 0.1         # (PW-1571, owner ruling 11-08 "asym") the clitic > affix and affix > fused steps of a gram that
                       # stands before its host, x this. Preposed grammatical material is less often affixed than
                       # postposed material of the same function (Bybee, Pagliuca & Perkins 1990; Himmelmann 2014:
                       # word-initial material is more prominent and resists reduction; Hawkins & Cutler 1988 give the
                       # processing account: stems are recognised from their onsets). This is the source of the
                       # world's suffixing preference (WALS 26A, Dryer 2013: suffixing about 2.5 : 1 over prefixing);
                       # before it bound class markers in a24559 were prefixes 417 to suffixes 329 (calibration.md "Lane 4")
AGE_SCALE = 200.0      # generations; fusion hazard x (1 + age/AGE_SCALE), capped at AGE_CAP
AGE_CAP = 2.0
#: grammar phase D (task 4): the polar-question particle. Intonation-only questions were 51% of the full pass against
#: WALS 116A's ~14% (Dryer): the aims ask for a particle in ~58% of lects, but the pull was slow under adult learners
#: and a free particle was abandoned like any optional periphrasis. Question particles are among the most frequent and
#: stable function words (Dryer 2013; Mandarin ma, Japanese ka), so the aims' pull toward one is PULL_BOOST times the
#: ordinary PRESSURE and a wanted one is abandoned at KEEP times ABANDON. A far demonstrative is as stable (WALS 41A:
#: 3-way distance contrasts in ~37% of languages; the sim had 14% before KEEP and the 'very common' X64).
#: Graded pasts (recent, remote) keep at 0.4 (WALS 66A: ~30% of languages with a past grade it; the sim had 9%, now 20%).
PULL_BOOST = {"Q": 3.0}
KEEP = {"Q": 0.25, "DIST": 0.25, "RECPST": 0.4, "REMPST": 0.4}
ABANDON = 0.0005       # an optional periphrasis (level 0-1) falls out of use; x4 when the typology no longer wants it
                       # (0.002 abandoned 44% of new periphrases before they bound when L2 learners slow fusion; now ~16%)
LOSS = 0.002          # a fused gram (level 3) is lost outright
L2_STRIP = 0.008       # bound gram (level >= 2) dropped by adult learners, x l2_share^3 (was 0.012 x l2^2: at the
                       # proxy's 0.7 ceiling a bound gram then lived ~170 generations, so a third of lects shed every
                       # affix as fast as it formed for 20 kyr; real contact simplification is strongest where adult
                       # learners are the majority, Trudgill 2011, so the cube keeps it there: 0.0027/gen at 0.7, 0.001 at 0.5)
ANALOGY = 0.003        # one irregular cell levelled per generation (high-frequency exemplars: half-life ~ 230 gens)
CLASS_GROW = 0.5       # chance a fusing class marker recruits a further class
PRESSURE = 0.03        # per generation (x social recruit factor), for each category the aims mark and no live gram
                       # realises (number, case, past, ...): one recruitment restricted to that category's functions, so a
                       # typology flip toward marking pulls a gram onto the ladder. 40 human lects, 700 generations, l2 0.5:
                       # shown value = aim in ~80% of lects for number/past/future/progressive (55-65% at 0), median 10 live
                       # functions (6 at 0)
UNWANTED_LOSS = 0.002  # a bound gram (level >= 2) whose category the aims no longer mark erodes away, x social loss
DEGRAM = 1 / 50        # degrammaticalization (Norde 2009): a clitic or affix climbs one level back up at this share of
                       # the hazard of the step it undoes (English genitive -es > ='s, Irish -mid > muid 'we'); x
                       # DEGRAM_EDGE for phrase-edge markers (case, articles: host NP) and x DEGRAM_ORPHAN when the
                       # paradigm it belonged to is gone (it is the last bound marker of its slot, and an older one of
                       # that slot was lost), as the English genitive outlived the rest of the case endings
DEGRAM_EDGE = 3.0
DEGRAM_ORPHAN = 3.0
CHUNK = 10.0           # generations per internal sub-step
# Species leanings (owner ruling 11-08, PW-1538 C: all three rows of the grammar D lane's proposal). Each is one named
# multiplier table on existing hazards, chosen by the people's life history (generation length) or voice profile (pitch
# range), never by a species name; `leanings` combines them per lect and grammar.step reads the result. Flavour, not
# measurement: long memories keep witnessed-vs-reported marking (evidentials, mirative) and wear morphology more slowly;
# a voice with a wide pitch range copies sounds (reduplication); short generations recruit a little faster.
LONG_GEN_YR = 140.0    # generation length (yr) from which LEAN_LONG_GEN applies (elves at 144.9, giants, dragons at 430;
#                       150 -> 140, owner ruling 11-08 on PW-1538 C / PW-1544: elves get the leanings and the deep past)
LEAN_LONG_GEN = {"evid_recruit": 1.5, "evid_loss": 0.5, "fuse": 0.7, "erode": 0.7}
SHORT_GEN_YR = 20.0    # generation length (yr) under which LEAN_SHORT_GEN applies (humans 25-28 do not; kobolds at 15 do)
LEAN_SHORT_GEN = {"recruit": 1.2}
WIDE_PITCH = 3         # voice profile pitch_range (rough octaves of speaking pitch; human 1) from which LEAN_WIDE_PITCH applies
LEAN_WIDE_PITCH = {"redup": 1.5}
EVID_FNS = ("EVID.DIR", "EVID.REP", "MIR")


def leanings(gen_yr: float | None, pitch_range: float | None) -> dict[str, float]:
    """The lect's species leanings: the product of the LEAN_* tables that apply to its people's generation length and
    voice profile pitch range (an empty dict for most peoples)."""
    out: dict[str, float] = {}
    tabs = []
    if gen_yr is not None and gen_yr >= LONG_GEN_YR:
        tabs.append(LEAN_LONG_GEN)
    if gen_yr is not None and gen_yr < SHORT_GEN_YR:
        tabs.append(LEAN_SHORT_GEN)
    if pitch_range is not None and pitch_range >= WIDE_PITCH:
        tabs.append(LEAN_WIDE_PITCH)
    for t in tabs:
        for k, v in t.items():
            out[k] = out.get(k, 1.0) * v
    return out

PATH_FREQ_WEIGHT = {"very common": 3.0, "common": 2.0, "attested": 1.0, "set": 0.0}
# ('set': a path only a paradigm's set-binding uses (`_person_set`), never drawn on its own: the rest of an object or
# possessor series binds with its first member, so one lead path per series keeps the draw's other targets undiluted)

# --------------------------------------------------------------------------------------------------------------------
# Functions: host, which typology feature fixes the side a new gram stands on, frequency weight, paradigm slot, gloss
# --------------------------------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class FuncInfo:
    host: str          # N | V | NP | VP
    side_rule: str     # dem | num | adp | aux | head | neg | agr
    freq: float        # token frequency weight (fusion and merger priority)
    slot: str          # paradigm slot; also the affix order (SLOT_ORDER, inner first)
    gloss: str


FUNCS: dict[str, FuncInfo] = {
    "PL": FuncInfo("N", "num", 1.5, "number", "plural"),
    "DU": FuncInfo("N", "num", 0.7, "number", "dual"),
    "DEF": FuncInfo("NP", "dem", 1.3, "det", "definite"),
    "INDEF": FuncInfo("NP", "num", 1.0, "det", "indefinite"),
    "GEN": FuncInfo("NP", "adp", 1.0, "case", "genitive"),
    "LOC": FuncInfo("NP", "adp", 1.1, "case", "locative"),
    "ABL": FuncInfo("NP", "adp", 0.8, "case", "ablative"),
    "ALL": FuncInfo("NP", "adp", 0.8, "case", "allative"),
    "DAT": FuncInfo("NP", "adp", 0.9, "case", "dative"),
    "ACC": FuncInfo("NP", "adp", 1.2, "case", "accusative"),
    "ERG": FuncInfo("NP", "adp", 1.2, "case", "ergative"),
    "INS": FuncInfo("NP", "adp", 0.8, "case", "instrumental"),
    "COM": FuncInfo("NP", "adp", 0.7, "case", "comitative"),
    # PW-1569 (owner ruling 11-08 "grow"): the local-case series and three more peripheral cases, so Finnish-, Hungarian-
    # and Daghestanian-size systems can form. An 'inside' and an 'on top' region marker (from 'in, belly' and 'top,
    # head': Heine & Kuteva 2002 BELLY > IN, HEAD > ON) are the static cases; each joins the allative and ablative into
    # 'into, out of' and 'onto, off from' (`_local_series`: Finnish -ssa / -sta < *-s-na / *-s-ta, Hungarian -ban / -ból /
    # -ba, the Tsez and Lezgian series-plus-orientation suffixes; Comrie & Polinsky 1998, Creissels 2009).
    "INE": FuncInfo("NP", "adp", 0.8, "case", "inessive ('in, inside')"),
    "ILL": FuncInfo("NP", "adp", 0.6, "case", "illative ('into')"),
    "ELA": FuncInfo("NP", "adp", 0.6, "case", "elative ('out of')"),
    "SUPE": FuncInfo("NP", "adp", 0.6, "case", "superessive ('on, on top of')"),
    "SUBL": FuncInfo("NP", "adp", 0.5, "case", "sublative ('onto')"),
    "DEL": FuncInfo("NP", "adp", 0.5, "case", "delative ('off, down from')"),
    "PERL": FuncInfo("NP", "adp", 0.5, "case", "perlative ('through, along')"),
    "PRIV": FuncInfo("NP", "adp", 0.5, "case", "privative ('without')"),
    "TRANSL": FuncInfo("NP", "adp", 0.5, "case", "translative ('into, becoming')"),
    "DIM": FuncInfo("N", "head", 0.8, "deriv", "diminutive"),
    "AGENT": FuncInfo("N", "head", 0.7, "deriv", "one who / person of"),
    "PLACE": FuncInfo("N", "head", 0.7, "deriv", "place of"),
    "PAST": FuncInfo("V", "aux", 1.5, "tense", "past"),
    "RECPST": FuncInfo("V", "aux", 0.6, "tense", "recent past"),
    "FUT": FuncInfo("V", "aux", 1.2, "tense", "future"),
    "PERF": FuncInfo("V", "aux", 1.2, "aspect", "perfect"),
    "PROG": FuncInfo("V", "aux", 1.1, "aspect", "progressive"),
    "IPFV": FuncInfo("V", "aux", 1.1, "aspect", "imperfective"),
    "HAB": FuncInfo("V", "aux", 0.9, "aspect", "habitual"),
    "EVID.DIR": FuncInfo("VP", "aux", 0.6, "mood", "witnessed (evidential)"),
    "EVID.REP": FuncInfo("VP", "aux", 0.7, "mood", "reported (evidential)"),
    "NEG": FuncInfo("VP", "neg", 1.5, "polarity", "negative"),
    "CAUS": FuncInfo("V", "aux", 0.8, "valence", "causative"),
    "PASS": FuncInfo("V", "aux", 0.8, "valence", "passive"),
    "REFL": FuncInfo("V", "aux", 0.6, "valence", "reflexive"),
    "1SG": FuncInfo("V", "agr", 1.4, "person", "I (subject)"),
    "2SG": FuncInfo("V", "agr", 1.2, "person", "you (subject)"),
    "3SG": FuncInfo("V", "agr", 1.4, "person", "he/she/it (subject)"),
    "1PL": FuncInfo("V", "agr", 1.0, "person", "we (subject)"),
    "2PL": FuncInfo("V", "agr", 0.8, "person", "you all (subject)"),
    "3PL": FuncInfo("V", "agr", 1.0, "person", "they (subject)"),
    # grammar phase B (2026-11-08): the inclusive 'we' in the subject series; mood; object agreement; possessor marking
    "1PL.INCL": FuncInfo("V", "agr", 0.9, "person", "we, you included (subject)"),
    "IMP": FuncInfo("V", "aux", 1.0, "mood", "imperative"),
    "HORT": FuncInfo("V", "aux", 0.6, "mood", "hortative ('let us')"),
    "OBLG": FuncInfo("V", "aux", 0.7, "mood", "obligative ('must')"),
    "APPR": FuncInfo("VP", "aux", 0.4, "mood", "apprehensive ('lest')"),
    **{f"{p}.O": FuncInfo("V", "oagr", fr, "person", f"{g} (object)") for p, fr, g in (
        ("1SG", 1.0, "me"), ("2SG", 0.9, "you"), ("3SG", 1.1, "him/her/it"), ("1PL", 0.7, "us"), ("2PL", 0.6, "you all"),
        ("3PL", 0.8, "them"))},
    **{f"{p}.POSS": FuncInfo("N", "gen", fr, "poss", f"{g} (possessor)") for p, fr, g in (
        ("1SG", 1.1, "my"), ("2SG", 0.9, "your"), ("3SG", 1.1, "his/her/its"), ("1PL", 0.7, "our"),
        ("2PL", 0.6, "your (pl.)"), ("3PL", 0.8, "their"))},
    # grammar phase C (2026-11-08). Constructions as grams (item 10): the polar question particle, the copula, the
    # relativizer, the complementizer, topic and focus markers (slot 'clause', outermost). Valence (item 14):
    # applicative, reciprocal, antipassive. Switch-reference (item 17): same / different subject on a medial verb.
    # Symmetrical voice (item 19): actor and patient voice on the verb (Austronesian).
    "Q": FuncInfo("VP", "q", 0.9, "clause", "polar question"),
    "COP": FuncInfo("VP", "aux", 1.0, "clause", "copula"),
    "REL": FuncInfo("VP", "rel", 0.8, "clause", "relativizer"),
    "COMP": FuncInfo("VP", "comp", 0.7, "clause", "complementizer ('that')"),
    "TOP": FuncInfo("NP", "adp", 0.6, "clause", "topic"),
    "FOC": FuncInfo("NP", "adp", 0.6, "clause", "focus"),
    "APPL": FuncInfo("V", "aux", 0.7, "valence", "applicative"),
    "RECP": FuncInfo("V", "aux", 0.6, "valence", "reciprocal"),
    "ANTIP": FuncInfo("V", "aux", 0.6, "valence", "antipassive"),
    "SS": FuncInfo("V", "comp", 0.8, "clause", "same subject (switch-reference)"),
    "DS": FuncInfo("V", "comp", 0.8, "clause", "different subject (switch-reference)"),
    "AV": FuncInfo("V", "head", 0.9, "valence", "actor voice"),
    "PV": FuncInfo("V", "head", 0.9, "valence", "patient voice"),
    # grammar phase D (2026-11-08): a third demonstrative ('yon'), a remote past beside the recent one, more aspects
    # (inceptive, completive, repetitive), the mirative, an honorific verb marker, the obviative third person
    "DIST": FuncInfo("NP", "dem", 0.4, "det", "far demonstrative ('yon')"),
    "REMPST": FuncInfo("V", "aux", 0.5, "tense", "remote past"),
    "INCH": FuncInfo("V", "aux", 0.6, "aspect", "inceptive ('begin to')"),
    "COMPL": FuncInfo("V", "aux", 0.7, "aspect", "completive ('finish, fully')"),
    "RPT": FuncInfo("V", "aux", 0.6, "aspect", "repetitive ('again')"),
    "MIR": FuncInfo("VP", "aux", 0.5, "mood", "mirative (news, surprise)"),
    "HON": FuncInfo("V", "aux", 0.6, "mood", "honorific (respect for the subject)"),
    "OBV": FuncInfo("N", "head", 0.6, "case", "obviative (the less central third person)"),
}
CLASS_INFO = FuncInfo("N", "dem", 1.3, "class", "noun class")

# affix order, innermost first (Bybee 1985 relevance: derivation, valence, aspect, tense, mood, person; number before case)
SLOT_ORDER = ("deriv", "class", "number", "poss", "det", "case", "valence", "aspect", "tense", "mood", "polarity",
              "person", "clause")   # ('poss' after number, before case: Turkish ev-ler-im-de 'house-PL-1SG.POSS-LOC')

#: noun-class groups, Bantu-like but generic, in the order a growing class system adds them
CLASS_GROUPS = ("person", "people", "manner", "abstract", "plant", "animal", "liquid", "place", "small")
GROUP_GLOSS = {
    "person": "a single person", "people": "people (plural of persons)", "manner": "languages, ways and tools",
    "abstract": "lands, qualities and abstractions", "plant": "trees and plants", "animal": "animals",
    "liquid": "liquids and masses", "place": "places", "small": "small things",
    "masculine": "men, and by default most other nouns", "feminine": "women and female beings",
    "animate": "living beings", "inanimate": "things",
}
#: lexical sources for classifiers that become class markers (first concept the lexicon has wins)
CLASS_SOURCES = {
    "person": ("PERSON", "MAN"), "people": ("PEOPLE", "THEY", "ALL"), "manner": ("TONGUE", "MOUTH", "SAY"),
    "abstract": ("NAME", "THAT"), "plant": ("TREE", "WOOD"), "animal": ("ANIMAL",), "liquid": ("WATER",),
    "place": ("EARTH (SOIL)", "HOUSE"), "small": ("CHILD (YOUNG HUMAN)", "CHILD"),
    "masculine": ("MAN", "HE"), "feminine": ("WOMAN",), "animate": ("PERSON", "ANIMAL"), "inanimate": ("STONE", "THAT"),
}

# --------------------------------------------------------------------------------------------------------------------
# Segment helpers (duck-typed)
# --------------------------------------------------------------------------------------------------------------------


def _percepts():
    try:
        from planet.language import percepts  # noqa: PLC0415
        return percepts
    except ImportError:  # builder A's module not there yet
        try:
            from planet.language import _segstub_d as percepts  # noqa: PLC0415
            return percepts
        except ImportError:
            return None


def _form(w) -> Form:
    """A Word (lexicon), a Segment tuple or list -> Segment tuple."""
    if w is None:
        return ()
    f = getattr(w, "form", w)
    return tuple(f)


def ipa(form: Iterable) -> str:
    form = tuple(form)
    p = _percepts()
    if p is not None and hasattr(p, "word_ipa"):
        try:
            return p.word_ipa(form)
        except Exception:  # noqa: BLE001 - unknown segments: fall through to per-segment
            pass
    out = []
    for s in form:
        if p is not None and hasattr(p, "to_ipa"):
            try:
                out.append(p.to_ipa(s))
                continue
            except Exception:  # noqa: BLE001
                pass
        out.append(getattr(s, "ipa", None) or str(s))
    return "".join(out)


def _is_v(seg) -> bool:
    return getattr(seg, "kind", "C") == "V"


def first_syllable(form: Form) -> Form:
    """Erosion on binding: keep the first syllable (onset + first vowel + one coda consonant if no vowel follows it)."""
    form = tuple(form)
    for i, s in enumerate(form):
        if _is_v(s):
            j = i + 1
            while j < len(form) and _is_v(form[j]) and getattr(form[j], "kind", "") == "T":
                j += 1
            if j < len(form) and not _is_v(form[j]) and (j + 1 >= len(form) or not _is_v(form[j + 1])):
                j += 1
            return form[:j]
    return form[:2]


def clip_syllables(form: Form, n: int = 2) -> Form:
    """The first `n` syllables of a form (percepts.syllabify; without it, cut before the (n+1)th vowel's onset)."""
    form = tuple(form)
    p = _percepts()
    if p is not None and hasattr(p, "syllabify"):
        try:
            syl = p.syllabify(form)
            if len(syl) <= n:
                return form
            return tuple(x for sy in syl[:n] for x in sy.segments)
        except Exception:  # noqa: BLE001 - duck-typed segments: fall through
            pass
    vs = [i for i, x in enumerate(form) if _is_v(x)]
    if len(vs) <= n:
        return form
    return form[:vs[n] - 1] if vs[n] - 1 > vs[n - 1] else form[:vs[n]]


MAX_GRAM_SYLL = 2   # a recruited gram keeps at most this many syllables of its source word


def _recruited_form(form: Form, kyr: float) -> tuple[Form, list[tuple[float, str]]]:
    f = clip_syllables(form, MAX_GRAM_SYLL)
    return f, ([(kyr, f"clipped {ipa(form)} > {ipa(f)}")] if f != tuple(form) else [])


def minimal_form(old: Form) -> Form:
    """What a sound change leaves of a stem it would delete whole: the last vowel, else the last segment (as
    lexicon.minimal_form, so stems stay in step with their words)."""
    old = tuple(old)
    v = [x for x in old if _is_v(x)]
    return (v[-1],) if v else old[-1:]


def _attach(stem: Form, gform: Form, side: str) -> Form:
    return tuple(gform) + tuple(stem) if side == "pre" else tuple(stem) + tuple(gform)


# --------------------------------------------------------------------------------------------------------------------
# Reference tables (read by header; built-in fallbacks when a file is missing)
# --------------------------------------------------------------------------------------------------------------------


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as fh:
        lines = [ln for ln in fh if not ln.startswith("#") and ln.strip()]
    return list(csv.DictReader(lines, delimiter="\t"))


#: WALS 81A-90A frequencies (fallback; the numbers match WALS Online as remembered and as derived in wals_wordorder.tsv)
_FB_ORDER = {"SOV": 0.41, "SVO": 0.355, "VSO": 0.069, "VOS": 0.018, "OVS": 0.008, "OSV": 0.003, "free": 0.137}
#: fallback conditionals P(value | OV or VO), Dryer 1992 / WALS from memory
_FB_CROSS = {
    "adposition": {"OV": {"post": 0.90, "pre": 0.04, "mixed": 0.04, "none": 0.02},
                   "VO": {"post": 0.08, "pre": 0.84, "mixed": 0.06, "none": 0.02},
                   "free": {"post": 0.5, "pre": 0.4, "mixed": 0.08, "none": 0.02}},
    "genitive": {"OV": {"GN": 0.88, "NG": 0.08, "mixed": 0.04}, "VO": {"GN": 0.25, "NG": 0.68, "mixed": 0.07},
                 "free": {"GN": 0.55, "NG": 0.37, "mixed": 0.08}},
    "adjective": {"OV": {"AN": 0.35, "NA": 0.57, "mixed": 0.08}, "VO": {"AN": 0.22, "NA": 0.70, "mixed": 0.08},
                  "free": {"AN": 0.27, "NA": 0.64, "mixed": 0.09}},
    "demonstrative": {"OV": {"DemN": 0.55, "NDem": 0.38, "mixed": 0.07}, "VO": {"DemN": 0.38, "NDem": 0.55, "mixed": 0.07},
                      "free": {"DemN": 0.45, "NDem": 0.47, "mixed": 0.08}},
    "relative": {"OV": {"NRel": 0.38, "RelN": 0.42, "other": 0.20}, "VO": {"NRel": 0.96, "RelN": 0.01, "other": 0.03},
                 "free": {"NRel": 0.70, "RelN": 0.17, "other": 0.13}},
}
_WALS_IDS = {"word_order": "81A", "adposition": "85A", "genitive": "86A", "adjective": "87A", "demonstrative": "88A",
             "relative": "90A"}


def _wals_code(feature: str, name: str) -> str:
    n = name.lower()
    if feature == "word_order":
        return name if name in _FB_ORDER else "free"
    if feature == "adposition":
        return {"postpositions": "post", "prepositions": "pre", "no adpositions": "none"}.get(n, "mixed")
    if feature == "genitive":
        return {"genitive-noun": "GN", "noun-genitive": "NG"}.get(n, "mixed")
    if feature == "adjective":
        return {"adjective-noun": "AN", "noun-adjective": "NA"}.get(n, "mixed")
    if feature == "demonstrative":
        if n in ("demonstrative-noun", "demonstrative prefix"):
            return "DemN"
        if n in ("noun-demonstrative", "demonstrative suffix"):
            return "NDem"
        return "mixed"
    if feature == "relative":
        return {"noun-relative clause": "NRel", "relative clause-noun": "RelN"}.get(n, "other")
    return name


#: Grambank v1.0.3 marginals for the features used here (copied from grambank_features.tsv, so the module works without it)
_FB_GB = {
    "GB020": 0.378, "GB021": 0.137, "GB022": 0.257, "GB023": 0.238, "GB028": 0.525, "GB043": 0.077, "GB044": 0.559,
    "GB048": 0.657, "GB051": 0.183, "GB052": 0.070, "GB053": 0.233, "GB054": 0.068, "GB057": 0.237, "GB059": 0.473,
    "GB068": 0.485, "GB070": 0.342, "GB072": 0.467, "GB083": 0.524, "GB084": 0.454, "GB086": 0.670, "GB089": 0.406,
    "GB090": 0.419, "GB093": 0.344, "GB094": 0.224, "GB107": 0.470, "GB117": 0.567, "GB118": 0.528, "GB120": 0.323,
    "GB147": 0.424, "GB155": 0.726, "GB158": 0.731, "GB187": 0.448, "GB250": 0.435, "GB252": 0.181, "GB257": 0.512,
    "GB262": 0.147, "GB263": 0.392, "GB265": 0.320, "GB266": 0.318, "GB286": 0.177, "GB302": 0.105, "GB322": 0.15,
    "GB323": 0.298, "GB326": 0.533, "GB333": 0.708, "GB335": 0.162, "GB408": 0.443, "GB409": 0.220, "GB522": 0.737,
}


@dataclass
class GPath:
    id: str
    sources: tuple[str, ...]      # lexicon concept candidates (upper-case), or gram functions when `from_gram`
    target: str                   # function code
    weight: float
    from_gram: bool = False
    example: str = ""
    raw_source: str = ""


#: map a path's target_function text to a function code (first matching prefix wins); None = not modelled
_TARGET_MAP = (
    ("RECENT PAST", "RECPST"), ("PAST HABITUAL", "HAB"), ("FUTURE", "FUT"), ("PERFECTIVE / PAST", "PAST"),
    ("PERFECT", "PERF"), ("COMPLETIVE > PERFECT", "PERF"), ("PROGRESSIVE", "PROG"), ("IMPERFECTIVE", "IPFV"),
    ("ABILITY > HABITUAL", "HAB"), ("DUMMY AUXILIARY / EMPHATIC / HABITUAL", "HAB"), ("DIRECT EVIDENTIAL", "EVID.DIR"),
    ("HEARSAY EVIDENTIAL", "EVID.REP"), ("BENEFACTIVE / DATIVE", "DAT"), ("DATIVE > ACCUSATIVE", "ACC"),
    ("OBJECT MARKER", "ACC"), ("INSTRUMENTAL", "INS"), ("COMITATIVE", "COM"), ("TERMINATIVE / ALLATIVE", "ALL"),
    ("INSIDE > IN", "LOC"), ("TOP > ON", "LOC"), ("CAUSATIVE", "CAUS"), ("PASSIVE", "PASS"), ("REFLEXIVE", "REFL"),
    ("INDEFINITE ARTICLE", "INDEF"), ("DEFINITE ARTICLE", "DEF"), ("NOUN MARKER / GENDER-CLASS", "CLASS"),
    ("VERB AGREEMENT", "3SG"), ("DIMINUTIVE", "DIM"), ("PLURAL", "PL"), ("NUMERAL CLASSIFIER", "CLASS"),
    ("GENITIVE", "GEN"), ("NEGATION", "NEG"), ("STANDARD NEGATION", "NEG"), ("INDEFINITE PRONOUN > FIRST PERSON", "1PL"),
    ("MIDDLE > PASSIVE", "PASS"),   # G060 reflexive > middle > passive (Russian -sja, Spanish se; mapped 2026-11-07)
    # grammar phase B (2026-11-08): mood from the written paths
    ("OBLIGATION", "OBLG"), ("PERMISSIVE > HORTATIVE", "HORT"), ("APPREHENSIVE", "APPR"),
    # grammar phase C (2026-11-08): the constructions' written paths (G055 and G058 > relativizer, G023 'say' >
    # complementizer, G056 demonstrative > copula, G057 copula > focus)
    ("RELATIVE", "REL"), ("QUOTATIVE > COMPLEMENTIZER", "COMP"), ("QUOTATIVE / COMPLEMENTIZER", "COMP"),
    ("COPULA", "COP"), ("FOCUS MARKER", "FOC"),
)
#: path source texts that are grams, not words (reanalysis: the gram changes function)
_GRAM_SOURCES = {"PERFECT": "PERF", "PROGRESSIVE": "PROG", "ALLATIVE": "ALL", "ABLATIVE": "ABL", "DEFINITE ARTICLE": "DEF",
                 "COMITATIVE": "COM", "REFLEXIVE": "REFL", "COPULA": "COP"}
#: source words -> lexicon concepts (Concepticon glosses as in concepts.tsv)
_SOURCE_ALIASES = {
    "HAVE": ("HOLD",), "BE AT": ("AT",), "DEMONSTRATIVE": ("THAT", "THIS"), "THIRD PERSON PRONOUN": ("HE OR SHE OR IT", "HE"),
    "CHILD": ("CHILD (YOUNG HUMAN)", "CHILD"), "SON": ("CHILD (DESCENDANT)",), "KNOW": ("KNOW (SOMETHING)",),
    # 'get' is not 'take' (G019 get > past, G032 get > passive need a real 'get' word); a negator comes from a negative
    # existential, 'lack' or 'nothing' (Croft 1991; Jespersen's minimizers), never from the negator 'not' itself
    "FEAR": ("FEAR (BE AFRAID)",), "NEGATIVE EXISTENTIAL": ("NOTHING", "LACK", "NO"),
    "MINIMIZER": ("NOTHING",),
    "NOUN": ("TREE", "BODY", "HEAD"), "COMPANION": ("FRIEND",), "LIE": ("LIE (REST)",), "PEOPLE": ("PERSON",),
    "MAN": ("MAN", "MALE PERSON"), "BASE": ("ROOT",), "WALK": ("WALK",), "BELLY": ("BELLY",),
    "MAKE": ("DO OR MAKE",), "DO": ("DO OR MAKE",), "ALL": ("ALL",), "WH-INTERROGATIVE": ("WHO", "WHAT"),
}
#: built-in paths beyond the table (from memory: Givon 1976 pronoun > agreement; Heine & Kuteva 2002 entries for
#: 'two' > dual, 'man' > agentive, 'place/house' > locative nominal, adpositions > case affixes (their ADPOSITION > CASE))
_BUILTIN_PATHS = (
    ("X01", ("NOTHING", "LACK", "REFUSE"), "NEG", "very common",
     "'nothing, lack, refuse' > negator (no such word: a coined negator particle)"),
    ("X02", ("MANY", "ALL"), "PL", "common", "quantifier > plural (as WLG MANY > PL)"),
    ("X03", ("TWO",), "DU", "attested", "'two' > dual"),
    ("X04", ("IN", "AT"), "LOC", "very common", "locative adposition > locative case"),
    ("X05", ("WITH",), "COM", "very common", "comitative adposition > comitative case"),
    ("X06", ("I",), "1SG", "very common", "1sg pronoun > clitic > agreement (Givon 1976)"),
    ("X07", ("THOU", "YOU"), "2SG", "very common", "2sg pronoun > agreement"),
    ("X08", ("HE OR SHE OR IT", "HE"), "3SG", "very common", "3sg pronoun > agreement"),
    ("X09", ("WE",), "1PL", "common", "1pl pronoun > agreement"),
    ("X10", ("YOU",), "2PL", "common", "2pl pronoun > agreement"),
    ("X11", ("THEY",), "3PL", "common", "3pl pronoun > agreement"),
    ("X12", ("PERSON", "MAN", "MALE PERSON"), "AGENT", "common", "'man, person' > agent noun ('one who')"),
    ("X13", ("HOUSE", "EARTH (SOIL)"), "PLACE", "attested", "'house, ground' > place noun (cf. -stead, -ham, -stan)"),
    ("X14", ("YESTERDAY",), "PAST", "attested", "temporal adverb > past particle"),
    ("X15", ("THAT", "THIS"), "DEF", "very common", "demonstrative > definite (WLG)"),
    ("X16", ("ONE",), "INDEF", "very common", "'one' > indefinite (WLG)"),
    ("X17", ("INS",), "ERG", "attested", "instrumental > ergative (Garrett 1990)"),
    ("X18", ("GIVE",), "DAT", "very common", "serial 'give' > dative (WLG)"),
    # 2026-11-07, grammar phase A: the ergative's other attested sources (Kuteva et al. 2019, 'ablative > ergative',
    # 'locative > ergative', 'genitive > ergative'; Dixon 1994 ch. 6; McGregor 2009), an agentive 'by' (the passive
    # agent marker, English by < 'near', reanalysed as an ergative when the passive becomes the basic transitive, as in
    # Indo-Iranian), the accusative from the dative (Hindi ko, Spanish a: differential object marking), and lexical
    # sources for the oblique cases that had none: 'leave, come from' > ablative (Ewe tso, Mandarin cong), 'go' >
    # allative, 'take, hold' > instrumental (Twi de, Akan de), 'use' > instrumental (G031 needs USE, which the lexicon lacks)
    ("X19", ("ABL",), "ERG", "attested", "ablative > ergative (Tibeto-Burman, Australian; Kuteva et al. 2019)"),
    ("X20", ("LOC",), "ERG", "attested", "locative > ergative (Kuteva et al. 2019; Dixon 1994)"),
    ("X21", ("GEN",), "ERG", "attested", "genitive > ergative (Eskimo relative case; Garrett 1990)"),
    ("X22", ("NEAR", "WITH"), "ERG", "attested", "agentive 'by, near' > passive agent > ergative (McGregor 2009)"),
    ("X23", ("DAT",), "ACC", "common", "dative > accusative (differential object marking: Hindi ko, Spanish a)"),
    ("X24", ("LEAVE", "COME"), "ABL", "common", "'leave, come from' > ablative (WLG: Ewe tso, Mandarin cong)"),
    ("X25", ("GO",), "ALL", "attested", "'go' > allative (WLG: Thai pai, Ewe yi)"),
    ("X26", ("TAKE", "HOLD"), "INS", "common", "serial 'take X and V' > instrumental (WLG: Twi de, Yoruba fi)"),
    # 2026-11-08, grammar phase B. Mood: 'come' and 'go' > hortative and 'give' > permissive/hortative (Heine & Kuteva
    # 2002; Russian davai 'give' > 'let's'); the imperative's own marker from an attention word 'look!, come!' or from
    # a hortative widened to the second person (a guess: the catalogue has no imperative source; most languages use
    # the bare stem, WALS 70A). Genitive: ablative > genitive (Latin de > French de; Kuteva et al. 2019) and a
    # demonstrative linker (Albanian i/e, the Persian ezafe; Kuteva et al. 2019), beside G067 'belong'. Object
    # agreement: object pronoun > object marker on the verb (Givon 1976; Bantu object prefixes, Swahili a-ni-ona); a
    # possessive pronoun > possessor affix on the noun (Turkish -im, Quechua -y). One lead path per series: the other
    # members bind with it ('set' paths, `_person_set`). The inclusive 'we' joins a binding subject series.
    ("X27", ("COME", "GO"), "HORT", "attested", "'come, go' > hortative particle (Heine & Kuteva 2002)"),
    ("X28", ("GIVE",), "HORT", "attested", "'give' > permissive > hortative (Russian davai; Heine & Kuteva 2002)"),
    ("X29", ("LOOK", "COME"), "IMP", "attested", "'look!, come!' > imperative particle (a guess; no catalogued path)"),
    ("X30", ("HORT",), "IMP", "attested", "hortative > imperative (the 'let us' marker widened to commands)"),
    ("X31", ("ABL",), "GEN", "common", "ablative > genitive (Latin de > French de; Kuteva et al. 2019)"),
    ("X32", ("THAT", "THIS"), "GEN", "attested", "demonstrative > genitive linker (Albanian i/e, Persian ezafe)"),
    ("X33", ("HE OR SHE OR IT", "HE"), "3SG.O", "common", "object pronoun > object agreement (Givon 1976; Swahili)"),
    ("X34", ("I",), "1SG.O", "set", "1sg object pronoun > object marker (with the series)"),
    ("X35", ("THOU", "YOU"), "2SG.O", "set", "2sg object pronoun > object marker (with the series)"),
    ("X36", ("WE",), "1PL.O", "set", "1pl object pronoun > object marker (with the series)"),
    ("X37", ("YOU",), "2PL.O", "set", "2pl object pronoun > object marker (with the series)"),
    ("X38", ("THEY",), "3PL.O", "set", "3pl object pronoun > object marker (with the series)"),
    ("X39", ("I",), "1SG.POSS", "common", "possessive pronoun > possessor affix (Turkish -im; Givon 1976)"),
    ("X40", ("THOU", "YOU"), "2SG.POSS", "set", "2sg possessive > possessor affix (with the series)"),
    ("X41", ("HE OR SHE OR IT", "HE"), "3SG.POSS", "set", "3sg possessive > possessor affix (with the series)"),
    ("X42", ("WE",), "1PL.POSS", "set", "1pl possessive > possessor affix (with the series)"),
    ("X43", ("YOU",), "2PL.POSS", "set", "2pl possessive > possessor affix (with the series)"),
    ("X44", ("THEY",), "3PL.POSS", "set", "3pl possessive > possessor affix (with the series)"),
    ("X45", ("WE (INCLUSIVE)",), "1PL.INCL", "set", "inclusive 'we' > inclusive subject marker (with the series)"),
    # 2026-11-08, grammar phase C. Constructions as grams: the question particle from 'if, whether' (Russian li,
    # Kuteva et al. 2019 'conditional > polar question') or from a negator (Mandarin ma < 'not have'; A-not-A
    # questions); the copula from a third-person pronoun (Hebrew hu; Li & Thompson 1977, beside G056's demonstrative)
    # or a posture verb (Spanish estar < 'stand'); the topic marker from 'if, when' (Haiman 1978: conditionals are
    # topics) or a demonstrative; the relativizer > complementizer (English that). Valence: 'give' > benefactive
    # applicative and comitative > applicative (Peterson 2007), reflexive > reciprocal (G059; Maslova & Nedjalkov,
    # WALS 106A), 'other' > reciprocal ('one ... the other'), reflexive > antipassive (Australian; Terrill 1997,
    # Polinsky WALS 108A). Switch-reference: 'and' or a comitative > same subject, a locative or 'when' > different
    # subject (Jacobsen 1967; Haiman & Munro 1983). Symmetrical voice: passive > patient voice (Ross 2002 on
    # Austronesian), an actor-voice marker from 'do, make' (a guess: the source of Austronesian *-um- is unknown).
    ("X46", ("IF",), "Q", "common", "'if, whether' > polar question particle (Russian li; Kuteva et al. 2019)"),
    ("X47", ("NOT", "NOTHING"), "Q", "attested", "negator > question particle (Mandarin ma < 'not have')"),
    ("X48", ("HE OR SHE OR IT", "HE"), "COP", "common", "3rd person pronoun > copula (Hebrew hu; Li & Thompson 1977)"),
    ("X49", ("STAND", "SIT"), "COP", "attested", "posture verb > copula (Spanish estar < Latin stare 'stand')"),
    ("X50", ("REL",), "COMP", "attested", "relativizer > complementizer (English that; Kuteva et al. 2019)"),
    ("X51", ("IF", "WHEN"), "TOP", "attested", "'if, when' > topic marker (Haiman 1978: conditionals are topics)"),
    ("X52", ("THAT", "THIS"), "TOP", "attested", "demonstrative > topic marker (Kuteva et al. 2019)"),
    ("X53", ("GIVE",), "APPL", "attested", "serial 'give' > benefactive applicative (Peterson 2007)"),
    ("X54", ("COM",), "APPL", "attested", "comitative > applicative (Peterson 2007)"),
    ("X55", ("REFL",), "RECP", "common", "reflexive > reciprocal (G059; Maslova & Nedjalkov, WALS 106A)"),
    ("X56", ("OTHER",), "RECP", "attested", "'other' > reciprocal ('one ... the other', French l'un l'autre)"),
    ("X57", ("REFL",), "ANTIP", "common", "reflexive > antipassive (Terrill 1997; Polinsky, WALS 108A)"),
    ("X58", ("AND",), "SS", "attested", "'and' > same-subject marker (Haiman & Munro 1983)"),
    ("X59", ("COM",), "SS", "attested", "comitative > same-subject marker (Haiman & Munro 1983)"),
    ("X60", ("LOC",), "DS", "attested", "locative > different-subject marker (Jacobsen 1967; Haiman & Munro 1983)"),
    ("X61", ("WHEN",), "DS", "attested", "'when' > different-subject marker (Jacobsen 1967; a subordinator)"),
    ("X62", ("PASS",), "PV", "attested", "passive > patient voice (Ross 2002; Austronesian)"),
    ("X63", ("DO OR MAKE",), "AV", "attested", "'do, make' > actor voice (a guess: no catalogued source)"),
    # 2026-11-08, grammar phase D. Deixis: 'that' reinforced by a place word becomes a far demonstrative ('that there'
    # > yon; Spanish aquel < eccum ille, French celui-la; Diessel 1999), so the language counts three distances. Tense
    # remoteness: a remote past beside the past and the recent past (Bantu graded pasts; Nurse 2008; the source 'long,
    # old, before' is a guess). Aspect: 'finish' > completive (Heine & Kuteva 2002 FINISH > COMPLETIVE; Bybee et al.
    # 1994), 'begin' > inceptive (Heine & Kuteva 2002), 'return, turn' > repetitive (Heine & Kuteva 2002 RETURN >
    # REPETITIVE). Mirativity: a perfect or a reportative evidential that also marks news and surprise (Turkish -mIs,
    # Bulgarian; DeLancey 1997, Aikhenvald 2004): copies, the source keeps its function. Honorific verb marker: 'lord,
    # master, king' > honorific (a guess: no catalogued path; Korean -si- has no known source). Obviative: a
    # demonstrative or 'other' > obviative (a guess: the Algonquian obviative's source is unknown).
    ("X64", ("THAT",), "DIST", "very common", "'that' + a place word > far demonstrative ('that there' > yon; Diessel 1999)"),
    ("X65", ("LONG", "OLD", "BEFORE"), "REMPST", "common", "'long, old, before' > remote past (graded pasts; a guess)"),
    ("X66", ("FINISH",), "COMPL", "very common", "'finish' > completive (Heine & Kuteva 2002; Bybee et al. 1994)"),
    ("X67", ("BEGIN",), "INCH", "attested", "'begin' > inceptive (Heine & Kuteva 2002)"),
    ("X68", ("RETURN HOME", "TURN AROUND"), "RPT", "attested", "'return, turn' > repetitive (Heine & Kuteva 2002)"),
    ("X69", ("PERF",), "MIR", "attested", "perfect > mirative (Turkish -mIs, Bulgarian; DeLancey 1997)"),
    ("X70", ("EVID.REP",), "MIR", "attested", "reportative > mirative (Aikhenvald 2004)"),
    ("X71", ("KING", "MASTER"), "HON", "attested", "'lord, master' > honorific verb marker (a guess)"),
    ("X72", ("THAT", "OTHER"), "OBV", "attested", "'that, other' > obviative (a guess: Algonquian's source is unknown)"),
    ("X73", ("WHAT",), "Q", "attested", "'what' > polar question particle (Polish czy; Kuteva et al. 2019)"),
    # 2026-11-09, PW-1569: sources of the local and peripheral cases. Region nouns and adpositions > region markers
    # (Heine & Kuteva 2002 BELLY > IN, HEAD > ON; Svorou 1994); 'through, road' > perlative (Svorou 1994; Kuteva et al.
    # 2019 PATH > PERLATIVE); 'without' > privative/abessive (Finnish -tta, Hungarian -talan, the privatives of
    # Australian languages; Dixon 2002); 'become' > translative (a guess: the Finnish -ksi's source is unknown).
    ("X74", ("IN", "BELLY"), "INE", "common", "'in, belly' > inessive (Heine & Kuteva 2002 BELLY > IN)"),
    ("X75", ("TOP", "HEAD"), "SUPE", "common", "'top, head' > superessive (Heine & Kuteva 2002 HEAD > ON)"),
    ("X76", ("THROUGH", "ROAD", "PATH"), "PERL", "attested", "'through, road' > perlative (Svorou 1994)"),
    ("X77", ("WITHOUT",), "PRIV", "common", "'without' > privative (Finnish -tta, Australian privatives; Dixon 2002)"),
    ("X78", ("BECOME",), "TRANSL", "attested", "'become' > translative (a guess; Finnish -ksi's source is unknown)"),
)
#: gram-to-gram paths whose source keeps its own function (polysemy: the copula stays a copula when a focus particle
#: splits off it, the reflexive stays reflexive beside a reciprocal); the new gram starts with the source's form. Every
#: other gram path is a reanalysis (the gram changes function: PERF > PAST).
COPY_PATHS = {"G057", "X50", "X54", "X55", "X57", "X59", "X60", "X69", "X70"}


def _parse_source(text: str) -> tuple[tuple[str, ...], bool]:
    t = text.strip().upper()
    for k, fn in _GRAM_SOURCES.items():
        if t.startswith(k) and not t.startswith("ALL "):
            return (fn,), True
    import re  # noqa: PLC0415
    bare = re.sub(r"\([^)]*\)", "", t)
    out: list[str] = []
    for tok in [x.strip() for x in bare.split("/") if x.strip()]:
        for alias in _SOURCE_ALIASES.get(tok, (tok,)):
            if alias not in out:
                out.append(alias)
    return tuple(out), False


def _map_target(text: str) -> str | None:
    t = text.strip().upper()
    for prefix, code in _TARGET_MAP:
        if t.startswith(prefix):
            return code
    return None


@dataclass
class Tables:
    wals_freq: dict[str, dict[str, float]]
    wals_cross: dict[str, dict[str, dict[str, float]]]      # feature -> word order value -> value -> p
    gb_marg: dict[str, float]                               # P(GBxxx = 1)
    gb_corr: dict[str, list[tuple[str, str, dict[str, float], float]]]  # f2 -> [(f1, v1, {v2: lift}, cramers_v)]
    paths: list[GPath]
    sources: dict[str, str]


@lru_cache(maxsize=2)
def load_tables(use_files: bool = True) -> Tables:
    """Read the reference tables by their headers; any missing or unreadable table falls back to the built-in set."""
    sources = {}
    wals_freq: dict[str, dict[str, float]] = {"word_order": dict(_FB_ORDER)}
    wals_cross: dict[str, dict[str, dict[str, float]]] = {}
    sources["wals"] = "builtin"
    p = DATA / "wals_wordorder.tsv"
    if use_files and p.exists():
        try:
            inv = {v: k for k, v in _WALS_IDS.items()}
            freq: dict[str, dict[str, float]] = {}
            cross: dict[str, dict[str, dict[str, float]]] = {}
            for r in _read_tsv(p):
                f1 = inv.get(r["feature"])
                if f1 is None:
                    continue
                if r["table"] == "freq":
                    d = freq.setdefault(f1, {})
                    c = _wals_code(f1, r["value_name"])
                    d[c] = d.get(c, 0.0) + float(r["count"])
                elif r["table"] == "crosstab" and f1 == "word_order":
                    f2 = inv.get(r["feature2"])
                    if f2 is None:
                        continue
                    wo = _wals_code("word_order", r["value_name"])
                    d = cross.setdefault(f2, {}).setdefault(wo, {})
                    c = _wals_code(f2, r["value2_name"])
                    d[c] = d.get(c, 0.0) + float(r["count"])
            for dd in [*freq.values(), *(x for v in cross.values() for x in v.values())]:
                tot = sum(dd.values()) or 1.0
                for k in dd:
                    dd[k] /= tot
            if "word_order" in freq:
                wals_freq, wals_cross = freq, cross
                sources["wals"] = str(p.name)
        except (KeyError, ValueError):
            pass
    gb_marg = dict(_FB_GB)
    sources["grambank_features"] = "builtin"
    p = DATA / "grambank_features.tsv"
    if use_files and p.exists():
        try:
            for r in _read_tsv(p):
                if r["value"] == "1" and r["feature_id"] in _FB_GB:
                    gb_marg[r["feature_id"]] = float(r["frequency"])
            sources["grambank_features"] = p.name
        except (KeyError, ValueError):
            pass
    gb_corr: dict[str, list] = {}
    sources["grambank_correlations"] = "none"
    p = DATA / "grambank_correlations.tsv"
    if use_files and p.exists():
        try:
            tmp: dict[tuple[str, str, str], dict[str, float]] = {}
            cv: dict[tuple[str, str], float] = {}
            for r in _read_tsv(p):
                key = (r["f2"], r["f1"], r["v1"])
                tmp.setdefault(key, {})[r["v2"]] = float(r["lift"])
                cv[(r["f2"], r["f1"])] = float(r["cramers_v"])
            for (f2, f1, v1), lifts in tmp.items():
                gb_corr.setdefault(f2, []).append((f1, v1, lifts, cv[(f2, f1)]))
            sources["grambank_correlations"] = p.name
        except (KeyError, ValueError):
            gb_corr = {}
    paths: list[GPath] = []
    sources["paths"] = "builtin"
    p = DATA / "grammaticalization_paths.tsv"
    if use_files and p.exists():
        try:
            for r in _read_tsv(p):
                tgt = _map_target(r["target_function"])
                if tgt is None:
                    continue
                srcs, from_gram = _parse_source(r["source_concept"])
                if not srcs:
                    continue
                paths.append(GPath(r["id"], srcs, tgt, PATH_FREQ_WEIGHT.get(r.get("frequency_class", ""), 1.0),
                                   from_gram, r.get("example", ""), r["source_concept"]))
            sources["paths"] = p.name + " + builtin"
        except KeyError:
            paths = []
    for pid, srcs, tgt, fc, ex in _BUILTIN_PATHS:
        from_gram = all(s in FUNCS for s in srcs)
        paths.append(GPath(pid, srcs, tgt, PATH_FREQ_WEIGHT[fc], from_gram, ex, "/".join(srcs)))
    return Tables(wals_freq, wals_cross, gb_marg, gb_corr, paths, sources)


# --------------------------------------------------------------------------------------------------------------------
# Typology
# --------------------------------------------------------------------------------------------------------------------


class Typology(dict):
    """feature -> value (strings). `head_direction` and `tone` are derived, not drawn."""

    def ov(self) -> str:
        wo = self.get("word_order", "SOV")
        if wo == "free":
            return "free"
        return "OV" if wo.index("O") < wo.index("V") else "VO"

    def head_final(self) -> bool:
        return self.get("head_direction", "final") == "final"


class Shown(Typology):
    """A grammar's shown typology. A value written into it from outside (a calque on shift, a test) sets the grammar's
    aim, and the shown value is re-read from the grams at once, so no writer can leave the two layers disagreeing."""

    def __setitem__(self, k, v):
        g = self.__dict__.get("_g")
        if g is None or g.__dict__.get("typology") is not self:   # (unattached, or mid-copy / unpickling)
            return super().__setitem__(k, v)
        aims(g)[k] = v
        realise(g)


#: draw order (fixed) and stability class per feature. Classes from memory of Dediu & Cysouw 2013 (PLoS ONE, "Some
#: structural aspects of language are more stable than others") and Greenhill et al. 2017 (PNAS, "Evolutionary dynamics of
#: language systems"): word order and adposition order among the slow features, gender and alignment slow, articles and
#: adjective order among the fast, TAM marking fairly fast. The ranking is theirs as remembered; the rates are ours.
FEATURES: tuple[tuple[str, str], ...] = (
    ("word_order", "very_stable"), ("adposition", "very_stable"), ("genitive", "stable"), ("adjective", "fickle"),
    ("demonstrative", "medium"), ("numeral", "medium"), ("relative", "stable"), ("definite_article", "fickle"),
    ("indefinite_article", "very_fickle"), ("case", "medium"), ("alignment", "stable"), ("number", "medium"),
    ("gender", "stable"), ("past", "fickle"), ("future", "fickle"), ("perfective", "fickle"), ("progressive", "very_fickle"),
    ("habitual", "very_fickle"), ("evidentiality", "medium"), ("negation", "medium"), ("polar_question", "medium"),
    ("pro_drop", "medium"), ("alienability", "stable"), ("numeral_classifiers", "medium"), ("clusivity", "stable"),
    ("verb_reduplication", "medium"), ("causative", "medium"), ("passive", "fickle"), ("diminutive", "fickle"),
    ("agent_noun", "medium"), ("comparative", "medium"), ("serial_verbs", "medium"), ("copula", "fickle"),
    ("predicative_possession", "medium"), ("adjective_verb_like", "stable"), ("numeral_base", "stable"),
    ("wh_in_situ", "medium"), ("verb_agreement", "medium"), ("object_agreement", "fickle"),
)
DERIVED = ("head_direction", "tone")

#: per-generation flip hazard by class (a flip re-draws the value, which may come back the same, so retention never falls
#: below the value's share in the re-draw). Calibrated (docs/review/language/calibration.md, "Word length and typology drift
#: round") so that over 20 kyr a human lect (27.7-yr generations, ~720 generations, the median adult-L2 share 0.54) keeps
#: its proto's value in about 85-90% of lects for the very stable features (basic order, adpositions), ~80% for the stable
#: ones, ~65% for the medium ones and ~50-60% for the fickle ones. Targets: Dediu 2011 (Proc. R. Soc. B 278:474) and
#: Dediu & Cysouw 2013 (PLoS ONE 8:e55009) rank word order, adposition order, gender and alignment among the slow
#: features and articles, adjective order and TAM marking among the fast; Greenhill et al. 2017 (PNAS 114:E8822) find
#: grammatical features as a whole change at rates overlapping basic vocabulary (many no slower, a stable core much
#: slower); Dunn et al. 2011 (Nature 473:79) show word-order features changing several times within families of 4-6 kyr
#: depth (Austronesian, Bantu, Indo-European, Uto-Aztecan), always with lineage-specific co-dependencies. Hazards are per
#: generation, so peoples with long generations change proportionally less per kyr, as sound change does.
STABILITY = {"very_stable": 2e-4, "stable": 5e-4, "medium": 1e-3, "fickle": 2.5e-3, "very_fickle": 4e-3}
#: a word-order harmony feature (adposition, genitive, adjective, demonstrative, relative) whose current value the basic
#: order now disfavours flips faster: hazard x (1 + DISHARMONY * (1 - p(value | order) / p(best value | order))). After an
#: OV > VO change, postpositions (p 0.08 vs 0.84 for prepositions) re-draw ~9x as often, so the harmony re-asserts itself
#: within a few kyr, as in Dunn et al. 2011's correlated transitions (Dryer 1992's harmonies), not only by chance.
DISHARMONY = 9.0
FEATURE_CLASS = dict(FEATURES)

#: morphological features adult L2 learners push toward their simplest value when they re-draw (Trudgill 2011)
SIMPLE_VALUE = {"case": "none", "number": "none", "gender": "none", "alignment": "neutral", "evidentiality": "none",
                "past": "none", "future": "none", "perfective": "none", "verb_agreement": "none",
                "object_agreement": "none", "causative": "periphrastic", "passive": "none", "diminutive": "none",
                "definite_article": "none", "indefinite_article": "none", "alienability": "no"}


def _implied_gb(name: str, v: str) -> dict[str, str]:
    """Grambank values implied by a named feature value (for conditioning later draws)."""
    b = lambda x: "1" if x else "0"  # noqa: E731
    if name == "word_order":
        if v == "free":
            return {}
        return {"GB133": b(v in ("SOV", "OSV")), "GB131": b(v in ("VSO", "VOS")), "GB132": b(v in ("SVO", "OVS"))}
    if name == "adposition":
        return {"GB074": b(v in ("pre", "mixed")), "GB075": b(v in ("post", "mixed"))}
    if name == "genitive":
        return {"GB065": {"GN": "1", "NG": "2"}.get(v, "3")}
    if name == "adjective":
        return {"GB193": {"AN": "1", "NA": "2"}.get(v, "3")}
    if name == "demonstrative":
        return {"GB025": {"DemN": "1", "NDem": "2"}.get(v, "3")}
    if name == "numeral":
        return {"GB024": {"NumN": "1", "NNum": "2"}.get(v, "3")}
    if name == "relative":
        return {"GB327": b(v == "NRel"), "GB328": b(v == "RelN")}
    if name == "definite_article":
        return {"GB020": b(v != "none"), "GB022": b(v == "pre"), "GB023": b(v == "post")}
    if name == "case":
        return {"GB070": b(v in ("few", "many")), "GB072": b(v == "many")}
    if name == "alignment":
        return {"GB408": b(v in ("nom-acc", "split")), "GB409": b(v in ("erg-abs", "split"))}
    if name == "number":
        return {"GB044": b(v != "none"), "GB043": b(v == "sg-du-pl")}
    if name == "gender":
        return {"GB051": b(v == "sex"), "GB053": b(v == "animacy"), "GB054": b(v == "classes")}
    if name == "verb_agreement":
        return {"GB090": b(v in ("prefix", "both")), "GB089": b(v in ("suffix", "both"))}
    if name == "object_agreement":
        return {"GB094": b(v == "prefix"), "GB093": b(v == "suffix")}
    if name == "polar_question":
        return {"GB263": b(v == "final_particle"), "GB262": b(v == "initial_particle"), "GB286": b(v == "verb_morph")}
    if name == "evidentiality":
        return {"GB323": b(v != "none"), "GB322": b(v == "direct+indirect")}
    if name == "passive":
        return {"GB147": b(v == "bound"), "GB302": b(v == "periphrastic")}
    if name == "comparative":
        return {"GB265": b(v == "exceed"), "GB266": b(v == "locational")}
    if name == "predicative_possession":
        return {"GB250": b(v == "have"), "GB252": b(v == "locational")}
    if name == "numeral_base":
        return {"GB335": b(v == "vigesimal"), "GB333": b(v == "decimal")}
    one = {"indefinite_article": "GB021", "past": "GB083", "future": "GB084", "perfective": "GB086", "pro_drop": "GB522",
           "alienability": "GB059", "numeral_classifiers": "GB057", "clusivity": "GB028", "verb_reduplication": "GB158",
           "causative": "GB155", "diminutive": "GB187", "agent_noun": "GB048", "serial_verbs": "GB118", "copula": "GB117",
           "adjective_verb_like": "GB068", "wh_in_situ": "GB326", "progressive": "GB120"}
    if name in one:
        return {one[name]: b(v not in ("none", "no", "periphrastic"))}
    return {}


def _ctx(typ: dict, skip: str | None = None) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in typ.items():
        if k != skip:
            out.update(_implied_gb(k, v))
    return out


def _p1(gb: str, ctx: dict[str, str], T: Tables, own: Iterable[str] = (), k: int = 3) -> float:
    """P(gb = 1 | ctx): Grambank marginal times the lifts of the k strongest already-known correlates (naive Bayes over the
    strongest few, so correlated parents are not counted many times)."""
    p = T.gb_marg.get(gb, 0.5)
    own = set(own) | {gb}
    cands = [(cv, f1, v1, lifts) for f1, v1, lifts, cv in T.gb_corr.get(gb, ()) if f1 not in own and ctx.get(f1) == v1]
    cands.sort(key=lambda x: -x[0])
    w1, w0 = p, 1.0 - p
    for _, _, _, lifts in cands[:k]:
        w1 *= lifts.get("1", 1.0)
        w0 *= lifts.get("0", 1.0)
    tot = w1 + w0
    return min(max(w1 / tot if tot > 0 else p, 0.01), 0.99)


def _choice(rng: np.random.Generator, probs: dict[str, float]) -> str:
    keys = list(probs)
    w = np.array([max(probs[k], 0.0) for k in keys], dtype=float)
    if w.sum() <= 0:
        return keys[0]
    return keys[int(rng.choice(len(keys), p=w / w.sum()))]


def _bern(rng, p) -> bool:
    return bool(rng.random() < p)


def _draw_feature(rng: np.random.Generator, name: str, typ: Typology, T: Tables) -> str:
    ctx = _ctx(typ, skip=name)
    ov = typ.ov() if "word_order" in typ else "free"
    if name == "word_order":
        return _choice(rng, T.wals_freq.get("word_order", _FB_ORDER))
    if name in _FB_CROSS:
        wo = typ.get("word_order", "free")
        table = T.wals_cross.get(name, {}).get(wo)
        if not table:
            table = _FB_CROSS[name][ov]
        return _choice(rng, table)
    if name == "numeral":
        # no WALS crosstab in the table set for 89A; Dryer: NumN slightly likelier in OV, NNum in VO
        base = {"NumN": 0.40, "NNum": 0.50, "mixed": 0.10}
        if ov == "OV":
            base = {"NumN": 0.50, "NNum": 0.40, "mixed": 0.10}
        return _choice(rng, base)
    p = lambda gb, own=(): _p1(gb, ctx, T, own)  # noqa: E731
    if name == "definite_article":
        if not _bern(rng, p("GB020", ("GB022", "GB023"))):
            return "none"
        pre = p("GB022", ("GB020", "GB023"))
        post = p("GB023", ("GB020", "GB022"))
        return "pre" if _bern(rng, pre / (pre + post)) else "post"
    if name == "indefinite_article":
        return "present" if _bern(rng, p("GB021")) else "none"
    if name == "case":
        core, obl = _bern(rng, p("GB070", ("GB072",))), _bern(rng, p("GB072", ("GB070",)))
        return "many" if core and obl else ("few" if core or obl else "none")
    if name == "alignment":
        acc, erg = _bern(rng, p("GB408", ("GB409",))), _bern(rng, p("GB409", ("GB408",)))
        return "split" if acc and erg else "nom-acc" if acc else "erg-abs" if erg else "neutral"
    if name == "number":
        if not _bern(rng, max(p("GB044", ("GB043",)), 0.0) + (1 - p("GB044", ("GB043",))) * T.gb_marg.get("GB318", 0.18)):
            return "none"
        return "sg-du-pl" if _bern(rng, p("GB043", ("GB044",)) / max(T.gb_marg.get("GB044", 0.56), 0.1)) else "sg-pl"
    if name == "gender":
        own = ("GB051", "GB052", "GB053", "GB054")
        if _bern(rng, max(p("GB054", own), p("GB052", own))):
            return "classes"
        if _bern(rng, p("GB051", own)):
            return "sex"
        if _bern(rng, p("GB053", own) * 0.6):  # many Grambank animacy 'yes' are pronoun-only; damp
            return "animacy"
        return "none"
    if name in ("past", "future", "perfective"):
        gb = {"past": "GB083", "future": "GB084", "perfective": "GB086"}[name]
        # Grambank asks about *bound* marking; free particles add some on top
        return "marked" if _bern(rng, min(p(gb) + 0.1, 0.95)) else "none"
    if name == "progressive":
        return "marked" if _bern(rng, 0.25 + 0.3 * p("GB120")) else "none"
    if name == "habitual":
        return "marked" if _bern(rng, 0.25) else "none"
    if name == "evidentiality":
        if not _bern(rng, p("GB323", ("GB322",))):
            return "none"
        return "direct+indirect" if _bern(rng, 0.35) else "indirect"
    if name == "negation":
        # Dryer (WALS 143A) from memory: preverbal negation dominant overall; postverbal and clause-final likelier in OV
        tab = {"OV": {"preverbal": 0.45, "postverbal": 0.28, "clause_final": 0.22, "clause_initial": 0.05},
               "VO": {"preverbal": 0.70, "postverbal": 0.10, "clause_final": 0.12, "clause_initial": 0.08},
               "free": {"preverbal": 0.60, "postverbal": 0.18, "clause_final": 0.15, "clause_initial": 0.07}}[ov]
        return _choice(rng, tab)
    if name == "polar_question":
        own = ("GB263", "GB262", "GB286")
        if _bern(rng, p("GB263", own)):
            return "final_particle"
        if _bern(rng, p("GB262", own)):
            return "initial_particle"
        if _bern(rng, p("GB286", own)):
            return "verb_morph"
        return "intonation"
    if name == "passive":
        if _bern(rng, p("GB147", ("GB302",))):
            return "bound"
        return "periphrastic" if _bern(rng, p("GB302", ("GB147",))) else "none"
    if name == "comparative":   # (owner ruling 11-08, PW-1538 D: WALS 121A shares, not the Grambank-drawn aim)
        return _choice(rng, COMPARE_PRIOR)
    if name == "predicative_possession":
        if _bern(rng, p("GB250", ("GB252",))):
            return "have"
        return "locational" if _bern(rng, p("GB252", ("GB250",))) else "other"
    if name == "numeral_base":
        if _bern(rng, p("GB335", ("GB333",))):
            return "vigesimal"
        return "decimal" if _bern(rng, p("GB333", ("GB335",))) else "other"
    if name == "verb_agreement":
        pre, suf = _bern(rng, p("GB090", ("GB089",))), _bern(rng, p("GB089", ("GB090",)))
        return "both" if pre and suf else "prefix" if pre else "suffix" if suf else "none"
    if name == "object_agreement":
        if _bern(rng, p("GB093", ("GB094",))):
            return "suffix"
        return "prefix" if _bern(rng, p("GB094", ("GB093",))) else "none"
    if name == "causative":
        return "bound" if _bern(rng, p("GB155")) else "periphrastic"
    gb = next(iter(_implied_gb(name, "x")), None)
    if gb is None:
        return "no"
    return "yes" if _bern(rng, p(gb)) else "no"


def _derive(typ: Typology, inv=None) -> None:
    ov = typ.ov()
    if ov == "OV":
        hd = "final"
    elif ov == "VO":
        hd = "initial"
    else:
        a = typ.get("adposition")
        hd = "final" if a == "post" else "initial" if a == "pre" else ("final" if typ.get("genitive") == "GN" else "initial")
    typ["head_direction"] = hd
    if inv is not None:
        typ["tone"] = "yes" if getattr(inv, "tones", None) else "no"
    else:
        typ.setdefault("tone", "no")


def draw_typology(rng: np.random.Generator, table: Tables | None = None, inv=None) -> Typology:
    """Draw every feature in FEATURES order, each conditional on the ones before (WALS crosstabs on basic order for the
    word-order harmonies, Grambank lifts for the rest). `table=None` reads the data tables (built-in fallbacks if absent)."""
    T = table if table is not None else load_tables()
    typ = Typology()
    for name, _ in FEATURES:
        typ[name] = _draw_feature(rng, name, typ, T)
    _derive(typ, inv)
    return typ


def _cross_table(name: str, typ: Typology, T: Tables) -> dict[str, float] | None:
    """P(value | basic order) for a word-order harmony feature (WALS crosstab, else the fallback), None for the rest."""
    if name not in _FB_CROSS:
        return None
    return T.wals_cross.get(name, {}).get(typ.get("word_order", "free")) or _FB_CROSS[name][typ.ov()]


def _disharmony(name: str, typ: Typology, T: Tables) -> float:
    """Hazard multiplier for a harmony feature whose value the current basic order disfavours (1 for the rest)."""
    tab = _cross_table(name, typ, T)
    if not tab or "word_order" not in typ:
        return 1.0
    best = max(tab.values())
    if best <= 0:
        return 1.0
    return 1.0 + DISHARMONY * (1.0 - min(1.0, tab.get(typ.get(name), 0.0) / best))


def drift(rng: np.random.Generator, typ: Typology, n_generations: float, l2_share: float = 0.0,
          table: Tables | None = None, kyr: float | None = None, **kw) -> list[tuple[str, str, str]]:
    """Flip features at their stability-class hazard over n generations; a flip re-draws the value conditional on the rest
    (so harmonies re-assert themselves after a word-order change, faster for a disharmonic value: `_disharmony`). Adult L2 learners raise every hazard (x(1 + l2)) and pull
    re-drawn morphological features to their simplest value with probability l2/2. Mutates `typ`; returns the changes."""
    T = table if table is not None else load_tables()
    if "l2" in kw and not l2_share:
        l2_share = float(kw["l2"])
    if isinstance(typ, Grammar):   # lect.py hands the whole grammar: drift its typology and log the flips
        gr = typ
        ch = drift(rng, aims(gr), n_generations, l2_share, T)
        gr.events += [(kyr if kyr is not None else 0.0, f"typology {n}: {a} > {b}") for n, a, b in ch]
        if ch:
            _follow_syntax(gr, kyr or 0.0)
        realise(gr)
        return ch
    l2 = min(max(float(l2_share), 0.0), 1.0)
    changes = []
    for name, cls in FEATURES:
        lam = STABILITY[cls] * n_generations * (1.0 + l2) * _disharmony(name, typ, T)
        if lam <= 0 or rng.random() >= 1.0 - math.exp(-lam):
            continue
        old = typ.get(name)
        if name in SIMPLE_VALUE and rng.random() < 0.5 * l2:
            new = SIMPLE_VALUE[name]
        else:
            new = _draw_feature(rng, name, typ, T)
        if new != old:
            typ[name] = new
            changes.append((name, old, new))
    if changes:
        _derive(typ, None)
    return changes


# --------------------------------------------------------------------------------------------------------------------
# Grams, classes, exemplars
# --------------------------------------------------------------------------------------------------------------------


#: verbal reduplication (2026-11-07, grammar phase A): a process, not a gram on the ladder (no source word, no
#: erosion step: it copies part of the stem it stands on). One meaning per lect, its gloss code the cell key: iterative /
#: pluractional ('hit again and again', 'many hit': Hausa, Salish, Austronesian), intensive ('hit hard': Indonesian,
#: Turkish emphatics) or continuous ('be hitting': Tagalog contemplated aspect, Yoruba, Ewe). Rubino (WALS 27A): 278 of
#: 368 languages have productive full and partial reduplication, 35 full only, 55 none; partial copies are mostly
#: prefixed CV- (Tagalog ka-kain, Ilocano ag-sa-sangit)
REDUP = {"ITER": 0.45, "INTS": 0.20, "CONT": 0.35}
REDUP_SHAPE = {"CV": 0.65, "full": 0.35}
REDUP_INFO = {f: FuncInfo("V", "head", 0.8, "deriv", g) for f, g in
              (("ITER", "iterative (reduplication)"), ("INTS", "intensive (reduplication)"),
               ("CONT", "continuous (reduplication)"))}
REDUP_LOSS = 0.002   # per generation (x social loss) once the aims no longer want it


def func_info(function: str) -> FuncInfo:
    if "+" in function:   # (a portmanteau, grammar C: the outer component's slot and side, both glosses)
        a, b = function.split("+", 1)
        ia, ib = func_info(a), func_info(b)
        return FuncInfo(ib.host, ib.side_rule, min(ia.freq, ib.freq), ib.slot, f"{ia.gloss} and {ib.gloss}")
    if function.startswith("CLASS"):
        return CLASS_INFO
    if function in REDUP_INFO:
        return REDUP_INFO[function]
    return FUNCS[function]


def reduplicant(stem: Form, shape: str, side: str = "pre") -> Form:
    """The copied part of a stem: all of it ('full'), or its first consonants and vowel ('CV', prefixed: Tagalog
    kain > ka-kain), or its last consonants and vowel (a suffixed CV copy)."""
    stem = tuple(stem)
    if shape == "full" or not stem:
        return stem
    vs = [i for i, x in enumerate(stem) if _is_v(x)]
    if not vs:
        return stem[:1]
    if side == "pre":
        return stem[:vs[0] + 1]
    i = vs[-1]
    while i > 0 and not _is_v(stem[i - 1]):
        i -= 1
    return stem[i:vs[-1] + 1]


@dataclass
class Gram:
    function: str
    form: Form
    host: str
    side: str
    level: int = 0
    source: tuple = ("?", "proto", "unknown")     # (source, path id, kind): kind concept | gram | coin | unknown
    born_kyr: float = 0.0
    history: list[tuple[float, str]] = field(default_factory=list)
    age_gens: float = 0.0
    id: str = ""
    #: grammar C: the second inflection class's form of this marker (empty: one class); which words take it is
    #: `iclass_member(g.processes["iclass"][function], concept)`
    alt: Form = ()

    @property
    def live(self) -> bool:
        return self.level < LOST

    @property
    def info(self) -> FuncInfo:
        return func_info(self.function)


@dataclass
class NounClass:
    k: int
    group: str
    gram_id: str


@dataclass
class ClassSystem:
    kind: str                         # classes | sex | animacy | classifiers
    classes: list[NounClass] = field(default_factory=list)

    def groups(self) -> list[str]:
        return [c.group for c in self.classes]

    def by_group(self, group: str) -> NounClass | None:
        return next((c for c in self.classes if c.group == group), None)


@dataclass
class Exemplar:
    concept: str
    pos: str                          # N | V
    stem: Form
    cells: dict[tuple[str, ...], Form] = field(default_factory=dict)
    #: the same cells cut into morphs, outermost-left to outermost-right: (("stem", form), ("PL", form), ...)
    parts: dict[tuple[str, ...], tuple[tuple[str, Form], ...]] = field(default_factory=dict)

    def set(self, key: tuple[str, ...], parts: tuple[tuple[str, Form], ...]) -> None:
        self.parts[key] = tuple((lab, tuple(f)) for lab, f in parts)
        self.cells[key] = tuple(s for _, f in parts for s in f)

    def drop(self, key: tuple[str, ...]) -> None:
        self.cells.pop(key, None)
        self.parts.pop(key, None)

    def morph(self, key: tuple[str, ...], label: str) -> Form | None:
        return next((f for lab, f in self.parts.get(key, ()) if lab == label), None)


@dataclass
class Grammar:
    typology: Typology
    grams: list[Gram] = field(default_factory=list)
    exemplars: list[Exemplar] = field(default_factory=list)
    class_system: ClassSystem | None = None
    helpers: dict[str, tuple[str, Form]] = field(default_factory=dict)   # role -> (concept, form) for name building
    events: list[tuple[float, str]] = field(default_factory=list)
    _n: int = 0
    last_changed: list[str] = field(default_factory=list)
    #: the drifting typology (what the community's syntax leans toward); `typology` is what the grammar shows, the aims
    #: with every gram-realised feature read from the live grams (`realise`). None until first needed (= typology).
    aims: Typology | None = None
    #: the typology as `realise` last wrote it: a later outside write (a calque on shift) is read as a new aim
    shown: dict = field(default_factory=dict)
    #: built constructions and processes that are not grams on the ladder (2026-11-07, grammar phase A): "split" (how a
    #: split-ergative lect divides its alignment: "person" or "aspect"), "redup" (verbal reduplication: meaning, shape,
    #: side). Set and dropped in `_processes`; read by `realise`, the paradigm cells and the sample sentences.
    processes: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.typology, Shown):
            self.typology = Shown(self.typology)
        self.typology.__dict__["_g"] = self

    def live(self) -> list[Gram]:
        return [g for g in self.grams if g.live]

    def gram(self, function: str, bound: bool = False) -> Gram | None:
        """The gram for a function: the youngest bound one (level 2-3) if any, else (unless `bound`) the youngest live."""
        cands = [g for g in self.grams if g.live and g.function == function]
        b = [g for g in cands if g.level >= AFFIX]
        if b:
            return min(b, key=lambda g: g.age_gens)
        if bound or not cands:
            return None
        return min(cands, key=lambda g: g.age_gens)

    def by_id(self, gid: str) -> Gram | None:
        return next((g for g in self.grams if g.id == gid), None)

    def new_id(self, function: str) -> str:
        self._n += 1
        return f"{function}#{self._n}"

    def bound(self, pos: str) -> list[Gram]:
        """Live grams at level >= 2 whose host is a noun (N/NP) or verb (V/VP), one per function (youngest)."""
        out = {}
        for g in self.grams:
            if g.live and g.level >= AFFIX and g.host[0] == pos[0]:
                cur = out.get(g.function)
                if cur is None or g.age_gens < cur.age_gens:
                    out[g.function] = g
        return list(out.values())

    def host_forms(self) -> list[tuple[str, Form]]:
        """Every stored form the driver's sound change must reach: gram forms, exemplar stems and cells, helper forms."""
        out = [(f"gram:{g.id}", g.form) for g in self.grams if g.live]
        out += [(f"alt:{g.id}", g.alt) for g in self.grams if g.live and g.alt]
        for ex in self.exemplars:
            out.append((f"stem:{ex.concept}", ex.stem))
            out += [(f"cell:{ex.concept}:{'.'.join(k)}", f) for k, f in ex.cells.items()]
        out += [(f"helper:{r}", f) for r, (_, f) in self.helpers.items()]
        return out


def copy(g: Grammar) -> Grammar:
    """A daughter's grammar (budding): deep enough that the two evolve apart (Segments are immutable and shared)."""
    return Grammar(
        typology=Typology(g.typology),
        grams=[dataclasses.replace(x, history=list(x.history)) for x in g.grams],
        exemplars=[Exemplar(e.concept, e.pos, e.stem, dict(e.cells), dict(e.parts)) for e in g.exemplars],
        class_system=None if g.class_system is None else ClassSystem(
            g.class_system.kind, [dataclasses.replace(c) for c in g.class_system.classes]),
        helpers=dict(g.helpers), events=[], _n=g._n,
        aims=None if g.aims is None else Typology(g.aims), shown=dict(g.shown),
        processes=_copy.deepcopy(g.processes))


def _side(function: str, typ: Typology, rng: np.random.Generator | None = None) -> str:
    """Where a new gram stands: affixes arise where their source word stood (Givon: today's morphology is yesterday's
    syntax)."""
    rule = func_info(function).side_rule
    hf = typ.head_final()
    if rule == "dem":
        v = typ.get("demonstrative", "DemN")
        return "pre" if v == "DemN" else "post" if v == "NDem" else ("post" if hf else "pre")
    if rule == "num":
        v = typ.get("numeral", "NNum")
        return "pre" if v == "NumN" else "post" if v == "NNum" else ("post" if hf else "pre")
    if rule == "adp":
        v = typ.get("adposition", "post")
        return "pre" if v == "pre" else "post"   # none/mixed: the suffixing preference
    if rule == "aux":
        return "post" if typ.ov() == "OV" or (typ.ov() == "free" and hf) else "pre"
    if rule == "head":
        return "post" if hf else "pre"
    if rule == "neg":
        v = typ.get("negation", "preverbal")
        return "pre" if v in ("preverbal", "clause_initial") else "post"
    if rule == "oagr":
        v = typ.get("object_agreement", "none")
        if v in ("prefix", "suffix"):
            return "pre" if v == "prefix" else "post"
        rule = "agr"
    if rule == "q":   # (a question particle stands where the aims put it; a verbal one with the auxiliaries)
        v = typ.get("polar_question", "final_particle")
        if v == "initial_particle":
            return "pre"
        if v == "verb_morph":
            rule = "aux"
        else:
            return "post"
    if rule == "rel":   # (a relativizer stands between noun and clause: before a following clause, after a preceding)
        return "post" if typ.get("relative") == "RelN" else "pre"
    if rule == "comp":  # (complementizers and clause-linkers: clause-final in head-final lects, Japanese to; else initial)
        return "post" if hf else "pre"
    if rule == "gen":   # (a possessor affix forms where the possessive pronoun stood: GN before the noun)
        v = typ.get("genitive", "GN")
        return "pre" if v == "GN" else "post" if v == "NG" else ("pre" if hf else "post")
    if rule == "agr":
        v = typ.get("verb_agreement", "none")
        if v == "prefix":
            return "pre"
        if v == "suffix":
            return "post"
        wo = typ.get("word_order", "SOV")
        return "post" if typ.ov() == "OV" or wo.startswith("V") else "pre"
    return "post"


def _wanted(function: str, typ: Typology) -> bool:
    """Does the typology (the community's syntax) favour marking this function?"""
    t = typ.get
    f = function
    if f.startswith("CLASS"):
        return t("gender", "none") != "none" or t("numeral_classifiers") == "yes"
    table = {
        "PL": t("number") != "none", "DU": t("number") == "sg-du-pl", "DEF": t("definite_article") != "none",
        "INDEF": t("indefinite_article") == "present", "GEN": t("case") != "none", "LOC": t("case") != "none",
        "DAT": t("case") != "none", "ABL": t("case") == "many", "ALL": t("case") == "many", "INS": t("case") == "many",
        "COM": t("case") == "many", **{x: t("case") == "many" for x in LOCAL_CASE + PERIPHERAL_CASE},
        "ACC": t("case") != "none" and t("alignment") in ("nom-acc", "split"),
        "ERG": t("case") != "none" and t("alignment") in ("erg-abs", "split"),
        "PAST": t("past") == "marked", "RECPST": t("past") == "marked", "FUT": t("future") == "marked", "PERF": t("perfective") == "marked",
        "IPFV": t("perfective") == "marked", "PROG": t("progressive") == "marked", "HAB": t("habitual") == "marked",
        "EVID.DIR": t("evidentiality") == "direct+indirect", "EVID.REP": t("evidentiality") != "none",
        "NEG": True, "CAUS": t("causative") == "bound", "PASS": t("passive") != "none", "REFL": True,
        "DIM": t("diminutive") == "yes", "AGENT": t("agent_noun") == "yes", "PLACE": True,
    }
    if f in table:
        return bool(table[f])
    if f in OBJ_FNS:
        return t("object_agreement", "none") != "none"
    if f in POSS_FNS or f in MOOD_FNS:
        return True   # (no typology feature asks for them: they come and go with the ordinary draw)
    # grammar phase C: constructions as grams, valence, switch-reference, symmetrical voice
    if f == "Q":
        return t("polar_question", "intonation") != "intonation"
    if f == "COP":
        return t("copula") == "yes"
    if f == "REL":
        return t("relative") != "RelN"   # (prenominal relatives mostly take no relativizer: participles, nominalizers)
    if f == "ANTIP":
        return t("alignment") in ("erg-abs", "split")   # (WALS 108A: antipassives are nearly all in ergative languages)
    if f in ("SS", "DS"):
        return typ.ov() == "OV"   # (switch-reference: overwhelmingly verb-final clause-chaining languages; Haiman & Munro)
    if f in ("AV", "PV"):
        return t("word_order", "SOV") in ("VSO", "VOS")   # (Philippine-type voice: verb-initial Austronesian)
    # grammar phase D
    if f == "REMPST":
        return t("past") == "marked"
    if f == "HON":
        return t("politeness", "none") != "none"   # (an honorific verb marker only in a language with polite address)
    if f == "OBV":   # (obviation: head-marking languages that index two third persons on the verb; Algonquian, Kutenai)
        return t("object_agreement", "none") != "none" and t("verb_agreement", "none") != "none"
    if f[0] in "123":
        return t("verb_agreement", "none") != "none" or t("pro_drop") == "yes"
    return True


# --------------------------------------------------------------------------------------------------------------------
# Typology from the grams (the 2026-11-04 "typology and grams" round)
# --------------------------------------------------------------------------------------------------------------------
# Two layers, one system. `Grammar.aims` is the drifting typology (`drift`, calibrated per stability class): what the
# community's syntax leans toward. It steers the ladder: `_wanted` (recruitment weight, abandonment) and `_side` read it,
# a flip toward marking raises the recruitment of a matching gram (PRESSURE), a flip to 'none' lets the bound grams
# erode (UNWANTED_LOSS). `Grammar.typology` is what the grammar does: the aims, with every feature a gram realises read
# from the live grams (`realise`), so a page never says "no grammatical number" above a plural suffix. A gram the aims did
# not want that binds anyway becomes grammar: the aim takes the bound category (`_adopt`). Order features keep drifting as
# before; free words (level 0) follow the syntax to the new side, bound morphology stays where it formed (Givon 1971).

#: features a gram realises (the typology value is read from the live grams), and the functions behind each
REALISED = ("definite_article", "indefinite_article", "case", "alignment", "number", "gender", "past", "future",
            "perfective", "progressive", "habitual", "evidentiality", "negation", "numeral_classifiers", "clusivity",
            "causative", "passive", "diminutive", "agent_noun", "verb_agreement", "object_agreement",
            "verb_reduplication", "polar_question", "copula")
#: order features the free grams constrain (a free locative postposition means the language has postpositions)
CONSTRAINED = ("adposition",)
LOCAL_CASE = ("INE", "ILL", "ELA", "SUPE", "SUBL", "DEL")   # (PW-1569: the local series, `_local_series`)
PERIPHERAL_CASE = ("PERL", "PRIV", "TRANSL")
CASE_FNS = ("GEN", "LOC", "ABL", "ALL", "DAT", "ACC", "ERG", "INS", "COM") + LOCAL_CASE + PERIPHERAL_CASE
RICH_CASE = ("ABL", "ALL", "INS", "COM")   # the oblique cases `_wanted` asks of a 'many' case system (with the local and
#                                            peripheral ones, which pull as groups of their own: `PULL_GROUP`)
#: the region markers of the local series and the members each makes with a directional case (`_local_series`)
LOCAL_SERIES = {"INE": {"ALL": "ILL", "ABL": "ELA"}, "SUPE": {"ALL": "SUBL", "ABL": "DEL"}}
LOCAL_FORM = 0.01     # per generation: a missing member forms while its region marker and directional case are bound
CASE_MANY = 6         # cases (bound case markers + 1, WALS 49A) from which the 'case' label reads 'many'
PERSON_FNS = ("1SG", "2SG", "3SG", "1PL", "2PL", "3PL")
INCL_FN = "1PL.INCL"
OBJ_FNS = tuple(f"{p}.O" for p in PERSON_FNS)
POSS_FNS = tuple(f"{p}.POSS" for p in PERSON_FNS)
MOOD_FNS = ("IMP", "HORT", "OBLG", "APPR")
#: the person series that bind as sets: subject agreement (with the inclusive 'we' when the lexicon has one), object
#: agreement on the verb, possessor marking on the noun
SERIES = {"S": PERSON_FNS + (INCL_FN,), "O": OBJ_FNS, "P": POSS_FNS}
SERIES_OF = {f: k for k, fs in SERIES.items() for f in fs}
_TAM = {"past": ("PAST", "RECPST", "REMPST"), "future": ("FUT",), "perfective": ("PERF", "IPFV"), "progressive": ("PROG",),
        "habitual": ("HAB",)}
_PRE_NEG = ("preverbal", "clause_initial")
#: the inclusive and exclusive 'we' concepts; the clusivity feature is 'yes' only when the lexicon holds both, apart
CLUSIVE = ("WE (INCLUSIVE)", "WE (EXCLUSIVE)")


def feature_of(function: str) -> tuple[str, ...]:
    """The typology features a gram function realises."""
    f = function
    if f.startswith("CLASS"):
        return ("gender", "numeral_classifiers")
    if f in ("PL", "DU"):
        return ("number",)
    if f == "DEF":
        return ("definite_article",)
    if f == "INDEF":
        return ("indefinite_article",)
    if f in ("ACC", "ERG"):
        return ("case", "alignment")
    if f in CASE_FNS:
        return ("case",)
    for feat, fns in _TAM.items():
        if f in fns:
            return (feat,)
    if f.startswith("EVID"):
        return ("evidentiality",)
    if f == "NEG":
        return ("negation",)
    if f in PERSON_FNS or f == INCL_FN:
        return ("verb_agreement",)
    if f in OBJ_FNS:
        return ("object_agreement",)
    if f == "Q":
        return ("polar_question",)
    if f == "COP":
        return ("copula",)
    return {"CAUS": ("causative",), "PASS": ("passive",), "DIM": ("diminutive",), "AGENT": ("agent_noun",)}.get(f, ())


def aims(g: Grammar) -> Typology:
    """The grammar's drifting typology (set from the shown one the first time it is asked for)."""
    if g.aims is None:
        g.aims = Typology(g.typology)
        g.shown = dict(g.typology)
    return g.aims


def _live_fns(g: Grammar) -> dict[str, list[Gram]]:
    out: dict[str, list[Gram]] = {}
    for gr in g.grams:
        if gr.live:
            out.setdefault(gr.function, []).append(gr)
    return out


def _adp_sides(lv: dict[str, list[Gram]]) -> set[str]:
    """Sides of the free and clitic case markers (adpositions; a bound case affix says nothing about adposition order)."""
    return {x.side for f in CASE_FNS for x in lv.get(f, ()) if x.level <= CLITIC}


def _class_state(g: Grammar) -> tuple[str, str]:
    """(gender, numeral_classifiers) from the class system: free classifier nouns are classifiers; once a class marker
    has bound (clitic or tighter) the system is gender of its kind (classifiers grown into noun classes, as in Bantu)."""
    cs = g.class_system
    grams = [x for c in (cs.classes if cs else ()) if (x := g.by_id(c.gram_id)) is not None and x.live]
    if not grams:
        return "none", "no"
    if any(x.level >= CLITIC for x in grams):
        return ("classes" if cs.kind == "classifiers" else cs.kind), "no"
    return "none", "yes"


def _clusive(lexicon) -> str | None:
    """'yes' when the lexicon holds an inclusive 'we' apart from the exclusive one (the exclusive is plain WE unless a
    WE (EXCLUSIVE) entry exists: a lect that grows the distinction keeps its old 'we' as the exclusive)."""
    if lexicon is None:
        return None
    a = _lex_get(lexicon, CLUSIVE[0])
    b = _lex_get(lexicon, CLUSIVE[1])
    if b is None:
        b = _lex_get(lexicon, "WE")
    return "yes" if a is not None and b is not None and _form(a) != _form(b) else "no"


def case_count(g: Grammar, lv: dict | None = None) -> int:
    """Cases as WALS 49A counts them: the bound (affix or fused) case markers + 1 for the unmarked case; 0 with none."""
    lv = _live_fns(g) if lv is None else lv
    n = sum(1 for x in CASE_FNS if any(m.level >= AFFIX for m in lv.get(x, ())))
    return n + 1 if n else 0


def case_bin(g: Grammar, lv: dict | None = None) -> str:
    """The WALS 49A bin of `case_count`: none | borderline (case clitics only) | 2 | 3 | 4 | 5 | 6-7 | 8-9 | 10+."""
    lv = _live_fns(g) if lv is None else lv
    n = case_count(g, lv)
    if not n:
        return "borderline" if any(m.level == CLITIC for x in CASE_FNS for m in lv.get(x, ())) else "none"
    return str(n) if n <= 5 else "6-7" if n <= 7 else "8-9" if n <= 9 else "10+"


def realised_value(feature: str, g: Grammar, lexicon=None, lv: dict | None = None) -> str:
    """The value the live grams (or the lexicon, for clusivity) give a realised feature, nearest to the aim where the
    grams leave a choice (negation: which side-compatible value; alignment and negation with no marker: the aim)."""
    lv = _live_fns(g) if lv is None else lv
    a = aims(g)
    aim = a.get(feature)
    has = lambda *fs: any(f in lv for f in fs)  # noqa: E731
    f = feature
    if f == "number":
        return "sg-du-pl" if has("DU") else "sg-pl" if has("PL") else "none"
    if f == "definite_article":
        d = g.gram("DEF")
        return d.side if d is not None else "none"
    if f == "indefinite_article":
        return "present" if has("INDEF") else "none"
    if f == "case":
        # (WALS 49 counts inflectional case: a free case-function gram is an adposition, case only from clitic level on;
        # PW-1569: 'many' by count, CASE_MANY cases or more, as WALS 49A's 6-7 / 8-9 / 10+ bins; clitic-only case,
        # WALS's 'borderline', reads 'few')
        cs = [x for x in CASE_FNS if any(m.level >= CLITIC for m in lv.get(x, ()))]
        if not cs:
            return "none"
        return "many" if case_count(g, lv) >= CASE_MANY else "few"
    if f == "alignment":
        # (of flagging, as WALS 98A: no accusative or ergative marker is neutral alignment, whatever the aims lean to;
        # before 2026-11-07 the aim showed through, so 16% of lects were 'ergative' with no ergative anywhere)
        acc, erg = has("ACC"), has("ERG")
        return "split" if acc and erg else "nom-acc" if acc else "erg-abs" if erg else "neutral"
    if f in _TAM:
        return "marked" if has(*_TAM[f]) else "none"
    if f == "evidentiality":
        return "direct+indirect" if has("EVID.DIR") else "indirect" if has("EVID.REP") else "none"
    if f == "negation":
        n = g.gram("NEG")
        if n is None:
            return aim
        if n.side == "pre":
            return aim if aim in _PRE_NEG else "preverbal"
        return aim if aim not in _PRE_NEG else "postverbal"
    if f == "verb_agreement":
        sides = {x.side for p in SERIES["S"] for x in lv.get(p, ()) if x.level >= CLITIC}
        return "both" if len(sides) > 1 else "prefix" if "pre" in sides else "suffix" if sides else "none"
    if f == "object_agreement":   # (Grambank GB093/GB094: a bound object marker on the verb; both sides read as the aim)
        sides = {x.side for p in OBJ_FNS for x in lv.get(p, ()) if x.level >= CLITIC}
        if not sides:
            return "none"
        if len(sides) > 1:
            return aim if aim in ("prefix", "suffix") else "suffix"
        return "prefix" if "pre" in sides else "suffix"
    if f == "gender":
        return _class_state(g)[0]
    if f == "numeral_classifiers":
        return _class_state(g)[1]
    if f == "clusivity":
        c = _clusive(lexicon)
        return c if c is not None else g.shown.get("clusivity", "no")   # (no lexicon at hand: the last verdict)
    if f == "causative":
        return "bound" if any(x.level >= AFFIX for x in lv.get("CAUS", ())) else "periphrastic"
    if f == "passive":
        ps = lv.get("PASS", ())
        return "bound" if any(x.level >= AFFIX for x in ps) else "periphrastic" if ps else "none"
    if f == "diminutive":
        return "yes" if has("DIM") else "no"
    if f == "agent_noun":
        return "yes" if has("AGENT") else "no"
    if f == "verb_reduplication":
        return "yes" if g.processes.get("redup") else "no"
    if f == "polar_question":   # (grammar C: a free or clitic particle by its side, a bound one is verbal morphology)
        q = g.gram("Q")
        if q is None:
            return "intonation"
        if q.level >= AFFIX:
            return "verb_morph"
        return "initial_particle" if q.side == "pre" else "final_particle"
    if f == "copula":
        return "yes" if has("COP") else "no"
    if f == "adposition":
        s = _adp_sides(lv)
        if not s:
            return aim
        if len(s) > 1:
            return "mixed"
        side = next(iter(s))
        return aim if aim in (side, "mixed") else side
    return aim


def consistent(feature: str, value, g: Grammar, lexicon=None, lv: dict | None = None) -> bool:
    """Does a typology value agree with the live grams? (alignment: the live ACC and ERG fix it, neutral with neither; negation:
    the side of the main negator; adposition: the sides of the free and clitic case markers; clusivity: two distinct
    'we' forms in the lexicon, or the last verdict when no lexicon is at hand)."""
    lv = _live_fns(g) if lv is None else lv
    if feature == "negation":
        n = g.gram("NEG")
        return n is None or (value in _PRE_NEG) == (n.side == "pre")
    if feature == "adposition":
        s = _adp_sides(lv)
        return not s or value == "mixed" or (len(s) == 1 and value in s)
    return value == realised_value(feature, g, lexicon, lv)


def clashes(g: Grammar, lexicon=None) -> list[str]:
    """Every shown typology feature the live grams contradict ('number: none' with a live plural): empty when the two
    layers agree. The language pass counts these in its checks (`checks.typology_consistency`)."""
    lv = _live_fns(g)
    out = []
    for f in REALISED + CONSTRAINED:
        v = g.typology.get(f)
        if v is not None and not consistent(f, v, g, lexicon, lv):
            out.append(f"{f}: {v} (the grams give {realised_value(f, g, lexicon, lv)})")
    return out


def realise(g: Grammar, lexicon=None) -> Typology:
    """Write the shown typology: the aims, with each realised feature the aim where the grams agree and the grams' value
    where they do not. A value written into `g.typology` from outside since the last call (a calque on shift) first
    becomes the aim. Mutates and returns `g.typology`."""
    a = aims(g)
    for k, v in list(g.typology.items()):
        if g.shown.get(k, None) != v and (k in g.shown or k not in a):
            a[k] = v
    lv = _live_fns(g)
    new = {}
    for k, v in a.items():
        if k == "clusivity" and lexicon is None and k in g.shown:
            new[k] = g.shown[k]   # (no lexicon to look in: keep the last verdict)
        elif k in REALISED or k in CONSTRAINED:
            new[k] = v if consistent(k, v, g, lexicon, lv) else realised_value(k, g, lexicon, lv)
        else:
            new[k] = v
    g.typology.clear()
    g.typology.update(new)
    g.shown = dict(new)
    return g.typology


def _adopt(g: Grammar, gr: Gram, kyr: float) -> None:
    """An unwanted gram that bound anyway is grammar now: the aims take the category it realises."""
    a = aims(g)
    lv = _live_fns(g)
    for feat in feature_of(gr.function):
        v = realised_value(feat, g, None, lv)
        if a.get(feat) != v:
            g.events.append((kyr, f"typology {feat}: {a.get(feat)} > {v} (the {gr.info.gloss} marker bound)"))
            a[feat] = v


_PULL_FNS = tuple(FUNCS) + ("CLASS",)


#: the pull groups: functions that answer one demand of the aims together. A function not listed answers its feature
#: (`feature_of(fn)[0]`) with every other function of that feature, so any case gram answers 'case: few' and PAST or
#: RECPST answers 'past: marked'; the listed ones are demands of their own: an accusative or ergative answers the
#: alignment (a locative does not), a dual the 'sg-du-pl' number (a plural does not), an oblique case 'case: many', a
#: witnessed evidential 'direct+indirect'. Before 2026-11-07 every function was grouped by its first feature, so any
#: case gram blocked the pull toward ACC/ERG, a plural blocked DU and a reportative blocked the direct evidential.
PULL_GROUP = {"ACC": "alignment:ACC", "ERG": "alignment:ERG", "DU": "number:DU", "EVID.DIR": "evidentiality:DIR",
              # (PW-1569: a 'many' case system asks for the allative and the ablative each on its own, and for a region
              # marker, the parts the local series is built from; the instrumental and comitative answer together, and
              # so do the peripheral cases)
              **{f: "case:rich" for f in RICH_CASE}, "ALL": "case:ALL", "ABL": "case:ABL",
              **{f: "case:local" for f in LOCAL_CASE}, **{f: "case:periph" for f in PERIPHERAL_CASE},
              "GEN": "case:GEN"}   # (grammar B: a language with case marks the possessor too, nearly always: WALS 51A)


def pull_group(fn: str) -> str:
    if fn.startswith("CLASS"):
        return "gender"
    return PULL_GROUP.get(fn) or (feature_of(fn) or ("",))[0]


def _unrealised(g: Grammar, a: Typology) -> dict[str, set[str]]:
    """Pull group -> the functions the aims want for it, for each demand of the aims no live gram answers yet (the
    categories a typology flip asked for and the ladder has not yet supplied; `PULL_GROUP`)."""
    lv = _live_fns(g)
    has_class = g.class_system is not None and any(
        (x := g.by_id(c.gram_id)) is not None and x.live for c in g.class_system.classes)
    answered = {pull_group(fn) for fn in lv} | {feature_of(fn)[0] for fn in lv if feature_of(fn)}
    if has_class:
        answered.add("gender")
    out: dict[str, set[str]] = {}
    for fn in _PULL_FNS:
        if not feature_of(fn) or fn == "NEG" or not _wanted(fn, a):
            continue
        grp = pull_group(fn)
        if grp in answered:
            continue
        out.setdefault(grp, set()).add(fn)
    return out


def _follow_syntax(g: Grammar, kyr: float) -> None:
    """After an order change, free grams (separate words) stand where the syntax now puts them; clitics and affixes stay
    on the side they fused on (yesterday's syntax, Givon 1971)."""
    a = aims(g)
    for gr in g.grams:
        if gr.live and gr.level == FREE:
            side = _side(gr.function, a)
            if side != gr.side:
                gr.side = side
                gr.history.append((kyr, f"now {'before' if side == 'pre' else 'after'} its host (word order)"))


# --------------------------------------------------------------------------------------------------------------------
# Lexicon access (duck-typed: dict-like concept -> Word with .form .pos .freq_class)
# --------------------------------------------------------------------------------------------------------------------


def _lex_get(lexicon, concept):
    if lexicon is None:
        return None
    try:
        return lexicon[concept] if concept in lexicon else None
    except (KeyError, TypeError):
        return None


def _lex_keys(lexicon) -> Iterable:
    words = getattr(lexicon, "words", None)
    if isinstance(words, dict):
        return words.keys()
    return lexicon.keys()


def _lex_index(lexicon) -> dict[str, str]:
    """upper-case gloss (and gloss without its parenthesis) -> lexicon key."""
    idx: dict[str, str] = {}
    if lexicon is None:
        return idx
    for k in list(_lex_keys(lexicon)):
        u = str(k).upper()
        idx.setdefault(u, k)
        base = u.split(" (")[0].strip()
        idx.setdefault(base, k)
    return idx


def _find(lexicon, idx: dict[str, str], cands: Iterable[str]):
    for c in cands:
        key = idx.get(c.upper())
        if key is not None:
            w = _lex_get(lexicon, key)
            if w is not None and len(_form(w)) > 0:
                return key, w
    return None, None


def _draw_morph(rng, inv) -> Form:
    try:
        from planet.language.inventory import draw_word  # noqa: PLC0415
        return tuple(draw_word(rng, inv, 1))
    except Exception:  # noqa: BLE001 - inventory not available: build a CV from the inventory lists if it has them
        cs = list(getattr(inv, "consonants", []) or [])
        vs = list(getattr(inv, "vowels", []) or [])
        if cs and vs:
            return (cs[int(rng.integers(len(cs)))], vs[int(rng.integers(len(vs)))])
        return ()


# --------------------------------------------------------------------------------------------------------------------
# Cells
# --------------------------------------------------------------------------------------------------------------------


def _slot_rank(function: str) -> int:
    return SLOT_ORDER.index(func_info(function).slot)


def _cell_keys(ex: Exemplar, g: Grammar) -> list[tuple[str, ...]]:
    """Which cells an exemplar carries: one per bound gram on its host, plus number x case (nouns) and aspect/tense x
    person and negative x tense (verbs) pairs. Class markers apply only for the noun's own class."""
    bound = g.bound(ex.pos)
    own_class = None
    if ex.pos == "N" and g.class_system is not None:
        own_class = _class_for(g, ex.concept)
    fns = []
    for gr in bound:
        if gr.function.startswith("CLASS"):
            if own_class is not None and gr.id == own_class.gram_id:
                fns.append(gr.function)
        elif gr.info.slot != "deriv" and "+" not in gr.function:
            fns.append(gr.function)
    fns.sort(key=lambda f: (_slot_rank(f), f))
    keys = [(f,) for f in fns]
    by_slot: dict[str, list[str]] = {}
    for f in fns:
        by_slot.setdefault(func_info(f).slot, []).append(f)
    pairs = []
    if ex.pos == "N":
        pairs = [(a, b) for a in by_slot.get("number", [])[:1] for b in by_slot.get("case", [])[:3]]
        pairs += [(a, b) for a in by_slot.get("class", []) for b in by_slot.get("number", [])[:1]]
    else:
        tam = (by_slot.get("aspect", []) + by_slot.get("tense", []))[:2]
        pairs = [(a, b) for a in tam for b in by_slot.get("person", [])[:3]]
        pairs += [(a, b) for a in tam[:1] for b in by_slot.get("polarity", [])]
    for a, b in pairs:
        keys.append(tuple(sorted((a, b), key=lambda f: (_slot_rank(f), f))))
    rd = g.processes.get("redup")
    if ex.pos == "V" and rd:
        keys.append((rd["fn"],))
    return keys


def _gram_for(g: Grammar, function: str) -> Gram | None:
    return g.gram(function, bound=True)


def build_parts(ex: Exemplar, key: tuple[str, ...], g: Grammar) -> tuple[tuple[str, Form], ...]:
    """The regular (agglutinative) morphs of a cell from today's lemma and gram forms: what analogy restores."""
    parts: list[tuple[str, Form]] = [("stem", tuple(ex.stem))]
    pm = {tuple(x.function.split("+")): x for x in g.grams if x.live and "+" in x.function}
    done: set = set()
    infix = None
    for f in key:  # key is inner-first
        if f in done:
            continue
        pair = next(((a, b) for (a, b) in pm if f in (a, b) and a in key and b in key), None)
        if pair is not None:   # (a portmanteau stands for both, on the outer one's side)
            done.update(pair)
            x = pm[pair]
            item = ("+".join(pair), tuple(gram_form(g, x, ex.concept)))
            parts.insert(0, item) if x.side == "pre" else parts.append(item)
            continue
        if f in REDUP_INFO:
            rd = g.processes.get("redup")
            if rd and rd["fn"] == f:
                red = reduplicant(ex.stem, rd["shape"], rd["side"])
                if rd["side"] == "pre":
                    parts.insert(0, (f, red))
                else:
                    parts.append((f, red))
            continue
        gr = _gram_for(g, f)
        if gr is None:
            continue
        form = tuple(gram_form(g, gr, ex.concept))
        if (g.processes.get("infix") or {}).get("fn") == f and gr.side == "pre":
            infix = (f, form)
            continue
        if gr.side == "pre":
            parts.insert(0, (f, form))
        else:
            parts.append((f, form))
    if infix is not None:   # (after the stem's first consonants: Tagalog s<um>ulat; a vowel-initial stem takes a prefix)
        si = next(i for i, (lab, _) in enumerate(parts) if lab == "stem")
        stem = parts[si][1]
        k = onset_len(stem)
        parts[si:si + 1] = ([("stem", stem[:k]), infix, ("stem", stem[k:])] if 0 < k < len(stem) else [infix, parts[si]])
    return tuple(parts)


def onset_len(stem: Form) -> int:
    """How many segments stand before the stem's first vowel."""
    return next((i for i, x in enumerate(stem) if _is_v(x)), len(stem))


def iclass_member(ic: dict | None, concept) -> bool:
    """Does a word belong to a marker's second inflection class? Lexically arbitrary and fixed (a stable hash of the
    concept and the split's salt; never the str hash), as German plural or Latin declension classes are once the stem
    shapes that first conditioned them have changed."""
    if not ic or concept is None:
        return False
    return zlib.crc32(f"{concept}|{ic['salt']}".encode()) % 1000 < int(1000 * ic["share"])


def gram_form(g: Grammar, gr: Gram, concept=None) -> Form:
    """The marker's form on a given word: its second-class form for the words of that class."""
    if gr.alt and iclass_member((g.processes.get("iclass") or {}).get(gr.function), concept):
        return tuple(gr.alt)
    return tuple(gr.form)


def rebuild(ex: Exemplar, key: tuple[str, ...], g: Grammar) -> Form:
    """The regular form of a cell (concatenation of `build_parts`)."""
    return tuple(s for _, f in build_parts(ex, key, g) for s in f)


def _irregular(ex: Exemplar, key: tuple[str, ...], g: Grammar) -> bool:
    return ex.parts.get(key) != build_parts(ex, key, g)


def _align_cuts(old: Form, new: Form, cuts: list[int]) -> list[int]:
    """Carry morph boundaries through a sound change: align input and output (edit distance; same-kind substitutions
    cheap) and map each cut in `old` to a cut in `new`. Insertions at a boundary go to the morph on the left. Fast path:
    trim the common prefix and suffix and align only the changed middle."""
    n, m = len(old), len(new)
    p = 0
    while p < n and p < m and old[p] == new[p]:
        p += 1
    q = 0
    while q < n - p and q < m - p and old[n - 1 - q] == new[m - 1 - q]:
        q += 1
    if n == m:
        return list(cuts)          # same length (substitutions): boundaries stay put
    mid = [c for c in cuts if p < c < n - q]
    if not mid:
        return [c if c <= p else c + (m - n) for c in cuts]
    inner = _align_dp(old[p:n - q], new[p:m - q], [c - p for c in mid])
    out, k = [], 0
    for c in cuts:
        if c <= p:
            out.append(c)
        elif c >= n - q:
            out.append(c + (m - n))
        else:
            out.append(inner[k] + p)
            k += 1
    return out


def _align_dp(old: Form, new: Form, cuts: list[int]) -> list[int]:
    n, m = len(old), len(new)
    INF = 1e9
    D = np.full((n + 1, m + 1), INF)
    D[0, :] = np.arange(m + 1)
    D[:, 0] = np.arange(n + 1)
    for i in range(1, n + 1):
        a = old[i - 1]
        for j in range(1, m + 1):
            b = new[j - 1]
            sub = 0.0 if a == b else (0.6 if getattr(a, "kind", "") == getattr(b, "kind", "") else 1.4)
            D[i, j] = min(D[i - 1, j - 1] + sub, D[i - 1, j] + 1.0, D[i, j - 1] + 1.0)
    # backtrace to a list of (i_consumed, j_consumed) steps
    i, j, ops = n, m, []
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            a, b = old[i - 1], new[j - 1]
            sub = 0.0 if a == b else (0.6 if getattr(a, "kind", "") == getattr(b, "kind", "") else 1.4)
            if D[i, j] == D[i - 1, j - 1] + sub:
                ops.append((1, 1)); i -= 1; j -= 1; continue  # noqa: E702
        if i > 0 and D[i, j] == D[i - 1, j] + 1.0:
            ops.append((1, 0)); i -= 1; continue  # noqa: E702
        ops.append((0, 1)); j -= 1  # noqa: E702
    ops.reverse()
    out, i, j, ci = [], 0, 0, 0
    cuts = sorted(cuts)
    for di, dj in ops:
        while ci < len(cuts) and cuts[ci] == i and di == 1:
            out.append(j)
            ci += 1
        i += di
        j += dj
    while ci < len(cuts):
        out.append(j)
        ci += 1
    return out


def _resplit(parts: tuple[tuple[str, Form], ...], new: Form) -> tuple[tuple[str, Form], ...]:
    old = tuple(s for _, f in parts for s in f)
    cuts, c = [], 0
    for _, f in parts[:-1]:
        c += len(f)
        cuts.append(c)
    nc = _align_cuts(old, new, cuts)
    bounds = [0, *nc, len(new)]
    out = [[lab, list(new[bounds[k]:bounds[k + 1]])] for k, (lab, _) in enumerate(parts)]
    # a morph that was empty (an affix worn to nothing) stays empty: a segment a rule inserts at its edge (epenthesis,
    # prothesis) belongs to the neighbour on the stem's side, never to a zero affix that would thereby come back to life
    si = next((k for k, (lab, _) in enumerate(parts) if lab == "stem"), 0)
    for k, (lab, f) in enumerate(parts):
        if not f and out[k][1] and k != si:
            d = -1 if k > si else 1
            j = k + d
            while j != si and not parts[j][1]:
                j += d   # the nearest morph toward the stem that is not itself a zero
            if k > si:
                out[j][1] = out[j][1] + out[k][1]
            else:
                out[j][1] = out[k][1] + out[j][1]
            out[k][1] = []
    return tuple((lab, tuple(f)) for lab, f in out)


def _sync_cells(g: Grammar) -> None:
    """Add cells for newly bound grams, drop cells whose function has no live gram."""
    for ex in g.exemplars:
        want = set(_cell_keys(ex, g))
        for k in list(ex.cells):
            if k not in want:
                ex.drop(k)
        for k in sorted(want):  # a set: sorted for determinism across processes
            if k not in ex.cells:
                ex.set(k, build_parts(ex, k, g))


# --------------------------------------------------------------------------------------------------------------------
# Class systems
# --------------------------------------------------------------------------------------------------------------------

_LIQUIDS = {"WATER", "BLOOD", "MILK", "RAIN (PRECIPITATION)", "SEA", "BEER", "OIL", "FAT (ORGANIC SUBSTANCE)", "URINE",
            "SALT", "SAND", "ASH", "SMOKE (EXHAUST)", "DUST", "HONEY", "SPIT"}
_PLACES = {"RIVER", "LAKE", "MOUNTAIN", "FOREST", "HOUSE", "EARTH (SOIL)", "ROAD", "SKY", "SEA", "HILL", "MARSH", "PLAIN",
           "COAST", "ISLAND", "SPRING", "FORD", "PASS"}
_FEMALE = {"WOMAN", "MOTHER", "WIFE", "DAUGHTER", "SISTER", "GRANDMOTHER", "kin:mother", "kin:sister", "kin:daughter"}
#: people words outside concepts.tsv's Kinship field (kin terms from the kin list, roles and agent nouns): class 'person'
_PERSONS = {"FATHER", "MOTHER", "BROTHER", "SISTER", "SON", "DAUGHTER", "HUSBAND", "WIFE", "AUNT", "UNCLE", "GRANDFATHER",
            "GRANDMOTHER", "ANCESTORS", "ELDER", "BABY", "BOY", "GIRL", "CHIEF", "GUEST", "HUNTER", "FISHER", "HERDER",
            "SMITH", "FIGHTER",
            # (roles and trades from the WOLD list, whose fields say 'Social and political relations', 'Possession',
            # 'Law', 'Cognition' or 'Warfare': a merchant is a person, not a thing; grammar B, 2026-11-08)
            "MERCHANT", "SOLDIER", "TEACHER", "THIEF", "SERVANT", "MASTER", "SLAVE", "NEIGHBOUR", "KING", "QUEEN",
            "PRIEST", "HEALER", "WARRIOR", "TRADER", "SHEPHERD", "FARMER", "POTTER", "WEAVER", "SAILOR", "GUARD",
            "WIDOW", "WIDOWER", "ORPHAN", "TWIN", "OWNER", "LEADER", "WITCH"}


@lru_cache(maxsize=1)
def _fields() -> dict[str, str]:
    p = DATA / "concepts.tsv"
    if not p.exists():
        return {}
    try:
        return {r["gloss"].upper(): r.get("semantic_field", "") for r in _read_tsv(p)}
    except KeyError:
        return {}


def semantic_group(concept: str, pos: str = "N") -> str:
    """Bantu-like semantic group of a concept (person, animal, plant, liquid, place, manner, abstract)."""
    c = str(concept)
    u = c.upper()
    if u.startswith(("KIN:", "PEOPLE", "PERSON")) or u in ("MAN", "WOMAN", "CHILD (YOUNG HUMAN)", "FRIEND", "ENEMY",
                                                             "STRANGER", "MALE PERSON") or u in _PERSONS:
        return "person"
    if u.startswith(("ANIMAL:", "HERD:")):
        return "animal"
    if u.startswith(("CROP:", "PLANT:")):
        return "plant"
    if u.startswith(("GOD:", "NAME:GOD:")) or u in ("GOD", "SPIRIT", "DEMON"):
        return "person"   # (polish lane: a god, its name and spirits are persons, not things or abstractions)
    if u in _LIQUIDS:
        return "liquid"
    if u in _PLACES or u.startswith(("PLACE:", "LAND:")):
        return "place"
    f = _fields().get(u, "")
    if f == "Kinship":
        return "person"
    if f == "Animals":
        return "animal"
    if f == "Agriculture and vegetation":
        return "plant"
    if f in ("Speech and language", "Basic actions and technology", "Clothing and grooming"):
        return "manner"
    return "abstract"


def _class_for(g: Grammar, concept: str) -> NounClass | None:
    cs = g.class_system
    if cs is None or not cs.classes:
        return None
    grp = semantic_group(concept)
    if cs.kind == "sex":
        want = "feminine" if str(concept).upper() in _FEMALE or str(concept) in _FEMALE else "masculine"
    elif cs.kind == "animacy":
        want = "animate" if grp in ("person", "animal") else "inanimate"
    else:
        want = grp
    c = cs.by_group(want)
    if c is not None:
        return c
    for alt in fallback_groups(grp):
        c = cs.by_group(alt)
        if c is not None:
            return c
    return cs.classes[-1]


#: the classes a noun falls back on when its own group has none, in order. Owner ruling 11-08 (PW-1538 B): an animate
#: noun (person or animal) takes the person or animal class first, as Bantu class 1/2 takes the animals a language has no
#: animal class for (Swahili mbwa 'dog' takes class 1/2 agreement; Katamba 2003), before the inanimate fallbacks.
ANIMATE_FALLBACK = ("person", "animal", "people")
CLASS_FALLBACK = ("abstract", "manner", "plant", "animal")


def fallback_groups(grp: str) -> tuple:
    """The fallback class groups for a noun of semantic group `grp` (ANIMATE_FALLBACK first for persons and animals)."""
    if grp in ("person", "animal"):
        return ANIMATE_FALLBACK + tuple(x for x in CLASS_FALLBACK if x not in ANIMATE_FALLBACK)
    return CLASS_FALLBACK


def add_class(g: Grammar, rng: np.random.Generator, inv, lexicon, kyr: float, group: str | None = None,
              level: int = FREE) -> NounClass | None:
    """Recruit a classifier (from the group's source noun, or a fresh form) as a new CLASS:k gram."""
    cs = g.class_system
    if cs is None:
        return None
    if group is None:
        pool = {"classes": CLASS_GROUPS, "classifiers": CLASS_GROUPS, "sex": ("masculine", "feminine", "abstract"),
                "animacy": ("animate", "inanimate", "abstract")}[cs.kind]
        free = [x for x in pool if x not in cs.groups()]
        if not free:
            return None
        group = free[0]
    if cs.by_group(group) is not None:
        return cs.by_group(group)
    k = 1 + max([int(x.function.split(":")[1]) for x in g.grams if x.function.startswith("CLASS:")] + [0])
    # (never reuse a lost class's number: two live CLASS:3 grams would shadow each other)
    fn = f"CLASS:{k}"
    key, w = _find(lexicon, _lex_index(lexicon), CLASS_SOURCES.get(group, ()))
    if w is not None:
        form, src = _form(w), (str(key), "G066", "concept")
    else:
        form, src = _draw_morph(rng, inv), ("?", "proto", "unknown")
    form, hist = _recruited_form(form, kyr)
    gr = Gram(fn, form, "N", _side(fn, aims(g)), level, src, kyr,
              [(kyr, f"recruited as classifier for {group}"), *hist], id=g.new_id(fn))
    g.grams.append(gr)
    nc = NounClass(k, group, gr.id)
    cs.classes.append(nc)
    return nc


# --------------------------------------------------------------------------------------------------------------------
# Proto grammar
# --------------------------------------------------------------------------------------------------------------------

_NOUN_PREF = ("WATER", "PERSON", "DOG", "TREE", "FISH", "HOUSE", "STONE", "EYE", "FIRE", "BIRD", "HAND")
_VERB_PREF = ("GO", "EAT", "SEE", "GIVE", "COME", "DRINK", "SAY", "KNOW (SOMETHING)", "SIT")
_HELPER_ROLES = {"person": ("PERSON", "MAN", "MALE PERSON"), "land": ("EARTH (SOIL)", "LAND", "GROUND"),
                 "speech": ("TONGUE", "LANGUAGE", "SPEAK", "MOUTH"), "many": ("MANY", "ALL")}


def _pick_exemplars(rng, lexicon, pos: str, pref: tuple[str, ...], n: int = 4) -> list[tuple[str, Form]]:
    idx = _lex_index(lexicon)
    out: list[tuple[str, Form]] = []
    for c in pref:
        key = idx.get(c)
        w = _lex_get(lexicon, key) if key is not None else None
        if w is not None and len(_form(w)) and key not in [o[0] for o in out]:
            out.append((key, _form(w)))
        if len(out) >= n:
            return out
    rest = []
    for k in list(_lex_keys(lexicon)) if lexicon is not None else []:
        w = _lex_get(lexicon, k)
        if w is None or getattr(w, "pos", None) != pos or k in [o[0] for o in out] or not len(_form(w)):
            continue
        rest.append((getattr(w, "freq_class", 3), str(k), k, _form(w)))
    rest.sort()
    for _, _, k, f in rest[: n - len(out)]:
        out.append((k, f))
    return out


#: a deep unrecorded past (owner ruling 11-08, PW-1544 (b)): grammaticalization runs per generation, so a people with
#: 150+ year generations gets under ~130 generations in the 20 kyr window and its protos' 1-3 free grams never bound
#: (93% of their living lects marked 0-1 verb categories with an affix). Their proto-languages are as old in years as
#: anyone's, so they start with DEEP_PAST_GENS generations of the gram cycle already run (no sound change, no typology
#: drift, mid social factors DEEP_PAST_L2): slowness then conserves the inflection they had (Lithuanian, Icelandic)
#: rather than preventing any from forming. Applies from LONG_GEN_YR (the long-generation leaning's threshold).
DEEP_PAST_GENS = 200.0  # (harness, 60 protos at 430-yr generations, no sound change, 22A bins 0-1/2-3/4-5/6-7/8+:
#                         none 92/8/0/0/0, 150 2/23/63/12/0, 200 0/13/62/25/0, 300 0/12/57/32/0; 100-yr from scratch
#                         2/18/68/12/0)
DEEP_PAST_L2 = 0.2


def deep_past_gens(gen_yr: float | None) -> float:
    """Generations of unrecorded grammar a proto of a people with this generation length starts with (DEEP_PAST_GENS
    from LONG_GEN_YR, else none)."""
    return DEEP_PAST_GENS if gen_yr is not None and gen_yr >= LONG_GEN_YR else 0.0


def proto_grammar(rng: np.random.Generator, inv, lexicon, typ: Typology | None = None, kyr: float = 20.0,
                  deep_gens: float = 0.0) -> Grammar:
    """A first language starts low: 1-3 grams at level 0-1 (likeliest NEG, PL, PAST), from lexical sources when the lexicon
    has one (else of unknown origin), and class markers only if the typology drew gender/classes or classifiers, starting
    as free classifier nouns. With `deep_gens` (deep_past_gens) the gram cycle then runs that many generations first."""
    if typ is None:
        typ = draw_typology(rng, inv=inv)
    typ = Typology(typ)
    _derive(typ, inv)
    g = Grammar(typology=typ, aims=Typology(typ), shown=dict(typ))
    T = load_tables()
    idx = _lex_index(lexicon)
    for role, cands in _HELPER_ROLES.items():
        key, w = _find(lexicon, idx, cands)
        g.helpers[role] = (str(key), _form(w)) if w is not None else ("?", _draw_morph(rng, inv))
    weights = {"NEG": 3.0, "PL": 2.5, "PAST": 2.0, "FUT": 0.6, "DEF": 0.6, "LOC": 0.6, "PERF": 0.5, "DAT": 0.4,
               "3SG": 0.4, "DIM": 0.3}
    weights = {f: w * (1.0 if _wanted(f, typ) else 0.25) for f, w in weights.items()}
    n = int(rng.integers(1, 4))
    chosen: list[str] = []
    while len(chosen) < n:
        f = _choice(rng, {k: v for k, v in weights.items() if k not in chosen})
        chosen.append(f)
    for f in chosen:
        paths = [p for p in T.paths if p.target == f and not p.from_gram]
        src, form = ("?", "proto", "unknown"), ()
        for p in sorted(paths, key=lambda p: -p.weight):
            key, w = _find(lexicon, idx, p.sources)
            if w is not None:
                src, form = (str(key), p.id, "concept"), _form(w)
                break
        if not form:
            form = _draw_morph(rng, inv)
            if f == "NEG":
                src = ("?", "X01", "coin")
        form, hist = _recruited_form(form, kyr)
        lvl = int(rng.choice([FREE, CLITIC], p=[0.6, 0.4]))
        if lvl == CLITIC:
            form = clip_syllables(form, 1) or form   # (a clitic keeps one syllable: `step`)
        info = func_info(f)
        g.grams.append(Gram(f, form, info.host, _side(f, typ), lvl, src, kyr, [(kyr, "proto"), *hist], id=g.new_id(f)))
    gk = typ.get("gender", "none")
    if gk != "none" or typ.get("numeral_classifiers") == "yes":
        kind = gk if gk != "none" else "classifiers"
        g.class_system = ClassSystem(kind)
        n0 = {"classes": 3, "classifiers": 2, "sex": 2, "animacy": 2}[kind]
        for _ in range(n0):
            add_class(g, rng, inv, lexicon, kyr)
    for concept, f in _pick_exemplars(rng, lexicon, "N", _NOUN_PREF):
        g.exemplars.append(Exemplar(concept, "N", f))
    for concept, f in _pick_exemplars(rng, lexicon, "V", _VERB_PREF):
        g.exemplars.append(Exemplar(concept, "V", f))
    _sync_cells(g)
    _clusivity(g, rng, kyr, 1.0, 0.0, lexicon, inv, None)   # (a proto that tells the two 'we's apart has both words)
    _redup(g, rng, kyr, 1.0, 0.0)
    _numerals(g, rng, lexicon, inv, kyr)
    _compare(g, rng, kyr, lexicon)
    realise(g, lexicon)
    if deep_gens > 0:
        _deep_past(g, rng, inv, lexicon, kyr, deep_gens)
    return g


def _deep_past(g: Grammar, rng, inv, lexicon, kyr: float, gens: float) -> None:
    """Run the gram cycle `gens` generations on a new proto (DEEP_PAST_GENS) and record the outcome as its starting
    state: the grams' histories and the grammar's events say 'a deep unrecorded past', not a dated story."""
    n_ev = len(g.events)
    step(rng, g, gens, inv=inv, lexicon=lexicon, l2_share=DEEP_PAST_L2, isolation=0.5, kyr=kyr, drift_typology=False)
    del g.events[n_ev:]
    for gr in g.grams:
        gr.history = [(kyr, "proto"), (kyr, f"already {LEVELS[gr.level]} (a deep unrecorded past)")] if gr.live else \
            [(kyr, "proto"), (kyr, "lost before the record")]
    bound = sum(1 for gr in g.grams if gr.live and gr.level >= AFFIX)
    g.events.append((kyr, f"a deep unrecorded past: {len(g.live())} grams at the start, {bound} of them bound"))


def _numerals(g: Grammar, rng, lexicon, inv, kyr: float) -> None:
    """The proto lexicon's counting system follows the grammar's counting base: lexsys.set_numerals draws the system
    inside the label (decimal; vigesimal pure or hybrid; for "other" a 5-based or a restricted count) and builds the
    composite numerals (twenty 'two ten', a hundred 'five twenties', six 'five one' ...), with a multiplier where the
    grammar puts a numeral beside its noun (Greenberg 1978: 'two ten' NumN, 'ten two' NNum). Only on a real lexicon (one
    with `systems`); the event lists what was built."""
    if lexicon is None or not hasattr(lexicon, "systems"):
        return
    from planet.language import lexsys as LS   # noqa: PLC0415
    base = aims(g).get("numeral_base", "decimal")
    built = LS.set_numerals(rng, lexicon, base, inv, kyr, getattr(lexicon, "lect", None),
                            mul_first=aims(g).get("numeral") != "NNum")
    made = [f"{k.lower()} = {lexicon.words[k].etym[-1].note.split(':', 1)[0]}" for k, _ in built if k in lexicon.words]
    sy = lexicon.systems.get("numeral") or {}
    g.events.append((kyr, f"counting base {base} ({sy.get('system', base)})" + (": " + "; ".join(made) if made else "")))


# --------------------------------------------------------------------------------------------------------------------
# Step
# --------------------------------------------------------------------------------------------------------------------


def _small_group(population: float | None) -> float:
    """+1 for ~100 speakers, 0 for ~10^4, -1 for ~10^6 and up."""
    if not population or population <= 0:
        return 0.0
    return float(np.clip((4.0 - math.log10(population)) / 2.0, -1.0, 1.0))


def social_factors(l2_share: float, population: float | None, isolation: float) -> dict[str, float]:
    """How the speech community pushes on each hazard (Trudgill 2011; Lupyan & Dale 2010; Wray & Grace 2007): adult L2
    learners cut recruitment and fusion and speed loss and regularization; small, isolated groups accrue and keep
    complexity."""
    l2 = float(np.clip(l2_share, 0.0, 1.0))
    sg = _small_group(population)
    iso = float(np.clip(isolation, 0.0, 1.0))
    return {
        "recruit": (1.0 - l2) * (1.0 + 0.4 * sg) * (0.8 + 0.4 * iso),
        # (fusion falls linearly with the adult-L2 share, as recruitment does; it was (1 - l2)^2, x0.09 at the proxy's 0.7
        # ceiling, so grams in contact lects never bound: synthesis lane 2026-11-08)
        "fuse": (1.0 - l2) * (1.0 + 0.3 * sg) * (0.6 + 0.8 * iso),
        "loss": (1.0 + 4.0 * l2) * (1.0 - 0.3 * sg) * (1.2 - 0.4 * iso),
        "strip": l2 ** 3,
        "analogy": (1.0 + 2.0 * l2) * (1.0 - 0.3 * sg),
        "large": max(0.0, -sg),   # (0 up to ~10^4 speakers, 1 from ~10^6: state-sized societies; politeness, phase D)
    }


def _p(h: float, dn: float) -> float:
    return 1.0 - math.exp(-max(h, 0.0) * dn)


def _sync_lexicon(g: Grammar, lexicon, kyr: float) -> None:
    """Stems follow the lexicon. The driver runs every rule over both, so they only part when the lexicon replaced or
    re-derived the word; then the paradigm is rebuilt regularly from the new stem."""
    if lexicon is None:
        return
    for ex in g.exemplars:
        w = _lex_get(lexicon, ex.concept)
        if w is None:
            continue
        f = _form(w)
        if f and f != tuple(ex.stem):
            ex.stem = f
            for k in list(ex.cells):
                ex.set(k, build_parts(ex, k, g))
            g.events.append((kyr, f"relexified {ex.concept}: paradigm rebuilt on {ipa(f)}"))
    for role, (concept, _) in list(g.helpers.items()):
        w = _lex_get(lexicon, concept)
        if w is not None and _form(w):
            g.helpers[role] = (concept, _form(w))


_DIST_PLACE = ("THERE", "FAR")


def _recruit(rng, g: Grammar, lexicon, kyr: float, T: Tables, idx, inv=None, targets: set | None = None,
             evid_x: float = 1.0) -> Gram | None:
    """One recruitment draw over the attested paths. `targets`: the aims' pull (PRESSURE), restricted to these functions
    (wanted ones no live gram marks yet: a flip to 'number: sg-pl' recruiting a plural word)."""
    at = aims(g)
    live_by_fn: dict[str, list[Gram]] = {}
    for gr in g.live():
        live_by_fn.setdefault(gr.function, []).append(gr)
    cands: list[tuple[float, GPath, Any, Any]] = []
    for p in T.paths:
        tgt = p.target
        if p.weight <= 0 or (targets is not None and tgt not in targets):
            continue   # (a 'set' path binds only with its series)
        if tgt in ("RECPST", "REMPST") and "PAST" not in live_by_fn:
            continue   # 'come from' > recent past only beside a past tense (G003); never the plain past
        if tgt == "DIST" and (_find(lexicon, idx, _DIST_PLACE)[1] is None or _find(lexicon, idx, ("THIS",))[1] is None):
            continue   # (a far demonstrative needs a place word to reinforce 'that', and a 'this' to stand beside)
        if tgt == "CLASS":
            if g.class_system is None:
                if not _wanted("CLASS", at):
                    continue   # (a class system the aims now want starts from a first classifier, below)
            w_mult = 1.0 if _wanted("CLASS", at) else 0.15
        else:
            cur = live_by_fn.get(tgt, [])
            wanted = _wanted(tgt, at)
            if targets is not None and cur:
                continue
            if cur:
                # renewal: only when the current marker is worn (fused, or down to one segment) and nothing new is
                # pending; or a negator on the side the syntax has left (a Jespersen-cycle reinforcer on the new side)
                moved = tgt == "NEG" and all(c.side != _side("NEG", at) for c in cur)
                if not moved and (any(c.level < AFFIX for c in cur)
                                  or not all(c.level >= FUSED or len(c.form) <= 1 for c in cur)):
                    continue
                w_mult = 0.3
            else:
                w_mult = 1.0
            w_mult *= 1.0 if wanted else 0.15
        if p.from_gram:
            src = next((x for s in p.sources for x in live_by_fn.get(s, [])), None)
            if src is None:
                continue
            cands.append((p.weight * w_mult, p, src, None))
        else:
            key, w = _find(lexicon, idx, p.sources)
            if w is None:
                if p.id == "X01" and not live_by_fn.get("NEG"):
                    cands.append((p.weight * w_mult, p, None, None))   # no 'nothing/lack' word: a coined negator
                continue
            cands.append((p.weight * w_mult, p, key, w))
    if not cands:
        return None
    ws = np.array([c[0] * (evid_x if c[1].target in EVID_FNS else 1.0) for c in cands], dtype=float)
    _, p, a, w = cands[int(rng.choice(len(cands), p=ws / ws.sum()))]
    if p.target == "CLASS":
        if g.class_system is None:
            gk = at.get("gender", "none")
            g.class_system = ClassSystem(gk if gk != "none" else "classifiers")
            g.events.append((kyr, f"a {g.class_system.kind} system begins with a first classifier"))
        nc = add_class(g, rng, inv, lexicon, kyr)
        return g.by_id(nc.gram_id) if nc else None
    if p.from_gram and p.id in COPY_PATHS:
        # polysemy: a new gram splits off the source, which keeps its own function (copula > focus, reflexive >
        # reciprocal); it starts free when the source is free or a clitic, else as an affix like its source
        info = func_info(p.target)
        lvl = min(a.level, AFFIX) if a.level >= AFFIX else FREE
        gr = Gram(p.target, tuple(a.form), info.host, a.side if lvl else _side(p.target, at), lvl, (a.function, p.id, "gram"),
                  kyr, [(kyr, f"split off the {a.info.gloss} marker ({p.id})")], id=g.new_id(p.target))
        g.grams.append(gr)
        g.events.append((kyr, f"{p.target} {ipa(gr.form)} split off the {a.function} marker"))
        return gr
    if p.from_gram:
        # reanalysis: the gram takes the new function (PERF > PAST, ALL > DAT, DEF > class marker)
        old = a.function
        a.function = p.target
        a.host = func_info(p.target).host
        a.source = (old, p.id, "gram")
        a.history.append((kyr, f"reanalysed {old} > {p.target} ({p.id})"))
        g.events.append((kyr, f"{old} gram {ipa(a.form)} became {p.target}"))
        return a
    info = func_info(p.target)
    if w is None:   # coined (X01 with no source word)
        form, hist = _recruited_form(_draw_morph(rng, inv), kyr)
        gr = Gram(p.target, form, info.host, _side(p.target, at), FREE, ("?", p.id, "coin"), kyr,
                  [(kyr, f"coined ({p.id})"), *hist], id=g.new_id(p.target))
        g.grams.append(gr)
        g.events.append((kyr, f"coined a {p.target} marker: {ipa(gr.form)}"))
        return gr
    form, hist = _recruited_form(_form(w), kyr)
    if p.target == "DIST":   # ('that' + the first syllable of 'there, far': that-there > yon)
        form = tuple(form) + tuple(first_syllable(_form(_find(lexicon, idx, _DIST_PLACE)[1])))
    gr = Gram(p.target, form, info.host, _side(p.target, at), FREE, (str(a), p.id, "concept"), kyr,
              [(kyr, f"recruited from '{a}' ({p.id})"), *hist], id=g.new_id(p.target))
    g.grams.append(gr)
    g.events.append((kyr, f"recruited {p.target} from '{a}': {ipa(gr.form)}" + (" (clipped)" if hist else "")))
    return gr


def recruit(rng: np.random.Generator, g: Grammar, lexicon, kyr: float = 0.0, function: str | None = None,
            source: str | None = None, inv=None) -> Gram | None:
    """Recruit one gram now (the step's recruit draw, optionally restricted to a target function and/or source concept).
    For the workbench and tests; `step` draws recruitments itself."""
    T = load_tables()
    if function is not None or source is not None:
        keep = [p for p in T.paths if (function is None or p.target == function)
                and (source is None or source.upper() in p.sources)]
        T = dataclasses.replace(T, paths=keep)
    gr = _recruit(rng, g, lexicon, kyr, T, _lex_index(lexicon), inv)
    realise(g, lexicon)
    return gr


def _lose(g: Grammar, gr: Gram, kyr: float, why: str) -> None:
    gr.level = LOST
    gr.history.append((kyr, f"lost: {why}"))
    g.events.append((kyr, f"lost {gr.function} {ipa(gr.form)}: {why}"))
    if gr.function.startswith("CLASS") and g.class_system is not None:
        g.class_system.classes = [c for c in g.class_system.classes if c.gram_id != gr.id]
    if g.gram(gr.function) is None:   # (no other marker of this function lives: its processes go with it)
        for k in ("iclass", "stem_change"):
            (g.processes.get(k) or {}).pop(gr.function, None)
            if k in g.processes and not g.processes[k]:
                del g.processes[k]
        if (g.processes.get("infix") or {}).get("fn") == gr.function:
            del g.processes["infix"]


#: how a lect with both an accusative and an ergative divides them (Dixon 1979, 1994; Silverstein 1976): by the
#: nominal hierarchy (pronouns accusative, nouns ergative: Dyirbal) or by aspect (ergative in the perfective or past,
#: accusative elsewhere: Hindi, Georgian, Mayan). NP-type splits are the commoner (Dixon 1994: 'the great majority').
SPLIT_KIND = {"person": 0.6, "aspect": 0.4}
SPLIT_ASPECT = ("PERF", "PAST")   # the clauses an aspect split makes ergative (the first the lect has)


def _split(g: Grammar, rng, kyr: float, lv: dict) -> None:
    """Choose (or drop) the way a split-ergative lect divides its alignment, once both an ACC and an ERG gram live."""
    both = "ACC" in lv and "ERG" in lv
    cur = g.processes.get("split")
    if not both:
        if cur is not None:
            del g.processes["split"]
            g.events.append((kyr, f"the {cur} split of the alignment ends (no longer both an accusative and an ergative)"))
        return
    if cur == "aspect" and not any(f in lv for f in SPLIT_ASPECT):
        cur = None   # (the perfective it hung on is gone: re-chosen)
    if cur is None:
        kinds = dict(SPLIT_KIND)
        if not any(f in lv for f in SPLIT_ASPECT):
            kinds.pop("aspect")
        k = _choice(rng, kinds)
        g.processes["split"] = k
        g.events.append((kyr, "split ergativity: " + ("pronouns accusative, nouns ergative" if k == "person"
                                                     else "ergative in the perfective, accusative elsewhere")))


#: how a lect that comes to tell inclusive from exclusive 'we' makes the inclusive (the old 'we' stays as the
#: exclusive): a 'we + you' compound (Tok Pisin yumi < you + me, Bislama yumi; Cysouw 2003 on the 'we + you' type), an
#: 'I + you' compound (the minimal inclusive: Tagalog kita, Ilocano ta), or a root of its own (Quechua -nchik vs -yku,
#: Malay kita vs kami: the commonest outcome in old systems, where any compound has long since become opaque)
INCLUSIVE_FROM = {"WE+THOU": 0.45, "I+THOU": 0.15, "root": 0.40}
CLUSIVE_LOSS = 0.002   # per generation (x social loss) once the aims no longer tell the two apart


def _clusivity(g: Grammar, rng, kyr: float, p_make: float, p_drop: float, lexicon, inv, lect_id: str | None) -> None:
    """The aims ask for inclusive vs exclusive 'we' and the lexicon has one 'we': make the inclusive (`INCLUSIVE_FROM`);
    they no longer ask and it has two: the distinction goes (the inclusive is dropped, or, a third of the time, takes
    over as the only 'we', as French on and Tok Pisin yumi spread)."""
    if lexicon is None or not hasattr(lexicon, "words") or _lex_get(lexicon, "WE") is None:
        return
    from planet.language import lexicon as LX   # noqa: PLC0415
    want = aims(g).get("clusivity") == "yes"
    has = _clusive(lexicon) == "yes"
    lid = lect_id or getattr(lexicon, "lect", "?")
    if want and not has and rng.random() < p_make:
        how = _choice(rng, INCLUSIVE_FROM)
        w = None
        if how != "root":
            head, mod = how.split("+")
            if mod == "THOU" and _lex_get(lexicon, "THOU") is None:
                mod = "YOU"
            if _lex_get(lexicon, head) is not None and _lex_get(lexicon, mod) is not None:
                w = LX.compound(rng, lexicon, CLUSIVE[0], inv, kyr, lid, head=head, modifier=mod,
                                note=f"{head.lower()} + {mod.lower()}: 'we, you included'")
        if w is None or _form(w) == _form(_lex_get(lexicon, "WE")):
            w = LX.coin(rng, lexicon, CLUSIVE[0], inv, kyr, lid, how="root", store=False)
            how = "root"
        lexicon.set(w)
        lexicon.words.pop(CLUSIVE[1], None)
        g.events.append((kyr, f"inclusive 'we' {ipa(_form(w))} told apart from exclusive "
                              f"{ipa(_form(_lex_get(lexicon, 'WE')))} ({'a new root' if how == 'root' else 'a compound'})"))
    elif not want and has and rng.random() < p_drop:
        inc = _lex_get(lexicon, CLUSIVE[0])
        if rng.random() < 1 / 3:
            we = _lex_get(lexicon, "WE")
            lexicon.set(dataclasses.replace(inc.with_step(LX._step(kyr, lid, f"shift:{CLUSIVE[0]}", inc.form, "we")),
                                            concept=we.concept, pos=we.pos, freq_class=we.freq_class))
            what = f"the inclusive {ipa(_form(inc))} became the only 'we'"
        else:
            what = f"the inclusive {ipa(_form(inc))} fell out of use; {ipa(_form(_lex_get(lexicon, 'WE')))} is 'we'"
        lexicon.words.pop(CLUSIVE[0], None)
        lexicon.words.pop(CLUSIVE[1], None)
        g.events.append((kyr, f"no more inclusive/exclusive 'we': {what}"))


def _redup(g: Grammar, rng, kyr: float, p_make: float, p_drop: float) -> None:
    """Verbal reduplication arises when the aims want it (`REDUP`, `REDUP_SHAPE`; a CV copy is prefixed three times in
    four) and fades when they no longer do; the verb exemplars carry its cell, so sound change wears the copy down with
    the rest of the word (Tagalog-style CV- copies that later lose their transparency)."""
    want = aims(g).get("verb_reduplication") == "yes"
    rd = g.processes.get("redup")
    if want and rd is None and rng.random() < p_make:
        fn = _choice(rng, REDUP)
        shape = _choice(rng, REDUP_SHAPE)
        side = "pre" if shape == "full" or rng.random() < 0.75 else "post"
        g.processes["redup"] = {"fn": fn, "shape": shape, "side": side}
        g.events.append((kyr, f"verbs reduplicate for the {REDUP_INFO[fn].gloss.split(' (')[0]} "
                              f"({'the whole stem' if shape == 'full' else 'a CV copy ' + ('before' if side == 'pre' else 'after') + ' the stem'})"))
        _sync_cells(g)
    elif not want and rd is not None and rng.random() < p_drop:
        del g.processes["redup"]
        g.events.append((kyr, f"verbal reduplication ({REDUP_INFO[rd['fn']].gloss.split(' (')[0]}) fell out of use"))
        _sync_cells(g)


def _processes(g: Grammar, rng, kyr: float, dn: float, soc: dict, lexicon=None, inv=None, lect_id: str | None = None
               ) -> None:
    """The built constructions that are not grams on the ladder (`Grammar.processes`)."""
    lv = _live_fns(g)
    _split(g, rng, kyr, lv)
    p_make = _p(PRESSURE * soc.get("recruit", 1.0), dn)
    _clusivity(g, rng, kyr, p_make, _p(CLUSIVE_LOSS * soc.get("loss", 1.0), dn), lexicon, inv, lect_id)
    _redup(g, rng, kyr, _p(PRESSURE * soc.get("recruit", 1.0) * soc.get("redup", 1.0), dn),
           _p(REDUP_LOSS * soc.get("loss", 1.0), dn))
    # grammar phase C (2026-11-08)
    fuse, loss = soc.get("fuse", 1.0), soc.get("loss", 1.0)
    _concord(g, rng, kyr, _p(CONCORD_GROW * fuse, dn), _p(CONCORD_LOSS * loss, dn))
    changed = _iclass(g, rng, kyr, _p(ICLASS_SPLIT * fuse, dn), _p(ICLASS_LEVEL * soc.get("analogy", 1.0), dn), lexicon, inv)
    changed |= _cumulate(g, rng, kyr, _p(CUMUL * fuse, dn))
    changed |= _infix(g, rng, kyr, _p(INFIX * fuse, dn))
    _second(g, rng, kyr, dn, fuse, loss)
    _incorp(g, rng, kyr, _p(INCORP * fuse, dn), _p(INCORP_LOSS * loss, dn))
    # grammar phase D (2026-11-08)
    _polite(g, rng, kyr, _p(POLITE_MAKE * soc.get("large", 0.0), dn),
            _p(POLITE_LOSS * (1.0 - soc.get("large", 0.0)) * loss, dn), lexicon)
    _compare(g, rng, kyr, lexicon)
    _dom(g, rng, kyr, lv, _p(DOM_MAKE * fuse, dn), _p(DOM_LOSS * loss, dn))
    if changed:
        _sync_cells(g)


# --------------------------------------------------------------------------------------------------------------------
# Grammar phase C processes (2026-11-08). Each hazard is per generation, scaled by the social factors (fusion-like
# processes by `fuse`, losses by `loss`); all are first guesses, listed for Daniel in for-daniel.md "Grammar phase C".
# --------------------------------------------------------------------------------------------------------------------

#: concord (item 8): a bound class marker is copied onto the noun's dependents and onto the verb. Corbett's Agreement
#: Hierarchy (attributive > predicate > relative > personal pronoun; Corbett 1979, 2006) orders the targets:
#: demonstratives and adjectives agree first, the verb's subject slot later (Bantu alliterative concord, Givon 1971:
#: the class prefixes and the subject concords come from the same old pronouns). Grows at CONCORD_GROW per generation
#: while a class marker is bound (clitic or tighter), one target at a time; goes with the last bound class marker.
CONCORD_TARGETS = {"dem": 1.0, "adj": 0.7, "verb": 0.5}
CONCORD_GROW = 0.02
CONCORD_LOSS = 0.0005


#: what the pages call a class system (owner ruling 11-08, PW-1538 A): "gender" only where something agrees with the noun
#: (Corbett 1991: gender is reflected in agreement; Grambank codes it the same way); a class marked on the noun alone, with
#: no concord anywhere, is GENDER_NO_AGREEMENT. Display only: the typology value (aims, Grambank comparison) is unchanged.
GENDER_NO_AGREEMENT = "noun class marking (no agreement)"


def gender_label(gender: str | None, concord) -> str:
    """The page label of the typology's gender value: the value itself where concord holds (something agrees with the
    noun), GENDER_NO_AGREEMENT where the class is marked on the noun only, 'none' for none."""
    if not gender or gender == "none":
        return "none"
    return gender if concord else GENDER_NO_AGREEMENT


def _concord(g: Grammar, rng, kyr: float, p_grow: float, p_loss: float) -> None:
    cs = g.class_system
    bound = cs is not None and any((x := g.by_id(c.gram_id)) is not None and x.live and x.level >= CLITIC
                                   for c in cs.classes)
    cur = list(g.processes.get("concord") or [])
    if not bound:
        if cur:
            del g.processes["concord"]
            g.events.append((kyr, "concord ends (no class marker is bound any more)"))
        return
    if cur and rng.random() < p_loss:
        t = cur.pop(int(rng.integers(len(cur))))
        g.events.append((kyr, f"the {'verb' if t == 'verb' else t + 'onstratives' if t == 'dem' else 'adjectives'} no "
                              "longer agree in class"))
    elif rng.random() < p_grow:
        left = {k: w for k, w in CONCORD_TARGETS.items() if k not in cur}
        if left:
            t = _choice(rng, left)
            cur.append(t)
            g.events.append((kyr, f"class concord spreads to the {dict(dem='demonstratives', adj='adjectives', verb='verb (subject concord)')[t]}"))
    if cur:
        g.processes["concord"] = sorted(cur)
    else:
        g.processes.pop("concord", None)


#: inflection classes (item 13): a bound marker splits into two lexically distributed forms, as old competing
#: markers end up spread over the lexicon (English -s / -en plurals; Latin declensions from stem-vowel classes once the
#: stem vowels changed). The second form comes from a competing source of the same function (another path's word),
#: else from an unrelated small morph; the second class takes a share of the words (`iclass_member`). Levelling
#: (analogy) removes the minority form again at ICLASS_LEVEL.
ICLASS_SPLIT = 0.0006
ICLASS_LEVEL = 0.0004
ICLASS_SLOTS = ("number", "case", "tense", "aspect", "person")


def _iclass(g: Grammar, rng, kyr: float, p_split: float, p_level: float, lexicon, inv) -> bool:
    ic = g.processes.setdefault("iclass", {})
    changed = False
    for gr in sorted((x for x in g.grams if x.live and x.level >= AFFIX and "+" not in x.function
                      and x.info.slot in ICLASS_SLOTS and x.host[0] in "NV"), key=lambda x: x.id):
        if gr.alt:
            if rng.random() < p_level:
                gr.alt = ()
                ic.pop(gr.function, None)
                _rebuild_fn(g, gr.function)
                g.events.append((kyr, f"analogy: the second {gr.info.gloss} form gave way to {ipa(gr.form)} in every word"))
                changed = True
            continue
        if not gr.form or rng.random() >= p_split:
            continue
        T = load_tables()
        idx = _lex_index(lexicon)
        alt = ()
        for path in T.paths:
            if path.target == gr.function and not path.from_gram and path.weight > 0:
                key, w = _find(lexicon, idx, path.sources)
                if w is not None and first_syllable(_form(w)) != tuple(gr.form):
                    alt = first_syllable(_form(w))
                    break
        if not alt:
            alt = first_syllable(_draw_morph(rng, inv))
        if not alt or alt == tuple(gr.form):
            continue
        gr.alt = alt
        ic[gr.function] = {"salt": int(rng.integers(1 << 30)), "share": round(float(rng.uniform(0.2, 0.5)), 2)}
        _rebuild_fn(g, gr.function)
        gr.history.append((kyr, f"a second inflection class takes {ipa(alt)}"))
        g.events.append((kyr, f"inflection classes: some words take the {gr.info.gloss} marker {ipa(alt)}, the rest "
                              f"{ipa(gr.form)}"))
        changed = True
    if not ic:
        g.processes.pop("iclass", None)
    return changed


def _rebuild_fn(g: Grammar, fn: str) -> None:
    """Rebuild every exemplar cell that carries `fn` (its form on some words changed by fiat, not by sound change)."""
    for ex in g.exemplars:
        for k in list(ex.cells):
            if fn in k:
                ex.set(k, build_parts(ex, k, g))


#: cumulative exponence (item 13): two bound markers side by side on one word (number and case on a noun, tense or
#: aspect and person on a verb: the pairs the paradigm cells carry) wear into one morph that no longer splits, a
#: portmanteau (Latin -orum GEN.PL, Spanish -o 1SG.PRS). Its form is the two run together; sound change then blurs it.
#: The two markers live on alone elsewhere.
CUMUL = 0.0008
CUMUL_PAIRS = (("number", "case"), ("aspect", "person"), ("tense", "person"))


def _cumulate(g: Grammar, rng, kyr: float, p: float) -> bool:
    have = {tuple(x.function.split("+")) for x in g.grams if x.live and "+" in x.function}
    by_slot: dict[str, list[Gram]] = {}
    for x in sorted(g.grams, key=lambda x: x.id):
        if x.live and x.level >= AFFIX and x.form and "+" not in x.function and not x.function.startswith("CLASS"):
            by_slot.setdefault(x.info.slot, []).append(x)
    for sa, sb in CUMUL_PAIRS:
        for a in by_slot.get(sa, ()):
            for b in by_slot.get(sb, ()):
                if (a.function, b.function) in have or a.side != b.side or a.host[0] != b.host[0] or rng.random() >= p:
                    continue
                form = tuple(b.form) + tuple(a.form) if a.side == "pre" else tuple(a.form) + tuple(b.form)
                fn = f"{a.function}+{b.function}"
                g.grams.append(Gram(fn, form, b.host, b.side, FUSED, (fn, "cumul", "gram"), kyr,
                                    [(kyr, f"{a.function} and {b.function} fused into one ending")], id=g.new_id(fn)))
                g.events.append((kyr, f"cumulative exponence: {a.function} and {b.function} merge into one ending "
                                      f"{ipa(form)}"))
                _rebuild_fn(g, a.function)
                return True
    return False


#: infixes (item 15): a vowel-initial prefix moves inside a consonant-initial stem, after its first consonants (Yu
#: 2007, A Natural History of Infixation: metathesis of VC- prefixes, Tagalog um- > s<um>ulat, Chamorro). Only such
#: prefixes can, so the share stays small.
INFIX = 0.003


def _infix(g: Grammar, rng, kyr: float, p: float) -> bool:
    cur = g.processes.get("infix")
    if cur:
        return False
    for gr in sorted(g.grams, key=lambda x: x.id):
        if (gr.live and gr.level == AFFIX and gr.side == "pre" and gr.host == "V" and len(gr.form) >= 2
                and _is_v(gr.form[0]) and not _is_v(gr.form[-1]) and "+" not in gr.function and rng.random() < p):
            g.processes["infix"] = {"fn": gr.function}
            _rebuild_fn(g, gr.function)
            gr.history.append((kyr, "became an infix"))
            g.events.append((kyr, f"the {gr.info.gloss} prefix {ipa(gr.form)}- moved inside the stem: an infix"))
            return True
    return False


def _stem_change(g: Grammar, gr: Gram, kyr: float) -> None:
    """A marker worn to nothing that still shows in the stem (umlaut, ablaut, mutation) becomes a stem change across
    the lexicon (item 15): the vowel changes its exemplar cells show become a rule every word of the category follows
    (German Gast/Gaeste, English foot/feet once the -i ending was gone)."""
    sc = g.processes.setdefault("stem_change", {})
    if gr.function in sc:
        return
    cnt: dict[tuple[str, str], int] = {}
    for ex in g.exemplars:
        for key, cell in ex.cells.items():
            if gr.function not in key:
                continue
            base_key = tuple(f for f in key if f != gr.function)
            base = ex.cells.get(base_key, tuple(ex.stem)) if base_key else tuple(ex.stem)
            if len(base) != len(cell):
                continue
            for a, b in zip(base, cell):
                if a != b and _is_v(a) and _is_v(b):
                    cnt[(ipa((a,)), ipa((b,)))] = cnt.get((ipa((a,)), ipa((b,))), 0) + 1
    if not cnt:
        if not sc:
            del g.processes["stem_change"]
        return
    best = sorted(cnt.items(), key=lambda x: (-x[1], x[0]))
    vmap, seen = [], set()
    for (a, b), _ in best:
        if a not in seen:
            vmap.append([a, b])
            seen.add(a)
    sc[gr.function] = vmap[:4]
    g.events.append((kyr, f"the {gr.info.gloss} is now a stem change: " + ", ".join(f"{a} > {b}" for a, b in vmap[:4])))


#: second-position clitics (item 16): a lect's verbal clitics (tense, mood, negation, person, question) gather after
#: the first word or phrase of the clause (Wackernagel 1892; Slavic, Warlpiri, Tagalog, Pashto). Arises while the lect
#: has a verbal clitic, three times faster under free word order, where 2P clitics are commonest (Hale 1973 on Warlpiri;
#: Spencer & Luis 2012); goes when no verbal clitic is left.
SECOND = 0.0015
SECOND_LOSS = 0.0005


def _second(g: Grammar, rng, kyr: float, dn: float, fuse: float, loss: float) -> None:
    clit = any(x.live and x.level == CLITIC and x.host[0] == "V" for x in g.grams)
    cur = g.processes.get("second")
    if cur and (not clit or rng.random() < _p(SECOND_LOSS * loss, dn)):
        del g.processes["second"]
        g.events.append((kyr, "the verb's clitics no longer go to second position"))
    elif not cur and clit:
        h = SECOND * fuse * (3.0 if aims(g).get("word_order") == "free" else 1.0)
        if rng.random() < _p(h, dn):
            g.processes["second"] = True
            g.events.append((kyr, "the verb's clitics move to second position in the clause (after the first word)"))


#: noun incorporation (item 18): in a head-marking lect with rich verb morphology (an object marker bound and at least
#: three bound verb categories) a generic object noun compounds into the verb (Mithun 1984, type I; Mohawk, Chukchi,
#: Nahuatl). Goes at INCORP_LOSS, or when the lect stops being polysynthetic-leaning.
INCORP = 0.003
INCORP_LOSS = 0.0005


def _verb_categories(g: Grammar) -> int:
    cats = set()
    for x in g.grams:
        if x.live and x.level >= AFFIX and x.host[0] == "V" and "+" not in x.function:
            sl = x.info.slot
            cats.add("object" if x.function in OBJ_FNS else sl)
    return len(cats)


def _incorp(g: Grammar, rng, kyr: float, p_make: float, p_loss: float) -> None:
    ok = any(x.live and x.level >= CLITIC and x.function in OBJ_FNS for x in g.grams) and _verb_categories(g) >= 3
    cur = g.processes.get("incorp")
    if cur and (not ok or rng.random() < p_loss):
        del g.processes["incorp"]
        g.events.append((kyr, "noun incorporation fell out of use"))
    elif not cur and ok and rng.random() < p_make:
        g.processes["incorp"] = True
        g.events.append((kyr, "object nouns can be incorporated into the verb ('fish-eat')"))


#: person agreement grows as a set (Givon 1976; Siewierska 2004 ch. 8; Fuss 2005): when one subject pronoun binds to the
#: verb, the rest of the series it belongs to binds with it, each member with PERSON_JOIN (the third singular less
#: often: a zero 3SG is the commonest gap, Koryak, Hungarian, Turkish), from its own pronoun; a member that missed the
#: moment is filled in later by analogy with the paradigm (PERSON_FILL per generation, x social recruit). Members whose
#: pronouns share a form come out syncretic; a missing pronoun leaves a gap.
PERSON_JOIN = {"1SG": 0.85, "2SG": 0.85, "3SG": 0.6, "1PL": 0.8, "2PL": 0.75, "3PL": 0.75, "INCL": 0.7}
PERSON_FILL = 0.004


def _degram_bias(g: Grammar, gr: Gram) -> float:
    b = DEGRAM_EDGE if gr.host == "NP" else 1.0
    slot = gr.info.slot
    mates = [x for x in g.grams if x is not gr and x.info.slot == slot and x.host[0] == gr.host[0]]
    if any(not x.live for x in mates) and not any(x.live and x.level >= CLITIC for x in mates):
        b *= DEGRAM_ORPHAN
    return b


def _degram(g: Grammar, gr: Gram, kyr: float) -> None:
    """One step back up the ladder (affix > clitic, clitic > free word), logged as a grammar event."""
    old = gr.level
    gr.level -= 1
    if gr.level == FREE:
        gr.side = _side(gr.function, aims(g))
    what = f"{LEVELS[old]} > {LEVELS[gr.level]}"
    gr.history.append((kyr, f"degrammaticalized: {what}"))
    g.events.append((kyr, f"degrammaticalization: the {gr.info.gloss} marker {ipa(gr.form)} went from {what} "
                          "(a rare climb back up the ladder; Norde 2009)"))


def _person_member(g: Grammar, fn: str, level: int, side: str, lexicon, idx, kyr: float, T: Tables, why: str,
                   rng=None, inv=None) -> Gram | None:
    """Bind one person function at `level`: a live free person gram climbs down to it; else its pronoun is recruited."""
    cur = [x for x in g.grams if x.live and x.function == fn]
    if any(x.level >= CLITIC for x in cur):
        return None
    if cur:
        gr = min(cur, key=lambda x: x.age_gens)
        gr.level, gr.side = level, side
        gr.history.append((kyr, f"now {LEVELS[level]} ({why})"))
    else:
        key = w = pid = None
        for p in T.paths:
            if p.target == fn and not p.from_gram:
                key, w = _find(lexicon, idx, p.sources)
                if w is not None:
                    pid = p.id
                    break
        if w is None:
            return None
        form, hist = _recruited_form(_form(w), kyr)
        if level >= CLITIC:
            e = first_syllable(form) if level >= AFFIX else clip_syllables(form, 1)
            if e != form:
                hist.append((kyr, f"eroded {ipa(form)} > {ipa(e)}"))
            form = e
        gr = Gram(fn, form, func_info(fn).host, side, level, (str(key), pid, "concept"), kyr,
                  [(kyr, f"recruited from '{key}' ({pid}), {why}"), *hist], id=g.new_id(fn))
        g.grams.append(gr)
    g.events.append((kyr, f"{fn} {ipa(gr.form)} joins the person paradigm as a {LEVELS[level]} ({why})"))
    return gr


def _join_p(fn: str) -> float:
    return PERSON_JOIN.get(fn.split(".")[0] if fn != INCL_FN else "INCL", 0.7)


def _person_set(g: Grammar, gr: Gram, rng, lexicon, kyr: float, T: Tables) -> None:
    """`gr`, a person marker, has just bound (clitic or tighter): the rest of its series (subject, object or possessor;
    `SERIES`) binds with it (PERSON_JOIN), each member from its own pronoun."""
    if lexicon is None:
        return
    idx = _lex_index(lexicon)
    for fn in SERIES[SERIES_OF[gr.function]]:
        if fn != gr.function and rng.random() < _join_p(fn):
            _person_member(g, fn, min(gr.level, AFFIX), gr.side, lexicon, idx, kyr, T,
                           f"with {gr.function}: the pronoun series binds as a set")


def _local_series(g: Grammar, rng, kyr: float, p: float) -> bool:
    """The local-case series (PW-1569): a bound region marker (inessive, superessive) and a bound directional case
    (allative, ablative) on the same side of the noun make a compound case marker, 'in-to' > illative, 'on-from' >
    delative (`LOCAL_SERIES`), with chance `p` for each missing member: the region marker stays next to the stem, the
    directional one outside it, at the looser of the two levels. True when a member formed."""
    lv = _live_fns(g)
    made = False
    for reg, members in LOCAL_SERIES.items():
        r = next((x for x in lv.get(reg, ()) if x.level >= CLITIC and x.form), None)
        if r is None:
            continue
        for dfn, mfn in members.items():
            if mfn in lv or rng.random() >= p:
                continue
            d = next((x for x in lv.get(dfn, ()) if x.level >= CLITIC and x.side == r.side and x.form), None)
            if d is None:
                continue
            form = tuple(r.form) + tuple(d.form) if r.side == "post" else tuple(d.form) + tuple(r.form)
            lvl = min(r.level, d.level, AFFIX)
            gr = Gram(mfn, form, "NP", r.side, lvl, (f"{reg}+{dfn}", "series", "gram"), kyr,
                      [(kyr, f"formed from the {r.info.gloss.split(' (')[0]} and {d.info.gloss} markers")],
                      id=g.new_id(mfn))
            g.grams.append(gr)
            g.events.append((kyr, f"{mfn} {ipa(form)} formed from {reg} + {dfn} (the local-case series)"))
            lv.setdefault(mfn, []).append(gr)
            made = True
    return made


def _person_fill(g: Grammar, rng, lexicon, kyr: float, T: Tables, p: float) -> None:
    """A paradigm with gaps fills one by analogy with its bound members (at their side and commonest level)."""
    if lexicon is None:
        return
    for ser in sorted(SERIES):
        _fill_series(g, rng, lexicon, kyr, T, p, ser)


def _fill_series(g: Grammar, rng, lexicon, kyr: float, T: Tables, p: float, ser: str) -> None:
    bound = [x for x in g.grams if x.live and SERIES_OF.get(x.function) == ser and x.level >= CLITIC]
    if not bound:
        return
    have = {x.function for x in bound}
    gaps = [f for f in SERIES[ser] if f not in have and (f != INCL_FN or _lex_get(lexicon, "WE (INCLUSIVE)") is not None)]
    if not gaps or rng.random() >= p:
        return
    fn = gaps[int(rng.integers(len(gaps)))]
    lv = sorted(x.level for x in bound)[len(bound) // 2]
    side = max(("pre", "post"), key=lambda s: sum(x.side == s for x in bound))
    if _person_member(g, fn, min(lv, AFFIX), side, lexicon, _lex_index(lexicon), kyr, T,
                      "by analogy with the paradigm") is not None and lv >= AFFIX:
        _sync_cells(g)


def step(rng: np.random.Generator, g: Grammar, n_generations: float, inv=None, lexicon=None, l2_share: float = 0.0,
         population: float | None = None, isolation: float = 0.5, kyr: float = 0.0, drift_typology: bool = False,
         rate: float = 1.0, **kw) -> None:
    """Advance the grammar n generations (fractional is fine): recruit, fuse, lose, analogy, class growth, and typology
    drift when `drift_typology` (lect.grammar_step asks for it; `rate` is the lect's own change rate, applied to the drift
    as it is to sound change). Runs in sub-steps of at most CHUNK generations so events
    keep their order inside a long interval. Accepts lect.py's context names too (`l2`, `inventory`)."""
    if inv is None:
        inv = kw.get("inventory")
    if "l2" in kw and not l2_share:
        l2_share = float(kw["l2"])
    if n_generations <= 0:
        return
    realise(g, lexicon)   # (takes in any outside write to the shown typology, a calque on shift, as an aim)
    a = aims(g)
    if lexicon is not None and hasattr(lexicon, "head_first"):
        lexicon.head_first = not a.head_final()   # lexicon compounds follow the head-direction feature
    T = load_tables()
    soc = social_factors(l2_share, population, isolation)
    lean = kw.get("lean") or {}
    if lean:   # (species leanings: `leanings`)
        soc = {**soc, "recruit": soc["recruit"] * lean.get("recruit", 1.0), "fuse": soc["fuse"] * lean.get("fuse", 1.0),
               "redup": lean.get("redup", 1.0)}
    ev_rec, ev_loss, erode = lean.get("evid_recruit", 1.0), lean.get("evid_loss", 1.0), lean.get("erode", 1.0)
    _sync_lexicon(g, lexicon, kyr)
    if inv is not None:
        a["tone"] = "yes" if getattr(inv, "tones", None) else "no"
    idx = None
    chunks = max(1, math.ceil(n_generations / CHUNK))
    dn = n_generations / chunks
    for _ in range(chunks):
        if drift_typology:
            ch = drift(rng, a, dn * max(float(rate), 0.0), l2_share, T)
            for name, old, new in ch:
                g.events.append((kyr, f"typology {name}: {old} > {new}"))
            if ch:
                _follow_syntax(g, kyr)
        # recruit: the ordinary draw, then the aims' pull toward each category they mark and no gram yet realises
        k = int(rng.poisson(dn * RECRUIT * soc["recruit"]))
        for _ in range(k):
            if idx is None:
                idx = _lex_index(lexicon)
            _recruit(rng, g, lexicon, kyr, T, idx, inv, evid_x=ev_rec)
        if PRESSURE > 0:
            for fns in _unrealised(g, a).values():
                boost = max(PULL_BOOST.get(f, 1.0) * (ev_rec if f in EVID_FNS else 1.0) for f in fns) if fns else 1.0
                if rng.random() < _p(PRESSURE * boost * soc["recruit"], dn):
                    if idx is None:
                        idx = _lex_index(lexicon)
                    _recruit(rng, g, lexicon, kyr, T, idx, inv, targets=fns)
        # fuse / lose
        grew_class = False
        changed = False
        for gr in list(g.grams):
            if not gr.live:
                continue
            gr.age_gens += dn
            wanted = _wanted(gr.function, a)
            lx = ev_loss if gr.function in EVID_FNS else 1.0   # (species leaning: evidentials kept)
            if gr.level <= CLITIC and rng.random() < _p(ABANDON * (KEEP.get(gr.function, 1.0) if wanted else 4.0) * lx, dn):
                _lose(g, gr, kyr, "the periphrasis fell out of use")
                changed = True
                continue
            if gr.level >= AFFIX and not wanted and rng.random() < _p(UNWANTED_LOSS * soc["loss"] * lx, dn):
                _lose(g, gr, kyr, "fell out of use (the grammar no longer marks it)")
                changed = True
                continue
            if gr.level >= AFFIX and rng.random() < _p(L2_STRIP * soc["strip"] * lx, dn):
                _lose(g, gr, kyr, "dropped by adult learners")
                changed = True
                continue
            if gr.level == FUSED and rng.random() < _p(LOSS * soc["loss"] * lx * erode, dn):
                _lose(g, gr, kyr, "worn away")
                changed = True
                continue
            if CLITIC <= gr.level <= AFFIX and gr.form and DEGRAM > 0:
                h = (FUSE * gr.info.freq * min(1.0 + gr.age_gens / AGE_SCALE, AGE_CAP) * soc["fuse"]
                     * FUSE_LEVEL[gr.level - 1] * DEGRAM * _degram_bias(g, gr))
                if rng.random() < _p(h, dn):
                    _degram(g, gr, kyr)
                    changed = True
                    continue
            if gr.level < FUSED:
                h = FUSE * gr.info.freq * min(1.0 + gr.age_gens / AGE_SCALE, AGE_CAP) * soc["fuse"] * FUSE_LEVEL[gr.level]
                if gr.side == "pre" and gr.level >= CLITIC:
                    h *= PRE_FUSE   # (a proclitic binds and fuses more slowly than an enclitic: the suffixing preference)
                if rng.random() < _p(h, dn):
                    gr.level += 1
                    gr.history.append((kyr, f"now {LEVELS[gr.level]}"))
                    if gr.level == CLITIC:
                        # (a clitic has no stress of its own: it keeps one syllable of its word, PW-1570; Spanish
                        # nosotros > nos, Latin illum > lo, English them > 'em)
                        eroded = clip_syllables(gr.form, 1)
                        if eroded and eroded != tuple(gr.form):
                            gr.history.append((kyr, f"eroded {ipa(gr.form)} > {ipa(eroded)}"))
                            gr.form = eroded
                    if gr.level == CLITIC and gr.function in SERIES_OF:
                        _person_set(g, gr, rng, lexicon, kyr, T)
                    if gr.level == AFFIX:
                        eroded = first_syllable(gr.form)
                        if eroded != tuple(gr.form):
                            gr.history.append((kyr, f"eroded {ipa(gr.form)} > {ipa(eroded)}"))
                        gr.form = eroded
                        # a newer marker that binds retires an older one with the same function (renewal)
                        for old in g.grams:
                            if old is not gr and old.live and old.function == gr.function:
                                _lose(g, old, kyr, f"replaced by {ipa(gr.form)}")
                        if gr.function.startswith("CLASS"):
                            grew_class = True
                        if not _wanted(gr.function, a):
                            _adopt(g, gr, kyr)
                    g.events.append((kyr, f"{gr.function} {ipa(gr.form)} is now {LEVELS[gr.level]}"))
                    changed = True
        if PERSON_FILL > 0:
            _person_fill(g, rng, lexicon, kyr, T, _p(PERSON_FILL * soc["recruit"], dn))
        if LOCAL_FORM > 0 and _local_series(g, rng, kyr, _p(LOCAL_FORM * soc["recruit"], dn)):
            changed = True
        if grew_class and g.class_system is not None and rng.random() < CLASS_GROW:
            add_class(g, rng, inv, lexicon, kyr)
        if changed:
            _sync_cells(g)
        # analogy
        for ex in g.exemplars:
            for key, cell in list(ex.cells.items()):
                if not _irregular(ex, key, g):
                    continue
                fused = any((x := _gram_for(g, f)) is not None and x.level >= FUSED for f in key)
                if rng.random() < _p(ANALOGY * soc["analogy"] * (0.3 if fused else 1.0), dn):
                    analogy(g, ex, key, kyr)
        _check_lost(g, kyr)
        _processes(g, rng, kyr, dn, soc, lexicon, inv, kw.get("lect"))
    realise(g, lexicon)


def analogy(g: Grammar, ex: Exemplar, key: tuple[str, ...], kyr: float) -> None:
    """Level one cell back to lemma + regular affixes; recorded as an `analogy` event."""
    old = ex.cells.get(key, ())
    ex.set(key, build_parts(ex, key, g))
    g.events.append((kyr, f"analogy: {ex.concept} {'.'.join(key)} {ipa(old)} > {ipa(ex.cells[key])}"))


def _check_lost(g: Grammar, kyr: float) -> None:
    """An empty gram survives (as fused) while some cell still differs from its base (umlaut-style stem marking); otherwise
    it is lost. Same-slot grams that sound change made identical merge (syncretism): the rarer goes."""
    changed = False
    for gr in g.grams:
        if not gr.live or len(gr.form) > 0:
            continue
        carried = False
        for ex in g.exemplars:
            for key, cell in ex.cells.items():
                if gr.function in key:
                    base_key = tuple(f for f in key if f != gr.function)
                    base = ex.cells.get(base_key, tuple(ex.stem)) if base_key else tuple(ex.stem)
                    if cell != base:
                        carried = True
        if carried and gr.level >= AFFIX:
            if gr.level != FUSED:
                gr.level = FUSED
                gr.history.append((kyr, "affix gone; marked only by the stem"))
            _stem_change(g, gr, kyr)
        else:
            _lose(g, gr, kyr, "eroded to nothing")
            changed = True
    live = {x.function for x in g.grams if x.live}
    for gr in g.grams:   # (a portmanteau lives only while both its categories do)
        if gr.live and "+" in gr.function and not all(f in live for f in gr.function.split("+")):
            _lose(g, gr, kyr, "one of its two categories is gone")
            for f in gr.function.split("+"):
                _rebuild_fn(g, f)
            changed = True
    seen: dict[tuple, Gram] = {}
    for gr in sorted(g.live(), key=lambda x: -x.info.freq):
        if gr.level < AFFIX or not gr.form or "+" in gr.function:
            continue
        key = (gr.host[0], gr.side, gr.info.slot, tuple(gr.form))
        if key in seen and not gr.function.startswith("CLASS"):
            # syncretism (grammar C): the two categories keep one form, as Latin dative and ablative plural -is; the
            # rarer is lost only half the time (before 2026-11-08 always)
            first = seen[key]
            tag = f"syncretic with {first.function}"
            if any(tag in h[1] for h in gr.history):
                continue
            if zlib.crc32(f"{gr.id}|{first.id}".encode()) % 2:
                gr.history.append((kyr, tag))
                g.events.append((kyr, f"syncretism: {gr.function} and {first.function} share the form {ipa(gr.form)}"))
            else:
                _lose(g, gr, kyr, f"merged with {first.function}")
                changed = True
        else:
            seen.setdefault(key, gr)
    if changed:
        _sync_cells(g)
        realise(g)


@lru_cache(maxsize=256)
def _takes_stem_index(fn) -> bool:
    """Does a rule callable accept a second argument / `stem_index` keyword (root-controlled harmony)?"""
    import inspect  # noqa: PLC0415
    try:
        ps = list(inspect.signature(fn).parameters.values())
    except (TypeError, ValueError):
        return False
    if any(p.name == "stem_index" or p.kind == p.VAR_KEYWORD for p in ps):
        return True
    pos = [p for p in ps if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    return len(pos) >= 2 or any(p.kind == p.VAR_POSITIONAL for p in ps)


def _stem_offset(parts: tuple[tuple[str, Form], ...]) -> int:
    """Index of the stem's first segment in a cell's flat form."""
    off = 0
    for lab, f in parts:
        if lab == "stem":
            return off
        off += len(f)
    return 0


def apply_rule_to_grammar(g: Grammar, rule_apply_fn: Callable[[Form], Form], rule_id: str = "?",
                          kyr: float = 0.0) -> int:
    """Run one sound change over every live gram form, exemplar stem and cell, and helper form. Cells change as wholes, so
    a rule conditioned across the stem-affix boundary leaves the cell different from stem + affix: an alternation. When the
    rule callable takes a second argument (`stem_index`, rules.apply), each cell passes the offset of its stem morph, so
    vowel harmony is controlled by the root. A stem or helper the rule would delete whole keeps a minimal form
    (`minimal_form`, as the lexicon does); a cell keeps minimal stem + affixes; a gram worn to nothing goes through the
    loss path (`_check_lost`). Returns the number of forms changed; the ids of grams whose form changed are in
    `g.last_changed` (and in each gram's history)."""
    changed = []
    n = 0
    cache: dict[tuple, Form] = {}
    with_stem = _takes_stem_index(rule_apply_fn)

    def run(f: Form, stem_index: int = 0) -> Form:
        nonlocal n
        f = tuple(f)
        key = (f, stem_index) if with_stem else (f,)
        out = cache.get(key)
        if out is None:
            out = cache[key] = tuple(rule_apply_fn(f, stem_index) if with_stem else rule_apply_fn(f))
        if out != f:
            n += 1
        return out

    for ex in g.exemplars:
        old_stem = tuple(ex.stem)
        new_stem = run(old_stem)
        if not new_stem and old_stem:
            new_stem = minimal_form(old_stem)
            g.events.append((kyr, f"{ex.concept}: stem {ipa(old_stem)} kept minimal as {ipa(new_stem)} ({rule_id})"))
        elif any(_is_v(x) for x in old_stem) and not any(_is_v(x) for x in new_stem):
            new_stem = old_stem   # (minimal word, as lexicon.apply_rule_to_lexicon: a stem keeps its vowel)
        ex.stem = new_stem
        for k in list(ex.cells):
            old = ex.cells[k]
            nf = run(old, _stem_offset(ex.parts[k]))
            if not nf and old:   # the whole cell would vanish: the stem survives minimally, each affix as the rule leaves it
                ex.set(k, tuple((lab, tuple(ex.stem) if lab == "stem" else tuple(rule_apply_fn(tuple(f))))
                                for lab, f in ex.parts[k]))
            elif nf != old:
                ex.set(k, _resplit(ex.parts[k], nf))
    # gram forms: a free word or clitic changes on its own; a bound gram's form is the realisation its cells show most
    # (what a learner would extract), the isolated form breaking ties
    for gr in g.grams:
        if not gr.live:
            continue
        if not gr.form:
            continue   # worn to nothing (marked only by the stem): sound change cannot give it a form back; renewal is a
                       # new periphrasis, recruited as a new Gram (`_recruit`)
        alone = tuple(rule_apply_fn(tuple(gr.form)))
        new = alone
        if gr.level >= AFFIX:
            seen: dict[Form, int] = {}
            ic = (g.processes.get("iclass") or {}).get(gr.function) if gr.alt else None
            for ex in g.exemplars:
                if ic and iclass_member(ic, ex.concept):
                    continue   # (a second-class cell shows the other form)
                for k in ex.parts:
                    f = ex.morph(k, gr.function)
                    if f is not None and _gram_for(g, gr.function) is gr:
                        seen[f] = seen.get(f, 0) + 1
            if seen:
                top = max(seen.values())
                best = [f for f, c in seen.items() if c == top]
                new = alone if alone in best else min(best, key=lambda f: (len(f), ipa(f)))
        if gr.alt:
            gr.alt = tuple(rule_apply_fn(tuple(gr.alt))) or tuple(gr.alt[-1:])
        if new != tuple(gr.form):
            gr.history.append((kyr, f"sound:{rule_id} {ipa(gr.form)} > {ipa(new)}"))
            gr.form = new
            changed.append(gr.id)
    for role, (c, f) in list(g.helpers.items()):
        nf = run(f)
        g.helpers[role] = (c, nf if nf or not f else minimal_form(f))
    g.last_changed = changed
    _check_lost(g, kyr)
    return n + len(changed)


# --------------------------------------------------------------------------------------------------------------------
# Measured complexity
# --------------------------------------------------------------------------------------------------------------------


def complexity(g: Grammar) -> dict:
    """Measured, never stored. obligatory = functions with a bound (level 2-3) gram; mean_level over live grams;
    allomorphy = exemplar cells that differ from today's stem + affixes (stem or affix alternants); classes = live class
    markers (bound ones counted apart); score = a scalar summary for checks."""
    live = g.live()
    bound_fns = {gr.function for gr in live if gr.level >= AFFIX and "+" not in gr.function}
    n_cells = sum(len(ex.cells) for ex in g.exemplars)
    allo = sum(1 for ex in g.exemplars for k in ex.cells if _irregular(ex, k, g))
    stem_alt = sum(1 for ex in g.exemplars for k in ex.cells
                   if tuple(s for lab, f in ex.parts[k] if lab == "stem" for s in f) != tuple(ex.stem))
    cls = [gr for gr in live if gr.function.startswith("CLASS")]
    # (grammar C: free clause particles, a question word or a copula, are syntax: they leave the binding mean alone)
    infl = [gr for gr in live if not (gr.level == FREE and gr.info.slot == "clause")]
    mean_level = float(np.mean([gr.level for gr in infl])) if infl else 0.0
    out = {
        "obligatory": len(bound_fns),
        "live_grams": len(live),
        "mean_level": round(mean_level, 3),
        "fused": sum(1 for gr in live if gr.level == FUSED),
        "cells": n_cells,
        "allomorphy": allo,
        "stem_alternations": stem_alt,
        "allomorphy_share": round(allo / n_cells, 3) if n_cells else 0.0,
        "classes": len(cls),
        "classes_bound": sum(1 for gr in cls if gr.level >= AFFIX),
        "portmanteaus": sum(1 for gr in live if "+" in gr.function),
        "inflection_classes": sum(1 for gr in live if gr.alt),
    }
    out["score"] = round(out["obligatory"] + mean_level + 4.0 * out["allomorphy_share"] + 0.5 * out["classes_bound"], 3)
    return out


# --------------------------------------------------------------------------------------------------------------------
# Names through grammar
# --------------------------------------------------------------------------------------------------------------------


def _name(words: list[Form], pattern: str, gloss: str) -> dict:
    form = tuple(s for w in words for s in w)
    return {"form": form, "words": words, "ipa": " ".join(ipa(w) for w in words), "pattern": pattern, "gloss": gloss}


def _with_gram(root: Form, gr: Gram) -> tuple[list[Form], str]:
    """Free markers stand as their own word; clitics and affixes attach."""
    if gr.level == FREE:
        words = [tuple(gr.form), root] if gr.side == "pre" else [root, tuple(gr.form)]
        return words, f"{gr.function} particle"
    return [_attach(root, gr.form, gr.side)], f"{gr.function} {LEVELS[gr.level]}"


def compound(a, b, g: Grammar) -> Form:
    """Compound of head `a` and modifier `b`: head-initial languages put the head first (a+b), head-final last (b+a)."""
    fa, fb = _form(a), _form(b)
    return fa + fb if not g.typology.head_final() else fb + fa


def people_set(root_word, g: Grammar, inv=None, lexicon=None) -> dict:
    """Land / people / person / language from one root. With a noun-class system the class markers make the set
    (Buganda / Baganda / Muganda / Luganda); otherwise PL for the people, AGENT (or DIM) for a person, PLACE (or LOC) for
    the land, and a 'speech of' compound for the language. Each value: {form, words, ipa, pattern, gloss}."""
    root = _form(root_word)
    out: dict[str, dict] = {}
    cs = g.class_system

    def by_class(group: str):
        if cs is None:
            return None
        c = cs.by_group(group)
        gr = g.by_id(c.gram_id) if c else None
        return gr if gr is not None and gr.live and gr.form else None

    def helper(role: str) -> Form:
        if lexicon is not None:
            key, w = _find(lexicon, _lex_index(lexicon), _HELPER_ROLES[role])
            if w is not None:
                return _form(w)
        return tuple(g.helpers.get(role, ("?", ()))[1])

    def via(keys: list[tuple[str, str]], fallback):
        for kind, name in keys:
            gr = by_class(name) if kind == "class" else g.gram(name)
            if gr is not None and gr.form:
                words, pat = _with_gram(root, gr)
                return words, ("class " + name + ": " + pat) if kind == "class" else pat
        return fallback()

    w, p = via([("class", "person"), ("gram", "AGENT"), ("gram", "DIM")],
               lambda: ([compound(helper("person"), root, g)], "compound with 'person'"))
    out["person"] = _name(w, p, "a person of the people")
    w, p = via([("class", "people"), ("gram", "PL")], lambda: ([root], "bare root"))
    out["people"] = _name(w, p, "the people")
    w, p = via([("class", "place"), ("class", "abstract"), ("gram", "PLACE"), ("gram", "LOC")],
               lambda: ([compound(helper("land"), root, g)], "compound with 'land'"))
    out["land"] = _name(w, p, "their land")
    w, p = via([("class", "manner")], lambda: ([compound(helper("speech"), root, g)], "compound 'speech of'"))
    out["language"] = _name(w, p, "their language")
    return out


def place_name(base_word, g: Grammar, loc: bool = True) -> dict:
    """A place name from a base: the LOC gram at its level (free: a separate word; clitic or affix: attached), else the
    PLACE derivation, else the bare base."""
    base = _form(base_word)
    if loc:
        for fn in ("LOC", "PLACE"):
            gr = g.gram(fn)
            if gr is not None and gr.form:
                words, pat = _with_gram(base, gr)
                return _name(words, pat, f"at {fn.lower()}")
    return _name([base], "bare", "place")


# --------------------------------------------------------------------------------------------------------------------
# Output: paradigm table, JSON, plain-word description
# --------------------------------------------------------------------------------------------------------------------


def paradigm_table(g: Grammar) -> dict:
    """{'nouns'|'verbs': {'columns': [...], 'rows': [{'concept', 'cells': {col: ipa}}]}, 'periphrastic': [...]}.
    Columns are cell keys joined by '.'; 'lemma' is the bare stem. Free and clitic grams are listed as periphrases."""
    out: dict[str, Any] = {}
    for pos, label in (("N", "nouns"), ("V", "verbs")):
        exs = [e for e in g.exemplars if e.pos == pos]
        cols = ["lemma"]
        for e in exs:
            for k in e.cells:
                c = ".".join(k)
                if c not in cols:
                    cols.append(c)
        rows = []
        for e in exs:
            cells = {"lemma": ipa(e.stem)}
            for k, f in e.cells.items():
                cells[".".join(k)] = ipa(f)
            irregular = [".".join(k) for k in e.cells if _irregular(e, k, g)]
            segmented = {".".join(k): "-".join(ipa(m) for _, m in e.parts[k] if m) for k in e.cells}
            rows.append({"concept": str(e.concept), "cells": cells, "segmented": segmented, "irregular": irregular})
        out[label] = {"columns": cols, "rows": rows}
    out["periphrastic"] = [{"function": gr.function, "ipa": ipa(gr.form), "level": gr.level, "side": gr.side,
                            "host": gr.host} for gr in g.live() if gr.level < AFFIX]
    return out


def _seg_to_json(s) -> Any:
    if dataclasses.is_dataclass(s):
        d = {}
        for f in dataclasses.fields(s):
            if not f.init:   # (Segment's cached hash)
                continue
            v = getattr(s, f.name)
            if f.name == "kind" or v != f.default:
                d[f.name] = v
        return d
    return {"ipa": ipa((s,))}


def _seg_from_json(d: dict):
    p = _percepts()
    if "ipa" in d and len(d) == 1 and p is not None:
        return tuple(p.from_ipa(d["ipa"]))[0]
    if p is None:
        raise RuntimeError("percepts module needed to read segments")
    return p.Segment(**d)


def _fj(form) -> list:
    return [_seg_to_json(s) for s in form]


def _ff(lst) -> Form:
    return tuple(_seg_from_json(d) for d in lst)


def to_json(g: Grammar) -> dict:
    return {
        "typology": dict(g.typology),
        "aims": dict(aims(g)),
        "grams": [{"id": gr.id, "function": gr.function, "form": _fj(gr.form), "form_ipa": ipa(gr.form), "host": gr.host,
                   "side": gr.side, "level": gr.level, "source": list(gr.source), "born_kyr": gr.born_kyr,
                   "age_gens": gr.age_gens, "history": [list(h) for h in gr.history],
                   **({"alt": _fj(gr.alt)} if gr.alt else {})} for gr in g.grams],
        "exemplars": [{"concept": e.concept, "pos": e.pos, "stem": _fj(e.stem),
                       "cells": [{"key": list(k), "ipa": ipa(f),
                                  "parts": [[lab, _fj(m)] for lab, m in e.parts[k]]} for k, f in e.cells.items()]}
                      for e in g.exemplars],
        "class_system": None if g.class_system is None else {
            "kind": g.class_system.kind,
            "classes": [{"k": c.k, "group": c.group, "gram_id": c.gram_id} for c in g.class_system.classes]},
        "helpers": {r: {"concept": c, "form": _fj(f)} for r, (c, f) in g.helpers.items()},
        "events": [list(e) for e in g.events],
        "processes": {k: (dict(v) if isinstance(v, dict) else v) for k, v in g.processes.items()},
        "n": g._n,
        "complexity": complexity(g),
    }


def from_json(d: dict) -> Grammar:
    g = Grammar(typology=Typology(d["typology"]))
    g.aims, g.shown = Typology(d.get("aims") or d["typology"]), dict(d["typology"])
    for x in d["grams"]:
        g.grams.append(Gram(x["function"], _ff(x["form"]), x["host"], x["side"], x["level"], tuple(x["source"]),
                            x["born_kyr"], [tuple(h) for h in x["history"]], x.get("age_gens", 0.0), x["id"],
                            _ff(x.get("alt") or [])))
    for x in d["exemplars"]:
        ex = Exemplar(x["concept"], x["pos"], _ff(x["stem"]))
        for c in x["cells"]:
            ex.set(tuple(c["key"]), tuple((lab, _ff(m)) for lab, m in c["parts"]))
        g.exemplars.append(ex)
    cs = d.get("class_system")
    if cs:
        g.class_system = ClassSystem(cs["kind"], [NounClass(c["k"], c["group"], c["gram_id"]) for c in cs["classes"]])
    g.helpers = {r: (v["concept"], _ff(v["form"])) for r, v in d.get("helpers", {}).items()}
    g.events = [tuple(e) for e in d.get("events", [])]
    g.processes = _copy.deepcopy(d.get("processes") or {})
    g._n = d.get("n", len(g.grams))
    return g


_ORDER_WORDS = {
    "adposition": {"post": "postpositions", "pre": "prepositions", "mixed": "both pre- and postpositions",
                   "none": "no adpositions"},
    "genitive": {"GN": "possessor before the noun", "NG": "possessor after the noun", "mixed": "possessor either side"},
    "adjective": {"AN": "adjectives before the noun", "NA": "adjectives after the noun", "mixed": "adjectives either side"},
    "relative": {"NRel": "relative clauses after the noun", "RelN": "relative clauses before the noun",
                 "other": "relative clauses of other kinds"},
}


def _origin(gr: Gram) -> str:
    src, pid, kind = (tuple(gr.source) + ("concept",))[:3]
    if kind == "coin":
        return "a newly coined word"
    if src == "?" or kind == "unknown":
        return "of unknown origin"
    if kind == "gram":
        return f"once the {func_info(src).gloss} marker"
    return f"once the word for '{src.lower()}'"


def describe(g: Grammar) -> list[str]:
    """Plain-word lines for the workbench ("Nouns take a plural suffix -ka, once the word for 'many'")."""
    t = g.typology
    lines = [f"Basic order {t.get('word_order')}, {_ORDER_WORDS['adposition'].get(t.get('adposition'), '')}, "
             f"{_ORDER_WORDS['genitive'].get(t.get('genitive'), '')}, {_ORDER_WORDS['adjective'].get(t.get('adjective'), '')}, "
             f"{_ORDER_WORDS['relative'].get(t.get('relative'), '')}; compounds put the head "
             f"{'last' if t.head_final() else 'first'}."]
    for gr in sorted(g.live(), key=lambda x: (x.host, _slot_rank(x.function), x.function)):
        who = "Nouns" if gr.host[0] == "N" else "Verbs"
        what = gr.info.gloss
        if gr.function.startswith("CLASS") and g.class_system is not None:
            c = next((c for c in g.class_system.classes if c.gram_id == gr.id), None)
            what = f"class marker for {GROUP_GLOSS.get(c.group, c.group) if c else '?'}"
        f = ipa(gr.form)
        if gr.level == FREE:
            how = f"a {what} word {f} {'before' if gr.side == 'pre' else 'after'} them"
        elif gr.level == CLITIC:
            how = f"a {what} clitic {f + '=' if gr.side == 'pre' else '=' + f}"
        elif gr.level == AFFIX:
            how = f"a {what} {'prefix' if gr.side == 'pre' else 'suffix'} {f + '-' if gr.side == 'pre' else '-' + f}"
        elif f:
            how = f"a {what} ending fused with the stem ({f + '-' if gr.side == 'pre' else '-' + f})"
        else:
            how = f"the {what} shown only by a change in the stem"
        if how.startswith("a ") and how[2:3] in ("a", "e", "i", "o", "u"):
            how = "an " + how[2:]
        lines.append(f"{who} take {how}, {_origin(gr)}.")
    if g.class_system is not None and g.class_system.classes:
        lines.append(f"Nouns fall into {len(g.class_system.classes)} classes ("
                     + ", ".join(GROUP_GLOSS.get(c.group, c.group) for c in g.class_system.classes) + ").")
    lost = [gr for gr in g.grams if not gr.live]
    for gr in lost[-3:]:
        when = gr.history[-1][0] if gr.history else gr.born_kyr
        lines.append(f"An older {gr.info.gloss} marker {ipa(gr.form) or '(worn to nothing)'} was lost about {when:g} kyr ago.")
    c = complexity(g)
    lines.append(f"Measured: {c['obligatory']} obligatory categories, mean binding level {c['mean_level']:.1f} of 3, "
                 f"{c['allomorphy']} irregular forms among {c['cells']} paradigm cells.")
    return lines


__all__ = [
    "Typology", "Gram", "Grammar", "Exemplar", "ClassSystem", "NounClass", "Tables", "GPath", "FEATURES", "STABILITY",
    "FUNCS", "load_tables", "copy", "recruit", "draw_typology", "drift", "proto_grammar", "step", "apply_rule_to_grammar", "complexity",
    "people_set", "compound", "place_name", "paradigm_table", "to_json", "from_json", "describe", "add_class",
    "semantic_group", "social_factors", "rebuild", "build_parts", "analogy", "first_syllable", "ipa",
]


# --------------------------------------------------------------------------------------------------------------------
# Grammar phase D processes (2026-11-08): polite address, comparison, differential object marking. First guesses, listed
# for Daniel in for-daniel.md "Grammar phase D and texts".
# --------------------------------------------------------------------------------------------------------------------

#: polite address (T-V; Brown & Gilman 1960; Helmbrecht, WALS 45A: 2-way 24%, several 7%, avoidance 3%, none 66%).
#: Polite second-person pronouns concentrate in large, stratified societies (Eurasian states), so the hazard scales with
#: the social factor `large` (0 up to ~10^4 speakers, 1 from ~10^6); a small community drops it at POLITE_LOSS. The
#: polite form is the plural 'you' (French vous; 70%) or a third person (German Sie, Italian Lei; 30%). The aims then
#: want an honorific verb marker (HON). Stored as `processes["polite"]` {kind, concept} and the aims' `politeness`.
POLITE_MAKE = 0.002
POLITE_LOSS = 0.001
POLITE_KIND = {"plural": 0.7, "third": 0.3}


def _form_of(lexicon, concept):
    w = _lex_get(lexicon, concept)
    return None if w is None else getattr(w, "form", w)


def polite_contrast(lexicon, concept: str) -> bool:
    """Can `concept` ('you all' or 'they') serve as the polite 'you'? Only where it is a word apart from the plain 'you':
    a lect whose 2SG and 2PL fell together (English you, once thou was gone) has no plural to be polite with."""
    a, b = _form_of(lexicon, "THOU"), _form_of(lexicon, concept)
    return a is not None and b is not None and a != b


def _polite(g: Grammar, rng, kyr: float, p_make: float, p_loss: float, lexicon) -> None:
    cur = g.processes.get("polite")
    if cur is None and p_make > 0 and rng.random() < p_make:
        kind = _choice(rng, POLITE_KIND)
        concept = "YOU" if kind == "plural" else "THEY"
        if not polite_contrast(lexicon, concept):   # (polish lane: T-V only where 2SG and the polite form differ)
            return
        g.processes["polite"] = {"kind": kind, "concept": concept}
        g.aims["politeness"] = "binary"
        g.events.append((kyr, f"polite address: '{'you all' if kind == 'plural' else 'they'}' is used to address one "
                              "person with respect"))
    elif cur is not None and lexicon is not None and not polite_contrast(lexicon, cur["concept"]):
        # the plain and the polite 'you' fell together (sound change): the distinction is gone, as English thou / you
        del g.processes["polite"]
        g.aims["politeness"] = "none"
        g.events.append((kyr, "polite address was lost: the plain and the polite 'you' fell together"))
    elif cur is not None and rng.random() < p_loss:
        del g.processes["polite"]
        g.aims["politeness"] = "none"
        g.events.append((kyr, "polite address fell out of use"))


#: comparison (Stassen, WALS 121A: locational 47%, exceed 20%, conjoined 20%, particle 13%). The typology aim
#: `comparative` (Grambank GB265/GB266: exceed / locational / other) picks the construction; "other" splits between
#: the particle type (likelier in VO languages, as in Europe) and the conjoined type ('A is big, B is small'). The
#: construction follows the aim whenever it drifts; an exceed aim with no 'climb'/'jump' verb falls back to locational.
#: The exceed verb is 'climb' or 'jump' ('climb over' > 'exceed'; a guess where the lexicon has no 'surpass').
COMPARE_OTHER = {"conjoined": 0.6, "particle": 0.4}
#: the aim's prior (owner ruling 11-08, PW-1538 D): Stassen's WALS 121A shares; "other" is conjoined 20% + particle 13%,
#: split by COMPARE_OTHER (0.6 / 0.4). Before, the Grambank GB265/GB266 draw gave locational 18%, exceed 34% in a24559.
COMPARE_PRIOR = {"locational": 0.47, "exceed": 0.20, "other": 0.33}
EXCEED_VERBS = ("CLIMB", "JUMP")


def _compare(g: Grammar, rng, kyr: float, lexicon) -> None:
    t = aims(g)
    aim = t.get("comparative") or "locational"
    if aim == "exceed" and lexicon is not None and not any(_lex_get(lexicon, c) is not None for c in EXCEED_VERBS):
        aim = "locational"
    cur = g.processes.get("compare")
    if cur is not None and (cur == aim or (aim == "other" and cur in COMPARE_OTHER)):
        return
    if aim == "other":
        w = dict(COMPARE_OTHER)
        if t.ov() == "VO":
            w["particle"] *= 2.0
        kind = _choice(rng, w)
    else:
        kind = aim
    if cur is not None:
        g.events.append((kyr, f"comparison changed from the {cur} type to the {kind} type"))
    g.processes["compare"] = kind


#: differential object marking (Bossong 1985; Aissen 2003): the accusative marks only objects high on the animacy
#: hierarchy (human and animal), as Spanish a and Hindi ko. It arises where an accusative is live, more often when the
#: accusative came from a dative (X23; that is how Spanish a and Hindi ko began), and spreads to all objects (the
#: marker generalizes) at DOM_LOSS.
DOM_MAKE = 0.0015
DOM_LOSS = 0.0006


def _dom(g: Grammar, rng, kyr: float, lv: dict, p_make: float, p_loss: float) -> None:
    acc = lv.get("ACC")
    cur = g.processes.get("dom")
    if not acc:
        if cur:
            del g.processes["dom"]
        return
    from_dat = any(x.source[1] == "X23" for x in acc)
    if cur is None and rng.random() < p_make * (4.0 if from_dat else 1.0):
        g.processes["dom"] = "animate"
        g.events.append((kyr, "the accusative now marks only animate objects (differential object marking)"))
    elif cur is not None and rng.random() < p_loss:
        del g.processes["dom"]
        g.events.append((kyr, "the accusative spread to every object"))
