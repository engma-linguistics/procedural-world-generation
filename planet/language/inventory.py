"""Proto-inventories, phonotactics and word shapes (architecture.md section 4).

`draw_inventory` builds a sound system the way PHOIBLE's 2,175 inventories look: consonant and vowel counts from the
PHOIBLE size distribution, segments picked one at a time with weight `freq ** A / (1 + species_cost)` times a feature
economy bonus (a segment that reuses a place, or a manner-and-laryngeal series, the system already has is likelier:
Clements 2003), vowels under a dispersion floor (no two vowel qualities closer than `MIN_V_DIST`; length and nasal
series only on qualities the system has: Liljencrants and Lindblom 1972, Lindblom 1986), tone with PHOIBLE's share of
tonal inventories scaled by the speaker's tone cost and pitch hearing. A species' make costs (`profiles.species_cost`)
shape every pick; an impossible segment (cost inf) is never drawn.

Phonotactics follow sonority sequencing (Clements 1990): onsets rise toward the nucleus by at least `min_rise`, codas
fall away from it, cluster sizes and coda classes by the syllable type (WALS 12A: simple, moderately complex, complex).
`repair` makes any word legal by the cheapest edit in the lect's own style: epenthesis of its commonest high vowel or
deletion (cluster simplification, coda drop).
"""

from __future__ import annotations

import csv
import functools
import math
from dataclasses import dataclass, field
from .percepts import replace  # (PW-1555: the interned Segment's fast path; dataclasses.replace otherwise)
from pathlib import Path

import numpy as np

from .percepts import AXES, SONORITY, Segment, distance, from_ipa, is_liquid, is_nonhuman, parse_segment, to_ipa

DATA = Path(__file__).parent / "data"

A_FREQ = 1.0            # exponent on the PHOIBLE frequency in the pick weight (tuned by tests: top-20 overlap, quartiles)
ECON = 0.6              # feature-economy bonus per shared place and per shared series (saturating)
V_ODDS_CAP = 0.98       # cap on a vowel quality's PHOIBLE frequency in its odds weight f / (1 - f)
MIN_V_DIST = 1.5        # vowel quality floor in (height 0-6, back 0-4 x1.5, round) space
TONAL_SHARE = None      # PHOIBLE share of inventories with tones (read from the sizes table)
STRESS = {"none": 0.20, "weight": 0.24, "initial": 0.19, "penult": 0.27, "final": 0.10}   # WALS 14A (Goedemans & van der
# Hulst), folded; its "no fixed stress" (44%) split (sound lane pass 3): "weight" for quantity-sensitive stress (the Latin
# rule, rules.weight_stress; WALS 15A finds weight-sensitive stress common), "none" for no word stress at all (many tone
# languages, French-type phrase prominence). Before the split "none" meant stressless, so no stress-conditioned change
# (apocope, syncope, reduction) ever ran in 44% of lects while coda losses did.
SYLLABLE_TYPES = {"simple": 0.12, "moderate": 0.56, "complex": 0.32}     # WALS 12A (Maddieson): 61 / 274 / 151 of 486


# --- sonority -----------------------------------------------------------------------------------------------------------

sonority = SONORITY   # V 10 > glide 8 > liquid 7 > nasal 6 > voiced F 5 > F 4 > affricate 3 > voiced P 2 > P 1


MAX_ONSET = 2   # onset and coda clusters of at most two consonants (WALS 12A's "complex" goes higher; the demo keeps them
MAX_CODA = 2    # readable and the reviewers found 3-consonant onsets like vnj- unpronounceable)


def _s_cluster(s1: Segment, s2: Segment) -> bool:
    """s (or sh) + a voiceless plain stop: the one onset that falls in sonority and is still common (sp-, st-, sk-)."""
    return (s1.kind == "C" and s1.manner == 2 and s1.sibilant == 1 and s1.voice == 0 and s1.place in (2, 3)
            and s2.kind == "C" and s2.manner == 0 and s2.voice == 0 and s2.larynx == 0 and s2.place in (0, 1, 2, 5))


def _onset_pair_ok(a: Segment, b: Segment, min_rise: int) -> bool:
    """A two-consonant onset: an obstruent (stop, affricate or fricative) or a nasal before a liquid or glide, rising
    by at least `min_rise` into the nucleus (pl-, kr-, fj-, mw-), or s + voiceless stop (st-). Nothing else: no stop +
    nasal (pn-), no fricative + nasal (vn-), no glottal first member (ʔl-), no clicks."""
    if a == b:
        return False
    if _s_cluster(a, b):
        return True
    if a.manner in (8, 9) or a.place == 8 or a.prenasal or b.manner in (8, 9):
        return False
    sa, sb = sonority(a), sonority(b)
    if sb < 7 or sa > 6:
        return False
    if sa == 6 and sb < 8:
        return False   # nasal only before a glide (mw-, nj-), not before a liquid (ml-)
    return sb - sa >= min_rise


_STRIPPED: dict = {}


def _strip_tone(v: Segment) -> Segment:
    if not v.tone:
        return v
    u = _STRIPPED.get(v)
    if u is None:
        u = _STRIPPED[v] = replace(v, tone=0)
    return u


# --- hiatus (shared with lect.normalize and lect.resolve_hiatus) --------------------------------------------------------

_LEVEL = {7: 0, 1: 1, 2: 2, 3: 3, 6: 4}  # level tones low to high (4 rising, 5 falling are contours)


def _fusible(a, b) -> bool:
    return (a.kind == "V" and b.kind == "V" and a.height == b.height and a.back == b.back and a.round == b.round
            and a.phonation == b.phonation and a.source2 == b.source2 and a.register == b.register)


def _fused_tone(t1: int, t2: int) -> int:
    """The tone of two tone-bearing vowels fused into one: kept when they agree, a contour from two levels (H + L falling,
    L + H rising: tone stability, Goldsmith 1976; Yoruba and Bantu vowel contraction), else the first."""
    if t1 == t2 or not t2:
        return t1
    if not t1:
        return t2
    if t1 in _LEVEL and t2 in _LEVEL:
        return 4 if _LEVEL[t1] < _LEVEL[t2] else 5
    return t1


def fuse_vowels(f: tuple, long_ok: bool = True) -> tuple:
    """Identical vowels side by side are one vowel (Casali 1997: identical-vowel hiatus is resolved nearly everywhere; Old
    Portuguese door > dor 'pain', maa > má 'bad', leer > ler 'read'; Attic e + e > ē): long in a lect with long vowels
    (`long_ok`; or when either was long), short in one without (Portuguese had lost Latin quantity). Nasality spreads to
    the fused vowel; tones fuse by _fused_tone. Returns `f` itself when nothing fuses."""
    n = len(f)
    if n < 2 or not any(_fusible(f[i], f[i + 1]) for i in range(n - 1)):
        return f
    out = [f[0]]
    for x in f[1:]:
        y = out[-1]
        if _fusible(y, x):
            out[-1] = replace(y, length=1 if (long_ok or y.length or x.length) else 0, nasal=max(y.nasal, x.nasal),
                              tone=_fused_tone(y.tone, x.tone), tone2=_fused_tone(y.tone2, x.tone2))
        else:
            out.append(x)
    return tuple(out)


def _diphthong(a, b) -> bool:
    """A falling diphthong (a non-high vowel + a short high vowel of another quality: ai, au, ei, oi, ou) is not hiatus."""
    return b.height >= 5 and a.height < 5 and b.length == 0


def hiatus_in(f) -> int:
    """Hiatus junctions in a form: adjacent vowels that are not a falling diphthong."""
    k = 0
    prev = None
    for x in f:
        if x.kind == "V":
            if prev is not None and not _diphthong(prev, x):
                k += 1
            prev = x
        else:
            prev = None
    return k


def hiatus_count(forms) -> int:
    return sum(hiatus_in(f) for f in forms)


# --- the inventory ------------------------------------------------------------------------------------------------------

@dataclass
class Inventory:
    consonants: list
    vowels: list
    tones: list = field(default_factory=list)       # [] or e.g. [1, 3]
    shapes: dict = field(default_factory=dict)      # syllable template -> weight ("CV", "CVC", "CCV", "V", ...)
    max_onset: int = 1
    max_coda: int = 1
    min_rise: int = 2                               # least sonority rise inside an onset cluster (and fall in a coda)
    coda_class: str = "any"                         # any | sonorant | nasal  (which single consonants may close)
    onset_required: bool = False
    stress: str = "none"
    repair_style: str = "epenthesis"                # epenthesis | deletion
    cost: dict = field(default_factory=dict)        # Segment -> species cost at draw time
    freq: dict = field(default_factory=dict)        # Segment -> PHOIBLE frequency (lexical commonness proxy)
    # allophone (a surface sound in complementary distribution with a commoner close one) -> (its phoneme, or None for an
    # inserted ʔ; the environment test, ALLO_TESTS): consonants and vowels list only the phonemes (phonemic(), observed())
    allophones: dict = field(default_factory=dict)
    # the lect's live phonological rules in order, ((rules.Rule, level), ...), set by phonology.attach; run by realize on
    # every word the lect makes (coinage, derivation, compound, loan, name). Not compared, not in the json.
    live: tuple = field(default=(), compare=False, repr=False)

    def __post_init__(self):
        self._cset = frozenset(self.consonants)
        self._vset = frozenset(self.vowels)
        self._aset = frozenset(self.allophones)

    # phonotactics over natural classes
    def onset_ok(self, cl: tuple) -> bool:
        if len(cl) > min(self.max_onset, MAX_ONSET):
            return False
        if len(cl) <= 1:
            return True
        return _onset_pair_ok(cl[0], cl[1], self.min_rise)

    def coda_ok(self, cl: tuple) -> bool:
        if len(cl) > min(self.max_coda, MAX_CODA):
            return False
        if not cl:
            return True
        first = cl[0]
        if self.coda_class == "nasal" and first.manner != 3:
            return False
        if self.coda_class == "sonorant" and sonority(first) < 6:
            return False
        s = [sonority(c) for c in cl]
        if len(cl) == 2 and s[0] < 6 and not _s_cluster(cl[1], cl[0]):
            return False   # a two-consonant coda opens with a sonorant (-nt, -lk, -rs), or is stop + s (-ks, -ts)
        if len(cl) == 2 and _s_cluster(cl[1], cl[0]):
            return cl[0] != cl[1]
        return all(a - b >= self.min_rise for a, b in zip(s, s[1:])) and len(set(cl)) == len(cl)

    @property
    def _shape_class(self) -> str:
        return "simple" if self.max_onset <= 1 and self.max_coda == 0 else "complex" if self.max_onset >= 3 or self.max_coda >= 2 else "moderate"

    @property
    def tonal(self) -> bool:
        return bool(self.tones)


def segments(inv: Inventory) -> list:
    """Every segment of the inventory (consonants then vowels), for `profiles.hear_word`; in a tonal lect each vowel also
    with each of its tones, so a loan or a name heard by a tone language keeps the nearest tone it has (before, the tone
    was lost in hearing and the lect's default tone put back: sound lane, 2026-11-08)."""
    vs = list(inv.vowels)
    if inv.tones:
        vs = vs + [replace(v, tone=t) for v in inv.vowels if not v.tone for t in inv.tones]
    return list(inv.consonants) + vs


# --- PHOIBLE tables -----------------------------------------------------------------------------------------------------

def _rows(name: str) -> list[dict]:
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader((ln for ln in f if not ln.startswith("#")), delimiter="\t"))


@functools.cache
def phoible_pool() -> tuple[tuple, tuple]:
    """((Segment, freq) consonants, (Segment, freq) vowels) from phoible_segments.tsv, each PHOIBLE segment read whole by
    `parse_segment` (PHOIBLE writes k͡p as "kp" and ᵐb as "mb": read letter by letter they were two segments and the row was
    dropped, so labial-velars and prenasalized stops never entered a proto; sound lane 2026-11-08); diphthongs (not one
    segment) stay out; duplicates (two symbols, one percept) keep the higher frequency."""
    best: dict = {}
    for r in _rows("phoible_segments.tsv"):
        if r["class"] not in ("consonant", "vowel"):
            continue
        try:
            s = parse_segment(r["segment"])
        except Exception:
            continue
        if s is None:
            continue
        if (r["class"] == "vowel") != (s.kind == "V"):
            continue
        f = float(r["frequency"])
        if f > best.get(s, 0.0):
            best[s] = f
    # one percept per printed symbol: PHOIBLE's fine variants (ɲ̟ beside ɲ, u̜ beside u) that the percept space renders
    # with the same IPA would otherwise give an inventory two segments spelled alike
    by_ipa: dict = {}
    for s, f in sorted(best.items(), key=lambda t: -t[1]):
        by_ipa.setdefault(to_ipa(s), (s, f))
    best = {s: f for s, f in by_ipa.values() if from_ipa(to_ipa(s)) == [s]}
    cons = tuple(sorted(((s, f) for s, f in best.items() if s.kind == "C"), key=lambda t: -t[1]))
    vows = tuple(sorted(((s, f) for s, f in best.items() if s.kind == "V"), key=lambda t: -t[1]))
    return cons, vows


@functools.cache
def phoible_sizes() -> dict:
    """measure -> {"stat": {key: value}, "count": (sizes array, fractions array)}."""
    out: dict = {}
    for r in _rows("phoible_inventory_sizes.tsv"):
        d = out.setdefault(r["measure"], {"stat": {}, "count": ([], [])})
        if r["kind"] == "stat":
            d["stat"][r["key"]] = float(r["value"])
        elif r["kind"] == "count":
            d["count"][0].append(int(r["key"]))
            d["count"][1].append(float(r["fraction"]))
    for d in out.values():
        k, f = d["count"]
        f = np.array(f, float)
        d["count"] = (np.array(k, int), f / f.sum() if len(f) else f)
    return out


def _sample_size(rng, measure: str, fallback_median: float) -> int:
    try:
        k, f = phoible_sizes()[measure]["count"]
        if len(k):
            return int(rng.choice(k, p=f))
    except (KeyError, FileNotFoundError):
        pass
    return max(2, int(round(rng.lognormal(math.log(fallback_median), 0.3))))


SIZE_BW = 0.12  # bandwidth (in ln n) of the kernel that smooths PHOIBLE's size counts into a prior
SIZE_FLOOR = 0.25  # pseudo-count (in languages) spread over every size up to 1.5x PHOIBLE's largest: the far tail is rare, not 0


@functools.cache
def _prior(measure: str) -> np.ndarray:
    """PHOIBLE's inventory-size distribution for a measure, smoothed in ln n (SIZE_BW) with a SIZE_FLOOR pseudo-count, as an
    array over sizes 0 .. 1.5 x the largest; sums to 1."""
    k, f = phoible_sizes()[measure]["count"]
    top = int(1.5 * max(k.max(), 2)) + 2
    n = np.arange(top + 1, dtype=float)
    ln = np.log(np.maximum(n, 0.5))
    w = np.zeros(top + 1)
    for size, frac in zip(k, f):
        w += frac * np.exp(-0.5 * ((ln - math.log(max(size, 0.5))) / SIZE_BW) ** 2) / n.clip(1.0)
    w = w / w[1:].sum()
    n_lang = 2175.0
    w = w + SIZE_FLOOR / n_lang / top
    w[0] = 0.0
    w[1] = min(w[1], w[2] * 0.5)
    return w / w.sum()


def size_prior(measure: str, n: int) -> float:
    """Smoothed PHOIBLE probability of an inventory with n segments of a measure ("consonants" | "vowels"); sizes beyond the
    array share its last value (tiny), and n < 1 is impossible (0 -> a tiny floor, so ratios stay finite)."""
    w = _prior(measure)
    if n < 1:
        return 1e-12
    return float(w[min(n, len(w) - 1)])


def size_max(measure: str) -> int:
    return int(phoible_sizes()[measure]["stat"]["max"])


def size_quantiles(measure: str, qs=(0.05, 0.25, 0.5, 0.75, 0.95)) -> list[float]:
    """Quantiles of PHOIBLE's (unsmoothed) size counts for a measure."""
    k, f = phoible_sizes()[measure]["count"]
    c = np.cumsum(f)
    return [float(k[int(np.searchsorted(c, q - 1e-12))]) for q in qs]


TONE_SIMPLE = 0.60   # share of tonal protos with a two-tone (simple) system: WALS 13A, 132 simple of 220 tonal languages; the
# complex rest split by PHOIBLE's counts of 3+ tones (sound lane pass 3; PHOIBLE alone put two tones at 28%, as its sources
# count contour tonemes that WALS folds into simple systems)


def tonal_share() -> float:
    try:
        k, f = phoible_sizes()["tones"]["count"]
        return float(f[k > 0].sum())
    except (KeyError, FileNotFoundError):
        return 0.23


# --- costs --------------------------------------------------------------------------------------------------------------

def _cost(profile, seg) -> float:
    from . import profiles

    if profile is None:
        return float(profiles.human_cost(seg))
    return float(profiles.species_cost(profile, seg))


# non-human percepts PHOIBLE cannot list: variants of common segments a species may make (growl, purr, a second voice).
# Their pseudo-frequency is NONHUMAN_SHARE x the base segment's, divided by the species' make cost for the key.
NONHUMAN_SHARE = 0.25
# A register variant (sub-bass ˯, ultra ˰) rides on vowels: the dragon profile's main claim, a voice partly carried below
# ~20 Hz, appeared in no lect before (phonology-gaps.md 5.4; sound lane 2026-11-08).
_NONHUMAN_VARIANTS = (("harsh", "phonation", 3, "CV"), ("purr", "phonation", 4, "V"), ("source2", "source2", 1, "V"),
                      ("sub_register", "register", -1, "V"), ("ultra_register", "register", 1, "V"))


def _pool_for(profile) -> tuple[tuple, tuple]:
    cons, vows = phoible_pool()
    if profile is None:
        return cons, vows
    extra_c, extra_v = [], []
    for key, axis, val, kinds in _NONHUMAN_VARIANTS:
        mk = (getattr(profile, "make_cost", None) or {}).get(key, math.inf)
        if not math.isfinite(mk):
            continue
        for pool, out, k in ((cons, extra_c, "C"), (vows, extra_v, "V")):
            if k not in kinds:
                continue
            for seg, f in pool[:30]:
                if k == "C" and sonority(seg) < 6:
                    continue   # growl on sonorants (and vowels) only
                out.append((replace(seg, **{axis: val}), f * NONHUMAN_SHARE / max(mk, 1e-6)))
    return cons + tuple(extra_c), vows + tuple(extra_v)


def _vq(v: Segment) -> tuple:
    return (v.height, v.back * 1.5, v.round)


def vowel_distance(a: Segment, b: Segment) -> float:
    """Distance between two vowel *qualities* (length, nasality, tone ignored) for the dispersion floor."""
    qa, qb = _vq(a), _vq(b)
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(qa, qb)))


def _quality(v: Segment) -> Segment:
    return replace(v, length=0, nasal=0, tone=0, phonation=0, source2=0, tone2=0)


# --- series (sound lane, 2026-11-08) ------------------------------------------------------------------------------------
# Languages pick whole sets of sounds, not single sounds: a language has retroflexes (then usually several) or none.
# Drawing segment by segment gets each sound's share right but makes "has at least one of the set" far too common
# (phonology-gaps.md 5.3: any retroflex 75%, any long vowel 77%, implosives 29% of human lects). So the draw first decides
# which series a proto has, each with PHOIBLE's share of inventories holding at least one member (phoible_series.tsv,
# built by tools/language/build_reference_tables.py from the same predicates), then fills places inside the series it
# has with the members' conditional frequency (freq / share). A segment in no series is drawn as before; one in several
# needs all of them. Clicks are their own system (click_system) and are in no series.
SERIES = {
    "labial_velar": lambda s: s.kind == "C" and bool(s.double) and s.manner in (0, 3),
    "prenasal": lambda s: s.kind == "C" and bool(s.prenasal) and s.manner != 8,
    "retroflex": lambda s: s.kind == "C" and bool(s.retroflex),
    "aspirated": lambda s: s.kind == "C" and s.larynx == 1 and s.manner != 8,
    "ejective": lambda s: s.kind == "C" and s.larynx == 2 and s.manner != 8,
    "implosive": lambda s: s.kind == "C" and s.larynx == 3,
    "uvular": lambda s: s.kind == "C" and s.place == 6 and s.manner != 8,
    "pharyngeal": lambda s: s.kind == "C" and s.place == 7,
    "breathy_c": lambda s: s.kind == "C" and s.phonation == 1 and s.manner != 8,
    "creaky_c": lambda s: s.kind == "C" and s.phonation == 2,
    "labialized": lambda s: s.kind == "C" and s.secondary == 1,
    "palatalized": lambda s: s.kind == "C" and s.secondary == 2,
    "velarized": lambda s: s.kind == "C" and s.secondary in (3, 4),
    "geminate": lambda s: s.kind == "C" and s.length == 1,
    "long_v": lambda s: s.kind == "V" and s.length == 1,
    "nasal_v": lambda s: s.kind == "V" and bool(s.nasal),
    "phonation_v": lambda s: s.kind == "V" and s.phonation in (1, 2),
}
SERIES_FILL = 0.75        # share of PHOIBLE's mean member count picked first (the rest come from the free picks)
SERIES_BOOST_MAX = 12.0   # cap on the in-series weight factor (1 / share, multiplied over a segment's series)


def series_of(s: Segment) -> tuple:
    return tuple(k for k, f in SERIES.items() if f(s))


@functools.cache
def series_shares() -> dict:
    """series -> PHOIBLE share of inventories with at least one member (phoible_series.tsv); {} when the table is missing."""
    try:
        return {r["key"]: float(r["value"]) for r in _rows("phoible_series.tsv") if r["kind"] == "series"}
    except FileNotFoundError:
        return {}


@functools.cache
def series_members() -> dict:
    """series -> PHOIBLE's mean member count where the series is present."""
    try:
        return {r["key"]: float(r["extra"]) for r in _rows("phoible_series.tsv") if r["kind"] == "series" and r["extra"]}
    except FileNotFoundError:
        return {}


@functools.cache
def v_ratios() -> dict:
    """vowel series -> PHOIBLE's mean (members / distinct vowel qualities) where present; {} when the table lacks it."""
    try:
        return {r["key"]: float(r["value"]) for r in _rows("phoible_series.tsv") if r["kind"] == "v_ratio"}
    except FileNotFoundError:
        return {}


SIZE_BINS = {"C": (("<=12", 0, 12), ("13-18", 13, 18), ("19-25", 19, 25), ("26+", 26, 10 ** 6)),
             "V": (("<=5", 0, 5), ("6-8", 6, 8), ("9-13", 9, 13), ("14+", 14, 10 ** 6))}   # as the table builder's
SERIES_FLOOR = 0.002      # least share of a series in any size bin (PHOIBLE's empty bins are small samples, not zeros)


def _size_bin(n: int, kind: str) -> str:
    return kind + next(b for b, lo, hi in SIZE_BINS[kind] if lo <= n <= hi)


@functools.cache
def series_bin_shares() -> dict:
    """(series, size bin) -> PHOIBLE share of inventories of that size holding a member: small inventories seldom have a
    series at all (an ejective series in 0 of 134 inventories with at most 12 consonants), big ones often."""
    try:
        out = {}
        for r in _rows("phoible_series.tsv"):
            if r["kind"] == "series_bin" and r["value"]:
                k, b = r["key"].split("|")
                out[(k, b)] = float(r["value"])
        return out
    except FileNotFoundError:
        return {}


def draw_series(rng, nc: int = 21, nv: int = 7) -> frozenset:
    """The series a proto of nc consonants and nv vowels has: each independently with PHOIBLE's share among inventories of
    that size (a species that cannot make any member simply draws none, through the members' cost)."""
    by_bin = series_bin_shares()
    out = []
    for k, sh in sorted(series_shares().items()):
        b = _size_bin(nv, "V") if k.endswith("_v") else _size_bin(nc, "C")
        p = max(by_bin.get((k, b), sh), SERIES_FLOOR)
        if rng.random() < p:
            out.append(k)
    return frozenset(out)


def _series_factor(segs, have: frozenset) -> np.ndarray:
    """Weight factor per pool segment under the drawn series: 0 for a member of a series the proto lacks, 1 / share for
    each series it has (capped), 1 outside every series."""
    sh = series_shares()
    out = np.ones(len(segs))
    if not sh:
        return out
    for i, s in enumerate(segs):
        f = 1.0
        for k in series_of(s):
            if k not in sh:
                continue
            if k not in have:
                f = 0.0
                break
            f /= max(sh[k], 1e-3)
        out[i] = min(f, SERIES_BOOST_MAX)
    return out


# --- drawing an inventory -----------------------------------------------------------------------------------------------

@functools.cache
def _pool_freq() -> dict:
    return {s: f for s, f in phoible_pool()[0] + phoible_pool()[1]}


@functools.cache
def _human_costs(kind: int) -> np.ndarray:
    return np.array([_cost(None, s) for s, _ in phoible_pool()[kind]])


def _base_weights(pool, profile):
    segs = [s for s, _ in pool]
    f = np.array([x for _, x in pool])
    if profile is None:
        cost = _human_costs(0 if pool is phoible_pool()[0] else 1)
    else:
        cost = np.array([_cost(profile, s) for s in segs])
    fin = np.isfinite(cost)
    base = np.where(fin, f ** A_FREQ / (1.0 + np.where(fin, cost, 0.0)), 0.0)
    return segs, base, cost


def _pick_consonants(rng, n: int, profile, have=None) -> tuple[list, dict]:
    pool, _ = _pool_for(profile)
    segs, base, cost = _base_weights(pool, profile)
    if have is not None:
        base = base * _series_factor(segs, have)
    places = np.array([s.place for s in segs])
    _, series = np.unique([f"{s.manner}.{s.voice}.{s.larynx}.{s.secondary}" for s in segs], return_inverse=True)
    cnt_place = np.zeros(places.max() + 1)
    cnt_series = np.zeros(series.max() + 1)
    avail = base > 0
    chosen: list[int] = []

    def pick(mask) -> None:
        w = base * (1 + ECON * np.minimum(cnt_place[places], 3) / 3) * (1 + ECON * np.minimum(cnt_series[series], 3) / 3) * avail * mask
        if w.sum() <= 0:
            return
        i = int(rng.choice(len(w), p=w / w.sum()))
        chosen.append(i)
        avail[i] = False
        cnt_place[places[i]] += 1
        cnt_series[series[i]] += 1

    # the series first: each series the proto has gets about PHOIBLE's mean member count where present (scaled by the
    # consonant count against PHOIBLE's median 21), so a series comes as a set (pʼ tʼ kʼ, ɓ ɗ), not a lone member
    if have:
        mem = series_members()
        for k in sorted(have):
            if k not in mem or k.endswith("_v"):
                continue
            mask = np.array([SERIES[k](x) for x in segs], float)
            if not mask.any():
                continue
            m = max(1, min(int(round(SERIES_FILL * mem[k] * n / 21.0)), n // 3))
            for _ in range(m):
                if len(chosen) >= n:
                    break
                pick(mask)
    one = np.ones(len(segs))
    while len(chosen) < n and avail.any():
        before = len(chosen)
        pick(one)
        if len(chosen) == before:
            break
    return [segs[i] for i in chosen], {segs[i]: float(cost[i]) for i in chosen}


def _pick_vowels(rng, n: int, profile, have=None) -> tuple[list, dict]:
    _, pool = _pool_for(profile)
    segs, base, cost = _base_weights(pool, profile)
    if have is not None:
        base = base * _series_factor(segs, have)
    qual = [_quality(s) for s in segs]
    q_idx = {q: k for k, q in enumerate(dict.fromkeys(qual))}
    qi = np.array([q_idx[q] for q in qual])
    qxyz = np.array([_vq(q) for q in q_idx], float)                      # per distinct quality
    plain = np.array([s == q for s, q in zip(segs, qual)])
    # Qualities are weighted by their PHOIBLE odds f / (1 - f), not f: drawing a handful without replacement by f flattens
    # the shares (i, a, u fall to ~0.86 and ɑ, ə, ɨ rise to twice PHOIBLE's), while odds weights make the draw close to
    # conditional Poisson sampling, whose inclusion shares track f (sound lane pass 2)
    fq = np.array([x for _, x in pool])
    base = np.where(plain, base / (1.0 - np.minimum(fq, V_ODDS_CAP)), base)
    _, series = np.unique([f"{s.length}.{s.nasal}.{s.phonation}" for s in segs], return_inverse=True)
    series_cnt = np.zeros(series.max() + 1)
    have_q = np.zeros(len(q_idx), bool)
    blocked_q = np.zeros(len(q_idx), bool)                               # within the floor of a chosen quality
    avail = base > 0
    chosen: list[int] = []

    def pick(mask) -> bool:
        ok = avail & np.where(plain, ~blocked_q[qi], have_q[qi]) & mask
        if not ok.any():
            return False   # the system is full
        bonus = np.where(plain, 1.0, 1 + ECON * np.minimum(series_cnt[series], 3) / 3)
        w = base * bonus * ok
        i = int(rng.choice(len(w), p=w / w.sum()))
        chosen.append(i)
        avail[i] = False
        if plain[i]:
            have_q[qi[i]] = True
            d = np.sqrt(((qxyz - qxyz[qi[i]]) ** 2).sum(axis=1))
            np.logical_or(blocked_q, d < MIN_V_DIST, out=blocked_q)
        else:
            series_cnt[series[i]] += 1
        return True

    # Vowel series take slots (sound lane pass 2). PHOIBLE's vowel count includes long and nasal vowels, but its number of
    # distinct qualities hardly depends on them (median 6 with or without a long series). So a proto with a vowel series
    # first picks n / (1 + sum of the series' member-per-quality ratios) qualities, then the series members on those
    # qualities; a proto without one spends all n on qualities, as PHOIBLE's series-less inventories do. Before this every
    # slot went to a new quality whenever the plain picks won the weight race, so rare qualities (ɑ, ɤ, ɘ) entered too
    # often (pass 1's overuse regression).
    vser = sorted(k for k in (have or ()) if k.endswith("_v"))
    ratio = v_ratios()
    if vser and ratio:
        nq = max(2, int(round(n / (1.0 + sum(ratio.get(k, 1.0) for k in vser)))))
        while len(chosen) < nq and pick(plain):
            pass
        for k in vser:
            mask = np.array([SERIES[k](x) for x in segs]) & ~plain
            m = max(1, int(round(ratio.get(k, 1.0) * int(have_q.sum()))))
            for _ in range(m):
                if len(chosen) >= n or not pick(mask):
                    break
    allm = np.ones(len(segs), bool)
    while len(chosen) < n and pick(allm):
        pass
    return [segs[i] for i in chosen], {segs[i]: float(cost[i]) for i in chosen}


# Clicks. PHOIBLE lists a click in ~1.5% of its inventories (ǀ alone in 32 of 2175; the table keeps segments in >= 5
# inventories) and those inventories are big (Nama 31 consonants with 20 clicks, Zulu ~45 with 15, !Xóõ 130 with 83): clicks
# come as a system of places x accompaniments, the main source of PHOIBLE's long tail. A human-voiced proto whose drawn
# consonant count is at least CLICK_MIN_C gets one with the probability that makes CLICK_SHARE of all protos click languages;
# about CLICK_PART of its consonants are then clicks. The percept space has the five click places (ʘ ǀ ǃ ǂ ǁ) and the
# accompaniments as its ordinary axes: plain (velar) k-, voiced ɡ-, nasal ŋ- (prenasal), aspirated, glottalized (ejective),
# breathy-voiced.
CLICK_SHARE = 0.015
CLICK_MIN_C = 28
CLICK_PART = 0.45
CLICK_PLACES = ((("ǀ", "ǃ", "ǁ"), 0.5), (("ǀ", "ǃ", "ǁ", "ǂ"), 0.35), (("ǀ", "ǃ", "ǁ", "ǂ", "ʘ"), 0.15))
CLICK_SERIES = ({}, {"voice": 1}, {"prenasal": 1}, {"larynx": 1}, {"larynx": 2}, {"voice": 1, "phonation": 1})
CLICK_LEX_FREQ = 0.5  # lexical commonness of a click inside a click language (inv.freq; PHOIBLE's world share is ~0.01)


def _p_click() -> float:
    k, f = phoible_sizes()["consonants"]["count"]
    big = float(f[k >= CLICK_MIN_C].sum()) or 1.0
    return min(1.0, CLICK_SHARE / big)


def click_system(rng, nc: int) -> list:
    """A click system for an inventory of nc consonants: CLICK_PLACES x as many CLICK_SERIES as fill ~CLICK_PART of nc."""
    from .percepts import from_ipa
    opts = [p for p, _ in CLICK_PLACES]
    places = opts[int(rng.choice(len(opts), p=[w for _, w in CLICK_PLACES]))]
    m = max(1, min(len(CLICK_SERIES), int(round(CLICK_PART * nc / len(places)))))
    out = []
    for sets in CLICK_SERIES[:m]:
        for sym in places:
            out.append(replace(from_ipa(sym)[0], **sets))
    return out


_TONE_SETS = {2: [1, 3], 3: [1, 2, 3], 4: [1, 2, 3, 5], 5: [1, 2, 3, 4, 5], 6: [1, 2, 3, 4, 5, 6],
              7: [1, 2, 3, 4, 5, 6, 7]}   # (6 and 7: Cantonese- and Hmong-size systems, PHOIBLE 6+ about 7%)


# Second-voice tone (syrinx lane, 2026-11-08; docs/review/language/syrinx.md). A syrinx-voiced proto whose vowels include
# second-voice ones gives its second voice a tone of its own with TONE2_SHARE x hear.tone2 / make_cost.tone2; else the
# second voice moves in parallel with the first (tone2 0). The set is drawn from TONE2_SETS: two levels (the simple
# systems, as for the first voice), level / rising / falling (sweeps, what a syrinx does best), or both kinds. The tone is
# stored on the vowel (iᴖ˦, iᴖ˨ are two vowels), so the syllable space multiplies by itself (lexicon._space).
TONE2_SHARE = 0.5
TONE2_SETS = (((3, 1), 0.5), ((3, 4, 5), 0.3), ((1, 3, 4, 5), 0.2))


def draw_tone2(rng, profile, vows: list) -> tuple:
    """The second voice's tone set for a proto with vowels `vows` (empty: no second-voice vowel, or no contrast)."""
    if profile is None or not any(v.source2 for v in vows):
        return ()
    mk = _profile_get(profile, "make_cost", "tone2", math.inf)
    hear = _profile_get(profile, "hear", "tone2", 1.0)
    if not math.isfinite(mk) or hear <= 0 or rng.random() >= min(0.95, TONE2_SHARE * hear / max(mk, 1e-6)):
        return ()
    k = int(rng.choice(len(TONE2_SETS), p=[w for _, w in TONE2_SETS]))
    return TONE2_SETS[k][0]


def _profile_get(profile, attr: str, key: str, default: float) -> float:
    d = getattr(profile, attr, None) or {}
    try:
        return float(d.get(key, default))
    except (TypeError, ValueError):
        return default


def _draw_shapes(rng) -> dict:
    kind = list(SYLLABLE_TYPES)[int(rng.choice(3, p=list(SYLLABLE_TYPES.values())))]
    if kind == "simple":
        shapes = {"CV": 0.85, "V": 0.15}
        mo, mc = 1, 0
    elif kind == "moderate":
        shapes = {"CV": 0.45, "CVC": 0.25, "V": 0.07, "VC": 0.04, "CCV": 0.11, "CCVC": 0.08}
        mo, mc = 2, 1
        if rng.random() < 0.35:   # (C)V(C) without onset clusters
            shapes = {"CV": 0.55, "CVC": 0.33, "V": 0.08, "VC": 0.04}
            mo = 1
    else:
        shapes = {"CV": 0.33, "CVC": 0.29, "V": 0.04, "VC": 0.03, "CCV": 0.13, "CCVC": 0.1, "CVCC": 0.06,
                  "CCVCC": 0.02}
        mo, mc = MAX_ONSET, MAX_CODA
    return {"shapes": shapes, "max_onset": mo, "max_coda": mc, "kind": kind}


def marked_sound(s) -> bool:
    """A marked series member (PW-1537 R3): aspirated or ejective, growled or purred, or a vowel of the sub-bass or ultra
    register. Breathy and creaky voice and implosives are left out: they stand without a plain partner in real
    inventories often enough (Maddieson 1984). Prenasalised stops too (Fijian ᵐb ⁿd have no plain b d): only a
    prenasalised ejective is barred, by rules.impossible."""
    return s.larynx in (1, 2) or s.phonation in (3, 4) or bool(s.register)


def plain_partners(s) -> set:
    """The plain partners of a marked sound at its place (length aside; either voicing for a stop that lost an
    aspirate or ejective mark, so tʰ is partnered by t or d)."""
    p = replace(s, phonation=0 if s.phonation in (3, 4) else s.phonation, register=0, length=0,
                larynx=0 if s.larynx in (1, 2) else s.larynx)
    return {p, replace(p, voice=1 - p.voice)} if s.larynx in (1, 2) else {p}


FILL_MANNERS = (0, 1)   # stops and affricates (lateral affricates aside: `_fill_partners`)


def _fill_partners(rng, cons: list, ccost: dict, profile) -> list:
    """PW-1537 R3, the orphans a proto is drawn with: a marked stop or affricate (kʼ, qʰ, tsʰ) needs a plain partner at
    its place (Maddieson 1984: a marked series member implies the plain one). The draw picks series members and fillers
    independently, so a quarter of human protos had one with no partner (lane 9: aspirates 124, ejectives 75 in 300
    draws), and the marked members overshot PHOIBLE (1500 human draws: pʰ 0.195 against 0.165, tʰ 0.177 against 0.124,
    cʰ 0.073 against 0.027, tsʰ 0.102 against 0.057, tsʼ 0.071 against 0.040). An orphan gives its slot back to the
    ordinary draw (base weights, never another orphan), so sizes hold: pʰ 0.164, tʰ 0.133, kʰ 0.159, tsʰ 0.033, tʃʰ
    0.060, tʃʼ 0.039. Adding the partner instead raised ts, t̪ and c by 7-10 points. Lateral affricates are exempt:
    PHOIBLE has tɬʼ (0.9%) more often than tɬ (0.6%), beside ɬ (Salish, Caucasian)."""
    pool = _pool_for(profile)[0]
    segs, base, _ = _base_weights(pool, profile)
    out = list(cons)

    def orphan(x, have) -> bool:
        return (x.kind == "C" and marked_sound(x) and x.manner in FILL_MANNERS and not x.lateral
                and not (plain_partners(x) & have))

    for s in list(out):
        have = {replace(x, length=0) for x in out}
        if not orphan(s, have):
            continue
        rest = [x for x in out if x != s]
        h2 = {replace(x, length=0) for x in rest}
        w = np.array([b if (x not in rest and x != s and not orphan(x, h2)) else 0.0 for x, b in zip(segs, base)])
        if w.sum() <= 0:
            continue
        p = segs[int(rng.choice(len(w), p=w / w.sum()))]
        i = out.index(s)
        ccost.pop(s, None)
        out[i] = p
        ccost[p] = _cost(profile, p)
    return out


def draw_inventory(rng, profile=None, size_hint=None) -> Inventory:
    """A proto-inventory for a speaker with `profile` (None: human). `size_hint`: (n_consonants, n_vowels), or a scale
    factor on the drawn sizes, or None (PHOIBLE's distribution; fallback lognormal around 22 C / 6 V)."""
    if isinstance(size_hint, tuple):
        nc, nv = size_hint
    else:
        nc = _sample_size(rng, "consonants", 22)
        nv = _sample_size(rng, "vowels", 6)
        if isinstance(size_hint, (int, float)) and size_hint:
            nc, nv = max(4, round(nc * size_hint)), max(2, round(nv * size_hint))
    clicks: list = []
    from .profiles import human_voiced
    if nc >= CLICK_MIN_C and human_voiced(profile) and rng.random() < _p_click():
        clicks = click_system(rng, nc)
    have = draw_series(rng, nc, nv)
    cons, ccost = _pick_consonants(rng, nc - len(clicks), profile, have)
    cons = _fill_partners(rng, cons, ccost, profile)
    if clicks:
        ccost.update({c: _cost(profile, c) for c in clicks})
        cons = cons + [c for c in clicks if c not in cons]
    vows, vcost = _pick_vowels(rng, nv, profile, have)
    # tone
    tones: list = []
    hear = _profile_get(profile, "hear", "tone", 1.0) if profile is not None else 1.0
    mk = _profile_get(profile, "make_cost", "tone", 1.0) if profile is not None else 1.0
    p_tone = 0.0 if not math.isfinite(mk) or hear <= 0 else min(0.95, tonal_share() * hear / max(mk, 1e-6))
    if rng.random() < p_tone:
        k, f = phoible_sizes()["tones"]["count"] if "tones" in phoible_sizes() else (np.array([2, 3]), np.array([.5, .5]))
        m = k >= 2
        p = f[m] / f[m].sum()
        p = np.where(k[m] == 2, TONE_SIMPLE, (1.0 - TONE_SIMPLE) * np.where(k[m] == 2, 0.0, p) / p[k[m] > 2].sum())
        nt = int(rng.choice(k[m], p=p / p.sum()))
        tones = list(_TONE_SETS[min(7, nt)])
    t2 = draw_tone2(rng, profile, vows)
    if t2:
        split = {v: [replace(v, tone2=t) for t in t2] for v in vows if v.source2}
        vows = [x for v in vows for x in split.get(v, [v])]
        for v, xs in split.items():
            vcost.pop(v, None)
            for x in xs:
                vcost[x] = _cost(profile, x)
    sh = _draw_shapes(rng)
    coda = "any"
    if sh["max_coda"] >= 1 and sh["kind"] != "complex":
        coda = str(rng.choice(["any", "sonorant", "nasal"], p=[0.6, 0.25, 0.15]))
    stress = str(rng.choice(list(STRESS), p=list(STRESS.values())))
    pc, pv = _pool_for(profile)
    pool_f = {s: f for s, f in pc + pv}
    inv = Inventory(
        consonants=cons, vowels=vows, tones=tones, shapes=sh["shapes"], max_onset=sh["max_onset"],
        max_coda=sh["max_coda"], min_rise=int(rng.choice([1, 2, 3], p=[0.3, 0.5, 0.2])), coda_class=coda,
        onset_required=bool(sh["kind"] == "simple" and rng.random() < 0.5), stress=stress,
        repair_style="epenthesis" if rng.random() < 0.7 else "deletion",
        cost={**ccost, **vcost}, freq={s: (CLICK_LEX_FREQ if s in clicks else pool_f.get(s, 0.01)) for s in cons + vows})
    if t2:   # (k second-voice tones share their vowel's lexical weight: freq / k^2 keeps the vowel's total sqrt weight)
        inv.freq.update({v: pool_f.get(replace(v, tone2=0), 0.01) / len(t2) ** 2 for v in vows if v.tone2})
    return inv


# --- stress shown (sound lane, 2026-11-08) ------------------------------------------------------------------------------

def stress_marked(word: tuple, stress: str | None) -> str:
    """A form as IPA with ˈ before its stressed syllable (the lect's fixed stress: initial | penult | final; antepenult),
    so pages show and speech plays the stress the lect has. A one-syllable word and a lect with no fixed stress ("none")
    get no mark. The syllable starts at its onset (percepts.syllabify: maximal onset)."""
    from .percepts import syllabify, word_ipa
    from .rules import stressed_vowel
    w = tuple(word)
    if not stress or stress == "none":
        return word_ipa(w)
    vs = [i for i, x in enumerate(w) if x.kind == "V"]
    if len(vs) < 2:
        return word_ipa(w)
    sv = stressed_vowel(w, stress)
    if sv is None:
        return word_ipa(w)
    start = 0
    for syl in syllabify(w):
        n = len(syl.onset) + len(syl.nucleus) + len(syl.coda)
        if start + len(syl.onset) == sv or start <= sv < start + n:
            break
        start += n
    return word_ipa(w[:start]) + "ˈ" + word_ipa(w[start:])


def stressed_ipa(ipa: str, stress: str | None) -> str:
    """stress_marked over an IPA string, word by word (spaces kept); a string already holding ˈ is left alone."""
    if not ipa or "ˈ" in ipa or not stress or stress == "none":
        return ipa
    out = []
    for part in ipa.split(" "):
        try:
            segs = from_ipa(part)
        except Exception:
            out.append(part)
            continue
        out.append(stress_marked(tuple(segs), stress) if segs else part)
    return " ".join(out)


# --- words --------------------------------------------------------------------------------------------------------------

# how often a segment of each manner turns up in words, relative to its share of inventories: glides and glottals are in
# nearly every inventory but carry far fewer words than stops and nasals (a house prior, not a published table)
LEXICAL_MANNER = {0: 1.4, 1: 0.9, 2: 1.0, 3: 1.2, 4: 0.45, 5: 0.9, 6: 0.8, 7: 0.8, 8: 0.6, 9: 0.6}


def _lexical(s: Segment) -> float:
    if s.kind != "C":
        return 1.0
    return LEXICAL_MANNER.get(s.manner, 1.0) * (0.5 if s.place == 8 else 1.0)


def _weights(inv: Inventory, segs: list) -> np.ndarray:
    w = np.array([_lexical(s) * math.sqrt(inv.freq.get(s, 0.05) / (1.0 + inv.cost.get(s, 0.0))) for s in segs], float)
    w = np.where(np.isfinite(w) & (w > 0), w, 1e-6)
    return w / w.sum()


def _pick_seg(rng, segs, w):
    return segs[int(rng.choice(len(segs), p=w))]


def _onset_cluster(rng, inv: Inventory, size: int, cw) -> tuple:
    cons = inv.consonants
    son = [c for c in cons if sonority(c) >= 7]
    sw = _weights(inv, son) if son else None
    for k in range(40):
        if size >= 2 and son and k < 30 and rng.random() < 0.75:   # the commonest clusters: obstruent or nasal + liquid or glide
            cl = tuple(_pick_seg(rng, cons, cw) for _ in range(size - 1)) + (_pick_seg(rng, son, sw),)
        else:
            cl = tuple(_pick_seg(rng, cons, cw) for _ in range(size))
        if inv.onset_ok(cl):
            return cl
    # build rising: lowest-sonority first
    srt = sorted(cons, key=sonority)
    for a in srt:
        for b in reversed(srt):
            if inv.onset_ok((a, b)):
                return (a, b)[:size]
    return (_pick_seg(rng, cons, cw),)


# Syllable-final consonants lean toward sonorants (PW-1557, owner ruling 11-08 "sonorant"): codas favour high sonority
# (Clements 1990, the sonority dispersion principle: a syllable rises steeply into its nucleus and falls gently out of
# it), many languages allow only sonorants or only nasals in the coda (Mandarin n ŋ, Japanese N; Blevins 1995), and
# where obstruents may close a syllable, nasals and liquids are still over-represented there against their onset share.
# A multiplier on the onset weights, by manner: nasals and liquids (laterals, trills, taps, rhotic approximants) up,
# glides and plain fricatives as in onsets (s is a common coda), stops a little down, affricates, clicks and percussives
# well down, and ejectives and implosives (larynx 2, 3) halved: glottalic codas are rare. Coda shares among nasals,
# liquids and obstruents in the reference word lists (tools/language/data/reference_words.tsv, English sketch list):
# Turkish 0.35, Arabic 0.44, English 0.48, Georgian 0.57, Welsh 0.62, Finnish 0.64, Spanish 0.77, Mandarin 1.0; the
# protos drew ~0.30 before (the onset weights), 0.55 with these (calibration.md "Lane 4").
CODA_MANNER = {0: 0.7, 1: 0.4, 2: 1.0, 3: 2.6, 5: 2.6, 6: 2.6, 7: 2.6, 8: 0.1, 9: 0.2}
CODA_LIQUID, CODA_GLIDE, CODA_GLOTTALIC = 2.6, 1.0, 0.5


def _coda_factor(s: Segment) -> float:
    if s.kind != "C":
        return 1.0
    if s.manner == 4:
        f = CODA_LIQUID if is_liquid(s) else CODA_GLIDE
    else:
        f = CODA_MANNER.get(s.manner, 1.0)
    return f * (CODA_GLOTTALIC if s.larynx in (2, 3) else 1.0)


def coda_weights(inv: Inventory, segs: list) -> np.ndarray:
    """`_weights` for a syllable-final position: the onset weights times `_coda_factor` (sonorants favoured)."""
    w = _weights(inv, segs) * np.array([_coda_factor(s) for s in segs], float)
    return w / w.sum()


def _coda_cluster(rng, inv: Inventory, size: int, cw) -> tuple:
    cons = inv.consonants
    for _ in range(30):
        cl = tuple(_pick_seg(rng, cons, cw) for _ in range(size))
        if inv.coda_ok(cl):
            return cl
    ok1 = [c for c in cons if inv.coda_ok((c,))]
    return (ok1[int(rng.integers(len(ok1)))],) if ok1 else ()


def _toned(rng, inv: Inventory, v: Segment) -> Segment:
    if not inv.tones:
        return v
    return replace(v, tone=int(inv.tones[int(rng.integers(len(inv.tones)))]))


def draw_word(rng, inv: Inventory, n_syll: int | None = None, syllables: int | None = None) -> tuple:
    """A legal word of `n_syll` syllables (default 1-3, mostly 2) by the inventory's templates and segment weights."""
    n = n_syll or syllables or int(rng.choice([1, 2, 3], p=[0.3, 0.5, 0.2]))
    cw, vw = _weights(inv, inv.consonants), _weights(inv, inv.vowels)
    kw = coda_weights(inv, inv.consonants)
    names = list(inv.shapes)
    sw = np.array([inv.shapes[k] for k in names], float)
    sw /= sw.sum()
    for _ in range(40):
        out: list = []
        prev_coda = 0
        for i in range(n):
            t = names[int(rng.choice(len(names), p=sw))]
            if t.startswith("V") and (inv.onset_required or (i > 0 and rng.random() < 0.7)):
                t = "C" + t if "C" + t in inv.shapes or inv.max_onset >= 1 else t
            on = len(t) - len(t.lstrip("C"))
            co = len(t) - len(t.rstrip("C"))
            if prev_coda and on > 1:
                on = 1   # syllable contact: after a coda the next onset is one consonant (no -lp.n- runs of three or four)
            prev_coda = co if inv.max_coda else 0
            if on:
                out.extend(_onset_cluster(rng, inv, min(on, inv.max_onset, MAX_ONSET), cw))
            out.append(_toned(rng, inv, _pick_seg(rng, inv.vowels, vw)))
            if co and inv.max_coda:
                out.extend(_coda_cluster(rng, inv, min(co, inv.max_coda, MAX_CODA), kw))
        w = tuple(out)
        if legal(w, inv):
            return realize(w, inv)
    return repair(w, inv)


# --- syllables and legality ---------------------------------------------------------------------------------------------

def _runs(word: tuple) -> list:
    """Alternating consonant runs and vowels: [C-run, V, C-run, V, ..., C-run] (runs may be empty)."""
    runs, cur = [], []
    for s in word:
        if s.kind == "V":
            runs.append(tuple(cur))
            runs.append(s)
            cur = []
        else:
            cur.append(s)
    runs.append(tuple(cur))
    return runs


def _split_medial(run: tuple, inv: Inventory):
    """Split a medial consonant run into (coda, onset), maximising the onset; None if no legal split."""
    for k in range(0, len(run) + 1):   # k = coda length
        coda, onset = run[:k], run[k:]
        if inv.coda_ok(coda) and inv.onset_ok(onset) and not (inv.onset_required and not onset):
            return coda, onset
    return None


def _seg_ok(s: Segment, inv: Inventory) -> bool:
    """A phoneme of the lect, or one of its allophones (a surface sound a word may hold where its environment calls for it)."""
    if s.kind == "C":
        return s in inv._cset or s in inv._aset
    if s.kind == "V":
        q = _strip_tone(s)
        if inv.tones:
            return (q in inv._vset or q in inv._aset) and s.tone in inv.tones
        return s.tone == 0 and (s in inv._vset or s in inv._aset)
    return False


def legal(word: tuple, inv: Inventory) -> bool:
    """Every segment in the inventory (vowels carry one of the lect's tones when it has tone), at least one vowel, and
    every syllable within the templates: onsets rise, codas fall, sizes and coda class as the lect allows. No two vowels
    of one quality side by side (that is a long vowel), no run of three vowels (V.V.V: rare in any language, and a lect's
    templates seldom put two onsetless syllables in a row) and no word-initial geminate."""
    if not word or not all(_seg_ok(s, inv) for s in word):
        return False
    if _vowel_trouble(word) is not None or _initial_geminate(word):
        return False
    r = _runs(word)
    if len(r) < 3:
        return False
    first, last = r[0], r[-1]
    if not inv.onset_ok(first) or (inv.onset_required and not first):
        return False
    if not inv.coda_ok(last):
        return False
    for j in range(2, len(r) - 1, 2):
        if _split_medial(r[j], inv) is None:
            return False
    return True


def _vowel_trouble(word: tuple):
    """The first vowel problem legal() rejects: ("fuse", i) for two vowels of one quality at i, i + 1; ("run", i) for the
    hiatus pair at i, i + 1 to resolve inside a run of three or more vowels (the first that is not a falling diphthong,
    else the run's first pair); None when there is none."""
    n = len(word)
    for i in range(n - 1):
        if _fusible(word[i], word[i + 1]):
            return ("fuse", i)
    i = 0
    while i < n:
        if word[i].kind != "V":
            i += 1
            continue
        j = i
        while j < n and word[j].kind == "V":
            j += 1
        if j - i >= 3:
            k = next((k for k in range(i, j - 1) if not _diphthong(word[k], word[k + 1])), i)
            return ("run", k)
        i = j
    return None


_GLIDES = {k: from_ipa(k)[0] for k in ("j", "w")}


def _initial_geminate(word: tuple) -> bool:
    return len(word) > 1 and word[0].kind == "C" and (word[0].length == 1 or word[1] == word[0])


def _resolve_vowels(w: list, inv: Inventory) -> list:
    """Hiatus and initial geminates out of a word to be repaired, by the commonest resolutions (Casali 1997): identical
    vowels fuse (long when the lect has that long vowel), a high vowel before another vowel in a long run becomes its
    glide when the lect has it (i > j, u > w), else the first vowel of the pair is elided; a word-initial geminate is
    simplified."""
    for _ in range(2 * len(w) + 2):
        bad = _vowel_trouble(tuple(w))
        if bad is None:
            break
        kind, i = bad
        a, b = w[i], w[i + 1]
        if kind == "fuse":
            v = replace(a, length=1, nasal=max(a.nasal, b.nasal), tone=_fused_tone(a.tone, b.tone),
                        tone2=_fused_tone(a.tone2, b.tone2))
            if not _seg_ok(v, inv):
                v = replace(v, length=0)
            if not _seg_ok(v, inv):
                v = a
            w[i:i + 2] = [v]
            continue
        g = None
        if a.height >= 5:
            g = _GLIDES["w" if a.round else "j"]
            g = g if g in inv._cset else None
        if g is not None:
            w[i] = g
        else:
            del w[i]
    if len(w) > 1 and _initial_geminate(tuple(w)):
        if w[1] == w[0]:
            del w[0]
        else:
            s = replace(w[0], length=0)
            w[0] = s if _seg_ok(s, inv) else w[0]
            if w[0].length:
                del w[0]
    return w


def epenthetic_vowel(inv: Inventory) -> Segment:
    """The rarest of the inventory's high vowels (short, oral, not front- or central-rounded when another is there; with the
    lowest tone when tonal). The commonest one, inserted in every lect and every repair, made i (earlier ə, ɨ) the vowel of
    the run; the rarest spreads the insertions over the high vowels."""
    plain = [v for v in inv.vowels if v.length == 0 and v.nasal == 0] or list(inv.vowels)
    # (a second voice, a register or a growl is never the inserted vowel when a plain one is there: Iulahad's recurring
    # epenthetic u˨ᴖ was the rarest high vowel being a second-voice one; syrinx lane 2026-11-08)
    plain = [v for v in plain if not is_nonhuman(v)] or plain
    top = max(v.height for v in plain)
    high = [v for v in plain if v.height == top]
    high = [v for v in high if not (v.round and v.back < 3)] or high
    best = min(high, key=lambda v: (inv.freq.get(v, 0.0), v.back, v.round))
    return replace(best, tone=min(inv.tones)) if inv.tones else best


def _onset_filler(inv: Inventory) -> Segment:
    # (a short consonant first: a word-initial geminate is illegal, so a long ʔː filler was cut again at once and the
    # repair gave up; seen on a drawn inventory whose glottal stop is only long)
    short = [c for c in inv.consonants if not c.length] or list(inv.consonants)
    for pred in (lambda c: c.manner == 0 and c.place == 8, lambda c: sonority(c) == 8, lambda c: c.place == 8):
        cs = [c for c in short if pred(c)]
        if cs:
            return max(cs, key=lambda c: inv.freq.get(c, 0))
    return max(short, key=lambda c: inv.freq.get(c, 0))


def _nearest(s: Segment, inv: Inventory) -> Segment | None:
    pool = inv.consonants if s.kind == "C" else inv.vowels if s.kind == "V" else []
    if not pool:
        return None
    q = _strip_tone(s) if s.kind == "V" else s
    best = min(pool, key=lambda t: (distance(q, t), -inv.freq.get(t, 0)))
    if s.kind == "V" and inv.tones:
        t = s.tone if s.tone in inv.tones else min(inv.tones, key=lambda x: (abs(x - (s.tone or 2)), x))
        best = replace(best, tone=t)
    return best


def _fix_segments(word: tuple, inv: Inventory) -> list:
    out = []
    for s in word:
        if _seg_ok(s, inv):
            out.append(s)
        elif s.kind == "V" and not inv.tones and s.tone and _strip_tone(s) in inv._vset:
            out.append(_strip_tone(s))
        else:
            n = _nearest(s, inv)
            if n is not None:
                out.append(n)
    return out


def repair(word: tuple, inv: Inventory) -> tuple:
    """The cheapest edit that makes `word` legal: foreign segments to their nearest inventory segment, then clusters by
    the lect's style (epenthesis of the commonest high vowel, or deletion: cluster simplification and coda drop), and a
    filler consonant where an onset is required."""
    w = _fix_segments(tuple(word), inv)
    if not w:
        return ()
    ev = epenthetic_vowel(inv)
    if not any(s.kind == "V" for s in w):
        w = w[:1] + [ev] + w[1:]
    w = _resolve_vowels(list(w), inv)
    if not w:
        return ()
    for _ in range(4 * len(w) + 8):
        t = tuple(w)
        if legal(t, inv):
            return realize(t, inv)
        if _initial_geminate(t):   # (an onset cut down to its geminate tail: pʰrː- > rː-; sound lane pass 2)
            w = _resolve_vowels(w, inv)
            if not w:
                return ()
            continue
        r = _runs(t)
        # locate the first bad run; positions in w
        pos, fixed = 0, False
        for j, item in enumerate(r):
            if j % 2 == 1:
                pos += 1
                continue
            run = item
            start = pos
            pos += len(run)
            if j == 0:
                bad = not inv.onset_ok(run) or (inv.onset_required and not run)
                if not bad:
                    continue
                if not run:
                    w.insert(0, _onset_filler(inv))
                elif inv.repair_style == "deletion" and len(run) > 1:
                    # simplify: keep the most sonorous-rising tail that is legal, else the last consonant
                    keep = next((run[k:] for k in range(1, len(run)) if inv.onset_ok(run[k:])), run[-1:])
                    w[start:start + len(run)] = list(keep)
                else:
                    w.insert(start + 1, ev)
                fixed = True
            elif j == len(r) - 1:
                if inv.coda_ok(run):
                    continue
                ok_k = next((k for k in range(len(run), -1, -1) if inv.coda_ok(run[:k])), 0)
                if inv.repair_style == "deletion":
                    del w[start + ok_k:start + len(run)]   # cluster simplification / coda drop
                else:
                    w.append(ev)   # the final run becomes medial; the medial pass splits it further if needed
                fixed = True
            else:
                if _split_medial(run, inv) is not None:
                    continue
                if inv.onset_required and not run:
                    w.insert(start, _onset_filler(inv))
                elif inv.repair_style == "deletion" and len(run) > 1:
                    # drop consonants from the middle of the run until a split exists
                    best = None
                    for k in range(len(run)):
                        cand = run[:k] + run[k + 1:]
                        if _split_medial(cand, inv) is not None:
                            best = cand
                            break
                    if best is None:
                        best = run[-1:] if _split_medial(run[-1:], inv) is not None else ()
                    w[start:start + len(run)] = list(best)
                else:
                    w.insert(start + max(1, len(run) // 2), ev)
                fixed = True
            if fixed:
                break
        if not fixed:
            break
    t = tuple(w)
    if legal(t, inv):
        return realize(t, inv)
    return realize(_cv_fallback(t, inv), inv)


def _cv_fallback(word: tuple, inv: Inventory) -> tuple:
    """Last resort: every consonant gets its own vowel (CV CV ...), onsets filled where required."""
    ev = epenthetic_vowel(inv)
    out: list = []
    for i, s in enumerate(word):
        if s.kind == "V":
            if (not out or out[-1].kind == "V") and inv.onset_required:
                out.append(_onset_filler(inv))
            out.append(s)
        else:
            if out and out[-1].kind == "C":
                out.append(ev)
            out.append(s)
    if out and out[-1].kind == "C" and not inv.coda_ok((out[-1],)):
        out.append(ev)
    if not out or not any(s.kind == "V" for s in out):
        out = [_onset_filler(inv), ev]
    t = tuple(out)
    if legal(t, inv):
        return t
    # onset clusters of size one may still be illegal per segment (should not happen); give the simplest word
    return tuple(x for s in t for x in ((s,) if s.kind == "V" or inv.onset_ok((s,)) else ()))


# --- inventory after change ---------------------------------------------------------------------------------------------

# --- phonotactics re-read from the words (sound lane pass 3) ---------------------------------------------------------------

TEMPLATE_SHARE = 0.03   # a syllable structure counts as part of a lect's phonotactics when this share of its words have it
_ALL_SHAPES = {"CV": 0.33, "CVC": 0.29, "V": 0.04, "VC": 0.03, "CCV": 0.13, "CCVC": 0.1, "CVCC": 0.06, "CCVCC": 0.02}


def word_shape(f) -> tuple:
    """(onset consonants, final coda consonants, has a medial coda) of a form, tone letters aside; None without a vowel. A
    medial run of two or more consonants, or a geminate between vowels, closes the syllable before it."""
    f = [s for s in f if s.kind != "T"]
    vi = [i for i, s in enumerate(f) if s.kind == "V"]
    if not vi:
        return None
    medial = any((b - a - 1) >= 2 or (b - a - 1 == 1 and f[a + 1].length) for a, b in zip(vi, vi[1:]))
    return vi[0], len(f) - 1 - vi[-1], medial


def syllable_profile(forms, share: float = TEMPLATE_SHARE) -> tuple:
    """The phonotactics the words show: (largest onset, largest final coda, medial codas at all), each counted only when at
    least `share` of the words have it (a stray loan or one odd form does not make a template)."""
    sh = [x for x in (word_shape(f) for f in forms) if x is not None]
    if not sh:
        return 1, 0, False
    n = len(sh)

    def top(k):
        best = 0
        for m in range(1, 4):
            if sum(1 for x in sh if x[k] >= m) >= share * n:
                best = m
        return best
    return max(1, top(0)), top(1), sum(1 for x in sh if x[2]) >= share * n


def new_violations(before, after, prof, types_only: bool = False) -> float:
    """Share of the forms a change rewrites whose new shape breaks the phonotactics `prof` (syllable_profile) where the old
    one did not: a longer onset or final coda than the words allow, or a medial coda in a lect without them. types_only:
    count only a syllable type the lect has none of (an onset cluster where onsets are single, a final coda in an
    open-syllable lect, a medial coda), not a larger cluster of a type it has (PW-1622)."""
    changed = bad = 0
    mo, mc, med = prof
    if types_only:   # (one consonant more of a type the lect has is not a new type)
        mo, mc = (mo if mo <= 1 else 99), (mc if mc == 0 else 99)
    for a, b in zip(before, after):
        if a == b:
            continue
        changed += 1
        sa, sb = word_shape(a), word_shape(b)
        if sa is None or sb is None:
            continue
        if (sb[0] > mo and sb[0] > sa[0]) or (sb[1] > mc and sb[1] > sa[1]) or (sb[2] and not med and not sa[2]):
            bad += 1
    return bad / changed if changed else 0.0


def retemplate(inv: Inventory, forms) -> Inventory:
    """The phonotactics re-check: the lect's templates (max_onset, max_coda, shapes) re-read from its words after sound
    change, so coinages and loans follow the syllables the language has now, not the proto's. Unchanged when they agree."""
    mo, mc, med = syllable_profile(forms)
    mo, mc = min(mo, MAX_ONSET), min(max(mc, 1 if med else 0), MAX_CODA)
    if (mo, mc) == (inv.max_onset, inv.max_coda):
        return inv
    shapes = {k: v for k, v in _ALL_SHAPES.items() if len(k) - len(k.lstrip("C")) <= mo and len(k) - len(k.rstrip("C")) <= mc}
    if mc == 0:
        shapes = {"CV": 0.85, "V": 0.15}
    return replace(inv, max_onset=mo, max_coda=mc, shapes=shapes)


def observed(inv: Inventory, forms, profile=None) -> Inventory:
    """The inventory a lexicon actually uses after sound change: segments in `forms` (tones stripped into `tones`; never two
    with the same IPA spelling), keeping `inv`'s phonotactics; costs and frequencies for new segments are computed."""
    cons, vows, tones = [], [], set()
    seen, spelt = set(), set()
    for f in forms:
        for s in f:
            q = _strip_tone(s) if s.kind == "V" else s
            if s.kind == "V" and s.tone:
                tones.add(s.tone)
            if q in seen:
                continue
            seen.add(q)
            k = to_ipa(q)
            if k in spelt:  # (two segments spelt alike are reported once)
                continue
            spelt.add(k)
            (cons if q.kind == "C" else vows).append(q)
    pool_f = _pool_freq()
    cost = {s: inv.cost.get(s) if s in inv.cost else _cost(profile, s) for s in cons + vows}
    allo = phonemic(forms, cons + vows) if cons and vows else {}
    pc = [x for x in cons if x not in allo] or list(inv.consonants)
    pv = [x for x in vows if x not in allo] or list(inv.vowels)
    return replace(inv, consonants=pc, vowels=pv,
                   tones=sorted(tones) if inv.tones else [], cost=cost,
                   freq={s: inv.freq.get(s, pool_f.get(s, 0.01)) for s in cons + vows}, allophones=allo)


# --- phonemes and allophones -------------------------------------------------------------------------------------------
# A surface sound is listed as an allophone, not a phoneme, when it stands only in a predictable environment and in
# complementary distribution with a commoner sound close to it: the standard test (e.g. Hayes 2009, Introductory Phonology
# ch. 2; Pike 1947), run on the lect's own word forms. Only the clear, common kinds are tested (ALLO_TESTS), each a pair
# that differs in one feature group and an environment that conditions it; a pair that also contrasts (any shared
# environment) stays two phonemes. The commoner sound is the phoneme (the elsewhere form). An allophone keeps its surface
# place in the forms; new words (draw_word) and repaired loans (repair) are drawn from the phonemes and then realized
# (realize), so coinages stay in the pattern instead of scattering the allophone into every environment.
ALLO_TESTS = {
    "nasal_place": "a nasal taking the place of the consonant after it (nasal place assimilation: [ŋ] before velars)",
    "palatal": "palatalized before front vowels and j (as Italian [ɲ]-like n before i)",
    "intervocalic": "between vowels only (lenition: intervocalic voicing or spirantization, Spanish [β ð ɣ])",
    "final": "word-finally only (final devoicing or voicing)",
    "initial": "word-initially only (aspirated or strengthened at the start of a word)",
    "nasal_vowel": "a vowel nasalized before a nasal consonant",
    "coda": "in the coda only, before a consonant or at the end of a word (English dark [ɫ], Dutch approximant coda r)",
    "glottal_onset": "a glottal stop inserted before a vowel at the start of a word or between vowels (German-like onset)",
}
ALLO_MIN_PHONEME = 3  # tokens the phoneme (the commoner sound) needs before a complementary distribution counts


def _rkey(n: Segment | None) -> str:
    """The right-hand environment of a token, coarse: # (word end), Vf (front vowel), V, j (palatal glide), N<place> (nasal
    consonant), C<place> (other consonant)."""
    if n is None:
        return "#"
    if n.kind == "V":
        return "Vf" if n.back <= 1 else "V"
    if n.kind == "C":
        if n.manner == 4 and n.place == 4:
            return "j"
        return ("N" if n.manner == 3 else "C") + str(n.place)
    return "?"


def _diff(a: Segment, b: Segment) -> frozenset:
    return frozenset(ax for ax in AXES if ax != "tone" and getattr(a, ax) != getattr(b, ax))


def _pair_tests(x: Segment, p: Segment) -> list[str]:
    """The environment tests a rarer sound x could pass as an allophone of the commoner p (by how they differ)."""
    if x.kind != p.kind:
        return []
    d = _diff(x, p)
    out = []
    if x.kind == "C":
        if x.manner == 3 and p.manner == 3 and d <= {"place", "secondary"} and "place" in d:
            out.append("nasal_place")
        if x.manner == p.manner and ((d == {"place"} and x.place in (3, 4) and p.place in (1, 2, 5))
                                     or (d == {"secondary"} and x.secondary == 2 and p.secondary == 0)):
            out.append("palatal")
        if (d == {"voice"} or (d <= {"manner", "voice"} and {x.manner, p.manner} <= {0, 1, 2} and "manner" in d)) \
                and x.manner != 3:
            out.append("intervocalic")
        if d == {"voice"}:
            out.append("final")
        if d == {"larynx"} and x.larynx == 1 and p.larynx == 0:
            out.append("initial")
        if (d == {"secondary"} and x.manner == 5 and x.secondary == 3 and p.secondary == 0) \
                or (d == {"manner"} and x.manner == 4 and p.manner in (6, 7) and not x.lateral):
            out.append("coda")  # a velarized lateral or an approximant r beside the plain l or the trill / tap
    elif x.kind == "V" and d == {"nasal"} and x.nasal and not p.nasal:
        out.append("nasal_vowel")
    return out


def _env_ok(test: str, x: Segment, left: str, right: str) -> bool:
    """Is a token (left key: # / V / C, right key: _rkey) in the conditioning environment of a test for allophone x?"""
    if test == "nasal_place":
        return right in (f"N{x.place}", f"C{x.place}") or (x.place == 4 and right == "j")
    if test == "palatal":
        return right in ("Vf", "j")
    if test == "intervocalic":
        return left == "V" and right in ("V", "Vf")
    if test == "final":
        return right == "#"
    if test == "initial":
        return left == "#"
    if test == "nasal_vowel":
        return right.startswith("N")
    if test == "coda":
        return right == "#" or right == "j" or right[:1] in ("C", "N")
    return False


def _tokens(forms):
    """(segment without tone, left key, right key) for every token of the forms; plus counts of word-initial vowels and of
    vowel-vowel hiatus (the zero alternative of an inserted ʔ)."""
    toks, init_v, hiatus = [], 0, 0
    for f in forms:
        n = len(f)
        for i, s in enumerate(f):
            if s.kind not in ("C", "V"):
                continue
            q = _strip_tone(s) if s.kind == "V" else s
            lp = f[i - 1] if i else None
            left = "#" if lp is None else ("V" if lp.kind == "V" else "C")
            toks.append((q, left, _rkey(f[i + 1] if i + 1 < n else None)))
            if s.kind == "V":
                if i == 0:
                    init_v += 1
                elif lp.kind == "V":
                    hiatus += 1
    return toks, init_v, hiatus


def phonemic(forms, segs) -> dict:
    """The allophones among a lect's surface sounds `segs` (tone stripped), from its word forms: {allophone: (phoneme or
    None, test)}. x is an allophone of p (p commoner, ALLO_MIN_PHONEME tokens or more, the pair one of _pair_tests) when every
    token of x stands in the test's environment and no token of p does. A glottal stop is an inserted one (phoneme None)
    when it stands only word-initially before a vowel or between vowels and the lect has no word-initial vowel (resp. no
    hiatus) without it. Rarest sounds first; a phoneme is never itself an allophone (no chains), and two allophones of
    one phoneme never share an environment (they would contrast with each other)."""
    forms = list(forms)
    toks, init_v, hiatus = _tokens(forms)
    cnt: dict = {}
    envs: dict = {}
    for q, left, right in toks:
        cnt[q] = cnt.get(q, 0) + 1
        envs.setdefault(q, set()).add((left, right))
    present = [q for q in segs if q in cnt]
    out: dict = {}
    phon: set = set()
    for x in sorted(present, key=lambda q: (cnt[q], to_ipa(q), repr(q))):
        if x.kind == "C" and x.manner == 0 and x.place == 8 and not x.voice and x.larynx == 0 and not x.secondary:
            ev = envs[x]
            if all(r in ("V", "Vf") and l in ("#", "V") for l, r in ev):
                if (any(l == "#" for l, _r in ev) and init_v == 0 or not any(l == "#" for l, _r in ev)) and \
                        (any(l == "V" for l, _r in ev) and hiatus == 0 or not any(l == "V" for l, _r in ev)):
                    out[x] = (None, "glottal_onset")
                    continue
        best = None
        for p in present:
            if p is x or p in out or cnt[p] <= cnt[x] or cnt[p] < ALLO_MIN_PHONEME:
                continue
            if any(q == p and envs[y] & envs[x] for y, (q, _t) in out.items()):
                continue  # (two allophones of one phoneme that share an environment contrast with each other)
            for t in _pair_tests(x, p):
                if all(_env_ok(t, x, l, r) for l, r in envs[x]) and not any(_env_ok(t, x, l, r) for l, r in envs[p]):
                    if best is None or cnt[p] > cnt[best[0]]:
                        best = (p, t)
                    break
        if best is not None and x not in phon:
            out[x] = best
            phon.add(best[0])
    return out


def realize(word: tuple, inv: Inventory) -> tuple:
    """A word drawn from the phonemes as the lect says it: first the lect's live phonological rules (`inv.live`, set by
    phonology.attach: they apply productively to every new word, affix join, compound and loan), then each phoneme with an
    allophone takes it in that allophone's environment (an inserted ʔ goes before a word-initial vowel and between vowels);
    each step is kept only when the result keeps the phonotactics."""
    if inv.live and word:
        from .phonology import apply_word
        w2 = apply_word(word, inv.live, inv.stress)
        if w2 != word and w2 and legal(w2, inv):
            word = w2
    if not inv.allophones or not word:
        return word
    by_p: dict = {}
    glottal = None
    for x, (p, t) in inv.allophones.items():
        if p is None:
            glottal = x
        else:
            by_p.setdefault(p, []).append((x, t))
    out = list(word)
    if by_p:
        for i, s in enumerate(word):
            q = _strip_tone(s) if s.kind == "V" else s
            alts = by_p.get(q)
            if not alts:
                continue
            lp = word[i - 1] if i else None
            left = "#" if lp is None else ("V" if lp.kind == "V" else "C")
            right = _rkey(word[i + 1] if i + 1 < len(word) else None)
            for x, t in alts:
                if _env_ok(t, x, left, right):
                    out[i] = replace(x, tone=s.tone) if s.kind == "V" else x
                    break
    if glottal is not None:
        g = []
        for i, s in enumerate(out):
            if s.kind == "V" and (i == 0 or out[i - 1].kind == "V"):
                g.append(glottal)
            g.append(s)
        out = g
    t = tuple(out)
    return t if t == word or legal(t, inv) else word


def allophones_json(inv: Inventory) -> list:
    """[{"ipa", "of" (the phoneme's IPA; null for an inserted ʔ), "test", "where" (plain words)}], by phoneme then allophone."""
    rows = [{"ipa": to_ipa(x), "of": to_ipa(p) if p is not None else None, "test": t, "where": ALLO_TESTS.get(t, t)}
            for x, (p, t) in inv.allophones.items()]
    return sorted(rows, key=lambda r: (r["of"] or "", r["ipa"]))


# --- json ---------------------------------------------------------------------------------------------------------------

def to_json(inv: Inventory) -> dict:
    def fin(x):
        return x if math.isfinite(x) else None
    return {"consonants": [to_ipa(s) for s in inv.consonants], "vowels": [to_ipa(s) for s in inv.vowels],
            "tones": list(inv.tones), "shapes": dict(inv.shapes), "max_onset": inv.max_onset, "max_coda": inv.max_coda,
            "min_rise": inv.min_rise, "coda_class": inv.coda_class, "onset_required": inv.onset_required,
            "stress": inv.stress, "repair_style": inv.repair_style,
            "cost": {to_ipa(s): fin(c) for s, c in inv.cost.items()},
            "freq": {to_ipa(s): f for s, f in inv.freq.items()},
            "allophones": allophones_json(inv)}


def _one(ipa: str) -> Segment:
    s = from_ipa(ipa)
    return s[0]


def from_json(d: dict) -> Inventory:
    cons = [_one(x) for x in d["consonants"]]
    vows = [_one(x) for x in d["vowels"]]
    return Inventory(
        consonants=cons, vowels=vows, tones=list(d.get("tones", [])), shapes=dict(d.get("shapes", {})),
        max_onset=int(d.get("max_onset", 1)), max_coda=int(d.get("max_coda", 1)), min_rise=int(d.get("min_rise", 2)),
        coda_class=d.get("coda_class", "any"), onset_required=bool(d.get("onset_required", False)),
        stress=d.get("stress", "none"), repair_style=d.get("repair_style", "epenthesis"),
        cost={_one(k): (math.inf if v is None else float(v)) for k, v in d.get("cost", {}).items()},
        freq={_one(k): float(v) for k, v in d.get("freq", {}).items()},
        allophones={_one(a["ipa"]): (_one(a["of"]) if a.get("of") else None, a["test"]) for a in d.get("allophones", [])})
