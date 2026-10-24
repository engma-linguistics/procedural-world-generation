"""The lineage input: a graph of peoples with origin times, niches, traits, and soft wishes.

TOML (or JSON of the same shape); preset: planet/lineages/samples/dnd.toml. Each
[[lineage]] has an `origin` and a time `at` (years before the present: "8 Myr",
"450 kyr", "12000 yr"; a bare number is kyr):
- root:     arises in the world (no parents)
- split:    branches from `parents = [p]` (the usual tree edge); the parent ends at its last split unless `persists`
- arrival:  comes from outside the world (feywild, the planes) at `place = [lat, lon]` or where its habitat is best
- hybrid:   of two `parents`, where their ranges overlap; `contact = true` (default): it exists only where both
            parents meet (half-elves); false: it founds a people of its own
- template: an overlay on `parents` (hosts) from `at` on (tieflings): a `share` of the hosts' people,
            spreading from a few `sites` through the hosts' range only
- group:    a way of life within a people (`group_of = <people>`, default `at` GROUP_KYR): steppe and forest orcs,
            human seafarers and farmers. Not a split: it appears where its own niche beats its people's, never
            ends its people, mixes freely with it and its sister groups, and rolls up into it in the summaries
So the "tree" is a DAG. Anything a line leaves out it inherits from its first parent.
[[use]] (by = a trait, a place tag or a line's id, good = land.GOODS, weight, optional pull) says what each way
of life looks for in the land (farmland, pasture, ores, harbours, coral coasts, volcanoes...); meta.land_pull how
strongly, or the use's own pull (a line takes the strongest pull of its favoured goods; history._land_mult);
strict = true: off those goods the habitat is cut, not lifted back to a mean of 1 (peoples bound to one country).
meta.mode (PW-695): "fantasy" (default; every line, the fantasy goods) or "real" (only the lines with `real = true`,
the humans, leave the rest out as if disabled; the fantasy goods (FANTASY_GOODS) drop out of [[use]]). Magic is PW-696.
meta.animals / animals_force / animals_at (PW-691, PW-710): the domesticable animals (animal_defs.TABLE; default every
real one), the fantasy ones whose rare taming is forced (tests) and the anchor dates; fantasy animals drop out in real mode.
meta.crops / crops_force / crops_at (PW-721): the same for the staple plants (crop_defs.TABLE).
meta.portal_mode / portals / portal_sites (PW-697): arrivals from outside come "off" (each at its best habitat),
or through N portals placed "random"ly or at interesting "sites" (history.History.portal_cells).
"""

from __future__ import annotations

import json
import re
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path

# movement and behaviour (docs/proposals/lineages.md section 2). sea: share of the carried
# pressure kept per sea cell crossed (0: can't cross; establishment needs spread.EST, so 0.55 ~ 3 cells);
# relief: share kept per 1000 m climbed between cells is exp(-relief) (walkers 0.6); speed: x the base
# speed; the rest are habitat knobs. How dense, exploring, seafaring and insular a people is: DEMOGRAPHY.
TRAITS = {
    "flies": {"sea": 0.72, "relief": 0.0},
    "swims": {"sea": 0.55, "coast": 0.15},
    "coastal": {"coast": 0.6},
    "seafaring": {},  # (boats: its sea share, DEMOGRAPHY)
    "agricultural": {"farm": 1.0},
    "nomadic": {"speed": 2.0, "open": 0.3},
    "mountain": {"relief": 0.0, "mountain": 0.5},
    "hardy": {"widen": 1.25},
    "insular": {},  # (insularity and exploration: DEMOGRAPHY)
    "cosmopolitan": {},
    "subterranean": {"relief": 0.15, "widen": 1.15, "mountain": 0.3},
    "hunter": {},  # (no movement knob: hunting and foraging peoples are who tames dogs and first cultivates wild plants, PW-718, PW-721)
    "miner": {},  # (no movement knob: what it looks for in the land is the [[use]] table's)
}
# ways of life (PW-723): how a people gets its living, a cultural trait (a group of a people may differ from it). The goods a
# way reads (weight per good; the same [[use]] rows a trait would give) REPLACE the food rows its traits would give
# (agricultural -> fertile, nomadic -> grazing; place and own-id rows stay), set who tames the herd animals (herd share),
# who first cultivates plants (gather share) and who tames dogs (forage share), and so the fuels and the brief's foods.
# A line with no way keeps its traits' rows. Raiding, tribute and trade belong on top of these (PW-661), not here.
WAYS = {
    "forager": {"foraging": 1.0},  # broad hunting and gathering
    "fisher_forager": {"foraging": 0.6, "fish": 1.0, "shellfish": 0.5},  # specialised, often settled, on rich coasts, rivers and lakes
    "horticulturalist": {"fertile": 0.5, "foraging": 0.5},  # gardens and swidden, still half gathered
    "farmer": {"fertile": 1.0},  # plough and irrigation
    "pastoral_nomad": {"grazing": 1.0},  # herds followed over open country, all year
    "transhumant": {"grazing": 0.7, "fertile": 0.3},  # herds moved between seasonal pastures from a home base with some fields
    "agro_pastoral": {"fertile": 0.5, "grazing": 0.5},  # fields and herds on the same ground
    "sea_nomad": {"fish": 1.0, "harbour": 0.7, "foraging": 0.3},  # boat-dwelling fishers moving along the coasts
}
WAY_FOOD = ("fertile", "grazing", "foraging", "fish", "shellfish")  # (the goods a way's rows replace from the traits; harbours, timber and the rest stay)
LATE_SEA_KYR = 3.0  # short sea hops by boat (the spread's sea factor) from then, for a sea share >= SHORT_HOP_SHARE
SHORT_HOP_SHARE = 0.2
# long sea crossings (crossing.py): way -> (rate per kyr at a zero gap, length scale km, only since kyr ago).
# The chance a line reaches a landmass it doesn't hold in a step of dt kyr is 1 - exp(-dt x sum over its
# ways of rate x exp(-gap / L)) x the landing's habitat. 'raft' is everyone's (drift rafts, storms: monkeys
# across the young Atlantic, lemurs to Madagascar): a few hundred km once in a few Myr. Coastal foragers'
# canoes (Sahul ~60 kyr ago, ~100 km gaps), swimmers and fliers reach further. Every way but the raft is
# x the line's will to explore and leave home (crossing.modes).
HOPS = {
    "raft": (3e-4, 150.0, None),
    "coastal": (0.01, 250.0, None),
    "swims": (0.05, 400.0, None),
    "flies": (0.05, 700.0, None),
}
# boats (the way 'seafaring'): the share of a people's frontier that takes to the sea (sea_share) sets the
# rate, BOATS[0] x share / BOATS_FULL per kyr, and the reach, from BOATS[1] km at share 0 to BOATS[2] km at
# BOATS_FULL, from BOATS[3] kyr ago (the Lapita / Polynesian voyages, 1000s of km). A seafaring people
# (share 0.6) sails as the old 'seafaring' way did (1 /kyr, 1500 km); dwarves (0.05) put to sea ~12x less
# often and less far, but not never.
BOATS = (1.0, 300.0, 1500.0, 6.0)
BOATS_FULL = 0.6
# canoes (PW-677): before the voyaging (BOATS[3]) and since CANOES_KYR ago (Sahul ~60 kyr ago), a people with a
# sea share crosses the way boats do but only over short gaps (reach BOATS[1] km): modern peoples that have been
# around for tens of kyr reach the next landmass over a few hundred km of water, not only after the voyages.
CANOES_KYR = 60.0

# demography and movement, per people (PW-650): each can be given in the spec; else it comes from the traits
# (the strongest value among its traits; 'insular' sets exploration and insularity whatever else).
# density: people per km² of full habitat (K = 1); a people's number is the sum of presence x density x area.
#   Also: a separate patch with fewer than meta.viable_pop people fades (history.MVP_TAU_KYR), so a sparse people
#   (giants: a band roaming thousands of km²) needs a large piece of good country to hold a land at all; and
#   in competition a denser people weighs more (history.DENSITY_PUSH: farmers press on foragers; giants
#   barely dent anyone's room, and anyone dents theirs).
# explore 0..1: how readily the frontier pushes into marginal land and over the sea (long crossings x 2 explore).
# sea_share 0..1: the share of the frontier that tries water crossings (BOATS; short hops over straits from
#   LATE_SEA_KYR at >= SHORT_HOP_SHARE).
# insularity 0..1: resistance to mixing (the late relaxing of competition x 2 (1 - insularity)) and to leaving
#   home (long crossings x (1.25 - 0.5 insularity)).
BAND = 25  # people in a band: band_km2 = BAND / density, the land a band roams
DEMO_DEFAULT = {"density": 2.0, "explore": 0.5, "sea_share": 0.03, "insularity": 0.5}
DEMOGRAPHY = {
    "agricultural": {"density": 10.0},
    "nomadic": {"density": 0.6, "explore": 0.7},
    "subterranean": {"density": 3.0, "explore": 0.35},
    "miner": {"density": 3.0},
    "flies": {"density": 0.6, "explore": 0.65},
    "seafaring": {"sea_share": 0.6, "explore": 0.7},
    "swims": {"sea_share": 0.4},
    "coastal": {"sea_share": 0.3, "density": 3.0},
    "cosmopolitan": {"insularity": 0.2, "explore": 0.7},
    "insular": {"insularity": 0.85, "explore": 0.25},
}
DEMO_KEYS = tuple(DEMO_DEFAULT)
VIABLE_POP = 500.0  # default meta.viable_pop


def demography(traits) -> dict:
    """The demography knobs a set of traits gives (DEMOGRAPHY: the strongest value; 'insular' overrides)."""
    out = dict(DEMO_DEFAULT)
    for k in DEMO_KEYS:
        vals = [DEMOGRAPHY[t][k] for t in traits if k in DEMOGRAPHY.get(t, {}) and t != "insular"]
        if vals:
            out[k] = max(vals) if k != "insularity" else min(vals)
        if "insular" in traits and k in DEMOGRAPHY["insular"]:
            out[k] = DEMOGRAPHY["insular"][k]
    return out


# senses and bodies (PW-694): what a people tastes, digests and is poisoned by, for the future cuisine pass (PW-692);
# nothing in the simulation reads them. Real-world analogues: cats lack the sweet receptor, birds feel no capsaicin,
# lactase persistence in herding humans, onions and garlic poison dogs, cats and birds, chocolate (theobromine) too.
# Inherited from the first parent key by key (a `body` table in the spec gives only what differs).
# The culinary keys (PW-726; intake section 4.3): suction (drinking and slurping), teeth, gut (ruminants are foregut),
# salt (herbivores crave it), display (horns are permanent and ringed, antlers shed yearly) and shed (who sheds: one
# clock or two), hours (when it is active), thermo (ectotherms feast and fast) and fire (false: cooks without fire).
# Only `fire = false` is read by a pass (fuels.py); the rest are for the story and the culinary brief.
BODY_DEFAULT = {"sweet": True, "milk": False, "capsaicin": True, "bitter": "normal", "smell": "normal",
                "diet": "omnivore", "raw_meat": False, "cellulose": False, "toxic": [],
                "suction": "normal", "teeth": "grinding", "gut": "simple", "salt": "normal", "display": "none",
                "shed": "none", "hours": "diurnal", "thermo": "endo", "fire": True}
BODY_CHOICES = {"bitter": ("low", "normal", "high"), "smell": ("low", "normal", "keen"),
                "diet": ("herbivore", "omnivore", "carnivore", "obligate_carnivore"),
                "suction": ("none", "poor", "normal"), "teeth": ("grinding", "conical", "dental_pad", "beak"),
                "gut": ("simple", "hindgut", "foregut"), "salt": ("normal", "craving"), "display": ("none", "horns", "antlers"),
                "shed": ("none", "both", "males"), "hours": ("diurnal", "crepuscular", "nocturnal"), "thermo": ("endo", "ecto")}
TOXINS = ("alliums", "theobromine")
BODY_BOOLS = ("sweet", "milk", "capsaicin", "raw_meat", "cellulose")


def parse_body(v, lid: str = "") -> dict:
    """Validate a `body` table (only the keys given)."""
    if v in (None, ""):
        return {}
    if not isinstance(v, dict):
        raise ValueError(f"{lid}: body must be a table of {sorted(BODY_DEFAULT)}")
    out = {}
    for k, x in v.items():
        if k not in BODY_DEFAULT:
            raise ValueError(f"{lid}: unknown body key {k!r} (one of {sorted(BODY_DEFAULT)})")
        if k in BODY_BOOLS:
            # true / false, or a share 0..1 of the people (lactase persistence is a population frequency, PW-701)
            if isinstance(x, bool):
                out[k] = x
            elif isinstance(x, (int, float)) and 0 <= x <= 1:
                out[k] = float(x)
            else:
                raise ValueError(f"{lid}: body.{k} must be true, false or a share between 0 and 1")
        elif k == "fire":
            if not isinstance(x, bool):
                raise ValueError(f"{lid}: body.fire must be true or false")
            out[k] = x
        elif k == "toxic":
            xs = [x] if isinstance(x, str) else list(x)
            bad = [t for t in xs if t not in TOXINS]
            if bad:
                raise ValueError(f"{lid}: unknown toxicity {bad} (one of {list(TOXINS)})")
            out[k] = sorted(set(xs))
        else:
            if x not in BODY_CHOICES[k]:
                raise ValueError(f"{lid}: body.{k} must be one of {list(BODY_CHOICES[k])}")
            out[k] = x
    return out


def body_notes(b: dict) -> list[str]:
    """What is notable about a body (differences from the human-like baseline), as short phrases. A share
    (0 < x < 1) reads as 'x% ...'."""
    out = []
    pct = lambda v: f"{round(100 * v)}% "  # noqa: E731
    if b["sweet"] is not True:
        out.append("cannot taste sweet" if not b["sweet"] else pct(b["sweet"]) + "taste sweet")
    if b["milk"]:
        out.append("digest milk as adults" if b["milk"] is True else pct(b["milk"]) + "digest milk as adults")
    if b["capsaicin"] is not True:
        out.append("feel no capsaicin heat" if not b["capsaicin"] else pct(b["capsaicin"]) + "feel capsaicin heat")
    if b["bitter"] != "normal":
        out.append("taste bitterness faintly" if b["bitter"] == "low" else "are very sensitive to bitter tastes")
    if b["smell"] != "normal":
        out.append("have a poor sense of smell" if b["smell"] == "low" else "have a keen sense of smell")
    if b["diet"] != "omnivore":
        out.append({"herbivore": "are herbivores", "carnivore": "are carnivores",
                    "obligate_carnivore": "are obligate carnivores"}[b["diet"]])
    if b["raw_meat"]:
        out.append("eat raw meat safely" if b["raw_meat"] is True else pct(b["raw_meat"]) + "eat raw meat safely")
    if b["cellulose"]:
        out.append("digest cellulose" if b["cellulose"] is True else pct(b["cellulose"]) + "digest cellulose")
    for k, text in (("suction", {"none": "cannot suck (they lap or tip their drink)", "poor": "suck poorly"}),
                    ("teeth", {"conical": "have conical, tearing teeth", "dental_pad": "have a dental pad and no upper incisors",
                               "beak": "have a beak and no teeth"}),
                    ("gut", {"hindgut": "ferment plant food in a hindgut", "foregut": "ferment plant food in a foregut (they chew the cud)"}),
                    ("salt", {"craving": "crave salt"}),
                    ("display", {"horns": "carry permanent horns (growth rings)", "antlers": "carry antlers, shed yearly"}),
                    ("shed", {"both": "shed antlers in both sexes", "males": "shed antlers in males only"}),
                    ("hours", {"crepuscular": "are active at dawn and dusk", "nocturnal": "are active at night"}),
                    ("thermo", {"ecto": "are ectotherms (their appetite follows the weather)"})):
        if b.get(k) in text:
            out.append(text[b[k]])
    if b.get("fire") is False:
        out.append("cook without fire")
    tox = [{"alliums": "alliums (onion, garlic)", "theobromine": "theobromine (chocolate)"}[t] for t in b["toxic"]]
    if tox:
        out.append("are poisoned by " + " and ".join(tox))
    return out


ORIGINS = ("root", "split", "arrival", "hybrid", "template", "group")
GROUP_KYR = 6.0  # a group's default time (kyr ago): the Holocene ways of life

KOPPEN_CODES = ["Af", "Am", "Aw", "BWh", "BWk", "BSh", "BSk", "Csa", "Csb", "Csc", "Cwa", "Cwb", "Cwc", "Cfa", "Cfb",
                "Cfc", "Dsa", "Dsb", "Dsc", "Dsd", "Dwa", "Dwb", "Dwc", "Dwd", "Dfa", "Dfb", "Dfc", "Dfd", "ET", "EF"]
GROUPS = {  # Köppen groups usable in prefers / avoids (climate.KOPPEN ids)
    "tropical": [0, 1, 2], "rainforest": [0, 1], "savanna": [2], "arid": [3, 4, 5, 6], "desert": [3, 4],
    "steppe": [5, 6], "mediterranean": [7, 8, 9], "temperate": list(range(7, 16)), "subtropical": [10, 13],
    "oceanic": [14, 15], "continental": list(range(16, 28)), "subarctic": [18, 19, 22, 23, 26, 27],
    "polar": [28, 29], "tundra": [28],
}
PLACES = ("coast", "island", "mountain", "lowland", "inland", "forest", "open", "wetland",
          "jungle", "steppe", "desert", "tundra", "island_chain", "volcanic", "hills")
# (history._tags; all usable as place wishes. volcanic: the world's volcanoes and young volcanic ground, land.goods,
# glacial and recent epochs only; hills: rolling country, moderate relief under the mountains)


@dataclass
class Lineage:
    id: str
    name: str = ""
    origin: str = "root"  # root | split | arrival | hybrid | template | group
    parents: list[str] = field(default_factory=list)
    ago_kyr: float = 0.0  # when it appears, splits, arrives, kyr before present
    temp_c: tuple[float, float] = (8.0, 24.0)  # comfort range of the annual mean (soft edges)
    rain_mm: tuple[float, float] = (400.0, 2500.0)  # comfort range of the annual rain (soft edges)
    elev_m: tuple[float, float] | None = None
    prefers: list[str] = field(default_factory=list)
    avoids: list[str] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
    speed_kmyr: float = 0.5  # expansion: how fast the frontier advances, km/yr (x the traits' speed)
    density: float | None = None  # people per km² at full habitat (None: from the traits, DEMOGRAPHY)
    explore: float | None = None  # 0..1, how readily it pushes into new land and over the sea
    sea_share: float | None = None  # 0..1, the share of its frontier that tries water crossings
    insularity: float | None = None  # 0..1, resistance to mixing and to leaving home
    body: dict = field(default_factory=lambda: {**BODY_DEFAULT, "toxic": []})  # senses and body, resolved (BODY_DEFAULT)
    body_given: dict = field(default_factory=dict)  # of it, what the spec gave on this line itself
    way: str | None = None  # way of life (WAYS), inherited from the parent (a group's people) where not given; None: from the traits
    way_given: str | None = None  # of it, what the spec gave on this line itself
    persists: bool = False  # keeps living after its last split child
    color: str | None = None
    place: tuple[float, float] | None = None  # arrival: lat, lon
    share: float = 0.1  # template / contact hybrid: share of the hosts' people
    contact: bool = True  # hybrid: exists only where both parents meet
    sites: int = 3  # template: incursion sites
    extinct_kyr: float | None = None  # gone by this long before the present (dwindles over the time before)
    custom: bool = False  # added by the user (the editor marks it), not from a preset
    real: bool = False  # lives in the real-world mode too (meta.mode = 'real' keeps only these lines, PW-695)
    children: list[str] = field(default_factory=list)  # split children

    @property
    def parent(self) -> str | None:
        return self.parents[0] if self.origin == "split" else None

    @property
    def group_of(self) -> str | None:
        """The people a group belongs to (None for any other line)."""
        return self.parents[0] if self.origin == "group" else None

    @property
    def overlay(self) -> bool:
        """Lives on others' ranges, not a range of its own (templates, contact hybrids)."""
        return self.origin == "template" or (self.origin == "hybrid" and self.contact)

    def trait(self, key: str, default=None):
        """The strongest value of a trait knob over the line's traits."""
        vals = [TRAITS[t][key] for t in self.traits if key in TRAITS.get(t, {})]
        if not vals:
            return default
        return min(vals) if key == "relief" else max(vals)

    def label(self) -> str:
        return self.name or self.id

    def demo(self, key: str) -> float:
        """A demography knob: as given (or inherited), else from the traits (DEMOGRAPHY)."""
        v = getattr(self, key)
        return float(v) if v is not None else demography(self.traits)[key]

    def demos(self) -> dict:
        return {k: self.demo(k) for k in DEMO_KEYS}

    def given_demo(self) -> dict:
        return {k: getattr(self, k) for k in DEMO_KEYS if getattr(self, k) is not None}


@dataclass
class Wish:
    a: str
    want: str  # near | apart | one of PLACES
    b: str | None = None
    weight: float = 1.0


@dataclass
class Use:
    """A way of life looking for a good in the land: lines with trait (or preferred place, or the line whose id
    is) `by` favour (weight > 0) or avoid (< 0) the world's `good` (land.GOODS) in their habitat; `pull`
    (0..1, default meta.land_pull) how strongly; the use's own strength is pull x min(weight, 1) (PW-635: a weight of
    0.5 pulls half as hard as a weight of 1, so mines can bite harder than forests); `strict`: the habitat off the goods is cut by the pull,
    not renormalised to a mean of 1 over the line's country (history._land_mult)."""
    by: str
    good: str
    weight: float = 1.0
    pull: float | None = None
    strict: bool = False


ERAS = ("stone age", "bronze age", "classical", "medieval", "renaissance", "industrial")
ERA_DEFAULT = "renaissance"  # meta.era: the vague D&D-default present. A PLACEHOLDER (PW-690): nothing reads it yet; the
# technology tree (epic PW-675, v3) will, to say how far population, spread, mixing and technology climb by the present.
# The history is not run forward past the present for it.

FANTASY_GOODS = ("mithril",)  # land.GOODS entries that are not geology (resources group 'fantasy'); real mode ignores them
MODES = ("fantasy", "real")
MODE_DEFAULT = "fantasy"  # meta.mode (PW-695): fantasy = every people and the fantasy goods; real = humans only (lines marked real = true), real goods
PORTAL_MODES = ("off", "random", "sites")
PORTAL_SITES = ("forest", "desert", "reef", "volcano")  # (history.History.portal_sites: deepest forest, middle of a desert, a coral reef, the foot of a volcano)
LAND_PULL = 0.5  # default: habitat x(1 - pull + pull G), G the best of a line's goods (mean 1 over its country)


@dataclass
class Tree:
    name: str
    seed: int
    lines: dict[str, Lineage]
    wishes: list[Wish]
    mixing_start_kyr: float = 3.0
    source: str | None = None
    disabled: list[str] = field(default_factory=list)  # lines switched off (enabled = false) and those that went with them
    uses: list[Use] = field(default_factory=list)  # [[use]]: trait or place -> good, weight
    land_pull: float = LAND_PULL
    era: str = ERA_DEFAULT  # meta.era: the target era of the present (placeholder for the technology tree, PW-690)
    animals: list[str] | None = None  # meta.animals: the domesticable animals (animal_defs.IDS) of the world; None: every real one; [] none
    animals_force: list[str] = field(default_factory=list)  # meta.animals_force: fantasy animals whose rare taming is certain (tests)
    animals_at: dict = field(default_factory=dict)  # meta.animals_at: id -> anchor time of the taming, kyr ago (default: the table's)
    crops: list[str] | None = None  # meta.crops: the cultivated plants (crop_defs.IDS) of the world; None: every real one; [] none
    crops_force: list[str] = field(default_factory=list)  # meta.crops_force: fantasy crops whose rare domestication is certain (tests)
    crops_at: dict = field(default_factory=dict)  # meta.crops_at: id -> anchor time of the first cultivation, kyr ago
    mode: str = MODE_DEFAULT  # meta.mode: 'fantasy' (all the peoples, the fantasy goods) or 'real' (only the lines marked real, real goods; PW-695)
    portal_mode: str = "off"  # meta.portal_mode: arrivals from outside: 'off' (each at its best habitat), 'random' or 'sites' (PW-697)
    portals: int = 1  # meta.portals: how many portals the arrivals come through (portal_mode random / sites)
    portal_sites: list[str] = field(default_factory=lambda: list(PORTAL_SITES))  # meta.portal_sites: the kinds of place 'sites' draws from
    viable_pop: float = VIABLE_POP  # a separate patch of a people with fewer people fades (history.MVP_TAU_KYR)

    def uses_of(self, l: Lineage) -> list[tuple[str, float]]:
        """The goods a line looks for (from its traits and preferred places), weights summed per good."""
        out: dict[str, float] = {}
        for u in self._uses_by(l):
            out[u.good] = out.get(u.good, 0.0) + u.weight
        return [(k, v) for k, v in out.items() if v != 0]

    def _uses_by(self, l: Lineage) -> list[Use]:
        rows = [u for u in self.uses if u.by in l.traits or u.by in l.prefers or u.by == l.id]
        if l.way:  # (the way's goods replace the food rows its traits give; place and own-id rows stay)
            rows = [u for u in rows if not (u.good in WAY_FOOD and u.by in TRAITS)]
            rows += [Use(l.way, g, w) for g, w in WAYS[l.way].items()]
        return rows

    def pulls_of(self, l: Lineage) -> dict[str, float]:
        """Per favoured good, how strongly it moves a line: the row's pull (meta.land_pull unless given) x
        min(weight, 1), the strongest row where several name the good (PW-635: the weight is the use's own strength)."""
        out: dict[str, float] = {}
        for u in self._uses_by(l):
            if u.weight > 0:
                p = (self.land_pull if u.pull is None else u.pull) * min(u.weight, 1.0)
                out[u.good] = max(out.get(u.good, 0.0), p)
        return out

    def pull_of(self, l: Lineage) -> float:
        """How strongly a line's land use acts at most: the strongest per-good pull (pulls_of); meta.land_pull
        for a line with no favoured good."""
        ps = self.pulls_of(l)
        return max(ps.values()) if ps else self.land_pull

    def strict_of(self, l: Lineage) -> bool:
        """Whether any of a line's favoured goods is a strict use (no renormalising of its land use)."""
        return any(u.strict for u in self._uses_by(l) if u.weight > 0)

    def order(self) -> list[Lineage]:
        """Lines oldest event first (parents before children)."""
        return sorted(self.lines.values(), key=lambda l: (-l.ago_kyr, l.id))

    def leaves(self) -> list[Lineage]:
        """What lives at the present (if the habitat lets it): lines with no split children, or persisting."""
        return [l for l in self.order() if not self.living_children(l.id) or l.persists]

    def living_children(self, lid: str) -> list[str]:
        """Split children that are not set to die out (a side branch that dies leaves its parent going)."""
        return [c for c in self.lines[lid].children if self.lines[c].extinct_kyr is None]

    def share_traits(self) -> list[str]:
        """The body flags some line gives as a share of its people (0..1), not true/false: mapped per cell
        as a population frequency (PW-701)."""
        return [k for k in BODY_BOOLS if any(not isinstance(l.body.get(k), bool) for l in self.lines.values() if not l.overlay)]

    def groups_of(self, lid: str) -> list[str]:
        """The groups (ways of life) within a people, oldest first."""
        return [l.id for l in self.order() if l.group_of == lid]

    def people_of(self, lid: str) -> str:
        """The people a line belongs to: its people for a group, else itself."""
        return self.lines[lid].group_of or lid

    def ancestors(self, lid: str) -> list[str]:
        out, l = [], self.lines[lid]
        while l.parents:
            out.append(l.parents[0])
            l = self.lines[l.parents[0]]
        return out


_T = re.compile(r"^\s*([0-9.eE+-]+)\s*(myr|ma|mya|kyr|ka|kya|yr|y|years?|bp)?\s*(ago)?\s*$", re.I)


def parse_ago(v) -> float:
    """'8 Myr' / '450 kyr' / '12000 yr' / a bare number (kyr) -> kyr before present."""
    if isinstance(v, (int, float)):
        return float(v)
    m = _T.match(str(v))
    if not m:
        raise ValueError(f"can't read the time {v!r} (use e.g. '8 Myr', '450 kyr', '12000 yr')")
    x, u = float(m.group(1)), (m.group(2) or "kyr").lower()
    return x * 1000 if u in ("myr", "ma", "mya") else x / 1000 if u in ("yr", "y", "year", "years", "bp") else x


def _pair(v, what):
    if v is None:
        return None
    if not (isinstance(v, (list, tuple)) and len(v) == 2 and float(v[0]) <= float(v[1])):
        raise ValueError(f"{what} must be [low, high], got {v!r}")
    return (float(v[0]), float(v[1]))


def _check_tag(t, lid):
    if t in GROUPS or t in PLACES or t in KOPPEN_CODES:
        return t
    raise ValueError(f"{lid}: unknown climate or place {t!r} (Köppen codes, {sorted(GROUPS)} or {list(PLACES)})")


def load(path: str | Path, mode: str | None = None) -> Tree:
    p = Path(path)
    raw = json.loads(p.read_text()) if p.suffix == ".json" else tomllib.loads(p.read_text())
    t = parse(raw, mode)
    t.source = str(p)
    return t


def _parents_of(r) -> list[str]:
    ps = r.get("parents")
    if ps is None and r.get("group_of"):
        ps = [r["group_of"]]
    if ps is None:
        ps = [r["parent"]] if r.get("parent") else []
    return [str(x) for x in ([ps] if isinstance(ps, str) else ps)]


def parse(raw: dict, mode: str | None = None) -> Tree:
    """mode: overrides meta.mode ('fantasy' | 'real'); in real mode only the lines marked `real = true` live."""
    meta = raw.get("meta", {})
    mode = str(mode or meta.get("mode") or MODE_DEFAULT).strip().lower()
    if mode not in MODES:
        raise ValueError(f"meta.mode must be one of {list(MODES)}")
    given = raw.get("lineage") or raw.get("lineages") or []
    if not given:
        raise ValueError("no [[lineage]] entries")
    rows = {}
    for r in given:
        lid = str(r["id"])
        if lid in rows:
            raise ValueError(f"lineage {lid!r} given twice")
        rows[lid] = r
    lines: dict[str, Lineage] = {}

    def build(lid: str, seen=()) -> Lineage:
        if lid in lines:
            return lines[lid]
        if lid in seen:
            raise ValueError(f"lineage {lid!r} is its own ancestor")
        r = rows[lid]
        pars = _parents_of(r)
        origin = str(r.get("origin") or ("split" if pars else "root"))
        if origin not in ORIGINS:
            raise ValueError(f"{lid}: origin must be one of {ORIGINS}")
        lo, hi = {"root": (0, 0), "arrival": (0, 0), "split": (1, 1), "hybrid": (2, 2), "template": (1, 9), "group": (1, 1)}[origin]
        if not lo <= len(pars) <= hi:
            raise ValueError(f"{lid}: a {origin} line takes {lo}{'' if lo == hi else '+'} parent(s), got {pars}")
        for q in pars:
            if q not in rows:
                raise ValueError(f"{lid}: unknown parent {q!r}")
        bases = [build(q, seen + (lid,)) for q in pars]
        base = bases[0] if bases else Lineage(id="")
        when = next((r[k] for k in ("at", "split", "appears", "arrives", "ago") if k in r), None)
        if when is None and origin == "group":
            when = min(GROUP_KYR, 0.5 * bases[0].ago_kyr)
        if origin == "group" and bases[0].origin in ("group", "template") or origin == "group" and bases[0].overlay:
            raise ValueError(f"{lid}: a group belongs to a people of its own (not a group, template or contact hybrid)")
        if when is None:
            raise ValueError(f"{lid}: give at (e.g. at = '2 Myr')")
        ago = parse_ago(when)
        for b in bases:
            if ago >= b.ago_kyr:
                raise ValueError(f"{lid} at {ago:g} kyr must come after its parent {b.id} ({b.ago_kyr:g} kyr)")
        temp, rain, traits = base.temp_c, base.rain_mm, list(base.traits)
        if origin == "hybrid":  # between its parents
            a, b = bases
            temp = ((a.temp_c[0] + b.temp_c[0]) / 2, (a.temp_c[1] + b.temp_c[1]) / 2)
            rain = ((a.rain_mm[0] * b.rain_mm[0]) ** 0.5, (a.rain_mm[1] * b.rain_mm[1]) ** 0.5)
            traits = sorted(set(a.traits) | set(b.traits))
        traits = [str(x) for x in r.get("traits", traits)]
        for x in traits:
            if x not in TRAITS:
                raise ValueError(f"{lid}: unknown trait {x!r} (one of {sorted(TRAITS)})")
        if r.get("band_km2") not in (None, "") and r.get("density") in (None, ""):
            r = {**r, "density": BAND / float(r["band_km2"])}
        demo = {}
        for k in DEMO_KEYS:
            v = r.get(k)
            if v in (None, ""):
                # inherited from a split's parent where given there (else from its own traits); a hybrid's,
                # an arrival's or a template's from its own (merged) traits unless given
                demo[k] = getattr(base, k) if origin in ("split", "group") else None
                continue
            v = float(v)
            if k == "density" and not v > 0:
                raise ValueError(f"{lid}: density must be > 0 (people per km²)")
            if k != "density" and not 0 <= v <= 1:
                raise ValueError(f"{lid}: {k} must be within 0..1")
            demo[k] = v
        bgiven = parse_body(r.get("body"), lid)
        body = {**base.body, **bgiven} if bases else {**BODY_DEFAULT, **bgiven}
        body["toxic"] = list(body["toxic"])
        wgiven = r.get("way")
        if wgiven in ("",):
            wgiven = None
        if wgiven is not None and wgiven not in WAYS:
            raise ValueError(f"{lid}: unknown way of life {wgiven!r} (one of {sorted(WAYS)})")
        place = r.get("place")
        if place is not None:
            place = (float(place["lat"]), float(place["lon"])) if isinstance(place, dict) else (float(place[0]), float(place[1]))
        l = replace(base, id=lid, name=str(r.get("name", lid)), origin=origin, parents=pars, ago_kyr=ago,
                    temp_c=_pair(r.get("temp_c"), "temp_c") or temp,
                    rain_mm=_pair(r.get("rain_mm"), "rain_mm") or rain,
                    elev_m=_pair(r.get("elev_m"), "elev_m") if "elev_m" in r else base.elev_m,
                    prefers=[_check_tag(x, lid) for x in r.get("prefers", base.prefers)],
                    avoids=[_check_tag(x, lid) for x in r.get("avoids", base.avoids)],
                    traits=traits, speed_kmyr=float(r.get("speed_kmyr", r.get("expansion_kmyr", base.speed_kmyr))), **demo,
                    body=body, body_given=bgiven, way=wgiven or (base.way if bases else None), way_given=wgiven, persists=bool(r.get("persists", False)), color=r.get("color"), place=place,
                    share=float(r.get("share", 0.1)), contact=bool(r.get("contact", True)),
                    sites=int(r.get("sites", 3)), custom=bool(r.get("custom", False)), real=bool(r.get("real", False)), children=[],
                    extinct_kyr=parse_ago(r["extinct"]) if r.get("extinct") not in (None, "") else None)
        if l.extinct_kyr is not None and not 0 <= l.extinct_kyr < ago:
            raise ValueError(f"{lid}: extinct ({l.extinct_kyr:g} kyr) must come after it appears ({ago:g} kyr)")
        lines[lid] = l
        return l

    for lid in rows:
        build(lid)
    # disabled lines (enabled = false) leave cleanly: a split child re-parents to the disabled line's parent
    # (or, under a disabled root or arrival, becomes a root or arrival itself, keeping the niche it inherited);
    # hybrids and templates of a disabled line go too (no half-elves without elves)
    off = {lid for lid, r in rows.items() if r.get("enabled", True) is False}
    if mode == "real":  # humans only: the lines marked real stay, the rest leave like a disabled line
        if not any(r.get("real") for r in rows.values()):
            raise ValueError("real mode needs lines marked `real = true` (the humans)")
        off |= {lid for lid, r in rows.items() if not r.get("real")}
    changed = True
    while changed:
        changed = False
        for l in lines.values():
            if l.id not in off and l.origin in ("hybrid", "template", "group") and any(q in off for q in l.parents):
                off.add(l.id)
                changed = True
    for l in sorted(lines.values(), key=lambda l: -l.ago_kyr):
        if l.id in off or l.origin != "split" or l.parents[0] not in off:
            continue
        p = lines[l.parents[0]]
        while p.id in off and p.origin == "split":
            p = lines[p.parents[0]]
        if p.id in off:
            l.origin, l.parents = ("arrival" if p.origin == "arrival" else "root"), []
        else:
            l.parents = [p.id]
    disabled = sorted(off)
    lines = {k: v for k, v in lines.items() if k not in off}
    for l in lines.values():
        if l.origin == "split":
            lines[l.parents[0]].children.append(l.id)
    wishes = []
    for w in raw.get("wish", raw.get("wishes", [])):
        want = str(w["want"])
        if w["a"] in off or w.get("b") in off:
            continue
        if w["a"] not in lines or (w.get("b") and w["b"] not in lines):
            raise ValueError(f"wish {w}: unknown lineage")
        if want in ("near", "apart") and not w.get("b"):
            raise ValueError(f"wish {w}: '{want}' needs b")
        if want not in ("near", "apart") and want not in PLACES:
            raise ValueError(f"wish {w}: want must be near, apart or one of {PLACES}")
        wishes.append(Wish(str(w["a"]), want, w.get("b") or None, float(w.get("weight", 1.0))))
    from .land import GOODS
    uses = []
    for u in raw.get("use", raw.get("uses", [])):
        by, good = str(u.get("by", "")), str(u.get("good", u.get("layer", "")))
        if by in off or (mode == "real" and good in FANTASY_GOODS):
            continue
        if by not in TRAITS and by not in PLACES and by not in GROUPS and by not in KOPPEN_CODES and by not in lines:
            raise ValueError(f"use {u}: by must be a trait ({sorted(TRAITS)}), a place or climate tag or a line's id")
        if good not in GOODS:
            raise ValueError(f"use {u}: good must be one of {list(GOODS)}")
        pull = None if u.get("pull") in (None, "") else float(u["pull"])
        if pull is not None and not 0 <= pull <= 1:
            raise ValueError(f"use {u}: pull must be within 0..1")
        uses.append(Use(by, good, float(u.get("weight", 1.0)), pull, bool(u.get("strict", False))))
    t = Tree(str(meta.get("name", "peoples")), int(meta.get("seed", 1)), lines, wishes,
             float(parse_ago(meta.get("mixing_start", 3.0))))
    t.disabled = disabled
    t.mode = mode
    t.portal_mode = str(meta.get("portal_mode") or "off").strip().lower()
    if t.portal_mode not in PORTAL_MODES:
        raise ValueError(f"meta.portal_mode must be one of {list(PORTAL_MODES)}")
    t.portals = int(meta.get("portals", 1))
    if not 1 <= t.portals <= 12:
        raise ValueError("meta.portals must be within 1..12")
    t.portal_sites = [str(x) for x in meta.get("portal_sites", PORTAL_SITES)]
    if not t.portal_sites or any(x not in PORTAL_SITES for x in t.portal_sites):
        raise ValueError(f"meta.portal_sites must be some of {list(PORTAL_SITES)}")
    t.uses = uses
    from . import animal_defs as AD
    am = meta.get("animals")
    t.animals = None if am is None else [str(x) for x in am]
    t.animals_force = [str(x) for x in meta.get("animals_force", [])]
    for x in [*(t.animals or []), *t.animals_force, *(meta.get("animals_at") or {})]:
        if x not in AD.BY_ID:
            raise ValueError(f"meta.animals: unknown animal '{x}' (known: {', '.join(AD.IDS)})")
    t.animals_at = {str(k): parse_ago(v) for k, v in (meta.get("animals_at") or {}).items() if v not in (None, "")}
    if mode == "real":  # the fantasy domestications are left out in the real-world mode (PW-710)
        t.animals = [x for x in (AD.REAL_IDS if t.animals is None else t.animals) if not AD.BY_ID[x].fantasy]
        t.animals_force = [x for x in t.animals_force if not AD.BY_ID[x].fantasy]
    from . import crop_defs as CD
    cm = meta.get("crops")
    t.crops = None if cm is None else [str(x) for x in cm]
    t.crops_force = [str(x) for x in meta.get("crops_force", [])]
    for x in [*(t.crops or []), *t.crops_force, *(meta.get("crops_at") or {})]:
        if x not in CD.BY_ID:
            raise ValueError(f"meta.crops: unknown crop '{x}' (known: {', '.join(CD.IDS)})")
    t.crops_at = {str(k): parse_ago(v) for k, v in (meta.get("crops_at") or {}).items() if v not in (None, "")}
    if mode == "real":  # the fantasy plants are left out in the real-world mode
        t.crops = [x for x in (CD.REAL_IDS if t.crops is None else t.crops) if not CD.BY_ID[x].fantasy]
        t.crops_force = [x for x in t.crops_force if not CD.BY_ID[x].fantasy]
    t.land_pull = float(meta.get("land_pull", LAND_PULL))
    t.era = str(meta.get("era") or ERA_DEFAULT).strip().lower()
    if t.era not in ERAS:
        raise ValueError(f"meta.era must be one of {list(ERAS)}")
    t.viable_pop = float(meta.get("viable_pop", VIABLE_POP))
    if t.viable_pop < 0:
        raise ValueError("meta.viable_pop must be >= 0")
    if not 0 <= t.land_pull <= 1:
        raise ValueError("meta.land_pull must be within 0..1")
    return t


def to_raw(t: Tree) -> dict:
    """The tree back in the input's shape (JSON-able)."""
    out = []
    for l in t.order():
        r = {"id": l.id, "name": l.name, "origin": l.origin, "at": f"{l.ago_kyr:g} kyr"}
        if l.origin == "group":
            r["group_of"] = l.group_of
        elif l.parents:
            r["parents"] = l.parents
        r.update(temp_c=list(l.temp_c), rain_mm=list(l.rain_mm), prefers=l.prefers, avoids=l.avoids,
                 traits=l.traits, speed_kmyr=l.speed_kmyr, **l.given_demo())
        if l.elev_m is not None:
            r["elev_m"] = list(l.elev_m)
        if l.place is not None:
            r["place"] = list(l.place)
        if l.body_given:
            r["body"] = l.body_given
        if l.way_given:
            r["way"] = l.way_given
        if l.color:
            r["color"] = l.color
        if l.persists:
            r["persists"] = True
        if l.extinct_kyr is not None:
            r["extinct"] = f"{l.extinct_kyr:g} kyr"
        if l.custom:
            r["custom"] = True
        if l.real:
            r["real"] = True
        if l.origin in ("template", "hybrid"):
            r["share"] = l.share
        if l.origin == "hybrid":
            r["contact"] = l.contact
        if l.origin == "template":
            r["sites"] = l.sites
        out.append(r)
    return {"meta": {"name": t.name, "seed": t.seed, "mixing_start": f"{t.mixing_start_kyr:g} kyr", "land_pull": t.land_pull,
                     "era": t.era, "viable_pop": t.viable_pop, "mode": t.mode, "portal_mode": t.portal_mode,
                     "portals": t.portals, "portal_sites": t.portal_sites,
                     **({"animals": t.animals} if t.animals is not None else {}),
                     **({"animals_force": t.animals_force} if t.animals_force else {}),
                     **({"animals_at": {k: f"{v:g} kyr" for k, v in t.animals_at.items()}} if t.animals_at else {}),
                     **({"crops": t.crops} if t.crops is not None else {}),
                     **({"crops_force": t.crops_force} if t.crops_force else {}),
                     **({"crops_at": {k: f"{v:g} kyr" for k, v in t.crops_at.items()}} if t.crops_at else {})},
            "lineage": out, "wish": [{k: v for k, v in vars(w).items() if v is not None} for w in t.wishes],
            "use": [{k: v for k, v in vars(u).items() if v is not None and v is not False} for u in t.uses]}
