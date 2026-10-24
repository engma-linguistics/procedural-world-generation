"""The staple crops as one table (PW-721), in the same row shape as the animals (`animal_defs.Animal`, `plant=True`).

No plants are simulated as species, so each crop's wild range is derived from the land (annual temperature and rain, tree
cover, height, flat wet ground, soil where the world has it) by a function of the epoch; nothing names Earth's continents,
so "wheat and barley" are the cool-temperate grain grasses of open dry ground on any world, "rice" the grain of warm wet
flats, "maize" the tall warm-season grain, and so on. A crop's row says: its wild range (`wild(env, tags, land, widen)`;
`widen` > 0 gives the wider range it can be *grown* in, past where it grew wild), the date it was first cultivated on Earth
(the anchor; each run draws its own around it), who first cultivates it (a people's farm share, plus gatherers of wild plants (the foraging use) on
the range: weights on {farm, gather}), who then takes it up, how fast its use spreads over peopled land (seed travels
easily: all crops go by canoe too, `size` 0), what it does (`k["farm"]`: the farm capacity it adds where it is known and
grows; `weight`: how much of a staple it is for the cropland in landuse.py) and what it leaves (`straw`, fuels.py).
Several homelands per world come from the landmass draw (animals.HOME_PENALTY: a landmass that already has a first
cultivation is less likely to get another), as the Fertile Crescent, China, Mesoamerica, the Andes, the Sahel and New
Guinea each had their own. `fantasy` rows are plants Earth never farmed: rare when on, certain when forced
(`meta.crops_force`), and dropped in the real-world mode (PW-695), like the fantasy animals.

Bit i of the stored `crop_known` / `crop_wild` layers (uint16) is the crop with `bit` i here.
"""

from __future__ import annotations

import numpy as np

from .animal_defs import Animal, _open, _win


def _winw(x, e, w):
    """`_win` with the ramps pushed outward by `w` of their width (the range a crop can be grown in, past the wild one)."""
    a, b, c, d = e
    return _win(x, (a - w * (b - a), b - w * (b - a), c + w * (d - c), d + w * (d - c)))


def _soil(tags, w):
    s = tags.get("soil")
    return 1.0 if s is None or w <= 0 else (1.0 - w) + w * np.clip(s / 0.45, 0, 1)


def _range(t, r, tree=(0.0, 100.0), elev=(-1.0, 0.0, 2800.0, 4200.0), flat=0.0, soil=0.4):
    """A crop's range function. t, r: the ramps (rises, full from, full to, gone) of annual temperature (C) and rain (mm);
    tree: the tree cover (%) it tolerates (fully below the first value, gone at the second: clearing makes room);
    elev: the heights (m); flat: how much it needs flat wet lowland (0..1; rice); soil: the weight of the world's farmland."""
    def wild(env, tags, land, widen=0.0):
        el = np.maximum(env["elevation"] - env["ice"], 0)
        v = _winw(env["temperature"], t, widen) * _winw(env["precipitation"], r, widen) * _winw(el, elev, widen)
        v = v * (_open(env, *tree) if tree[1] < 100 else 1.0) * _soil(tags, soil)
        if flat > 0:
            low = np.maximum(tags["wetland"] * 1.0, 0.55 * _win(el, (-1.0, 0.0, 600.0, 1500.0)))
            v = v * ((1.0 - flat) + flat * low)
        return np.where(land, v, 0.0)
    return wild


def _stonegrain(env, tags, land, widen=0.0):
    """(Fantasy) a hardy grain of high cold ground: the uplands and high steppe, cold, dry to moist."""
    el = np.maximum(env["elevation"] - env["ice"], 0)
    return np.where(land, _winw(env["temperature"], (-14.0, -6.0, 6.0, 12.0), widen) * _winw(env["precipitation"], (150.0, 300.0, 1200.0, 1800.0), widen)
                    * _winw(el, (1000.0, 2000.0, 5500.0, 7000.0), widen) * _soil(tags, 0.2), 0.0)


def _emberpod(env, tags, land, widen=0.0):
    """(Fantasy) a fiery pod of warm, wet, young volcanic ground (and the hills beside it)."""
    ground = np.maximum(tags["volcanic"] * 1.0, 0.4 * tags["hills"])
    return np.where(land, _winw(env["temperature"], (16.0, 22.0, 34.0, 40.0), widen) * _winw(env["precipitation"], (500.0, 900.0, 3000.0, 4000.0), widen)
                    * np.maximum(ground, 0.5 * widen), 0.0)


_FARM = {"farm": 1.0, "gather": 0.5}  # first cultivated by farmers, or by gatherers of wild plants (the foraging use) on the range
_PROP = {"farm": 0.9, "gather": 0.15}
_EXCL = ("flies", "swims", "subterranean")


def _crop(i, id_, label, wild, anchor, front, k, weight, straw, **kw):
    return Animal(id_, label, kw.pop("noun", label), i, wild, anchor, 0, _FARM, 0.4, 0.1, _PROP, front, excl=_EXCL, gap=0.7, again=0.03,
                  k={"farm": k}, plant=True, deed="first cultivated", weight=weight, straw=straw, **kw)


TABLE: tuple[Animal, ...] = (
    _crop(0, "wheat", "wheat and barley", _range((0, 6, 22, 28), (200, 350, 1100, 1600), tree=(30, 70)), 10.5, 1.1, 0.22, 0.7, 1.0),
    _crop(1, "pulses", "lentils and peas", _range((2, 8, 22, 28), (200, 350, 1000, 1500), tree=(30, 70)), 10.0, 1.1, 0.06, 0.3, 0.4,
          noun="lentil and pea"),
    _crop(2, "foxtail_millet", "foxtail millet", _range((2, 8, 20, 27), (150, 300, 800, 1200), tree=(20, 60)), 10.0, 1.2, 0.12, 0.5, 0.7,
          noun="foxtail millet"),
    _crop(3, "rice", "rice", _range((16, 22, 32, 37), (900, 1400, 5000, 7000), tree=(60, 95), elev=(-1, 0, 1000, 2000), flat=0.8), 9.0, 0.9, 0.35, 0.8, 0.9),
    _crop(4, "sorghum", "sorghum and pearl millet", _range((18, 23, 32, 38), (250, 400, 1000, 1500), tree=(30, 80)), 5.5, 1.2, 0.15, 0.6, 0.9,
          noun="sorghum and pearl millet"),
    _crop(5, "maize", "maize", _range((14, 19, 28, 34), (400, 700, 1800, 2500), tree=(30, 80), elev=(-1, 0, 3000, 4200)), 9.0, 1.0, 0.25, 0.7, 0.8),
    _crop(6, "potato", "potatoes and other cool tubers", _range((1, 5, 16, 22), (400, 600, 1600, 2200), elev=(-1, 200, 4000, 4800)), 8.0, 0.8, 0.25, 0.6, 0.1,
          noun="potato-like tuber"),
    _crop(7, "roots", "yams, taro and cassava", _range((20, 24, 32, 37), (900, 1400, 5000, 7000), elev=(-1, 0, 1500, 2500)), 7.5, 0.8, 0.2, 0.6, 0.1,
          noun="yam, taro and cassava"),
    _crop(8, "banana", "bananas and plantains", _range((21, 25, 32, 37), (1200, 1800, 5000, 7000), elev=(-1, 0, 1500, 2500)), 7.0, 0.8, 0.15, 0.4, 0.2,
          noun="banana"),
    _crop(9, "rye", "rye and oats", _range((-4, 2, 12, 18), (300, 450, 1000, 1500), tree=(20, 60)), 3.5, 1.5, 0.08, 0.4, 1.0, noun="rye and oats"),
    _crop(10, "stonegrain", "stonegrain", _stonegrain, 6.0, 1.0, 0.12, 0.4, 0.6, fantasy=True, rare=0.3),
    _crop(11, "emberpod", "emberpods", _emberpod, 5.0, 1.0, 0.1, 0.3, 0.0, fantasy=True, rare=0.25, noun="emberpod"),
)
BY_ID = {a.id: a for a in TABLE}
IDS = tuple(a.id for a in TABLE)
REAL_IDS = tuple(a.id for a in TABLE if not a.fantasy)


def resolve(ids, force, mode: str) -> list[Animal]:
    """The crops a tree has: `ids` (None: every real one) plus the forced ones, without the fantasy rows in the real mode."""
    on = list(REAL_IDS if ids is None else ids)
    for f in force:
        if f not in on:
            on.append(f)
    return [a for a in TABLE if a.id in on and not (a.fantasy and mode == "real")]
