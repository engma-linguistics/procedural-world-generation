"""A lect: one speech variety, spoken by one deme at a time (PW-986, architecture section 8).

A lect holds an inventory, a lexicon (lexicon.py), a grammar (grammar.py), its rule history and a rate. `step` advances it by
a batch of generations (one frame interval): k rule events ~ Poisson(n x RATE_RULE x RATE_SCALE x rate) through
rules.pick_rule (weighted, vetoed by functional load) applied to every stored form (lexicon words, affixes, grams, paradigm
forms), then the lexical events (lexicon.step) and the grammar events (grammar.step, typology drift). Rates are per
generation with exponent 1 (Daniel, 2026-11-03): a people with 430-year generations changes 15x slower per year than humans.

The other modules are reached through the small adapters at the top so a signature change touches one place."""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

import numpy as np

from . import lexicon as LX
from . import rules as RU
from .inventory import fuse_vowels, hiatus_count, hiatus_in  # noqa: F401 (hiatus helpers, shared with repair)
from .inventory import marked_sound, plain_partners

RATE_RULE = 0.1  # sound-change draws per generation at rate 1, x history.RATE_SCALE (calibrated by the horizon check; see
# calibration.md); since PW-1551 a draw fires only when it lands on a row that changes something (rules.pick_rule)
RATE_SIGMA = 0.5  # lognormal sigma of a proto lect's rate (0.3 -> 0.5, owner ruling 11-08, PW-1539 E: some lines change
#                  fast, a Hawaiian-type collapse; the review suggested ~0.6)
RATE_REDRAW = 0.1  # lognormal sigma of the re-draw at budding
# Bursts (owner ruling 11-08, PW-1539 E): after a language shift or a founder split the lect's rate is multiplied by
# BURST_X for BURST_KYR (punctuational bursts at splits, Atkinson et al. 2008, 10-33% of lexical divergence; founder
# effects and imperfect learning by a shifting population, Thomason & Kaufman 1988). A bud is a founder split when the
# budding deme holds at most FOUNDER_SHARE of its parent's population (history.birth); every shift is a burst.
BURST_X = 2.0
BURST_KYR = 1.0
FOUNDER_SHARE = 0.25
# Founder drift in inventory size (owner ruling 11-08, PW-1565 b): while a burst holds, the inventory-size anchor
# (SIZE_ANCHOR, below) is loosened BURST_ANCHOR_X times, so a founder or shifted line can drift off its proto's size
# (Polynesian-type: a small founder population losing contrasts, Trudgill 2004, 2011); when the burst ends the line
# re-anchors on the size it has then (Lect.size_base, inherited), and holds that. Nothing pushes it down: which way it
# drifts is the catalogue's and PHOIBLE's prior's business.
BURST_ANCHOR_X = 3.0
# Inventory size has no hard cap: rules are steered by PHOIBLE's size distribution (inventory.size_prior), so small and big
# inventories stay possible but grow rare in PHOIBLE's proportions (Rotokas' 6 consonants, !Xóõ's 130). A rule that would take
# the lect's consonant (or vowel-quality) count from n to n + d is drawn (prior(n + d) / prior(n)) ** SIZE_K times as often,
# clamped to SIZE_CLAMP; past INV_MAX x PHOIBLE's largest count the rarest units fold (a sanity ceiling, not a shape).
# Sound change by itself pulls every inventory toward the middle (a big one has more to merge, a small one more to split),
# which would turn PHOIBLE's wide proto draw into a narrow living one; so the steer also holds each line near its own proto
# size, a lognormal of sigma SIZE_ANCHOR in ln n (inventory size runs in families: Khoisan big, Polynesian small).
# (2026-11-04, measures and phonemes round: anchor 0.2 -> 0.12 and clamp (0.1, 2) -> (0.02, 3): a small inventory is offered
# about five times as many splits as mergers, so lines from 7-8 consonant protos grew to 11-12 in 20 kyr and the living
# small end stayed tame; in the isolated-lect harness 8 C protos now end at a median of 10, 35 C at 28; calibration.md)
SIZE_K = 0.5
SIZE_ANCHOR = 0.12
SIZE_CLAMP = (0.02, 3.0)
INV_MAX = 1.0
# Ease (markedness) drag, the owner's "light normalization toward easier consonants": a rule's weight is multiplied by
# exp(EASE_K x the mean over the segments it rewrites of (cost before - cost after)), clamped to EASE_CLAMP. For a human vocal
# tract (profiles.human_voiced) the cost is PHOIBLE's -ln(share of languages with the sound), so the factor is
# (share_out / share_in) ** EASE_K: p > f (0.85 -> 0.43) is drawn 0.71x as often, f > p 1.4x; b > bʱ (0.62 -> 0.01) is held
# at the floor; a deletion counts as making nothing (h > ∅ 1.3x, ʔ > ∅ 1.6x); insertions are neutral. For other voices the
# cost is the species' own (profiles.species_cost: the human cost of the sound's human-makeable core x the profile's make
# multipliers, the same cost their proto-inventories are drawn by), so what is easy for a dragon or a kenku counts, not
# what is easy for a human. (Until 2026-11-07, finish lane, other voices had no drag at all, only the catalogue's make-cost
# ratio (rules.cost_factor), which is neutral on a change between two equally dear sounds: u > y in a lipless reptilian or
# avian mouth (both rounded, both dear) then ran unchecked and y reached 25 of 27 kenku and half the kobold and dragonborn
# lects, ɫ likewise; calibration.md "Final run".)
# Light on purpose: the clamp keeps an unusual change at a quarter of its weight, not out of reach.
EASE_K = 0.5
EASE_CLAMP = (0.25, 3.0)
# Stop steer (2026-11-04, word families round; draft-language-plain-stops-erode): the catalogue wears oral stops down far
# faster than it makes them (lenition, spirantization, Grimm, debuccalization against a few fortitions and devoicings), and
# with fresh coinages rare (lexicon.SOURCES) nothing refilled them: in the isolated-lect harness p, t, k fell from 24% of
# consonant tokens to 3.5% in 20 kyr and from ~95% of lects to under half. Real lexicons keep plosives the commonest manner
# class (roughly a third of consonant tokens; written from knowledge of text counts, cf. Maddieson 1984 for inventories),
# so, as the size steer does for inventory size, a human-voiced lect's rule weights lean against the drift: a rule that
# turns stops into non-stops (or deletes them) is weighted (s / STOP_NORM) ** STOP_K, one that makes stops the inverse,
# where s is the oral-stop share of consonant tokens in the lect's most frequent words (load_forms), binned by STOP_BIN in
# log space so the weighted catalogue caches; clamped to STOP_CLAMP. Glottal ʔ does not count as a stop (k > ʔ is a loss).
# Harness (96 human lects, 22-C protos, 20 kyr, no contact), p/t/k present at the end: no steer 0.48/0.50/0.43; K 1
# 0.60/0.70/0.65; K 2 (clamp 0.1-4) 0.69/0.78/0.73; K 3 (0.05-6) 0.72/0.81/0.70, so K 2: the catalogue, not the steer,
# limits it beyond that (the pick redraws among applicable rules, so a damped lenition gives way to another one).
STOP_NORM = 0.33
STOP_K = 2.0
STOP_CLAMP = (0.1, 4.0)
STOP_BIN = 0.1
# Keep steer (2026-11-04, sinks round): a human-voiced lect seldom loses a near-universal phoneme outright. PHOIBLE has p in
# 85% of languages, k in 90%, m in 97%: if the catalogue's mergers took them as readily as any other sound, they could not be
# that common. A rule that would leave none of a phoneme with PHOIBLE share >= KEEP_SHARE in the lect's most frequent words
# (load_forms; it had some) is drawn KEEP_FACTOR times as often; one that only thins it (a conditioned lenition) is not
# touched. Before it, plain p and k were in under half the living lects (run H: 0.48/0.48, harness 0.66/0.64) with
# lenition, spirantization and Grimm's law each taking the last p or k (draft-language-plain-stops-erode).
KEEP_SHARE = 0.7
KEEP_FACTOR = 0.25
FOLD_RARE = 0.2  # a unit the proto lacked, under this fraction of an average unit's share of its kind's tokens (1% at 20
# units, 0.33% at 60: a big inventory's units are each rarer) and one axis from a commoner unit, folds into it
NEW_SEG_WEIGHT = 0.3  # a rule that would add a segment the lect lacks is drawn this much less often (phonemicization is rare)
PHONO_VETO = 0.8   # probability a change that breaks the lect's syllable phonotactics is turned down (Lect.phonotactic_veto)
PHONO_MIN = 0.2    # ... when at least this share of the words it rewrites would get a shape the lect lacks
PHONO_STATS = {"vetoed": 0}
LOAD_SAMPLE = 120  # forms handed to rules.pick_rule for the functional-load estimate (the most frequent words first)
REFIRE_KYR = 4.0  # a rule that fired in a lect is not drawn (nor adopted by wave) again for this long ... (3 until the
# sound lane, 2026-11-08: a line re-ran ~half the catalogue it fired, so "the same law again" was most of a late history).
# Kept after the single draw (PW-1551): without it the commonest rows re-fire as soon as their input comes back (harness:
# apocope 16.5, h-loss 14.6 firings a line in 20 kyr, applied changes 14.4 -> 23.8 per lect-kyr); a law that just ran is
# a live rule of the lect (phonology.py), not a new change
REFIRE_GEN_YR = 28.0  # the wait is REFIRE_KYR x (generation / REFIRE_GEN_YR) from this generation length up (= history.SOFT_GEN_YR:
# rates are per generation there, owner 11-03), so a 430-yr dragon line waits as many generations as a human one (PW-1551
# lane: with the single draw a human line is bound by its inputs and its wait, a dragon line by its draws, and a wait in
# years let long-lived lines re-fire their common rows 15x as often per generation: own changes per kyr, dragons 1.7 ->
# 3.4 against humans 14.5 -> 15.2, failing "long generations change less")
MAX_FIRES = 2  # ... and fires at most this many times in a lect's life, counting its ancestors' (daughters inherit the memory)
HARMONY_MAX = 1  # harmony rules (family "harmony") at most once per lect line
LIFETIME_CAP_FAMILIES = frozenset({"epenthesis", "harmony", "tone"})  # families under the lifetime cap (the rest only wait
# REFIRE_KYR; tonogenesis uses up the coda/onset contrast that conditions it, so a line does not re-run it every 3 kyr;
# epenthesis and harmony feed themselves: PW-1551 harness without the cap, back harmony 4.2 and S123 4.5 firings a line)
# (LIFETIME_CAP_IDS, S042 ʔ-prothesis, went with the single draw, PW-1551: at naturalness 1 x RULE_WEIGHT 0.15 it fires on
# 0.12 of the harness lines uncapped, against 0.55 before)
# One-off rows (sound lane pass 3, 2026-11-08): the two whole-class coda changes, S099 (every final consonant lost,
# Hawaiian-type) and S124 (paragoge: a vowel added after every final consonant), fire at most ONE_OFF_MAX times per line
# (wave adoptions included): each re-firing undid the codas apocope had just made, so lines flip-flopped to fully open
# syllables every few kyr (calibration.md, sound lane pass 3). Kept after the single draw (PW-1551): without it, and even
# with S099 at naturalness 2, the share of harness lines ending under 5% of words in a consonant rose 0.18 -> 0.22-0.26
# (S099 then fires 2.2 times on the lines that have it). The other one-offs (every chain shift, and the named laws S097,
# S098, S173, S093, S046, S047, S063, S064, S128, S139, S148, S174, S176, S185), added because under the old redraw
# Grimm's law fired in 83% of lects, went with PW-1551: the naturalness weight now sets how many lines get them (Grimm
# 0.34 of harness lines, S148 uvular r 0.06 against 0.53 before) and the ones that recur on a line (Verner, Slavic
# palatalization, diphthongization) recur as the generic changes they are once their input comes back.
ONE_OFF_MAX = 1
ONE_OFF_IDS = frozenset({"S099", "S124"})
# Line drift (sound lane, 2026-11-08; soundchange-gaps.md recommendation 1, Sapir's drift): each proto line draws a standing
# preference per rule family (lognormal sigma LINE_FAMILY_SIGMA) and per row (LINE_ROW_SIGMA), keyed like hiatus_pref by
# the line's proto (hiatus_key) so every daughter keeps it, and each budded lect a small jitter of its own (LINE_BUD_SIGMA,
# keyed by the lect's id: not cumulative down a line, a cheap stand-in for a re-draw at budding). Multiplied into the
# weights in rule_pool, so a family has a sound personality (one line lenites, another palatalizes) and named laws stop
# being universal. Isolated-lect harness (48 human lects, 24 protos each budding in two at 10 kyr, 20 kyr, no wave; scratchpad
# sc/harness.py), before -> after (with REFIRE_KYR 3 -> 4 and the one-off cap): distinct rows fired per line 97.5 -> 87.5,
# rows fired twice or more 49 -> 34, rows fired in >= 80% of lects 45 -> 19, fired-row overlap (Jaccard) of unrelated lects
# 0.50 -> 0.40 with sisters 0.81 -> 0.84. Side effect: ~1/3 fewer changes fire after the split (106 -> 70 a lect), because
# draws that land on a strongly preferred row that changes nothing were redrawn only rules.PICK_REDRAWS times (gone since
# PW-1551: one draw, no redraw). Saturation is mostly structural: ~200 drawn changes a line in 20 kyr against ~100-140
# applicable rows, so a row whose input is there fires within a kyr or so; the naturalness weight (rules.NATURAL_BASE)
# sets how often the rest fire.
LINE_FAMILY_SIGMA = 0.7
LINE_ROW_SIGMA = 1.0
LINE_BUD_SIGMA = 0.2
# Hiatus (2026-11-04, hiatus round). Consonant losses (h > ∅, j > ∅ / V_V, w > ∅, ð ɣ > ∅) leave vowels side by side, and
# languages resolve such hiatus fast (Casali 1997, 2011): identical vowels fuse (normalize, below), and a change that leaves
# new hiatus in the lect's words is followed at once by HIATUS_REPAIRS firing(s) of the catalogue's hiatus family
# (S125-S127, S205-S207: glide formation, V1 elision, contraction, glide epenthesis; resolve_hiatus). Which repair a line
# uses is its strategy: the row's weight x a lognormal preference of sigma HIATUS_SPREAD keyed by the line (inherited).
# A falling diphthong (a non-high vowel + a short high one: ai, au, ei, ou) is not hiatus.
# HIATUS_REPAIRS 3 / HIATUS_MIN 1 cost the sisters check 0.06 (every small hiatus repaired, two or three repairs a change);
# one repair once a change leaves HIATUS_MIN new junctions keeps three-vowel runs under 2% at half the divergence.
HIATUS_REPAIRS = 1
HIATUS_MIN = 8  # new hiatus junctions (over the lexicon) a change must leave before it is repaired
HIATUS_SPREAD = 1.0
HIATUS_SAMPLE = 80  # hiatus words a candidate repair is tried on
# Holes in the pattern (owner ruling 11-08, PW-1539 D: sounds spread into places of articulation the old speakers lacked).
# Martinet (1952, 1955) argued that a gap in an inventory's pattern draws sounds into it ("case vide"), and every human
# language has labial, coronal and dorsal consonants (Maddieson 1984: the few without bilabials, Iroquoian and Tlingit,
# lack them by history, and Tlingit has taken labials in from English loans). A lect whose speakers make a major place
# cheaply (the place's plain stop costs them at most GAP_COST: species_cost; human p 0.16, t 0.33, k 0.10, a lipless
# reptilian p 3.6) but which has no consonant there (a lipless dragon language taken up by giants) splits one of its
# consonants toward it with hazard GAP_RATE per generation: the consonant nearest the place (labialized and rounded-vowel
# neighbours first, as kʷ > p, θ > f, x > f arise) moves there next to the vowels that favour it (rounded for a labial,
# back for a dorsal, front for a coronal) and in GAP_SPLIT of its other words (a lexical-diffusion split, Wang 1969).
# Mild on purpose: one split per event, a few events per line where a gap is cheap to fill, none where it is dear.
GAP_PLACES = {"labial": ((0,), 0), "coronal": ((1, 2, 3), 2), "dorsal": ((4, 5, 6), 5)}   # place group, place filled
# (a place counts as held by a stop, affricate, fricative or nasal there; glides and liquids do not: w and j are not a
# labial or dorsal series. Dorsal is palatal, velar or uvular, so a lect with c or q but no k has no dorsal gap)
GAP_COST = 1.0
GAP_RATE = 0.002
GAP_SPLIT = 0.3
TONE_MIN_MARKED = 0.3  # tone phonemicizes only once marks stand on this share of the core-list vowels (else they are stripped)
GLOTTAL = None  # (ʔ, set on first use)


# ---------------------------------------------------------------------------------------------- adapters to A, C, D
def _inv_mod():
    from . import inventory as INV
    return INV


def _gr_mod():
    try:
        from . import grammar as GR
        return GR
    except ImportError:
        return None


def inventory_segments(inv) -> list:
    INV = _inv_mod()
    return list(INV.segments(inv))


def draw_inventory(rng, profile):
    return _inv_mod().draw_inventory(rng, profile)


def stress_of(inv):
    return getattr(inv, "stress", None) or RU.DEFAULT_STRESS


_CATALOGUES: dict = {}


def catalogue_for(profile, key: str) -> list:
    if key not in _CATALOGUES:
        _CATALOGUES[key] = RU.catalogue(profile)
    return _CATALOGUES[key]


def filtered_apply(rule, stress, segments, inventory=None):
    """rules.apply for one rule, then normalize, skipping (unchanged) every form that holds none of the rule's target
    segments among `segments` (an insertion, target None, runs on every form). Fused vowels are long when `segments` hold a
    long vowel."""
    tgt = None if rule.target is None else frozenset(x for x in segments if rule.target(x))
    long_ok = any(x.kind == "V" and x.length for x in segments)

    def fn(f, stem_index=0):
        if tgt is not None and tgt.isdisjoint(f):
            return f
        return normalize(RU.apply(rule, f, stress, stem_index=stem_index, inventory=inventory), long_ok)
    return fn


def normalize(f: tuple, long_ok: bool = True) -> tuple:
    """Driver-side phonetic tidy of a rule's output: a voiceless consonant left with breathy phonation (a devoiced bʱ, a
    breathy-voiced p) is an aspirated one (kʱ{voice=0} > kʰ), as in the Indic and Greek devoicings; a voiced consonant both
    aspirated and breathy (dʰʱ) is the breathy-voiced one (dʱ, the Indic "voiced aspirate"); a segment the house notation can
    only write malformed (doubled diacritics, feature braces) is heard as its nearest symbol-table segment (tidy_segment);
    two vowels of one quality side by side are one vowel (fuse_vowels); a word-initial geminate is a single consonant."""
    out = []
    ch = False
    for x in f:
        y = _TIDY.get(x)
        if y is None:
            y = _TIDY[x] = tidy_segment(x)
        ch |= y is not x
        out.append(y)
    g = fuse_vowels(tuple(out) if ch else f, long_ok)
    # (an initial geminate simplifies: S035's degemination, where geminates are least stable)
    if len(g) > 2 and g[0].kind == "C" and (g[0] == g[1] or g[0].length):
        g = g[1:] if g[0] == g[1] else (replace(g[0], length=0),) + g[1:]
    return g




_TIDY: dict = {}
_TABLE: dict = {}
_PREF: dict = {}
_HIATUS_ROWS: dict = {}


def table_segments(kind: str) -> list:
    """The symbol table's segments of a kind (percepts.symbols()): the only fold targets the driver makes."""
    if not _TABLE:
        from .percepts import symbols, to_ipa
        for k in ("C", "V"):
            _TABLE[k] = sorted({s.seg for s in symbols() if s.seg.kind == k}, key=lambda q: (to_ipa(q), repr(q)))
    return _TABLE.get(kind, [])


def malformed(x) -> bool:
    """True when the house notation writes the segment with a doubled diacritic or a feature brace (ʊ̞̞, m{retroflex=1})."""
    import unicodedata
    from .percepts import to_ipa
    t = unicodedata.normalize("NFD", to_ipa(_unit(x)))
    if "{" in t or "ʰʱ" in t:
        return True
    return any(a == b and unicodedata.combining(a) for a, b in zip(t, t[1:]))


def tidy_segment(x):
    if x.kind == "C" and x.phonation == 1 and not x.voice:
        x = replace(x, phonation=0, larynx=1)
    if x.kind == "C" and x.phonation == 1 and x.voice and x.larynx == 1:
        x = replace(x, larynx=0)
    if x.kind not in ("C", "V") or not malformed(x):
        return x
    from .percepts import distance, to_ipa
    u = _unit(x)
    best = min(table_segments(x.kind), key=lambda q: (distance(u, q), to_ipa(q), repr(q)), default=None)
    if best is None:
        return x
    return replace(best, tone=x.tone, tone2=x.tone2 if best.source2 else 0) if x.kind == "V" else best


def base_id(rid: str) -> str:
    """A rule's catalogue id (a lect's epenthesis variant `S123/i` is S123)."""
    return rid.split("/", 1)[0]


def weight_override(weights: dict, rule):
    """The driver's weight override for a rule (history.RULE_WEIGHT): by exact id, then catalogue id, then `family:<name>`;
    None when there is none."""
    if not weights:
        return None
    for k in (rule.id, base_id(rule.id), "family:" + (rule.family or "")):
        if k in weights:
            return weights[k]
    return None


def reduction_variant(rule, inv):
    """A reduction to a central vowel (family "reduction", a `set` to back 2) re-pointed at the lect's own central-most
    vowel (short, oral; ə when it has one), id `<id>/<vowel>`: reduction merges into what the lect has rather than
    bringing in a new ə or ɨ (which, drawn in every lect, made ɨ the commonest vowel of the run)."""
    ch = rule.change
    if rule.family != "reduction" or ch.kind != "set" or len(ch.items) != 1 or inv is None:
        return rule
    sets = dict(ch.items[0][2])
    if sets.get("back") != 2 or "height" not in sets:
        return rule
    vs = [v for v in getattr(inv, "vowels", ()) if v.length == 0 and v.nasal == 0]
    if not vs:
        return rule
    v = min(vs, key=lambda q: (abs(q.back - 2), abs(q.height - 3), q.round, q.height, q.back))
    if v.back == sets.get("back") and v.height == sets.get("height") and v.round == sets.get("round", v.round):
        return rule
    from .percepts import to_ipa
    new = tuple((a, getattr(v, a)) if a in ("height", "back", "round") else (a, x) for a, x in ch.items[0][2])
    items = ((ch.items[0][0], ch.items[0][1], new),)
    return replace(rule, id=f"{base_id(rule.id)}/{to_ipa(replace(v, tone=0))}", change=replace(ch, items=items))


def epenthesis_variant(rule, inv):
    """An epenthesis insertion (family "epenthesis", a literal vowel inserted) re-pointed at the lect's own epenthetic vowel
    (inventory.epenthetic_vowel: its commonest high vowel), id `<id>/<vowel>`. The catalogue rows write ə; inserting ə into
    every lect is what made ə the commonest vowel of the run."""
    ch = rule.change
    if ch.kind != "insert" or rule.family != "epenthesis" or not ch.items or inv is None:
        return rule
    if not all(lit is not None and lit.kind == "V" for _r, lit, _s in ch.items):
        return rule
    try:
        v = _inv_mod().epenthetic_vowel(inv)
    except (ValueError, AttributeError):
        return rule
    if all(lit == v for _r, lit, _s in ch.items):
        return rule
    from .percepts import to_ipa
    items = tuple((ref, v, sets) for ref, _lit, sets in ch.items)
    return replace(rule, id=f"{base_id(rule.id)}/{to_ipa(v)}", change=replace(ch, items=items, out_text=to_ipa(v)))


def glottal():
    global GLOTTAL
    if GLOTTAL is None:
        from .percepts import from_ipa
        GLOTTAL = from_ipa("ʔ")[0]
    return GLOTTAL


# ---------------------------------------------------------------------------------------------- word access (families)
FORMATION_SKIP = ("sound_change", "borrow", "substrate", "nativize", "analogy")


def word_form(lect, concept: str):
    w = lect.lexicon.get(concept) if lect.lexicon is not None else None
    return w.form if w is not None else None


def word_root(lect, concept: str):
    """The etymology root of a lect's word for a concept: its last word-formation step (proto, coin, derive, compound, shift,
    taboo, elaborate) as (kyr, lect, process, gloss). Inherited words share it with their sisters; loans share it with their
    donors; independent coinages differ."""
    w = lect.lexicon.get(concept) if lect.lexicon is not None else None
    if w is None:
        return None
    for s in reversed(w.etym):
        if not s.process.split(":", 1)[0] in FORMATION_SKIP:
            return (s.kyr, s.lect, s.process, s.gloss)
    return (w.etym[0].kyr, w.etym[0].lect, w.etym[0].process, w.etym[0].gloss) if w.etym else None


# ---------------------------------------------------------------------------------------------- the lect
@dataclass
class Lect:
    id: str
    deme: int | None
    people: str
    parent: str | None
    how: str  # proto | bud | shift | arrival
    born_kyr: float
    rate: float = 1.0
    substrate: str | None = None
    died_kyr: float | None = None
    end: str | None = None  # bud parents keep living; extinct | fused | shifted
    inventory: object = None
    lexicon: object = None
    grammar: object = None
    profile: object = None
    profile_key: str = "human"
    gen_yr: float = 25.0
    changes: list = field(default_factory=list)  # {kyr, rule, cause, origin_lect}
    shares: dict = field(default_factory=dict)  # lect id -> share of this deme speaking it (bilingual years)
    shares_history: list = field(default_factory=list)  # [kyr, {lect: share}]
    snapshots: list = field(default_factory=list)  # [kyr, snapshot dict] per frame alive (history.snapshot)
    l2: float = 0.0
    population: float = 0.0
    isolation: float = 0.0
    deme_name: str | None = None
    language: str | None = None
    family_true: str | None = None
    family_scholars: str | None = None
    rules_applied: int = 0
    generations: float = 0.0
    base_segs: frozenset = frozenset()  # the proto-language's consonants (inventory cap; carried by daughters)
    rule_text: dict = field(default_factory=dict)  # rules.describe of rules made on the fly (dispersion pushes), for the json
    fired: dict = field(default_factory=dict)  # catalogue rule id -> [kyr it fired, ...] (own and inherited: the re-fire memory)
    glottal_phonetic: bool = False  # ʔ came only from prothesis (S042) in a lect without ʔ: not a phoneme (kept out of the inventory)
    minority: bool = False  # an old lect still spoken by part of its deme after the deme shifted (lives until its share < 0.1)
    hiatus_key: str = ""  # the line whose hiatus strategy this lect keeps (resolve_hiatus; its proto's id, inherited)
    live: list = field(default_factory=list)  # phonology.Live: the live phonological rules (inherited; phonology.update)
    dead_rules: list = field(default_factory=list)  # [ref, born, died, why] of the latest rules that died
    sandhi_drawn: bool = False  # the line has drawn its tone sandhi (phonology.draw_sandhi), once
    burst_until: float | None = None  # kyr (ago) until which the rate runs at BURST_X (a shift or founder split; not inherited)
    size_base: dict | None = None  # {"C", "V"} the size the line re-anchored on after a burst (inherited; None: the proto's)
    orth: tuple = ("house", "double")  # the book-spelling tradition (romanize.LETTER_STYLES, LENGTH_W; inherited, PW-1546)
    insdel: dict = field(default_factory=dict)  # segment (tone aside) -> (kyr, "ins" | "del"): the line's last insertion or
    #                                             loss of it (inherited; `alternates`, PW-1537 R9)

    def copy(self, new_id: str, deme: int | None, kyr: float, how: str, rng=None) -> "Lect":
        """A daughter lect: same inventory, a copied lexicon and grammar, the rate re-drawn a little (budding)."""
        rate = self.rate
        if rng is not None and how == "bud":
            rate = float(self.rate * math.exp(rng.normal(0.0, RATE_REDRAW)))
        GR = _gr_mod()
        gram = None
        if self.grammar is not None:
            gram = GR.copy(self.grammar) if GR is not None and hasattr(GR, "copy") else _deepcopy(self.grammar)
        return Lect(id=new_id, deme=deme, people=self.people, parent=self.id, how=how, born_kyr=float(kyr), rate=rate,
                    inventory=_copy_inv(self.inventory), lexicon=self.lexicon.copy(new_id) if self.lexicon is not None else None,
                    grammar=gram, profile=self.profile, profile_key=self.profile_key, gen_yr=self.gen_yr,
                    base_segs=self.base_segs or self.consonants(), fired={k: list(v) for k, v in self.fired.items()},
                    glottal_phonetic=self.glottal_phonetic, hiatus_key=self.hiatus_key or self.id,
                    live=list(self.live), dead_rules=list(self.dead_rules), sandhi_drawn=self.sandhi_drawn,
                    size_base=dict(self.size_base) if self.size_base else None, orth=tuple(self.orth),
                    insdel=dict(self.insdel))

    def gaps(self) -> list:
        """The major places (GAP_PLACES) the lect has no consonant at though its speakers make the place cheaply
        (the plain voiceless stop there costs them at most GAP_COST)."""
        from . import profiles as PR
        from .percepts import Segment
        if self.profile is None or self.lexicon is None:
            return []
        have = {x.place for x in self.segments() if x.kind == "C" and not x.double and x.manner <= 3}
        out = []
        for name, (group, at) in GAP_PLACES.items():
            if have & set(group):
                continue
            if PR.species_cost(self.profile, Segment("C", place=at, manner=0)) <= GAP_COST:
                out.append(name)
        return out

    def gap_fill(self, rng, n_generations: float, kyr: float) -> bool:
        """Holes in the pattern (GAP_RATE): with hazard GAP_RATE x n, split a consonant into an empty major place the
        speakers make cheaply. True when a split happened."""
        if GAP_RATE <= 0 or self.lexicon is None:
            return False
        gaps = self.gaps()
        if not gaps or rng.random() >= 1.0 - math.exp(-GAP_RATE * n_generations):
            return False
        from . import profiles as PR
        from .percepts import place_distance, to_ipa
        name = gaps[int(rng.integers(len(gaps)))]
        at = GAP_PLACES[name][1]
        cnt: dict = {}
        for w in self.lexicon.words.values():
            for x in w.form:
                if x.kind == "C":
                    cnt[x] = cnt.get(x, 0) + 1
        tot = sum(cnt.values()) or 1
        floor = 1.5 * FOLD_RARE * tot / max(1, len(cnt))   # (the new unit must not be folded straight back: cap_inventory)
        cands = []
        for c in sorted(cnt, key=lambda q: (to_ipa(q), repr(q))):
            if c.place == 8 or c.manner in (8, 9) or c.double:
                continue
            t = replace(c, place=at, retroflex=0, labiodental=0, sibilant=c.sibilant if name == "coronal" else 0,
                        lateral=c.lateral if name == "coronal" else 0,
                        secondary=0 if (name == "labial" and c.secondary == 1) else c.secondary)
            cost = PR.species_cost(self.profile, t)
            if t in cnt or not math.isfinite(cost) or cost > 2.0 * GAP_COST + 1.0 or cnt[c] * GAP_SPLIT < floor:
                continue
            w = math.exp(-place_distance(c.place, at) / 2.0 - cost) * cnt[c]
            if name == "labial" and c.secondary == 1:
                w *= 4.0   # (kʷ > p: the labialized consonant is the usual source)
            cands.append((w, c, t))
        if not cands:
            return False
        ws = np.array([x[0] for x in cands], dtype=float)
        _w, src, tgt = cands[int(rng.choice(len(cands), p=ws / ws.sum()))]

        def favours(v) -> bool:
            if v is None or v.kind != "V":
                return False
            return bool(v.round) if name == "labial" else v.back >= 3 if name == "dorsal" else v.back <= 1
        salt = f"gap|{self.id}|{to_ipa(src)}"

        def fn(f, stem_index=0):
            f = tuple(f)
            if src not in f:
                return f
            whole = partial_pick(f, GAP_SPLIT, salt)
            return tuple(tgt if x == src and (whole or favours(f[j - 1] if j else None)
                                              or favours(f[j + 1] if j + 1 < len(f) else None)) else x
                         for j, x in enumerate(f))
        n = LX.apply_rule_to_lexicon(self.lexicon, fn, f"gap:{to_ipa(src)}>{to_ipa(tgt)}", kyr, self.id)
        if not n:
            return False
        GR = _gr_mod()
        if GR is not None and self.grammar is not None:
            GR.apply_rule_to_grammar(self.grammar, fn, f"gap:{to_ipa(src)}>{to_ipa(tgt)}", kyr)
        self.touch()
        self._dirty = True
        self.sync()
        self.changes.append({"kyr": round(float(kyr), 3), "rule": f"gap:{to_ipa(src)}>{to_ipa(tgt)}", "cause": "gap",
                             "origin_lect": None})
        return True

    def rate_now(self, kyr: float) -> float:
        """The lect's rate at `kyr` (the end of a step): its own, x BURST_X while a burst holds (burst_until)."""
        if self.burst_until is not None and kyr >= self.burst_until - 1e-9:
            return self.rate * BURST_X
        return self.rate

    def in_burst(self, kyr: float | None = None) -> bool:
        """A burst holds at `kyr` (default: the lect's latest step)."""
        kyr = getattr(self, "_last_kyr", None) if kyr is None else kyr
        return self.burst_until is not None and kyr is not None and kyr >= self.burst_until - 1e-9

    def size_anchor(self) -> tuple:
        """({"C", "V"} counts the size steer anchors on, its sigma): the re-anchored size after a burst, else the proto's
        (base_segs); sigma SIZE_ANCHOR, x BURST_ANCHOR_X while a burst holds (PW-1565)."""
        base = self.size_base or {k: sum(1 for u in self.base_segs if u.kind == k) for k in ("C", "V")}
        return base, SIZE_ANCHOR * (BURST_ANCHOR_X if self.in_burst() else 1.0)

    def end_burst(self, kyr: float) -> bool:
        """At the first step after a burst: re-anchor the size steer on the inventory as it is now (PW-1565)."""
        if self.burst_until is None or kyr >= self.burst_until - 1e-9 or self.inventory is None:
            return False
        self.size_base = {"C": len(self.inventory.consonants), "V": len({_unit(v) for v in self.inventory.vowels})}
        self.burst_until = None
        return True

    def refire_kyr(self) -> float:
        """The re-fire wait in kyr: REFIRE_KYR, counted in generations from REFIRE_GEN_YR up (rates are per generation)."""
        return REFIRE_KYR * max(1.0, self.gen_yr / REFIRE_GEN_YR) if REFIRE_GEN_YR else REFIRE_KYR

    def may_fire(self, rule, kyr: float) -> bool:
        """The re-fire memory: a rule fired in the last REFIRE_KYR, or already MAX_FIRES times in the lect's line (HARMONY_MAX
        for harmony, ONE_OFF_MAX for a one-off row: one_off), is not drawn or adopted again."""
        h = self.fired.get(base_id(rule.id))
        if not h:
            return True
        # the lifetime cap holds only for the rules that pile up (prothesis, epenthesis, harmony: each firing feeds the next);
        # every other rule just waits REFIRE_KYR, so a fast-changing line does not use up the catalogue
        if one_off(rule) and len(h) >= ONE_OFF_MAX:
            return False
        if rule.family in LIFETIME_CAP_FAMILIES and len(h) >= (HARMONY_MAX if rule.family == "harmony" else MAX_FIRES):
            return False
        return h[-1] - kyr >= self.refire_kyr() - 1e-9

    def alternates(self, rule, segs, kyr: float) -> bool:
        """PW-1537 R9: would this rule insert a segment the line lost, or lose one it inserted, within its re-fire wait?
        (cold review: elf 7 inserted w after u before a vowel seven times and lost w before u four times, j went in after
        i and out between vowels in turn: 448 of 621 living a24559 lects had such a pair within 4 kyr.) A sound change
        undone and redone on that time scale is the engine's ping-pong, not history; the second change waits."""
        kd = _ins_del(rule, segs)
        if kd is None or not self.insdel:
            return False
        wait = self.refire_kyr()
        for x in kd[1]:
            last = self.insdel.get(x)
            if last is not None and last[1] != kd[0] and last[0] - kyr < wait - 1e-9:
                return True
        return False

    def consonants(self) -> frozenset:
        """The proto-like base for the inventory cap: the consonants, and the vowel qualities (tone set aside)."""
        if self.lexicon is None:
            return frozenset()
        return frozenset(_unit(x) for x in self.segments() if x.kind in ("C", "V"))

    def weighted_rules(self, rules, cache: bool = True) -> list:
        """The catalogue weighted for this lect's sounds (cached per segment set and stop-share bin): rule_factor (new
        segments, ease drag, stop steer, inventory size)."""
        segs = frozenset(self.segments())
        inv = self.inventory
        # (the size steer counts phonemes: the inventory lists them, its allophones aside; inventory.phonemic)
        counts = None if inv is None else (len(inv.consonants), len({_unit(v) for v in inv.vowels}))
        from . import profiles as PR
        hv = PR.human_voiced(self.profile)
        sb = stop_bin(stop_share(self.load_forms())) if hv and self.lexicon is not None else None
        hit = getattr(self, "_rw", None) if cache else None
        base, sigma = self.size_anchor()
        key = (counts, sb, tuple(sorted(base.items())), sigma)
        if hit is not None and hit[0] is rules and hit[1] == segs and hit[3] == key:
            return hit[2]
        units = frozenset(_unit(x) for x in segs)
        cn = None if counts is None else {"C": counts[0], "V": counts[1]}
        out = []
        forms = self.load_forms() if hv else None
        for r in rules:
            f = rule_factor(r, segs, units, hv, base, cn, sb, None if hv else self.profile, sigma)
            if hv and f > 0:
                f *= keep_part(r, segs, forms, stress_of(inv))
            out.append(replace(r, weight=r.weight * f) if f != 1.0 else r)
        if cache:
            self._rw = (rules, segs, out, key)
        return out

    def cap_inventory(self, kyr: float) -> int:
        """Tidy the inventory after sound change: two units spelt alike are one (the commoner stays); a rare unit the proto
        lacked (under FOLD_RARE of an average unit's share of its kind's tokens) one axis from a commoner unit folds into it; past the sanity ceiling
        (INV_MAX x PHOIBLE's largest count; vowels by quality with length and nasality, tone set aside) the rarest units fold
        into their nearest remaining unit. A fold lands on the commoner and, among near neighbours, the cheaper unit
        (fold_target). Consistent over the lexicon and grammar; logged as one `simplification:` change with cause
        "dispersion". Returns units folded. Size itself is steered softly by the rule weights (rule_factor), not here."""
        from .percepts import distance, to_ipa
        from . import inventory as INV
        segs = self.all_segments()
        mapping = {}
        for kind in ("C", "V"):
            units = sorted({_unit(x) for x in segs if x.kind == kind}, key=lambda q: (to_ipa(q), repr(q)))
            cap = int(INV_MAX * INV.size_max("consonants" if kind == "C" else "vowels"))
            cnt = dict.fromkeys(units, 0)
            for w in self.lexicon.words.values():
                for x in w.form:
                    u = _unit(x)
                    if u in cnt:
                        cnt[u] += 1
            keep = set(units)
            table = set(table_segments(kind))
            um = {}
            ipa_of = {}
            for x in sorted(units, key=lambda q: (-cnt[q], repr(q))):  # (two units spelt alike are one: the commoner stays)
                k = to_ipa(x)
                if k in ipa_of:
                    um[x] = ipa_of[k]
                    keep.discard(x)
                else:
                    ipa_of[k] = x
            tot = sum(cnt.values()) or 1
            for x in sorted(keep, key=lambda q: (cnt[q], to_ipa(q), repr(q))):  # (rare new units one axis from another fold)
                if x in self.base_segs or cnt[x] >= FOLD_RARE * tot / max(1, len(units)):
                    continue
                near = [q for q in keep if q != x and _axes_apart(x, q) == 1 and cnt[q] > cnt[x]]
                if near:
                    keep.discard(x)
                    um[x] = max(near, key=lambda q: (cnt[q] / (1.0 + self.unit_cost(q)), to_ipa(q), repr(q)))
            while len(keep) > cap:
                # (malformed or off-table units go first, then those the proto lacked; folds land on symbol-table segments)
                pool = ([x for x in keep if malformed(x)] or [x for x in keep if x not in self.base_segs and x not in table]
                        or [x for x in keep if x not in self.base_segs] or list(keep))
                x = min(pool, key=lambda q: (cnt[q], to_ipa(q), repr(q)))
                keep.discard(x)
                tgt = [q for q in keep if q in table] or list(keep)
                um[x] = fold_target(x, tgt, cnt, self.unit_cost, distance)
            for x in um:  # (a fold into a unit folded later follows it on)
                y = um[x]
                while y in um:
                    y = um[y]
                um[x] = y
            for x in segs:
                u = _unit(x)
                if u in um:
                    mapping[x] = (replace(um[u], tone=x.tone, tone2=x.tone2 if um[u].source2 else 0) if x.kind == "V"
                                  else um[u])
        if not mapping:
            return 0

        long_ok = any(x.kind == "V" and x.length for x in segs)

        def fn(f, stem_index=0, m=mapping):
            return normalize(tuple(m.get(y, y) for y in f), long_ok)
        what = ", ".join(sorted({f"{to_ipa(_unit(a))} > {to_ipa(_unit(b))}" for a, b in mapping.items()}))
        rid = "simplification"
        self.touch()
        LX.apply_rule_to_lexicon(self.lexicon, fn, "simplification", kyr, self.id)
        GR = _gr_mod()
        if GR is not None and self.grammar is not None:
            GR.apply_rule_to_grammar(self.grammar, fn, "simplification", kyr)
        self.changes.append({"kyr": round(float(kyr), 3), "rule": rid, "cause": "dispersion", "origin_lect": None, "merged": what})
        self._dirty = True
        return len(mapping)

    def unit_cost(self, x) -> float:
        """What a unit costs this lect's voice (profiles.species_cost; PHOIBLE's for a human voice), for fold targets."""
        from . import profiles as PR
        c = PR.species_cost(self.profile, x) if self.profile is not None else PR.human_cost(x)
        return c if math.isfinite(c) else PR.COST_MAX * 4

    @property
    def alive(self) -> bool:
        return self.died_kyr is None

    def segments(self) -> list:
        """The segments in use: every segment of every word (the inventory as it now stands after sound change); cached until
        the forms change (touch())."""
        segs = getattr(self, "_segs", None)
        if segs is None:
            seen = {}
            for w in self.lexicon.words.values():
                for s in w.form:
                    seen[s] = True
            segs = self._segs = list(seen)
        return segs

    def all_segments(self) -> list:
        """Segments of the words and of the grammar's forms (grams, paradigm cells): what a rule may touch."""
        segs = set(self.segments())
        if self.grammar is not None:
            for gr in getattr(self.grammar, "grams", ()):
                segs.update(gr.form)
            for ex in getattr(self.grammar, "exemplars", ()):
                segs.update(ex.stem)
                for f in ex.cells.values():
                    segs.update(f)
            for _c, f in getattr(self.grammar, "helpers", {}).values():
                segs.update(f)
        for f, _s in getattr(self.lexicon, "affixes", {}).values():
            segs.update(f)
        return list(segs)

    def touch(self) -> None:
        self._segs = None
        self._sylprof = None

    def phonotactic_veto(self, rule, rng) -> bool:
        """Phonotactic resistance (Kisseberth's conspiracies; the stability of syllable structure within families): a change
        that would give PHONO_MIN or more of the words it rewrites a syllable shape the lect's words do not have (a longer
        onset or final coda, or a medial coda; inventory.syllable_profile) is turned down with probability PHONO_VETO.
        Changes that simplify syllables pass, and a change that gets through re-templates the lect (inventory.retemplate),
        so a coda once established is no longer resisted."""
        if PHONO_VETO <= 0 or self.lexicon is None or rule.family in ("tone", "hiatus"):
            return False
        inv_mod = _inv_mod()
        prof = getattr(self, "_sylprof", None)
        if prof is None:
            prof = self._sylprof = inv_mod.syllable_profile(self.all_forms())
        forms = self.load_forms()
        outs = RU.apply_all(rule, forms, stress_of(self.inventory))
        if inv_mod.new_violations(forms, outs, prof) < PHONO_MIN:
            return False
        if rng.random() < PHONO_VETO:
            PHONO_STATS["vetoed"] += 1
            return True
        return False

    def all_forms(self) -> list:
        return [w.form for w in self.lexicon.words.values()]

    def load_forms(self) -> list:
        """The forms the functional-load veto looks at: the LOAD_SAMPLE most frequent words (frequency class, then concept),
        a fixed sample so the estimate costs the same for every lect."""
        ws = sorted(self.lexicon.words.values(), key=lambda w: (w.freq_class, w.concept))[:LOAD_SAMPLE]
        return [w.form for w in ws]

    def sync(self) -> None:
        """Bring the inventory in line with the forms after this interval's sound changes."""
        if getattr(self, "_dirty", False):
            _sync_inventory(self, getattr(self, "_last_kyr", None))
            self._dirty = False

    def apply_rule(self, rule, kyr: float, origin: str | None = None, repair: bool = False) -> int:
        """Run one sound change over every stored form; record it. A change that leaves new hiatus is followed by its repair
        (resolve_hiatus; `repair` marks such a follow-up, which is not repaired again). Returns words changed."""
        pre = None
        if not repair and self.lexicon is not None:
            pre = {c: w.form for c, w in self.lexicon.words.items()}
        n = self._apply_rule(rule, kyr, origin)
        if n and pre is not None:
            self.resolve_hiatus(kyr, origin, pre)
        return n

    def resolve_hiatus(self, kyr: float, origin, pre: dict) -> int:
        """After a change, while the lect's words hold more hiatus than before it (hiatus_count, over the lexicon), fire the
        hiatus repair the line prefers (hiatus_pool: weight x hiatus_pref) among those that reduce the hiatus of the words
        that have it and do not simply undo the change (put most changed words back), at most HIATUS_REPAIRS times. Each
        firing is an ordinary recorded change (its own id and cause), outside the re-fire memory. Returns repairs fired."""
        h0 = hiatus_count(pre.values())
        fired = 0
        for k in range(HIATUS_REPAIRS):
            now = {c: w.form for c, w in self.lexicon.words.items()}
            if hiatus_count(now.values()) - h0 < (HIATUS_MIN if k == 0 else 1):
                break
            sample = [f for f in now.values() if hiatus_in(f)][:HIATUS_SAMPLE]
            back = [(pre[c], f) for c, f in now.items() if c in pre and pre[c] != f and hiatus_in(f)][:HIATUS_SAMPLE]
            segs = self.all_segments()
            stress = stress_of(self.inventory)
            best = None
            for r in self.hiatus_pool():
                if self.alternates(r, segs, kyr):
                    continue   # (no glide back in where the line just lost it: PW-1537 R9)
                fn = filtered_apply(r, stress, segs, self.inventory)
                gain = 0
                for f in sample:
                    gain += hiatus_in(f) - hiatus_in(fn(f))
                if gain <= 0:
                    continue
                if back and 2 * sum(1 for p, f in back if fn(f) == p) > len(back):
                    continue
                sc = r.weight * self.hiatus_pref(r)
                if best is None or sc > best[0]:
                    best = (sc, r)
            again = any(base_id(c["rule"]) == base_id(best[1].id) and float(c["kyr"]) - kyr < self.refire_kyr() - 1e-9
                        for c in self.changes[-60:]) if best is not None else False
            # (PW-1537 R9: a repair the line made within the re-fire wait is its persistent rule at work on new input,
            # Chafe 1968, not a new change: recorded with cause "persistent", so a history lists the law once)
            if best is None or self._apply_rule(best[1], kyr, origin, remember=False,
                                                cause="persistent" if again else None) == 0:
                break
            fired += 1
        return fired

    def hiatus_pool(self) -> list:
        """The catalogue's hiatus repairs (family "hiatus") as this lect weights them (weighted_rules), re-fire memory
        aside."""
        rules = catalogue_for(self.profile, self.profile_key)
        hs = _HIATUS_ROWS.get(id(rules))
        if hs is None or hs[0] is not rules:
            hs = _HIATUS_ROWS[id(rules)] = (rules, [r for r in rules if r.family == "hiatus"])
        return [r for r in self.weighted_rules(hs[1], cache=False) if r.weight > 0]

    def line_pref(self, rule) -> float:
        """The line's standing preference for a rule (line drift): its family's and its row's lognormal, keyed by the line
        (hiatus_key, inherited from the proto), times this lect's own small jitter when it is a daughter."""
        line = self.hiatus_key or self.id
        b = base_id(rule.id)
        fam = rule.family or b.split(".")[0]
        f = _lognormal(f"{line}|fam|{fam}", LINE_FAMILY_SIGMA) * _lognormal(f"{line}|row|{b}", LINE_ROW_SIGMA)
        if self.hiatus_key:
            f *= _lognormal(f"{self.id}|bud|{b}", LINE_BUD_SIGMA)
        return f

    def hiatus_pref(self, rule) -> float:
        """The line's standing preference for a hiatus repair: a lognormal (sigma HIATUS_SPREAD) keyed by the line
        (hiatus_key) and the rule, so daughters resolve hiatus as their parent did."""
        key = (self.hiatus_key or self.id) + "|" + base_id(rule.id)
        v = _PREF.get(key)
        if v is None:
            import zlib
            z = float(np.random.default_rng(zlib.crc32(key.encode("utf-8"))).normal())
            v = _PREF[key] = math.exp(HIATUS_SPREAD * z)
        return v

    def _series_drag(self, rule, segs0, kyr: float) -> int:
        """PW-1537 R3: a change that took a sound's last plain partner away takes the marked members of its series along
        (kʼ follows k > tʃ as tʃʼ, ǀʰ follows ǀ > k as kʰ, a˯ follows a > ɑ): sound changes act on natural classes, and
        a marked series member implies its plain partner at the same place (Maddieson 1984; Lass 1984 on series
        changes). A marked sound whose partner was not there before, or moved where the mark cannot go, stays. Returns
        the words changed."""
        if self.lexicon is None:
            return 0
        before = {replace(x, length=0) for x in segs0}
        now = self.all_segments()
        have = {replace(x, length=0) for x in now}
        moves = {}
        for s in now:
            if s.kind not in ("C", "V") or not (_marked(s) or _click_member(s)):
                continue
            cands = _click_partner(s) if _click_member(s) else _partners(s)
            if cands & have:
                continue
            for c in sorted(cands & before, key=lambda x: x.voice):
                o = RU._single(rule, c)
                if o and len(o) == 1 and o[0] != c:
                    t = _remark(o[0], s)
                    if t is not None and t != s and not RU.impossible(t):
                        moves[s] = t
                    break
        if not moves:
            return 0

        def fn(f, *_a):
            return tuple(moves.get(x, x) for x in f)
        n = LX.apply_rule_to_lexicon(self.lexicon, fn, rule.id, kyr, self.id)
        GR = _gr_mod()
        if GR is not None and self.grammar is not None:
            g = GR.apply_rule_to_grammar(self.grammar, fn, rule.id, kyr)
            n += g if isinstance(g, int) else len(g or ())
        self.touch()
        return n

    def _apply_rule(self, rule, kyr: float, origin: str | None = None, remember: bool = True,
                    cause: str | None = None) -> int:
        self._last_kyr = float(kyr)
        segs0 = self.all_segments()
        memo = getattr(self, "_step_pairs", None)
        if memo is None or memo[0] != round(float(kyr), 6):
            memo = self._step_pairs = (round(float(kyr), 6), [])
        if any(_undoes(rule, y, x) for x, y in memo[1]):  # (a change and its reverse never fire in one step)
            return 0
        if self.alternates(rule, segs0, kyr):
            return 0
        stress = stress_of(self.inventory)
        fn = filtered_apply(rule, stress, segs0, self.inventory)
        self.touch()
        n = LX.apply_rule_to_lexicon(self.lexicon, fn, rule.id, kyr, self.id)
        GR = _gr_mod()
        had_glottal = base_id(rule.id) == "S042" and glottal() in self.segments()
        if GR is not None and self.grammar is not None:
            g = GR.apply_rule_to_grammar(self.grammar, fn, rule.id, kyr)
            n += g if isinstance(g, int) else len(g or ())
        self.touch()
        if n == 0:  # (a rule that changed nothing is not a change: no record)
            return 0
        self.changes.append({"kyr": round(float(kyr), 3), "rule": rule.id, "cause": cause or rule.cause, "origin_lect": origin})
        self._series_drag(rule, segs0, kyr)
        for x in segs0:
            o = RU._single(rule, x)
            if o and len(o) == 1 and o[0] != x:
                memo[1].append((x, o[0]))
        if (rule.id.startswith("dispersion.") or "/" in rule.id) and rule.id not in self.rule_text:
            self.rule_text[rule.id] = RU.describe(rule)
        from . import phonology as PH
        PH.on_change(self, rule, kyr)  # (a conditioned change lives on as a rule of the lect's phonology)
        kd = _ins_del(rule, segs0)
        if kd is not None:
            for x in kd[1]:
                self.insdel[x] = (round(float(kyr), 3), kd[0])
        if remember:  # (a hiatus repair is not drawn, so it keeps no re-fire memory)
            self.fired.setdefault(base_id(rule.id), []).append(round(float(kyr), 3))
        if base_id(rule.id) == "S042" and not had_glottal and not self.glottal_phonetic:
            self.glottal_phonetic = True
        self.rules_applied += 1
        self._dirty = True
        return n

    def rule_pool(self, rules, kyr: float, weights: dict | None = None, with_mass: bool = False):
        """The rules this lect may draw now: the down-weighted catalogue (weighted_rules) with the driver's weight overrides
        (history.RULE_WEIGHT) and the line's drift (line_pref), epenthesis re-pointed at the lect's epenthetic vowel, and the
        re-fire memory applied. ``with_mass``: also the total weight including the rows the re-fire memory sets aside (the
        mass rules.pick_rule draws against, so a blocked row's share fires nothing rather than going to the others)."""
        weights = weights or {}
        out = []
        mass = 0.0
        for r in self.weighted_rules(rules):
            w = weight_override(weights, r)
            w = self.line_pref(r) * (1.0 if w is None else w)
            mass += r.weight * w
            if not self.may_fire(r, kyr):
                continue
            r = replace(r, weight=r.weight * w)
            v = reduction_variant(epenthesis_variant(r, self.inventory), self.inventory)
            out.append(v)
        return (out, mass) if with_mass else out

    def step(self, rng, n_generations: float, kyr: float, ctx: dict) -> list:
        """Advance by n generations in one batch (one frame interval). ctx: contact_words {lect id: Lexicon}, niche, l2,
        population, isolation, rate_scale, replace_scale. Returns the rules that fired (for the wave)."""
        self.l2 = float(ctx.get("l2", self.l2))
        self.population = float(ctx.get("population", self.population))
        self.isolation = float(ctx.get("isolation", self.isolation))
        self.generations += n_generations
        self._last_kyr = float(kyr)
        self.end_burst(kyr)
        fired = []
        lam = n_generations * RATE_RULE * ctx.get("rate_scale", 1.0) * self.rate_now(kyr)
        k = int(rng.poisson(lam)) if lam > 0 else 0
        if k:
            rules = catalogue_for(self.profile, self.profile_key)
            pool, mass = self.rule_pool(rules, kyr, ctx.get("rule_weight"), with_mass=True)
            forms = segs = stress = None
            cum = RU.cumulative_weights(pool)
            for _ in range(k):
                if forms is None:  # (read again only after a change: most draws now fire nothing)
                    forms, segs, stress = self.load_forms(), self.segments(), stress_of(self.inventory)
                r = RU.pick_rule(rng, pool, forms, segs, stress, mass=mass, cum=cum)
                if r is None:
                    continue
                if self.phonotactic_veto(r, rng):
                    continue
                if not self.may_fire(r, kyr):  # (a dispersion push made on the fly that fired already)
                    continue
                forms = None
                if self.apply_rule(r, kyr) > 0:
                    fired.append(r)
                    pool = [x for x in pool if base_id(x.id) != base_id(r.id)]  # (its weight stays in mass: set aside)
                    cum = RU.cumulative_weights(pool)
        self.gap_fill(rng, n_generations, kyr)
        self.cap_inventory(kyr)  # (also catches segments brought by wave adoptions applied before this step)
        self.sync()
        self.touch()
        from . import phonology as PH
        PH.update(self, kyr)  # (age the live rules; the inventory carries them for the words made below)
        rs = ctx.get("replace_scale", 1.0)
        typ = getattr(self.grammar, "typology", None)
        self.lexicon.gram_forms = _gram_forms(self.grammar)
        LX.step(rng, self.lexicon, n_generations * rs, self.inventory, contact_words=ctx.get("contact_words"), kyr=kyr,
                lect_id=self.id, niche_weights=ctx.get("niche"), profile=self.profile,
                head_first=getattr(self.lexicon, "head_first", None), contact_weights=ctx.get("contact_weights"),
                numeral_base=typ.get("numeral_base") if isinstance(typ, dict) else None, population=self.population,
                kin_weights=ctx.get("kin"), speech_taboo=ctx.get("speech_taboo", 1.0))
        GR = _gr_mod()
        if GR is not None and self.grammar is not None:
            gctx = {"l2": self.l2, "population": self.population, "isolation": self.isolation, "kyr": kyr, "lect": self.id,
                    "lexicon": self.lexicon, "inventory": self.inventory}
            grammar_step(GR, rng, self, n_generations, gctx)
        return fired

    def record_shares(self, kyr: float) -> None:
        if self.shares:
            self.shares_history.append([round(float(kyr), 3), {k: round(v, 3) for k, v in self.shares.items() if v > 0.005}])


def one_off(rule) -> bool:
    """A one-off row (ONE_OFF_IDS: the whole-class coda changes): at most ONE_OFF_MAX firings a line."""
    return base_id(rule.id) in ONE_OFF_IDS


def _lognormal(key: str, sigma: float) -> float:
    """exp(sigma z), z a standard normal fixed by the key (crc32-seeded, so the same in every process and run)."""
    v = _PREF.get((key, sigma))
    if v is None:
        import zlib
        v = _PREF[(key, sigma)] = math.exp(sigma * float(np.random.default_rng(zlib.crc32(key.encode("utf-8"))).normal()))
    return v


_marked = marked_sound   # (PW-1537 R3; inventory.py, shared with the proto draw)
_partners = plain_partners


def _click_member(s) -> bool:
    """A click of a series other than the plain one (voiced, nasal, breathy, aspirated or glottalized accompaniment): it
    goes where the plain click at its place goes (PW-1537 R3, declicking per place: elf 7 lost plain ǀ ǁ ǃ ǂ and kept
    the voiced, nasal and ejective clicks at those places; a click language that declicks replaces a place across its
    accompaniments: sound changes act on classes)."""
    return s.kind == "C" and s.manner == 8 and bool(s.voice or s.prenasal or s.phonation or s.larynx)


def _click_partner(s) -> set:
    return {replace(s, voice=0, prenasal=0, phonation=0, larynx=0, length=0)}


def _remark(q, s):
    """The sound q (where s's plain partner went) with s's marks; None where the mark cannot go on q (an aspirate or
    ejective mark on anything but a stop, affricate or click)."""
    if q.kind != s.kind:
        return None
    if s.larynx in (1, 2) and (q.kind != "C" or q.manner not in (0, 1, 8)):
        return None
    t = replace(q, phonation=s.phonation if s.phonation in (3, 4) else q.phonation, register=s.register or q.register,
                length=s.length)
    if s.larynx in (1, 2):
        t = replace(t, larynx=s.larynx, voice=0 if s.larynx == 2 else s.voice)
    if _click_member(s):   # (the click's accompaniment rides on the stop it became: ᵑǀ > ᵑk, ǀ̬ > ɡ, ǀ̬ʱ > ɡʱ)
        if q.kind != "C" or q.manner not in (0, 1, 8):
            return None
        t = replace(t, voice=0 if s.larynx == 2 else s.voice, prenasal=s.prenasal,
                    phonation=s.phonation if s.phonation else t.phonation)
    return t


def _ins_del(rule, segs) -> tuple | None:
    """("ins", {segment}) for an insertion, ("del", {segments of `segs` it targets}) for a loss, tone set aside; None for
    any other change (a staged rule's later steps are its own business: S056's j lost after the sibilant it made)."""
    ch = rule.change
    if rule.then:
        return None
    if ch.kind == "insert" and ch.items:
        lit = ch.items[0][1]
        return ("ins", {RU._tonekey(lit)}) if lit is not None else None
    if ch.kind == "delete" and rule.target is not None and not rule.span:
        hit = {RU._tonekey(x) for x in segs if rule.target(x)}
        return ("del", hit) if hit else None
    return None


def _undoes(rule, y, x) -> bool:
    """Does `rule` turn segment y (a lone segment, context aside) back into x?"""
    o = RU._single(rule, y)
    return bool(o) and len(o) == 1 and o[0] == x


def partial_pick(form, share: float, salt: str) -> bool:
    """Is this form among the `share` of forms a partial change takes (a stable crc32 of its IPA and `salt`, the same in
    every process: the words a lexical-diffusion change has reached)?"""
    import zlib
    from .percepts import word_ipa
    return zlib.crc32(f"{salt}|{word_ipa(form)}".encode("utf-8")) < share * 4294967296.0


def _axes_apart(a, b) -> int:
    """How many percept axes (tone aside) two segments differ on."""
    from dataclasses import fields
    return sum(1 for f in fields(a) if f.compare and f.name != "tone" and getattr(a, f.name) != getattr(b, f.name))


_UNIT: dict = {}


def _unit(x):
    """What the inventory cap counts: a consonant, or a vowel with its tones set aside, the second voice's too
    (memoized: millions of calls). (Syrinx lane: a second-voice tone made by a coda rule on a few words was a 'rare new
    unit' and folded back at once, a gate the first voice's tone never met; pass C folded 30 that way. Both tones are now
    left to the hygiene, tone_hygiene and voice2_hygiene.)"""
    if (not x.tone and not x.tone2) or x.kind != "V":
        return x
    u = _UNIT.get(x)
    if u is None:
        u = _UNIT[x] = replace(x, tone=0, tone2=0)
    return u


FOLD_SLACK = 1.0  # a fold may land up to this much farther (percepts.distance) than the nearest unit, to reach a cheaper one


def fold_target(x, targets, cnt: dict, cost, distance):
    """Where a folded unit goes: among the units within FOLD_SLACK of the nearest, the cheapest for the voice (the commoner
    or easier neighbour), then the commonest in the lexicon."""
    from .percepts import to_ipa
    d = {q: distance(x, q) for q in targets}
    near = min(d.values())
    pool = [q for q in targets if d[q] <= near + FOLD_SLACK]
    return min(pool, key=lambda q: (cost(q), d[q], -cnt.get(q, 0), to_ipa(q), repr(q)))


_SINGLE: dict = {}


def single(rule, x):
    """rules._single, memoized per (rule id, notation, segment): what the rule makes of a lone segment."""
    k = (rule.id, rule.notation, x)
    if k not in _SINGLE:
        o = RU._single(rule, x)
        _SINGLE[k] = None if o is None else tuple(o)
    return _SINGLE[k]


_HCOST: dict = {}


def human_cost(x) -> float:
    if x not in _HCOST:
        from . import profiles as PR
        _HCOST[x] = PR.human_cost(x)
    return _HCOST[x]


def size_steer(measure: str, n: int, d: int, n0: int = 0, sigma: float = SIZE_ANCHOR) -> float:
    """The size factor of a rule taking a count from n to n + d: PHOIBLE's prior ratio ** SIZE_K times the anchor ratio
    (lognormal of sigma `sigma`) around the line's count n0 (none when n0 is 0)."""
    from . import inventory as INV
    g = (INV.size_prior(measure, n + d) / INV.size_prior(measure, n)) ** SIZE_K
    if n0 > 0 and n + d > 0 and n > 0:
        a, b = math.log((n + d) / n0), math.log(n / n0)
        g *= math.exp(-(a * a - b * b) / (2.0 * sigma ** 2))
    return g


def _ease(touched, cost=None) -> float:
    cost = cost or human_cost
    ds = [cost(x) - math.fsum(cost(y) for y in o) for x, o in touched]
    ds = [d for d in ds if math.isfinite(d)]
    if not ds:
        return 1.0
    return min(EASE_CLAMP[1], max(EASE_CLAMP[0], math.exp(EASE_K * math.fsum(ds) / len(ds))))  # (fsum: exact, so the
    # order of a frozenset, which varies between processes with str hashing, cannot change a weight)


def is_stop(x) -> bool:
    """An oral stop (any larynx setting), not ʔ or a pharyngeal."""
    return x.kind == "C" and x.manner == 0 and x.place < 7


def stop_share(forms) -> float:
    """Oral stops over the supralaryngeal consonant tokens in `forms` (ʔ, h and the pharyngeals left out: a prothetic ʔ
    before every initial vowel is no reason to make more stops)."""
    c = n = 0
    for f in forms:
        for x in f:
            if x.kind == "C" and x.place < 7:
                n += 1
                c += is_stop(x)
    return c / n if n else STOP_NORM


def stop_bin(share: float) -> int:
    return int(round(math.log(max(share, 0.02) / STOP_NORM) / STOP_BIN))


def _stop_part(touched, sbin: int | None) -> float:
    """The stop steer of a rule (STOP_K): the mean change in stop-ness over the segments it rewrites (+1 a non-stop made a
    stop, -1 a stop made a non-stop or deleted), times -ln(share / STOP_NORM) at the lect's binned share."""
    if sbin is None or not sbin or not touched:
        return 1.0
    ds = [(1 if any(is_stop(y) for y in o) else 0) - (1 if is_stop(x) else 0) for x, o in touched]
    d = math.fsum(ds) / len(ds)
    if not d:
        return 1.0
    return min(STOP_CLAMP[1], max(STOP_CLAMP[0], math.exp(-STOP_K * d * sbin * STOP_BIN)))


def touched_by(rule, segs) -> list:
    """[(segment, its output tuple)] for the segments of `segs` a rule rewrites. An assimilation ([αplace] and the like, whose
    output depends on its neighbour; not vowel harmony) counts once per output it could make here: the target with the
    assimilating axes of each consonant of the lect that could condition it (place assimilation: not glottal or pharyngeal), so the inventory
    steer sees the homorganic nasals it brings in (before 2026-11-04 it saw nothing and nasal place assimilation, the most
    drawn rule, grew small inventories unchecked)."""
    out = []
    ch = rule.change
    if getattr(ch, "kind", None) == "assimilate" and getattr(ch, "source", None) in ("left", "right") and rule.target is not None:
        axes = tuple(getattr(ch, "axes", ()) or ())
        ctx = [y for y in segs if y.kind == "C" and not ("place" in axes and y.place in (7, 8))]
        for x in segs:
            if not rule.target(x):
                continue
            for y in sorted({replace(x, **{a: getattr(c, a) for a in axes}) for c in ctx} - {x}, key=repr):
                out.append((x, (y,)))
        return out
    for x in segs:
        o = single(rule, x)
        if o is None or o == (x,):
            continue
        out.append((x, o))
    return out


_COMMON: dict = {}


def common(x) -> bool:
    """A near-universal human phoneme (PHOIBLE share >= KEEP_SHARE)."""
    if x not in _COMMON:
        _COMMON[x] = x.kind in ("C", "V") and math.exp(-human_cost(x)) >= KEEP_SHARE
    return _COMMON[x]


def keep_part(rule, segs, forms, stress=None) -> float:
    """The keep steer: KEEP_FACTOR when the rule would leave no token of a near-universal phoneme (common()) that the lect's
    frequent `forms` hold, else 1. Only rules that rewrite such a phoneme are tried on the forms that contain it."""
    if not forms or rule.target is None:
        return 1.0
    hit = [x for x in segs if common(x) and rule.target(x)]
    if not hit:
        return 1.0
    for x in sorted(hit, key=repr):
        seen = False
        for f in forms:
            if x not in f:
                continue
            seen = True
            if x in RU.apply(rule, f, stress):
                break  # (some x survives: not a loss of the phoneme)
        else:
            if seen:
                return KEEP_FACTOR
    return 1.0


def ease_factor(rule, lect) -> float:
    """The ease drag and the stop steer for a lect (1 for a non-human voice): used to damp wave adoption of a change toward
    rarer sounds (history.interval), so a hard sound does not spread by contact more readily than it arises at home."""
    from . import profiles as PR
    if not PR.human_voiced(lect.profile):   # (another voice: its own make costs, no stop or keep steer)
        touched = touched_by(rule, lect.segments())
        return _ease(touched, _species_cost_fn(lect.profile)) if touched and lect.profile is not None else 1.0
    touched = touched_by(rule, lect.segments())
    if not touched:
        return 1.0
    forms = lect.load_forms()
    return (_ease(touched) * _stop_part(touched, stop_bin(stop_share(forms)))
            * keep_part(rule, frozenset(lect.segments()), forms, stress_of(lect.inventory)))


def _size_part(rule, touched: list, units: frozenset, base: dict | None, counts: dict | None,
               sigma: float = SIZE_ANCHOR) -> float:
    uncond = rule.target is not None and not rule.span and rule.env == RU.ANYWHERE and not rule.then
    outs = {_unit(y) for _x, o in touched for y in o}
    added = outs - units
    removed = ({_unit(x) for x, _o in touched} - outs) if uncond else set()
    g = 1.0
    for kind, measure in (("C", "consonants"), ("V", "vowels")):
        d = sum(1 for u in added if u.kind == kind) - sum(1 for u in removed if u.kind == kind)
        if d:
            n = counts[kind] if counts else sum(1 for u in units if u.kind == kind)
            g *= size_steer(measure, n, d, (base or {}).get(kind, 0), sigma)
    return min(SIZE_CLAMP[1], max(SIZE_CLAMP[0], g)) if g != 1.0 else 1.0


def size_factor(rule, lect) -> float:
    """The size steer alone for a lect (rule_factor's): used to damp wave adoption of a change that would take the lect's
    inventory away from its line's size, as it would be at home."""
    segs = frozenset(lect.segments())
    touched = touched_by(rule, segs)
    if not touched:
        return 1.0
    inv = lect.inventory
    counts = None if inv is None else {"C": len(inv.consonants), "V": len({_unit(v) for v in inv.vowels})}
    base, sigma = lect.size_anchor()
    return _size_part(rule, touched, frozenset(_unit(x) for x in segs), base, counts, sigma)


def rule_factor(rule, segs: frozenset, units: frozenset, human_voice: bool, base: dict | None = None,
                counts: dict | None = None, sbin: int | None = None, profile=None, sigma: float = SIZE_ANCHOR) -> float:
    """The lect-specific weight multiplier of a catalogue rule: NEW_SEG_WEIGHT when it would bring in a segment the lect
    lacks; the ease drag (EASE_K: PHOIBLE commonness of what it makes vs what it rewrites for human voices, the species cost (`profile`) for others); and the size
    steer (size_steer: PHOIBLE's inventory-size distribution at the count the rule would leave, over the count now, and
    the pull toward the line's proto count). A
    context-free rule removes the units it rewrites; a conditioned one keeps them (a split). counts: {"C", "V"} phoneme
    counts the size steer starts from (the inventory, allophones aside); default the surface units. sbin: the lect's binned
    oral-stop share (stop_bin) for the stop steer (human voices only; None: none)."""
    touched = touched_by(rule, segs)
    if not touched:
        return 1.0
    f = NEW_SEG_WEIGHT if any(y not in segs for _x, o in touched for y in o) else 1.0
    if human_voice:
        f *= _ease(touched) * _stop_part(touched, sbin)
    elif profile is not None:
        f *= _ease(touched, _species_cost_fn(profile))
    return f * _size_part(rule, touched, units, base, counts, sigma)


_SPECIES_COST: dict = {}


def _species_cost_fn(profile):
    """profiles.species_cost for one profile, memoized per segment (the ease drag of a non-human voice)."""
    from .profiles import species_cost
    key = id(profile)
    hit = _SPECIES_COST.get(key)
    if hit is None or hit[0] is not profile:
        memo: dict = {}

        def fn(x, _p=profile, _m=memo):
            v = _m.get(x)
            if v is None:
                v = _m[x] = species_cost(_p, x)
            return v
        hit = _SPECIES_COST[key] = (profile, fn)
    return hit[1]


def grammar_step(GR, rng, lect: Lect, n: float, gctx: dict) -> None:
    """grammar.step, with the typology drift on (per generation, at the lect's own rate, as sound change). Until the
    2026-11-04 round no caller asked for the drift, so typology only changed by calques on shift."""
    from . import phonology as PH
    before = PH.cell_parts(lect.grammar)
    GR.step(rng, lect.grammar, n, inv=lect.inventory, lexicon=lect.lexicon, l2_share=gctx["l2"],
            population=gctx["population"], isolation=gctx["isolation"], kyr=gctx["kyr"], drift_typology=True,
            rate=lect.rate_now(gctx["kyr"]) if hasattr(lect, "rate_now") else getattr(lect, "rate", 1.0),
            lect=getattr(lect, "id", None),
            lean=GR.leanings(getattr(lect, "gen_yr", None), getattr(lect.profile, "pitch_range", None))
            if hasattr(GR, "leanings") else None)
    PH.apply_new_cells(lect.grammar, lect.inventory, before)   # (new cells join under the live rules: phonology.py)


def _accepted(fn, kw: dict) -> dict:
    import inspect
    try:
        ps = inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return {}
    if any(p.kind == p.VAR_KEYWORD for p in ps.values()):
        return kw
    return {k: v for k, v in kw.items() if k in ps}


def _gram_forms(g) -> dict:
    """form -> the source concepts of the live free-word and clitic grams with that form (lexicon._renewal_boost renews a
    word that sounds like one of them and is not its source)."""
    out: dict = {}
    for gr in getattr(g, "grams", None) or ():
        if gr.live and gr.level <= 1 and gr.form:
            out.setdefault(tuple(gr.form), set()).add(gr.source[0] if gr.source else "?")
    return out


def _deepcopy(x):
    import copy
    return copy.deepcopy(x)


def _copy_inv(inv):
    if inv is None:
        return None
    try:
        from dataclasses import replace
        return replace(inv)
    except TypeError:
        return _deepcopy(inv)


def _sync_inventory(lect: Lect, kyr: float | None = None) -> None:
    """Keep the inventory's segment lists in step with the forms after a sound change (so new words use today's sounds): the
    tone marks are made consistent first (tone_hygiene), then the inventory is observed from the forms with its tones the
    ones on the vowels, and a ʔ that only prothesis put before initial vowels is left out (not a phoneme)."""
    tones = tone_hygiene(lect, kyr)
    voice2_hygiene(lect, kyr)
    inv = _inv_mod().observed(lect.inventory, lect.all_forms(), lect.profile)
    inv = _inv_mod().retemplate(inv, lect.all_forms())
    if hasattr(inv, "tones"):
        inv = replace(inv, tones=tones)
    if lect.glottal_phonetic:
        q = glottal()
        if all(j == 0 and len(f) > 1 and f[1].kind == "V" for f in lect.all_forms() for j, x in enumerate(f) if x == q):
            if q in inv.consonants and len(inv.consonants) > 1:
                inv = replace(inv, consonants=[x for x in inv.consonants if x != q])
        else:
            lect.glottal_phonetic = False  # (ʔ now stands elsewhere too: it has phonemicized)
    lect.inventory = inv


def tone_hygiene(lect: Lect, kyr: float | None = None) -> list:
    """Tone marks and the tone inventory agree. No marks: no tones. Fewer than 2 distinct tones over the core-list vowels, marks
    on under TONE_MIN_MARKED of the core vowels, or a profile that does not hear tone: no contrast, so the stray marks are
    stripped everywhere (a `simplification`, cause "dispersion"). Otherwise the lect is
    tonal, its tones the levels present, and a vowel left unmarked takes the commonest level (`tone.phonemic/<t>`, cause
    "tonogenesis"), since in a tone language every syllable carries one. Returns the tone list."""
    segs = lect.all_segments()
    if level_stray_contours(lect, segs, kyr):
        segs = lect.all_segments()
    marked = sorted({x.tone for x in segs if x.kind == "V" and x.tone})
    if not marked:
        return []
    cnt: dict = {}
    for c in _core():
        w = lect.lexicon.get(c)
        if w is not None:
            for x in w.form:
                if x.kind == "V" and x.tone:
                    cnt[x.tone] = cnt.get(x.tone, 0) + 1
    kyr = float(kyr if kyr is not None else lect.born_kyr)
    nv = sum(1 for c in _core() if lect.lexicon.get(c) is not None for x in lect.lexicon.get(c).form if x.kind == "V")
    hears = (getattr(lect.profile, "hear", None) or {}).get("tone", 1.0) > 0
    if len(cnt) < 2 or not hears or sum(cnt.values()) < TONE_MIN_MARKED * nv:
        mapping = {x: replace(x, tone=0) for x in segs if x.kind == "V" and x.tone}
        what = ("tone marks dropped (" + ", ".join(sorted({_tone_name(x.tone) for x in mapping})) + "): "
                + ("no tone contrast" if len(cnt) < 2 else "not heard" if not hears else "too few marked vowels to phonemicize"))
        _map_forms(lect, mapping, "simplification", kyr)
        lect.changes.append({"kyr": round(kyr, 3), "rule": "simplification", "cause": "dispersion", "origin_lect": None,
                             "merged": what})
        return []
    if not any(x.kind == "V" and not x.tone for x in segs):
        return tonemes(segs)
    d = max(cnt, key=lambda t: (cnt[t], -t))
    mapping = {x: replace(x, tone=d) for x in segs if x.kind == "V" and not x.tone}
    if getattr(lect.inventory, "tones", None):
        # (already a tone language: a toneless vowel from a loan, an epenthesis or a new vowel quality just takes the
        # default tone, as every syllable must; not a sound change and not tonogenesis, so no change record)
        rid = f"tone.default/{d}"
        _map_forms(lect, mapping, rid, kyr)
        lect.rule_text.setdefault(rid, f"a vowel with no tone (from a loan, an epenthesis or a new vowel) took the "
                                       f"{_tone_name(d)} tone, the language's default")
        return tonemes(lect.all_segments())
    rid = f"tone.phonemic/{d}"
    _map_forms(lect, mapping, rid, kyr)
    lect.rule_text.setdefault(rid, f"tone became phonemic: vowels with no tone mark took the {_tone_name(d)} tone, the commonest "
                                   "(tonogenesis: phonemicization)")
    lect.changes.append({"kyr": round(kyr, 3), "rule": rid, "cause": "tonogenesis", "origin_lect": None})
    return tonemes(lect.all_segments())


TONE2_MIN_MARKED = 0.1  # a second-voice tone contrast stays only once marks stand on this share of the lexicon's second-voice vowels


def voice2_hygiene(lect: Lect, kyr: float | None = None) -> bool:
    """Second-voice tone marks agree with a contrast (syrinx lane, 2026-11-08; docs/review/language/syrinx.md). The second
    voice moving in parallel (tone2 0) is itself a category, the unmarked one, so a split needs two categories over the
    lexicon's second-voice vowels (all words, not the core list: they are rare), marks on at least TONE2_MIN_MARKED of them (lower than the first voice's
    TONE_MIN_MARKED: no default tone fills the rest) and an ear that hears the second voice's pitch; otherwise every
    second-voice tone mark is stripped (a `simplification`, cause "dispersion"), the second voice moving in parallel again.
    A tone2 left on a vowel that lost its second voice goes too. Returns whether anything changed."""
    segs = lect.all_segments()
    orphan = {x: replace(x, tone2=0) for x in segs if x.kind == "V" and x.tone2 and not x.source2}
    if orphan:
        _map_forms(lect, orphan, "simplification", float(kyr if kyr is not None else lect.born_kyr))
        segs = lect.all_segments()
    if not any(x.kind == "V" and x.tone2 for x in segs):
        return bool(orphan)
    cnt: dict = {}
    for w in lect.lexicon.words.values():   # (the whole lexicon: second-voice vowels are rare, the core list holds few)
        for x in w.form:
            if x.kind == "V" and x.source2:
                cnt[x.tone2] = cnt.get(x.tone2, 0) + 1
    n = sum(cnt.values())
    marked = n - cnt.get(0, 0)
    hears = (getattr(lect.profile, "hear", None) or {}).get("tone2", 1.0) > 0
    if len(cnt) >= 2 and hears and marked >= TONE2_MIN_MARKED * n:
        return bool(orphan)
    kyr = float(kyr if kyr is not None else lect.born_kyr)
    mapping = {x: replace(x, tone2=0) for x in segs if x.kind == "V" and x.tone2}
    what = ("second-voice tone marks dropped (" + ", ".join(sorted({_tone_name(x.tone2) for x in mapping})) + "): "
            + ("no second-voice tone contrast" if len(cnt) < 2 else "not heard" if not hears
               else "too few marked second-voice vowels to phonemicize"))
    _map_forms(lect, mapping, "simplification", kyr)
    lect.changes.append({"kyr": round(kyr, 3), "rule": "simplification", "cause": "dispersion", "origin_lect": None,
                         "merged": what})
    return True


_CONTOUR_PARTS = {4: (1, 3), 5: (3, 1)}  # rising = low + high, falling = high + low
CONTOUR_MIN = 0.01  # a contour on short vowels stays a toneme only on this share of the toned vowel tokens or more


def level_stray_contours(lect, segs, kyr=None) -> bool:
    """A contour tone that stands on a short vowel in only a few words (under CONTOUR_MIN of the toned vowel tokens) is
    levelled to high, as S227 and S228 do: a contour needs duration (Zhang 2002, The Effects of Duration and Sonority on
    Contour Tone Distribution), and a handful of short contours left by a vowel shortening or a fusion is not learned as a
    new toneme. Tonogenesis from codas marks many words at once and passes. Before this (sound lane pass 3) such strays were
    the commonest way a tonal lect gained a toneme, and four-tone systems outnumbered two-tone ones 10 to 1 (WALS 13A: simple
    systems are 60% of tonal languages). Returns whether anything changed."""
    short = [x for x in segs if x.kind == "V" and x.tone in _CONTOUR_PARTS and not x.length]
    if not short or lect.lexicon is None:
        return False
    cnt: dict = {}
    toned = 0
    for w in lect.lexicon.words.values():
        for x in w.form:
            if x.kind == "V" and x.tone:
                toned += 1
                if x.tone in _CONTOUR_PARTS and not x.length:
                    cnt[x.tone] = cnt.get(x.tone, 0) + 1
    stray = {t for t, n in cnt.items() if n < CONTOUR_MIN * toned}
    if not stray:
        return False
    mapping = {x: replace(x, tone=3) for x in short if x.tone in stray}
    rid = "tone.contour_levelled"
    _map_forms(lect, mapping, rid, float(kyr if kyr is not None else lect.born_kyr))
    lect.rule_text.setdefault(rid, "a rising or falling tone left on a short vowel in a few words levelled to high")
    return True


def tonemes(segs) -> list:
    """The lect's tonemes from the tones on its vowels: every level tone, and a contour (rising, falling) only where it
    stands on a short vowel. A contour found only on long vowels is two level tones on two moras (Yoruba, Hausa: a long
    vowel carries a sequence, as fusion makes them, H + L on aa), so it adds its levels, not a toneme. Before this (sound
    lane, 2026-11-08) every fused long vowel added a contour toneme and 78% of tonal lects ended with 5 tones (WALS 13A
    and PHOIBLE: two or three tones are the commonest systems)."""
    out = set()
    for x in segs:
        if x.kind != "V" or not x.tone:
            continue
        if x.tone in _CONTOUR_PARTS and x.length:
            out.update(_CONTOUR_PARTS[x.tone])
        else:
            out.add(x.tone)
    return sorted(out)


_CORE: list = []


def _core() -> list:
    if not _CORE:
        _CORE.extend(sorted(LX.CORE100))
    return _CORE


def _tone_name(t: int) -> str:
    return {1: "low", 2: "mid", 3: "high", 4: "rising", 5: "falling", 6: "extra-high", 7: "extra-low"}.get(t, f"tone {t}")


def _map_forms(lect: Lect, mapping: dict, rid: str, kyr: float) -> None:
    def fn(f, stem_index=0, m=mapping):
        return tuple(m.get(y, y) for y in f)
    LX.apply_rule_to_lexicon(lect.lexicon, fn, rid, kyr, lect.id)
    GR = _gr_mod()
    if GR is not None and lect.grammar is not None:
        GR.apply_rule_to_grammar(lect.grammar, fn, rid, kyr)
    lect.touch()
