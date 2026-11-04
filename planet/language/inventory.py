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
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np

from .percepts import SONORITY, Segment, distance, from_ipa, to_ipa

DATA = Path(__file__).parent / "data"

A_FREQ = 1.0            # exponent on the PHOIBLE frequency in the pick weight (tuned by tests: top-20 overlap, quartiles)
ECON = 0.6              # feature-economy bonus per shared place and per shared series (saturating)
MIN_V_DIST = 1.5        # vowel quality floor in (height 0-6, back 0-4 x1.5, round) space
TONAL_SHARE = None      # PHOIBLE share of inventories with tones (read from the sizes table)
STRESS = {"none": 0.44, "initial": 0.19, "penult": 0.27, "final": 0.10}   # WALS 14A (Goedemans & van der Hulst), folded
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


def _strip_tone(v: Segment) -> Segment:
    return replace(v, tone=0) if v.tone else v


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

    def __post_init__(self):
        self._cset = frozenset(self.consonants)
        self._vset = frozenset(self.vowels)

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
    """Every segment of the inventory (consonants then vowels), for `profiles.hear_word`."""
    return list(inv.consonants) + list(inv.vowels)


# --- PHOIBLE tables -----------------------------------------------------------------------------------------------------

def _rows(name: str) -> list[dict]:
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader((ln for ln in f if not ln.startswith("#")), delimiter="\t"))


@functools.cache
def phoible_pool() -> tuple[tuple, tuple]:
    """((Segment, freq) consonants, (Segment, freq) vowels) from phoible_segments.tsv, each PHOIBLE segment that parses
    to exactly one Segment; duplicates (two symbols, one percept) keep the higher frequency."""
    best: dict = {}
    for r in _rows("phoible_segments.tsv"):
        if r["class"] not in ("consonant", "vowel"):
            continue
        try:
            segs = from_ipa(r["segment"])
        except Exception:
            continue
        if len(segs) != 1:
            continue
        s = segs[0]
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
_NONHUMAN_VARIANTS = (("harsh", "phonation", 3, "CV"), ("purr", "phonation", 4, "V"), ("source2", "source2", 1, "V"))


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
    return replace(v, length=0, nasal=0, tone=0, phonation=0, source2=0)


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


def _pick_consonants(rng, n: int, profile) -> tuple[list, dict]:
    pool, _ = _pool_for(profile)
    segs, base, cost = _base_weights(pool, profile)
    places = np.array([s.place for s in segs])
    _, series = np.unique([f"{s.manner}.{s.voice}.{s.larynx}.{s.secondary}" for s in segs], return_inverse=True)
    cnt_place = np.zeros(places.max() + 1)
    cnt_series = np.zeros(series.max() + 1)
    avail = base > 0
    chosen: list[int] = []
    for _ in range(min(n, int(avail.sum()))):
        w = base * (1 + ECON * np.minimum(cnt_place[places], 3) / 3) * (1 + ECON * np.minimum(cnt_series[series], 3) / 3) * avail
        i = int(rng.choice(len(w), p=w / w.sum()))
        chosen.append(i)
        avail[i] = False
        cnt_place[places[i]] += 1
        cnt_series[series[i]] += 1
    return [segs[i] for i in chosen], {segs[i]: float(cost[i]) for i in chosen}


def _pick_vowels(rng, n: int, profile) -> tuple[list, dict]:
    _, pool = _pool_for(profile)
    segs, base, cost = _base_weights(pool, profile)
    qual = [_quality(s) for s in segs]
    q_idx = {q: k for k, q in enumerate(dict.fromkeys(qual))}
    qi = np.array([q_idx[q] for q in qual])
    qxyz = np.array([_vq(q) for q in q_idx], float)                      # per distinct quality
    plain = np.array([s == q for s, q in zip(segs, qual)])
    _, series = np.unique([f"{s.length}.{s.nasal}.{s.phonation}" for s in segs], return_inverse=True)
    series_cnt = np.zeros(series.max() + 1)
    have_q = np.zeros(len(q_idx), bool)
    blocked_q = np.zeros(len(q_idx), bool)                               # within the floor of a chosen quality
    avail = base > 0
    chosen: list[int] = []
    while len(chosen) < n:
        ok = avail & np.where(plain, ~blocked_q[qi], have_q[qi])
        if not ok.any():
            break   # the system is full
        bonus = np.where(plain, 1.0, 1 + ECON * np.minimum(series_cnt[series], 3) / 3)
        w = base * bonus * ok
        i = int(rng.choice(len(w), p=w / w.sum()))
        chosen.append(i)
        avail[i] = False
        if plain[i]:
            have_q[qi[i]] = True
            d = np.sqrt(((qxyz - qxyz[qi[i]]) ** 2).sum(axis=1))
            blocked_q |= d < MIN_V_DIST
        else:
            series_cnt[series[i]] += 1
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


_TONE_SETS = {2: [1, 3], 3: [1, 2, 3], 4: [1, 2, 3, 5], 5: [1, 2, 3, 4, 5]}


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
    cons, ccost = _pick_consonants(rng, nc - len(clicks), profile)
    if clicks:
        ccost.update({c: _cost(profile, c) for c in clicks})
        cons = cons + [c for c in clicks if c not in cons]
    vows, vcost = _pick_vowels(rng, nv, profile)
    # tone
    tones: list = []
    hear = _profile_get(profile, "hear", "tone", 1.0) if profile is not None else 1.0
    mk = _profile_get(profile, "make_cost", "tone", 1.0) if profile is not None else 1.0
    p_tone = 0.0 if not math.isfinite(mk) or hear <= 0 else min(0.95, tonal_share() * hear / max(mk, 1e-6))
    if rng.random() < p_tone:
        k, f = phoible_sizes()["tones"]["count"] if "tones" in phoible_sizes() else (np.array([2, 3]), np.array([.5, .5]))
        m = k >= 2
        nt = int(rng.choice(k[m], p=f[m] / f[m].sum()))
        tones = list(_TONE_SETS[min(5, nt)])
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
    return inv


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
                out.extend(_coda_cluster(rng, inv, min(co, inv.max_coda, MAX_CODA), cw))
        w = tuple(out)
        if legal(w, inv):
            return w
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
    if s.kind == "C":
        return s in inv._cset
    if s.kind == "V":
        if inv.tones:
            return _strip_tone(s) in inv._vset and s.tone in inv.tones
        return s.tone == 0 and s in inv._vset
    return False


def legal(word: tuple, inv: Inventory) -> bool:
    """Every segment in the inventory (vowels carry one of the lect's tones when it has tone), at least one vowel, and
    every syllable within the templates: onsets rise, codas fall, sizes and coda class as the lect allows."""
    if not word or not all(_seg_ok(s, inv) for s in word):
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


def epenthetic_vowel(inv: Inventory) -> Segment:
    """The rarest of the inventory's high vowels (short, oral, not front- or central-rounded when another is there; with the
    lowest tone when tonal). The commonest one, inserted in every lect and every repair, made i (earlier ə, ɨ) the vowel of
    the run; the rarest spreads the insertions over the high vowels."""
    plain = [v for v in inv.vowels if v.length == 0 and v.nasal == 0] or list(inv.vowels)
    top = max(v.height for v in plain)
    high = [v for v in plain if v.height == top]
    high = [v for v in high if not (v.round and v.back < 3)] or high
    best = min(high, key=lambda v: (inv.freq.get(v, 0.0), v.back, v.round))
    return replace(best, tone=min(inv.tones)) if inv.tones else best


def _onset_filler(inv: Inventory) -> Segment:
    for pred in (lambda c: c.manner == 0 and c.place == 8, lambda c: sonority(c) == 8, lambda c: c.place == 8):
        cs = [c for c in inv.consonants if pred(c)]
        if cs:
            return max(cs, key=lambda c: inv.freq.get(c, 0))
    return max(inv.consonants, key=lambda c: inv.freq.get(c, 0))


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
    for _ in range(4 * len(w) + 8):
        t = tuple(w)
        if legal(t, inv):
            return t
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
        return t
    return _cv_fallback(t, inv)


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
    return replace(inv, consonants=cons or list(inv.consonants), vowels=vows or list(inv.vowels),
                   tones=sorted(tones) if inv.tones else [], cost=cost,
                   freq={s: inv.freq.get(s, pool_f.get(s, 0.01)) for s in cons + vows})


# --- json ---------------------------------------------------------------------------------------------------------------

def to_json(inv: Inventory) -> dict:
    def fin(x):
        return x if math.isfinite(x) else None
    return {"consonants": [to_ipa(s) for s in inv.consonants], "vowels": [to_ipa(s) for s in inv.vowels],
            "tones": list(inv.tones), "shapes": dict(inv.shapes), "max_onset": inv.max_onset, "max_coda": inv.max_coda,
            "min_rise": inv.min_rise, "coda_class": inv.coda_class, "onset_required": inv.onset_required,
            "stress": inv.stress, "repair_style": inv.repair_style,
            "cost": {to_ipa(s): fin(c) for s, c in inv.cost.items()},
            "freq": {to_ipa(s): f for s, f in inv.freq.items()}}


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
        freq={_one(k): float(v) for k, v in d.get("freq", {}).items()})
