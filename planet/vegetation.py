"""Vegetation: plant functional types, their productivity, competition and
fire, and the named vegetation types made from them (PW-187; the design is
docs/proposals/vegetation.md, with the owner's decisions in its section 9.3).

The state is, per land cell, the cover fraction of each of 19 plant
functional types (PFTs: groups of plants that behave alike, such as
"boreal needleleaf evergreen tree" or "C4 grass"). Everything else is
derived from it.

How a cell's mix is found (equilibrium):
1. Months. The climate's twelve months (climate.months: temperature, rain
   and snowmelt, potential evaporation, light), plus the indices that set
   where each PFT can live (its envelope): coldest month, an estimated
   absolute minimum (BIOME4's fit), degree-days above 5 C, warmest month.
2. Productivity, per PFT as if it grew alone (potential NPP): a
   light-use-efficiency scheme (CASA / MODIS MOD17), month by month:
   GPP = efficiency x light caught by the leaves (Beer's law) x a
   temperature hump x a water-stress factor. Water comes from a two-layer
   soil bucket (topsoil 0-0.3 m, subsoil to 1.5 m) that the plant draws
   from by its root shares: grasses mostly from the top, trees from both
   (Walter's explanation of tree-grass coexistence). NPP = 75% of what is
   left after maintenance respiration (Q10 = 2). The leaf area index (LAI)
   is the one that maximises NPP net of leaf turnover (as BIOME4): more
   leaf catches more light, but costs carbon and dries the soil.
3. Competition (TRIFFID, the UK Met Office's vegetation model):
   Lotka-Volterra cover dynamics in which taller types shade shorter ones,
   types of one height share space (similar ones coexist, a clearly
   better one takes over), each spreads at its net NPP over the carbon a
   square metre of it costs (grass fills a gap in a year, forest in a
   century), and dies back at a background rate plus fire.
4. Fire (GlobFIRM, LPJ's fire module): the burned share per year rises
   steeply with the length of the dry season, if there is fuel (fine
   litter, mostly from grass) and lightning. Each type loses the burned
   share x (1 - its resistance). Grass fuels fire and fire keeps trees out,
   while closed forest is too damp to burn: forest and savanna are both
   stable over a wide range of rain, and history decides (warm starts).
5. Wetlands: the flooded share of a cell (floodplains of big rivers, flat
   wet ground, permafrost flats, lake shores) belongs to the wetland types
   (reeds and sedges, peat moss) and to flood-tolerant trees; dryland
   types are kept off it.
6. Named types: a fixed order of rules on the mix, its structure and the
   site (classify): 56 vegetated types plus ice, rock, barren desert and
   lake. `biome` (climate.BIOMES) is now a coarse grouping of them.

In a run (decision 5) the same model runs cheaply at every climate update,
warm-started from the last one, and its ground cover and productivity feed
erosion and rock weathering (tectonics/earth.py). Plant groups appear one
after another during the run (decision 3; GROUPS, flora_update).
"""

from __future__ import annotations

import numpy as np
from numba import njit, prange

from . import climate
from .geo import R_KM

# ---------------------------------------------------------------------------
# Plant functional types
# ---------------------------------------------------------------------------
EVERGREEN, SUMMERGREEN, RAINGREEN, HERBAL = 0, 1, 2, 3  # leaf habit (HERBAL: warm enough and wet enough)
GROUND, HERB, SHRUB, TREE = 0, 1, 2, 3  # height class

# Starting values from LPJ (Sitch et al. 2003), BIOME4 (Kaplan et al. 2003)
# and TRIFFID (Cox 2001); all are tuning knobs. Columns:
#   code, name, colour, group (GROUPS), height class, leaf habit, on: leaf-on
#   threshold (C for summergreen and herbal, topsoil water share for raingreen)
#   envelope: tc_min, tc_max (coldest month, C), tmin (absolute minimum, C),
#     gdd (degree-days above 5 C), tw (warmest month, C), amin (drought
#     tolerance: least growing-season water-stress ratio AET/demand)
#   top: share of roots in the topsoil; eps: light-use efficiency, g C per MJ
#     of absorbed light; temp: growth zero / full from / full to / zero (C)
#   laimax; lma: g C of leaf per unit LAI; tleaf: leaf life, yr; rl, rw:
#     maintenance respiration of leaves (per LAI) and wood, g C/m2/month at 20 C;
#     kt: transpiration per light caught (C4 and CAM save water)
#   wet: lives only on flooded ground; flood: tolerance of flooding (0..1)
#   carbon: g C per m2 to establish full cover; gamma: background
#     mortality /yr; resist: share surviving a fire; hmax: height, m;
#     litf: share of NPP that becomes fine (burnable) litter; tau: years the
#     standing carbon lasts (biomass = NPP x tau)
_COLS = ("code", "name", "color", "group", "cls", "phen", "on", "tc_min", "tc_max", "tmin", "gdd", "tw", "amin",
         "top", "eps", "temp", "laimax", "lma", "tleaf", "rl", "rw", "kt", "wet", "flood", "carbon", "gamma",
         "resist", "hmax", "litf", "tau")
_NO = -99.0
_ROWS = [
    ("TrBE", "tropical broadleaf evergreen tree", "#1f6b2a", 4, TREE, EVERGREEN, 0, 15.5, 99, _NO, 0, _NO, 0.70,
     0.35, 1.10, (2, 20, 32, 42), 7.0, 40, 2, 7.4, 40, 1.0, 0, 0.5, 15000, 0.010, 0.10, 40, 0.30, 15),
    ("TrBR", "tropical broadleaf raingreen tree", "#7aa83a", 4, TREE, RAINGREEN, 0.35, 15.5, 99, _NO, 0, _NO, 0.35,
     0.40, 1.10, (2, 20, 32, 42), 6.0, 33, 1, 7.4, 30, 1.0, 0, 0.2, 10000, 0.012, 0.85, 25, 0.35, 12),
    ("TeBE", "temperate broadleaf evergreen tree", "#3d8a5a", 4, TREE, EVERGREEN, 0, 3.0, 18.8, -15, 1200, _NO, 0.40,
     0.40, 1.05, (-1, 14, 28, 38), 6.0, 50, 2, 7.0, 35, 1.0, 0, 0.3, 12000, 0.010, 0.60, 35, 0.30, 15),
    ("TeBS", "temperate broadleaf summergreen tree", "#5fa04a", 4, TREE, SUMMERGREEN, 5, -17, 15.5, _NO, 1200, _NO,
     0.50, 0.40, 1.05, (-1, 14, 27, 38), 6.0, 33, 1, 7.0, 35, 1.0, 0, 0.5, 12000, 0.010, 0.30, 35, 0.35, 15),
    ("TeNE", "temperate needleleaf evergreen tree", "#2d6e60", 3, TREE, EVERGREEN, 0, -2, 22, _NO, 900, _NO, 0.30,
     0.35, 1.00, (-3, 12, 26, 38), 5.5, 100, 3, 6.0, 35, 1.0, 0, 0.2, 13000, 0.008, 0.60, 50, 0.30, 18),
    ("BoNE", "boreal needleleaf evergreen tree", "#25503f", 3, TREE, EVERGREEN, 0, -32.5, -2, _NO, 600, _NO, 0.45,
     0.60, 1.00, (-4, 10, 22, 34), 5.0, 100, 4, 6.0, 30, 1.0, 0, 0.5, 8000, 0.008, 0.10, 25, 0.30, 20),
    ("BoNS", "boreal needleleaf summergreen tree", "#9c9a3a", 3, TREE, SUMMERGREEN, 3, _NO, -2, _NO, 350, _NO, 0.35,
     0.70, 1.00, (-4, 10, 22, 34), 4.0, 50, 1, 6.0, 25, 1.0, 0, 0.3, 6000, 0.010, 0.40, 20, 0.30, 20),
    ("BoBS", "boreal broadleaf summergreen tree", "#9ccf6a", 4, TREE, SUMMERGREEN, 5, _NO, 5, _NO, 350, _NO, 0.45,
     0.60, 1.05, (-3, 11, 24, 35), 4.5, 33, 1, 6.0, 25, 1.0, 0, 0.4, 5000, 0.030, 0.05, 20, 0.35, 12),
    ("SclS", "sclerophyll evergreen shrub", "#8a7d3a", 4, SHRUB, EVERGREEN, 0, -5, 18, _NO, 1500, _NO, 0.20,
     0.30, 0.90, (0, 15, 30, 42), 3.5, 80, 2, 5.0, 12, 1.0, 0, 0.0, 3000, 0.030, 0.80, 4, 0.40, 8),
    ("XerS", "xeric (desert) shrub", "#c2a970", 4, SHRUB, RAINGREEN, 0.10, -35, 99, _NO, 500, _NO, 0.05,
     0.35, 0.80, (-2, 15, 32, 45), 2.0, 60, 1, 4.0, 6, 0.8, 0, 0.0, 1500, 0.040, 0.60, 2, 0.40, 8),
    ("DecS", "cold-deciduous shrub", "#a4b06a", 4, SHRUB, SUMMERGREEN, 3, _NO, 5, _NO, 150, _NO, 0.35,
     0.60, 0.95, (-4, 8, 20, 32), 3.0, 33, 1, 5.0, 8, 1.0, 0, 0.5, 1500, 0.040, 0.80, 3, 0.40, 8),
    ("HthS", "evergreen dwarf heath shrub", "#8e6a8a", 4, SHRUB, EVERGREEN, 0, -35, 10, _NO, 100, _NO, 0.50,
     0.80, 0.80, (-4, 8, 20, 30), 2.0, 70, 2, 4.0, 3, 1.0, 0, 0.4, 800, 0.050, 0.70, 1, 0.40, 6),
    ("C4G", "C4 grass", "#d8c24a", 6, HERB, HERBAL, 10, _NO, 99, _NO, 0, 22, 0.10,
     0.85, 1.20, (10, 25, 38, 50), 4.0, 25, 1, 4.0, 0, 0.7, 0, 0.3, 300, 0.10, 0.95, 2, 0.90, 1),
    ("C3G", "C3 grass and forbs", "#b5c86a", 5, HERB, HERBAL, 0, _NO, 15.5, _NO, 200, _NO, 0.15,
     0.80, 1.10, (-2, 12, 25, 38), 4.0, 25, 1, 4.0, 0, 1.0, 0, 0.3, 300, 0.10, 0.95, 1, 0.90, 1),
    ("TunH", "tundra graminoids and forbs", "#a9b59a", 5, HERB, SUMMERGREEN, 0, _NO, 5, _NO, 50, _NO, 0.25,
     0.95, 1.00, (-4, 6, 18, 30), 2.5, 25, 1, 3.0, 0, 1.0, 0, 0.6, 200, 0.10, 0.90, 0.3, 0.80, 1),
    ("Succ", "succulents (CAM)", "#c98a5a", 6, SHRUB, EVERGREEN, 0, 0, 99, -10, 2000, _NO, 0.02,
     0.90, 0.35, (5, 20, 38, 50), 1.0, 150, 3, 2.0, 3, 0.25, 0, 0.0, 2000, 0.020, 0.10, 5, 0.10, 15),
    ("Moss", "moss, lichen and soil crust", "#b8b8a0", 1, GROUND, EVERGREEN, 0, _NO, 99, _NO, 0, _NO, 0.0,
     1.00, 0.40, (-5, 5, 20, 35), 1.5, 30, 3, 1.5, 0, 0.5, 0, 0.6, 150, 0.050, 0.20, 0.05, 0.50, 3),
    ("WetH", "wetland emergent herbs", "#4fa39a", 2, HERB, SUMMERGREEN, 5, _NO, 99, _NO, 100, _NO, 0.0,
     0.90, 1.20, (0, 15, 32, 45), 5.0, 30, 1, 5.0, 0, 1.0, 1, 1.0, 600, 0.10, 0.80, 3, 0.60, 1),
    ("Sph", "peat moss", "#7a5a3a", 1, GROUND, EVERGREEN, 0, _NO, 18, _NO, 50, _NO, 0.0,
     1.00, 0.50, (-4, 8, 20, 30), 2.0, 30, 3, 1.5, 0, 0.5, 1, 1.0, 300, 0.020, 0.30, 0.1, 0.50, 5),
]
PFTS = [dict(zip(_COLS, r)) for r in _ROWS]
# water-use efficiency, g C of GPP per mm transpired in moderately humid air
# (C4 and CAM plants waste less water), and the warmest month above which a
# type can't hold its own (heath: cool summers)
_TUNE = {  # (tuned on Earth with tools/veg_check.py; overrides of the table above)
    "TeNE": dict(eps=0.95, gamma=0.005), "BoNS": dict(eps=0.95, lma=35),
    "XerS": dict(eps=0.45, laimax=1.5, carbon=2500, gamma=0.05), "Succ": dict(eps=0.3, gamma=0.04, carbon=3000), "TrBE": dict(gamma=0.005),
    "TrBR": dict(eps=1.0, carbon=13000, gamma=0.008, resist=0.93), "TeBE": dict(gamma=0.006), "BoNE": dict(gamma=0.005, carbon=10000),
    "TeBS": dict(eps=1.15, gamma=0.005, carbon=11000),
}
PIONEERS = ("BoBS", "BoNS")  # light-hungry trees that shade-tolerant ones crowd out (birch, aspen, larch)
for _p in PFTS:
    _p.update(_TUNE.get(_p["code"], {}))
    _p["wue"] = {"C4G": 4.0, "Succ": 4.0}.get(_p["code"], 3.0)
    _p["tw_max"] = {"HthS": 20.0, "DecS": 20.0, "TunH": 18.0}.get(_p["code"], 99.0)
    # mm/yr: succulents need rain (or fog) most years; the hyper-arid cores of deserts are barren
    _p["p_min"] = {"Succ": 100.0}.get(_p["code"], 0.0)
CODES = [p["code"] for p in PFTS]
NP = len(PFTS)
IDX = {c: i for i, c in enumerate(CODES)}
TREES = np.array([p["cls"] == TREE for p in PFTS])
SHRUBS = np.array([p["cls"] == SHRUB for p in PFTS])
HERBS = np.array([p["cls"] == HERB for p in PFTS])
GROUNDS = np.array([p["cls"] == GROUND for p in PFTS])


def _col(k):
    return np.array([p[k] for p in PFTS], float)


# the per-PFT numbers the kernels read, one row per PFT (column order: _K_*)
_K_COLS = ("eps", "t0", "t1", "t2", "t3", "amin", "top", "phen", "on", "rl", "rw", "lma", "tleaf", "kt", "wet",
           "laimax", "wue")
EPS_SCALE = 0.8  # all efficiencies (tuned: Earth's land NPP)
_KP = np.stack([EPS_SCALE * _col("eps"), *(np.array([p["temp"][j] for p in PFTS], float) for j in range(4)), _col("amin"),
                _col("top"), _col("phen"), _col("on"), _col("rl"), _col("rw"), _col("lma"), _col("tleaf"),
                _col("kt"), _col("wet"), _col("laimax"), _col("wue")], 1)
C4 = IDX["C4G"]
C3_PFTS = np.array([p["code"] not in ("C4G", "Succ") for p in PFTS])

# ---------------------------------------------------------------------------
# Plant groups that appear during a run (decision 3)
# ---------------------------------------------------------------------------
# (name, PFTs it unlocks, when it appeared on Earth as a share of the ~470 Myr since land plants)
GROUPS = [
    ("pioneers: mosses, lichens, soil crusts", ("Moss", "Sph"), 0.0),
    ("early vascular marsh plants", ("WetH",), 0.08),
    ("forests without flowers: spore trees, seed ferns, conifers", ("TeNE", "BoNE", "BoNS"), 0.2),
    ("flowering trees and shrubs", ("TrBE", "TrBR", "TeBE", "TeBS", "BoBS", "SclS", "XerS", "DecS", "HthS"), 0.73),
    ("grasses and sedges", ("C3G", "TunH"), 0.85),
    ("C4 grasses and succulents (CAM)", ("C4G", "Succ"), 0.94),
]
# Before its group exists, a PFT's niche is filled by the first available
# PFT on its list, with that PFT's limits widened to cover it and its
# efficiency reduced (STANDIN_EFF): conifer-like forest in the tropics before
# flowering trees, moss and crust where grass would be.
STANDINS = {
    "TrBE": ("TeNE", "Moss"), "TrBR": ("TeNE", "Moss"), "TeBE": ("TeNE", "Moss"), "TeBS": ("TeNE", "Moss"),
    "BoBS": ("BoNE", "Moss"), "SclS": ("TeNE", "Moss"), "XerS": ("Moss",), "DecS": ("BoNS", "Moss"),
    "HthS": ("Moss",), "C3G": ("Moss",), "TunH": ("Moss",), "C4G": ("C3G", "Moss"), "Succ": ("XerS", "Moss"),
    "TeNE": ("Moss",), "BoNE": ("Moss",), "BoNS": ("BoNE", "Moss"), "WetH": ("Moss",), "Sph": ("Moss",),
}
STANDIN_EFF = 0.7


def all_unlocked() -> np.ndarray:
    return np.ones(NP, bool)


def unlocked_at(times, t: float) -> np.ndarray:
    """Which PFTs exist at time t (Myr), given each group's appearance time
    (None/NaN: not yet)."""
    ok = np.zeros(NP, bool)
    for (_, codes, _), tg in zip(GROUPS, times):
        if tg is not None and np.isfinite(tg) and tg <= t + 1e-9:
            ok[[IDX[c] for c in codes]] = True
    return ok


def standin_map(unlocked: np.ndarray) -> np.ndarray:
    """(NP, NP) bool: [p, q] = PFT p stands in for locked PFT q."""
    out = np.zeros((NP, NP), bool)
    for q, code in enumerate(CODES):
        if unlocked[q]:
            continue
        for s in STANDINS.get(code, ()):
            if unlocked[IDX[s]]:
                out[IDX[s], q] = True
                break
    return out


def group_windows(plants_from: float, end: float) -> list[tuple[float, float]]:
    """(earliest, latest) appearance time (Myr) of each group: from 0.6x to
    1.3x its Earth fraction of the span from plants_from to the hard
    deadline D = end - max(16 Myr, 5% of the span), every group by D."""
    span = max(end - plants_from, 1e-6)
    d = end - max(16.0, 0.05 * span)
    s = max(d - plants_from, 0.0)
    return [(plants_from + 0.6 * f * s, min(plants_from + 1.3 * f * s, d)) if f > 0 else (plants_from, plants_from)
            for _, _, f in GROUPS]


# ---------------------------------------------------------------------------
# Named vegetation types (section 2.3 of the proposal)
# ---------------------------------------------------------------------------
# id, name, group, colour, BIOMES id (the coarse grouping), game-facing line
TYPES = [
    (0, "sea", "sea", "#1d3f6e", 1, ""),
    (1, "tropical lowland rainforest", "tropical forest", "#0f5a1e", 14,
     "Towering three-layer canopy 40 m up, dim and humid at ground level; vines, buttress roots, endless insects. Slow going, few sightlines."),
    (2, "tropical montane cloud forest", "tropical forest", "#2f7a5a", 14,
     "Gnarled, moss-draped trees in near-constant fog on tropical mountains; epiphytes, orchids, dripping wet."),
    (3, "tropical monsoon (semi-evergreen) forest", "tropical forest", "#3c7f22", 13,
     "Tall forest that partly drops its leaves in the dry season; teak and sal, bamboo thickets."),
    (4, "tropical dry deciduous forest", "tropical forest", "#6f8f25", 13,
     "Leafless and dusty in the dry season, green and dense in the rains."),
    (5, "tropical swamp forest", "tropical forest", "#1e6e58", 14,
     "Flooded forest along big rivers; travel by boat for half the year."),
    (6, "tropical peat swamp forest", "tropical forest", "#3a5a3a", 14,
     "Forest on metres of black peat; tea-coloured water, smouldering fires in drought years."),
    (7, "tropical thorn woodland", "tropical woodland", "#a8963a", 12,
     "Low, spiny, drought-deciduous scrub-forest; acacia, cactus-like euphorbias."),
    (8, "moist savanna woodland", "savanna", "#8fa335", 12,
     "Open woodland over tall grass (miombo, cerrado); burns most years, so the trees have thick bark."),
    (9, "dry savanna", "savanna", "#c4b44a", 12,
     "Scattered flat-topped trees in a sea of grass; big herds and their predators."),
    (10, "tropical grassland", "savanna", "#d7c661", 12,
     "Open tall-grass plains to the horizon, burned and regrown each year."),
    (11, "seasonally flooded grassland", "savanna", "#8fbf8a", 12,
     "Vast flats that become shallow lakes each wet season; birds, caimans, cattle-country."),
    (12, "tropical alpine (paramo)", "alpine", "#9fae7a", 5,
     "Cold, misty grassland with giant rosette plants; frost every night, sun every day."),
    (13, "succulent desert", "desert", "#d49a6a", 11,
     "Columnar cacti or tree-aloes over bare stony ground; fog or rare rain."),
    (14, "hot desert scrub", "desert", "#e2c68e", 11,
     "Creosote-bush or saltbush spaced metres apart on gravel; water is everything."),
    (15, "semi-desert grassland", "desert", "#dccf8a", 8,
     "Bunchgrass and scattered shrubs; good grazing after rain, nothing in drought."),
    (16, "cold desert scrub", "desert", "#c9bea0", 7,
     "Grey-green aromatic shrubland on high plateaus; snow in winter, dust in summer."),
    (17, "salt desert scrub", "desert", "#d8d2b8", 11,
     "Succulent saltbushes around white salt flats; brackish water only."),
    (18, "oasis / desert riparian woodland", "desert", "#5f9a4a", 11,
     "A green ribbon of poplars, tamarisk or date palms along a desert river; the only shade for days."),
    (19, "Mediterranean scrub (maquis, chaparral, fynbos)", "Mediterranean", "#9a8a3a", 8,
     "Dense, aromatic, head-high evergreen thicket; summer fire season, spring flowers."),
    (20, "Mediterranean evergreen woodland", "Mediterranean", "#8a9a4a", 9,
     "Open stands of evergreen oak or olive over golden summer grass."),
    (21, "Mediterranean pine forest", "Mediterranean", "#5a7a4a", 9,
     "Resinous pinewoods on rocky hills; dry needles underfoot, fire-prone."),
    (22, "warm temperate evergreen (laurel) forest", "warm temperate", "#2f7f4a", 9,
     "Glossy-leaved evergreen broadleaf forest, misty and lush; camphor, laurel, magnolia."),
    (23, "warm temperate mixed forest", "warm temperate", "#4f8f3f", 9,
     "Varied forest of evergreen and deciduous trees; rich in nuts, fruit and game."),
    (24, "warm temperate pine forest", "warm temperate", "#6a8f5a", 9,
     "Open, park-like pine forest over grass, kept open by frequent low fires."),
    (25, "temperate rainforest", "temperate forest", "#1f5f4a", 10,
     "Giant conifers (or southern beeches) dripping with moss; fallen logs everywhere; the biggest timber on the planet."),
    (26, "temperate deciduous forest", "temperate forest", "#5a9a3a", 9,
     "Oak, beech and maple; bare in winter, a blaze of colour in autumn."),
    (27, "temperate mixed forest", "temperate forest", "#3f7f45", 9,
     "Broadleaves and conifers together; good hunting, good timber."),
    (28, "temperate conifer forest", "temperate forest", "#3a6a55", 9,
     "Dry, open conifer forest of the mountains and plateaus; ponderosa-like pines, fir higher up."),
    (29, "montane conifer forest", "temperate forest", "#2f5a50", 9,
     "Dark fir and spruce on the upper slopes of warm-climate mountains."),
    (30, "temperate woodland and parkland", "temperate woodland", "#8aae5a", 9,
     "Open woods and glades; easy travel, good pasture, scattered great trees."),
    (31, "tall-grass prairie", "temperate grassland", "#b9c46a", 8,
     "Shoulder-high grass and flowers on deep black soil; fire every few years."),
    (32, "short-grass steppe", "temperate grassland", "#cfc98a", 8,
     "Short, tough grass under a huge sky; horse country, dust storms."),
    (33, "shrub steppe", "temperate grassland", "#bdb78f", 8,
     "Grass and wormwood or sagebrush; harsh winters."),
    (34, "forest steppe", "temperate woodland", "#9fb86a", 8,
     "Islands of birch or oak in a grassland sea, at the forest's dry edge."),
    (35, "heathland and moorland", "temperate shrubland", "#9a7a9a", 8,
     "Purple heather and wind; bog pools in hollows; sheep and grouse."),
    (36, "temperate scrub and thicket", "temperate shrubland", "#8f9a5a", 8,
     "Bramble, hazel and thornbush; tough going off the paths."),
    (37, "boreal spruce-fir taiga", "boreal forest", "#2a4f3a", 6,
     "Dark, endless spruce forest over moss; mosquitoes in summer, deep snow in winter."),
    (38, "boreal larch taiga", "boreal forest", "#8a8a3f", 6,
     "Sparse larch that turns gold and drops its needles; the coldest forest on the planet."),
    (39, "boreal birch-aspen forest", "boreal forest", "#7fae6a", 6,
     "Bright, white-trunked forest regrowing after a fire; spruce coming up underneath."),
    (40, "boreal mixed forest", "boreal forest", "#3f6a45", 6,
     "Spruce and fir with birch, aspen and the odd lime or oak at the southern edge."),
    (41, "lichen woodland", "boreal woodland", "#8f9f85", 6,
     "Widely spaced spruce on a pale carpet of reindeer lichen; caribou winter range."),
    (42, "forest-tundra", "boreal woodland", "#7f8f6a", 5,
     "The treeline: stunted trees in sheltered hollows, tundra between."),
    (43, "shrub tundra", "tundra", "#9aa56a", 5,
     "Knee- to head-high willow and dwarf birch; thick, wet going in summer."),
    (44, "tussock and sedge tundra", "tundra", "#a8b08f", 5,
     "Ankle-breaking tussocks and wet sedge meadows over permafrost; birds by the million in summer."),
    (45, "dwarf-shrub and lichen tundra", "tundra", "#b5aa9a", 5,
     "Low heath and lichen; dry walking, wide views."),
    (46, "polar desert and fellfield", "tundra", "#c8c4bc", 7,
     "Frost-shattered stones with scattered moss and cushion plants; nearly lifeless."),
    (47, "alpine meadow", "alpine", "#b2c08a", 5,
     "Flower-filled summer pastures above the forest; snow until June."),
    (48, "alpine scrub (krummholz)", "alpine", "#8a9a7a", 5,
     "Wind-flattened, twisted trees and scrub; impassable in places."),
    (49, "alpine fellfield and scree", "alpine", "#a8a29a", 15,
     "Rock, scree and lichen between the meadows and the ice."),
    (50, "freshwater marsh and reedbed", "wetland", "#4f9f8f", 8,
     "Reeds taller than a person around lakes and in deltas; wildfowl, fish, fever."),
    (51, "temperate and boreal swamp forest", "wetland", "#3f6f5f", 9,
     "Alder, cypress or black spruce standing in water."),
    (52, "raised bog", "wetland", "#8a6a4a", 6,
     "A dome of living moss over metres of peat; treacherous pools, preserved bodies."),
    (53, "fen", "wetland", "#7f8f5a", 6,
     "Sedge and moss over peat, fed by springs; richer than bog, still soggy."),
    (54, "permafrost peatland (palsa and polygon mire)", "wetland", "#8f7f6a", 5,
     "Frost-heaved peat mounds and polygon ponds; firm in winter, a maze in summer."),
    (55, "mangrove forest", "coastal", "#2f6f6f", 14,
     "Stilt-rooted trees in tidal mud; crocodiles, crabs, a maze of creeks. (Placed by coastal life, PW-188.)"),
    (56, "salt marsh", "coastal", "#7fa08f", 8,
     "Flat green marsh cut by tidal creeks, flooded at spring tides; salt and wildfowl. (Placed by coastal life, PW-188.)"),
    (57, "ice", "non-vegetated", "#f4f7fa", 4, ""),
    (58, "bare rock and scree", "non-vegetated", "#8b8178", 15, ""),
    (59, "barren desert (sand or stone)", "non-vegetated", "#efe0b0", 11, "Dunes or gravel plains with no plants at all."),
    (60, "lake", "non-vegetated", "#4f8fcf", 3, ""),
]
T = {name: i for i, name, *_ in TYPES}
TYPE_BIOME = np.array([t[4] for t in TYPES])


def legend() -> dict:
    """The vegetation legend every file stores (store.legends): named types
    and PFTs."""
    return {"types": [{"id": i, "name": n, "group": g, "color": c, "biome": b, "text": d}
                      for i, n, g, c, b, d in TYPES],
            "pfts": [{"id": i, "code": p["code"], "name": p["name"], "color": p["color"],
                      "group": GROUPS[p["group"] - 1][0]} for i, p in enumerate(PFTS)],
            "groups": [{"id": k + 1, "name": g[0], "pfts": list(g[1])} for k, g in enumerate(GROUPS)]}


# ---------------------------------------------------------------------------
# Site: the climate a cell offers, month by month
# ---------------------------------------------------------------------------
TOP_MM, DEEP_MM = 50.0, 150.0  # water the topsoil (0-0.3 m) and subsoil (0.3-1.5 m) hold (PW-185 will set them)
SMAX = 5.0  # mm/day: what full soil can supply to the leaves (LPJ's Emax)


def site(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt: float = 23.4, cloud_jul=None, cloud_jan=None,
         relief=None) -> dict:
    """The climate inputs of each cell: climate.months plus the envelope
    indices (tc, tw, tmin: BIOME4's absolute-minimum estimate, gdd5), the
    annual moisture index mi = P/PET, Gaussen dry months (rain under twice
    the temperature) and the soil's water capacity (thinner on steep
    ground; relief: m to the steepest neighbour)."""
    mo = climate.months(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, cloud_jul, cloud_jan)
    tc, tw = np.minimum(t_cold, t_warm), np.maximum(t_cold, t_warm)
    pet = mo["pet"].sum(0)
    p = 0.5 * (p_jul + p_jan)
    dry = ((mo["p"] < 2 * mo["t"]) & (mo["t"] > 0)).sum(0)
    rel = np.zeros_like(temp) if relief is None else np.asarray(relief, float)
    steep = np.clip((rel - 500.0) / 2000.0, 0, 0.6)
    north = np.asarray(lat) >= 0
    mi = p / np.maximum(pet, 1.0)
    # fire weather: the expected share of the year the litter is dry. A month
    # (above 5 C, free of snow) is dry for sure when rain and snowmelt bring
    # under 20% of its potential evaporation, never above 100% (in between,
    # in some years: its dry spells)
    ratio = mo["water"] / np.maximum(mo["pet"], 1e-6)
    fire = (np.clip((1.0 - ratio) / 0.8, 0, 1) * (mo["t"] > 5) * (mo["snow"] <= 1)).sum(0) / 12.0
    return dict(mo, fire_season=fire, tc=tc, tw=tw, dryair=np.clip(0.35 + 0.65 * mi, 0.45, 1.2), tmin=0.006 * tc ** 2 + 1.316 * tc - 21.9, temp=np.asarray(temp, float),
                precip=p, pet_y=pet, mi=p / np.maximum(pet, 1.0), dry=dry, lat=np.asarray(lat, float),
                cap1=np.full(len(p), TOP_MM), cap2=DEEP_MM * (1 - steep),
                p_summer=np.where(north, p_jul, p_jan), p_winter=np.where(north, p_jan, p_jul),
                cloud=None if cloud_jul is None else 0.5 * (np.asarray(cloud_jul) + np.asarray(cloud_jan)))


def envelope(s: dict, co2: float = 0.0) -> np.ndarray:
    """(NP, n) bool: where each PFT can establish by its climate limits
    (section 2.2; the drought limit is checked after the water balance).
    co2 (the run's log CO2 index, ~log2 of CO2 against today's) moves the
    C4 grasses' warmth threshold: lower CO2, cooler C4 (Ehleringer 1997)."""
    out = np.zeros((NP, len(s["tc"])), bool)
    for i, p in enumerate(PFTS):
        tw_min = p["tw"] + (3.0 * float(np.clip(co2, -1.5, 1.5)) if i == C4 else 0.0)
        out[i] = ((s["tc"] >= p["tc_min"]) & (s["tc"] <= p["tc_max"]) & (s["tmin"] >= p["tmin"])
                  & (s["gdd5"] >= p["gdd"]) & (s["tw"] >= tw_min) & (s["tw"] <= p["tw_max"]) & (s["precip"] >= p["p_min"]))
    return out


# ---------------------------------------------------------------------------
# Productivity (kernels)
# ---------------------------------------------------------------------------
_DAYS = climate.MONTH_DAYS.astype(np.float64)


@njit(cache=True)
def _ft(t, t0, t1, t2, t3):
    if t <= t0 or t >= t3:
        return 0.0
    if t < t1:
        return (t - t0) / (t1 - t0)
    if t <= t2:
        return 1.0
    return (t3 - t) / (t3 - t2)


@njit(cache=True)
def _year(kp, i, lai, T, W, PET, PAR, cap1, cap2, eff, dryf, days, out):
    """One PFT growing alone at LAI lai on cell i, two years of months
    (the first spins the soil bucket up from full). Writes into out:
    [0] NPP, [1] net (NPP - leaf and fine-root turnover), [2] GPP,
    [3] mean water-stress ratio over the leaf-on months, [4] months with
    a dry topsoil (< 30% full, above 5 C), [5] leaf-on months Apr-Sep,
    [6] leaf-on months Oct-Mar."""
    eps, t0, t1, t2, t3, amin, top, phen, on_t = kp[0], kp[1], kp[2], kp[3], kp[4], kp[5], kp[6], kp[7], kp[8]
    rl, rw, lma, tleaf, kt, wet, wue = kp[9], kp[10], kp[11], kp[12], kp[13], kp[14], kp[16]
    w1, w2 = cap1, cap2
    gpp = resp = asum = 0.0
    non = ndry = 0.0
    onj = ona = 0.0
    fap_full = 1.0 - np.exp(-0.5 * lai)
    half = 0.5 * amin
    for k in range(24):
        m = k % 12
        t = T[m, i]
        w1 += W[m, i]
        if w1 > cap1:
            w2 += w1 - cap1
            w1 = cap1
        if w2 > cap2:
            w2 = cap2
        r1 = w1 / cap1 if cap1 > 0 else 0.0
        r2 = w2 / cap2 if cap2 > 0 else 0.0
        rootw = top * r1 + (1.0 - top) * r2
        if k >= 12 and r1 < 0.3 and t > 5.0:  # the topsoil (and the litter on it) stays dry this month
            ndry += 1.0
        if phen == 0:
            on = True
        elif phen == 1:
            on = t > on_t
        elif phen == 2:
            on = rootw > on_t and t > 0.0
        else:
            on = t > on_t and rootw > 0.2
        if wet > 0:
            rootw = 1.0
        fap = fap_full if on else 0.0
        demand = kt * PET[m, i] * fap
        aet = demand
        if wet == 0:
            # roots take from each layer by their share there, at most what it holds
            # (and shallow roots reach only part of the subsoil)
            reach = min(2.0 * (1.0 - top), 1.0)
            s1, s2 = top * r1, (1.0 - top) * r2
            tot = s1 + s2
            supply = SMAX * days[m] * rootw
            if aet > supply:
                aet = supply
            if tot > 0 and aet > 0.0:
                e1 = min(aet * s1 / tot, w1)
                e2 = min(aet * s2 / tot, w2 * reach)
                w1 -= e1
                w2 -= e2
                aet = e1 + e2
            else:
                aet = 0.0
        alpha = aet / demand if demand > 1e-9 else 1.0
        # bare-soil evaporation dries the topsoil between the plants
        w1 = max(w1 - 0.3 * PET[m, i] * (1.0 - fap_full) * r1, 0.0)
        if k >= 12:
            q10 = 2.0 ** ((t - 20.0) / 10.0)
            leaf = lai if (on or phen == 0) else 0.0
            resp += (rl * leaf + rw) * q10 * days[m] / 30.4
            if on:
                fw = (alpha - half) / (1.0 - half)
                fw = min(max(fw, 0.0), 1.0)
                g_m = eps * eff * fap * PAR[m, i] * _ft(t, t0, t1, t2, t3) * fw
                if wet == 0 and g_m > wue * dryf * aet:  # no more carbon than the water allows
                    g_m = wue * dryf * aet
                gpp += g_m
                asum += alpha
                non += 1.0
                if 3 <= m <= 8:
                    onj += 1.0
                else:
                    ona += 1.0
    npp = 0.75 * (gpp - resp) if gpp > resp else gpp - resp
    out[0] = npp
    out[1] = npp - 1.5 * lma * lai / tleaf
    out[2] = gpp
    out[3] = asum / non if non > 0 else 0.0
    out[4] = ndry
    out[5] = onj
    out[6] = ona


@njit(parallel=True, cache=True)
def _potential(cells, kp, T, W, PET, PAR, cap1, cap2, viable, eff, dryf, lai0, mode, days, res):
    """Potential NPP of every viable PFT on every cell in cells, at the LAI
    that maximises its net NPP. mode 0: golden-section search over
    (0.05, laimax) (8 evaluations); mode 1: a local step around lai0 (the
    last update's LAI; 3 evaluations), the run's cheap variant. res:
    (8, NP, n): the 7 _year outputs and the LAI."""
    npft = kp.shape[0]
    gr = 0.6180339887
    for jj in prange(len(cells)):
        i = cells[jj]
        out = np.zeros(7)
        best = np.zeros(7)
        for p in range(npft):
            if not viable[p, i]:
                continue
            lmax = kp[p, 15]
            if mode == 1 and lai0[p, i] > 0.05:
                bl, bv = 0.0, -1e30
                for f in (1.0, 0.8, 1.25):
                    x = min(max(lai0[p, i] * f, 0.05), lmax)
                    _year(kp[p], i, x, T, W, PET, PAR, cap1[i], cap2[i], eff[p, i], dryf[i], days, out)
                    if out[1] > bv:
                        bv, bl = out[1], x
                        best[:] = out
            else:
                a, b = 0.05, lmax
                c = b - gr * (b - a)
                d = a + gr * (b - a)
                _year(kp[p], i, c, T, W, PET, PAR, cap1[i], cap2[i], eff[p, i], dryf[i], days, out)
                fc = out[1]
                bv, bl = fc, c
                best[:] = out
                _year(kp[p], i, d, T, W, PET, PAR, cap1[i], cap2[i], eff[p, i], dryf[i], days, out)
                fd = out[1]
                if fd > bv:
                    bv, bl = fd, d
                    best[:] = out
                for _ in range(6):
                    if fc > fd:
                        b, d, fd = d, c, fc
                        c = b - gr * (b - a)
                        x = c
                    else:
                        a, c, fc = c, d, fd
                        d = a + gr * (b - a)
                        x = d
                    _year(kp[p], i, x, T, W, PET, PAR, cap1[i], cap2[i], eff[p, i], dryf[i], days, out)
                    if x == c:
                        fc = out[1]
                    else:
                        fd = out[1]
                    if out[1] > bv:
                        bv, bl = out[1], x
                        best[:] = out
            for k in range(7):
                res[k, p, i] = best[k]
            res[7, p, i] = bl


def potential(s: dict, viable: np.ndarray, eff: np.ndarray, co2: float = 0.0, lai0=None, cheap: bool = False) -> dict:
    """Potential productivity of each PFT on each cell where viable (NP, n),
    as if it grew alone (section 3.2). eff: (NP, n) efficiency multipliers
    (stand-ins). co2: the run's CO2 index nudges C3 efficiency (a mild
    'fertilisation', +-~20%). Returns (NP, n) arrays npp, net, gpp, alpha,
    dry (months), on_jul, on_jan (leaf-on months per half-year), lai; and
    the drought limit applied: a PFT whose growing-season water ratio is
    under its amin is not viable."""
    n = len(s["tc"])
    cells = np.flatnonzero(viable.any(0)).astype(np.int64)
    kp = _KP.copy()
    kp[C3_PFTS, 0] *= 1.0 + 0.12 * float(np.clip(co2, -1.5, 1.5))
    res = np.zeros((8, NP, n))
    lai = np.zeros((NP, n)) if lai0 is None else np.asarray(lai0, float)
    _potential(cells, kp, s["t"], s["water"], s["pet"], s["par"], s["cap1"], s["cap2"], viable,
               np.asarray(eff, float), s["dryair"], lai, 1 if cheap else 0, _DAYS, res)
    out = dict(zip(("npp", "net", "gpp", "alpha", "dry", "on_jul", "on_jan", "lai"), res))
    amin = _col("amin")[:, None]
    ok = viable & (out["net"] > 0) & (out["alpha"] >= amin)
    out["ok"] = ok
    return out


# ---------------------------------------------------------------------------
# Wetlands: the flooded share of each cell (section 3.6)
# ---------------------------------------------------------------------------
def relief(grid, elev) -> np.ndarray:
    """m to the steepest neighbour (land), a cell-scale slope proxy."""
    e = np.asarray(elev, float)
    d = np.abs(e[grid.nbr_idx] - np.repeat(e, np.diff(grid.nbr_off)))
    return np.maximum.reduceat(d, grid.nbr_off[:-1])


def flooded(grid, elev, flow, lake_kind, s: dict, ice=None) -> np.ndarray:
    """Share of each land cell (0..0.7) under water for part of the year:
    floodplains and deltas of big rivers, flat ground with a water
    surplus, flat permafrost (which can't drain), and lake shores."""
    from .hydrology import CLOSED_LAKE, OPEN_LAKE
    land = elev > 0
    rel = relief(grid, elev)
    flat = np.clip(1 - rel / 400.0, 0, 1)
    area_m2 = 4 * np.pi * (R_KM * 1e3) ** 2 / grid.n
    q = np.asarray(flow, float) * area_m2 / 3.156e7  # m3/s
    plain = 0.35 * np.clip(np.log10(np.maximum(q, 1.0) / 500.0) / 1.5, 0, 1) * flat
    # flat ground with more rain than evaporation can't drain it all (mires),
    # the more so where it is cool (slow decay builds peat that holds the water)
    mi = s["precip"] / np.maximum(s["pet_y"], 1.0)
    wet = 0.6 * np.clip((mi - 0.9) / 0.6, 0, 1) * flat ** 3 * np.clip((10.0 - s["temp"]) / 10.0, 0.3, 1.0)
    perma = 0.35 * (s["temp"] < -2) * np.clip(s["precip"] / 400.0, 0, 1) * flat ** 2
    lk = np.isin(np.asarray(lake_kind), (OPEN_LAKE, CLOSED_LAKE))
    shore = np.zeros(grid.n)
    if lk.any():
        nb = np.add.reduceat(lk[grid.nbr_idx].astype(float), grid.nbr_off[:-1])
        shore = 0.15 * (nb > 0) * ~lk
    f = np.clip(1 - (1 - plain) * (1 - wet) * (1 - perma) * (1 - shore), 0, 0.75)
    if ice is not None:
        f = np.where(ice > 0, 0.0, f)
    return np.where(land, f, 0.0)


# ---------------------------------------------------------------------------
# Competition and fire (kernels)
# ---------------------------------------------------------------------------
C_SAME, C_UNDER = 0.7, 0.2
NPP_FULL = 600.0  # g C/m2/yr at which a type's stand costs its full carbon
GRAZE = 0.05  # /yr extra tree and shrub mortality x grass cover^2: big herds need open grassland (placeholder for fauna: remove in PW-103)
START = dict(trees=0.4, herbs=0.3)  # cover shares a cell without history starts from  # competition from a type of the same height, and from a shorter one


def _competition() -> np.ndarray:
    h = _col("cls")
    C = np.where(h[None, :] > h[:, None], 1.0, np.where(h[None, :] == h[:, None], C_SAME, C_UNDER))
    for c in PIONEERS:
        i = CODES.index(c)
        C[i, TREES] = 1.0  # a pioneer is shaded by the trees around it...
        C[TREES, i] = 0.4  # ...and takes little from them
    np.fill_diagonal(C, 1.0)
    C[:, GROUNDS] = np.where(GROUNDS[:, None], C[:, GROUNDS], 0.0)  # ground layers don't crowd the vascular plants
    # The flooded share is its own habitat: wetland types meet only the part of
    # the others that grows on flooded ground (by their flood tolerance), and
    # dryland types don't meet the wetland types at all.
    wet, flood = _col("wet"), _col("flood")
    hab = np.where(wet[:, None] > 0, flood[None, :], 1.0 - wet[None, :])
    np.fill_diagonal(hab, 1.0)
    return C * hab


_C = _competition()


FIRE_MAX, FIRE_MID, FIRE_WIDTH = 0.35, 0.45, 0.09
FUEL_MIN, FUEL_SPAN = 250.0, 350.0  # g C/m2 of fine litter: no fire below FUEL_MIN, fully fuelled FUEL_SPAN above


@njit(cache=True)
def globfirm(s):
    """Burned share per year from the fire season s (share of the year the
    fuel is dry, 0..1): GlobFIRM's steep rise with the season's length
    (Thonicke et al. 2001), as a logistic that reaches ~1/3 of the land
    burning each year at a 5-month dry season (GlobFIRM's own curve gives
    only ~2% there, its known shortfall in the savannas), ~1/40 at 2 months,
    ~1/150 at 1."""
    if s <= 0.0:
        return 0.0
    return FIRE_MAX / (1.0 + np.exp(-(s - FIRE_MID) / FIRE_WIDTH))


@njit(parallel=True, cache=True)
def _step(cells, nu, g, K, ok, mort, C, resist, litter, season, kdec, ign, dt, seed, diff, nbr_off, nbr_idx,
          food, browsed, graze, out, burned):
    """One implicit step of the cover equations on every cell in cells:
    dnu/dt = g nu (K - sum_q C_pq nu_q) - (mort + fire (1 - resist)) nu,
    plus seeds (every viable type keeps at least `seed`) and a little
    spread from neighbours (diff). Fire from this cover's fuel."""
    npft = nu.shape[0]
    for jj in prange(len(cells)):
        i = cells[jj]
        fuel = 0.0
        for p in range(npft):
            fuel += nu[p, i] * litter[p, i]
        fuel /= kdec[i]
        a = globfirm(season[i]) * min(max((fuel - FUEL_MIN) / FUEL_SPAN, 0.0), 1.0) * ign[i]
        burned[i] = a
        grass = 0.0
        for p in range(npft):
            grass += food[p] * nu[p, i]
        n0, n1 = nbr_off[i], nbr_off[i + 1]
        for p in range(npft):
            if not ok[p, i]:
                out[p, i] = 0.0
                continue
            x = 0.0
            for q in range(npft):
                x += C[p, q] * nu[q, i]
            loss = mort[p] + a * (1.0 - resist[p]) + graze[i] * grass * grass * browsed[p]
            v = nu[p, i] * (1.0 + dt * g[p, i] * K[p, i]) / (1.0 + dt * (g[p, i] * x + loss))
            if diff > 0 and n1 > n0:
                m = 0.0
                for k in range(n0, n1):
                    m += nu[p, nbr_idx[k]]
                v += diff * (m / (n1 - n0) - nu[p, i]) * (m > nu[p, i])
            out[p, i] = max(v, seed)


def equilibrium(grid, s: dict, pot: dict, fw: np.ndarray, land: np.ndarray, nu0=None, steps=None,
                diff: float = 0.02) -> dict:
    """The cover fractions (NP, n) in equilibrium with the climate (section
    3.3), warm-started from nu0 (the previous state: history decides
    between forest and savanna), with fire. steps: list of (count, dt in
    years); default 30 x 2 yr then 40 x 10 yr. Returns nu (fractions, the
    seeds taken off), burned (share per year), and the growth rates."""
    n = grid.n
    ok = pot["ok"] & land[None, :] & ((_col("wet")[:, None] == 0) | (fw[None, :] > 0.01))
    cells = np.flatnonzero(ok.any(0)).astype(np.int64)
    carbon, mort = _col("carbon"), _col("gamma")
    # a square metre of a type costs less where it grows poorly (stunted
    # trees at the treeline hold far less carbon than a lowland forest)
    cost = carbon[:, None] * np.clip(np.maximum(pot["npp"], 0.0) / NPP_FULL, 0.3, 1.0)
    g = np.maximum(pot["net"], 0.0) / cost
    # where each type may grow: the flooded share belongs to the wetland types
    wet, flood = _col("wet")[:, None], _col("flood")[:, None]
    K = np.where(wet > 0, fw[None, :], 1.0 - fw[None, :] * (1.0 - flood))
    # water caps tree cover: in dry climates the canopy can't close (Sankaran et al. 2005)
    cap = np.clip((s["mi"] - 0.05) / 0.4, 0.0, 1.0)
    K = np.where(TREES[:, None], np.minimum(K, cap[None, :]), K)
    litter = np.maximum(pot["npp"], 0.0) * _col("litf")[:, None]
    # fire weather: the share of the year the fuel bed (the topsoil under the
    # likeliest burner, the herbs) is dry; lightning from warm, showery summers
    season = s["fire_season"]
    kdec = 0.5 * 2.0 ** ((s["temp"] - 10.0) / 10.0)
    kdec = np.clip(kdec, 0.05, 2.0)
    ign = np.clip(0.2 + 0.8 * np.clip((s["tw"] - 10.0) / 12.0, 0, 1) * np.clip(s["p_summer"] / 600.0, 0, 1), 0, 1)
    seed = 0.005
    # grazers (a placeholder until fauna, PW-103; decision 8): where grass is,
    # browsing and trampling kill tree and shrub seedlings
    food = np.isin(np.array(CODES), ("C3G", "C4G")).astype(float)
    browsed = (TREES | SHRUBS).astype(float)
    # (herds follow nutritious grass: none where it is wet all year)
    graze = GRAZE * np.clip(1.5 - s["mi"], 0.0, 1.0)
    if nu0 is None:  # no history: start from a young woodland over grass (see START), shared by the types that can grow
        nt = np.maximum((ok & TREES[:, None]).sum(0), 1)
        nh = np.maximum((ok & HERBS[:, None]).sum(0), 1)
        nu0 = np.where(TREES[:, None], START["trees"] / nt, np.where(HERBS[:, None], START["herbs"] / nh, 0.0))
    nu = np.where(ok, np.maximum(np.asarray(nu0, float), seed), 0.0)
    out = np.empty_like(nu)
    burned = np.zeros(n)
    C, resist = _C, _col("resist")
    for count, dt in steps or ((30, 2.0), (150, 10.0)):
        for _ in range(count):
            _step(cells, nu, g, K, ok, mort, C, resist, litter, season, kdec, ign, float(dt), seed, diff,
                  grid.nbr_off, grid.nbr_idx, food, browsed, graze, out, burned)
            nu, out = out, nu
    nu = np.where(nu > 2 * seed, nu - seed, 0.0)
    tot = nu.sum(0)
    nu = np.where(tot > 1, nu / np.maximum(tot, 1e-9), nu)
    return dict(nu=nu, burned=np.where(land, burned, 0.0), g=g, season=season)


# ---------------------------------------------------------------------------
# Summary fields and the named types
# ---------------------------------------------------------------------------
CLOSED = 2.5  # LAI at which a canopy shades all the ground under it


def summary(s: dict, pot: dict, eq: dict) -> dict:
    """Per-cell structure from the fractions: cover, tree cover, LAI (and
    per half-year), NPP, biomass, canopy height, fire return interval and
    stand age."""
    nu = eq["nu"]
    lai_p = pot["lai"]
    # the ground a type's share of the cell actually shades: a sparse canopy
    # (LAI under CLOSED) covers only part of its share
    closed = np.clip(lai_p / np.where(GROUNDS, 1.0, CLOSED)[:, None], 0, 1)
    shade = nu * closed
    npp = (nu * np.maximum(pot["npp"], 0)).sum(0)
    lai = (nu * lai_p).sum(0)
    evg = (_col("phen") == EVERGREEN)[:, None]
    l_jul = (nu * lai_p * np.where(evg, 1.0, pot["on_jul"] / 6.0)).sum(0)
    l_jan = (nu * lai_p * np.where(evg, 1.0, pot["on_jan"] / 6.0)).sum(0)
    tree = shade[TREES].sum(0)
    b = eq["burned"]
    resist, mort = _col("resist"), _col("gamma")
    tw = np.maximum(tree, 1e-9)
    r_tree = (nu[TREES] * resist[TREES, None]).sum(0) / np.maximum(nu[TREES].sum(0), 1e-9)
    m_tree = (nu[TREES] * mort[TREES, None]).sum(0) / np.maximum(nu[TREES].sum(0), 1e-9)
    stand = np.where(tree > 0.05, 1.0 / np.maximum(b * (1 - r_tree) + m_tree, 1e-4), 1.0 / (b + 0.1))
    biomass = (nu * np.maximum(pot["npp"], 0) * _col("tau")[:, None]).sum(0) * 0.01  # g/m2 -> t/ha
    hfrac = np.sqrt(np.clip(lai_p / _col("laimax")[:, None], 0, 1))
    h = _col("hmax")[:, None] * hfrac * np.where(TREES[:, None], 1 - np.exp(-stand / 60.0)[None, :], 1.0)
    height = np.where(nu > 0.1, h, 0.0).max(0)
    return dict(cover=shade.sum(0), tree=tree, shrub=shade[SHRUBS].sum(0), herb=shade[HERBS].sum(0),
                ground=shade[GROUNDS].sum(0), shade=shade, lai=lai, lai_jul=l_jul, lai_jan=l_jan, npp=npp, biomass=biomass,
                height=height, fire_return=np.where(b > 1e-4, 1.0 / np.maximum(b, 1e-9), 0.0),
                stand_age=np.minimum(stand, 2000.0))


def classify(s: dict, eq: dict, sm: dict, elev, ice=None, lake=None, lake_kind=None, fw=None) -> np.ndarray:
    """Named vegetation type (TYPES id) per cell: the first rule that holds
    (section 2.3): non-vegetated, wetland, forest (trees >= 60%),
    woodland and savanna (10-60%), sparse, shrubland, grassland."""
    from .hydrology import CLOSED_LAKE, SALT_PAN
    nu = sm["shade"]
    n = len(elev)
    f = {c: nu[i] for i, c in enumerate(CODES)}
    tree, cover = sm["tree"], sm["cover"]
    shrub, herb = sm["shrub"], sm["herb"]
    tw, tc, mat, P, mi, dry = s["tw"], s["tc"], s["temp"], s["precip"], s["mi"], s["dry"]
    lat = np.abs(s["lat"])
    elev = np.asarray(elev, float)
    fw = np.zeros(n) if fw is None else fw
    # alpine: cold because it is high (it would be warm enough for trees at sea level)
    sl_tw = tw + climate.LAPSE * np.maximum(elev, 0)
    alpine = (tw < 12) & (sl_tw >= 14) & (elev > 800)
    tropical_lat = (tc + climate.LAPSE * np.maximum(elev, 0)) >= 15
    summer_dry = (s["p_summer"] < 0.5 * s["p_winter"]) & (tc > -3)
    cloud = s["cloud"] if s.get("cloud") is not None else np.clip(P / 3000.0, 0, 1)
    trop_tree = f["TrBE"] + f["TrBR"]
    out = np.full(n, -1)

    def put(mask, tid):
        sel = mask & (out < 0)
        out[sel] = tid[sel] if np.ndim(tid) else tid

    put(elev <= 0, 0)
    if ice is not None:
        put(np.asarray(ice) > 0, T["ice"])
    if lake is not None:
        put(np.asarray(lake).astype(bool), T["lake"])
    salt = np.zeros(n, bool) if lake_kind is None else np.isin(np.asarray(lake_kind), (CLOSED_LAKE, SALT_PAN))
    put(salt & (cover < 0.4), T["salt desert scrub"])
    # 1. (next to) nothing grows
    bare = cover < 0.05
    put(bare & (s["gdd5"] < 100), np.where(alpine | (elev > 2500), T["bare rock and scree"],
                                           T["polar desert and fellfield"]))
    put(bare & (alpine | (elev > 2500)), T["bare rock and scree"])
    put(bare, T["barren desert (sand or stone)"])
    # 3. wetlands
    wetv = f["WetH"] + f["Sph"]
    wetland = (wetv >= 0.4) | (fw >= 0.45)
    perma = mat < -2
    put(wetland & (tree >= 0.4) & (trop_tree >= 0.5 * tree),
        np.where(f["Sph"] > 0.05, T["tropical peat swamp forest"], T["tropical swamp forest"]))
    put(wetland & (tree >= 0.4), T["temperate and boreal swamp forest"])
    put(wetland & perma & (f["Sph"] + f["TunH"] + f["Moss"] >= 0.3), T["permafrost peatland (palsa and polygon mire)"])
    put(wetland & (f["Sph"] >= f["WetH"]) & (s["precip"] > s["pet_y"]) & (fw < 0.45), T["raised bog"])
    put(wetland & (f["Sph"] >= f["WetH"]), T["fen"])
    put(wetland & (tc >= 15) & (dry >= 3) & (f["C4G"] + f["WetH"] >= 0.3), T["seasonally flooded grassland"])
    put(wetland, T["freshwater marsh and reedbed"])
    # 4. forest
    trees = np.stack([f[c] for c in ("TrBE", "TrBR", "TeBE", "TeBS", "TeNE", "BoNE", "BoNS", "BoBS")])
    tnames = np.array([0, 1, 2, 3, 4, 5, 6, 7])
    dom = tnames[np.argmax(trees, 0)]
    share = trees / np.maximum(tree, 1e-9)
    forest = tree >= 0.6
    trop = trop_tree >= 0.5 * tree
    put(forest & trop & alpine | forest & trop & (tw < 21) & (cloud >= 0.65) & (elev > 1000),
        T["tropical montane cloud forest"])
    put(forest & trop & (dry <= 1) & (f["TrBE"] >= 0.5 * tree), T["tropical lowland rainforest"])
    put(forest & trop & (dry <= 4), T["tropical monsoon (semi-evergreen) forest"])
    put(forest & trop, T["tropical dry deciduous forest"])
    rainy = (P > 1500) & (tc > -2) & (tw < 22)
    put(forest & (dom == 4) & rainy, T["temperate rainforest"])
    put(forest & (dom == 4) & summer_dry, T["Mediterranean pine forest"])
    put(forest & (dom == 4) & alpine & tropical_lat, T["montane conifer forest"])
    put(forest & (dom == 4) & (tc > 3), T["warm temperate pine forest"])
    put(forest & (dom == 4), T["temperate conifer forest"])
    put(forest & (dom == 2) & rainy, T["temperate rainforest"])
    put(forest & (dom == 2) & summer_dry, T["Mediterranean evergreen woodland"])
    put(forest & (dom == 2) & (share[2] >= 0.6), T["warm temperate evergreen (laurel) forest"])
    put(forest & (dom == 2), T["warm temperate mixed forest"])
    put(forest & (dom == 3) & (share[2] >= 0.25), T["warm temperate mixed forest"])
    put(forest & (dom == 3) & (share[4] + share[5] >= 0.25), T["temperate mixed forest"])
    put(forest & (dom == 3), T["temperate deciduous forest"])
    put(forest & (dom == 5) & (share[3] + share[2] >= 0.25), T["temperate mixed forest"])
    put(forest & (dom == 5) & (share[7] >= 0.25), T["boreal mixed forest"])
    put(forest & (dom == 5) & alpine & (lat < 45), T["montane conifer forest"])
    put(forest & (dom == 5), T["boreal spruce-fir taiga"])
    put(forest & (dom == 6), T["boreal larch taiga"])
    put(forest & (dom == 7) & (share[5] >= 0.25), T["boreal mixed forest"])
    put(forest & (dom == 7), T["boreal birch-aspen forest"])
    put(forest & trop, T["tropical dry deciduous forest"])
    put(forest, T["temperate mixed forest"])
    # 5. woodland and savanna
    wood = tree >= 0.1
    boreal = (f["BoNE"] + f["BoNS"] + f["BoBS"]) >= 0.5 * tree
    put(wood & trop & (dry >= 7) & (f["XerS"] + f["Succ"] >= 0.08), T["tropical thorn woodland"])
    put(wood & trop & (tree >= 0.3), T["moist savanna woodland"])
    put(wood & trop, T["dry savanna"])
    put(wood & alpine & ~boreal & (tw < 14), T["alpine scrub (krummholz)"])
    put(wood & boreal & (s["gdd5"] < 600) & (tree < 0.3), T["forest-tundra"])
    put(wood & boreal & (f["Moss"] >= 0.15), T["lichen woodland"])
    put(wood & boreal & (f["C3G"] >= 0.25), T["forest steppe"])
    put(wood & boreal, T["lichen woodland"])
    put(wood & summer_dry & ((dom == 2) | (f["SclS"] >= 0.15)), T["Mediterranean evergreen woodland"])
    put(wood & summer_dry & (dom == 4), T["Mediterranean pine forest"])
    put(wood & (f["C3G"] >= 0.25) & (mi < 0.7), T["forest steppe"])
    put(wood, T["temperate woodland and parkland"])
    # 6. sparse cover, named by climate
    sparse = cover < 0.25
    put(sparse & alpine, T["alpine fellfield and scree"])
    put(sparse & (s["gdd5"] < 300), T["polar desert and fellfield"])
    put(sparse & (f["Succ"] >= 0.5 * cover), T["succulent desert"])
    put(sparse & (tc < 0), T["cold desert scrub"])
    put(sparse, T["hot desert scrub"])
    # 7. shrubland
    shrubby = (shrub >= herb) & (shrub >= 0.05)
    tundra = (tw < 12) | (s["gdd5"] < 600)
    sd = np.stack([f[c] for c in ("SclS", "XerS", "DecS", "HthS", "Succ")])
    sdom = np.argmax(sd, 0)
    put(shrubby & (f["Succ"] >= 0.2), T["succulent desert"])
    put(shrubby & (sdom == 0), T["Mediterranean scrub (maquis, chaparral, fynbos)"])
    put(shrubby & (sdom == 1) & (tc < 0), T["cold desert scrub"])
    put(shrubby & (sdom == 1) & (cover < 0.45), T["hot desert scrub"])
    put(shrubby & (sdom == 1), T["semi-desert grassland"])
    put(shrubby & (sdom >= 2) & alpine, T["alpine scrub (krummholz)"])
    put(shrubby & (sdom == 2) & tundra, T["shrub tundra"])
    put(shrubby & (sdom == 3) & tundra, T["dwarf-shrub and lichen tundra"])
    put(shrubby & (sdom == 3), T["heathland and moorland"])
    put(shrubby & (sdom == 4), T["succulent desert"])
    put(shrubby, T["temperate scrub and thicket"])
    # 8. grass and herbs, or (where they don't make it) moss and crust
    grassy = herb >= 0.05
    put(alpine & tropical_lat & grassy, T["tropical alpine (paramo)"])
    put(alpine & grassy, T["alpine meadow"])
    put(alpine, T["alpine fellfield and scree"])
    put(tundra & (f["TunH"] >= 0.4) & ((mi > 1.0) | (fw > 0.15)), T["tussock and sedge tundra"])
    put(tundra & (f["TunH"] >= f["Moss"]) & grassy, T["tussock and sedge tundra"])
    put(tundra, T["dwarf-shrub and lichen tundra"])
    put(~grassy, np.where(tc < 0, T["cold desert scrub"], T["hot desert scrub"]))
    put((f["C4G"] >= f["C3G"]) & ((mi < 0.25) | (cover < 0.4)), T["semi-desert grassland"])
    put((f["C4G"] >= f["C3G"]) & (tc >= 10), T["tropical grassland"])
    put((mi < 0.25) & (f["XerS"] >= 0.1), T["shrub steppe"])
    put(mi < 0.25, T["semi-desert grassland"])
    put((f["XerS"] >= 0.15) & (tc < 0), T["shrub steppe"])
    put((mi >= 0.5) & (sm["lai"] >= 2), T["tall-grass prairie"])
    put(np.ones(n, bool), T["short-grass steppe"])
    return out


def biome_of(types, sea_biome) -> np.ndarray:
    """The coarse climate.BIOMES grouping of named types (sea cells keep
    sea_biome: deep, shallow, sea ice)."""
    return np.where(np.asarray(types) == 0, sea_biome, TYPE_BIOME[np.asarray(types)])


# ---------------------------------------------------------------------------
# The whole model on a world, and on a run's climate update
# ---------------------------------------------------------------------------
def model(grid, elev, temp, t_warm, t_cold, p_jul, p_jan, tilt=23.4, cloud_jul=None, cloud_jan=None, flow=None,
          lake_kind=None, lake=None, ice=None, nu0=None, lai0=None, co2: float = 0.0, unlocked=None,
          cheap: bool = False, steps=None, locked_potential: bool = False) -> dict:
    """Vegetation in equilibrium with a climate. Inputs are per-cell
    arrays (climate.compute's names); nu0, lai0: (NP, n) warm starts;
    unlocked: (NP,) bool, the PFTs that exist (default all; the rest are
    stood in for, STANDINS). cheap: the run's variant (local LAI step,
    fewer competition steps). locked_potential: also compute the locked
    PFTs' potential (for flora_update's niches). Returns a dict with the
    site s, the potential pot, eq (nu, burned), the flooded share fw, the
    summary sm and the named types."""
    n = grid.n
    elev = np.asarray(elev, float)
    ice = np.zeros(n) if ice is None else np.asarray(ice, float)
    land = (elev > 0) & (ice <= 0)
    if lake is not None:
        land &= ~np.asarray(lake).astype(bool)
    unlocked = all_unlocked() if unlocked is None else np.asarray(unlocked, bool)
    rel = relief(grid, elev)
    s = site(grid.lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, cloud_jul, cloud_jan, rel)
    env = envelope(s, co2) & land[None, :]
    viable = env & unlocked[:, None]
    eff = np.ones((NP, n))
    sub = standin_map(unlocked)
    for p, q in zip(*np.nonzero(sub)):
        extra = env[q] & ~env[p]
        viable[p] |= extra
        eff[p] = np.where(extra, STANDIN_EFF, eff[p])
    if locked_potential:
        viable_c = viable | (env & ~unlocked[:, None])
    else:
        viable_c = viable
    pot_all = potential(s, viable_c, eff, co2, lai0, cheap)
    pot = dict(pot_all, ok=pot_all["ok"] & viable)
    fw = flooded(grid, elev, np.zeros(n) if flow is None else flow, np.zeros(n) if lake_kind is None else lake_kind,
                 s, ice)
    eq = equilibrium(grid, s, pot, fw, land, nu0, steps or (((25, 10.0),) if cheap else None))
    sm = summary(s, pot, eq)
    types = classify(s, eq, sm, elev, ice, lake, lake_kind, fw)
    return dict(s=s, pot=pot, pot_all=pot_all, eq=eq, fw=fw, sm=sm, types=types, land=land, unlocked=unlocked)


def start_from_tree_cover(tree) -> np.ndarray:
    """A warm start (NP, n) from a stored tree cover (0..1; a run's
    keyframe): the trees' share split between the tree types, the rest
    grass (equilibrium keeps only the viable ones). It carries the
    history (forest or savanna) into a world built from a keyframe."""
    tree = np.clip(np.asarray(tree, float), 0, 1)
    return np.where(TREES[:, None], tree[None, :] / 2.0,
                    np.where(HERBS[:, None], (1 - tree)[None, :] / 2.0, 0.0))


def world_layers(v: dict) -> dict:
    """The world layers (store.LAYERS names) from a model() result."""
    sm, nu, land = v["sm"], v["eq"]["nu"], v["land"]
    dom = np.where(nu.max(0) > 0.05, np.argmax(nu, 0), 255)
    out = {
        "vegetation": v["types"].astype(int),
        "tree_cover": np.round(100 * sm["tree"]).astype(int),
        "plant_cover": np.round(100 * sm["cover"]).astype(int),
        "lai": np.round(sm["lai"], 1), "lai_jul": np.round(sm["lai_jul"], 1), "lai_jan": np.round(sm["lai_jan"], 1),
        "canopy_height": np.round(sm["height"]).astype(int),
        "npp": np.round(sm["npp"]).astype(int),
        "biomass": np.round(sm["biomass"]).astype(int),
        "fire_return": np.round(np.minimum(sm["fire_return"], 9999)).astype(int),
        "stand_age": np.round(np.where(land, sm["stand_age"], 0)).astype(int),
        "pft_dominant": np.where(land, dom, 255).astype(int),
        "flooded": np.round(100 * v["fw"]).astype(int),
    }
    for i, c in enumerate(CODES):
        out[f"veg_{c}"] = np.round(100 * nu[i]).astype(int)
    return out


def ground_cover(v: dict) -> np.ndarray:
    """0..1: how well plants hold the soil (section 4.5): canopy and herbs
    (1 - e^(-0.7 LAI)), plus moss, crust and litter on the ground."""
    sm, nu = v["sm"], v["eq"]["nu"]
    g = 1 - np.exp(-0.7 * sm["lai"])
    return 1 - (1 - g) * (1 - 0.6 * nu[GROUNDS].sum(0))


def niches(v: dict) -> np.ndarray:
    """For each group (GROUPS), the share of vegetated land where one of
    its PFTs would grow faster (net NPP per carbon) than anything there
    now: the room it would have if it appeared."""
    pot, land, unlocked = v["pot_all"], v["land"], v["unlocked"]
    g = np.where(pot["ok"], np.maximum(pot["net"], 0) / _col("carbon")[:, None], 0.0)
    cur = np.where(unlocked[:, None], g, 0.0).max(0)
    lam = land & (g.max(0) > 0)
    out = np.zeros(len(GROUPS))
    for k, (_, codes, _) in enumerate(GROUPS):
        idx = [IDX[c] for c in codes]
        if unlocked[idx].all():
            continue
        new = g[idx].max(0)
        out[k] = float((lam & (new > 1.2 * cur)).sum()) / max(int(lam.sum()), 1)
    return out


def flora_update(times: list, t: float, dt: float, plants_from: float, end: float, niche: np.ndarray, rng) -> list:
    """New appearance times (Myr; NaN: not yet) of the plant groups at a
    climate update at time t, dt Myr after the last. A group may appear
    from the start of its window (group_windows) once the one before it
    exists, with a chance per update proportional to its niche, times a
    ramp that reaches certainty at the window's end."""
    times = list(times)
    if t < plants_from - 1e-9:
        return times
    win = group_windows(plants_from, end)
    for k, (a, b) in enumerate(win):
        if np.isfinite(times[k]):
            continue
        if k > 0 and not np.isfinite(times[k - 1]):
            break
        if t < a - 1e-9:
            break
        if t >= b - 1e-9:
            times[k] = t
            continue
        width = max(b - a, dt)
        ramp = (t - a) / width
        p = 1 - np.exp(-4.0 * dt * niche[k] / width)
        p = p + (1 - p) * ramp ** 6
        if rng.random() < p:
            times[k] = t
        else:
            break
    return times
