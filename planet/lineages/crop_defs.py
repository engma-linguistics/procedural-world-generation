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

The regional foods (PW-765, rows 24-32) are cuisine rows too.
The first ten real rows are staples (weight > 0: they feed the cropland); rows 12-23 are the cuisine plants (PW-738): tree fruit and
nuts, olives, vines, oil seeds, coconut and oil palm, tropical spices, chili-like capsicum, cane sugar, sap sugar, tea and coffee,
cooking greens and alliums. They have `weight` 0 (no say in the cropland or the straw), a small `k` (a little farm capacity where they
grow: orchards, oil, sugar feed people) and mostly serve as a per-cell "crops known" list and wild range for the culinary brief.
Dry-summer plants (olive, vine) read the Koppen class (`climate=`).

Bit i of the stored `crop_known` / `crop_wild` layers (uint64 since the regional foods: 33 rows) is the crop with `bit` i here.
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


_DRY_SUMMER = (7, 8, 9)  # Koppen ids Csa, Csb, Csc: the Mediterranean classes (olive and vine country)


def _range(t, r, tree=(0.0, 100.0), elev=(-1.0, 0.0, 2800.0, 4200.0), flat=0.0, soil=0.4, climate=None):
    """A crop's range function. t, r: the ramps (rises, full from, full to, gone) of annual temperature (C) and rain (mm);
    tree: the tree cover (%) it tolerates (fully below the first value, gone at the second: clearing makes room);
    elev: the heights (m); flat: how much it needs flat wet lowland (0..1; rice); soil: the weight of the world's farmland;
    climate: (Koppen ids, floor): the share of the range kept outside those classes (floor 0: only in them; the wider grown range
    lets half the rest back in)."""
    def wild(env, tags, land, widen=0.0):
        el = np.maximum(env["elevation"] - env["ice"], 0)
        v = _winw(env["temperature"], t, widen) * _winw(env["precipitation"], r, widen) * _winw(el, elev, widen)
        v = v * (_open(env, *tree) if tree[1] < 100 else 1.0) * _soil(tags, soil)
        if climate is not None:
            ids, floor = climate
            v = v * (np.isin(env["climate"].astype(int), ids) + (floor + widen * 0.5 * (1.0 - floor)) * ~np.isin(env["climate"].astype(int), ids))
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
_EXCL = ("flies", "swims")  # (PW-1275 Q6 A, Q4 A: holds farm their valleys and den peoples may farm, rarely: lineages.ladder; was also subterranean)


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
    # the cuisine plants (PW-738): weight 0 and a small k; anchors are Earth's first cultivation, kyr ago
    _crop(12, "tree_fruit", "tree fruit and nuts", _range((3, 8, 22, 28), (400, 700, 2000, 3000), elev=(-1, 0, 2500, 3500)), 7.0, 1.0, 0.03, 0.0, 0.0,
          noun="fruit and nut tree"),
    _crop(13, "olive", "olives", _range((9, 14, 24, 30), (250, 350, 900, 1200), climate=(_DRY_SUMMER, 0.0)), 6.5, 0.9, 0.03, 0.0, 0.0, noun="olive"),
    _crop(14, "vine", "grapes and vines", _range((8, 12, 24, 30), (300, 450, 1100, 1500), climate=(_DRY_SUMMER, 0.45)), 8.0, 0.9, 0.03, 0.0, 0.0,
          noun="vine"),
    _crop(15, "oil_seeds", "oil seeds (sesame, flax, rape)", _range((6, 12, 28, 34), (250, 400, 1200, 1800), tree=(30, 70)), 6.0, 1.1, 0.02, 0.0, 0.0,
          noun="oil seed"),
    _crop(16, "coconut", "coconut and oil palm", _range((22, 25, 32, 37), (1200, 1800, 5000, 7000), elev=(-1, 0, 800, 1500)), 4.5, 0.7, 0.03, 0.0, 0.0,
          noun="coconut and oil palm"),
    _crop(17, "spice_tree", "pepper, cinnamon and other tropical spices", _range((21, 24, 31, 36), (1500, 2200, 5000, 7000), elev=(-1, 0, 1200, 2000)),
          3.5, 0.7, 0.01, 0.0, 0.0, noun="tropical spice"),
    _crop(18, "chili", "chili-like capsicum", _range((15, 20, 30, 36), (400, 700, 2000, 3000), elev=(-1, 0, 2600, 3600)), 6.0, 1.0, 0.01, 0.0, 0.0,
          noun="chili-like pepper"),
    _crop(19, "cane", "sugar cane", _range((19, 23, 32, 37), (1000, 1500, 3500, 5000), elev=(-1, 0, 1200, 2000)), 8.0, 0.8, 0.05, 0.0, 0.0,
          noun="sugar cane"),
    _crop(20, "sap_sugar", "sap sugar (maple and birch) and beet", _range((0, 4, 14, 20), (500, 700, 1600, 2200), elev=(-1, 0, 2000, 3000)), 1.0, 1.0, 0.01,
          0.0, 0.0, noun="sap sugar"),
    _crop(21, "tea", "tea, coffee and other infusions", _range((14, 18, 26, 31), (1200, 1700, 4000, 6000), elev=(-1, 300, 2200, 3200)), 3.0, 0.8, 0.0, 0.0, 0.0,
          noun="tea and coffee"),
    _crop(22, "greens", "cooking greens (brassicas, leeks)", _range((0, 5, 20, 26), (300, 500, 1800, 2500), elev=(-1, 0, 3000, 4000)), 5.0, 1.1, 0.02,
          0.0, 0.0, noun="cooking green"),
    _crop(23, "alliums", "onions and garlic", _range((2, 8, 26, 32), (200, 350, 1200, 1800), tree=(30, 70)), 6.0, 1.1, 0.0, 0.0, 0.0, noun="allium"),
    # the regionally restricted foods (PW-765): cuisine rows (weight 0) with their own wild range and homelands from the landmass draw, and a slow
    # front, so a world's cuisines differ by which of them grew where (Earth's New World foods, as plants of those climates on any world)
    _crop(24, "nightshade_fruit", "tomatoes and other nightshade fruits", _range((12, 17, 28, 33), (400, 700, 2200, 3200), elev=(-1, 0, 2600, 3600)), 5.0, 0.6,
          0.02, 0.0, 0.0, noun="tomato-like fruit"),
    _crop(25, "squash", "squash and gourds", _range((12, 17, 28, 34), (400, 650, 1800, 2600), tree=(30, 80), elev=(-1, 0, 2500, 3500)), 10.0, 0.7, 0.03,
          0.0, 0.0, noun="squash"),
    _crop(26, "beans", "common beans", _range((10, 15, 26, 32), (400, 650, 1600, 2400), tree=(30, 80), elev=(-1, 0, 3000, 4000)), 7.0, 0.7, 0.05,
          0.0, 0.0, noun="bean"),
    _crop(27, "cacao", "cacao", _range((21, 24, 30, 35), (1500, 2000, 4000, 6000), elev=(-1, 0, 600, 1200)), 5.3, 0.5, 0.01, 0.0, 0.0, noun="cacao"),
    _crop(28, "vanilla", "vanilla", _range((20, 23, 30, 35), (1500, 2000, 4000, 6000), elev=(-1, 0, 800, 1400)), 1.0, 0.4, 0.0, 0.0, 0.0, noun="vanilla"),
    _crop(29, "peanut", "peanuts", _range((16, 21, 30, 35), (400, 600, 1500, 2200), tree=(30, 80), elev=(-1, 0, 1500, 2500)), 7.6, 0.7, 0.03, 0.0, 0.0,
          noun="groundnut"),
    _crop(30, "sweet_potato", "sweet potatoes", _range((16, 21, 30, 35), (600, 900, 2500, 3500), elev=(-1, 0, 2200, 3200)), 5.0, 0.7, 0.05, 0.0, 0.0,
          noun="sweet potato"),
    _crop(31, "pseudograin", "quinoa and amaranth", _range((3, 8, 20, 26), (200, 350, 900, 1400), tree=(20, 60), elev=(-1, 100, 4000, 4800)), 7.0, 0.6,
          0.05, 0.0, 0.0, noun="quinoa and amaranth"),
    _crop(32, "avocado", "avocados", _range((14, 18, 28, 33), (700, 1100, 2500, 3500), elev=(-1, 0, 2300, 3300)), 5.5, 0.6, 0.02, 0.0, 0.0, noun="avocado"),
    _crop(10, "stonegrain", "stonegrain", _stonegrain, 6.0, 1.0, 0.12, 0.4, 0.6, fantasy=True, rare=0.3),
    _crop(11, "emberpod", "emberpods", _emberpod, 5.0, 1.0, 0.1, 0.3, 0.0, fantasy=True, rare=0.25, noun="emberpod"),
)
TABLE = tuple(sorted(TABLE, key=lambda a: a.bit))  # (TABLE[i] is the crop with bit i)
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
