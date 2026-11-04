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

import csv
import dataclasses
import math
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

RECRUIT = 0.015        # new periphrasis per generation, before social factors (~1 per 65 gens ~ 1.7 kyr at 25 yr)
FUSE = 0.012           # one step down the ladder per generation for an average gram (~80 gens ~ 2 kyr per step)
FUSE_LEVEL = (1.0, 0.7, 0.06)   # multiplier for 0->1, 1->2, 2->3 (binding is fast; true fusion with the stem is slow)
AGE_SCALE = 200.0      # generations; fusion hazard x (1 + age/AGE_SCALE), capped at AGE_CAP
AGE_CAP = 2.0
ABANDON = 0.002        # an optional periphrasis (level 0-1) falls out of use; x4 when the typology no longer wants it
LOSS = 0.002          # a fused gram (level 3) is lost outright
L2_STRIP = 0.012       # bound gram (level >= 2) dropped by adult learners, x l2_share^2
ANALOGY = 0.003        # one irregular cell levelled per generation (high-frequency exemplars: half-life ~ 230 gens)
CLASS_GROW = 0.5       # chance a fusing class marker recruits a further class
CHUNK = 10.0           # generations per internal sub-step

PATH_FREQ_WEIGHT = {"very common": 3.0, "common": 2.0, "attested": 1.0}

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
}
CLASS_INFO = FuncInfo("N", "dem", 1.3, "class", "noun class")

# affix order, innermost first (Bybee 1985 relevance: derivation, valence, aspect, tense, mood, person; number before case)
SLOT_ORDER = ("deriv", "class", "number", "det", "case", "valence", "aspect", "tense", "mood", "polarity", "person")

#: noun-class groups, Bantu-like but generic, in the order a growing class system adds them
CLASS_GROUPS = ("person", "people", "manner", "abstract", "plant", "animal", "liquid", "place", "small")
GROUP_GLOSS = {
    "person": "a single person", "people": "people (plural of persons)", "manner": "languages, ways and tools",
    "abstract": "lands, qualities and abstractions", "plant": "trees and plants", "animal": "animals",
    "liquid": "liquids and masses", "place": "places", "small": "small things",
    "masculine": "men and male things", "feminine": "women and female things",
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
)
#: path source texts that are grams, not words (reanalysis: the gram changes function)
_GRAM_SOURCES = {"PERFECT": "PERF", "PROGRESSIVE": "PROG", "ALLATIVE": "ALL", "ABLATIVE": "ABL", "DEFINITE ARTICLE": "DEF",
                 "COMITATIVE": "COM", "REFLEXIVE": "REFL"}
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
    "MAKE": ("DO OR MAKE",), "DO": ("DO OR MAKE",), "ALL": ("ALL",),
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
)


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

#: per-generation flip hazard by class (a flip re-draws the value, which may come back the same)
STABILITY = {"very_stable": 2e-4, "stable": 5e-4, "medium": 1e-3, "fickle": 2.5e-3, "very_fickle": 4e-3}
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
    if name == "comparative":
        if _bern(rng, p("GB265", ("GB266",))):
            return "exceed"
        return "locational" if _bern(rng, p("GB266", ("GB265",))) else "other"
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


def drift(rng: np.random.Generator, typ: Typology, n_generations: float, l2_share: float = 0.0,
          table: Tables | None = None, kyr: float | None = None, **kw) -> list[tuple[str, str, str]]:
    """Flip features at their stability-class hazard over n generations; a flip re-draws the value conditional on the rest
    (so harmonies re-assert themselves after a word-order change). Adult L2 learners raise every hazard (x(1 + l2)) and pull
    re-drawn morphological features to their simplest value with probability l2/2. Mutates `typ`; returns the changes."""
    T = table if table is not None else load_tables()
    if "l2" in kw and not l2_share:
        l2_share = float(kw["l2"])
    if isinstance(typ, Grammar):   # lect.py hands the whole grammar: drift its typology and log the flips
        gr = typ
        ch = drift(rng, gr.typology, n_generations, l2_share, T)
        gr.events += [(kyr if kyr is not None else 0.0, f"typology {n}: {a} > {b}") for n, a, b in ch]
        return ch
    l2 = min(max(float(l2_share), 0.0), 1.0)
    changes = []
    for name, cls in FEATURES:
        lam = STABILITY[cls] * n_generations * (1.0 + l2)
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


def func_info(function: str) -> FuncInfo:
    if function.startswith("CLASS"):
        return CLASS_INFO
    return FUNCS[function]


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
        helpers=dict(g.helpers), events=[], _n=g._n)


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
        "COM": t("case") == "many", "ACC": t("case") != "none" and t("alignment") in ("nom-acc", "split"),
        "ERG": t("case") != "none" and t("alignment") in ("erg-abs", "split"),
        "PAST": t("past") == "marked", "RECPST": t("past") == "marked", "FUT": t("future") == "marked", "PERF": t("perfective") == "marked",
        "IPFV": t("perfective") == "marked", "PROG": t("progressive") == "marked", "HAB": t("habitual") == "marked",
        "EVID.DIR": t("evidentiality") == "direct+indirect", "EVID.REP": t("evidentiality") != "none",
        "NEG": True, "CAUS": t("causative") == "bound", "PASS": t("passive") != "none", "REFL": True,
        "DIM": t("diminutive") == "yes", "AGENT": t("agent_noun") == "yes", "PLACE": True,
    }
    if f in table:
        return bool(table[f])
    if f[0] in "123":
        return t("verb_agreement", "none") != "none" or t("pro_drop") == "yes"
    return True


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
        elif gr.info.slot != "deriv":
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
    return keys


def _gram_for(g: Grammar, function: str) -> Gram | None:
    return g.gram(function, bound=True)


def build_parts(ex: Exemplar, key: tuple[str, ...], g: Grammar) -> tuple[tuple[str, Form], ...]:
    """The regular (agglutinative) morphs of a cell from today's lemma and gram forms: what analogy restores."""
    parts: list[tuple[str, Form]] = [("stem", tuple(ex.stem))]
    for f in key:  # key is inner-first
        gr = _gram_for(g, f)
        if gr is None:
            continue
        if gr.side == "pre":
            parts.insert(0, (f, tuple(gr.form)))
        else:
            parts.append((f, tuple(gr.form)))
    return tuple(parts)


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
    return tuple((lab, tuple(new[bounds[k]:bounds[k + 1]])) for k, (lab, _) in enumerate(parts))


def _sync_cells(g: Grammar) -> None:
    """Add cells for newly bound grams, drop cells whose function has no live gram."""
    for ex in g.exemplars:
        want = set(_cell_keys(ex, g))
        for k in list(ex.cells):
            if k not in want:
                ex.drop(k)
        for k in want:
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
                                                             "STRANGER", "MALE PERSON"):
        return "person"
    if u.startswith(("ANIMAL:", "HERD:")):
        return "animal"
    if u.startswith(("CROP:", "PLANT:")):
        return "plant"
    if u.startswith(("GOD:",)):
        return "person"
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
    for alt in ("abstract", "manner", "plant", "animal"):
        c = cs.by_group(alt)
        if c is not None and alt != "person":
            return c
    return cs.classes[-1]


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
    k = len(cs.classes) + 1
    fn = f"CLASS:{k}"
    key, w = _find(lexicon, _lex_index(lexicon), CLASS_SOURCES.get(group, ()))
    if w is not None:
        form, src = _form(w), (str(key), "G066", "concept")
    else:
        form, src = _draw_morph(rng, inv), ("?", "proto", "unknown")
    form, hist = _recruited_form(form, kyr)
    gr = Gram(fn, form, "N", _side(fn, g.typology), level, src, kyr,
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


def proto_grammar(rng: np.random.Generator, inv, lexicon, typ: Typology | None = None, kyr: float = 20.0) -> Grammar:
    """A first language starts low: 1-3 grams at level 0-1 (likeliest NEG, PL, PAST), from lexical sources when the lexicon
    has one (else of unknown origin), and class markers only if the typology drew gender/classes or classifiers, starting
    as free classifier nouns."""
    if typ is None:
        typ = draw_typology(rng, inv=inv)
    typ = Typology(typ)
    _derive(typ, inv)
    g = Grammar(typology=typ)
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
    return g


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
        "fuse": (1.0 - l2) ** 2 * (1.0 + 0.3 * sg) * (0.6 + 0.8 * iso),
        "loss": (1.0 + 4.0 * l2) * (1.0 - 0.3 * sg) * (1.2 - 0.4 * iso),
        "strip": l2 ** 2,
        "analogy": (1.0 + 2.0 * l2) * (1.0 - 0.3 * sg),
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


def _recruit(rng, g: Grammar, lexicon, kyr: float, T: Tables, idx, inv=None) -> Gram | None:
    live_by_fn: dict[str, list[Gram]] = {}
    for gr in g.live():
        live_by_fn.setdefault(gr.function, []).append(gr)
    cands: list[tuple[float, GPath, Any, Any]] = []
    for p in T.paths:
        tgt = p.target
        if tgt == "RECPST" and "PAST" not in live_by_fn:
            continue   # 'come from' > recent past only beside a past tense (G003); never the plain past
        if tgt == "CLASS":
            if g.class_system is None:
                continue
            w_mult = 1.0
        else:
            cur = live_by_fn.get(tgt, [])
            if cur:
                # renewal: only when the current marker is worn (fused, or down to one segment) and nothing new is pending
                if any(c.level < AFFIX for c in cur) or not all(c.level >= FUSED or len(c.form) <= 1 for c in cur):
                    continue
                w_mult = 0.3
            else:
                w_mult = 1.0
            w_mult *= 1.0 if _wanted(tgt, g.typology) else 0.15
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
    ws = np.array([c[0] for c in cands], dtype=float)
    _, p, a, w = cands[int(rng.choice(len(cands), p=ws / ws.sum()))]
    if p.target == "CLASS":
        nc = add_class(g, rng, inv, lexicon, kyr)
        return g.by_id(nc.gram_id) if nc else None
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
        gr = Gram(p.target, form, info.host, _side(p.target, g.typology), FREE, ("?", p.id, "coin"), kyr,
                  [(kyr, f"coined ({p.id})"), *hist], id=g.new_id(p.target))
        g.grams.append(gr)
        g.events.append((kyr, f"coined a {p.target} marker: {ipa(gr.form)}"))
        return gr
    form, hist = _recruited_form(_form(w), kyr)
    gr = Gram(p.target, form, info.host, _side(p.target, g.typology), FREE, (str(a), p.id, "concept"), kyr,
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
    return _recruit(rng, g, lexicon, kyr, T, _lex_index(lexicon), inv)


def _lose(g: Grammar, gr: Gram, kyr: float, why: str) -> None:
    gr.level = LOST
    gr.history.append((kyr, f"lost: {why}"))
    g.events.append((kyr, f"lost {gr.function} {ipa(gr.form)}: {why}"))
    if gr.function.startswith("CLASS") and g.class_system is not None:
        g.class_system.classes = [c for c in g.class_system.classes if c.gram_id != gr.id]


def step(rng: np.random.Generator, g: Grammar, n_generations: float, inv=None, lexicon=None, l2_share: float = 0.0,
         population: float | None = None, isolation: float = 0.5, kyr: float = 0.0, drift_typology: bool = False,
         **kw) -> None:
    """Advance the grammar n generations (fractional is fine): recruit, fuse, lose, analogy, class growth (and typology
    drift when `drift_typology`; lect.py calls `drift` itself). Runs in sub-steps of at most CHUNK generations so events
    keep their order inside a long interval. Accepts lect.py's context names too (`l2`, `inventory`)."""
    if inv is None:
        inv = kw.get("inventory")
    if "l2" in kw and not l2_share:
        l2_share = float(kw["l2"])
    if n_generations <= 0:
        return
    if lexicon is not None and hasattr(lexicon, "head_first"):
        lexicon.head_first = not g.typology.head_final()   # lexicon compounds follow the head-direction feature
    T = load_tables()
    soc = social_factors(l2_share, population, isolation)
    _sync_lexicon(g, lexicon, kyr)
    if inv is not None:
        g.typology["tone"] = "yes" if getattr(inv, "tones", None) else "no"
    idx = None
    chunks = max(1, math.ceil(n_generations / CHUNK))
    dn = n_generations / chunks
    for _ in range(chunks):
        if drift_typology:
            for name, old, new in drift(rng, g.typology, dn, l2_share, T):
                g.events.append((kyr, f"typology {name}: {old} > {new}"))
        # recruit
        k = int(rng.poisson(dn * RECRUIT * soc["recruit"]))
        for _ in range(k):
            if idx is None:
                idx = _lex_index(lexicon)
            _recruit(rng, g, lexicon, kyr, T, idx, inv)
        # fuse / lose
        grew_class = False
        changed = False
        for gr in list(g.grams):
            if not gr.live:
                continue
            gr.age_gens += dn
            wanted = _wanted(gr.function, g.typology)
            if gr.level <= CLITIC and rng.random() < _p(ABANDON * (1.0 if wanted else 4.0), dn):
                _lose(g, gr, kyr, "the periphrasis fell out of use")
                changed = True
                continue
            if gr.level >= AFFIX and rng.random() < _p(L2_STRIP * soc["strip"], dn):
                _lose(g, gr, kyr, "dropped by adult learners")
                changed = True
                continue
            if gr.level == FUSED and rng.random() < _p(LOSS * soc["loss"], dn):
                _lose(g, gr, kyr, "worn away")
                changed = True
                continue
            if gr.level < FUSED:
                h = FUSE * gr.info.freq * min(1.0 + gr.age_gens / AGE_SCALE, AGE_CAP) * soc["fuse"] * FUSE_LEVEL[gr.level]
                if rng.random() < _p(h, dn):
                    gr.level += 1
                    gr.history.append((kyr, f"now {LEVELS[gr.level]}"))
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
                    g.events.append((kyr, f"{gr.function} {ipa(gr.form)} is now {LEVELS[gr.level]}"))
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
        else:
            _lose(g, gr, kyr, "eroded to nothing")
            changed = True
    seen: dict[tuple, Gram] = {}
    for gr in sorted(g.live(), key=lambda x: -x.info.freq):
        if gr.level < AFFIX or not gr.form:
            continue
        key = (gr.host[0], gr.side, gr.info.slot, tuple(gr.form))
        if key in seen and not gr.function.startswith("CLASS"):
            _lose(g, gr, kyr, f"merged with {seen[key].function}")
            changed = True
        else:
            seen.setdefault(key, gr)
    if changed:
        _sync_cells(g)


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
        alone = tuple(rule_apply_fn(tuple(gr.form)))
        new = alone
        if gr.level >= AFFIX:
            seen: dict[Form, int] = {}
            for ex in g.exemplars:
                for k in ex.parts:
                    f = ex.morph(k, gr.function)
                    if f is not None and _gram_for(g, gr.function) is gr:
                        seen[f] = seen.get(f, 0) + 1
            if seen:
                top = max(seen.values())
                best = [f for f, c in seen.items() if c == top]
                new = alone if alone in best else min(best, key=lambda f: (len(f), ipa(f)))
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
    bound_fns = {gr.function for gr in live if gr.level >= AFFIX}
    n_cells = sum(len(ex.cells) for ex in g.exemplars)
    allo = sum(1 for ex in g.exemplars for k in ex.cells if _irregular(ex, k, g))
    stem_alt = sum(1 for ex in g.exemplars for k in ex.cells if ex.morph(k, "stem") != tuple(ex.stem))
    cls = [gr for gr in live if gr.function.startswith("CLASS")]
    mean_level = float(np.mean([gr.level for gr in live])) if live else 0.0
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
        "grams": [{"id": gr.id, "function": gr.function, "form": _fj(gr.form), "form_ipa": ipa(gr.form), "host": gr.host,
                   "side": gr.side, "level": gr.level, "source": list(gr.source), "born_kyr": gr.born_kyr,
                   "age_gens": gr.age_gens, "history": [list(h) for h in gr.history]} for gr in g.grams],
        "exemplars": [{"concept": e.concept, "pos": e.pos, "stem": _fj(e.stem),
                       "cells": [{"key": list(k), "ipa": ipa(f),
                                  "parts": [[lab, _fj(m)] for lab, m in e.parts[k]]} for k, f in e.cells.items()]}
                      for e in g.exemplars],
        "class_system": None if g.class_system is None else {
            "kind": g.class_system.kind,
            "classes": [{"k": c.k, "group": c.group, "gram_id": c.gram_id} for c in g.class_system.classes]},
        "helpers": {r: {"concept": c, "form": _fj(f)} for r, (c, f) in g.helpers.items()},
        "events": [list(e) for e in g.events],
        "n": g._n,
        "complexity": complexity(g),
    }


def from_json(d: dict) -> Grammar:
    g = Grammar(typology=Typology(d["typology"]))
    for x in d["grams"]:
        g.grams.append(Gram(x["function"], _ff(x["form"]), x["host"], x["side"], x["level"], tuple(x["source"]),
                            x["born_kyr"], [tuple(h) for h in x["history"]], x.get("age_gens", 0.0), x["id"]))
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
