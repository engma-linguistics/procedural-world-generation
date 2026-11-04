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
from .percepts import Segment, from_ipa, word_ipa

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

SOURCES = {"derive": 0.40, "compound": 0.25, "shift": 0.20, "borrow": 0.10, "taboo": 0.05}
COLEX_MIN_FAMILIES = 12       # proto colexifications only from CLICS edges seen in at least this many families
COLEX_P_PER_FAMILY = 0.008    # chance a proto-lexicon colexifies an edge, per family attesting it (TREE/WOOD 59 -> 0.47)
MAX_SYLL = 4                  # a compound longer than this keeps only the first syllable of its modifier
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
        out.append(Concept(_i(g), g.lower(), pos, sc, dom, lists, g, True, taboo, local))
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
    return Concept(cid, cid.lower(), "NAME" if cid.startswith("name:") else "N", 4, "other", local=cid.startswith("name:"))


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
        return Lexicon(lect or self.lect, dict(self.words), dict(self.affixes), self.head_first)


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
            if f not in used:
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


# --- making new words ---------------------------------------------------------------------------------------------------

_QUALITY = ("BLACK", "WHITE", "RED", "YELLOW", "GREEN", "BROWN", "BIG", "SMALL", "LONG", "OLD", "SHARP", "ROUND", "HEAVY")


def _related(lex: Lexicon, cid: str, exclude=()) -> list[tuple[str, float]]:
    """Words a new word for `cid` can be built from: CLICS neighbours, then the concept's base hints, weighted."""
    ex = {cid, *exclude}
    out = [(n, float(f)) for n, f in clics_neighbours(cid) if n in lex.words and n not in ex]
    for b in concept_info(cid).base:
        b = resolve(b)
        if b in lex.words and b not in ex and all(b != n for n, _ in out):
            out.append((b, 10.0))
    return out


def _pick(rng, items: list[tuple[str, float]]) -> str:
    w = np.array([x[1] for x in items], float)
    return items[int(rng.choice(len(items), p=w / w.sum()))][0]


def _any_word(rng, lex: Lexicon, exclude=(), max_class=3) -> str | None:
    ks = [k for k, w in lex.words.items() if w.freq_class <= max_class and w.pos in ("N", "A", "V") and k not in exclude]
    return ks[int(rng.integers(len(ks)))] if ks else None


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


def _join(lex: Lexicon, head: Form, mod: Form, head_first: bool | None) -> Form:
    hf = lex.head_first if head_first is None else head_first
    if _nsyl(head) + _nsyl(mod) > MAX_SYLL:
        mod = _first_syllable(mod)
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


def derive(rng, lex: Lexicon, concept: str, inv, kyr: float, lect_id: str | None = None, base: str | None = None,
           meaning: str | None = None) -> Word | None:
    """A new word for `concept`: a related word plus a derivational affix ('little', 'place of', 'one who', 'thing',
    'do', 'like'), repaired to the phonotactics. Not stored; see `coin` / `step`."""
    c = concept_info(concept)
    lect_id = lect_id or lex.lect
    if base is None:
        rel = _related(lex, c.id)
        base = _pick(rng, rel) if rel else _any_word(rng, lex, exclude=(c.id,))
    if base is None:
        return None
    meaning = meaning or _affix_meaning(c)
    b = lex.words[resolve(base)]
    form = _inv.repair(_attach(lex, b.form, meaning), inv)
    return Word(c.id, form, c.pos, c.freq_class,
                b.etym + (_step(kyr, lect_id, f"derive:{meaning}", form, c.gloss, f"{b.concept} + '{meaning}'"),), float(kyr))


def compound(rng, lex: Lexicon, concept: str, inv, kyr: float, lect_id: str | None = None,
             head_first: bool | None = None, head: str | None = None, modifier: str | None = None,
             process: str | None = None, note: str | None = None) -> Word | None:
    """A new word for `concept` from two existing words (head: a related word; modifier: another related word or a
    quality), in the lexicon's head order unless `head_first` says otherwise."""
    c = concept_info(concept)
    lect_id = lect_id or lex.lect
    if head is None:
        rel = _related(lex, c.id)
        head = _pick(rng, rel) if rel else _any_word(rng, lex, exclude=(c.id,))
    if head is None:
        return None
    head = resolve(head)
    if modifier is None:
        rel = _related(lex, c.id, exclude=(head,))
        qual = [(q, 3.0) for q in _QUALITY if q in lex.words and q != head]
        pool = rel + qual
        modifier = _pick(rng, pool) if pool else _any_word(rng, lex, exclude=(c.id, head))
    if modifier is None:
        return None
    modifier = resolve(modifier)
    h, m = lex.words[head], lex.words[modifier]
    form = _inv.repair(_join(lex, h.form, m.form, head_first), inv)
    proc = process or f"compound:{head}+{modifier}"
    return Word(c.id, form, c.pos, c.freq_class,
                h.etym + (_step(kyr, lect_id, proc, form, c.gloss, note or f"{head} + {modifier} ({m.ipa})"),), float(kyr))


def coin(rng, lex: Lexicon, concept: str, inv, kyr: float, lect_id: str | None = None, how: str | None = None,
         head_first: bool | None = None, store: bool = True) -> Word:
    """A word for a concept the lect has no word for (a crop arriving with no donor word, an elaboration): derive or
    compound from related words, or a fresh root when nothing is related. Stored unless `store=False`."""
    c = concept_info(concept)
    lect_id = lect_id or lex.lect
    how = how or ("derive" if rng.random() < 0.6 else "compound")
    w = derive(rng, lex, c.id, inv, kyr, lect_id) if how == "derive" else compound(rng, lex, c.id, inv, kyr, lect_id, head_first)
    if w is None or how == "root":
        f = _inv.draw_word(rng, inv, n_syll=_n_syll_for(rng, c.freq_class))
        w = Word(c.id, f, c.pos, c.freq_class, (_step(kyr, lect_id, "coin", f, c.gloss),), float(kyr))
    if store:
        lex.set(w)
    return w


def taboo_word(rng, lex: Lexicon, concept: str, inv, kyr: float, lect_id: str | None = None) -> Word | None:
    """A taboo paraphrase: a quality plus 'one who' / 'thing' ('the brown one', 'the long thing')."""
    c = concept_info(concept)
    qual = [q for q in _QUALITY if q in lex.words]
    if not qual:
        return None
    q = qual[int(rng.integers(len(qual)))]
    meaning = "agent" if c.domain in ("animal", "fauna") or c.taboo and c.pos == "N" else "thing"
    if c.pos == "V":
        meaning = "do"
    b = lex.words[q]
    form = _inv.repair(_attach(lex, b.form, meaning), inv)
    return Word(c.id, form, c.pos, c.freq_class,
                b.etym + (_step(kyr, lect_id or lex.lect, "taboo", form, c.gloss, f"'the {q.lower()} one'"),), float(kyr))


def shift_word(rng, lex: Lexicon, concept: str, kyr: float, lect_id: str | None = None) -> Word | None:
    """Colexification shift: `concept` takes the word of a CLICS neighbour (which keeps it too, now colexified, until a
    later replacement re-fills it)."""
    c = concept_info(concept)
    nb = [(n, float(f)) for n, f in clics_neighbours(c.id) if n in lex.words]
    if not nb:
        return None
    src = lex.words[_pick(rng, nb)]
    return Word(c.id, src.form, c.pos, c.freq_class,
                src.etym + (_step(kyr, lect_id or lex.lect, f"shift:{src.concept}", src.form, c.gloss),), float(kyr))


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


def step(rng, lex: Lexicon, n_generations: float, inv, contact_words: dict[str, Lexicon] | None = None,
         kyr: float = 0.0, lect_id: str | None = None, niche_weights: dict[str, float] | None = None,
         profile=None, head_first: bool | None = None) -> list[tuple[str, str]]:
    """Lexical events over `n_generations` (fractional is fine) in one batch: each word is replaced with probability
    1 - (1 - h)^n, h = BASE_REPLACE * RATE_BY_FREQ[freq_class], the new word coming from a derivation (40%), a compound
    (25%), a colexification shift (20%), a loan (10%, only if a contact lexicon has the concept) or a taboo paraphrase (5%,
    animals and dangerous things only); unavailable sources are dropped and the rest renormalised. Then elaboration by
    niche. Mutates `lex`; returns [(concept, process)] for the events."""
    lect_id = lect_id or lex.lect
    events: list[tuple[str, str]] = []
    if n_generations > 0 and lex.words:
        keys = list(lex.words)
        h = np.array([hazard(lex.words[k].freq_class) for k in keys])
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
            if not c.taboo:
                opts.pop("taboo")
            if not clics_neighbours(k) or not any(n in lex.words for n, _ in clics_neighbours(k)):
                opts.pop("shift")
            names = list(opts)
            w = np.array([opts[s] for s in names])
            src = names[int(rng.choice(len(names), p=w / w.sum()))]
            new = None
            if src in ("derive", "compound"):
                taken = {w.form for c2, w in lex.words.items() if c2 != k}
                for _ in range(3):   # avoid making a homophone when another base or modifier would do
                    new = (derive(rng, lex, k, inv, kyr, lect_id) if src == "derive"
                           else compound(rng, lex, k, inv, kyr, lect_id, head_first))
                    if new is None or new.form not in taken:
                        break
            elif src == "shift":
                new = shift_word(rng, lex, k, kyr, lect_id)
            elif src == "taboo":
                new = taboo_word(rng, lex, k, inv, kyr, lect_id)
            elif src == "borrow":
                d = have[int(rng.integers(len(have)))]
                new = borrow(contact_words[d][k], d, lex, profile, inv, kyr, "contact")
            if new is None:
                new = coin(rng, lex, k, inv, kyr, lect_id, how="root", store=False)
                src = "coin"
            lex.set(new)
            events.append((k, src))
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


def _sound_step(w: Word, form: Form, rule_id: str, kyr: float, lect_id: str) -> Word:
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
                              last.note)
            return replace(w, form=form, etym=w.etym[:-1] + (merged,))
    return w.with_step(_step(kyr, lect_id, f"sound_change:{rule_id}", form, concept_info(w.concept).gloss), form)


def apply_rule_to_lexicon(lex: Lexicon, rule_apply_fn: Callable[[Form], Form], rule_id: str, kyr: float,
                          lect_id: str | None = None) -> int:
    """Run a sound change (`rule_apply_fn(form) -> form`) over every word and the derivational affixes. Only words that
    changed get a `sound_change:<id>` step; successive changes at the same kyr in the same lect collapse into one step
    (ids joined by '+', '+…n' past four), and so does anything past a run of MAX_SOUND_RUN sound-change steps. Returns
    the number of words changed."""
    lect_id = lect_id or lex.lect
    n = 0
    cache: dict[Form, Form] = {}
    for k, w in list(lex.words.items()):
        f = cache.get(w.form)
        if f is None:
            f = cache[w.form] = tuple(rule_apply_fn(w.form))
        if f != w.form and f:
            lex.words[k] = _sound_step(w, f, rule_id, kyr, lect_id)
            n += 1
    for m, (af, suf) in list(lex.affixes.items()):
        f = tuple(rule_apply_fn(af))
        if f:
            lex.affixes[m] = (f, suf)
    return n


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
    return {"lect": lex.lect, "head_first": lex.head_first,
            "affixes": {m: {"ipa": word_ipa(f), "suffix": s} for m, (f, s) in lex.affixes.items()},
            "words": words}


def from_json(d: dict) -> Lexicon:
    lex = Lexicon(d["lect"], {}, {}, bool(d.get("head_first", False)))
    for m, a in d.get("affixes", {}).items():
        lex.affixes[m] = (tuple(from_ipa(a["ipa"])), bool(a["suffix"]))
    for k, v in d["words"].items():
        lex.words[_i(k)] = Word(_i(k), tuple(from_ipa(v["ipa"])), v["pos"], int(v["freq"]),
                                tuple(EtymStep.from_list(s) for s in v["etym"]), float(v["born_kyr"]))
    return lex
