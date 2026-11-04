"""Words, the concept list and the lexical history of a lect (architecture.md section 6).

A `Lexicon` maps concept ids to `Word`s; every word carries its etymology as a chain of `EtymStep`s, oldest first. Over
time (`step`) words are replaced at a rate that falls with their frequency class (Pagel, Atkinson and Meade 2007: frequent
words are replaced about ten times slower than rare ones), and the replacement comes from somewhere: a derivation from a
related word, a compound, a colexification shift from a CLICS neighbour (Rzymski et al. 2020), a loan from a contact lect
(heard through the borrower's ears and inventory, then repaired), or, for animals and dangerous things, a taboo
paraphrase. Language shift leaves substrate words (`substrate_transfer`), sound change runs over every form
(`apply_rule_to_lexicon`).

Concept ids: Concepticon-style upper-case glosses ("WATER", "RIVER", "MILK (SOURED)") for plain concepts, and prefixed
ids for items the run itself defines (`crop:<id>`, `animal:<id>`, `fuel:<id>`, `good:<id>`). A prefixed id that names a
concept already on the core list (fuel:wood, animal:dog, good:salt) is an alias of it (`ALIASES`, resolved by
`Lexicon.get`), so a lect never has two words for WOOD. The god domains of `gods.DOMAINS` are plain concepts (SEA, STORM,
SMITHING ...) tagged with domain "god"; `GOD_DOMAIN_CONCEPT` maps a domain to its concept.

The etymology chain is the history of the *form*: a derived word's chain is its base's chain plus the derivation step,
a loan's chain is the donor word's chain plus the `borrow:<lect>` step, so a food word's chain is its route. Steps are
never removed or reordered; a run of sound changes within one interval (same kyr, same lect) collapses into one step.
`kyr` is kyr *ago*, so oldest-first means `kyr` does not increase along the chain.
"""

from __future__ import annotations

import csv
import functools
import math
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable, Iterable

import numpy as np

from . import inventory as _inv
from .percepts import Segment, from_ipa, syllabify, word_ipa

DATA = Path(__file__).parent / "data"

Form = tuple  # tuple[Segment, ...]

# --- calibration --------------------------------------------------------------------------------------------------------

GEN_YR_HUMAN = 27.7
# Hazard per generation = BASE_REPLACE * RATE_BY_FREQ[freq_class]. RATE_BY_FREQ is geometric, class 5 (rare, fast)
# FREQ_SPREAD times class 1 (frequent, slow): Pagel, Atkinson & Meade 2007 (Nature 449:717) find frequent words replaced
# several times slower than rare ones (frequency explains about half the variance in their rates). BASE_REPLACE is solved
# so the Swadesh-100 (with the class mix concepts.tsv gives it: 31/31/13/16/9) keeps 86% of its words per 1000 yr at
# 27.7-yr generations (`calibrate_base_replace`, checked by tests/test_language_lexicon.py), the top of the 80-86% per
# lineage of the lexicostatistics literature (Swadesh 1955; Lees 1953 81% on the 200 list).
# 2026-11-04 (word families round): FREQ_SPREAD 10 -> 4 and history.REPLACE_SCALE 1.25 -> 1. With a 10x spread the core
# end held sister lects' true shared roots at ~0.57 (1-2 kyr apart) while the slow class-1 words kept 0.15 of the core
# shared at 10 kyr; 4x gives ~0.64 and ~0.09 in the isolated-lineage harness. Then 4 -> 3: the full run's human horizon
# sat at 10.6 kyr (target 6-10) with sisters at 0.51; 3x keeps the 1.5-kyr share (-1%) and cuts the 10-kyr tail ~17%
# (calibration.md, "Word families and derivation round"). Pagel et al. 2007 find a larger spread on the 200 list; ours
# stays at 3x because recognisability, not survival alone, ends the horizon.
FREQ_SPREAD = 3.0
RATE_BY_FREQ = {c: FREQ_SPREAD ** ((c - 1) / 4) for c in range(1, 6)}
SWADESH_RETENTION_1KYR = 0.86
BASE_REPLACE = 0.0026726   # per generation; re-solve with calibrate_base_replace() if the table or RATE_BY_FREQ change

# Where a replacement comes from. A fresh root ("coin", origin unknown) keeps a real share: in attested histories a good
# part of the basic vocabulary has no known etymology, and without it every new word is built from old ones and words
# only grow. Only nouns compound (for the rest the compound share goes to the rest); borrow needs a contact lect, taboo a taboo
# concept, shift a CLICS neighbour with a word.
SOURCES = {"derive": 0.36, "compound": 0.22, "shift": 0.10, "renew": 0.12, "coin": 0.03, "borrow": 0.12, "taboo": 0.05}
# (2026-11-04, word families round: coin 0.15 -> 0.03, shift 0.15 -> 0.10, "renew" (a word replaced by its own diminutive or frequentative,
# RENEW_LITTLE / RENEW_INTENS) and the fallback chain derive > compound > shift > renew > borrow > coin. In
# etymological dictionaries most "unknown origin" basic words turn out to be loans from unattested neighbours or obscured
# derivations; a word from nothing is the last resort, not a fixed share)
COLEX_MIN_FAMILIES = 12       # proto colexifications only from CLICS edges seen in at least this many families
COLEX_P_PER_FAMILY = 0.008    # chance a proto-lexicon colexifies an edge, per family attesting it (TREE/WOOD 59 -> 0.47)
MAX_SYLL = 3                  # a derived word has at most this many syllables (the base is clipped to fit)
MAX_SYLL_COMPOUND = 4         # a compound has at most this many (its parts are clipped to their first 1-2 syllables)
MAX_SEG = 12                  # and no new word is longer than this many segments
# (the three caps are for a language of the reference syllable space; `limits(inv)` scales them by `length_scale(inv)`)

# Word length follows the syllable space. Nettle 1995 (Linguistics 33:359, ten languages) and 1998 (J. Quant. Ling.
# 5:240, twelve West African languages) find dictionary stems shorter the larger the segment inventory: combined fit
# X = 17.87 S^-0.31 segments (r = 0.82; S counts each vowel x tone combination), from ~8.5 segments at S = 11
# (Rotokas-sized: 6 C + 5 V) to ~5.4 at S = 47 and ~4 at S = 119 (!Xu). The synergetic argument behind it (Kohler 1986)
# is a coding one: a lexicon of fixed size needs length ~ log(N) / log(alphabet). We measure the alphabet as the
# syllable space (`syllable_space`: the effective number of distinct syllables the inventory and its templates allow, so
# a CV-only language counts as small even with a mid-sized inventory, Maddieson 2006 / Fenk-Oczlon & Fenk 1999 on the
# syllable-complexity vs word-length trade-off) and damp the pure coding law to match Nettle's slope:
#   length_scale = (LN_SIGMA_REF / ln sigma) ** LENGTH_EXP
# LENGTH_EXP = 0.7 turns the coding ratio between a Rotokas-like CV language (sigma ~35) and a 25 C / 8 V (C)V(C) one
# (sigma ~1100, ln ratio 1.98) into a syllable ratio of 1.61, close to Nettle's fit (segments 8.5 vs 5.7 at
# 1.9 vs 2.5 segments a syllable: 1.8). Descriptive grammars agree on the small end: Rotokas (Firchow and Firchow 1969;
# Robinson 2006) has mostly 2-4-syllable roots (avaraka, kopiroa, vokovoko); Piraha (Everett 1986; 8 C, 3 V, 2 tones)
# few monosyllables, roots mostly 2-3 syllables. Hawaiian (13 segments, CV(V)) stems average 7.1 segments (Nettle 1995).
# LN_SIGMA_REF is the median ln sigma of human proto inventories drawn by inventory.draw_inventory (so the median
# language keeps the old lengths). The scale is clipped to LENGTH_SCALE_RANGE so 6 C + 3 V and 80 C both stay sane.
# The caps (`limits`) grow with the scale but never fall below MAX_SYLL / MAX_SYLL_COMPOUND / MAX_SEG: a language
# with a huge syllable space gets shorter roots, but its derivations and compounds are not clipped harder (clipping
# only makes homophones).
LN_SIGMA_REF = 7.7      # median ln sigma of 300 human draw_inventory() protos (quartiles 6.7 and 8.6)
LENGTH_EXP = 0.7
LENGTH_SCALE_RANGE = (0.7, 2.0)
BUILD_MIN_FAMILIES = 5        # CLICS edges a derivation's weight is joined with (3-4 families is mostly chance)
SHIFT_GAP = 50.0              # generations: a concept takes or passes on a word by colexification shift at most this often
# Semantic shifts (2026-11-04, compounds and shifts round): a concept takes a neighbour's word only along a CLICS3
# colexification of >= SHIFT_MIN_FAMILIES families (SHIFT_MIN_CORE for the core vocabulary: the Swadesh-100 and
# frequency classes 1-2, whose shifts are rarest; Pagel 2007), between concepts of one semantic field (concepts.tsv /
# CLICS3 field: HAND/ARM, SALTY/SOUR, GIRL/CHILD) and one part of speech, or along an attested pathway of
# data/derivations.tsv's 'shift' rows across fields (TREE > WOOD, SKY > GOD, SEE > KNOW: Buck 1949, Wilkins 1996,
# Sweetser 1990) or parts of speech (grammaticalization, Heine & Kuteva 2002: BELLY > IN, WITH > AND). The 4-family fallback is gone: DOG ~ MOON, EGG ~ NAME, SEED ~ EYE, TREE ~ FIRE are colexifications
# of a few languages or of a sense we do not model (seed 'grain' ~ eyeball), not paths words travel. A word shifted
# within SHIFT_CHAIN_KYR is not taken again (no PULL > SUCK > EAT > TREE in a few millennia).
SHIFT_MIN_FAMILIES = 5
SHIFT_MIN_CORE = 6
SHIFT_CHAIN_KYR = 3.0
HOMOPHONE_BOOST = 4.0         # replacement hazard x this for the rarer members of a homophone group of 3+ or of an
                              # accidental pair (repair by renewal)
COLEX_BOOST = 4.0             # and x this for the rarer member of a deliberate pair (a shift; a proto pair: x1)
AFFIX_RENEW = 0.01            # per generation: a derivational affix worn to nothing is renewed from a word (or coined)
ELAB_THRESHOLD = 0.5          # niche weight above which a concept starts to split
ELAB_RATE = 0.02              # per generation, times the niche weight, once past the threshold
AFFIX_MEANINGS = ("little", "place", "agent", "thing", "do", "like", "cause", "intens")  # derivational morphemes, one form each
# Derivation is table-driven (data/derivations.tsv: relation, base, target): an affix only makes the targets its
# meaning gives it from bases that fit (HUNT -> HUNTER 'agent', RIVER -> STREAM 'little', SLEEP -> BED 'place', CUT ->
# KNIFE 'thing', BLOOD -> RED 'like', SALT -> SALT (FOOD) 'do', DIE -> KILL 'cause'). Stacking: a living word carries at most
# MAX_AFFIXES transparent derivational affixes and MAX_MORPHEMES morphemes in all; a derivation older than OPAQUE_KYR,
# or one whose base word has since been replaced, or one under a later loan, shift, taboo or substrate step, is
# lexicalised: the word counts as a simple root again and may take new affixes (burden is no longer felt as bear + -th).
MAX_AFFIXES = 2
MAX_MORPHEMES = 3
OPAQUE_KYR = 3.0
# the expressive diminutive renewal: a word of these classes may be replaced by its own diminutive (Latin auricula >
# French oreille 'ear', genuculum > genou 'knee', avicellus > oiseau 'bird', soliculus > soleil 'sun', vetulus > vieux
# 'old', novellus > nouveau 'new'; Hasselrot 1957), and a verb by its frequentative or preverb form, the 'intens' affix
# (Latin canere > cantare 'sing', iacere > iactare 'throw', edere > comedere > Spanish comer 'eat'; Vaananen 1981).
# 2026-11-04 (compounds and shifts round): tools, plants and kin terms too (Latin cultellus > French couteau 'knife',
# martellus > marteau 'hammer', feniculum > fenouil 'fennel', aviolus > Spanish abuelo 'grandfather', avunculus 'uncle'
# < avus), now that compounds come only from recipes and a noun with none would otherwise fall to a fresh root.
RENEW_LITTLE = frozenset({"body", "animal", "nature", "quality", "tool", "plant", "kin"})
RENEW_INTENS = frozenset({"verb"})
RENEW_WEIGHT = 1.0
# Proto-languages grow from a root stock (PIE-style word families): a proto concept that derivations.tsv lets be built
# from another proto concept is built so with this probability by frequency class (core Swadesh items are mostly
# simple roots, rare words mostly derived), PROTO_DERIVE_DERIVED for the derived-vocabulary concepts (HUNTER, KNIFE ...)
PROTO_DERIVE = {1: 0.15, 2: 0.3, 3: 0.55, 4: 0.7, 5: 0.75}
PROTO_DERIVE_DERIVED = 0.95


# --- records ------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class EtymStep:
    kyr: float
    lect: str
    process: str   # proto | coin | sound_change:<ids> | derive:<affix> | compound:<a>+<b> | shift:<from> | borrow:<lect>
                   # | taboo | substrate:<lect> | elaborate:<niche> | analogy | nativize
    form: str      # IPA at that step
    gloss: str     # meaning at that step
    note: str = ""

    def to_list(self) -> list:
        return [self.kyr, self.lect, self.process, self.form, self.gloss, self.note]

    @classmethod
    def from_list(cls, v) -> "EtymStep":
        return cls(float(v[0]), _i(v[1]), _i(v[2]), v[3], _i(v[4]), v[5] if len(v) > 5 else "")


@dataclass(frozen=True, slots=True)
class Word:
    concept: str
    form: Form                    # tuple[Segment, ...]
    pos: str                      # N | V | A | FUNC | NAME
    freq_class: int               # 1 most frequent, slowest to replace .. 5
    etym: tuple = ()              # tuple[EtymStep, ...], oldest first (a tuple so lexicon copies share it safely)
    born_kyr: float = 0.0
    roots: tuple = ()             # root ids the word is built on, main root first: "<proto lect>:<CONCEPT>" for a proto
                                  # root, "<lect>:<CONCEPT>@<kyr>" for a later coinage (a compound has its head's and its
                                  # modifier's); kept through sound change, derivation, shift, loan and substrate

    @property
    def ipa(self) -> str:
        return word_ipa(self.form)

    def with_step(self, step: EtymStep, form: Form | None = None) -> "Word":
        return replace(self, form=self.form if form is None else form, etym=self.etym + (step,))


@dataclass(frozen=True, slots=True)
class Concept:
    id: str
    gloss: str                    # English gloss for notes
    pos: str
    freq_class: int
    domain: str                   # core | food | crop | animal | fuel | good | landscape | direction | kin | number | social
                                  # | colour | quality | god | fauna | flora
    lists: frozenset = frozenset()  # LJ100, SW100, SW200, SW207 membership (core concepts)
    clics: str | None = None      # CLICS gloss, for colexification edges
    proto: bool = True            # has a word from the start (crops, metals, straw: only once known)
    taboo: bool = False           # may be replaced by a taboo paraphrase
    local: bool = False           # kept from a substrate on language shift
    base: tuple = ()              # related concepts a new word is built from when CLICS gives none
    field: str = ""               # concepts.tsv semantic field (core concepts)


def _i(s: str) -> str:
    return sys.intern(s)


# --- the concept list ---------------------------------------------------------------------------------------------------

_VERBS = {
    "BLOW (OF WIND)", "GO", "CARRY", "GRIND", "SING", "VOMIT", "FALL", "EAT", "LAUGH", "DRINK", "BITE", "BREATHE", "HEAR",
    "SEE", "KNOW (SOMETHING)", "LIE (REST)", "PLAY", "SQUEEZE", "SIT", "KILL", "DIG", "FEAR (BE AFRAID)", "COUNT", "SUCK",
    "BE ALIVE", "FIGHT", "FREEZE", "CUT", "HIT", "STAB", "HUNT", "SCRATCH", "SPLIT", "SWIM", "SPIT",
    "FLY (MOVE THROUGH AIR)", "STAND", "WALK", "TURN AROUND", "COME", "GIVE", "HOLD", "RUB", "PUSH", "WASH", "WIPE",
    "PULL", "THROW", "SEW", "SAY", "DIE", "RUN", "SWELL", "FLOAT", "SLEEP", "SMELL (PERCEIVE)", "TAKE", "CRY", "TIE",
    "FLOW", "BURN", "STRIKE OR BEAT", "THINK", "HIDE", "DO OR MAKE", "KNOW", "RAIN (RAINING)", "BURNING",
}
_ADJS = {
    "RED", "BLACK", "LEFT", "BLUNT", "SWEET", "BITTER", "RIGHT", "GOOD", "BIG", "LONG", "HEAVY", "OLD", "DIRTY", "NEW",
    "SMOOTH", "WIDE", "THICK", "SMALL", "NARROW", "COLD", "BAD", "WHITE", "ROUND", "SHARP", "DRY", "STRAIGHT", "FAR",
    "YELLOW", "GREEN", "FULL", "SHORT", "CORRECT (RIGHT)", "WET", "ROTTEN", "HARD", "NEAR", "WARM (OF WEATHER)",
    "HOT OR WARM", "THIN", "COLD (OF WEATHER)", "FEW", "MANY",
}
_FUNC = {
    "THAT", "ALL", "HERE", "OTHER", "HE OR SHE OR IT", "THEY", "BECAUSE", "I", "HE", "WE", "YOU", "THIS", "THOU", "WHO",
    "WHAT", "WHERE", "WHEN", "HOW", "NOT", "SOME", "WITH", "IF", "IN", "AT", "AND", "THERE",
}
_TABOO_CORE = {"DIE", "KILL", "BLOOD", "SNAKE", "LOUSE", "WORM", "DEATH", "STORM", "FLOOD", "BEAR", "WOLF", "ENEMY"}
_LOCAL_FIELDS = {"Animals", "Agriculture and vegetation"}
_LOCAL_CORE = {"RIVER", "LAKE", "SEA", "MOUNTAIN", "FOREST", "SAND", "STONE", "STONE OR ROCK", "EARTH (SOIL)"}

# base hints for the core concepts CLICS links to nothing on the list (not even by a 2-family edge), so a replacement can
# still be derived or compounded instead of always coined: the usual sources of such words (left < hand, knee < leg,
# yesterday < night, eight < two-four ...)
_CORE_BASE = {
    "LEFT": ("HAND",), "UPPER LEG (THIGH)": ("LEG",), "ANT": ("FLY (INSECT)", "SMALL"), "ROAD": ("GO", "WALK"),
    "BERRY": ("FRUIT", "SEED"), "YESTERDAY": ("NIGHT",), "LAUGH": ("MOUTH", "PLAY"), "KNEE": ("LEG",),
    "SHADE": ("TREE", "SUN"), "BREATHE": ("WIND", "MOUTH"), "FEAR (BE AFRAID)": ("RUN", "COLD"),
    "TURN AROUND": ("GO", "BACK"), "NAVEL": ("BELLY",), "MALE PERSON": ("MAN",), "WARM (OF WEATHER)": ("SUN", "HOT OR WARM"),
    "ARM OR HAND": ("HAND",), "STONE OR ROCK": ("STONE", "MOUNTAIN"), "HIDE": ("BLACK", "NIGHT"), "KNOW": ("SEE", "HEAD"),
    "EIGHT": ("FOUR", "TWO"), "NINE": ("TEN", "ONE"),
}

# (id, pos, freq_class, domain, clics, proto, taboo, local, base)
_EXTRA = [
    # landscape (RIVER, LAKE, SEA, MOUNTAIN, FOREST are core)
    *[(g, "N", f, "landscape", c, True, False, True, b) for g, f, c, b in [
        ("HILL", 3, "HILL", ("MOUNTAIN",)), ("MARSH", 4, "SWAMP", ("WATER", "EARTH (SOIL)")), ("PLAIN", 4, "PLAIN", ("EARTH (SOIL)",)),
        ("COAST", 4, "COAST", ("SEA",)), ("ISLAND", 4, "ISLAND", ("SEA", "LAND")), ("SPRING (OF WATER)", 4, "SPRING (OF WATER)", ("WATER",)),
        ("FORD", 4, None, ("RIVER", "GO")), ("PASS", 4, "PASS", ("MOUNTAIN", "ROAD")), ("VALLEY", 4, "VALLEY", ("MOUNTAIN", "RIVER")),
        ("DESERT", 4, None, ("SAND", "DRY")), ("LAND", 3, "LAND", ("EARTH (SOIL)",)), ("CAVE", 4, "CAVE", ("STONE",)),
    ]],
    # directions
    *[(g, "N", 4, "direction", c, True, False, False, b) for g, c, b in [
        ("NORTH", "NORTH", ("COLD",)), ("SOUTH", "SOUTH", ("WARM (OF WEATHER)",)), ("EAST", "EAST", ("SUN",)),
        ("WEST", "WEST", ("SUN",)), ("UPSTREAM", None, ("RIVER",)), ("DOWNSTREAM", None, ("RIVER",)),
        ("SUNRISE", None, ("SUN",)), ("SUNSET", None, ("SUN",)),
    ]],
    # kin (MOTHER, FATHER, HUSBAND, WIFE are core)
    *[(g, "N", f, "kin", g, True, False, False, b) for g, f, b in [
        ("SON", 2, ("CHILD (DESCENDANT)",)), ("DAUGHTER", 2, ("CHILD (DESCENDANT)",)), ("BROTHER", 2, ("MAN",)),
        ("SISTER", 2, ("WOMAN",)), ("GRANDMOTHER", 3, ("MOTHER", "OLD")), ("GRANDFATHER", 3, ("FATHER", "OLD")),
        ("UNCLE", 3, ("FATHER",)), ("AUNT", 3, ("MOTHER",)),
    ]],
    # numbers (ONE..FIVE are core)
    *[(g, "A", 2, "number", c, True, False, False, ()) for g, c in [
        ("SIX", "SIX"), ("SEVEN", "SEVEN"), ("EIGHT", None), ("NINE", None), ("TEN", "TEN")]],
    # social
    *[(g, p, f, "social", c, True, t, False, b) for g, p, f, c, t, b in [
        ("PEOPLE", "N", 3, "PEOPLE", False, ("PERSON",)), ("REAL", "A", 3, None, False, ("GOOD",)),
        ("SPEAK", "V", 2, "SPEAK", False, ("SAY", "MOUTH")), ("MUTE", "A", 4, "MUTE", False, ("SPEAK", "NOT")),
        ("STRANGER", "N", 3, "STRANGER", False, ("PERSON", "FAR")), ("ENEMY", "N", 3, None, True, ("FIGHT", "PERSON")),
        ("FRIEND", "N", 3, "FRIEND", False, ("PERSON", "GOOD")), ("LANGUAGE", "N", 3, "LANGUAGE", False, ("TONGUE", "SPEAK")),
        ("CHIEF", "N", 3, None, False, ("HEAD", "PERSON")), ("VILLAGE", "N", 3, "VILLAGE", False, ("HOUSE",)),
        ("TOWN", "N", 4, "TOWN", False, ("VILLAGE", "BIG")), ("GOD", "N", 3, "GOD", False, ("SKY", "SPIRIT")),
        ("SPIRIT", "N", 3, "SPIRIT", False, ("BREATHE",)), ("WORD", "N", 3, "WORD", False, ("SAY",)),
    ]],
    # colours, size, tastes (RED, BLACK, WHITE, YELLOW, GREEN, BIG, SMALL, OLD, NEW, SWEET, BITTER are core)
    ("BLUE", "A", 4, "colour", "BLUE", True, False, False, ("SKY",)),
    ("BROWN", "A", 4, "colour", None, True, False, False, ("EARTH (SOIL)",)),
    ("SOUR", "A", 3, "food", "SOUR", True, False, False, ("BITTER",)),
    ("SALTY", "A", 4, "food", "SALTY", True, False, False, ("SALT",)),
    # cooking acts (GRIND is core)
    *[(g, "V", 4, "food", c, True, False, False, b) for g, c, b in [
        ("COOK", "COOK (SOMETHING)", ("FIRE",)), ("BOIL", "BOIL (SOMETHING)", ("WATER", "FIRE")),
        ("ROAST", "ROAST (SOMETHING)", ("FIRE", "BURN")), ("SMOKE (FOOD)", None, ("SMOKE (EXHAUST)",)),
        ("FERMENT", None, ("ROTTEN", "SOUR")), ("SALT (FOOD)", None, ("SALT",)),
    ]],
    # food things
    *[(g, "N", f, "food", c, pr, False, False, b) for g, f, c, pr, b in [
        ("MILK", 3, "MILK", True, ("BREAST", "DRINK")), ("FRUIT", 3, "FRUIT", True, ("TREE", "SEED")),
        ("HONEY", 4, "HONEY", True, ("SWEET",)), ("BREAD", 4, "BREAD", False, ("GRIND", "EAT")),
        ("BEER", 4, "BEER", False, ("FERMENT", "DRINK")), ("FOOD", 3, "FOOD", True, ("EAT",)),
    ]],
    # wild fauna that taboo targets
    *[(g, "N", 3, "fauna", g, True, True, True, ("ANIMAL",)) for g in ("BEAR", "WOLF", "DEER")],
    # derived vocabulary (2026-11-04): the agent, instrument, place, result and diminutive nouns the derivation table
    # builds (data/derivations.tsv), so a root has a family to grow (HUNT > HUNTER, CUT > KNIFE, SLEEP > BED, RIVER >
    # STREAM); `base` is the compound fallback ('sharp stone' for a knife, 'drink horn' for a cup)
    *[(g, "N", f, "derived", g, True, False, g in ("STREAM", "POND"), b) for g, f, b in [
        ("HUNTER", 4, ("HUNT",)), ("FIGHTER", 4, ("FIGHT",)), ("GUEST", 4, ("COME",)), ("HERDER", 4, ("HERD",)),
        ("FISHER", 4, ("FISH",)), ("SMITH", 4, ("SMITHING",)), ("ELDER", 3, ("OLD",)), ("BABY", 3, ("SMALL",)),
        ("GIRL", 3, ("SMALL",)), ("BOY", 3, ("SMALL",)), ("KNIFE", 3, ("STONE", "SHARP")), ("AXE", 4, ("STONE", "SPLIT")),
        ("NEEDLE", 4, ("BONE", "SHARP")), ("SPEAR", 4, ("STICK", "SHARP")), ("CUP", 4, ("HORN (ANATOMY)", "DRINK")),
        ("BURDEN", 4, ()), ("SEAT", 4, ("WOOD",)), ("BED", 3, ()), ("CAMP", 4, ("HOUSE",)), ("GRAVE", 4, ("EARTH (SOIL)", "DEATH")),
        ("STREAM", 4, ("RIVER", "SMALL")), ("POND", 4, ("LAKE", "SMALL")), ("PEBBLE", 4, ("STONE", "SMALL")),
        ("TWIG", 4, ("STICK", "SMALL")), ("PUPPY", 4, ("DOG", "SMALL")), ("CHICK", 4, ("BIRD", "SMALL")),
        ("SONG", 3, ()), ("DREAM", 4, ()), ("BREATH", 3, ("WIND", "MOUTH")), ("GIFT", 4, ()), ("HEAT", 4, ("FIRE",)),
    ]],
    # god domains not already in the core list
    *[(g, "N", 3, "god", c, True, t, False, b) for g, c, t, b in [
        ("FLOOD", None, True, ("WATER", "RIVER")), ("STORM", "STORM", True, ("WIND", "RAIN (PRECIPITATION)")),
        ("HERD", "HERD (SOMETHING)", False, ("ANIMAL", "MANY")), ("HARVEST", "HARVEST", False, ("CUT", "SEED")),
        ("FERTILITY", None, False, ("CHILD (YOUNG HUMAN)", "SEED")), ("HEARTH", None, False, ("FIRE", "HOUSE")),
        ("SMITHING", None, False, ("FIRE", "STRIKE OR BEAT")), ("DEATH", "DEATH", True, ("DIE",)),
        ("WAR", "WAR", False, ("FIGHT",)), ("ANCESTORS", "ANCESTORS", False, ("OLD", "FATHER")),
    ]],
]

# gods.DOMAINS -> concept (planet/lineages/gods.py: water/sky/land/life/human groups)
GOD_DOMAIN_CONCEPT = {
    "sea": "SEA", "river": "RIVER", "rain": "RAIN (PRECIPITATION)", "flood": "FLOOD", "sky": "SKY", "sun": "SUN",
    "storm": "STORM", "mountain": "MOUNTAIN", "fire": "FIRE", "forest": "FOREST", "desert": "DESERT", "herd": "HERD",
    "hunt": "HUNT", "harvest": "HARVEST", "fertility": "FERTILITY", "hearth": "HEARTH", "smithing": "SMITHING",
    "death": "DEATH", "war": "WAR", "ancestors": "ANCESTORS",
}

# crop id -> (CLICS gloss, base concepts, freq_class)
_CROP = {
    "wheat": ("WHEAT", ("SEED", "GRASS")), "pulses": ("BEAN", ("SEED",)), "foxtail_millet": (None, ("SEED", "GRASS")),
    "rice": ("RICE", ("SEED", "WATER")), "sorghum": (None, ("SEED", "GRASS")), "maize": ("MAIZE", ("SEED", "BIG")),
    "potato": ("POTATO", ("ROOT",)), "roots": (None, ("ROOT",)), "banana": (None, ("FRUIT", "TREE")),
    "rye": ("RYE", ("SEED", "GRASS")), "stonegrain": (None, ("SEED", "STONE")), "emberpod": (None, ("FRUIT", "FIRE")),
    "tree_fruit": ("FRUIT", ("FRUIT", "TREE")), "olive": (None, ("FRUIT", "FAT (ORGANIC SUBSTANCE)")),
    "vine": ("GRAPE", ("FRUIT", "ROPE")), "oil_seeds": (None, ("SEED", "FAT (ORGANIC SUBSTANCE)")),
    "coconut": (None, ("FRUIT", "TREE")), "spice_tree": (None, ("BARK", "SMELL (PERCEIVE)")),
    "chili": ("CHILI PEPPER", ("FRUIT", "BURN")), "cane": ("SUGAR CANE", ("SWEET", "GRASS")),
    "sap_sugar": ("SUGAR", ("SWEET", "TREE")), "tea": (None, ("LEAF", "DRINK")), "greens": (None, ("LEAF", "EAT")),
    "alliums": (None, ("ROOT", "BITTER")), "nightshade_fruit": (None, ("FRUIT", "RED")), "squash": ("PUMPKIN", ("FRUIT", "BIG")),
    "beans": ("BEAN", ("SEED",)), "cacao": (None, ("SEED", "BITTER")), "vanilla": (None, ("SEED", "SWEET")),
    "peanut": (None, ("SEED", "EARTH (SOIL)")), "sweet_potato": ("SWEET POTATO", ("ROOT", "SWEET")),
    "pseudograin": (None, ("SEED",)), "avocado": (None, ("FRUIT", "FAT (ORGANIC SUBSTANCE)")),
}
_ANIMAL = {
    "horse": ("HORSE", ("ANIMAL", "RUN")), "dog": ("DOG", ("ANIMAL",)), "caprine": ("GOAT", ("ANIMAL", "HORN (ANATOMY)")),
    "cattle": ("COW", ("ANIMAL", "BIG")), "fowl": ("CHICKEN", ("BIRD",)), "great_elk": ("DEER", ("DEER", "BIG")),
    "riding_lizard": ("LIZARD", ("SNAKE", "BIG")),
}
# fuels.FUELS: id -> (core concept it is the same as | None, CLICS gloss, proto, base)
_FUEL = {
    "wood": ("WOOD", None, True, ()), "charcoal": (None, "CHARCOAL", True, ("WOOD", "BLACK")),
    "dung": (None, None, True, ("ANIMAL", "DIRTY")), "peat": (None, None, True, ("EARTH (SOIL)", "BURN")),
    "straw": (None, None, False, ("GRASS", "DRY")), "grass": ("GRASS", None, True, ()),
    "drift": (None, None, True, ("WOOD", "SEA")), "coal": (None, None, True, ("STONE", "BLACK")),
    "heath": (None, None, True, ("GRASS", "MOUNTAIN")), "oil": (None, "OIL (ORGANIC SUBSTANCE)", True, ("FAT (ORGANIC SUBSTANCE)",)),
    "tallow": (None, None, True, ("FAT (ORGANIC SUBSTANCE)", "ANIMAL")), "bone": ("BONE", None, True, ()),
}
# a few land.GOODS that are things people name (the rest are land qualities)
_GOOD = {
    "salt": ("SALT", None, True, ()), "fish": ("FISH", None, True, ()), "stone": ("STONE", None, True, ()),
    "shellfish": (None, None, True, ("FISH", "STONE")), "seals": (None, None, True, ("FISH", "ANIMAL")),
    "iron": (None, "IRON", False, ("STONE", "HARD")), "copper": (None, "COPPER", False, ("STONE", "RED")),
    "gold": (None, "GOLD", False, ("STONE", "YELLOW")), "tin": (None, None, False, ("STONE", "WHITE")),
    "gems": (None, None, False, ("STONE", "STAR")), "metal": (None, None, False, ("STONE", "FIRE")),
    "timber": ("WOOD", None, True, ()),
}

ALIASES: dict[str, str] = {}
for _k, (_core, *_r) in _FUEL.items():
    if _core:
        ALIASES[f"fuel:{_k}"] = _core
for _k, (_core, *_r) in _GOOD.items():
    if _core:
        ALIASES[f"good:{_k}"] = _core
ALIASES["animal:dog"] = "DOG"


def resolve(concept: str) -> str:
    return ALIASES.get(concept, concept)


def _read_tsv(name: str) -> list[dict]:
    with open(DATA / name, newline="", encoding="utf-8") as f:
        rows = [ln for ln in f if not ln.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


@functools.cache
def _core_concepts() -> tuple[Concept, ...]:
    out = []
    for r in _read_tsv("concepts.tsv"):
        g = r["gloss"]
        lists = frozenset(x for x in r["lists"].split(",") if x)
        sc = int(r["stability_class"] or 0) or 3
        pos = "V" if g in _VERBS else "A" if g in _ADJS else "FUNC" if g in _FUNC else "N"
        local = r["semantic_field"] in _LOCAL_FIELDS or g in _LOCAL_CORE
        taboo = r["semantic_field"] == "Animals" or g in _TABOO_CORE
        dom = "god" if g in GOD_DOMAIN_CONCEPT.values() else "core"
        out.append(Concept(_i(g), g.lower(), pos, sc, dom, lists, g, True, taboo, local, _CORE_BASE.get(g, ()),
                           r["semantic_field"]))
    return tuple(out)


@functools.cache
def _all_concepts() -> tuple[Concept, ...]:
    from planet.lineages import animal_defs, crop_defs, fuels

    core = list(_core_concepts())
    have = {c.id for c in core}
    out = core[:]

    def add(c: Concept):
        if c.id not in have:
            have.add(c.id)
            out.append(c)

    if "DOG" not in have:  # the dog is on the Swadesh list; keep the alias honest if it ever drops out
        ALIASES.pop("animal:dog", None)
    for g, pos, f, dom, cl, proto, taboo, local, base in _EXTRA:
        add(Concept(_i(g), g.lower(), pos, f, dom, frozenset(), cl, proto, taboo, local, base))
    for a in crop_defs.TABLE:
        cl, base = _CROP.get(a.id, (None, ("SEED",)))
        add(Concept(_i(f"crop:{a.id}"), a.label, "N", 4, "crop", frozenset(), cl, False, False, True, base))
    for a in animal_defs.TABLE:
        cid = resolve(f"animal:{a.id}")
        cl, base = _ANIMAL.get(a.id, (None, ("ANIMAL",)))
        add(Concept(_i(cid), a.label, "N", 3, "animal", frozenset(), cl, True, True, True, base))
    for fu in fuels.FUELS:
        core_id, cl, proto, base = _FUEL.get(fu, (None, None, True, ("FIRE",)))
        if core_id is None:
            add(Concept(_i(f"fuel:{fu}"), fu, "N", 4, "fuel", frozenset(), cl, proto, False, False, base))
    for gd, (core_id, cl, proto, base) in _GOOD.items():
        if core_id is None:
            add(Concept(_i(f"good:{gd}"), gd, "N", 4, "good", frozenset(), cl, proto, False, gd in ("shellfish", "seals"), base))
    for d in GOD_DOMAIN_CONCEPT.values():
        assert d in have, d
    return tuple(out)


def concepts(run_meta: dict | None = None) -> list[Concept]:
    """The concept list: core (Leipzig-Jakarta + Swadesh, concepts.tsv), food (every crop and animal of the defs tables,
    the fuels, cooking acts, tastes), landscape, directions, kin, numbers 1-10, social words, colours, and the god
    domains. With `run_meta` (a run's meta dict), crops and animals are limited to the stocks the run has
    (`meta.crops.stocks`, `meta.animals.stocks`)."""
    allc = list(_all_concepts())
    if not run_meta:
        return allc
    keep = {}
    for dom, key in (("crop", "crops"), ("animal", "animals")):
        st = (run_meta.get(key) or {}).get("stocks")
        if st is not None:
            keep[dom] = {f"{dom}:{k}" for k in st}
    return [c for c in allc if c.domain not in keep or c.id in keep[c.domain] or c.id in ALIASES.values()]


@functools.cache
def concept_index() -> dict[str, Concept]:
    return {c.id: c for c in _all_concepts()}


def concept_info(cid: str) -> Concept:
    cid = resolve(cid)
    c = concept_index().get(cid)
    if c is not None:
        return c
    # elaborations and anything a caller invents: inherit from the part before " (" when known
    head = cid.split(" (")[0]
    h = concept_index().get(head)
    if h is not None:
        return replace(h, id=cid, gloss=cid.lower(), lists=frozenset(), clics=None, base=(head,))
    eb = _elaboration_bases().get(cid)
    if eb is not None:   # CALF, BULL, PASTURE ...: built (and later rebuilt) from the word they split from
        h = concept_index().get(eb[0])
        dom = h.domain if h is not None else "other"
        return Concept(cid, cid.lower(), "N", 4, dom, base=eb, local=bool(h is not None and h.local))
    return Concept(cid, cid.lower(), "NAME" if cid.startswith("name:") else "N", 4, "other", local=cid.startswith("name:"))


@functools.cache
def _elaboration_bases() -> dict[str, tuple[str, ...]]:
    """An elaborated concept that is not "X (...)" -> (the concept it split from, its modifier): CALF -> (cattle, SMALL)."""
    out: dict[str, tuple[str, ...]] = {}
    for splits in ELABORATIONS.values():
        for base, items in splits.items():
            for sid, mod in items:
                if " (" not in sid or concept_index().get(sid.split(" (")[0]) is None:
                    out.setdefault(sid, (resolve(base), mod))
    return out


CORE100 = frozenset(c.id for c in _core_concepts() if "SW100" in c.lists)


@functools.cache
def _clics() -> dict[str, tuple[tuple[str, int], ...]]:
    """CLICS gloss -> ((neighbour CLICS gloss, families), ...), strongest first."""
    nb: dict[str, list] = {}
    for r in _read_tsv("clics_edges.tsv"):
        a, b, f = r["concept_a"], r["concept_b"], int(r["families"])
        nb.setdefault(a, []).append((b, f))
        nb.setdefault(b, []).append((a, f))
    return {k: tuple(sorted(v, key=lambda t: (-t[1], t[0]))) for k, v in nb.items()}


@functools.cache
def _clics_to_concept() -> dict[str, str]:
    return {c.clics: c.id for c in reversed(_all_concepts()) if c.clics}


def clics_neighbours(cid: str, min_families: int = 3) -> list[tuple[str, int]]:
    """Concepts on our list that CLICS colexifies with `cid`, as (concept id, families), strongest first."""
    c = concept_info(cid)
    if not c.clics:
        return []
    m = _clics_to_concept()
    return [(m[g], f) for g, f in _clics().get(c.clics, ()) if f >= min_families and g in m and m[g] != c.id]


# --- the lexicon --------------------------------------------------------------------------------------------------------

@dataclass
class Lexicon:
    lect: str
    words: dict[str, Word] = field(default_factory=dict)
    affixes: dict[str, tuple] = field(default_factory=dict)   # meaning -> (Form, is_suffix)
    head_first: bool = False                                  # compound head order (grammar may overwrite)
    gen: float = 0.0                                          # generations stepped so far (the shift clock)
    shifted: dict[str, float] = field(default_factory=dict)  # concept -> `gen` of its last colexification shift
    notes: list = field(default_factory=list)                 # (kyr, text): affixes lost and renewed
    length_scale: float = 1.0                                 # `length_scale` of the inventory at the last step
    syllable_space: float = 0.0                               # and its `syllable_space` (0: not measured yet)
    counts: dict = field(default_factory=dict)                # replacement source -> events along the lineage
    share_cache: dict = field(default_factory=dict, repr=False, compare=False)   # affix_share's cache

    def __contains__(self, concept: str) -> bool:
        return resolve(concept) in self.words

    def __getitem__(self, concept: str) -> Word:
        return self.words[resolve(concept)]

    def __len__(self) -> int:
        return len(self.words)

    def get(self, concept: str, default=None):
        return self.words.get(resolve(concept), default)

    def set(self, word: Word) -> None:
        self.words[resolve(word.concept)] = word

    def forms(self) -> dict[str, Form]:
        """concept -> form, for the rule engine (functional load) and the driver."""
        return {k: w.form for k, w in self.words.items()}

    def homophones(self) -> dict[Form, list[str]]:
        """Forms shared by two or more concepts (colexifications and mergers), form -> concepts."""
        by: dict[Form, list[str]] = {}
        for k, w in self.words.items():
            by.setdefault(w.form, []).append(k)
        return {f: v for f, v in by.items() if len(v) > 1}

    def copy(self, lect: str | None = None) -> "Lexicon":
        """A cheap copy: Words and EtymSteps are immutable and shared."""
        return Lexicon(lect or self.lect, dict(self.words), dict(self.affixes), self.head_first, self.gen,
                       dict(self.shifted), [], self.length_scale, self.syllable_space, dict(self.counts))


def _step(kyr, lect, process, form, gloss, note="") -> EtymStep:
    return EtymStep(float(kyr), _i(lect), _i(process), word_ipa(form), _i(gloss), note)


def _nsyl(form: Form) -> int:
    return sum(1 for s in form if s.kind == "V")


def _n_syll_for(rng, freq_class: int, scale: float = 1.0) -> int:
    """Syllables for a new root: 1-3 by frequency class (frequent words shorter: Zipf's law of abbreviation), times the
    language's `length_scale`, rounded stochastically so the mean scales exactly and the frequency order is kept."""
    p = {1: (0.55, 0.40, 0.05), 2: (0.40, 0.50, 0.10), 3: (0.25, 0.55, 0.20), 4: (0.15, 0.55, 0.30),
         5: (0.10, 0.50, 0.40)}[min(5, max(1, freq_class))]
    n = int(rng.choice(3, p=p)) + 1
    if scale == 1.0:
        return n
    x = n * scale
    return max(1, int(x) + int(rng.random() < x - int(x)))


# --- word length and the syllable space ---------------------------------------------------------------------------------

def _inv_key(inv) -> tuple:
    return (tuple(inv.consonants), tuple(inv.vowels), tuple(inv.tones), tuple(sorted(inv.shapes.items())),
            inv.max_onset, inv.max_coda, inv.min_rise, inv.coda_class, inv.onset_required)


@functools.lru_cache(maxsize=8192)
def _space(key: tuple) -> float:
    cons, vows, tones, shapes, max_onset, max_coda, min_rise, coda_class, onset_required = key
    inv = _inv.Inventory(list(cons), list(vows), list(tones), dict(shapes), max_onset=max_onset, max_coda=max_coda,
                         min_rise=min_rise, coda_class=coda_class, onset_required=onset_required)
    nv = max(1, len(vows)) * max(1, len(tones))
    on = {0: 1, 1: len(cons)}
    co = {0: 1, 1: sum(1 for c in cons if inv.coda_ok((c,)))}
    if max_onset >= 2:
        on[2] = sum(1 for a in cons for b in cons if inv.onset_ok((a, b)))
    if max_coda >= 2:
        co[2] = sum(1 for a in cons for b in cons if inv.coda_ok((a, b)))
    tot = sum(w for w in dict(shapes).values() if w > 0)
    h = 0.0
    for t, w in shapes:
        if w <= 0:
            continue
        o = len(t) - len(t.lstrip("C"))
        c = len(t) - len(t.rstrip("C"))
        n = on.get(min(o, 2), 0) * nv * co.get(min(c, 2), 0)
        if n <= 0:
            continue
        q = w / tot
        h += q * (math.log(n) - math.log(q))
    return math.exp(h) if h > 0 else float(nv)


def syllable_space(inv) -> float:
    """The effective number of distinct syllables (perplexity) the inventory allows: for each syllable template of
    weight q, N = onsets x vowels (x tones) x codas legal under the phonotactics, and sigma = exp(sum q (ln N - ln q)).
    A 6 C / 5 V CV-only language: ~35; 25 C / 8 V (C)V(C): ~1100; a 40 C / 12 V complex one: ~10^5."""
    if inv is None or not getattr(inv, "consonants", None) and not getattr(inv, "vowels", None):
        return math.exp(LN_SIGMA_REF)
    return _space(_inv_key(inv))


def length_scale(inv) -> float:
    """How much longer (> 1) or shorter (< 1) words are than in a language of the reference syllable space:
    (LN_SIGMA_REF / ln sigma) ** LENGTH_EXP, clipped to LENGTH_SCALE_RANGE (see the constants)."""
    if inv is None:
        return 1.0
    ln = math.log(max(syllable_space(inv), 2.0))
    lo, hi = LENGTH_SCALE_RANGE
    return float(min(hi, max(lo, (LN_SIGMA_REF / ln) ** LENGTH_EXP)))


def limits(inv) -> tuple[int, int, int]:
    """(MAX_SYLL, MAX_SYLL_COMPOUND, MAX_SEG) scaled up by the language's `length_scale` (never below the constants)."""
    s = max(1.0, length_scale(inv))
    return round(MAX_SYLL * s), round(MAX_SYLL_COMPOUND * s), round(MAX_SEG * s)


def _draw_affixes(rng, inv) -> dict[str, tuple]:
    suffixing = rng.random() < 0.75   # suffixing preference (Greenberg; Dryer's WALS 26A: strongly suffixing most common)
    out, used = {}, set()
    for m in AFFIX_MEANINGS:
        for _ in range(20):
            f = _inv.draw_word(rng, inv, n_syll=1)
            if len(f) > 3:
                continue
            if f not in used:
                break
        used.add(f)
        out[m] = (f, suffixing if rng.random() < 0.85 else not suffixing)
    return out


def proto_lexicon(rng, inv, concepts: Iterable[Concept], kyr: float, lect_id: str,
                  head_first: bool | None = None, include_late: bool = False) -> Lexicon:
    """A proto-language's words, grown from a root stock (PIE-style word families). Each concept is either a simple
    root of 1-3 syllables (frequent concepts shorter; times `length_scale(inv)`, so a small syllable space gives longer
    roots) or, with PROTO_DERIVE[freq class] (PROTO_DERIVE_DERIVED for the derived vocabulary), built from another
    proto word along a relation of data/derivations.tsv (CARRY > BURDEN 'thing', SLEEP > BED 'place', DIE > KILL
    'cause'), up to MAX_AFFIXES deep; core Swadesh items mostly stay roots. Every word records its root
    (`Word.roots`, "<lect>:<CONCEPT>"), so the families can be listed in the proto and in its daughters. No accidental
    homophones where avoidable, and a few colexifications from strong CLICS edges (TREE/WOOD, HAND/ARM...) with one
    word for both. Concepts with `proto=False` (crops, metals, straw) are left out unless `include_late`."""
    cl = [c for c in concepts if include_late or c.proto]
    if head_first is None:
        head_first = bool(rng.random() < 0.4)
    lex = Lexicon(lect_id, {}, _draw_affixes(rng, inv), head_first)
    ids = {c.id for c in cl}
    # colexified pairs, strongest edges first; each concept in at most one pair
    pair_of: dict[str, str] = {}
    for c in cl:
        for nb, fam in clics_neighbours(c.id, COLEX_MIN_FAMILIES):
            if c.id < nb and nb in ids and c.id not in pair_of and nb not in pair_of:
                if rng.random() < min(0.6, COLEX_P_PER_FAMILY * fam):
                    pair_of[nb] = c.id   # nb takes c's word
    # which concepts are built from the root stock (a row whose base is on this proto's list)
    built: dict[str, bool] = {}
    for c in sorted(cl, key=lambda c: c.id):
        if c.id in pair_of:
            continue
        if any(r.base in ids and r.base != c.id for r in _rows_by_target().get(c.id, ())):
            p = PROTO_DERIVE_DERIVED if c.domain == "derived" else PROTO_DERIVE[min(5, max(1, c.freq_class))]
            built[c.id] = bool(rng.random() < p)
    used: set = set(a for a, _ in lex.affixes.values())
    scale, mseg = length_scale(inv), limits(inv)[2]
    lex.length_scale, lex.syllable_space = scale, syllable_space(inv)

    def root_word(c: Concept) -> Word:
        for _ in range(30):
            f = _inv.draw_word(rng, inv, n_syll=_n_syll_for(rng, c.freq_class, scale))
            if f not in used and len(f) <= mseg:
                break
        used.add(f)
        return Word(c.id, f, c.pos, c.freq_class, (_step(kyr, lect_id, "proto", f, c.gloss),), float(kyr),
                    (_i(f"{lect_id}:{c.id}"),))

    for c in sorted(cl, key=lambda c: (c.freq_class, c.id)):
        if c.id not in pair_of and not built.get(c.id):
            lex.words[c.id] = root_word(c)
    # derived words, in passes: a word waits until a base of its rows is there (bases may be derived themselves)
    todo = sorted(k for k, v in built.items() if v)
    while todo:
        left = []
        for k in todo:
            rows = [r for r in _rows_by_target().get(k, ()) if r.base in ids and r.base != k]
            if not any(r.base in lex.words for r in rows):
                if any(r.base in built and built[r.base] and r.base not in lex.words for r in rows):
                    left.append(k)   # (its base is still to be built)
                    continue
            w = None
            tried: set = set()
            for _ in range(DERIVE_TRIES):
                w = derive(rng, lex, k, inv, kyr, lect_id, exclude=tried)
                if w is None or w.form not in used:
                    break
                tried.add(resolve(w.etym[-1].note.split(" + '")[0]))
                w = None
            if w is None and any(r.base in built and built[r.base] and r.base not in lex.words for r in rows):
                left.append(k)
                continue
            if w is None:
                w = root_word(concept_info(k))
            used.add(w.form)
            lex.words[k] = w
        if len(left) == len(todo):   # (a cycle of bases still to be built: the first becomes a root)
            k = left.pop(0)
            lex.words[k] = root_word(concept_info(k))
        todo = left
    for nb in sorted(pair_of):
        src, seen = pair_of[nb], {nb}
        while src in pair_of and src not in seen:   # a chain (A <- B <- C): all three share A's word
            seen.add(src)
            src = pair_of[src]
        c, w = concept_info(nb), lex.words.get(src)
        if w is None:   # the source has no word (not on this list, or itself unresolved): give nb its own root
            lex.words[nb] = root_word(c)
            continue
        lex.words[nb] = Word(nb, w.form, c.pos, c.freq_class,
                             w.etym[:-1] + (_step(kyr, lect_id, w.etym[-1].process, w.form, c.gloss,
                                                  f"colexified with {src}"),), float(kyr), w.roots)
    return lex


# --- word-building vocabulary -------------------------------------------------------------------------------------------

_QUALITY = ("BLACK", "WHITE", "RED", "YELLOW", "GREEN", "BROWN", "BIG", "SMALL", "LONG", "OLD", "SHARP", "ROUND", "HEAVY")
COLOURS = frozenset({"BLACK", "WHITE", "RED", "YELLOW", "GREEN", "BROWN", "BLUE"})

# --- semantic classes (homophony domains, renewal classes) ---------------------------------------------------------------

_WATER_BODIES = {"RIVER", "LAKE", "SEA", "MARSH", "SPRING (OF WATER)", "FORD", "COAST"}
_PERSON_ROLES = {"PEOPLE", "STRANGER", "ENEMY", "FRIEND", "CHIEF", "PERSON", "MAN", "WOMAN", "CHILD (YOUNG HUMAN)",
                 "MALE PERSON"}
_SETTLEMENTS = {"VILLAGE", "TOWN", "HOUSE"}
_GOD_DOMAIN_CLASS = {"HERD": "animal", "HEARTH": "settlement", "STORM": "nature", "FLOOD": "water", "HARVEST": "abstract",
                     "FERTILITY": "abstract", "SMITHING": "abstract", "DEATH": "abstract", "WAR": "abstract"}
_TOOL_FIELDS = {"Basic actions and technology", "The house", "Clothing and grooming", "Warfare and hunting"}
#: the semantic class of the derived-vocabulary concepts (domain "derived")
_DERIVED_CLASS = {
    **dict.fromkeys(("HUNTER", "FIGHTER", "GUEST", "HERDER", "FISHER", "SMITH", "ELDER", "BABY", "GIRL", "BOY"), "person"),
    **dict.fromkeys(("KNIFE", "AXE", "NEEDLE", "SPEAR", "CUP", "BURDEN", "SEAT", "BED"), "tool"),
    "CAMP": "settlement", "GRAVE": "land", "PEBBLE": "land", "STREAM": "water", "POND": "water", "TWIG": "plant",
    "PUPPY": "animal", "CHICK": "animal", "SONG": "abstract", "DREAM": "abstract", "GIFT": "abstract",
    "BREATH": "nature", "HEAT": "nature",
}


@functools.cache
def sem_class(cid: str) -> str:
    """A coarse semantic class: verb | quality | colour | number | func | name | animal | plant | kin | person | god |
    water | land | settlement | food | tool | body | nature | abstract."""
    c = concept_info(cid)
    if c.pos == "V":
        return "verb"
    if c.pos in ("FUNC", "NAME"):
        return c.pos.lower()
    if c.id in COLOURS:
        return "colour"
    if c.domain == "number":
        return "number"
    if c.pos == "A":
        return "quality"
    if c.id in _DERIVED_CLASS:
        return _DERIVED_CLASS[c.id]
    d, f = c.domain, c.field
    if d in ("animal", "fauna") or f == "Animals":
        return "animal"
    if d == "crop" or f == "Agriculture and vegetation":
        return "plant"
    if c.id in _PERSON_ROLES:
        return "person"
    if d == "kin" or f == "Kinship":
        return "kin"
    if c.id in ("GOD", "SPIRIT", "ANCESTORS"):
        return "god"   # (the other god-domain concepts, SEA, HARVEST, SMITHING ..., are plain things)
    if c.id in _GOD_DOMAIN_CLASS:
        return _GOD_DOMAIN_CLASS[c.id]
    if c.id in _WATER_BODIES:
        return "water"
    if d == "landscape" or c.id in _LOCAL_CORE:
        return "land"
    if c.id in _SETTLEMENTS:
        return "settlement"
    if d == "food" or f == "Food and drink":
        return "food"
    if d in ("fuel", "good") or f in _TOOL_FIELDS:
        return "tool"
    if f == "The body":
        return "body"
    if f == "The physical world":
        return "nature"
    return "abstract"


def _domain_key(cid: str) -> str:
    """The domain used by homophony avoidance: the semantic class, verbs and qualities apart from nouns."""
    return sem_class(cid)


# --- making new words ---------------------------------------------------------------------------------------------------

def syllables(form: Form) -> int:
    """Syllables of a form (percepts.syllabify)."""
    return len(syllabify(form)) if form else 0


def clip(form: Form, n: int) -> Form:
    """The first `n` syllables of a form (as compounds clip their parts: Oxford < oxen-ford)."""
    syl = syllabify(form)
    if len(syl) <= n:
        return tuple(form)
    return tuple(s for x in syl[:max(1, n)] for s in x.segments)


def _short(lex: Lexicon, items: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """Prefer short bases: weight x 1/syllables."""
    return [(k, w / max(1, syllables(lex.words[k].form))) for k, w in items]


def _pick(rng, items: list[tuple[str, float]]) -> str:
    w = np.array([x[1] for x in items], float)
    return items[int(rng.choice(len(items), p=w / w.sum()))][0]


AFFIX_CAP = 0.08  # a derivational affix is not used again once this share of the lexicon's words carry it (a lɨ- 'thing'
# prefix on 12% of a family's words faked cognates; 0.05 -> 0.08 with the root families of the protos, 2026-11-04)


@dataclass(frozen=True, slots=True)
class DerivRow:
    relation: str     # the affix meaning (AFFIX_MEANINGS)
    base: str
    target: str
    weight: float     # typicality 1-3, plus the CLICS3 family count when the pair is also a colexification
    example: str = ""


@functools.cache
def derivation_rows() -> tuple[DerivRow, ...]:
    """data/derivations.tsv, every row whose base and target are on the concept list (the rest are skipped), each
    weighted by its typicality plus CLICS3's family count for the pair (a motivated pair is often colexified too)."""
    idx = concept_index()
    out = []
    for r in _read_tsv("derivations.tsv"):
        rel, b, t = r["relation"], resolve(r["base"]), resolve(r["target"])
        if rel not in AFFIX_MEANINGS or b not in idx or t not in idx or b == t:
            continue
        fam = max([f for n, f in clics_neighbours(t, 3) if n == b] or [0])
        out.append(DerivRow(_i(rel), _i(b), _i(t), float(r["weight"]) + fam / 10.0, r.get("example", "")))
    return tuple(out)


@functools.cache
def _rows_by_target() -> dict[str, tuple[DerivRow, ...]]:
    out: dict[str, list] = {}
    for r in derivation_rows():
        out.setdefault(r.target, []).append(r)
    return {k: tuple(v) for k, v in out.items()}


def derivation_sources(target: str) -> tuple[DerivRow, ...]:
    """The table rows that may build `target` (plus the diminutive renewal row for RENEW_LITTLE classes)."""
    t = resolve(target)
    rows = _rows_by_target().get(t, ())
    k = sem_class(t)
    if k in RENEW_LITTLE:
        rows = rows + (DerivRow("little", t, t, RENEW_WEIGHT, "diminutive renewal"),)
    elif k in RENEW_INTENS:
        rows = rows + (DerivRow("intens", t, t, RENEW_WEIGHT, "frequentative renewal"),)
    return rows


@functools.cache
def reinforcers() -> dict[str, tuple[tuple[str, float], ...]]:
    """Function word -> ((reinforcing word, weight), ...) from the 'reinforce' rows of data/derivations.tsv (THIS +
    HERE > this, NOT + ONE > not): how function words are renewed, by compounding with themselves."""
    idx = concept_index()
    out: dict[str, list] = {}
    for r in _read_tsv("derivations.tsv"):
        if r["relation"] == "reinforce" and r["base"] in idx and r["target"] in idx:
            out.setdefault(r["target"], []).append((r["base"], float(r["weight"])))
    return {k: tuple(v) for k, v in out.items()}


SELF = "SELF"   # a compound recipe's modifier: the target's own current word (generic + specific: Thai plaa-X, rein-deer)


@dataclass(frozen=True, slots=True)
class CompRow:
    target: str
    head: str        # the semantic category the target is a kind or part of ('tree SKIN' = bark)
    modifier: str    # which one; SELF = the target's own word
    weight: float    # typicality 1-3, plus CLICS3 family count / 10 for a (target, head) or (target, modifier) colexification
    example: str = ""


def _clics_fam(a: str, b: str) -> int:
    return max([f for n, f in clics_neighbours(a, 3) if n == b] or [0])


@functools.cache
def compound_rows() -> tuple[CompRow, ...]:
    """data/compounds.tsv: the attested compound recipes (target = head + modifier), every row whose concepts are on the
    list (the rest are skipped)."""
    idx = concept_index()
    out = []
    for r in _read_tsv("compounds.tsv"):
        t, h = resolve(r["target"]), resolve(r["head"])
        m = r["modifier"] if r["modifier"] == SELF else resolve(r["modifier"])
        if t not in idx or h not in idx or h == t or (m != SELF and (m not in idx or m in (t, h))):
            continue
        fam = _clics_fam(t, h) + (_clics_fam(t, m) if m != SELF else 0)
        out.append(CompRow(_i(t), _i(h), _i(m), float(r["weight"]) + fam / 10.0, r.get("example", "")))
    return tuple(out)


@functools.cache
def _comp_by_target() -> dict[str, tuple[CompRow, ...]]:
    out: dict[str, list] = {}
    for r in compound_rows():
        out.setdefault(r.target, []).append(r)
    # an elaborated concept (MILK (SOURED), CALF, PASTURE) is re-made as it was first made: ELABORATIONS is its recipe
    for splits in ELABORATIONS.values():
        for base, items in splits.items():
            for sid, mod in items:
                rows = out.setdefault(sid, [])
                row = CompRow(_i(sid), _i(resolve(base)), _i(resolve(mod)), 2.0, "elaboration (lexicon.ELABORATIONS)")
                if row not in rows:
                    rows.append(row)
    return {k: tuple(v) for k, v in out.items()}


def compound_templates(target: str) -> tuple[CompRow, ...]:
    """The compound recipes for `target` (data/compounds.tsv, and lexicon.ELABORATIONS for the elaborated concepts);
    empty: the concept is never compounded."""
    return _comp_by_target().get(resolve(target), ())


@functools.cache
def shift_paths() -> frozenset:
    """{(base, target)}: the attested cross-field shift pathways of data/derivations.tsv ('shift' rows: TREE > WOOD,
    SKY > GOD, SEE > KNOW): the target concept may take the base's word whatever the fields and CLICS counts."""
    idx = concept_index()
    return frozenset((resolve(r["base"]), resolve(r["target"])) for r in _read_tsv("derivations.tsv")
                     if r["relation"] == "shift" and resolve(r["base"]) in idx and resolve(r["target"]) in idx)


@functools.cache
def _clics_fields() -> dict[str, str]:
    out = {}
    for r in _read_tsv("clics_edges.tsv"):
        out[r["concept_a"]] = r["semantic_field_a"]
        out[r["concept_b"]] = r["semantic_field_b"]
    return out


@functools.cache
def semantic_field(cid: str) -> str:
    """The concept's semantic field: concepts.tsv's (core concepts), else CLICS3's for its gloss (the IDS/WOLD fields:
    'The body', 'Kinship', 'The physical world' ...), else ''."""
    c = concept_info(cid)
    return c.field or (_clics_fields().get(c.clics, "") if c.clics else "")


def shift_fits(base: str, target: str, families: int) -> bool:
    """May `target` take `base`'s word (a colexification edge of `families` CLICS3 families)? Along an attested pathway
    (`shift_paths`), or along an edge of >= SHIFT_MIN_FAMILIES (SHIFT_MIN_CORE when the target is core vocabulary)
    between concepts of one semantic field and one part of speech."""
    b, t = resolve(base), resolve(target)
    if (b, t) in shift_paths():
        return True
    ct, cb = concept_info(t), concept_info(b)
    core = t in CORE100 or ct.freq_class <= 2
    if families < (SHIFT_MIN_CORE if core else SHIFT_MIN_FAMILIES) or ct.pos != cb.pos:
        return False
    ft, fb = semantic_field(t), semantic_field(b)
    return bool(ft) and ft == fb


def affix_fits(meaning: str, target: str, base: str) -> bool:
    """Does the affix make sense from `base` to `target`? Only the pairs of data/derivations.tsv do (an agent noun from
    the verb it names: HUNT > HUNTER; a diminutive of a bigger thing: RIVER > STREAM; a place of an act: SLEEP > BED; an
    instrument or result: CUT > KNIFE; a quality: BLOOD > RED; a verb from a noun: SALT > SALT (FOOD); a causative: DIE >
    KILL), and the diminutive renewal of a body part, animal or natural thing by itself (SUN > SUN + 'little')."""
    t, b = resolve(target), resolve(base)
    return any(r.relation == meaning and r.base == b for r in derivation_sources(t))


def word_layers(lex: "Lexicon", w: Word, kyr: float) -> tuple[int, int]:
    """(transparent derivational affixes, transparent morphemes) of `w` at `kyr`: walking back from the latest step,
    each derivation and each compound still felt as such counts; the walk stops (the rest is one simple root) at a
    proto root, a coinage, a loan, a shift, a taboo or substrate step, a derivation or compound older than OPAQUE_KYR,
    or a derivation whose base word has since been replaced (its root is no longer the word's)."""
    aff, morph = _transparent(lex, w, kyr)
    return len(aff), morph


def _transparent(lex: "Lexicon", w: Word, kyr: float) -> tuple[list[str], int]:
    """(the transparent affix meanings, latest first; the transparent morpheme count): see `word_layers`."""
    aff, extra = [], 0
    for s in reversed(w.etym):
        p = s.process.split(":", 1)[0]
        if p == "sound_change":
            continue
        if p not in ("derive", "compound", "elaborate") or s.kyr - kyr > OPAQUE_KYR:
            break
        if p == "derive":
            if is_renewal(s) or not _intact(lex, _derive_base(s), s.kyr, w.etym[:w.etym.index(s)]):
                break   # (base gone or replaced since; or a renewal, cantare for canere, bleached at once)
            aff.append(s.process.split(":", 1)[1])
        else:
            extra += 1
    return aff, 1 + len(aff) + extra


def _derive_base(st: EtymStep) -> str | None:
    """The base concept of a derive step (its note: "<BASE> + '<affix>' ...")."""
    return resolve(st.note.split(" + '")[0]) if " + '" in st.note else None


def _intact(lex: "Lexicon", concept: str | None, since_kyr: float, chain: tuple | None = None) -> bool:
    """Is `concept`'s word the one it had at `since_kyr` (not replaced since)? With `chain` (the chain the word had then:
    a derivation's or compound's own chain up to that step), its latest word-formation step must be the chain's;
    otherwise it must be older than `since_kyr`, or a proto word (the proto builds its stock at one date)."""
    w = lex.words.get(concept) if concept else None
    if w is None:
        return False
    if chain is not None:
        a, b = _lexical_last(w), next((s for s in reversed(chain) if not s.process.startswith("sound_change:")), None)
        return a is not None and a == b
    return w.born_kyr > since_kyr + 1e-9 or w.born_kyr >= since_kyr - 1e-9 and _proto_word(w)


# --- root families: the roots a speaker still feels ---------------------------------------------------------------------

@functools.cache
def _gloss_concept() -> dict[str, str]:
    out: dict[str, str] = {}
    for c in reversed(_all_concepts()):
        out[c.gloss] = c.id
    return out


def _step_concept(st: EtymStep, fallback: str) -> str:
    """The concept id a step's gloss names (`fallback` when it is that concept's gloss)."""
    if concept_info(fallback).gloss == st.gloss and (fallback in concept_index() or concept_info(fallback).domain != "other"):
        return fallback
    return _gloss_concept().get(st.gloss) or next((k for k in _elaboration_bases() if k.lower() == st.gloss), fallback)


def _root_id(st: EtymStep, etym: tuple, concept: str) -> str:
    """The id of a root that starts at step `st` of chain `etym` (meaning `concept` there): "<lect>:<CONCEPT>" for a
    word of the proto-language (made at its date, in its lect), else "<lect>:<CONCEPT>@<kyr>". A proto colexification
    (TREE/WOOD, one word) is its source's root."""
    if st.note.startswith("colexified with "):
        concept = resolve(st.note[len("colexified with "):])
    e0 = etym[0] if etym else st
    if e0.process == "proto" and st.lect == e0.lect and st.kyr == e0.kyr:
        return _i(f"{st.lect}:{concept}")
    return _i(f"{st.lect}:{concept}@{float(st.kyr):g}")


def _compound_parts_of(st: EtymStep) -> tuple[str, str] | None:
    """(head, modifier) of a compound or elaboration step."""
    if st.process.startswith("compound:"):
        h, _, m = st.process[len("compound:"):].partition("+")
        return resolve(h), resolve(m)
    if st.process.startswith("elaborate:") and " + " in st.note:
        h, _, m = st.note.split(" (clip ")[0].partition(" + ")
        return resolve(h), resolve(m)
    return None


def felt_roots(lex: "Lexicon", w: Word, kyr: float, _depth: int = 0) -> tuple:
    """The roots a speaker still feels in `w` at `kyr`, main root first: walking back from the word's latest step, a
    transparent derivation (`word_layers`: younger than OPAQUE_KYR, its base word not replaced since) or taboo
    paraphrase ('the brown one') has its base's felt roots; a transparent compound its head's then its modifier's (a
    part replaced since is no longer felt; a generic + specific compound or a reinforced function word keeps the word's
    own); a renewal (the word's own diminutive) keeps the word's root. Anything else starts a root at that step
    (`_root_id`): a proto root or coinage, a derivation or compound older than OPAQUE_KYR (burden is no longer felt as
    bear + -th), a shift away from the old meaning, a loan, a substrate word."""
    etym = w.etym
    concept = w.concept
    i = len(etym) - 1
    while i >= 0:
        st = etym[i]
        p = st.process.split(":", 1)[0]
        if p == "sound_change":
            i -= 1
            continue
        fresh = st.kyr - kyr <= OPAQUE_KYR and _depth < 8
        if st.note.startswith("colexified with "):   # (a proto colexification: the source word's roots)
            src = resolve(st.note[len("colexified with "):])
            sw = lex.words.get(src)
            if sw is not None and src != w.concept and sw.form == w.form and _depth < 8 and _proto_word(sw) \
                    and sw.etym[0].lect == st.lect:   # (the source is still that proto word, not one shifted back since)
                return felt_roots(lex, sw, kyr, _depth + 1)
            return (_root_id(st, etym, src),)
        if p == "derive":
            if is_renewal(st):
                i -= 1
                concept = _step_concept(etym[i], concept) if i >= 0 else concept
                continue
            b = _derive_base(st)
            if fresh and b != concept and _intact(lex, b, st.kyr, etym[:i]):
                return felt_roots(lex, lex.words[b], kyr, _depth + 1)
        elif p == "taboo" and fresh and st.note.startswith("'the ") and _intact(lex, st.note[5:-5].upper(), st.kyr):
            return felt_roots(lex, lex.words[st.note[5:-5].upper()], kyr, _depth + 1)
        elif p in ("compound", "elaborate") and fresh and _compound_parts_of(st):
            h, m = _compound_parts_of(st)
            own = _step_concept(st, concept)
            out: list = []
            for part in ((m, h) if m == own else (h, m)):   # (a generic + specific renewal: the word's own root first)
                if part == own:   # (the word itself: SELF renewal or a reinforced function word)
                    out += felt_roots(lex, replace(w, etym=etym[:i]), kyr, _depth + 1) if i else []
                elif _intact(lex, part, st.kyr, etym[:i] if part == h and m != own else None):
                    out += felt_roots(lex, lex.words[part], kyr, _depth + 1)
                elif part == h:
                    out.append(_root_id(st, etym, own))   # (the head replaced since: the compound is a root of its own)
            return tuple(dict.fromkeys(out)) or (_root_id(st, etym, own),)
        return (_root_id(st, etym, _step_concept(st, concept)),)
    return (_root_id(etym[0], etym, concept),) if etym else ()


def refresh_roots(lex: "Lexicon", kyr: float) -> int:
    """Re-read every word's `roots` as felt at `kyr` (`felt_roots`); returns how many changed."""
    n = 0
    for k, w in list(lex.words.items()):
        r = felt_roots(lex, w, kyr)
        if r != w.roots:
            lex.words[k] = replace(w, roots=r)
            n += 1
    return n


def root_step(w: Word) -> EtymStep | None:
    """The step of `w`'s chain its main root id names (the root word as its lect made it), else the first step."""
    if not w.roots or not w.etym:
        return w.etym[0] if w.etym else None
    lect, _, rest = w.roots[0].partition(":")
    concept, _, k = rest.partition("@")
    gl = concept_info(concept).gloss
    for st in w.etym:
        if st.lect == lect and not st.process.startswith("sound_change:") and (not k or abs(st.kyr - float(k)) < 1e-6) \
                and (st.gloss == gl or st.note == f"colexified with {concept}"):
            return st
    return w.etym[0]


def is_renewal(st: EtymStep) -> bool:
    """Is a derive step a renewal (a word replaced by its own diminutive or frequentative: SUN + 'little' = 'sun')?"""
    return st.process.startswith("derive:") and " + '" in st.note and \
        concept_info(st.note.split(" + '")[0]).gloss == st.gloss


def affix_share(lex: Lexicon, meaning: str) -> float:
    """The share of the lexicon's words whose outermost word-formation step is the derivational affix for `meaning`
    (renewals aside): the affix a word visibly ends or starts with. Cached per (generation, size) of the lexicon: within
    one batch of replacements the share is the batch's starting one."""
    key = (lex.gen, len(lex.words))
    if lex.share_cache.get("key") != key:
        c: dict = {}
        for w in lex.words.values():
            st = _lexical_last(w)
            if st is not None and st.process.startswith("derive:") and not is_renewal(st):
                m = st.process[7:]
                c[m] = c.get(m, 0) + 1
        n = max(1, len(lex.words))
        lex.share_cache = {"key": key, **{m: v / n for m, v in c.items()}}
    return lex.share_cache.get(meaning, 0.0)


def _attach(lex: Lexicon, base: Form, meaning: str) -> Form:
    af, suf = lex.affixes.get(meaning, ((), True))
    return base + af if suf else af + base


def _carries(lex: Lexicon, w: Word, meaning: str, kyr: float | None = None) -> bool:
    """Does `w` already carry the derivational affix for `meaning` (in its history, or with `kyr` in its transparent
    part only, `word_layers`; or visibly at its edge)?"""
    p = f"derive:{meaning}"
    if kyr is None and any(s.process == p for s in w.etym) or kyr is not None and meaning in _transparent(lex, w, kyr)[0]:
        return True
    af, suf = lex.affixes.get(meaning, ((), True))
    return bool(af) and len(w.form) > len(af) and (w.form[-len(af):] == af if suf else w.form[:len(af)] == af)


def _join(lex: Lexicon, head: Form, mod: Form, head_first: bool | None) -> Form:
    hf = lex.head_first if head_first is None else head_first
    return head + mod if hf else mod + head


def _first_syllable(form: Form) -> Form:
    """The onset and first vowel (plus a following consonant when the next vowel is not adjacent)."""
    for i, s in enumerate(form):
        if s.kind == "V":
            j = i + 1
            if j < len(form) and form[j].kind == "C" and (j + 1 >= len(form) or form[j + 1].kind == "C"):
                j += 1
            return form[:j]
    return form


def _fit_base(base: Form, affix: Form, inv=None) -> tuple[Form, bool]:
    """Clip a derivation's base so base + affix keeps to the language's MAX_SYLL syllables and MAX_SEG segments
    (`limits`); the base keeps its first 1-2 syllables (more in a language with long words)."""
    ms, _, mseg = limits(inv)
    a = syllables(affix)
    room = max(1, min(round(2 * max(1.0, length_scale(inv))), ms - a))
    clipped = False
    if syllables(base) + a > ms:
        base, clipped = clip(base, room), True
    if len(base) + len(affix) > mseg and syllables(base) > 1:
        base, clipped = clip(base, 1), True
    return base, clipped


def _fit_parts(h: Form, m: Form, inv=None) -> tuple[Form, Form, bool]:
    """Clip a compound's parts (the modifier first) to their first 1-2 syllables (more in a language with long words)
    until the whole keeps to the language's MAX_SYLL_COMPOUND syllables and MAX_SEG segments (`limits`)."""
    _, msc, mseg = limits(inv)
    k = round(2 * max(1.0, length_scale(inv)))
    clipped = False
    for part, n in [(x, j) for j in range(k, 0, -1) for x in ("m", "h")]:
        if syllables(h) + syllables(m) <= msc and len(h) + len(m) <= mseg:
            break
        if part == "m" and syllables(m) > n:
            m, clipped = clip(m, n), True
        elif part == "h" and syllables(h) > n:
            h, clipped = clip(h, n), True
    return h, m, clipped


def _cap(form: Form, n_syll: int, inv) -> Form:
    """Last guard after repair: at most n_syll syllables and the language's MAX_SEG segments (`limits`)."""
    mseg = limits(inv)[2]
    if syllables(form) > n_syll or len(form) > mseg:
        f = clip(form, n_syll)
        while len(f) > mseg and syllables(f) > 1:
            f = clip(f, syllables(f) - 1)
        form = _inv.repair(f[:mseg], inv) or form[:mseg]
    return form


def derive(rng, lex: Lexicon, concept: str, inv, kyr: float, lect_id: str | None = None, base: str | None = None,
           meaning: str | None = None, exclude: Iterable[str] = (), free: bool = False,
           renew: bool | None = None) -> Word | None:
    """A new word for `concept`: a word of the lexicon plus a derivational affix, along a relation of
    data/derivations.tsv (`derivation_sources`: HUNT + 'agent' = HUNTER, RIVER + 'little' = STREAM ...), repaired to the
    phonotactics. Rows are weighted by typicality / base syllables; a base that already carries the same affix, or would
    pass MAX_AFFIXES transparent affixes or MAX_MORPHEMES morphemes (`word_layers`), or that once meant the target itself
    (no round trips, SING > SONG > SING), is refused, as is an affix on more
    than AFFIX_CAP of the lexicon; the result keeps to MAX_SYLL syllables (the base is clipped to its first 1-2
    syllables, noted 'clip'). `base` / `meaning` restrict the rows; `free=True` (elaborations: CALF = cattle + 'little')
    takes the given base and meaning without the table. `renew`: True for the renewal rows only (the word's own
    diminutive or frequentative), False for none of them. None when no row will do or the affix has worn away.
    `exclude`: bases not to use (a retry after a clash). Not stored; see `coin` / `step`."""
    c = concept_info(concept)
    lect_id = lect_id or lex.lect
    ex = set(exclude)
    if free:
        if base is None or meaning is None:
            return None
        rows = [DerivRow(meaning, resolve(base), c.id, 1.0)]
    else:
        rows = [r for r in derivation_sources(c.id) if (meaning is None or r.relation == meaning)
                and (base is None or r.base == resolve(base)) and r.base not in ex
                and (renew is None or renew == (r.base == r.target))]
    cand, share = [], {}
    for r in rows:
        af, _ = lex.affixes.get(r.relation, ((), True))
        b = lex.words.get(r.base)
        if not af or b is None or _carries(lex, b, r.relation, kyr):
            continue
        if r.base != r.target and _worn(b, c.gloss):
            continue   # no round trips: a base once worn by this meaning (SING > SONG > SING, KNIFE > CUT > KNIFE)
        if r.base != r.target:   # (a renewal keeps its root, so it fakes no cognates: no cap)
            if r.relation not in share:
                share[r.relation] = affix_share(lex, r.relation)
            if share[r.relation] + 1.0 / max(1, len(lex.words)) > AFFIX_CAP:
                continue
        aff, morph = word_layers(lex, b, kyr)
        if aff + 1 > MAX_AFFIXES or morph + 1 > MAX_MORPHEMES:
            continue
        cand.append((r, r.weight / max(1, syllables(b.form))))
    if not cand:
        return None
    w = np.array([x[1] for x in cand], float)
    row = cand[int(rng.choice(len(cand), p=w / w.sum()))][0]
    b, meaning = lex.words[row.base], row.relation
    af, _ = lex.affixes[meaning]
    bf, clipped = _fit_base(b.form, af, inv)
    form = _cap(_inv.repair(_attach(lex, bf, meaning), inv), limits(inv)[0], inv)
    note = f"{b.concept} + '{meaning}'" + (f" (clip {b.ipa} > {word_ipa(bf)})" if clipped else "")
    return Word(c.id, form, c.pos, c.freq_class,
                b.etym + (_step(kyr, lect_id, f"derive:{meaning}", form, c.gloss, note),), float(kyr), b.roots)


def _clash(a: str, b: str) -> bool:
    """Pairs a compound never joins: a verb with a colour."""
    ca, cb = sem_class(a), sem_class(b)
    return {ca, cb} == {"verb", "colour"}


def _worn(w: Word, gloss: str) -> bool:
    """Has this word meant `gloss` before (anywhere in its chain)? Such a word does not become a part of a new word for
    that meaning, nor shift back to it: no round trips (SING > SONG > SING, LEG + CLAW = FOOT > FOOT + CLAW = LEG)."""
    return any(st.gloss == gloss for st in w.etym)


def _self_renewed(w: Word, head: str, modifier: str) -> bool:
    """Has `w` been renewed by this very compound before (anywhere in its chain)? No 'deer-animal-animal', no
    'they-that-that': a generic + specific renewal or a reinforcement happens once per word."""
    p = f"compound:{head}+{modifier}"
    return any(st.process == p for st in w.etym)


def _compound_parts(rng, lex: Lexicon, c: Concept, head: str | None, modifier: str | None,
                    kyr: float = 0.0) -> tuple[str | None, str | None]:
    """(head, modifier) for a compound naming `c`: a recipe of data/compounds.tsv (`compound_templates`: SKIN + TREE =
    bark, EYE + DAY = sun, CHILD + WOMAN = girl; modifier SELF = the concept's own word, a generic + specific renewal),
    weighted by typicality over the parts' syllables; a function word is reinforced by another along the 'reinforce'
    rows of data/derivations.tsv (THIS + HERE). A recipe is refused when a part is missing, has meant the concept before
    (`_worn`, no round trips), shares the head's root or form, or (SELF) the word already is that compound. Explicit
    parts (elaborations: MILK + SOUR) are taken as given; a given head or modifier narrows the recipes."""
    if head is not None and modifier is not None:
        return resolve(head), resolve(modifier)
    if head is None and modifier is None and c.pos == "FUNC":   # a function word reinforced by another (THIS + HERE)
        rs = [(m, w) for m, w in reinforcers().get(c.id, ()) if m in lex.words and c.id in lex.words
              and not _self_renewed(lex.words[c.id], c.id, m)]   # (not 'they-that-that')
        if not rs:
            return None, None
        return c.id, _pick(rng, rs)
    cand = []
    for r in compound_templates(c.id):
        m = c.id if r.modifier == SELF else r.modifier
        if head is not None and r.head != resolve(head) or modifier is not None and m != resolve(modifier):
            continue
        hw, mw = lex.words.get(r.head), lex.words.get(m)
        if hw is None or mw is None or _worn(hw, c.gloss) or hw.form == mw.form:
            continue
        if r.modifier == SELF:
            if _self_renewed(mw, r.head, c.id):
                continue
        elif _worn(mw, c.gloss) or (hw.roots[:1] and hw.roots[:1] == mw.roots[:1]):
            continue
        cand.append(((r.head, m), r.weight / max(1, syllables(hw.form) + syllables(mw.form) - 1)))
    if not cand:
        return None, None
    w = np.array([x[1] for x in cand], float)
    return cand[int(rng.choice(len(cand), p=w / w.sum()))][0]


def compound(rng, lex: Lexicon, concept: str, inv, kyr: float, lect_id: str | None = None,
             head_first: bool | None = None, head: str | None = None, modifier: str | None = None,
             process: str | None = None, note: str | None = None) -> Word | None:
    """A new word for `concept` from two existing words, in the lexicon's head order unless `head_first` says otherwise,
    after a recipe of data/compounds.tsv (`_compound_parts`): the head is the category the concept is a kind or part of
    ('tree SKIN' = bark, 'day EYE' = sun), the modifier says which. None when no recipe fits (most concepts have none:
    they are renewed by derivation, shift, a loan or a fresh root). Parts are clipped so the compound keeps to
    MAX_SYLL_COMPOUND syllables (noted 'clip'). A generic + specific compound (modifier SELF) carries the old word's
    chain and roots (it is that word, renewed: rein-deer); any other carries the head's chain, roots head then modifier."""
    c = concept_info(concept)
    lect_id = lect_id or lex.lect
    head, modifier = _compound_parts(rng, lex, c, head, modifier, kyr)
    if head is None or modifier is None or head not in lex.words or modifier not in lex.words:
        return None
    h, m = lex.words[head], lex.words[modifier]
    if process is None and word_layers(lex, h, kyr)[1] + word_layers(lex, m, kyr)[1] > MAX_MORPHEMES:
        return None   # (a compound of two complex words is a phrase, not a word)
    hf_, mf_, clipped = _fit_parts(h.form, m.form, inv)
    form = _cap(_inv.repair(_join(lex, hf_, mf_, head_first), inv), limits(inv)[1], inv)
    proc = process or f"compound:{head}+{modifier}"
    nt = note or f"{head} + {modifier} ({m.ipa})"
    if clipped:
        nt += f" (clip {h.ipa} {m.ipa} > {word_ipa(hf_)} {word_ipa(mf_)})"
    renewal = modifier == c.id and process is None
    base, other = (m, h) if renewal else (h, m)
    return Word(c.id, form, c.pos, c.freq_class, base.etym + (_step(kyr, lect_id, proc, form, c.gloss, nt),), float(kyr),
                base.roots + tuple(r for r in other.roots if r not in base.roots))


def coin(rng, lex: Lexicon, concept: str, inv, kyr: float, lect_id: str | None = None, how: str | None = None,
         head_first: bool | None = None, store: bool = True) -> Word:
    """A word for a concept the lect has no word for (a crop arriving with no donor word, an elaboration): derive or
    compound from related words, or a fresh root when nothing is related (`how="root"`: always a fresh root, origin
    unknown). Stored unless `store=False`."""
    c = concept_info(concept)
    lect_id = lect_id or lex.lect
    w = None
    if how != "root":
        tries = [how] if how else (["derive", "compound"] if rng.random() < 0.5 else ["compound", "derive"])
        for t in tries:
            w = derive(rng, lex, c.id, inv, kyr, lect_id) if t == "derive" else compound(rng, lex, c.id, inv, kyr, lect_id,
                                                                                       head_first)
            if w is not None:
                break
    if w is None:
        n = _n_syll_for(rng, c.freq_class, length_scale(inv))   # (the current inventory: mergers lengthen coinages)
        mseg = limits(inv)[2]
        for _ in range(10):
            f = _inv.draw_word(rng, inv, n_syll=n)
            if len(f) <= mseg:
                break
        w = Word(c.id, f, c.pos, c.freq_class, (_step(kyr, lect_id, "coin", f, c.gloss),), float(kyr),
                 (_i(f"{lect_id}:{c.id}@{float(kyr):g}"),))
    if store:
        lex.set(w)
    return w


def taboo_word(rng, lex: Lexicon, concept: str, inv, kyr: float, lect_id: str | None = None) -> Word | None:
    """A taboo paraphrase: a quality plus 'one who' / 'thing' ('the brown one', 'the long thing')."""
    c = concept_info(concept)
    meaning = "agent" if c.domain in ("animal", "fauna") or c.taboo and c.pos == "N" else "thing"
    if c.pos == "V":
        meaning = "do"
    af, _ = lex.affixes.get(meaning, ((), True))
    qual = [q for q in _QUALITY if q in lex.words and not (c.pos == "V" and q in COLOURS)]
    if not qual or not af:
        return None
    q = qual[int(rng.integers(len(qual)))]
    b = lex.words[q]
    bf, _ = _fit_base(b.form, af, inv)
    form = _cap(_inv.repair(_attach(lex, bf, meaning), inv), limits(inv)[0], inv)
    return Word(c.id, form, c.pos, c.freq_class,
                b.etym + (_step(kyr, lect_id or lex.lect, "taboo", form, c.gloss, f"'the {q.lower()} one'"),), float(kyr),
                b.roots)


def _shift_root(lex: Lexicon, k: str) -> str:
    """Follow a chain of shifts back to the concept the word was first coined for (A took B's word, B took C's: C)."""
    seen = {k}
    while True:
        w = lex.words.get(k)
        last = next((s for s in reversed(w.etym) if not s.process.startswith("sound_change:")), None) if w else None
        if last is None or not last.process.startswith("shift:"):
            return k
        nxt = last.process[len("shift:"):]
        if nxt in seen or nxt not in lex.words or lex.words[nxt].form != w.form:
            return k
        seen.add(nxt)
        k = nxt


def _shift_ok(lex: Lexicon, k: str) -> bool:
    t = lex.shifted.get(k)
    return t is None or lex.gen - t >= SHIFT_GAP


def _shifted_recently(w: Word, kyr: float) -> bool:
    """Has `w` come to its meaning, or passed through one, by a shift within SHIFT_CHAIN_KYR?"""
    return any(st.process.startswith("shift:") and st.kyr - kyr <= SHIFT_CHAIN_KYR for st in w.etym)


def shift_candidates(lex: Lexicon, concept: str, kyr: float, min_families: int | None = None) -> list[tuple[str, float]]:
    """The neighbours whose word `concept` may take by a colexification shift, as (concept, weight): a CLICS3 edge that
    `shift_fits` (an attested pathway, or >= SHIFT_MIN_FAMILIES / SHIFT_MIN_CORE families inside one semantic field and
    part of speech; `min_families` raises the floor), both concepts free of a shift for SHIFT_GAP generations, a word
    not already shared by two concepts, not shifted within SHIFT_CHAIN_KYR, and never one that meant this concept
    before (no PUSH > GRIND > PUSH). Function words shift only among themselves."""
    c = concept_info(concept)
    if not _shift_ok(lex, c.id):
        return []
    edges = dict(clics_neighbours(c.id, 3))
    for b, t in shift_paths():
        if t == c.id and b not in edges:
            edges[b] = 0
    shared = set(lex.homophones()) if lex.words else set()
    out = []
    for n, f in edges.items():
        w = lex.words.get(n)
        if w is None or not _shift_ok(lex, n) or w.form in shared or _worn(w, c.gloss) or _shifted_recently(w, kyr):
            continue
        if not shift_fits(n, c.id, f) or (n, c.id) not in shift_paths() and (c.pos == "FUNC") != (w.pos == "FUNC"):
            continue
        if min_families is not None and f < min_families and (n, c.id) not in shift_paths():
            continue
        out.append((n, float(max(f, 3))))
    return out


def shift_word(rng, lex: Lexicon, concept: str, kyr: float, lect_id: str | None = None,
               min_families: int | None = None) -> Word | None:
    """Colexification shift: `concept` takes the word of a neighbour (`shift_candidates`; which keeps it too, now
    colexified, until a later replacement re-fills it). A concept takes or passes on a word this way at most once per
    SHIFT_GAP generations, and the step names the root of a shift chain (the note says through which neighbour). The
    shifted word starts a root of its own (`felt_roots`: a speaker no longer links it to the old meaning's family)."""
    c = concept_info(concept)
    nb = shift_candidates(lex, c.id, kyr, min_families)
    if not nb:
        return None
    via = _pick(rng, nb)
    src = lex.words[via]
    root = _shift_root(lex, via)
    note = "" if root == via else f"via {via}"
    lex.shifted[c.id] = lex.gen
    lex.shifted[via] = lex.gen
    st = _step(kyr, lect_id or lex.lect, f"shift:{root}", src.form, c.gloss, note)
    return Word(c.id, src.form, c.pos, c.freq_class, src.etym + (st,), float(kyr), (_root_id(st, src.etym + (st,), c.id),))


def borrow(word: Word, from_lect_id: str, to_lex: Lexicon, profile, inv, kyr: float, note: str = "",
           drop_distance: float | None = None, store: bool = True) -> Word:
    """Borrow `word` into `to_lex`: hear it through the receiver's profile and inventory (`profiles.hear_word`), repair
    it to the receiver's phonotactics, append `borrow:<lect>` to the donor's chain, store and return it."""
    from . import profiles

    if profile is None:
        profile = profiles.HUMAN
    kw = {} if drop_distance is None else {"drop_distance": drop_distance}
    heard = tuple(profiles.hear_word(word.form, profile, _inv.segments(inv), **kw))
    form = _inv.repair(heard, inv)
    if not form:
        form = _inv.repair(tuple(_inv.segments(inv)[:1]), inv) or word.form
    if len(form) > limits(inv)[2]:   # epenthesis can swell a cluster-heavy loan; long loans get clipped in use
        form = _cap(form, limits(inv)[1], inv)
        note = (note + "; " if note else "") + "clipped"
    c = concept_info(word.concept)
    st = _step(kyr, to_lex.lect, f"borrow:{from_lect_id}", form, c.gloss, note)
    w = Word(c.id, form, word.pos, c.freq_class, word.etym + (st,), float(kyr), (_root_id(st, word.etym + (st,), c.id),))
    if store:
        to_lex.set(w)
    return w


# --- elaboration --------------------------------------------------------------------------------------------------------

# niche -> concept -> [(new concept, modifier concept)]; the new word is the base word compounded with the modifier
ELABORATIONS: dict[str, dict[str, list[tuple[str, str]]]] = {
    "herder": {"MILK": [("MILK (FRESH)", "NEW"), ("MILK (SOURED)", "SOUR")],
               "animal:cattle": [("CALF", "SMALL"), ("BULL", "MAN")],
               "animal:caprine": [("KID (YOUNG GOAT)", "SMALL")],
               "HERD": [("PASTURE", "GRASS")]},
    "coast": {"FISH": [("FISH (SEA)", "SEA"), ("FISH (RIVER)", "RIVER")],
              "SEA": [("WAVE", "WIND"), ("TIDE", "MOON")]},
    "farmer": {"SEED": [("SEED (SOWN)", "EARTH (SOIL)"), ("GRAIN (RIPE)", "YELLOW")],
               "EARTH (SOIL)": [("FIELD", "SEED")]},
    "hunter": {"DEER": [("DEER (STAG)", "MAN"), ("DEER (FAWN)", "SMALL")],
               "HUNT": [("TRAP", "TIE")]},
    "mountain": {"STONE": [("CLIFF", "MOUNTAIN")], "SNOW": [("SNOW (FALLING)", "FALL"), ("SNOW (LYING)", "LIE (REST)")]},
    "cold": {"SNOW": [("SNOW (FALLING)", "FALL"), ("SNOW (LYING)", "LIE (REST)")], "ICE": [("ICE (SEA)", "SEA")]},
}

# way of life (spec.WAYS) and traits -> niche keys of ELABORATIONS
NICHE_OF = {
    "pastoral_nomad": "herder", "transhumant": "herder", "agro_pastoral": "herder", "fisher_forager": "coast",
    "sea_nomad": "coast", "coastal": "coast", "seafaring": "coast", "sea_hunter": "coast", "swims": "coast",
    "farmer": "farmer", "horticulturalist": "farmer", "agricultural": "farmer", "forager": "hunter", "hunter": "hunter",
    "mountain": "mountain", "hardy": "cold",
}


def niche_weights_from(way: str | None, traits: Iterable[str] = ()) -> dict[str, float]:
    """Niche weights from a people's way of life (1.0) and traits (0.7 each)."""
    out: dict[str, float] = {}
    if way and way in NICHE_OF:
        out[NICHE_OF[way]] = 1.0
    for t in traits:
        if t in NICHE_OF:
            out[NICHE_OF[t]] = max(out.get(NICHE_OF[t], 0.0), 0.7)
    return out


def elaborate(rng, lex: Lexicon, concept: str, how: str, inv=None, kyr: float = 0.0, lect_id: str | None = None,
              splits: list[tuple[str, str]] | None = None) -> list[Word]:
    """Split `concept` into finer concepts because the niche `how` ("herder", "coast", "farmer", "hunter", ...) makes the
    difference matter: MILK -> MILK (FRESH) / MILK (SOURED). Each new word is the base word compounded with a modifier
    (or derived with 'little' when the modifier word is missing). Returns the new words (stored)."""
    concept = resolve(concept)
    splits = splits if splits is not None else ELABORATIONS.get(how, {}).get(concept, [])
    base = lex.get(concept)
    out = []
    if base is None or inv is None:
        return out
    for new, mod in splits:
        if new in lex:
            continue
        c = concept_info(new)
        if resolve(mod) in lex.words:
            w = compound(rng, lex, new, inv, kyr, lect_id, head=concept, modifier=mod, process=f"elaborate:{how}",
                         note=f"{concept} + {resolve(mod)}")
        else:
            w = derive(rng, lex, new, inv, kyr, lect_id, base=concept, meaning="little", free=True)
        if w is None:
            continue
        w = replace(w, concept=c.id, pos=base.pos, freq_class=max(3, base.freq_class))
        lex.set(w)
        out.append(w)
    return out


# --- replacement over time ----------------------------------------------------------------------------------------------

def hazard(freq_class: int) -> float:
    """Replacement hazard per generation for a word of this frequency class."""
    return BASE_REPLACE * RATE_BY_FREQ[min(5, max(1, int(freq_class)))]


def calibrate_base_replace(classes: Iterable[int] | None = None, retention: float = SWADESH_RETENTION_1KYR,
                           gen_yr: float = GEN_YR_HUMAN, years: float = 1000.0) -> float:
    """Solve BASE so the mean over `classes` (default: the Swadesh-100) of (1 - BASE*RATE)^(years/gen_yr) = retention."""
    if classes is None:
        idx = concept_index()
        classes = [idx[c].freq_class for c in CORE100]
    cls = np.array(list(classes))
    r = np.array([RATE_BY_FREQ[c] for c in cls])
    n = years / gen_yr
    lo, hi = 0.0, 1.0 / r.max()
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if np.mean((1 - mid * r) ** n) > retention:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


#: words a worn-away derivational affix is renewed from (its first syllable); none present: a coined syllable
_AFFIX_SOURCES = {"little": ("CHILD (YOUNG HUMAN)", "SMALL"), "place": ("EARTH (SOIL)", "LAND", "HOUSE"),
                  "agent": ("PERSON", "MAN"), "thing": (), "do": ("DO OR MAKE",), "like": ("BODY",),
                  "cause": ("DO OR MAKE", "GIVE")}


def _lexical_last(w: Word) -> EtymStep | None:
    """The word's latest step that is not a sound change (how it came to mean what it means)."""
    return next((s for s in reversed(w.etym) if not s.process.startswith("sound_change:")), None)


def _proto_word(w: Word) -> bool:
    """Is `w` still the proto-language's word (made at the proto's date, root or derived, changed by sound only)?"""
    return bool(w.etym) and w.etym[0].process == "proto" and all(
        s.kyr == w.etym[0].kyr for s in w.etym if not s.process.startswith("sound_change:"))


def _deliberate(w: Word) -> bool:
    """A colexification made on purpose (a proto colexification or a shift), not an accidental merger."""
    last = _lexical_last(w)
    return last is not None and (last.process.startswith("shift:") or last.note.startswith("colexified with "))


def _renewal_boost(lex: Lexicon) -> dict[str, float]:
    """Repair by renewal: the rarer members of a homophone group of 3+, or of an accidental pair, get HOMOPHONE_BOOST
    times the replacement hazard; the rarer member of a deliberate colexification (a shift) COLEX_BOOST; a proto
    colexification both words still carry is left alone. The most frequent member keeps the form."""
    out = {}
    for _, cs in lex.homophones().items():
        b = HOMOPHONE_BOOST
        if len(cs) < 3 and any(_deliberate(lex.words[k]) for k in cs):
            if all(_proto_word(lex.words[k]) for k in cs):
                continue   # a proto colexification still in place: stable polysemy (TREE/WOOD), not a repair case
            b = COLEX_BOOST
        keep = min(cs, key=lambda k: (lex.words[k].freq_class, k))
        for k in cs:
            if k != keep:
                out[k] = b
    return out


def _clashes(lex: Lexicon, k: str, form: Form, any_domain: bool = True) -> bool:
    """Would `form` make `k` a homophone of another word (with `any_domain=False`: of a word in another domain, or join
    a group of 2+)?"""
    others = [c2 for c2, w in lex.words.items() if c2 != k and w.form == form]
    if not others:
        return False
    return any_domain or len(others) >= 2 or any(_domain_key(o) != _domain_key(k) for o in others)


def _renew_affixes(rng, lex: Lexicon, inv, n_generations: float, kyr: float) -> None:
    p = 1.0 - (1.0 - AFFIX_RENEW) ** n_generations
    for m in AFFIX_MEANINGS:
        af, suf = lex.affixes.get(m, ((), True))
        if af or rng.random() >= p:
            continue
        src = next((s for s in _AFFIX_SOURCES.get(m, ()) if s in lex.words), None)
        f = _first_syllable(lex.words[src].form) if src else ()
        if not f or len(f) > 3:
            src = None
            for _ in range(20):
                f = _inv.draw_word(rng, inv, n_syll=1)
                if len(f) <= 3:
                    break
        lex.affixes[m] = (tuple(f), suf)
        lex.notes.append((float(kyr), f"'{m}' affix renewed as {word_ipa(f)} < {src.lower() if src else 'coined'}"))


LONGER_RENEWAL = 2.0   # a homophone's replacement: derivation and compounding weights x this (lexical expansion)
BORROW_FALLBACK = 0.5  # a replacement no word-building source could make is a loan with this chance when a contact
                       # lect has the concept (else a fresh root): loans fill gaps, but not every gap
DERIVE_TRIES = 3   # a derivation that clashes (homophone) or finds no base is retried this often with another base or affix


def _derive_tries(rng, lex: Lexicon, k: str, c: Concept, inv, kyr: float, lect_id: str, renew: bool = False) -> Word | None:
    """Up to DERIVE_TRIES derivations for `k` that do not make a homophone, each with a base not tried before (`renew`:
    the renewal rows instead of the table's)."""
    tried: set = set()
    for _ in range(DERIVE_TRIES):
        new = derive(rng, lex, k, inv, kyr, lect_id, exclude=tried, renew=renew)
        if new is None:
            return None
        if not _clashes(lex, k, new.form):
            return new
        tried.add(resolve(new.etym[-1].note.split(" + '")[0]))   # the base, as `derive` notes it
    return None


def _replace_word(rng, lex: Lexicon, k: str, c: Concept, src: str, opts: dict, inv, kyr: float, lect_id: str,
                  head_first, have: list, contact_words, profile) -> tuple[str, Word]:
    """The replacement for `k` from the drawn source, falling back to the next plausible one in the order derive
    (DERIVE_TRIES bases), compound, colexification shift, a loan from a contact lect, and only then a fresh root: a
    derivation the table has no fitting row for, or that would make a homophone, is not by itself a reason to coin.
    Returns (process actually used, word)."""
    order = [src] + [x for x in ("derive", "compound", "shift", "renew") if x in opts and x != src]
    order += (["borrow"] if have and "borrow" not in order and rng.random() < BORROW_FALLBACK else []) + ["coin"]
    for s in order:
        new = None
        if s == "borrow":
            if have:
                d = have[int(rng.integers(len(have)))]
                return s, borrow(contact_words[d][k], d, lex, profile, inv, kyr, "contact", store=False)
        elif s in ("derive", "renew"):
            new = _derive_tries(rng, lex, k, c, inv, kyr, lect_id, renew=s == "renew")
        elif s == "compound":
            for _ in range(2):
                new = compound(rng, lex, k, inv, kyr, lect_id, head_first)
                if new is None or not _clashes(lex, k, new.form):
                    break
            else:
                new = None
        elif s == "taboo":
            for _ in range(2):
                new = taboo_word(rng, lex, k, inv, kyr, lect_id)
                if new is None or not _clashes(lex, k, new.form):
                    break
            else:
                new = None
        elif s == "shift":
            new = shift_word(rng, lex, k, kyr, lect_id)
        else:
            for _ in range(3):
                new = coin(rng, lex, k, inv, kyr, lect_id, how="root", store=False)
                if not _clashes(lex, k, new.form):
                    break
        if new is not None:
            return s, new
    raise AssertionError("coin always returns a word")


def step(rng, lex: Lexicon, n_generations: float, inv, contact_words: dict[str, Lexicon] | None = None,
         kyr: float = 0.0, lect_id: str | None = None, niche_weights: dict[str, float] | None = None,
         profile=None, head_first: bool | None = None) -> list[tuple[str, str]]:
    """Lexical events over `n_generations` (fractional is fine) in one batch: each word is replaced with probability
    1 - (1 - h)^n, h = BASE_REPLACE * RATE_BY_FREQ[freq_class] (x HOMOPHONE_BOOST for the rarer members of a homophone
    group, `_renewal_boost`), the new word coming from SOURCES: a derivation, a compound (data/compounds.tsv recipes only), a colexification
    shift, a fresh root, a loan (only if a contact lexicon has the concept) or a taboo paraphrase (animals and dangerous
    things only); an unusable compound or taboo source adds its weight to derivation, an unavailable loan or shift is
    dropped and the rest renormalised. A source that fails or would make a homophone falls back (`_replace_word`):
    derivation with another base or affix, compound, shift, and a fresh root only last. Then affix renewal and elaboration by niche. Mutates `lex`; returns
    [(concept, process)] for the events."""
    lect_id = lect_id or lex.lect
    events: list[tuple[str, str]] = []
    if n_generations > 0:
        lex.gen += float(n_generations)
    scale = length_scale(inv) if inv is not None else lex.length_scale
    if inv is not None:
        lex.length_scale, lex.syllable_space = scale, syllable_space(inv)
    if n_generations > 0 and lex.words:
        keys = list(lex.words)
        boost = _renewal_boost(lex)
        h = np.array([min(1.0, hazard(lex.words[k].freq_class) * boost.get(k, 1.0)) for k in keys])
        p = 1.0 - (1.0 - h) ** n_generations
        hit = np.nonzero(rng.random(len(keys)) < p)[0]
        donors = sorted(contact_words) if contact_words else []
        for i in hit:
            k = keys[int(i)]
            if k not in lex.words:
                continue
            c = concept_info(k)
            have = [d for d in donors if k in contact_words[d]]
            opts = dict(SOURCES)
            if not have:
                opts.pop("borrow")
            # a word-building source the concept cannot use (taboo for a harmless thing, compounding for a verb or
            # quality) hands its weight to derivation, the way verbs and qualities are mostly renewed; only borrowing
            # and shift are renormalised away, so a fresh root stays near its intended share
            if not c.taboo:
                opts["derive"] += opts.pop("taboo")
            if sem_class(k) not in RENEW_LITTLE | RENEW_INTENS:
                opts["derive"] += opts.pop("renew")
            if not compound_templates(k) and not (c.pos == "FUNC" and c.id in reinforcers()):
                opts["derive"] += opts.pop("compound")   # (only concepts with a recipe compound, data/compounds.tsv)
            if not shift_candidates(lex, k, kyr):
                opts.pop("shift")
            # word length follows the syllable space over time too (Nettle 1998: mergers make homophones, and
            # speakers answer with longer words, aujourd'hui < hui, Chinese disyllabic compounds): a lect whose
            # inventory has shrunk (length_scale > 1) builds more words and shifts fewer short ones, and a homophone
            # being renewed favours a built (longer) word by LONGER_RENEWAL; coinages are lengthened in `coin` (a
            # large syllable space only shortens coinages: fewer built words would just mean more fresh roots)
            up = max(1.0, scale)
            lw = up * (LONGER_RENEWAL if k in boost else 1.0)
            for x in ("derive", "compound", "renew"):
                if x in opts:
                    opts[x] *= lw
            if "shift" in opts:
                opts["shift"] /= up
            names = list(opts)
            w = np.array([opts[s] for s in names])
            src = names[int(rng.choice(len(names), p=w / w.sum()))]
            src, new = _replace_word(rng, lex, k, c, src, opts, inv, kyr, lect_id, head_first, have, contact_words,
                                     profile)
            lex.set(new)
            lex.counts[src] = lex.counts.get(src, 0) + 1
            events.append((k, src))
    if inv is not None and n_generations > 0:
        _renew_affixes(rng, lex, inv, n_generations, kyr)
    if niche_weights and inv is not None:
        for niche, wt in sorted(niche_weights.items()):
            if wt < ELAB_THRESHOLD:
                continue
            pe = 1.0 - (1.0 - min(1.0, ELAB_RATE * wt)) ** n_generations
            for base, splits in ELABORATIONS.get(niche, {}).items():
                if resolve(base) in lex.words and any(s not in lex for s, _ in splits) and rng.random() < pe:
                    for w in elaborate(rng, lex, base, niche, inv, kyr, lect_id):
                        events.append((w.concept, f"elaborate:{niche}"))
    if n_generations > 0:
        refresh_roots(lex, kyr)   # (derivations and compounds turn opaque, bases are replaced: the families a speaker feels)
    return events


# --- substrate and sound change -----------------------------------------------------------------------------------------

def local_concepts(lex: Lexicon) -> list[str]:
    """The concepts a shifting population keeps from its old lect: landscape, local plants and animals, names."""
    return [k for k in lex.words if concept_info(k).local or lex.words[k].pos == "NAME"]


def substrate_transfer(old_lex: Lexicon, new_lex: Lexicon, local_concepts: Iterable[str] | None = None,
                       kyr: float = 0.0, inv=None, profile=None) -> list[str]:
    """After a shift from `old_lex` to `new_lex`, keep the old words for the local concepts (default
    `local_concepts(old_lex)`), each with a `substrate:<old lect>` step. With `inv` (and `profile`) the kept words are
    heard through the new lect's inventory and repaired. Returns the concepts kept."""
    from . import profiles

    keep = list(local_concepts) if local_concepts is not None else globals()["local_concepts"](old_lex)
    out = []
    for k in keep:
        w = old_lex.get(k)
        if w is None:
            continue
        form = w.form
        if inv is not None:
            heard = tuple(profiles.hear_word(form, profile or profiles.HUMAN, _inv.segments(inv)))
            form = _inv.repair(heard, inv) or form
        c = concept_info(k)
        st = _step(kyr, new_lex.lect, f"substrate:{old_lex.lect}", form, c.gloss)
        new_lex.set(Word(c.id, form, w.pos, w.freq_class, w.etym + (st,), float(kyr), (_root_id(st, w.etym + (st,), c.id),)))
        out.append(c.id)
    return out


MAX_SOUND_RUN = 4   # at most this many sound-change steps in a row; past it the last step absorbs the newer changes


def _merge_ids(ids: str, rule_id: str) -> str:
    parts = ids.split("+")
    more = 0
    if parts[-1].startswith("…"):
        more = int(parts.pop()[1:])
    if len(parts) < 4:
        parts.append(rule_id)
    else:
        more += 1
    return "+".join(parts + ([f"…{more}"] if more else []))


def minimal_form(old: Form) -> Form:
    """What is left of a word a sound change would delete whole: its last vowel (the nucleus that held out), else its last
    segment. Words do not vanish; they wear down to a minimal form."""
    v = [s for s in old if s.kind == "V"]
    return (v[-1],) if v else tuple(old[-1:])


def _sound_step(w: Word, form: Form, rule_id: str, kyr: float, lect_id: str, note: str = "") -> Word:
    """Append a sound-change step, or fold it into the last step when that is a sound change of the same interval (same
    kyr, same lect) or ends a run of MAX_SOUND_RUN sound changes (then the last step takes the new kyr and form)."""
    last = w.etym[-1] if w.etym else None
    if last is not None and last.process.startswith("sound_change:") and last.lect == lect_id:
        run = 0
        for st in reversed(w.etym):
            if not st.process.startswith("sound_change:"):
                break
            run += 1
        if last.kyr == kyr or run >= MAX_SOUND_RUN:
            ids = _merge_ids(last.process[len("sound_change:"):], rule_id)
            merged = EtymStep(min(last.kyr, float(kyr)), last.lect, _i(f"sound_change:{ids}"), word_ipa(form), last.gloss,
                              note or last.note)
            return replace(w, form=form, etym=w.etym[:-1] + (merged,))
    return w.with_step(_step(kyr, lect_id, f"sound_change:{rule_id}", form, concept_info(w.concept).gloss, note), form)


def apply_rule_to_lexicon(lex: Lexicon, rule_apply_fn: Callable[[Form], Form], rule_id: str, kyr: float,
                          lect_id: str | None = None) -> int:
    """Run a sound change (`rule_apply_fn(form) -> form`) over every word and the derivational affixes. Only words that
    changed get a `sound_change:<id>` step; successive changes at the same kyr in the same lect collapse into one step
    (ids joined by '+', '+…n' past four), and so does anything past a run of MAX_SOUND_RUN sound-change steps. Returns
    the number of words changed. A word the rule would delete whole keeps a minimal form (`minimal_form`, noted 'kept
    minimal'); a derivational affix worn to nothing is lost (an empty entry, noted in `lex.notes`) until `step` renews
    it."""
    lect_id = lect_id or lex.lect
    n = 0
    cache: dict[Form, Form] = {}
    for k, w in list(lex.words.items()):
        f = cache.get(w.form)
        if f is None:
            f = cache[w.form] = tuple(rule_apply_fn(w.form))
        note = ""
        if not f and w.form:
            f, note = minimal_form(w.form), "kept minimal"
        if f != w.form:
            lex.words[k] = _sound_step(w, f, rule_id, kyr, lect_id, note)
            n += 1
    for m, (af, suf) in list(lex.affixes.items()):
        if not af:
            continue
        f = tuple(rule_apply_fn(af))
        if not f:
            lex.notes.append((float(kyr), f"'{m}' affix {word_ipa(af)} worn to nothing by {rule_id}"))
        lex.affixes[m] = (f, suf)
    return n


def stats(lex: Lexicon) -> dict:
    """Diagnostics: mean and max segments and syllables per word (all words, and the Swadesh-100 core), the
    syllable space and length scale last measured on the lect's inventory, the share of concepts in homophone groups, counts
    per etymology process (every step of every chain, and the latest non-sound-change step of each word), and
    `inherited_core_share`: the share of the Swadesh-100 words that are still the proto word (`inherited`)."""
    import collections

    words = list(lex.words.values())
    if not words:
        return {"words": 0, "mean_segments": 0.0, "max_segments": 0, "mean_syllables": 0.0, "replacements": {},
                "roots": 0, "root_family_max": 0, "words_in_families": 0.0,
                "core_mean_syllables": 0.0, "core_mean_segments": 0.0, "syllable_space": float(lex.syllable_space),
                "length_scale": float(lex.length_scale), "homophone_share": 0.0,
                "processes": {}, "latest": {}, "inherited_core_share": 0.0}
    lens = [len(w.form) for w in words]
    hom = sum(len(v) for v in lex.homophones().values())
    procs = collections.Counter(s.process.split(":")[0] for w in words for s in w.etym)
    latest = collections.Counter(
        next((s.process.split(":")[0] for s in reversed(w.etym) if not s.process.startswith("sound_change:")), "?")
        for w in words)
    core = [w for k, w in lex.words.items() if k in CORE100]
    fam = collections.Counter(w.roots[0] for w in words if w.roots)
    return {"words": len(words), "mean_segments": float(np.mean(lens)), "max_segments": int(max(lens)),
            "replacements": dict(lex.counts),
            "roots": len(fam), "root_family_max": max(fam.values()) if fam else 0,
            "words_in_families": sum(v for v in fam.values() if v > 1) / len(words),
            "mean_syllables": float(np.mean([syllables(w.form) for w in words])),
            "core_mean_syllables": float(np.mean([syllables(w.form) for w in core])) if core else 0.0,
            "core_mean_segments": float(np.mean([len(w.form) for w in core])) if core else 0.0,
            "syllable_space": float(lex.syllable_space), "length_scale": float(lex.length_scale),
            "homophone_share": hom / len(words), "processes": dict(procs), "latest": dict(latest),
            "inherited_core_share": (sum(map(inherited, core)) / len(core)) if core else 0.0}


_REPLACING = ("coin", "derive", "compound", "shift", "borrow", "taboo", "substrate", "elaborate")


def inherited(w: Word) -> bool:
    """Is `w` its concept's proto word, carried down by sound change alone (made at the proto's date for this very
    concept, as a root or a derivation from one, and no step since replaced it: no coinage, derivation, compound,
    shift, loan, taboo or substrate)?"""
    if not w.etym or not _proto_word(w):
        return False
    last = _lexical_last(w)   # (a proto root, or a proto derivation from one: either is the proto's word for it)
    return last is not None and last.gloss == concept_info(w.concept).gloss


# --- json ---------------------------------------------------------------------------------------------------------------

def to_json(lex: Lexicon, full: bool = True) -> dict:
    """{"lect", "head_first", "affixes": {meaning: {ipa, suffix}}, "words": {concept: {ipa, pos, freq, born_kyr,
    etym: [[kyr, lect, process, form, gloss, note], ...]}}}. Not full: the Swadesh-100 and names only."""
    words = {}
    for k, w in lex.words.items():
        if not full and k not in CORE100 and w.pos != "NAME":
            continue
        words[k] = {"ipa": w.ipa, "pos": w.pos, "freq": w.freq_class, "born_kyr": w.born_kyr,
                    "etym": [s.to_list() for s in w.etym], "roots": list(w.roots)}
    return {"lect": lex.lect, "head_first": lex.head_first, "gen": lex.gen, "shifted": dict(lex.shifted),
            "length_scale": lex.length_scale, "syllable_space": lex.syllable_space,
            "notes": [list(x) for x in lex.notes], "counts": dict(lex.counts),
            "affixes": {m: {"ipa": word_ipa(f), "suffix": s} for m, (f, s) in lex.affixes.items()},
            "words": words}


def from_json(d: dict) -> Lexicon:
    lex = Lexicon(d["lect"], {}, {}, bool(d.get("head_first", False)), float(d.get("gen", 0.0)),
                  {_i(k): float(v) for k, v in d.get("shifted", {}).items()}, [tuple(x) for x in d.get("notes", [])],
                  float(d.get("length_scale", 1.0)), float(d.get("syllable_space", 0.0)), dict(d.get("counts", {})))
    for m, a in d.get("affixes", {}).items():
        lex.affixes[m] = (tuple(from_ipa(a["ipa"])) if a["ipa"] else (), bool(a["suffix"]))
    for k, v in d["words"].items():
        lex.words[_i(k)] = Word(_i(k), tuple(from_ipa(v["ipa"])), v["pos"], int(v["freq"]),
                                tuple(EtymStep.from_list(s) for s in v["etym"]), float(v["born_kyr"]),
                                tuple(_i(r) for r in v.get("roots", ())))
    return lex
