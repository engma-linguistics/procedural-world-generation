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
# Hazard per generation = BASE_REPLACE * RATE_BY_FREQ[freq_class]. RATE_BY_FREQ is geometric, class 5 (rare, fast) ten
# times class 1 (frequent, slow), the spread of Pagel 2007's per-word rates. BASE_REPLACE is solved so the Swadesh-100
# (with the class mix concepts.tsv gives it: 31/31/13/16/9) keeps 86% of its words per 1000 yr at 27.7-yr generations
# (`calibrate_base_replace`, checked by tests/test_language_lexicon.py).
RATE_BY_FREQ = {1: 1.0, 2: 10 ** 0.25, 3: 10 ** 0.5, 4: 10 ** 0.75, 5: 10.0}
SWADESH_RETENTION_1KYR = 0.86
BASE_REPLACE = 0.001437   # per generation; re-solve with calibrate_base_replace() if the table or RATE_BY_FREQ change

# Where a replacement comes from. A fresh root ("coin", origin unknown) keeps a real share: in attested histories a good
# part of the basic vocabulary has no known etymology, and without it every new word is built from old ones and words
# only grow. Only nouns compound (for the rest the compound share goes to the rest); borrow needs a contact lect, taboo a taboo
# concept, shift a CLICS neighbour with a word.
SOURCES = {"derive": 0.35, "compound": 0.20, "shift": 0.15, "coin": 0.15, "borrow": 0.10, "taboo": 0.05}
COLEX_MIN_FAMILIES = 12       # proto colexifications only from CLICS edges seen in at least this many families
COLEX_P_PER_FAMILY = 0.008    # chance a proto-lexicon colexifies an edge, per family attesting it (TREE/WOOD 59 -> 0.47)
MAX_SYLL = 3                  # a derived word has at most this many syllables (the base is clipped to fit)
MAX_SYLL_COMPOUND = 4         # a compound has at most this many (its parts are clipped to their first 1-2 syllables)
MAX_SEG = 12                  # and no new word is longer than this many segments
BUILD_MIN_FAMILIES = 5        # CLICS edges a new word is built or shifted along (3-4 families is mostly chance)
SHIFT_GAP = 50.0              # generations: a concept takes or passes on a word by colexification shift at most this often
HOMOPHONE_BOOST = 4.0         # replacement hazard x this for the rarer members of a homophone group of 3+ or of an
                              # accidental pair (repair by renewal)
COLEX_BOOST = 4.0             # and x this for the rarer member of a deliberate pair (a shift; a proto pair: x1)
AFFIX_RENEW = 0.01            # per generation: a derivational affix worn to nothing is renewed from a word (or coined)
ELAB_THRESHOLD = 0.5          # niche weight above which a concept starts to split
ELAB_RATE = 0.02              # per generation, times the niche weight, once past the threshold
AFFIX_MEANINGS = ("little", "place", "agent", "thing", "do", "like")  # derivational morphemes, one form each per lexicon


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
                       dict(self.shifted), [])


def _step(kyr, lect, process, form, gloss, note="") -> EtymStep:
    return EtymStep(float(kyr), _i(lect), _i(process), word_ipa(form), _i(gloss), note)


def _nsyl(form: Form) -> int:
    return sum(1 for s in form if s.kind == "V")


def _n_syll_for(rng, freq_class: int) -> int:
    p = {1: (0.55, 0.40, 0.05), 2: (0.40, 0.50, 0.10), 3: (0.25, 0.55, 0.20), 4: (0.15, 0.55, 0.30),
         5: (0.10, 0.50, 0.40)}[min(5, max(1, freq_class))]
    return int(rng.choice(3, p=p)) + 1


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
    """A proto-language's words: one monomorphemic root of 1-3 syllables per concept (frequent concepts shorter), no
    accidental homophones where avoidable, and a few colexifications from strong CLICS edges (TREE/WOOD, HAND/ARM...)
    with one word for both. Concepts with `proto=False` (crops, metals, straw) are left out unless `include_late`."""
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
    used: set = set(a for a, _ in lex.affixes.values())
    for c in sorted(cl, key=lambda c: (c.freq_class, c.id)):
        if c.id in pair_of:
            continue
        for _ in range(30):
            f = _inv.draw_word(rng, inv, n_syll=_n_syll_for(rng, c.freq_class))
            if f not in used and len(f) <= MAX_SEG:
                break
        used.add(f)
        lex.words[c.id] = Word(c.id, f, c.pos, c.freq_class, (_step(kyr, lect_id, "proto", f, c.gloss),), float(kyr))
    for nb in sorted(pair_of):
        src, seen = pair_of[nb], {nb}
        while src in pair_of and src not in seen:   # a chain (A <- B <- C): all three share A's word
            seen.add(src)
            src = pair_of[src]
        c, w = concept_info(nb), lex.words.get(src)
        if w is None:   # the source has no word (not on this list, or itself unresolved): give nb its own root
            f = _inv.draw_word(rng, inv, n_syll=_n_syll_for(rng, c.freq_class))
            lex.words[nb] = Word(nb, f, c.pos, c.freq_class, (_step(kyr, lect_id, "proto", f, c.gloss),), float(kyr))
            continue
        lex.words[nb] = Word(nb, w.form, c.pos, c.freq_class,
                             (_step(kyr, lect_id, "proto", w.form, c.gloss, f"colexified with {src}"),), float(kyr))
    return lex


# --- word-building vocabulary -------------------------------------------------------------------------------------------

_QUALITY = ("BLACK", "WHITE", "RED", "YELLOW", "GREEN", "BROWN", "BIG", "SMALL", "LONG", "OLD", "SHARP", "ROUND", "HEAVY")
COLOURS = frozenset({"BLACK", "WHITE", "RED", "YELLOW", "GREEN", "BROWN", "BLUE"})

# --- semantic classes: what a compound may be built from -----------------------------------------------------------------

_WATER_BODIES = {"RIVER", "LAKE", "SEA", "MARSH", "SPRING (OF WATER)", "FORD", "COAST"}
_PERSON_ROLES = {"PEOPLE", "STRANGER", "ENEMY", "FRIEND", "CHIEF", "PERSON", "MAN", "WOMAN", "CHILD (YOUNG HUMAN)",
                 "MALE PERSON"}
_SETTLEMENTS = {"VILLAGE", "TOWN", "HOUSE"}
_GOD_DOMAIN_CLASS = {"HERD": "animal", "HEARTH": "settlement", "STORM": "nature", "FLOOD": "water", "HARVEST": "abstract",
                     "FERTILITY": "abstract", "SMITHING": "abstract", "DEATH": "abstract", "WAR": "abstract"}
_TOOL_FIELDS = {"Basic actions and technology", "The house", "Clothing and grooming", "Warfare and hunting"}
#: semantic plausibility: a compound for a concept of this class takes its head from this class word ("river" for a water
#: body, "person" for a kin term or a role, "animal" for an animal ...), the modifier saying which kind
COMPOUND_HEADS = {
    "water": ("RIVER", "WATER"), "land": ("LAND", "EARTH (SOIL)"), "animal": ("ANIMAL",),
    "plant": ("TREE", "GRASS"), "kin": ("PERSON",),
    "person": ("PERSON", "MAN"), "food": ("FOOD",), "god": ("SPIRIT", "GOD"), "settlement": ("HOUSE", "VILLAGE"),
}
_FEMALE_KIN = {"MOTHER", "WIFE", "DAUGHTER", "SISTER", "GRANDMOTHER", "AUNT", "WOMAN"}
_MALE_KIN = {"FATHER", "HUSBAND", "SON", "BROTHER", "GRANDFATHER", "UNCLE", "MAN", "MALE PERSON"}
#: classes whose compounds may take a plain quality modifier ('black-bird', 'big-river'); never kin, verbs, gods, abstracts
CONCRETE = frozenset({"animal", "plant", "water", "land", "food", "tool", "nature", "body"})


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


@functools.cache
def _class_members() -> dict[str, tuple[str, ...]]:
    out: dict[str, list[str]] = {}
    for c in _all_concepts():
        out.setdefault(sem_class(c.id), []).append(c.id)
    return {k: tuple(v) for k, v in out.items()}


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


def _related(lex: Lexicon, cid: str, exclude=()) -> list[tuple[str, float]]:
    """Words a new word for `cid` can be built from: CLICS neighbours, then the concept's base hints, weighted."""
    ex = {cid, *exclude}
    out = [(n, float(f)) for n, f in clics_neighbours(cid, BUILD_MIN_FAMILIES) if n in lex.words and n not in ex
           and lex.words[n].pos != "FUNC"]
    for b in concept_info(cid).base:
        b = resolve(b)
        if b in lex.words and b not in ex and all(b != n for n, _ in out):
            out.append((b, 10.0))
    return out


def _short(lex: Lexicon, items: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """Prefer short bases: weight x 1/syllables."""
    return [(k, w / max(1, syllables(lex.words[k].form))) for k, w in items]


def _pick(rng, items: list[tuple[str, float]]) -> str:
    w = np.array([x[1] for x in items], float)
    return items[int(rng.choice(len(items), p=w / w.sum()))][0]


AFFIX_CAP = 0.05  # a derivational affix is not used again once this share of the lexicon's words carry it (a lɨ- 'thing'
# prefix on 12% of a family's words faked cognates)
_SMALL = frozenset({"animal", "plant", "food", "tool", "body", "nature"})
_PLACE = frozenset({"land", "water", "settlement"})


def affix_fits(meaning: str, target: str, base: str) -> bool:
    """Does the affix make sense from `base` to `target`? 'one who' only for persons or animals from verbs; 'place of' for
    places from nouns or verbs; 'little' for small things from a noun; 'thing' only from a verb to its object or result;
    'do' for verbs, 'like' for qualities."""
    ct, cb = concept_info(target), concept_info(base)
    kt = sem_class(target)
    if meaning == "do":
        return ct.pos == "V"
    if meaning == "like":
        return ct.pos == "A"
    if ct.pos != "N":
        return False
    if meaning == "agent":
        return kt in ("person", "kin", "god", "animal") and cb.pos == "V"
    if meaning == "place":
        return (kt in _PLACE or ct.domain in ("landscape", "direction")) and cb.pos in ("N", "V")
    if meaning == "little":
        return cb.pos == "N" and (kt in _SMALL or kt == sem_class(base))
    if meaning == "thing":
        return cb.pos == "V" and kt not in ("person", "kin", "god", "animal", "plant", "land", "water", "nature")
    return False


def affix_share(lex: Lexicon, meaning: str) -> float:
    """The share of the lexicon's words whose history carries the derivational affix for `meaning`."""
    p = f"derive:{meaning}"
    n = len(lex.words)
    return sum(1 for w in lex.words.values() if any(st.process == p for st in w.etym)) / n if n else 0.0


def _affix_meaning(c: Concept) -> str:
    if c.pos == "V":
        return "do"
    if c.pos == "A":
        return "like"
    if c.domain in ("landscape", "direction"):
        return "place"
    if c.domain in ("social", "kin", "god") and c.id not in ("HEARTH", "FLOOD", "STORM"):
        return "agent"
    if c.domain in ("animal", "fauna") or c.id.startswith("crop:"):
        return "little"
    return "thing"


def _attach(lex: Lexicon, base: Form, meaning: str) -> Form:
    af, suf = lex.affixes.get(meaning, ((), True))
    return base + af if suf else af + base


def _carries(lex: Lexicon, w: Word, meaning: str) -> bool:
    """Does `w` already carry the derivational affix for `meaning` (in its history, or visibly at its edge)?"""
    p = f"derive:{meaning}"
    if any(s.process == p for s in w.etym):
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


def _fit_base(base: Form, affix: Form) -> tuple[Form, bool]:
    """Clip a derivation's base so base + affix keeps to MAX_SYLL syllables and MAX_SEG segments."""
    a = syllables(affix)
    room = max(1, min(2, MAX_SYLL - a))
    clipped = False
    if syllables(base) + a > MAX_SYLL:
        base, clipped = clip(base, room), True
    if len(base) + len(affix) > MAX_SEG and syllables(base) > 1:
        base, clipped = clip(base, 1), True
    return base, clipped


def _fit_parts(h: Form, m: Form) -> tuple[Form, Form, bool]:
    """Clip a compound's parts (the modifier first) to their first 1-2 syllables until the whole keeps to
    MAX_SYLL_COMPOUND syllables and MAX_SEG segments."""
    clipped = False
    for part, n in (("m", 2), ("h", 2), ("m", 1), ("h", 1)):
        if syllables(h) + syllables(m) <= MAX_SYLL_COMPOUND and len(h) + len(m) <= MAX_SEG:
            break
        if part == "m" and syllables(m) > n:
            m, clipped = clip(m, n), True
        elif part == "h" and syllables(h) > n:
            h, clipped = clip(h, n), True
    return h, m, clipped


def _cap(form: Form, n_syll: int, inv) -> Form:
    """Last guard after repair: at most n_syll syllables and MAX_SEG segments."""
    if syllables(form) > n_syll or len(form) > MAX_SEG:
        f = clip(form, n_syll)
        while len(f) > MAX_SEG and syllables(f) > 1:
            f = clip(f, syllables(f) - 1)
        form = _inv.repair(f[:MAX_SEG], inv) or form[:MAX_SEG]
    return form


def derive(rng, lex: Lexicon, concept: str, inv, kyr: float, lect_id: str | None = None, base: str | None = None,
           meaning: str | None = None, exclude: Iterable[str] = ()) -> Word | None:
    """A new word for `concept`: a related word plus a derivational affix ('little', 'place of', 'one who', 'thing',
    'do', 'like'), repaired to the phonotactics. Short bases are preferred (weight 1/syllables), a base that already
    carries the same affix is refused, and the result keeps to MAX_SYLL syllables (the base is clipped to its first 1-2
    syllables, noted 'clip'). None when no related word will do or the affix has worn away. `exclude`: bases not to
    use (a retry after a clash). Not stored; see `coin` / `step`."""
    c = concept_info(concept)
    lect_id = lect_id or lex.lect
    meaning = meaning or _affix_meaning(c)
    af, _ = lex.affixes.get(meaning, ((), True))
    if not af:
        return None
    if affix_share(lex, meaning) + 1.0 / max(1, len(lex.words)) > AFFIX_CAP:
        return None
    if base is None:
        ex = set(exclude)
        # (a strong CLICS edge or a base hint only: the weak edges gave EAT + 'thing' = 'tree', WATER + 'agent' = 'river')
        rel = [(k, w) for k, w in _related(lex, c.id, exclude=ex) if not _carries(lex, lex.words[k], meaning)
               and affix_fits(meaning, c.id, k)]
        if not rel and c.domain:  # (else a word of the same domain the affix fits: FISH > 'to fish', COOK > 'cooked thing')
            rel = [(k, 1.0) for k, w in lex.words.items() if k != c.id and k not in ex and w.pos != "FUNC"
                   and concept_info(k).domain == c.domain and not _carries(lex, w, meaning) and affix_fits(meaning, c.id, k)]
        if not rel:
            return None
        base = _pick(rng, _short(lex, rel))
    b = lex.words.get(resolve(base))
    if b is None or _carries(lex, b, meaning) or not affix_fits(meaning, c.id, b.concept):
        return None
    bf, clipped = _fit_base(b.form, af)
    form = _cap(_inv.repair(_attach(lex, bf, meaning), inv), MAX_SYLL, inv)
    note = f"{b.concept} + '{meaning}'" + (f" (clip {b.ipa} > {word_ipa(bf)})" if clipped else "")
    return Word(c.id, form, c.pos, c.freq_class,
                b.etym + (_step(kyr, lect_id, f"derive:{meaning}", form, c.gloss, note),), float(kyr))


def _clash(a: str, b: str) -> bool:
    """Pairs a compound never joins: a verb with a colour."""
    ca, cb = sem_class(a), sem_class(b)
    return {ca, cb} == {"verb", "colour"}


def _compound_parts(rng, lex: Lexicon, c: Concept, head: str | None, modifier: str | None) -> tuple[str | None, str | None]:
    """Head: the concept's class word (COMPOUND_HEADS) or a base hint of the same class, else a related noun. Modifier: a
    CLICS neighbour, base hint or same-class concept (weight 3), or for concrete nouns a quality (weight 1)."""
    cls = sem_class(c.id)
    if head is None:
        if c.pos != "N":
            return None, None   # verbs, qualities and function words are replaced by derivation, shift or coinage
        heads = COMPOUND_HEADS.get(cls, ())
        if cls in ("kin", "person"):   # 'woman' heads a female kin term, 'man' a male one
            g = ("WOMAN",) if c.id in _FEMALE_KIN else ("MAN", "MALE PERSON") if c.id in _MALE_KIN else ()
            heads = next(([h] for h in (*g, "PERSON") if h in lex.words and h != c.id), heads)
        cands = [(h, 3.0) for h in heads if h in lex.words and h != c.id]
        cands += [(resolve(b), 3.0) for b in c.base if resolve(b) in lex.words and resolve(b) != c.id
                  and sem_class(resolve(b)) == cls and all(resolve(b) != h for h, _ in cands)]
        if not cands:
            cands = [(k, w) for k, w in _related(lex, c.id) if lex.words[k].pos == "N"]
        if not cands:
            return None, None
        head = _pick(rng, _short(lex, cands))
    head = resolve(head)
    if modifier is None:
        ex = {c.id, head}
        pool = [(k, 3.0) for k, _ in _related(lex, c.id, exclude=ex)]
        same = [k for k in _class_members().get(cls, ()) if k in lex.words and k not in ex
                and all(k != p for p, _ in pool)] if cls not in ("abstract", "func", "name") else []
        pool += [(k, 3.0 / max(3, len(same))) for k in same]
        if cls in CONCRETE and lex.words[head].pos == "N":
            pool += [(q, 1.0) for q in _QUALITY if q in lex.words and q not in ex and all(q != p for p, _ in pool)]
        pool = [(k, w) for k, w in pool if not _clash(k, head) and not _clash(k, c.id)]
        if not pool:
            return head, None
        modifier = _pick(rng, _short(lex, pool))
    return head, resolve(modifier)


def compound(rng, lex: Lexicon, concept: str, inv, kyr: float, lect_id: str | None = None,
             head_first: bool | None = None, head: str | None = None, modifier: str | None = None,
             process: str | None = None, note: str | None = None) -> Word | None:
    """A new word for `concept` from two existing words, in the lexicon's head order unless `head_first` says otherwise.
    Head: the concept's class word (RIVER for a water body, PERSON for a kin term or role, ANIMAL for an animal ...) or a
    related noun; modifier: a related or same-class word, or a plain quality for concrete nouns only. Only nouns compound
    (None). Parts are clipped so the compound keeps to MAX_SYLL_COMPOUND syllables (noted 'clip')."""
    c = concept_info(concept)
    lect_id = lect_id or lex.lect
    head, modifier = _compound_parts(rng, lex, c, head, modifier)
    if head is None or modifier is None or head not in lex.words or modifier not in lex.words:
        return None
    h, m = lex.words[head], lex.words[modifier]
    hf_, mf_, clipped = _fit_parts(h.form, m.form)
    form = _cap(_inv.repair(_join(lex, hf_, mf_, head_first), inv), MAX_SYLL_COMPOUND, inv)
    proc = process or f"compound:{head}+{modifier}"
    nt = note or f"{head} + {modifier} ({m.ipa})"
    if clipped:
        nt += f" (clip {h.ipa} {m.ipa} > {word_ipa(hf_)} {word_ipa(mf_)})"
    return Word(c.id, form, c.pos, c.freq_class, h.etym + (_step(kyr, lect_id, proc, form, c.gloss, nt),), float(kyr))


def coin(rng, lex: Lexicon, concept: str, inv, kyr: float, lect_id: str | None = None, how: str | None = None,
         head_first: bool | None = None, store: bool = True) -> Word:
    """A word for a concept the lect has no word for (a crop arriving with no donor word, an elaboration): derive or
    compound from related words, or a fresh root when nothing is related (`how="root"`: always a fresh root, origin
    unknown). Stored unless `store=False`."""
    c = concept_info(concept)
    lect_id = lect_id or lex.lect
    how = how or ("derive" if rng.random() < 0.6 else "compound")
    w = None
    if how == "derive":
        w = derive(rng, lex, c.id, inv, kyr, lect_id)
    elif how == "compound":
        w = compound(rng, lex, c.id, inv, kyr, lect_id, head_first)
    if w is None:
        n = _n_syll_for(rng, c.freq_class)
        for _ in range(10):
            f = _inv.draw_word(rng, inv, n_syll=n)
            if len(f) <= MAX_SEG:
                break
        w = Word(c.id, f, c.pos, c.freq_class, (_step(kyr, lect_id, "coin", f, c.gloss),), float(kyr))
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
    bf, _ = _fit_base(b.form, af)
    form = _cap(_inv.repair(_attach(lex, bf, meaning), inv), MAX_SYLL, inv)
    return Word(c.id, form, c.pos, c.freq_class,
                b.etym + (_step(kyr, lect_id or lex.lect, "taboo", form, c.gloss, f"'the {q.lower()} one'"),), float(kyr))


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


def shift_word(rng, lex: Lexicon, concept: str, kyr: float, lect_id: str | None = None) -> Word | None:
    """Colexification shift: `concept` takes the word of a CLICS neighbour (which keeps it too, now colexified, until a
    later replacement re-fills it). A concept takes or passes on a word this way at most once per SHIFT_GAP generations,
    a word already shared by two concepts is not taken, and the step names the root of a shift chain (the note says through which neighbour)."""
    c = concept_info(concept)
    if not _shift_ok(lex, c.id):
        return None
    shared = {f for f, cs in lex.homophones().items()} if lex.words else set()
    nb = [(n, float(f)) for n, f in clics_neighbours(c.id, BUILD_MIN_FAMILIES) if n in lex.words and _shift_ok(lex, n)
          and lex.words[n].form not in shared    # a word already doing double duty is not taken on for a third
          and (c.pos != "FUNC") == (lex.words[n].pos != "FUNC")]   # function words shift only among themselves
    if not nb:
        return None
    via = _pick(rng, nb)
    src = lex.words[via]
    root = _shift_root(lex, via)
    note = "" if root == via else f"via {via}"
    lex.shifted[c.id] = lex.gen
    lex.shifted[via] = lex.gen
    return Word(c.id, src.form, c.pos, c.freq_class,
                src.etym + (_step(kyr, lect_id or lex.lect, f"shift:{root}", src.form, c.gloss, note),), float(kyr))


def borrow(word: Word, from_lect_id: str, to_lex: Lexicon, profile, inv, kyr: float, note: str = "",
           drop_distance: float | None = None) -> Word:
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
    if len(form) > MAX_SEG:   # epenthesis can swell a cluster-heavy loan; long loans get clipped in use
        form = _cap(form, MAX_SYLL_COMPOUND, inv)
        note = (note + "; " if note else "") + "clipped"
    c = concept_info(word.concept)
    w = Word(c.id, form, word.pos, c.freq_class,
             word.etym + (_step(kyr, to_lex.lect, f"borrow:{from_lect_id}", form, c.gloss, note),), float(kyr))
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
            w = derive(rng, lex, new, inv, kyr, lect_id, base=concept, meaning="little")
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
                  "agent": ("PERSON", "MAN"), "thing": (), "do": ("DO OR MAKE",), "like": ("BODY",)}


def _lexical_last(w: Word) -> EtymStep | None:
    """The word's latest step that is not a sound change (how it came to mean what it means)."""
    return next((s for s in reversed(w.etym) if not s.process.startswith("sound_change:")), None)


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
            if all(getattr(_lexical_last(lex.words[k]), "process", "") == "proto" for k in cs):
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


DERIVE_TRIES = 3   # a derivation that clashes (homophone) or finds no base is retried this often with another base or affix
_NOUN_AFFIXES = ("thing", "little", "place", "agent")


def _derive_tries(rng, lex: Lexicon, k: str, c: Concept, inv, kyr: float, lect_id: str) -> Word | None:
    """Up to DERIVE_TRIES derivations for `k` that do not make a homophone: the concept's own affix with a fresh base
    each time, then (nouns) another noun-forming affix."""
    own = _affix_meaning(c)
    meanings = [own]
    if c.pos == "N":
        alt = [m for m in _NOUN_AFFIXES if m != own and lex.affixes.get(m, ((),))[0]]
        if alt:
            meanings += [alt[int(i)] for i in rng.permutation(len(alt))]
    tried: dict[str, set] = {}
    for t in range(DERIVE_TRIES):
        m = meanings[min(t, len(meanings) - 1)]
        new = derive(rng, lex, k, inv, kyr, lect_id, meaning=m, exclude=tried.get(m, ()))
        if new is None:
            continue
        if not _clashes(lex, k, new.form):
            return new
        tried.setdefault(m, set()).add(new.etym[-1].note.split(" + '")[0])   # the base, as `derive` notes it
    return None


def _replace_word(rng, lex: Lexicon, k: str, c: Concept, src: str, opts: dict, inv, kyr: float, lect_id: str,
                  head_first, have: list, contact_words, profile) -> tuple[str, Word]:
    """The replacement for `k` from the drawn source, falling back in order derive (DERIVE_TRIES bases or affixes),
    compound, colexification shift, and only then a fresh root: a derivation that would make a homophone or finds no
    base is not by itself a reason to coin (the review of run a24559 found coinage at 65k latest steps against 40k
    derivations, intended 0.15 vs 0.35). Returns (process actually used, word)."""
    if src == "borrow":
        d = have[int(rng.integers(len(have)))]
        return src, borrow(contact_words[d][k], d, lex, profile, inv, kyr, "contact")
    if src == "coin":
        order = ["coin"]
    else:
        order = [src] + [x for x in ("derive", "compound", "shift") if x in opts and x != src] + ["coin"]
    for s in order:
        new = None
        if s == "derive":
            new = _derive_tries(rng, lex, k, c, inv, kyr, lect_id)
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
    group, `_renewal_boost`), the new word coming from SOURCES: a derivation, a compound (not for verbs), a colexification
    shift, a fresh root, a loan (only if a contact lexicon has the concept) or a taboo paraphrase (animals and dangerous
    things only); an unusable compound or taboo source adds its weight to derivation, an unavailable loan or shift is
    dropped and the rest renormalised. A source that fails or would make a homophone falls back (`_replace_word`):
    derivation with another base or affix, compound, shift, and a fresh root only last. Then affix renewal and elaboration by niche. Mutates `lex`; returns
    [(concept, process)] for the events."""
    lect_id = lect_id or lex.lect
    events: list[tuple[str, str]] = []
    if n_generations > 0:
        lex.gen += float(n_generations)
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
            if c.pos != "N":
                opts["derive"] += opts.pop("compound")
            if not _shift_ok(lex, k) or not any(n in lex.words and _shift_ok(lex, n)
                                                for n, _ in clics_neighbours(k, BUILD_MIN_FAMILIES)):
                opts.pop("shift")
            names = list(opts)
            w = np.array([opts[s] for s in names])
            src = names[int(rng.choice(len(names), p=w / w.sum()))]
            src, new = _replace_word(rng, lex, k, c, src, opts, inv, kyr, lect_id, head_first, have, contact_words,
                                     profile)
            lex.set(new)
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
        new_lex.set(Word(c.id, form, w.pos, w.freq_class,
                         w.etym + (_step(kyr, new_lex.lect, f"substrate:{old_lex.lect}", form, c.gloss),), float(kyr)))
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
    """Diagnostics: mean and max segments and syllables per word, the share of concepts in homophone groups, counts
    per etymology process (every step of every chain, and the latest non-sound-change step of each word), and
    `inherited_core_share`: the share of the Swadesh-100 words that are still the proto word (`inherited`)."""
    import collections

    words = list(lex.words.values())
    if not words:
        return {"words": 0, "mean_segments": 0.0, "max_segments": 0, "mean_syllables": 0.0, "homophone_share": 0.0,
                "processes": {}, "latest": {}, "inherited_core_share": 0.0}
    lens = [len(w.form) for w in words]
    hom = sum(len(v) for v in lex.homophones().values())
    procs = collections.Counter(s.process.split(":")[0] for w in words for s in w.etym)
    latest = collections.Counter(
        next((s.process.split(":")[0] for s in reversed(w.etym) if not s.process.startswith("sound_change:")), "?")
        for w in words)
    core = [w for k, w in lex.words.items() if k in CORE100]
    return {"words": len(words), "mean_segments": float(np.mean(lens)), "max_segments": int(max(lens)),
            "mean_syllables": float(np.mean([syllables(w.form) for w in words])),
            "homophone_share": hom / len(words), "processes": dict(procs), "latest": dict(latest),
            "inherited_core_share": (sum(map(inherited, core)) / len(core)) if core else 0.0}


_REPLACING = ("coin", "derive", "compound", "shift", "borrow", "taboo", "substrate", "elaborate")


def inherited(w: Word) -> bool:
    """Is `w` its concept's proto word, carried down by sound change alone (the root of its chain is the proto step
    for this very concept, and no step since replaced it: no coinage, derivation, compound, shift, loan, taboo or
    substrate)?"""
    if not w.etym:
        return False
    root = w.etym[0]
    if root.process != "proto" or root.gloss != concept_info(w.concept).gloss:
        return False
    return not any(s.process.split(":")[0] in _REPLACING for s in w.etym[1:])


# --- json ---------------------------------------------------------------------------------------------------------------

def to_json(lex: Lexicon, full: bool = True) -> dict:
    """{"lect", "head_first", "affixes": {meaning: {ipa, suffix}}, "words": {concept: {ipa, pos, freq, born_kyr,
    etym: [[kyr, lect, process, form, gloss, note], ...]}}}. Not full: the Swadesh-100 and names only."""
    words = {}
    for k, w in lex.words.items():
        if not full and k not in CORE100 and w.pos != "NAME":
            continue
        words[k] = {"ipa": w.ipa, "pos": w.pos, "freq": w.freq_class, "born_kyr": w.born_kyr,
                    "etym": [s.to_list() for s in w.etym]}
    return {"lect": lex.lect, "head_first": lex.head_first, "gen": lex.gen, "shifted": dict(lex.shifted),
            "notes": [list(x) for x in lex.notes],
            "affixes": {m: {"ipa": word_ipa(f), "suffix": s} for m, (f, s) in lex.affixes.items()},
            "words": words}


def from_json(d: dict) -> Lexicon:
    lex = Lexicon(d["lect"], {}, {}, bool(d.get("head_first", False)), float(d.get("gen", 0.0)),
                  {_i(k): float(v) for k, v in d.get("shifted", {}).items()}, [tuple(x) for x in d.get("notes", [])])
    for m, a in d.get("affixes", {}).items():
        lex.affixes[m] = (tuple(from_ipa(a["ipa"])) if a["ipa"] else (), bool(a["suffix"]))
    for k, v in d["words"].items():
        lex.words[_i(k)] = Word(_i(k), tuple(from_ipa(v["ipa"])), v["pos"], int(v["freq"]),
                                tuple(EtymStep.from_list(s) for s in v["etym"]), float(v["born_kyr"]))
    return lex
