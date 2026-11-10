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
   Open grassland also carries grazers (a placeholder until fauna, PW-103:
   GRAZE), which keep tree and shrub seedlings down.
5. Wetlands: the flooded share of a cell (floodplains of big rivers, flat
   wet ground, permafrost flats, lake shores) is a habitat of its own for
   the wetland types (reeds and sedges, peat moss) and flood-tolerant trees.
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
from .geo import is_land

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
#     mortality /yr; resist: share surviving a fire (resprouters: grass, savanna
#     trees and sclerophyll shrubs, which keep their roots and space); hmax: height, m;
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
     0.30, 0.90, (0, 15, 30, 42), 3.5, 80, 2, 5.0, 12, 1.0, 0, 0.0, 3000, 0.030, 0.90, 4, 0.40, 8),
    ("XerS", "xeric (desert) shrub", "#c2a970", 4, SHRUB, RAINGREEN, 0.10, -35, 99, _NO, 500, _NO, 0.05,
     0.35, 0.80, (-2, 15, 32, 45), 2.0, 60, 1, 4.0, 6, 0.8, 0, 0.0, 1500, 0.040, 0.60, 2, 0.40, 8),
    ("DecS", "cold-deciduous shrub", "#a4b06a", 4, SHRUB, SUMMERGREEN, 3, _NO, 5, _NO, 150, _NO, 0.35,
     0.60, 0.95, (-4, 8, 20, 32), 3.0, 33, 1, 5.0, 8, 1.0, 0, 0.5, 1500, 0.040, 0.80, 3, 0.40, 8),
    ("HthS", "evergreen dwarf heath shrub", "#8e6a8a", 4, SHRUB, EVERGREEN, 0, -35, 10, _NO, 100, _NO, 0.50,
     0.80, 0.80, (-4, 8, 20, 30), 2.0, 70, 2, 4.0, 3, 1.0, 0, 0.4, 800, 0.050, 0.70, 1, 0.40, 6),
    ("C4G", "C4 grass", "#d8c24a", 6, HERB, HERBAL, 10, _NO, 99, _NO, 0, 22, 0.10,
     0.85, 1.20, (10, 25, 38, 50), 4.0, 25, 1, 4.0, 0, 0.7, 0, 0.3, 300, 0.10, 0.95, 2, 0.90, 1),
    ("C3G", "C3 grass and forbs", "#b5c86a", 5, HERB, HERBAL, 0, _NO, 15.5, _NO, 200, _NO, 0.15,
     0.80, 1.10, (-2, 12, 32, 45), 4.0, 25, 1, 4.0, 0, 1.0, 0, 0.3, 300, 0.10, 0.95, 1, 0.90, 1),
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
# Respiration acclimates to the growth temperature (PW-806). The rates rl, rw (at 20 C, Q10 = 2 month to month) are
# those of each type grown where it grows on Earth: T_GROWN is its cover-weighted mean temperature of the warmest
# three months there (Earth's model climate at CA_REF; Atkin et al. 2015's TWQ). A stand grown warmer than that
# respires less at a given temperature, one grown colder more: RESP_ACCLIM of the growth temperature's difference
# is taken back from the month's Q10 term. Leaf respiration's global trait data give about half (Atkin et al.
# 2015's TWQ term against Heskel et al. 2016's instantaneous curve, as JULES takes them up, Huntingford et al.
# 2017); warming experiments on whole trees up to ~80% (Reich et al. 2016); whole plants' respiration/
# photosynthesis ratio is conserved at full acclimation (Gifford 1995; Dewar et al. 1999). Acclimation is bounded
# (Atkin & Tjoelker 2003): it counts within ACCLIM_SPAN of T_GROWN, about the span of growth temperatures the
# controlled-growth and seasonal acclimation data cover (a desert's soil crust, ~20 C above the mosses' Earth range,
# gets no more of it). (Succulents and wetland herbs are rare on Earth's model: their temperature plateau's middle.)
RESP_ACCLIM = 0.8
# Photosynthesis acclimates too: its optimum temperature moves ~0.4-0.6 C per C of growth temperature (Kattge &
# Knorr 2007; Kumarathunge et al. 2019), so the hump's high-temperature side (temp[2], temp[3]) moves by PS_ACCLIM of
# the same bounded difference. Its cold side stays (frost and the envelopes set it).
PS_ACCLIM = 0.5
ACCLIM_SPAN = 10.0  # C: acclimation is bounded; a stand grown further from T_GROWN than this gets no more of it
T_GROWN = {"TrBE": 25.5, "TrBR": 25.5, "TeBE": 24.0, "TeBS": 22.0, "TeNE": 22.0, "BoNE": 18.0, "BoNS": 11.0,
           "BoBS": 10.0, "SclS": 24.5, "XerS": 29.5, "DecS": 9.0, "HthS": 9.5, "C4G": 28.5, "C3G": 25.5, "TunH": 7.0,
           "Succ": 29.0, "Moss": 13.5, "WetH": 23.5, "Sph": 14.0}
# water-use efficiency, g C of GPP per mm transpired in moderately humid air
# (C4 and CAM plants waste less water), and the warmest month above which a
# type can't hold its own (heath: cool summers)
_TUNE = {  # (tuned on Earth with tools/veg_check.py; overrides of the table above)
    "TeNE": dict(eps=0.95, gamma=0.005), "BoNS": dict(eps=0.95, lma=35),
    "XerS": dict(eps=0.45, laimax=1.5, carbon=2500, gamma=0.05), "Succ": dict(eps=0.3, gamma=0.04, carbon=3000), "TrBE": dict(eps=1.43, gamma=0.005, rl=11.1),
    "TrBR": dict(eps=1.0, carbon=13000, gamma=0.008, resist=0.93), "TeBE": dict(gamma=0.006), "BoNE": dict(gamma=0.005, carbon=10000),
    "TeBS": dict(eps=1.15, gamma=0.005, carbon=11000),
}
# TrBE's eps (scout 210, PW-1331): 1.43 x EPS_SCALE = 1.14 g C per MJ of absorbed PAR, the canopy light-use efficiency
# measured by eddy covariance at Tapajos K67 in the dry season, at a diffuse fraction of 0.55 (GPP / (PAR x FPAR): 1.1,
# rising to 1.9 in the wet season at Df 0.9; Yan et al. 2017, JGR Biogeosci 122:3014, doi:10.1002/2017JG004008). LPJ's
# 1.10 gave 0.88, and tropical GPP ~2200 against ~3100 measured at the same tower (Hutyra et al. 2007, as Lloyd et al.
# 2010 quote it: 262 mol C/m2/yr). The wet season's higher value is the diffuse-light gain (DIFFUSE, PW-1518).
# TrBE's rl (PW-1518, scout 232): x1.5 LPJ's 7.4, Chambers et al. 2004's in-situ canopy leaf rate at Manaus (0.54
# umol/m2/s over 24 h against 0.33 at 25 C; Ecol Appl 14:S72; docs/review/climate/npp/scout3.md). Its leaves then
# breathe ~750 g C/m2/yr on Earth's observed climate (measured 710-980; docs/review/climate/diffuse/screens.md).
PIONEERS = ("BoBS", "BoNS")  # light-hungry trees that shade-tolerant ones crowd out (birch, aspen, larch)
# Herbs' roots respire too (PW-1261, lane 123): the herbs carry no wood term (rw = 0), so their rl, the leaves' rate,
# was all the maintenance a grass paid, and its NPP/GPP came out at ~0.7 (Earth's observed climate) against ~0.46 +- 0.12
# measured over 200+ studies (Collalti & Prentice 2019, Tree Physiol, doi:10.1093/treephys/tpz034, abstract; forests: the grass value is
# not sourced, an extrapolation). Their grass above-ground NPP ran 1.4-1.8x the field fits at the same rain (Deshmukh
# 1984, Yang et al. 2020; docs/review/vegetation/npp-check/diagnosis.md). The live roots and rhizomes of a herb stand
# respire with its leaves (x HERB_ROOT_RESP the leaves' rate while leaves are out: a judgement within 2-3, giving NPP/GPP ~0.55-0.65).
HERB_ROOT_RESP = 2.5
for _p in PFTS:
    _p.update(_TUNE.get(_p["code"], {}))
    if _p["cls"] == HERB:
        _p["rl"] = _p["rl"] * HERB_ROOT_RESP
    _p["wue"] = {"C4G": 4.0, "Succ": 4.0}.get(_p["code"], 3.0)
    _p["tw_max"] = {"HthS": 20.0, "DecS": 20.0, "TunH": 18.0}.get(_p["code"], 99.0)
    # mm/yr: succulents need rain (or fog) most years; the hyper-arid cores of deserts are barren
    _p["p_min"] = {"Succ": 100.0}.get(_p["code"], 0.0)
    # least moisture index P/PET: heath is a plant of wet, maritime or cold-humid ground
    # (the drought limit amin can't tell: a sparse heath's own demand is met even at 100 mm)
    _p["mi_min"] = {"HthS": 0.5}.get(_p["code"], 0.0)
    # the most of the year's rain that may fall in the warm half-year: hard,
    # evergreen sclerophyll leaves are a summer-drought adaptation (Mediterranean-type
    # and winter- or evenly-watered scrub); where the rain comes in the warm season,
    # raingreen trees, thorn shrubs and grasses use it instead (PW-234 follow-up)
    _p["summer_rain_max"] = {"SclS": 0.5}.get(_p["code"], 1.0)
    _p["t_grown"] = T_GROWN[_p["code"]]
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
           "laimax", "wue", "qy")
EPS_SCALE = 0.8  # all efficiencies (tuned: Earth's land NPP)
# Leaf enzyme (Vcmax) and with it leaf respiration fall exponentially with depth in a canopy (dark respiration a fixed
# share of capacity, Rd = 0.08 Amax), so a stand's leaf respiration grows as (1 - exp(-KN L)) / KN per unit of LAI L,
# not as L (scout 173, lane 181). KN per unit of cumulative LAI, read by scout 210 (docs/review/climate/npp/
# scout2.md): ~0.15 observed at Tapajos with L 5.1, 0.12 at Lloyd et al.'s optimum (Biogeosciences 7:1833, 2010), their
# 18-profile fit ln kV = 0.00963 Vmax(0) - 2.43 (0.13-0.28 for top-leaf Vmax 40-120); JULES kn 0.78 per relative depth
# i/n, ~0.15 per unit LAI at L 5 (Clark et al. 2011, GMD 4:701, from Mercado et al. 2007's Amazon profile). Always well
# under the light's own extinction (Lloyd: kI 0.7 for tropical forest). Herbs keep the linear form (one thin layer).
# 0 turns it off.
KN_RESP = 0.15
# Diffuse light (PW-1518): a canopy fixes more carbon per unit of absorbed light under a cloudy, diffuse sky, because
# the light then reaches the shaded inner leaves instead of saturating the sunlit ones (Mercado et al. 2009, Nature
# 458:1014). Per PFT (clumping index, the diffuse fraction its eps is for): the PFT's GPP takes Yan et al. 2017's
# two-leaf canopy (_two_leaf: sunlit and shaded leaves, the shaded ones' efficiency rising with the month's diffuse
# share Df, climate.months' df) in place of the big leaf's FPAR, normalised so a canopy of LAI_REF under Df0 fixes what
# today's eps does; a month clearer than Df0 is taken at Df0 (today's eps is the floor). The two-leaf form also pays the
# deep, shaded leaves more than the big leaf does, so the PFT keeps more leaf layers.
# TrBE only (PW-1518, scouts 232 and 239): its eps was measured at Tapajos K67 at the dry season's Df 0.55 (above), and
# Yan's two-leaf parameters (eps_sun 1.11, eps_shade 4.35 g C/MJ, Df exponent 1.8) were calibrated there, clumping 0.8
# for evergreen broadleaf forest (Yan's Table 1, after Zhou et al. 2016). The other trees' eps are fitted on Earth's
# land NPP (EPS_SCALE) at whatever sky they have, so they keep the big leaf until that fit is redone (PW-1574;
# docs/review/climate/diffuse/).
DIFFUSE: dict[str, tuple[float, float]] = {"TrBE": (0.8, 0.55)}
LAI_REF = 4.6  # the LAI the two-leaf canopy is normalised at: TrBE's on Earth's observed climate before PW-1518 (4.58)
C4, C3 = IDX["C4G"], IDX["C3G"]
_KP = np.stack([EPS_SCALE * _col("eps"), *(np.array([p["temp"][j] for p in PFTS], float) for j in range(4)), _col("amin"),
                _col("top"), _col("phen"), _col("on"), _col("rl"), _col("rw"), _col("lma"), _col("tleaf"),
                _col("kt"), _col("wet"), _col("laimax"), _col("wue"), (np.arange(NP) == C3).astype(float),
                _col("wue"), _col("t_grown"), np.where(HERBS, 0.0, KN_RESP),
                np.array([DIFFUSE.get(c, (0.0, 1.0))[0] for c in CODES]),
                np.array([DIFFUSE.get(c, (0.0, 1.0))[1] for c in CODES])], 1)  # (water-use efficiency at today's CA_REF, which potential()
# leaves unscaled; the growth temperature the respiration rates are for, T_GROWN)
# C3 against C4 grasses (PW-231): the two differ only in their photosynthetic
# pathway, and which wins a month is set by the quantum yield (Ehleringer &
# Bjorkman 1977; Ehleringer et al. 1997): C4's is the same at any temperature,
# C3's falls as photorespiration rises with temperature and falls with CO2,
# as (Ci - G*) / (Ci + 2 G*) (Farquhar et al. 1980; G*, the CO2 compensation
# point, from Bernacchi et al. 2001; Ci = 0.7 Ca). The two are equal at a
# monthly mean of QY_CROSS (Collatz et al. 1998's C4 climate criterion, at
# their ~350 ppm), so C3 grass's efficiency is C4 grass's there, scaled by
# its quantum yield elsewhere (vegetation._q3; the qy column flags it).
QY_CROSS, CA_REF = 22.0, climate.PCO2_REF  # C, ppm (today: the climate model's dT = 0; a run's balance is climate.PCO2_BALANCE)


def _gstar(t):
    """CO2 compensation point without dark respiration, ppm (Bernacchi et al. 2001)."""
    return 42.75 * np.exp(37830.0 * (t - 25.0) / (298.15 * 8.314 * (t + 273.15)))


def _q3(t, ci):
    """C3 quantum yield relative to its photorespiration-free value."""
    g = _gstar(t)
    return (ci - g) / (ci + 2.0 * g)


def _ft_np(t, t0, t1, t2, t3):
    return float(np.interp(t, (t0, t1, t2, t3), (0.0, 1.0, 1.0, 0.0)))


_KP[C3, 0] = _KP[C4, 0] * _ft_np(QY_CROSS, *PFTS[C4]["temp"]) / _q3(QY_CROSS, 0.7 * CA_REF)
# The other C3 plants (trees, shrubs, herbs, moss: all but C4 grass, CAM succulents and C3 grass, which has its
# own) feel CO2 through the same quantum yield, as today's times its ratio to today's at that month's temperature
# (qy column 2; PW-644): 1 at today's CA_REF, so their efficiencies stay as tuned on Earth today. A glacial's low
# CO2 costs them most where it is hot (photorespiration), which is why C4 grassland spread through the tropics at
# the LGM (Ehleringer et al. 1997; Collatz et al. 1998).
C3_PFTS = np.array([p["code"] not in ("C4G", "Succ", "C3G") for p in PFTS])
_KP[C3_PFTS, 17] = 2.0
CI_REF = 0.7 * CA_REF
CO2_RANGE = 1.5  # doublings: the plants' CO2 responses are held at their values this far from CA_REF (124-990 ppm)


def co2_doublings(pco2: float) -> float:
    """log2 of pCO2 (ppm) against today's CA_REF, within +-CO2_RANGE: the scale of the plants' CO2 responses
    (PW-646: the run and the time zoom hand them a real pCO2, climate.pco2)."""
    return float(np.clip(np.log2(max(float(pco2), 1e-9) / CA_REF), -CO2_RANGE, CO2_RANGE))


CO2_FLOOR = CA_REF * 2.0 ** -CO2_RANGE  # ppm (124): the low end of the plants' CO2 range


def starvation(t, pco2: float):
    """Per cell at monthly-or-annual temperature t (C), the C3 plants' growth below CO2_FLOOR as a share of
    theirs at the floor: the quantum yield's ratio _q3(t, 0.7 pCO2) / _q3(t, 0.7 CO2_FLOOR) (Farquhar et al.
    1980, Bernacchi et al. 2001's compensation point), 1 at and above the floor, 0 at and below the
    compensation point (photorespiration takes all the carbon). For the consumers that see CO2 below the
    range the vegetation itself holds (the weathering sink's plants, tectonics/earth.co2_law; PW-1227:
    Pagani et al. 2009, starving plants stop speeding up weathering, which keeps CO2 from falling further).
    Returns (share, d share / d ln pCO2)."""
    t = np.asarray(t, float)
    if pco2 >= CO2_FLOOR:
        return np.ones_like(t), np.zeros_like(t)
    g = _gstar(t)
    ci = 0.7 * max(float(pco2), 0.0)
    q = (ci - g) / (ci + 2.0 * g) / _q3(t, 0.7 * CO2_FLOOR)
    dq = 3.0 * g * ci / (ci + 2.0 * g) ** 2 / _q3(t, 0.7 * CO2_FLOOR)
    pos = q > 0.0
    return np.where(pos, q, 0.0), np.where(pos, dq, 0.0)

# ---------------------------------------------------------------------------
# Plant groups that appear during a run (decision 3)
# ---------------------------------------------------------------------------
# (name, PFTs it unlocks, (earliest, latest) Ma before now it appears in a run: Earth's own calendar counted
# back from the run's end, PW-807, owner 2026-10-24). The window is the per-seed spread; its latest end is the
# deadline by which the group exists. A group whose window lies before the run's start is there from the start.
# Ages: land plants (cryptospores, liverwort-grade pioneers) ~470-500 Ma (Wellman et al. 2003; Morris et al.
# 2018); vascular plants ~430 Ma (Cooksonia, Silurian); forests ~385 Ma (Archaeopteris, Gilboa: Stein et al.
# 2007, 2012); flowering plants ~130 Ma, dominant ~100 Ma; grasses ~70 Ma (Prasad et al. 2005, 2011), widespread
# ~55; C4 grasses ~30 Ma, spreading ~8 Ma (Christin et al. 2008; Edwards et al. 2010). Life in the sea is far
# older (algae > 1 Ga): what the run ties to sea life, reefs, is in tectonics/earth.py (REEF_BUILDERS_MA).
GROUPS = [
    ("pioneers: mosses, lichens, soil crusts", ("Moss", "Sph"), (500.0, 470.0)),
    ("early vascular marsh plants", ("WetH",), (440.0, 420.0)),
    ("forests without flowers: spore trees, seed ferns, conifers", ("TeNE", "BoNE", "BoNS"), (395.0, 375.0)),
    ("flowering trees and shrubs", ("TrBE", "TrBR", "TeBE", "TeBS", "BoBS", "SclS", "XerS", "DecS", "HthS"),
     (140.0, 120.0)),
    ("grasses and sedges", ("C3G", "TunH"), (75.0, 60.0)),
    ("C4 grasses and succulents (CAM)", ("C4G", "Succ"), (35.0, 25.0)),
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


def group_windows(now: float) -> list[tuple[float, float]]:
    """(earliest, latest) appearance time (run Myr) of each group: its GROUPS window in Ma before now, now
    being the run time that is today (tectonics.earth.now_myr: the run's end). Times before 0 mean the group
    is there from the run's start (it appears at the first climate update)."""
    return [(now - g[2][0], now - g[2][1]) for g in GROUPS]


def land_plants(times, t: float) -> bool:
    """Whether land plants (the pioneers, GROUPS[0]) exist at time t, given the groups' appearance times."""
    t0 = times[0] if len(times) else None
    return t0 is not None and bool(np.isfinite(t0)) and t0 <= t + 1e-9


def bare_niches() -> np.ndarray:
    """niches() for bare land: all of it is open to the pioneers, nothing to the rest."""
    out = np.zeros(len(GROUPS))
    out[0] = 1.0
    return out


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
    (61, "moss and crust carpet", "archaic", "#8f9a6a", 8,
     "Low carpets of moss, liverworts and dark microbial crust over thin soil; no grass yet, the land before flowers."),
    (62, "dry sclerophyll scrub (mallee, mulga)", "desert", "#a89a5a", 8,
     "Hard-leaved grey-green evergreen shrubs on poor dry ground, bare earth or tussock grass between; big fires after wet years."),
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
TOP_MM, DEEP_MM = 50.0, 150.0  # water the topsoil (0-0.3 m) and subsoil (0.3-1.5 m) hold without soils (worlds: soils.py)
SMAX = 5.0  # mm/day: what full soil can supply to the leaves (LPJ's Emax)


@njit(cache=True, parallel=True)
def _site_k(p_m, t_m, snow, water, pet_m, north, pet, dry, drought, fire, tg):
    """site's per-cell reductions over the twelve months, in one pass (numpy's arithmetic in its order, sums month by month)."""
    for i in prange(p_m.shape[1]):
        ps = pet_m[0, i]
        nd = 0
        dry_s = np.inf
        wet_w = -np.inf
        f = 0.0
        for m in range(12):
            if m > 0:
                ps = ps + pet_m[m, i]
            t = t_m[m, i]
            p = p_m[m, i]
            if p < 2 * t and t > 0:
                nd += 1
            jul = m >= 3 and m <= 8
            summer = jul if north[i] else not jul
            if summer:
                if p < dry_s:
                    dry_s = p
            elif p > wet_w:
                wet_w = p
            r = water[m, i] / max(pet_m[m, i], 1e-6)
            c = min(max((1.0 - r) / 0.8, 0.0), 1.0)
            v = c * (1.0 if t > 5 else 0.0) * (1.0 if snow[m, i] <= 1 else 0.0)
            f = v if m == 0 else f + v
        pet[i] = ps
        dry[i] = nd
        drought[i] = (dry_s < 40) and (dry_s < wet_w / 3)
        fire[i] = f / 12.0
        # growth temperature: the mean of the three warmest months, summed smallest to largest
        a0, a1, a2 = -np.inf, -np.inf, -np.inf  # a2 >= a1 >= a0 the three largest
        for m in range(12):
            t = t_m[m, i]
            if t >= a2:
                a0, a1, a2 = a1, a2, t
            elif t >= a1:
                a0, a1 = a1, t
            elif t > a0:
                a0 = t
        tg[i] = ((a0 + a1) + a2) / 3


def site(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt: float = 23.4, cloud_jul=None, cloud_jan=None,
         relief=None, light=None, extra_water=None, extra_pet=None) -> dict:
    """The climate inputs of each cell: climate.months plus the envelope
    indices (tc, tw, tmin: BIOME4's absolute-minimum estimate, gdd5), the
    annual moisture index mi = P/PET, Gaussen dry months (rain under twice
    the temperature), summer drought (Koppen's s) and the soil's water capacity (thinner on steep
    ground; relief: m to the steepest neighbour).
    For zoom pixels (zoom.vegetation): light (12, n) scales each month's
    light and potential evaporation (a slope's radiation index);
    extra_water (n,) mm/yr reaches the soil besides the rain, evenly over
    the year (groundwater in hollows); extra_pet (n,) adds that share of
    each month's potential evaporation (a river's water by its banks).
    Both count in the moisture index."""
    mo = climate.months(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, cloud_jul, cloud_jan)
    if light is not None:
        mo["par"], mo["pet"] = mo["par"] * light, mo["pet"] * light
    p = 0.5 * (p_jul + p_jan)
    pw = p  # rain plus any extra water: the moisture index's supply
    if extra_water is not None or extra_pet is not None:
        add = np.zeros_like(mo["water"])
        if extra_water is not None:
            add = add + np.asarray(extra_water, float)[None, :] * climate.MONTH_DAYS[:, None] / 365.25
        if extra_pet is not None:
            add = add + np.asarray(extra_pet, float)[None, :] * mo["pet"]
        mo["water"] = mo["water"] + add
        pw = p + add.sum(0)
    tc, tw = np.minimum(t_cold, t_warm), np.maximum(t_cold, t_warm)
    rel = np.zeros_like(temp) if relief is None else np.asarray(relief, float)
    steep = np.clip((rel - 500.0) / 2000.0, 0, 0.6)
    north = np.asarray(lat) >= 0
    # the per-cell reductions over the months, in one pass: potential evaporation of the year, Gaussen dry months,
    # summer drought as Koppen's Cs/Ds has it (the driest month of the summer half-year under 40 mm and under a third
    # of the winter's wettest), fire weather (the expected share of the year the litter is dry: a month above 5 C, free
    # of snow, is dry for sure when rain and snowmelt bring under 20% of its potential evaporation, never above 100%;
    # in between, in some years: its dry spells) and the growth temperature (the mean of the three warmest months,
    # the respiration acclimates to it, RESP_ACCLIM)
    n = len(north)
    pet, dry, drought, fire, tg = np.empty(n), np.empty(n, np.int64), np.empty(n, bool), np.empty(n), np.empty(n)
    _site_k(mo["p"], mo["t"], mo["snow"], mo["water"], mo["pet"], north, pet, dry, drought, fire, tg)
    mi = pw / np.maximum(pet, 1.0)
    return dict(mo, fire_season=fire, summer_drought=drought, tc=tc, tw=tw, tg=tg, dryair=np.clip(0.35 + 0.65 * mi, 0.45, 1.2), tmin=0.006 * tc ** 2 + 1.316 * tc - 21.9, temp=np.asarray(temp, float),
                precip=p, pet_y=pet, mi=mi, dry=dry, lat=np.asarray(lat, float),
                cap1=np.full(len(p), TOP_MM), cap2=DEEP_MM * (1 - steep),
                p_summer=np.where(north, p_jul, p_jan), p_winter=np.where(north, p_jan, p_jul),
                cloud=None if cloud_jul is None else 0.5 * (np.asarray(cloud_jul) + np.asarray(cloud_jan)))


def envelope(s: dict, pco2: float = CA_REF) -> np.ndarray:
    """(NP, n) bool: where each PFT can establish by its climate limits
    (section 2.2; the drought limit is checked after the water balance).
    pco2 (ppm) moves the C4 grasses' warmth threshold by 3 C per doubling
    against today's: lower CO2, cooler C4 (Ehleringer 1997)."""
    out = np.zeros((NP, len(s["tc"])), bool)
    for i, p in enumerate(PFTS):
        tw_min = p["tw"] + (3.0 * co2_doublings(pco2) if i == C4 else 0.0)
        out[i] = ((s["tc"] >= p["tc_min"]) & (s["tc"] <= p["tc_max"]) & (s["tmin"] >= p["tmin"])
                  & (s["gdd5"] >= p["gdd"]) & (s["tw"] >= tw_min) & (s["tw"] <= p["tw_max"]) & (s["precip"] >= p["p_min"])
                  & (s["mi"] >= p["mi_min"])
                  & (s["p_summer"] <= p["summer_rain_max"] * (s["p_summer"] + s["p_winter"]) + 1e-9))
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
def _two_leaf(lai, df, mu, om):
    """Yan et al. 2017's two-leaf canopy (JGR Biogeosci 122:3014, eq. 5-11): GPP per unit of PAR at the top, before
    the water and temperature factors, for leaf area lai, diffuse share df, cos noon zenith mu, clumping om."""
    pdir, pdif = 1.0 - df, df
    lsun = 2.0 * mu * (1.0 - np.exp(-0.5 * om * lai / mu))
    pdu = pdif * np.exp(-0.5 * om * lai / (0.537 + 0.025 * lai))
    c = 0.07 * om * pdir * (1.1 - 0.1 * lai) * np.exp(-mu)
    shd = (pdif - pdu) / lai + c
    return 1.11 * (pdir * 0.5 / mu + shd) * lsun + 4.35 * (0.25 + 0.75 * df ** 1.8) * shd * (lai - lsun)


@njit(cache=True)
def _year(kp, i, lai, T, W, PET, PAR, DF, MU, cap1, cap2, eff, dryf, tg, days, ci, out):
    """One PFT growing alone at LAI lai on cell i, two years of months
    (the first spins the soil bucket up from full). Writes into out:
    [0] NPP, [1] net (NPP - leaf and fine-root turnover), [2] GPP,
    [3] mean water-stress ratio over the leaf-on months, [4] months with
    a dry topsoil (< 30% full, above 5 C), [5] leaf-on months Apr-Sep,
    [6] leaf-on months Oct-Mar, [7 + m] GPP in month m (Jan..Dec). tg: the cell's growth temperature (C; the
    respiration acclimates to it, RESP_ACCLIM)."""
    eps, t0, t1, t2, t3, amin, top, phen, on_t = kp[0], kp[1], kp[2], kp[3], kp[4], kp[5], kp[6], kp[7], kp[8]
    rl, rw, lma, tleaf, kt, wet, wue, qy, wue0 = kp[9], kp[10], kp[11], kp[12], kp[13], kp[14], kp[16], kp[17], kp[18]
    kn = kp[20]  # canopy leaf-respiration depth constant (0: every leaf respires alike)
    om, df0 = kp[21], kp[22]  # the two-leaf canopy (DIFFUSE; om 0: the big leaf)
    fap_ref = 1.0 - np.exp(-0.5 * LAI_REF)
    w1, w2 = cap1, cap2
    gpp = resp = asum = 0.0
    gref = 0.0  # GPP as it would be at today's CA_REF (the respiration's carbon supply, below)
    dg = min(max(tg - kp[19], -ACCLIM_SPAN), ACCLIM_SPAN)  # C grown warmer than T_GROWN (within ACCLIM_SPAN)
    acc = RESP_ACCLIM * dg  # C the respiration's Q10 term is shifted by
    t2 += PS_ACCLIM * dg  # ... and the high-temperature side of the growth hump
    t3 += PS_ACCLIM * dg
    non = ndry = 0.0
    onj = ona = 0.0
    fap_full = 1.0 - np.exp(-0.5 * lai)
    half = 0.5 * amin
    for m in range(12):
        out[7 + m] = 0.0
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
            q10 = 2.0 ** ((t - 20.0 - acc) / 10.0)
            leaf = lai if (on or phen == 0) else 0.0
            if kn > 0:  # shaded leaves carry less enzyme, so respire less (Vcmax falls as exp(-kn L))
                leaf = (1.0 - np.exp(-kn * leaf)) / kn
            resp += (rl * leaf + rw) * q10 * days[m] / 30.4
            if on:
                fw = (alpha - half) / (1.0 - half)
                fw = min(max(fw, 0.0), 1.0)
                g_m = eps * eff * fap * PAR[m, i] * _ft(t, t0, t1, t2, t3) * fw
                if om > 0:  # sunlit and shaded leaves (DIFFUSE): in place of the big leaf's FPAR
                    mu = MU[m, i]
                    g_m *= fap_ref / fap * _two_leaf(lai, max(DF[m, i], df0), mu, om) / _two_leaf(LAI_REF, df0, mu, om)
                g_r = g_m
                if qy > 0:  # C3 plants: their quantum yield (QY_CROSS, _q3; C3_PFTS: against today's)
                    gs = 42.75 * np.exp(37830.0 * (t - 25.0) / (298.15 * 8.314 * (t + 273.15)))
                    q = max((ci - gs) / (ci + 2.0 * gs), 0.0)
                    q_r = max((CI_REF - gs) / (CI_REF + 2.0 * gs), 0.0)
                    if qy > 1.5:
                        q = q / q_r if q_r > 0 else 0.0
                        q_r = 1.0
                    g_m *= q
                    g_r *= q_r
                if wet == 0 and g_m > wue * dryf * aet:  # no more carbon than the water allows
                    g_m = wue * dryf * aet
                if wet == 0 and g_r > wue0 * dryf * aet:
                    g_r = wue0 * dryf * aet
                gpp += g_m
                gref += g_r
                out[7 + m] = g_m
                asum += alpha
                non += 1.0
                if 3 <= m <= 8:
                    onj += 1.0
                else:
                    ona += 1.0
    # The respiration follows the carbon supply's CO2 factor (PW-806): a plant grown at another CO2 keeps the
    # carbon-use efficiency NPP/GPP it has at today's (Gifford 1995; Dewar et al. 1998; Gifford 2003), so a
    # glacial's lower GPP lowers its NPP in proportion instead of tipping a forest's thin NPP margin below zero.
    if gref > 1e-9:
        resp *= gpp / gref
    npp = 0.75 * (gpp - resp) if gpp > resp else gpp - resp
    out[0] = npp
    out[1] = npp - 1.5 * lma * lai / tleaf
    out[2] = gpp
    out[3] = asum / non if non > 0 else 0.0
    out[4] = ndry
    out[5] = onj
    out[6] = ona


@njit(parallel=True, cache=True)
def _potential(cells, kp, T, W, PET, PAR, DF, MU, cap1, cap2, viable, eff, dryf, tg, lai0, mode, days, ci, grass, res, gmon):
    """Potential NPP of every viable PFT on every cell in cells, at the LAI
    that maximises its net NPP. mode 0: golden-section search over
    (0.05, laimax) (8 evaluations); mode 1: a local step around lai0 (the
    last update's LAI; 3 evaluations), the run's cheap variant. res:
    (8, NP, n): the 7 _year outputs and the LAI; gmon: (len(grass), 12, n),
    the monthly GPP of the PFTs in grass at that LAI."""
    npft = kp.shape[0]
    gr = 0.6180339887
    for jj in prange(len(cells)):
        i = cells[jj]
        out = np.zeros(19)
        best = np.zeros(19)
        for p in range(npft):
            if not viable[p, i]:
                continue
            lmax = kp[p, 15]
            if mode == 1 and lai0[p, i] > 0.05:
                bl, bv = 0.0, -1e30
                for f in (1.0, 0.8, 1.25):
                    x = min(max(lai0[p, i] * f, 0.05), lmax)
                    _year(kp[p], i, x, T, W, PET, PAR, DF, MU, cap1[i], cap2[i], eff[p, i], dryf[i], tg[i], days, ci, out)
                    if out[1] > bv:
                        bv, bl = out[1], x
                        best[:] = out
            else:
                a, b = 0.05, lmax
                c = b - gr * (b - a)
                d = a + gr * (b - a)
                _year(kp[p], i, c, T, W, PET, PAR, DF, MU, cap1[i], cap2[i], eff[p, i], dryf[i], tg[i], days, ci, out)
                fc = out[1]
                bv, bl = fc, c
                best[:] = out
                _year(kp[p], i, d, T, W, PET, PAR, DF, MU, cap1[i], cap2[i], eff[p, i], dryf[i], tg[i], days, ci, out)
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
                    _year(kp[p], i, x, T, W, PET, PAR, DF, MU, cap1[i], cap2[i], eff[p, i], dryf[i], tg[i], days, ci, out)
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
            for j in range(len(grass)):
                if grass[j] == p:
                    for m in range(12):
                        gmon[j, m, i] = best[7 + m]


def potential(s: dict, viable: np.ndarray, eff: np.ndarray, pco2: float = CA_REF, lai0=None,
              cheap: bool = False) -> dict:
    """Potential productivity of each PFT on each cell where viable (NP, n),
    as if it grew alone (section 3.2). eff: (NP, n) efficiency multipliers
    (stand-ins). pco2: the CO2, ppm (climate.pco2 of the run's stock; held
    within CO2_RANGE doublings of today's), sets
    the C3 plants' light-use efficiency through their quantum yield (_q3:
    C3 grass's own, the other C3 types' against today's) and every plant's
    water-use efficiency: carbon gained per water transpired is
    Ca (1 - Ci/Ca) / (1.6 VPD), and Ci/Ca stays near constant (Wong et al.
    1979), so it scales with Ca (PW-644). In a glacial's low CO2 the
    stomata open wider for the same carbon and the plants run dry sooner.
    The respiration follows the CO2's change to the carbon supply (_year:
    NPP/GPP stays today's, PW-806), and acclimates to the cell's growth
    temperature (s["tg"]; RESP_ACCLIM, PS_ACCLIM).
    Returns (NP, n) arrays npp, net, gpp, alpha, dry (months), on_jul,
    on_jan (leaf-on months per half-year), lai; c4_share (n,), the share of
    the grasses' growth that is C4's (the better pathway takes each month);
    and the drought limit applied: a PFT whose growing-season water ratio
    is under its amin is not viable."""
    n = len(s["tc"])
    cells = np.flatnonzero(viable.any(0)).astype(np.int64)
    kp = _KP.copy()
    x = co2_doublings(pco2)
    ci = CI_REF * 2.0 ** x  # Ci = 0.7 Ca
    kp[:, 16] *= 2.0 ** x  # water-use efficiency ~ Ca
    res = np.zeros((8, NP, n))
    gmon = np.zeros((2, 12, n))
    lai = np.zeros((NP, n)) if lai0 is None else np.asarray(lai0, float)
    _potential(cells, kp, s["t"], s["water"], s["pet"], s["par"], s["df"], s["mu"], s["cap1"], s["cap2"], viable,
               np.asarray(eff, float), s["dryair"], s["tg"], lai, 1 if cheap else 0, _DAYS, ci, np.array([C3, C4], np.int64),
               res, gmon)
    out = dict(zip(("npp", "net", "gpp", "alpha", "dry", "on_jul", "on_jan", "lai"), res))
    # the grasses' C4 share: each month's grass growth goes to the pathway that
    # grows better that month (seasonal niches: cool- and warm-season grasses;
    # Still et al. 2003's C4 fraction after Collatz et al. 1998)
    g3, g4 = gmon
    a4 = np.where(g4 > g3, g4, 0.0).sum(0)
    a3 = np.where(g4 > g3, 0.0, g3).sum(0)
    out["c4_share"] = np.where(a3 + a4 > 0, a4 / np.maximum(a3 + a4, 1e-12), 0.5)
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


# The cell scale (lane 274, docs/review/refine-l8/soils.md). The rules that read relief (the wetlands' flat ground and
# floodplains here, the thin buckets on steep ground, the soils' erosion law and slope classes) are written for the
# relief between neighbouring L7 cells, each the mean height of its own ~60 km footprint. A finer grid (a refined
# world, PW-1198) resolves steeper, rougher ground between closer cells: on 899985's L8 refine the neighbour slope is
# ~2x the L7 world's on the same land, and the soils' erosion (~ slope^2) thinned them by a quarter. So a finer grid
# reads its relief at the cell scale, as a zoom's pixel does (soils.zoom_slope): its heights averaged over one
# reference cell's footprint, then the relief to the highest and lowest of those within one reference spacing (k
# rings of its own cells). The L7 grid, and the coarser ones, read their own neighbours as before.
CELL_KM = 60.2  # km: the L7 grid's mean neighbour spacing (Grid.spacing x R_KM), the scale the relief rules are written for


def cell_rings(grid) -> int:
    """How many of the grid's own neighbour rings span one reference spacing (CELL_KM): 1 at L7 and coarser, 2 at
    L8, 4 at L9."""
    from .geo import R_KM
    return max(1, int(round(CELL_KM / (grid.spacing * R_KM))))


def cell_relief(grid, elev) -> np.ndarray:
    """m to the steepest ground one reference cell away (CELL_KM), as relief() reads it on the L7 grid: a finer
    grid's heights first averaged over a reference cell's footprint. One pass of (the cell + half of each
    neighbour) spreads a height over the area of four cells (a reference cell's at k = 2); passes add their
    variance, so a k-ring reference cell (k^2 x as large) takes ~0.74 k^2 / 4 of them."""
    k = cell_rings(grid)
    if k <= 1:
        return relief(grid, elev)
    e = np.asarray(elev, float)
    deg = np.diff(grid.nbr_off)
    for _ in range(max(1, int(round(0.74 * k * k / 4)))):
        e = (e + 0.5 * np.add.reduceat(e[grid.nbr_idx], grid.nbr_off[:-1])) / (1 + 0.5 * deg)
    hi, lo = e, e
    for _ in range(k):
        hi = np.maximum(hi, np.maximum.reduceat(hi[grid.nbr_idx], grid.nbr_off[:-1]))
        lo = np.minimum(lo, np.minimum.reduceat(lo[grid.nbr_idx], grid.nbr_off[:-1]))
    return np.maximum(hi - e, e - lo)


FLOOD_REF = 2.0  # a typical river's flood ratio (peak month / mean month): floodplains as calibrated on the mean flow


def flood_scale(flood_ratio) -> np.ndarray | float:
    """How much bigger than its mean flow a river's flood is, relative to a
    typical river's (hydrology.seasonal_flow's flood_ratio, PW-028; 1
    without one): a spring-flood or monsoon river floods a wider plain than
    a steady, lake-fed one of the same mean flow."""
    if flood_ratio is None:
        return 1.0
    return np.clip(np.asarray(flood_ratio, float), 1.0, 8.0) / FLOOD_REF


def floodplain(grid, elev, flow, rel=None, flood_ratio=None) -> np.ndarray:
    """The share of each cell that is a big river's floodplain or delta
    (part of flooded(); the zoom places it along its own rivers), from its
    flood flow (the mean x flood_scale)."""
    rel = cell_relief(grid, elev) if rel is None else rel
    flat = np.clip(1 - rel / 400.0, 0, 1)
    from .hydrology import discharge
    q = discharge(grid, np.asarray(flow, float)) * flood_scale(flood_ratio)  # m3/s
    return 0.35 * np.clip(np.log10(np.maximum(q, 1.0) / 500.0) / 1.5, 0, 1) * flat


PERMA_WET = np.array([0.0, 0.3, 0.7, 1.0])  # how much of flat ground permafrost keeps from draining, by class (soils.PERMAFROST)


def flooded(grid, elev, flow, lake_kind, s: dict, ice=None, flood_ratio=None, permafrost=None) -> np.ndarray:
    """Share of each land cell (0..0.7) under water for part of the year:
    floodplains and deltas of big rivers, flat ground with a water
    surplus, flat permafrost (which can't drain), and lake shores.
    permafrost: soils.mineral's class (0..3) per cell; without it, ground
    colder than -2 C on average counts as permafrost (the run and the zoom)."""
    from .hydrology import CLOSED_LAKE, OPEN_LAKE
    land = is_land(elev, grid=grid)
    rel = cell_relief(grid, elev)
    flat = np.clip(1 - rel / 400.0, 0, 1)
    plain = floodplain(grid, elev, flow, rel, flood_ratio)
    # flat ground with more rain than evaporation can't drain it all (mires),
    # the more so where it is cool (slow decay builds peat that holds the water)
    mi = s["precip"] / np.maximum(s["pet_y"], 1.0)
    wet = 0.6 * np.clip((mi - 0.9) / 0.6, 0, 1) * flat ** 3 * np.clip((10.0 - s["temp"]) / 10.0, 0.3, 1.0)
    pf = (s["temp"] < -2) if permafrost is None else PERMA_WET[np.asarray(permafrost, int)]
    perma = 0.35 * pf * np.clip(s["precip"] / 400.0, 0, 1) * flat ** 2
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
FUEL_MIN, FUEL_SPAN = 200.0, 350.0  # g C/m2 of fine fuel: no fire below FUEL_MIN, fully fuelled FUEL_SPAN above
# (FUEL_MIN: GlobFIRM's fuel threshold for fire occurrence, 200 g C/m2 of litter, Thonicke et al. 2001, as LPJmL's
# fire module documents it (PIK-LPJmL wiki, "Fire", assumption 1); was 250, tuned while the herbs' NPP ran ~1.4x
# the field values, PW-1328. FUEL_SPAN, the ramp to a fully fuelled cell, is the model's own: GlobFIRM is a step)
# Fuel age (PW-234): shrubs keep their fine litter as dead twigs and leaves in
# and under the crown, which decays like fine woody debris, about half as fast
# as fallen leaf litter (Harmon et al. 1986: twigs k ~0.1-0.3/yr, leaves
# ~0.3-0.7), and builds up again after a fire (Olson 1963's exponential
# approach): chaparral, fynbos and maquis burn every ~10-60 yr, as their dead
# fuel accumulates (Rothermel & Philpot 1973; Keeley et al. 2011), where
# grass fuel is ready every year. fire_rate turns it into a fire interval.
SLOW_FUEL = 0.5  # decay rate of the shrubs' dead fuel, x the litter's
# Crown fire (PW-347): GlobFIRM's steep curve is the curing of a grass layer,
# which needs months of drought; evergreen needleleaf stands carry fire in
# their own resinous, retained foliage and the dry moss and needle bed under
# it, on any run of fire weather, so they add a burned share that rises in
# step with the fire season: CROWN_FIRE a year for a fully conifer cell dry
# all year, x ignition. With 1-2 dry months that is ~1/200 yr, the
# stand-replacing crown fires of the taiga (Stocks et al. 2002: Canada's
# boreal fire cycle ~50-500 yr, shortest in the dry continental interior).
CROWN_FIRE = 0.08
CROWN = np.isin(np.array(CODES), ("TeNE", "BoNE")).astype(np.float64)


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


@njit(cache=True)
def fire_rate(fast, slow, kslow, weather):
    """Burned share per year of a cell (a renewal process: the years a
    burned patch needs to rebuild its fuel past FUEL_MIN, then the wait for
    a fire year). fast: g C/m2 of fuel that is back every year (grass and
    leaf litter in equilibrium with its decay); slow: the equilibrium stock
    of the shrubs' dead fuel, which a patch regains as slow x (1 -
    e^(-kslow age)); weather: the burned share a fully fuelled cell would
    have (globfirm x ignition). Fuel-free or fire-free cells: 0."""
    full = fast + slow
    if weather <= 0.0 or full <= FUEL_MIN:
        return 0.0
    r = weather * min((full - FUEL_MIN) / FUEL_SPAN, 1.0)
    ready = 0.0
    if fast < FUEL_MIN:
        ready = -np.log(1.0 - (FUEL_MIN - fast) / slow) / kslow
    return 1.0 / (ready + 1.0 / r)


MIGRATE_PRESENT = 0.03  # cover (with the seed) of an established stand that can seed its neighbours


@njit(parallel=True, cache=True)
def _step(cells, nu, g, K, ok, mort, C, resist, litter, slowf, crown, season, kdec, kslow, ign, dt, seed, diff, nbr_off, nbr_idx,
          food, browsed, graze, c4_share, mig, src, out, burned):
    """One implicit step of the cover equations on every cell in cells:
    dnu/dt = g nu (K - sum_q C_pq nu_q) - (mort + fire (1 - resist)) nu,
    plus seeds (every viable type keeps at least `seed`) and a little
    spread from neighbours (diff). Fire from this cover's fuel (fire_rate;
    slowf: 1 for the types whose dead fuel builds up slowly, the shrubs;
    crown: 1 for the types that carry crown fire, CROWN_FIRE x season x their cover).
    The C3 and C4 grasses are one grass layer, split by c4_share.
    mig (per type; the time zoom's and the finished world's, PW-213): 0 seeds everywhere; 1 keeps its seeds
    only where the type already is and takes new ground only beside a neighbour with an established stand
    (MIGRATE_PRESENT in src: the stands as they were when the step began), at most one cell per step; 2 only stays
    where it is."""
    npft = nu.shape[0]
    for jj in prange(len(cells)):
        i = cells[jj]
        fast = 0.0
        slow = 0.0
        cc = 0.0
        for p in range(npft):
            cc += crown[p] * nu[p, i]
            if slowf[p] > 0:
                slow += nu[p, i] * litter[p, i]
            else:
                fast += nu[p, i] * litter[p, i]
        wx = (globfirm(season[i]) + CROWN_FIRE * season[i] * min(cc, 1.0)) * ign[i]
        a = fire_rate(fast / kdec[i], slow / kslow[i], kslow[i], wx)
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
            if mig[p] > 0:
                here = nu[p, i] > 0.0
                if not here and mig[p] == 1:
                    for k in range(n0, n1):
                        if src[p, nbr_idx[k]] > MIGRATE_PRESENT:
                            here = True
                            break
                out[p, i] = max(v, seed) if here else 0.0
            else:
                out[p, i] = max(v, seed)
        if ok[C3, i] and ok[C4, i]:
            tot = out[C3, i] + out[C4, i]
            if tot <= 0.0:
                continue
            out[C4, i] = max(tot * c4_share[i], seed)
            out[C3, i] = max(tot * (1.0 - c4_share[i]), seed)


@njit(parallel=True, cache=True)
def _merge(cells, nu, out, tol, act):
    """After a whole step from nu into out: the cells it changed by more than tol are marked in act and
    both arrays hold their old state there (to take the step again in shorter ones); elsewhere both hold the step's result."""
    for jj in prange(len(cells)):
        i = cells[jj]
        d = 0.0
        for p in range(nu.shape[0]):
            d = max(d, abs(out[p, i] - nu[p, i]))
        if d > tol:
            act[i] = True
            for p in range(nu.shape[0]):
                out[p, i] = nu[p, i]
        else:
            for p in range(nu.shape[0]):
                nu[p, i] = out[p, i]


@njit(parallel=True, cache=True)
def _strip(x, seed, out):
    """equilibrium's cover with the seeds taken off: a type under twice the seed is gone, and a cell over full
    (the sum over its types above 1) is scaled down to 1."""
    for i in prange(x.shape[1]):
        tot = 0.0
        for k in range(x.shape[0]):
            v = x[k, i] - seed if x[k, i] > 2 * seed else 0.0
            out[k, i] = v
            tot = v if k == 0 else tot + v
        if tot > 1:
            d = tot if tot > 1e-9 else 1e-9
            for k in range(x.shape[0]):
                out[k, i] = out[k, i] / d


@njit(parallel=True, cache=True)
def _equilibrium_prep(pot_ok, land, fw, npp, net, cap, wet, flood, carbon, litf, trees, herbs, mig, nu0, no_nu0,
                      start_trees, start_herbs, seed, npp_full, g, K, litter, nu, ok, any_ok):
    """equilibrium's set-up in one pass per cell, in place of ~25 (NP, n) temporaries: where each type may grow
    (ok), its net growth per unit carbon (g), its room (K) and litter, and the starting cover (nu)."""
    for i in prange(fw.shape[0]):
        nt = nh = 0
        anyk = False
        for k in range(pot_ok.shape[0]):
            o = pot_ok[k, i] and land[i] and (wet[k] == 0 or fw[i] > 0.01)
            ok[k, i] = o
            anyk = anyk or o
            if o and trees[k]:
                nt += 1
            if o and herbs[k]:
                nh += 1
        any_ok[i] = anyk
        nt, nh = max(nt, 1), max(nh, 1)
        for k in range(pot_ok.shape[0]):
            pm = npp[k, i] if npp[k, i] > 0.0 else 0.0
            cost = carbon[k] * min(max(pm / npp_full, 0.3), 1.0)
            g[k, i] = (net[k, i] if net[k, i] > 0.0 else 0.0) / cost
            kk = fw[i] if wet[k] > 0 else 1.0 - fw[i] * (1.0 - flood[k])
            K[k, i] = min(kk, cap[i]) if trees[k] else kk
            litter[k, i] = pm * litf[k]
            if no_nu0:
                v = start_trees / nt if trees[k] else (start_herbs / nh if herbs[k] else 0.0)
            else:
                v = nu0[k, i]
            nu[k, i] = (v if mig[k] > 0 else max(v, seed)) if ok[k, i] else 0.0


def equilibrium(grid, s: dict, pot: dict, fw: np.ndarray, land: np.ndarray, nu0=None, steps=None,
                diff: float = 0.02, migrate=None, snaps=(), substeps: int = 1, crown: bool = True) -> dict:
    """The cover fractions (NP, n) in equilibrium with the climate (section
    3.3), warm-started from nu0 (the previous state: history decides
    between forest and savanna), with fire. steps: list of (count, dt in
    years); default 30 x 2 yr then 40 x 10 yr. Returns nu (fractions, the
    seeds taken off), burned (share per year), and the growth rates.
    migrate (PW-213): None, or per type 0/1/2 (see _step): the types that spread cell by cell from where they
    are (or stay) instead of being seeded everywhere; nu0 is then the previous call's nu_raw (with the seeds,
    so a type that is still in a cell stays) or a stand map (0 = not there); substeps: each step is this many
    shorter ones (the implicit step caps a young stand's growth per step, so a long step grows it too slowly),
    migration seeing the stands as the step began; snaps: step counts (cumulative over steps) after which the cover is also returned, in snaps.
    crown: the conifers' crown fire (CROWN_FIRE; the simulation's climate steps leave it off for now, so runs keep
    their pre-PW-347 fire until the run physics take it up)."""
    n = grid.n
    mort = _col("gamma")
    # water caps tree cover: in dry climates the canopy can't close (Sankaran et al. 2005)
    cap = np.clip((s["mi"] - 0.05) / 0.4, 0.0, 1.0)
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
    mig = np.zeros(NP, np.uint8) if migrate is None else np.asarray(migrate, np.uint8)
    # where each type may grow (ok), what it costs and gains (g: a square metre of a type costs less where it grows
    # poorly, stunted trees at the treeline hold far less carbon than a lowland forest), the room it has (K: the
    # flooded share belongs to the wetland types), its litter, and the start state (one fused pass)
    prep = tuple(np.empty((NP, n)) for _ in range(3)) + (np.empty((NP, n)), np.empty((NP, n), np.bool_), np.empty(n, np.bool_))
    g, K, litter, nu, ok, any_ok = prep
    _equilibrium_prep(pot["ok"], land, fw, pot["npp"], pot["net"], cap, _col("wet"), _col("flood"), _col("carbon"),
                      _col("litf"), TREES, HERBS, mig, np.zeros((1, 1)) if nu0 is None else np.asarray(nu0, float),
                      nu0 is None, START["trees"], START["herbs"], seed, NPP_FULL, g, K, litter, nu, ok, any_ok)
    cells = np.flatnonzero(any_ok).astype(np.int64)
    out = np.zeros_like(nu)  # (zeros, not empty: _step writes only `cells`, and reads their neighbours)
    burned = np.zeros(n)
    C, resist = _C, _col("resist")
    slowf = SHRUBS.astype(np.float64)
    c4s = np.asarray(pot.get("c4_share", np.full(n, 0.5)), np.float64)
    def strip(x):
        out_ = np.empty(x.shape)
        _strip(x, seed, out_)
        return out_
    snapped, k = [], 0
    for count, dt in steps or ((30, 2.0), (150, 10.0)):
        for _ in range(count):
            args = (g, K, ok, mort, C, resist, litter, slowf, CROWN if crown else 0.0 * CROWN, season, kdec, SLOW_FUEL * kdec, ign)
            nbr = (seed, diff, grid.nbr_off, grid.nbr_idx, food, browsed, graze, c4s, mig)
            if substeps <= 1:
                _step(cells, nu, *args, float(dt), *nbr, nu, out, burned)
                nu, out = out, nu
            else:
                # one whole step finds the cells that change (the rest take its result); those take the step
                # in `substeps` shorter ones, migration seeing the stands as the step began
                src = nu.copy()
                _step(cells, nu, *args, float(dt), *nbr, src, out, burned)
                act = np.zeros(n, np.bool_)
                _merge(cells, nu, out, 0.002, act)
                sub = np.flatnonzero(act)
                for _s in range(substeps):
                    _step(sub, nu, *args, float(dt) / substeps, *nbr, src, out, burned)
                    nu, out = out, nu
            k += 1
            if k in snaps:
                snapped.append(strip(nu))
    return dict(nu=strip(nu), nu_raw=nu, snaps=snapped, burned=np.where(land, burned, 0.0), g=g, season=season)


# ---------------------------------------------------------------------------
# Summary fields and the named types
# ---------------------------------------------------------------------------
CLOSED = 2.5  # LAI at which a canopy shades all the ground under it


@njit(parallel=True, cache=True)
def _summary_a(nu, lai_p, npp_p, on_jul, on_jan, trees, shrubs, herbs, grounds, evg, resist, mort, tau, den,
               shade, cover, tree, shrub, herb, ground, lai, l_jul, l_jan, npp, biomass, r_tree, m_tree):
    """summary's sums over the plant types, one pass per cell with no (NP, n) temporaries. The types are added in
    order from the first, as numpy's axis-0 sums add them, so the results are bit-identical."""
    for i in prange(nu.shape[1]):
        c = a_npp = a_lai = a_jul = a_jan = a_bio = 0.0
        t = sh = he = gr = nt = rt = mt = 0.0
        f_c = f_n = f_l = f_j = f_a = f_b = False
        f_t = f_s = f_h = f_g = f_nt = False
        for k in range(nu.shape[0]):
            v = nu[k, i]
            lp = lai_p[k, i]
            x = min(max(lp / den[k], 0.0), 1.0)
            sd = v * x
            shade[k, i] = sd
            c = sd if not f_c else c + sd
            f_c = True
            pp = npp_p[k, i]
            pm = pp if pp > 0.0 else 0.0
            w = v * pm
            a_npp = w if not f_n else a_npp + w
            f_n = True
            w = v * lp
            a_lai = w if not f_l else a_lai + w
            f_l = True
            wj = v * lp * (1.0 if evg[k] else on_jul[k, i] / 6.0)
            a_jul = wj if not f_j else a_jul + wj
            f_j = True
            wa = v * lp * (1.0 if evg[k] else on_jan[k, i] / 6.0)
            a_jan = wa if not f_a else a_jan + wa
            f_a = True
            wb = v * pm * tau[k]
            a_bio = wb if not f_b else a_bio + wb
            f_b = True
            if trees[k]:
                t = sd if not f_t else t + sd
                f_t = True
                w = v * resist[k]
                rt = w if not f_nt else rt + w
                w = v * mort[k]
                mt = w if not f_nt else mt + w
                nt = v if not f_nt else nt + v
                f_nt = True
            if shrubs[k]:
                sh = sd if not f_s else sh + sd
                f_s = True
            if herbs[k]:
                he = sd if not f_h else he + sd
                f_h = True
            if grounds[k]:
                gr = sd if not f_g else gr + sd
                f_g = True
        cover[i], tree[i], shrub[i], herb[i], ground[i] = c, t, sh, he, gr
        lai[i], l_jul[i], l_jan[i], npp[i], biomass[i] = a_lai, a_jul, a_jan, a_npp, a_bio * 0.01
        d = nt if nt > 1e-9 else 1e-9
        r_tree[i], m_tree[i] = rt / d, mt / d


@njit(parallel=True, cache=True)
def _summary_height(nu, lai_p, laimax, hmax, trees, tf, height):
    """summary's canopy height: the tallest type with cover over 0.1 (tf: the trees' 1 - exp(-stand / 60))."""
    for i in prange(nu.shape[1]):
        best = 0.0
        first = True
        for k in range(nu.shape[0]):
            if nu[k, i] > 0.1:
                h = hmax[k] * np.sqrt(min(max(lai_p[k, i] / laimax[k], 0.0), 1.0)) * (tf[i] if trees[k] else 1.0)
            else:
                h = 0.0
            if first or h > best:
                best = h
            first = False
        height[i] = best


def summary(s: dict, pot: dict, eq: dict) -> dict:
    """Per-cell structure from the fractions: cover, tree cover, LAI (and
    per half-year), NPP, biomass, canopy height, fire return interval and
    stand age."""
    nu = eq["nu"]
    lai_p = pot["lai"]
    b = eq["burned"]
    ins = (nu, lai_p, pot["npp"], pot["on_jul"], pot["on_jan"])
    if not all(isinstance(a, np.ndarray) and a.dtype == np.float64 and a.ndim == 2 and a.flags.c_contiguous
               and a.shape == nu.shape for a in ins) or b.dtype != np.float64:
        return _summary_numpy(s, pot, eq)
    n = nu.shape[1]
    shade = np.empty(nu.shape)
    o = {k: np.empty(n) for k in ("cover", "tree", "shrub", "herb", "ground", "lai", "l_jul", "l_jan", "npp",
                                   "biomass", "r_tree", "m_tree")}
    # (a type's share of the cell the canopy shades: a sparse canopy, LAI under CLOSED, covers part of its share)
    _summary_a(nu, lai_p, pot["npp"], pot["on_jul"], pot["on_jan"], TREES, SHRUBS, HERBS, GROUNDS, _col("phen") == EVERGREEN,
               _col("resist"), _col("gamma"), _col("tau"), np.where(GROUNDS, 1.0, CLOSED), shade,
               o["cover"], o["tree"], o["shrub"], o["herb"], o["ground"], o["lai"], o["l_jul"], o["l_jan"],
               o["npp"], o["biomass"], o["r_tree"], o["m_tree"])
    tree = o["tree"]
    stand = np.where(tree > 0.05, 1.0 / np.maximum(b * (1 - o["r_tree"]) + o["m_tree"], 1e-4), 1.0 / (b + 0.1))
    height = np.empty(n)
    _summary_height(nu, lai_p, _col("laimax"), _col("hmax"), TREES, 1 - np.exp(-stand / 60.0), height)
    return dict(cover=o["cover"], tree=tree, shrub=o["shrub"], herb=o["herb"], ground=o["ground"], shade=shade,
                lai=o["lai"], lai_jul=o["l_jul"], lai_jan=o["l_jan"], npp=o["npp"], biomass=o["biomass"],
                height=height, fire_return=np.where(b > 1e-4, 1.0 / np.maximum(b, 1e-9), 0.0),
                stand_age=np.minimum(stand, 2000.0))


def _summary_numpy(s: dict, pot: dict, eq: dict) -> dict:
    """summary() in plain numpy (for inputs that are not float64 (NP, n) arrays; the reference of the kernels)."""
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


def tree_cover(pot: dict, nu: np.ndarray) -> np.ndarray:
    """summary()['tree'] alone: the ground the trees' canopies shade (0..1), for cover fractions nu."""
    return (nu[TREES] * np.clip(pot["lai"][TREES] / CLOSED, 0, 1)).sum(0)


COASTAL_MIN = 0.3  # share of a cell under mangroves or salt marsh that names it so (proposal section 2.3, rule 2)


def classify(s: dict, eq: dict, sm: dict, elev, ice=None, lake=None, lake_kind=None, fw=None,
             coastal=None) -> np.ndarray:
    """Named vegetation type (TYPES id) per cell: the first rule that holds
    (section 2.3): ice and lakes, coastal (mangrove forest or salt marsh
    over COASTAL_MIN of the cell: coastal's shares 0..1, coastal.py),
    non-vegetated, wetland, forest (trees >= 60%), woodland and savanna
    (10-60%), sparse, shrubland, grassland."""
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
    summer_dry = (np.asarray(s["summer_drought"]) > 0) & (tc > -3)
    cloud = s["cloud"] if s.get("cloud") is not None else np.clip(P / 3000.0, 0, 1)
    trop_tree = f["TrBE"] + f["TrBR"]
    out = np.full(n, -1)

    def put(mask, tid):
        sel = mask & (out < 0)
        out[sel] = tid[sel] if np.ndim(tid) else tid

    put(~is_land(elev, ice), 0)  # (the sea; a bed below it under grounded ice is land: ice)
    if ice is not None:
        put(np.asarray(ice) > 0, T["ice"])
    if lake is not None:
        put(np.asarray(lake).astype(bool), T["lake"])
    # 2. coastal: mangroves or salt marsh between the tides (coastal.py; PW-188, PW-209)
    if coastal is not None:
        mang, marsh = (np.asarray(coastal.get(k, np.zeros(n)), float) for k in ("mangrove", "salt_marsh"))
        put((mang >= COASTAL_MIN) & (mang >= marsh), T["mangrove forest"])
        put(marsh >= COASTAL_MIN, T["salt marsh"])
        put(mang >= COASTAL_MIN, T["mangrove forest"])
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
    # (a tropical climate's forest whose biggest share is tropical trees is tropical forest,
    # even where warm-temperate trees together outnumber them, as in the lower montane belt)
    trop = trop | ((dom <= 1) & tropical_lat)
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
    # (boreal-named woodland needs a boreal climate: cold winters and short, cool
    # summers; birch and pine woodland elsewhere is named by its climate below)
    subarctic = (tc < -2) & ((tw < 16) | (s["gdd5"] < 1000))
    put(wood & boreal & (s["gdd5"] < 600) & (tree < 0.3), T["forest-tundra"])
    put(wood & boreal & subarctic & (f["Moss"] >= 0.15), T["lichen woodland"])
    put(wood & boreal & subarctic & (f["C3G"] >= 0.25), T["forest steppe"])
    put(wood & boreal & subarctic, T["lichen woodland"])
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
    # sclerophyll scrub is Mediterranean where the summer is dry; elsewhere it is
    # semi-arid (mallee, mulga), a cold steppe's (sagebrush) or a humid thicket
    put(shrubby & (sdom == 0) & summer_dry, T["Mediterranean scrub (maquis, chaparral, fynbos)"])
    put(shrubby & (sdom == 0) & (tc < 0) & (mi < 0.5), T["shrub steppe"])
    put(shrubby & (sdom == 0) & (mi < 0.65), T["dry sclerophyll scrub (mallee, mulga)"])
    put(shrubby & (sdom == 0), T["temperate scrub and thicket"])
    put(shrubby & (sdom == 1) & (tc < 0), T["cold desert scrub"])
    put(shrubby & (sdom == 1) & (cover < 0.45), T["hot desert scrub"])
    put(shrubby & (sdom == 1), T["semi-desert grassland"])
    put(shrubby & (sdom >= 2) & alpine, T["alpine scrub (krummholz)"])
    put(shrubby & (sdom == 2) & tundra, T["shrub tundra"])
    put(shrubby & (sdom == 3) & tundra, T["dwarf-shrub and lichen tundra"])
    put(shrubby & (sdom == 3) & (mi >= 0.7), T["heathland and moorland"])
    put(shrubby & (sdom == 3), T["shrub steppe"])
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
    # (before grasses exist: moss and crust carpets where something like them would grow)
    put(~grassy & (f["Moss"] + f["Sph"] >= 0.25), T["moss and crust carpet"])
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
          lake_kind=None, lake=None, ice=None, nu0=None, lai0=None, pco2: float = CA_REF, unlocked=None,
          cheap: bool = False, steps=None, locked_potential: bool = False, flood_ratio=None, coastal=None,
          soil: dict | None = None, migrate=None, snaps=(), substeps: int = 1, crown: bool = True,
          sky=None) -> dict:
    """Vegetation in equilibrium with a climate. Inputs are per-cell
    arrays (climate.compute's names; cloud_jul / cloud_jan: the cloud as the light sees it, compute's
    shade_jul / shade_jan; sky: (cloud_jul, cloud_jan), the sky's cover, which names the montane cloud
    forests, default the light's; flood_ratio: the rivers' peak month
    over their mean, hydrology.seasonal_flow); nu0, lai0: (NP, n) warm starts;
    unlocked: (NP,) bool, the PFTs that exist (default all; the rest are
    stood in for, STANDINS). soil: soils.mineral's result (the buckets
    cap1/cap2, the fertility factor f_soil on each stand's NPP and permafrost; PW-185), else
    fixed buckets (TOP_MM, DEEP_MM, thinner on steep ground: the run and the zoom). cheap: the run's variant (local LAI step,
    fewer competition steps). locked_potential: also compute the locked
    PFTs' potential (for flora_update's niches). coastal: the coastal-life
    shares (0..1) "mangrove" and "salt_marsh" (coastal.world_layers) that
    name a cell mangrove forest or salt marsh (classify). Returns a dict with the
    site s, the potential pot, eq (nu, burned), the flooded share fw, the
    summary sm and the named types."""
    n = grid.n
    elev = np.asarray(elev, float)
    ice = np.zeros(n) if ice is None else np.asarray(ice, float)
    land = is_land(elev, grid=grid) & (ice <= 0)
    if lake is not None:
        land &= ~np.asarray(lake).astype(bool)
    unlocked = all_unlocked() if unlocked is None else np.asarray(unlocked, bool)
    rel = cell_relief(grid, elev)
    s = site(grid.lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, cloud_jul, cloud_jan, rel)
    if sky is not None:
        s["cloud"] = 0.5 * (np.asarray(sky[0], float) + np.asarray(sky[1], float))
    if soil is not None:
        s["cap1"], s["cap2"] = soil["cap1"], soil["cap2"]
    env = envelope(s, pco2) & land[None, :]
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
    pot_all = potential(s, viable_c, eff, pco2, lai0, cheap)
    if soil is not None:  # the soil's fertility factor scales each stand's NPP (decision 6A: 0.85-1.1 on plants)
        fs = np.asarray(soil["f_soil"], float)[None, :]
        pot_all = dict(pot_all, npp=pot_all["npp"] * fs, net=pot_all["net"] * fs)
    pot = dict(pot_all, ok=pot_all["ok"] & viable)
    fw = flooded(grid, elev, np.zeros(n) if flow is None else flow, np.zeros(n) if lake_kind is None else lake_kind,
                 s, ice, flood_ratio, None if soil is None else soil["permafrost"])
    eq = equilibrium(grid, s, pot, fw, land, nu0, steps or (((25, 10.0),) if cheap else None), migrate=migrate, snaps=snaps,
                     substeps=substeps, crown=crown)
    sm = summary(s, pot, eq)
    types = classify(s, eq, sm, elev, ice, lake, lake_kind, fw, coastal)
    return dict(s=s, pot=pot, pot_all=pot_all, eq=eq, fw=fw, sm=sm, types=types, land=land, unlocked=unlocked)


# Migration (PW-213): the trees are the slow spreaders (100-500 m/yr after the ice; shrubs and herbs seed
# fast on the time scale of a frame, 2 kyr), so only they are limited to ground beside their own stands
# (SPREAD: the time zoom's cover) or to the ground they hold (HELD: a finished world, which then runs
# HELD_STEPS to settle on its own climate: ~2 kyr, so a front doesn't move on).
SPREAD = TREES.astype(np.uint8)
HELD = 2 * SPREAD
HELD_STEPS = ((8, 250.0),)


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


def rooted_cover(nu) -> np.ndarray:
    """0..1 per cell: the share of the ground under rooted (vascular) plants, the trees', shrubs' and herbs' cover
    fractions nu (NP, n) summed; mosses, lichens and soil crusts (the GROUND types) left out. What the weathering's
    plant factor reads (tectonics.earth.plant_factor, PW-1424 C): roots, their fungi and the soil CO2 they make are
    there or not, whatever the plants' carbon budget (GEOCARB's f_E is about vascular plants being there)."""
    if nu is None:
        return None
    return np.clip(np.asarray(nu, np.float64)[~GROUNDS].sum(0), 0.0, 1.0)


# Surface albedo (snow-free) of each type's canopy, and the share of lying snow
# its canopy hides (dark trees standing out of the snow: Bonan 1992; Betts &
# Ball 1997), for climate.compute's feedbacks (section 4.2)
ALBEDO = {"TrBE": 0.12, "TrBR": 0.15, "TeBE": 0.13, "TeBS": 0.16, "TeNE": 0.10, "BoNE": 0.09, "BoNS": 0.13,
          "BoBS": 0.16, "SclS": 0.16, "XerS": 0.20, "DecS": 0.17, "HthS": 0.15, "C4G": 0.19, "C3G": 0.19,
          "TunH": 0.18, "Succ": 0.20, "Moss": 0.17, "WetH": 0.16, "Sph": 0.14}
ALBEDO_BARE = 0.30  # bare soil, rock and sand (desert sand ~0.35-0.45, dark soil ~0.15)
SNOW_MASK = np.where(TREES, np.where(_col("phen") == EVERGREEN, 0.75, 0.45), np.where(SHRUBS, 0.2, 0.0))
DEEP = TREES & (_col("phen") == EVERGREEN)  # deep-rooted evergreen trees (Budyko w, section 4.1)


def feedback(nu, lai_p) -> dict:
    """What the climate needs from the vegetation (climate.compute's veg;
    section 4), from the cover fractions nu (NP, n) and each type's LAI
    lai_p (NP, n), per cell (0 where nothing grows):
      woody   tree + shrub cover (the ground their canopies shade)
      deep    of it, deep-rooted evergreen trees
      lai     total leaf area index
      albedo  snow-free surface albedo (bare ground ALBEDO_BARE)
      mask    share of lying snow the canopies hide"""
    nu = np.asarray(nu, np.float64)
    lai_p = np.asarray(lai_p, np.float64)
    closed = np.clip(lai_p / np.where(GROUNDS, 1.0, CLOSED)[:, None], 0, 1)
    shade = nu * closed
    cover = np.clip(shade.sum(0), 0, 1)
    alb = np.array([ALBEDO[c] for c in CODES])
    return dict(woody=shade[TREES | SHRUBS].sum(0), deep=shade[DEEP].sum(0), lai=(nu * lai_p).sum(0),
                albedo=(shade * alb[:, None]).sum(0) + (1 - cover) * ALBEDO_BARE,
                mask=np.clip((shade * SNOW_MASK[:, None]).sum(0), 0, 1))


def coupled_climate(grid, elev, dT: float = 0.0, tilt: float = 23.4, ice=None, nu0=None, pco2: float = CA_REF,
                    unlocked=None) -> tuple[dict, dict]:
    """climate.compute with the vegetation's feedbacks, as a world gets
    them (world.finish): the climate, a first cheap vegetation on it, then
    the climate again with that vegetation. Returns (climate, feedback)."""
    c = climate.compute(grid, elev, dT, tilt, ice)
    v = model(grid, elev, c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"], tilt, c["shade_jul"],
              c["shade_jan"], ice=ice, nu0=nu0, pco2=pco2, unlocked=unlocked, cheap=True)
    fb = feedback(v["eq"]["nu"], v["pot"]["lai"])
    return climate.compute(grid, elev, dT, tilt, ice, veg=fb), fb


def bare(n: int) -> dict:
    """feedback() of land with no plants (before land plants appear)."""
    z = np.zeros(n)
    return dict(woody=z, deep=z, lai=z, albedo=np.full(n, ALBEDO_BARE), mask=z)


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


def flora_update(times: list, t: float, dt: float, now: float, niche: np.ndarray, rng) -> list:
    """New appearance times (Myr; NaN: not yet) of the plant groups at a
    climate update at time t, dt Myr after the last. A group may appear
    from the start of its window (group_windows) once the one before it
    exists, with a chance per update proportional to its niche, times a
    ramp that reaches certainty at the window's end."""
    times = list(times)
    win = group_windows(now)
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
