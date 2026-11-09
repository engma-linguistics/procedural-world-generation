"""The domesticable animals as one table (PW-691), and the craft that carry them over the sea (PW-688 part 2).

No fauna is simulated (PW-184), so each animal's wild range is derived from the land (climate, cover, ground) by a
function of the epoch; nothing in it names Earth's continents or a species, so "horses" are the rideable grazing
herd animal of open country on any world. One row says, for an animal: its wild range, the date it was first tamed
on Earth (the anchor; each run draws its own around it), who tames it and who then takes it up (by a people's way
of life: the shares of `landuse.shares`: farm, herd and `forage` = the foraging use or the hunter trait, PW-718), how fast its use spreads
over peopled land, what it does (speed, capacity, the land a herder or farmer works), and how big a craft carries it
over the sea (`size`). `fantasy` rows are animals Earth never domesticated: off by default, rare when switched on
(`rare` = the chance a world has such a taming at all), always there when forced (`meta.animals_force`, for tests),
and dropped in the real-world mode (PW-695, PW-710).

Bit i of the stored `animal_known` / `animal_wild` layers (uint16 since PW-835: 13 animals) is the animal with `bit` i here.

Anchors and ranges (PW-835, lane 256; quotes in docs/review/food/lane256.md): chicken 3.5 ka (Peters et al. 2022 PNAS, Ban Non Wat,
1650-1250 BCE; it was 8 ka), horse 4.2 ka (Librado et al. 2021 Nature, DOM2 from the lower Volga-Don after ~2200 BC; it was 5.5 ka,
Botai), pig 10.5 ka (Frantz et al. 2019, PMC6717267), reindeer 2 ka (JUDGEMENT between herding certain from ~800-900 AD and a
suggested ~1500 BC, PMC7366605), camel 4.5 ka (Bactrian before 4.45 ka, PMC6946651; the dromedary ~3 ka, Almathen et al. 2016),
llama and alpaca 6 ka (Florida Museum: ~6000 years ago in the central Andean highlands), water buffalo 6.3 ka (river type, Wikipedia;
swamp type 3-7 ka, PMC8289072), yak 7.3 ka (Qiu et al. 2015 Nat Commun, PMC4703879).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np


def _win(x, e):
    a, b, c, d = e
    return np.clip(np.minimum((x - a) / (b - a), (d - x) / (d - c)), 0, 1)


def _open(env, lo, hi):
    tc = env.get("tree_cover", np.zeros(len(env["temperature"])))
    return np.clip((hi - tc) / (hi - lo), 0, 1)


def _elev(env):
    return np.maximum(env["elevation"] - env["ice"], 0)


# -- wild ranges: suitability 0..1 per cell from an epoch's env and tags, 0 off the ice-free land --------------------
def wild_horse(env, tags, land):
    """Open temperate grassland and steppe, as Equus on Earth: cool to mild, semi-arid to moist, little tree cover,
    not high mountains (thinning from 2800 m, gone at 4500 m)."""
    t, r = env["temperature"], env["precipitation"]
    return np.where(land, _win(t, (-4.0, 4.0, 20.0, 27.0)) * _win(r, (120.0, 300.0, 1000.0, 1700.0)) * _open(env, 8.0, 35.0)
                    * _win(_elev(env), (-1.0, 0.0, 2800.0, 4500.0)), 0.0)


def wild_dog(env, tags, land):
    """A wolf-like canid: anywhere with prey, so every ice-free land but the driest desert and the coldest margin."""
    t, r = env["temperature"], env["precipitation"]
    return np.where(land, _win(t, (-30.0, -15.0, 35.0, 45.0)) * _win(r, (40.0, 150.0, 6000.0, 7000.0)), 0.0)


def wild_caprine(env, tags, land):
    """Wild sheep and goats: hills and rough dry open ground (steppe, mediterranean scrub, mountain flanks)."""
    t, r = env["temperature"], env["precipitation"]
    rough = np.where(tags["hills"] | tags["mountain"], 1.0, 0.6)
    return np.where(land, _win(t, (-6.0, 2.0, 24.0, 32.0)) * _win(r, (120.0, 250.0, 900.0, 1300.0)) * _open(env, 20.0, 60.0)
                    * rough * _win(_elev(env), (-1.0, 0.0, 3500.0, 5000.0)), 0.0)


def wild_cattle(env, tags, land):
    """Aurochs-like cattle: moist grassland and open woodland, lowlands to foothills."""
    t, r = env["temperature"], env["precipitation"]
    return np.where(land, _win(t, (0.0, 8.0, 26.0, 31.0)) * _win(r, (450.0, 800.0, 2000.0, 2800.0)) * _open(env, 40.0, 75.0)
                    * _win(_elev(env), (-1.0, 0.0, 2500.0, 3500.0)), 0.0)


def wild_fowl(env, tags, land):
    """Junglefowl and wildfowl: warm wet forest edge and wetland (a forest-edge band of tree cover, wetlands)."""
    t, r = env["temperature"], env["precipitation"]
    tc = env.get("tree_cover", np.zeros(len(t)))
    edge = np.maximum(_win(tc, (5.0, 15.0, 70.0, 95.0)), np.where(tags["wetland"], 0.8, 0.0))
    return np.where(land, _win(t, (14.0, 22.0, 32.0, 38.0)) * _win(r, (800.0, 1500.0, 6000.0, 7000.0)) * edge, 0.0)


def wild_elk(env, tags, land):
    """(Fantasy) a great elk of the cold forest edge and the taiga: boreal temperatures, forest cover."""
    t, r = env["temperature"], env["precipitation"]
    tc = env.get("tree_cover", np.zeros(len(t)))
    return np.where(land, _win(t, (-20.0, -10.0, 8.0, 16.0)) * _win(r, (200.0, 400.0, 1500.0, 2500.0)) * _win(tc, (5.0, 20.0, 70.0, 95.0)), 0.0)


def wild_lizard(env, tags, land):
    """(Fantasy) a riding lizard of the hot dry and savanna country: warm, semi-arid to wet, little dense forest."""
    t, r = env["temperature"], env["precipitation"]
    return np.where(land, _win(t, (18.0, 24.0, 34.0, 42.0)) * _win(r, (200.0, 500.0, 2500.0, 3500.0)) * _open(env, 40.0, 80.0), 0.0)


def wild_pig(env, tags, land):
    """Wild boar: forest and woodland edge over most of Eurasia (Frantz 2019), temperate to tropical, not the driest or coldest
    land, below high mountains. The climate edges are JUDGEMENT (no numbers in the sources)."""
    t, r = env["temperature"], env["precipitation"]
    tc = env.get("tree_cover", np.zeros(len(t)))
    return np.where(land, _win(t, (-4.0, 3.0, 28.0, 34.0)) * _win(r, (250.0, 450.0, 3000.0, 4500.0)) * _win(tc, (3.0, 15.0, 90.0, 101.0))
                    * _win(_elev(env), (-1.0, 0.0, 2500.0, 3500.0)), 0.0)


def wild_reindeer(env, tags, land):
    """Reindeer: tundra and taiga, adapted for extreme cold (tundra herds on hard snow, forest herds in deep soft snow): mean annual
    temperature well below freezing to a little above (edges JUDGEMENT)."""
    t, r = env["temperature"], env["precipitation"]
    return np.where(land, _win(t, (-22.0, -15.0, -2.0, 4.0)) * _win(r, (80.0, 180.0, 1000.0, 1600.0)), 0.0)


def wild_camel(env, tags, land):
    """Camels, hot and cold: dromedaries in arid land with a long dry season (southern limit ~550 mm a year in the Sahel, sensitive
    to cold and damp), Bactrians in the cold deserts and steppe of Central Asia (coat good from -30 to 50 C). Open dry country."""
    t, r = env["temperature"], env["precipitation"]
    return np.where(land, _win(t, (-6.0, 0.0, 30.0, 36.0)) * _win(r, (10.0, 40.0, 350.0, 600.0)) * _open(env, 5.0, 25.0)
                    * _win(_elev(env), (-1.0, 0.0, 3000.0, 4200.0)), 0.0)


def wild_llama(env, tags, land):
    """Llamas and alpacas (guanaco and vicuna): the high Andean puna grassland, alpacas at 3500-5000 m: cold, open, high."""
    t, r = env["temperature"], env["precipitation"]
    return np.where(land, _win(_elev(env), (2600.0, 3400.0, 5000.0, 5600.0)) * _win(t, (-6.0, -1.0, 11.0, 15.0))
                    * _win(r, (100.0, 250.0, 1200.0, 1800.0)) * _open(env, 10.0, 40.0), 0.0)


def wild_buffalo(env, tags, land):
    """Water buffalo: hot and humid lowlands, wallowing in wet ground (both types 'well adapted to a hot and humid climate'; the swamp
    type follows rice). Wetlands count double."""
    t, r = env["temperature"], env["precipitation"]
    wet = np.where(tags["wetland"], 1.0, 0.7)
    return np.where(land, _win(t, (16.0, 21.0, 30.0, 34.0)) * _win(r, (700.0, 1100.0, 4000.0, 5500.0)) * wet
                    * _win(_elev(env), (-1.0, 0.0, 1200.0, 2000.0)), 0.0)


def wild_yak(env, tags, land):
    """Yak: the high plateau (Qinghai-Tibet, average 4200 m; pastures 3000-5000 m), heat exhaustion above about 15 C: cold, high, open."""
    t, r = env["temperature"], env["precipitation"]
    return np.where(land, _win(_elev(env), (2500.0, 3200.0, 5200.0, 5900.0)) * _win(t, (-14.0, -8.0, 4.0, 9.0))
                    * _win(r, (100.0, 200.0, 900.0, 1400.0)) * _open(env, 15.0, 45.0), 0.0)


@dataclass(frozen=True)
class Animal:
    id: str
    label: str  # plural, for events ("horses are tamed")
    noun: str  # singular, for stories ("the first to tame the horse")
    bit: int
    wild: Callable
    anchor_kyr: float  # Earth's date of the first taming (this run draws around it)
    size: int  # carried over the sea by: 0 canoes, 1 plank boats, 2 sailing ships
    tame: dict  # who tames it: weights on {farm, herd, forage} (a people's shares); the weighted sum must reach tame_min
    tame_min: float
    prop_floor: float  # a people's propensity to take it up: floor + sum of weights x its shares, within 0..1
    prop: dict
    front_kmyr: float  # the front of its use over peopled land
    excl: tuple = ()  # traits of peoples that never take it up (too big, too small, no ground...)
    uptake: str = "front"  # "front": its use creeps at front_kmyr; "contact" (a high-value mount, PW-794): peoples take it up at once on meeting, so the front moves at the contact speed (animals.CONTACT_KMYR) wherever the land suits it, and is held back by land that does not (dense forest, hot-wet tropics, high mountains: outside its wild range) and by open sea
    gap: float = 0.8  # pressure kept per unpeopled cell crossed
    again: float = 0.06  # per kyr per other landmass with tamers on the wild range and no use yet: taming again, on its own
    speed: float = 1.0  # x the people's spread at full adoption
    speed_open: bool = False  # ...only over open land (else everywhere)
    k: dict = field(default_factory=dict)  # capacity: x(1 + frac x adoption x share), keys herd (x grazing), forage, farm
    plough: tuple | None = None  # (kyr ago, frac): from then on an extra frac on the farm capacity (draft animals)
    herd_land: float = 0.0  # land-use: the land a herder works x(1 + this x adoption)
    crop_land: float = 0.0  # land-use: the land a farmer works x(1 + this x adoption) (the plough)
    dairy: bool = False  # milk peoples keep dairy herds of it
    fantasy: bool = False
    rare: float = 1.0  # fantasy rows: the chance a world has the taming at all
    plant: bool = False  # a crop row (crop_defs.TABLE, PW-721), not an animal: `wild` also takes a `widen` (the range it grows in)
    deed: str = "tamed"  # what the first people do with it, in events and stories ("tamed", "first cultivated")
    weight: float = 0.0  # crops: how much of a staple it is (the share of the cropland a known crop of this weight can feed; crop_defs)
    straw: float = 0.0  # crops: stalks and straw left on the fields, for fuel (fuels.py)


TABLE: tuple[Animal, ...] = (
    Animal("horse", "horses", "horse", 0, wild_horse, 4.2, 2, {"herd": 1.0}, 0.4, 0.15, {"herd": 0.85}, 1.8,
           excl=("flies", "swims", "subterranean"), uptake="contact", speed=2.5, speed_open=True, k={"herd": 0.3}, herd_land=0.5, dairy=True),
    Animal("dog", "dogs", "dog", 1, wild_dog, 15.0, 0, {"forage": 1.0}, 0.5, 0.6, {"forage": 0.4}, 3.0,
           excl=("flies", "swims", "subterranean"), gap=0.9, again=0.15, speed=1.15, k={"forage": 0.1}),
    Animal("caprine", "sheep and goats", "sheep and goat", 2, wild_caprine, 11.0, 1, {"farm": 1.0, "herd": 1.0}, 0.4, 0.1,
           {"farm": 0.6, "herd": 0.9}, 1.2, excl=("flies", "swims", "subterranean"), k={"herd": 0.15}, herd_land=0.3, dairy=True),
    Animal("cattle", "cattle", "cattle", 3, wild_cattle, 10.5, 2, {"farm": 1.0, "herd": 1.0}, 0.4, 0.1, {"farm": 0.6, "herd": 0.9}, 1.2,
           excl=("flies", "swims", "subterranean"), k={"herd": 0.15}, plough=(6.0, 0.1), herd_land=0.2, crop_land=0.25, dairy=True),
    Animal("fowl", "fowl", "fowl", 4, wild_fowl, 3.5, 0, {"farm": 1.0, "forage": 1.0}, 0.5, 0.5, {"farm": 0.5}, 1.5,
           excl=("swims", "subterranean"), k={"farm": 0.05, "forage": 0.05}),
    Animal("great_elk", "great elk", "great elk", 5, wild_elk, 6.0, 2, {"herd": 1.0, "forage": 1.0}, 0.5, 0.1, {"herd": 0.9}, 1.5,
           excl=("flies", "swims", "subterranean"), speed=1.5, fantasy=True, rare=0.3),
    Animal("riding_lizard", "riding lizards", "riding lizard", 6, wild_lizard, 5.0, 2, {"farm": 1.0, "herd": 1.0, "forage": 1.0}, 0.5, 0.3,
           {"herd": 0.7}, 1.5, excl=("flies", "swims", "subterranean"), speed=1.4, fantasy=True, rare=0.25),
    # PW-835: who tames and takes up each by way of life is JUDGEMENT after the existing rows (pigs: farmers and settled foragers, not
    # nomads; the cold and dry herds: herders, reindeer also hunters); pigs ride canoes (Lapita settlers brought dogs, pigs and jungle fowl, PMC428491)
    Animal("pig", "pigs", "pig", 7, wild_pig, 10.5, 0, {"farm": 1.0, "forage": 0.5}, 0.5, 0.1, {"farm": 0.8}, 1.2,
           excl=("flies", "swims", "subterranean"), k={"farm": 0.05}),
    Animal("reindeer", "reindeer", "reindeer", 8, wild_reindeer, 2.0, 1, {"herd": 1.0, "forage": 1.0}, 0.5, 0.1, {"herd": 0.9, "forage": 0.3}, 1.5,
           excl=("flies", "swims", "subterranean"), k={"herd": 0.1}, herd_land=0.2, dairy=True),
    Animal("camel", "camels", "camel", 9, wild_camel, 4.5, 2, {"herd": 1.0}, 0.4, 0.1, {"herd": 0.9}, 1.5,
           excl=("flies", "swims", "subterranean"), speed=1.3, speed_open=True, k={"herd": 0.1}, herd_land=0.3, dairy=True),
    Animal("llama", "llamas and alpacas", "llama", 10, wild_llama, 6.0, 1, {"herd": 1.0, "farm": 0.5}, 0.4, 0.1, {"herd": 0.9, "farm": 0.3}, 1.0,
           excl=("flies", "swims", "subterranean"), k={"herd": 0.1}, herd_land=0.2),
    Animal("buffalo", "water buffalo", "water buffalo", 11, wild_buffalo, 6.3, 2, {"farm": 1.0, "herd": 1.0}, 0.4, 0.1, {"farm": 0.7, "herd": 0.6}, 1.0,
           excl=("flies", "swims", "subterranean"), k={"herd": 0.1}, herd_land=0.2, crop_land=0.15, dairy=True),
    Animal("yak", "yaks", "yak", 12, wild_yak, 7.3, 2, {"herd": 1.0}, 0.4, 0.1, {"herd": 0.9}, 1.0,
           excl=("flies", "swims", "subterranean"), k={"herd": 0.1}, herd_land=0.2, dairy=True),
)
BY_ID = {a.id: a for a in TABLE}
IDS = tuple(a.id for a in TABLE)
REAL_IDS = tuple(a.id for a in TABLE if not a.fantasy)


# -- craft that carry animals over open sea, on a rough Earth timeline (PW-688 part 2) ----------------------------------
# (name, since kyr ago, reach km, biggest animal size carried, the sea share a people needs to man it). People themselves
# cross by the same craft (crossing.modes: canoes since CANOES_KYR over short gaps, voyaging since BOATS[3]); animals need a
# bigger boat than people: dogs, fowl and pigs ride in canoes and outriggers, sheep and goats need planked boats, horses and cattle
# a sailing ship. Before them only drift rafts, which carry no animals.
def craft_ladder() -> tuple[tuple, ...]:
    from . import spec as SP
    return (("raft or dugout", SP.RAFT_KYR, 120.0, -1, 0.1),  # (people only: no animal rides in one, PW-869)
            ("canoe or outrigger", SP.CANOES_KYR, 300.0, 0, 0.02),
            ("planked boat", SP.BOATS[3], 1500.0, 1, 0.2),
            ("sailing ship", SP.LATE_SEA_KYR, 2500.0, 2, 0.3))


def craft_for(size: int, ago_kyr: float):
    """The best craft (name, reach km, sea share needed) that carries an animal of that size at that time, or None."""
    best = None
    for name, since, reach, big, need in craft_ladder():
        if big >= size and ago_kyr <= since + 1e-9 and (best is None or reach > best[1]):
            best = (name, reach, need)
    return best


def craft_for_people(share: float, ago_kyr: float):
    """The best craft (name, reach km) a people with that sea share can man at that time, or None (PW-720: the same ladder as the
    animals'; a people needs the sea share of the craft and the craft must exist yet)."""
    best = None
    for name, since, reach, _, need in craft_ladder():
        if share >= need and ago_kyr <= since + 1e-9 and (best is None or reach > best[1]):
            best = (name, reach)
    return best


def resolve(ids, force, mode: str) -> list[Animal]:
    """The animals a tree has: `ids` (None: every real one) plus the forced ones, without the fantasy rows in the real mode."""
    on = list(REAL_IDS if ids is None else ids)
    for f in force:
        if f not in on:
            on.append(f)
    return [a for a in TABLE if a.id in on and not (a.fantasy and mode == "real")]
