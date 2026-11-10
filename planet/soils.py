"""Soils (PW-185; design and owner decisions: docs/proposals/soils.md).

Every land cell of a world gets a soil: one of 19 named types (WRB groups,
some merged, named for a player) plus continuous fields (depth, texture,
water capacity, fertility, drainage, soil carbon, peat, permafrost, loess).
Two short passes sit either side of the vegetation (world.finish):

1. mineral(): parent material (rock, loess, alluvium, till), an erosion
   estimate from relief and rain, soil depth and age (soil production after
   Heimsath et al. 1997, capped by glaciation, eruption and deposition
   ages), the weathering stage W, texture, water capacity, fertility,
   permafrost and loess (dust from deserts and ice margins blown downwind).
   It needs only geology and climate; vegetation then reads its water
   capacity (cap1, cap2), a mild fertility factor (f_soil) and permafrost.
2. organic(): soil carbon from the vegetation's litter (NPP) and a decay
   rate (CENTURY's logic), peat on the flooded share (Clymo 1984), then the
   classification (ordered rules, first that holds).

The order is fixed, so there is no loop (decision 5A): organic matter shows
in the displayed fertility only. No state is carried between worlds. A
world from a run can average the run's keyframe climate over each soil's
age (climate_memory; decision 3B), so relic deep-weathered soils survive a
climate change.
"""

from __future__ import annotations

import numpy as np

from . import climate
from .geo import R_KM, arc_km, is_land
from .hydrology import CLOSED_LAKE, OPEN_LAKE, SALT_PAN

# ---------------------------------------------------------------------------
# The types (decision 1A): id, key, player name, WRB / USDA, colour, one line
# ---------------------------------------------------------------------------
TYPES = [
    (0, "none", "no soil", "-", "-", "#8a8a8a", "Ice, lake water or bare rock."),
    (1, "peat", "peat", "Histosol", "Histosol", "#4a3326",
     "Wet, spongy, dark: plant remains piled up for thousands of years where the water never drains."),
    (2, "frozen", "frozen tundra soil", "Cryosol", "Gelisol", "#8aa3b4",
     "Frozen within a metre of the surface; it heaves into polygons and thaws to mud each summer."),
    (3, "thin", "thin stony soil", "Leptosol", "Entisol (lithic)", "#b9ab93",
     "A few handfuls of soil between the stones: steep slopes, fresh lava, ice-scoured rock."),
    (4, "salt", "salt-crusted soil", "Solonchak / Solonetz", "Aridisol (salid)", "#ece7d4",
     "White salt crusts where water comes up and evaporates; little but saltbush grows."),
    (5, "alluvium", "river-laid alluvium", "Fluvisol", "Entisol (fluvent)", "#5aa59c",
     "Fresh silt laid by floods every few years: young, deep and among the richest ground there is."),
    (6, "gley", "waterlogged grey clay", "Gleysol", "Inceptisol (aquept)", "#6d8fa6",
     "Grey and blue-mottled clay, soaked most of the year: wet meadows and swamp forest."),
    (7, "andosol", "volcanic ash soil", "Andosol", "Andisol", "#7d3550",
     "Light, dark and fluffy soil on fresh volcanic ash: holds water and feeds crops like nothing else."),
    (8, "sand", "loose sand", "Arenosol", "Entisol (psamment)", "#efd897",
     "Loose sand that holds little water or food: dune fields and sandy plains."),
    (9, "gypsic", "desert pavement soil", "Gypsisol", "Aridisol (gypsid)", "#e6c58e",
     "Gravel pavement over gypsum: the driest deserts, where rain almost never soaks in."),
    (10, "calcic", "caliche desert soil", "Calcisol", "Aridisol (calcid)", "#d6b37a",
     "A hard white lime layer a foot down: dry country where the rain can't wash the lime out."),
    (11, "vertisol", "cracking black clay", "Vertisol", "Vertisol", "#5d4c60",
     "Heavy dark clay that swells when wet and cracks open in the dry season."),
    (12, "chestnut", "chestnut steppe soil", "Kastanozem", "Mollisol (ustoll)", "#9d6e3c",
     "Brown, crumbly grassland soil of the dry steppes: good grazing, grain in wet years."),
    (13, "chernozem", "black earth", "Chernozem / Phaeozem", "Mollisol (udoll)", "#2b2420",
     "Deep, dark, crumbly and rich: the world's breadbaskets, built by grass roots."),
    (14, "podzol", "ash-grey podzol", "Podzol", "Spodosol", "#b4b3aa",
     "An ash-grey layer bleached by acid litter over a rusty one: poor sandy soils of cool forests and heaths."),
    (15, "rendzina", "dark limestone soil", "Leptosol (rendzic)", "Mollisol (rendoll)", "#55604c",
     "Shallow, dark, lime-rich soil straight on limestone: chalk downs and karst uplands."),
    (16, "ferralsol", "leached red tropical soil", "Ferralsol", "Oxisol", "#cf4b22",
     "Deep red earth weathered for millions of years: only iron and aluminium are left, so it is poor."),
    (17, "acrisol", "red clay forest soil", "Acrisol / Lixisol", "Ultisol", "#df8a52",
     "Red and yellow clay under warm forests: acid and leached, fertile only in its thin topsoil."),
    (18, "luvisol", "brown forest soil", "Luvisol", "Alfisol", "#b07e4e",
     "Brown soil with clay washed into the subsoil: the fertile farmland of temperate forests."),
    (19, "cambisol", "young brown soil", "Cambisol / Regosol", "Inceptisol", "#d2b26e",
     "Young, moderately weathered brown soil: hill country, mountains and recently glaciated plains."),
]
(NONE, PEAT, FROZEN, THIN, SALT, ALLUVIUM, GLEY, ANDOSOL, SAND, GYPSIC, CALCIC, VERTISOL, CHESTNUT, CHERNOZEM,
 PODZOL, RENDZINA, FERRALSOL, ACRISOL, LUVISOL, CAMBISOL) = range(len(TYPES))
TEXTURES = ["none", "sand", "loam", "silt", "clay", "peat"]
TX_NONE, TX_SAND, TX_LOAM, TX_SILT, TX_CLAY, TX_PEAT = range(len(TEXTURES))
DRAINAGE = ["", "excessive", "well", "moderate", "poor", "very poor"]
PERMAFROST = ["none", "sporadic", "discontinuous", "continuous"]

# ---------------------------------------------------------------------------
# Parent material (section 3.1), per surface.ROCKS id:
# texture class, available water (mm per m of soil), base richness 0..1
# (calcium, magnesium, potassium released), and what the rock makes:
# sandy (sand, podzols), acid (podzols), clayey (vertisols), calcareous
# (rendzinas), andic (ash: andosols while young), salty (salt soils).
# ---------------------------------------------------------------------------
AWC_SAND, AWC_SANDY_LOAM, AWC_LOAM, AWC_SILT, AWC_CLAY, AWC_PEAT = 70.0, 110.0, 150.0, 200.0, 130.0, 300.0
_P = {  # rock key: (texture, awc, base, flags)
    "ocean": (TX_CLAY, AWC_CLAY, 0.85, "clayey"),
    "hotspot": (TX_CLAY, AWC_CLAY, 0.85, "clayey"),
    "arc": (TX_LOAM, AWC_LOAM, 0.8, ""),
    "sediment": (TX_LOAM, AWC_LOAM, 0.55, "soft"),  # generic sedimentary rock and unconsolidated sediment (GLiM)
    "orogen": (TX_LOAM, AWC_SANDY_LOAM, 0.35, "acid"),
    "craton": (TX_LOAM, AWC_SANDY_LOAM, 0.35, "acid"),
    "limestone": (TX_CLAY, AWC_CLAY, 0.9, "calcareous"),
    "sandstone": (TX_SAND, AWC_SAND, 0.2, "sandy acid"),
    "shale": (TX_CLAY, AWC_CLAY, 0.55, "clayey"),
    "evaporite": (TX_LOAM, AWC_LOAM, 0.5, "salty"),
    "coal": (TX_LOAM, AWC_LOAM, 0.2, "acid"),
    "granite": (TX_LOAM, AWC_SANDY_LOAM, 0.35, "acid"),
    "quartzite": (TX_SAND, AWC_SAND, 0.2, "sandy acid"),
    "flood_basalt": (TX_CLAY, AWC_CLAY, 0.85, "clayey"),
    "dolomite": (TX_CLAY, AWC_CLAY, 0.9, "calcareous"),
    "tuff": (TX_LOAM, AWC_LOAM, 0.8, "andic"),
}


def _parent_table():
    from .surface import ROCKS
    keys = [r[1] for r in ROCKS]
    tx = np.array([_P[k][0] for k in keys], np.int8)
    awc = np.array([_P[k][1] for k in keys])
    base = np.array([_P[k][2] for k in keys])
    flags = {f: np.array([f in _P[k][3].split() for k in keys])
             for f in ("sandy", "acid", "clayey", "calcareous", "andic", "salty", "soft")}
    return tx, awc, base, flags


PARENT_TX, PARENT_AWC, PARENT_BASE, PARENT_FLAGS = _parent_table()
LOESS_BASE, ALLUVIUM_BASE, TILL_BASE = 0.8, 0.7, 0.5
AWC_TILL = 120.0  # stony loam
AWC_ROCK = 40.0  # weathered, fissured rock under a thin soil (rock moisture: Rempe & Dietrich 2018)

# ---------------------------------------------------------------------------
# Erosion, depth and age (section 3.2; decision 2A)
# ---------------------------------------------------------------------------
# Erosion E (mm/yr) from the cell's slope (m per km to its steepest
# neighbour) and the run's rain factor (surface.rain_factor), rising with the
# square of the slope (denudation climbs steeply with relief: Montgomery &
# Brandon 2002): shields and old plains (< 1 m/km) wear at ~0.001 mm/yr, hill
# country (~5 m/km) at ~0.03, steep wet ranges (~30 m/km, 1500+ mm) at
# ~1-2 mm/yr, as on Earth (Portenga & Bierman 2011's outcrop and basin rates
# span this range). Bare dry ground also loses E_WIND to the wind
# (deflation: the dust that makes loess).
E_MIN, E_STEEP, S_STEEP, E_WIND = 0.001, 1.0, 30.0, 0.01
# Soil production P(h) = P0 exp(-h / H0) (Heimsath et al. 1997), P0 faster
# where warm and wet; depth is capped at H_MAX, and never thinner than H_MIN
# on land outside fresh lava and ice (a cell-mean: valley floors and
# hollows keep soil under the steepest slopes).
P0_REF, H0, H_MAX, H_MIN = 0.15, 0.5, 3.0, 0.1
AGE_MAX = 5e7  # yr: a soil's age is at most this (relic surfaces)
# Weathering profile (PW-329): under the soil the weathering front eats into
# fresh rock at a rate that falls off with the saprolite above it (the
# solutes must diffuse and drain out through it), R = R_SAP x leaching water
# (m/yr) x warmth x e^(-D / D_SAP) mm/yr, so a surface wearing down at E keeps
# D = D_SAP ln(R / E) of saprolite: tens of metres on old shields in the wet
# tropics (Amazonia, the Congo, the West African and Brazilian shields:
# 20-100 m; Nahon 1991, Tardy 1997), a few metres in hill country, none on
# steep ranges or where little water leaches. The soil's material has spent
# (D + h) / E on its way up from the front, which is the age its weathering
# stage W counts (capped as the soil's, by glaciation, lava and AGE_MAX).
# Front advance in the wet tropics ~0.02-0.05 mm/yr (Puerto Rico's
# Rio Icacos ~0.04, Brantley & White 2009; Guinea ~0.02, Dosseto 2012).
R_SAP, D_SAP = 0.02, 10.0  # mm/yr per m/yr of leaching water at 15 C; m
SOFT_M = 1.0  # m: loose parent (unconsolidated sediment, fresh ash) is rootable at least this deep
TILL_MYR = 2.0  # glaciated within this many Myr: till and outwash
STEEP = 8.0  # m/km: steeper ground has no till, alluvium or cracking clay
# Blown sand (PW-330): the wind winnows dry, bare sandy ground, but the sand
# comes to rest in the flat lowlands (sand seas and sheets fill basins and
# plains: Wilson 1973, Lancaster 1995); on rolling and sloping ground it is
# carried on, leaving rock and stony pavement (hamada, reg)
SAND_SLOPE = 3.0  # m/km: flatter ground keeps a sand sheet
ALLUVIUM_KYR = 10.0  # age of floodplain soils (each flood lays fresh silt)
COASTAL_PLAIN_MYR = 1.0  # a coastal plain whose top stratum grew this recently is still aggrading
VOLCANIC_MYR = 1.0  # an arc or hotspot volcano this young covers the land with ash
FU_W = 2.6  # Fu's (1981) form of Budyko's curve, as the climate's water balance (Budyko w)

# Weathering stage W = log10(leaching water (m/yr) x warmth x age (yr)), warmth
# e^(K_WARM (T - 15)) (section 3.3)
K_WARM = 0.07
W_FRESH, W_SCALE = 3.0, 2.5  # fertility = base x e^(-(W - W_FRESH) / W_SCALE) above W_FRESH

# Water capacity: renormalised once on Earth (tools/soil_check.py) so the land
# mean of the vegetation's two buckets stays where it was with the old fixed
# values (50 / 137.5 mm on Earth's land outside Antarctica with the old steep thinning, observed
# climate, L6; section 3.3); CAP_SCALE = old mean / new mean
CAP_SCALE = (1.184, 0.950)
# vegetation's fertility factor (decision 6A): (0.85 + 0.25 x fertility) / F_NORM,
# F_NORM the Earth land mean of the numerator (tools/soil_check.py)
F_NORM = 0.9667

# Permafrost (section 3.5): ground = air mean + the snow's insulation (up to
# NIVAL C under a deep winter pack; Smith & Riseborough 2002's nival offset)
NIVAL, SWE_REF = 4.0, 100.0
PERMA_EDGES = (0.0, -2.0, -5.0)  # sporadic below 0 C, discontinuous below -2, continuous below -5

# Loess (section 3.6; decision 4C)
LOESS_KM = 500.0  # dust's settling length over grass (longer over bare ground)
EMIT = 0.05  # kg/m2/yr of silt a fully active source puts in the air (deserts, outwash)
LOESS_YR = 1e6  # deposition time loess represents (a few glacial cycles)
LOESS_RHO = 1500.0  # kg/m3 of loess
DESERT_DUST = 0.25  # a desert's silt source relative to a glacier margin's


def fu_runoff(p, pet, w: float = FU_W) -> np.ndarray:
    """mm/yr of water that passes through the soil (rain minus actual
    evaporation, Fu's form of Budyko's curve)."""
    p = np.maximum(np.asarray(p, float), 1e-6)
    phi = np.asarray(pet, float) / p
    aet = p * (1 + phi - (1 + phi ** w) ** (1 / w))
    return np.clip(p - aet, 0, None)


def erosion_rate(slope, precip, bare=0.0) -> np.ndarray:
    """mm/yr, from slope (m/km), annual rain and bare dry ground (0..1; decision 2A)."""
    from .surface import rain_factor
    return E_MIN + E_STEEP * (np.maximum(slope, 0.0) / S_STEEP) ** 2 * rain_factor(precip) + E_WIND * bare


def _edges(grid):
    """Directed neighbour edges (owner, neighbour, east and north components
    of the unit direction from owner to neighbour, length km)."""
    own = np.repeat(np.arange(grid.n), np.diff(grid.nbr_off))
    nb = grid.nbr_idx
    p = grid.centers
    d = p[nb] - p[own]
    d -= (d * p[own]).sum(1, keepdims=True) * p[own]
    d /= np.maximum(np.linalg.norm(d, axis=1, keepdims=True), 1e-12)
    G = climate._geom(grid)
    de, dn = (d * G["east"][own]).sum(1), (d * G["north"][own]).sum(1)
    km = arc_km((p[own] * p[nb]).sum(1))
    return own, nb, de, dn, km


def loess(grid, src, trap, winds, sea=None) -> np.ndarray:
    """m of wind-blown silt per cell (section 3.6). src: 0..1+ source
    strength (emission EMIT x src kg/m2/yr); trap: 0..1, how well the ground
    holds settling dust (plant cover); winds: [(east, north)] the seasons'
    surface winds (~1 = a steady trade wind), each carrying an equal share.
    Dust moves one cell per sweep, downwind (and a little sideways), and
    settles over LOESS_KM / trap (shorter in stronger trapping, longer in
    stronger winds); over the sea and ice it settles and is lost."""
    n = grid.n
    src = np.asarray(src, float)
    if not winds or src.max() <= 0:
        return np.zeros(n)
    own, nb, de, dn, km = _edges(grid)
    trap = np.clip(np.asarray(trap, float), 0.0, 1.0)
    if sea is not None:
        trap = np.where(sea, 1.0, trap)
    dep_total = np.zeros(n)
    for we, wn in winds:
        we, wn = np.asarray(we, float), np.asarray(wn, float)
        speed = np.hypot(we, wn)
        push = np.maximum(we[own] * de + wn[own] * dn, 0.0) + 0.1 * np.maximum(speed[own], 0.2)
        frac = push / np.maximum(np.add.reduceat(push, grid.nbr_off[:-1]), 1e-12)[own]
        step = np.add.reduceat(km, grid.nbr_off[:-1]) / np.diff(grid.nbr_off)
        reach = LOESS_KM * np.clip(speed, 0.3, 2.0) / np.maximum(trap, 1e-6)
        dep = 1 - np.exp(-step / reach)
        air = src * EMIT / len(winds)  # kg/m2/yr lifted over each cell
        total = air.sum()
        for _ in range(int(np.ceil(6 * 2 * LOESS_KM / step.mean()))):  # (6 settling lengths in a strong wind)
            dep_total += air * dep
            air = np.bincount(nb, (air * (1 - dep))[own] * frac, minlength=n)
            if air.sum() <= 1e-3 * total:
                break
    out = dep_total * LOESS_YR / LOESS_RHO
    return np.where(sea, 0.0, out) if sea is not None else out


MEMORY_AGES = np.array([0.0, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64])  # Myr: spans the run's climate is averaged over


def climate_memory(times, temp, precip, t_now: float, grid=None, velocity=None) -> dict | None:
    """The run's keyframe climate averaged back from t_now over growing
    spans (section 3.7; decision 3B): times (F,) Myr, temp, precip (F, n)
    (anything whose [i] is a frame), the climate taken as changing linearly
    between keyframes (so a soil younger than their spacing still sees part
    of the last change). With the grid and each cell's plate velocity now
    (rad/Myr), a cell's past climate is read where its ground was then
    (stepped back along today's motion: plates turn slowly over the few Myr
    a soil lasts), not at the fixed spot it is now. Returns dict(ages (B,)
    Myr, temp, precip (B, n): the means over [t_now - age, t_now] (over the
    whole record where it is shorter); now_temp, now_precip: the keyframe at
    t_now), or None with fewer than two keyframes."""
    times = np.asarray(times, float)
    keep = np.flatnonzero(times <= t_now + 1e-9)
    if len(keep) < 2:
        return None
    k_now = keep[-1]
    t0 = times[k_now]
    n = temp.shape[1]
    p = idx = None
    if grid is not None and velocity is not None:
        p = grid.centers
        v = np.asarray(velocity, float)
        speed = np.linalg.norm(v, axis=1)
        axis = np.cross(p, v) / np.maximum(speed, 1e-12)[:, None]  # turning p about it moves p along v
        idx = np.arange(n)

    def at(k):
        """Frame k's temperature and rain where each cell's ground was then."""
        nonlocal idx
        tk, pk = np.asarray(temp[k], float), np.asarray(precip[k], float)
        if p is None or k == k_now:
            return tk, pk
        ang = -speed * (t0 - times[k])  # back along the motion (Rodrigues' rotation)
        q = (p * np.cos(ang)[:, None] + np.cross(axis, p) * np.sin(ang)[:, None]
             + axis * (axis * p).sum(1, keepdims=True) * (1 - np.cos(ang))[:, None])
        idx = grid.locate(q / np.linalg.norm(q, axis=1, keepdims=True), idx)
        return tk[idx], pk[idx]

    f_now = at(k_now)
    out = [f_now]
    acc = [np.zeros(n), np.zeros(n)]
    t_prev, f_prev = t0, f_now
    b = 1  # next age to fill
    for k in keep[-2::-1]:
        if b >= len(MEMORY_AGES):
            break
        tk, fk = times[k], at(k)
        while b < len(MEMORY_AGES) and t0 - MEMORY_AGES[b] >= tk - 1e-9:  # this age's start lies in [tk, t_prev]
            x = t0 - MEMORY_AGES[b]
            w = (t_prev - x) / max(t_prev - tk, 1e-12)
            out.append(tuple((acc[i] + 0.5 * (2 * f_prev[i] + w * (fk[i] - f_prev[i])) * (t_prev - x))
                             / MEMORY_AGES[b] for i in range(2)))
            b += 1
        for i in range(2):
            acc[i] += 0.5 * (f_prev[i] + fk[i]) * (t_prev - tk)
        t_prev, f_prev = tk, fk
    while len(out) < len(MEMORY_AGES):  # ages beyond the record: its whole mean
        out.append(tuple(acc[i] / max(t0 - t_prev, 1e-12) for i in range(2)))
    return {"ages": MEMORY_AGES, "temp": np.array([o[0] for o in out]), "precip": np.array([o[1] for o in out]),
            "now_temp": f_now[0], "now_precip": f_now[1]}


def _remembered(mem: dict, age_yr, temp, precip):
    """The climate a soil of this age has seen: the present climate plus the
    keyframes' mean over its age minus their present (so the run's and the
    world's climate biases cancel). Ages under the keyframe spacing see the
    present climate."""
    a = np.log1p(np.asarray(age_yr, float) / 1e6)
    xa = np.log1p(mem["ages"])
    i = np.clip(np.searchsorted(xa, a) - 1, 0, len(xa) - 2)
    f = np.clip((a - xa[i]) / (xa[i + 1] - xa[i]), 0, 1)
    cols = np.arange(len(a))
    mt = (1 - f) * mem["temp"][i, cols] + f * mem["temp"][i + 1, cols]
    mp = (1 - f) * mem["precip"][i, cols] + f * mem["precip"][i + 1, cols]
    return temp + (mt - mem["now_temp"]), np.maximum(precip + (mp - mem["now_precip"]), 0.0)


# ---------------------------------------------------------------------------
# Pass 1: mineral
# ---------------------------------------------------------------------------
def mineral(grid, elev, temp, t_warm, t_cold, p_jul, p_jan, tilt: float = 23.4, cloud_jul=None, cloud_jan=None,
            rock=None, landform=None, landform_age=None, glaciated_myr=None, ice=None, lake_kind=None,
            lake=None, flow=None, flood_ratio=None, winds=(), memory: dict | None = None, glacial_loess=None) -> dict:
    """Soils pass 1 (section 3), from geology and climate only. rock: the
    parent rock per cell (surface.ROCKS ids: the exposed stratum); landform,
    landform_age, glaciated_myr: the run's record (landform.LAYERS; absent
    for Earth and generate worlds); lake_kind, lake (wet cells), flow,
    flood_ratio: rivers and lakes; winds: [(east, north)] seasonal surface
    winds; memory: climate_memory() of the run. Returns the fields the
    vegetation reads (cap1, cap2, f_soil, permafrost) and what organic() needs.
    What needs the grid (slope, floodplains, loess, salt lakes nearby) is
    worked out here; the rest is per cell (_mineral, shared with the zoom).
    glacial_loess (m): a glacial time zoom's own loess (timezoom.deposit), which replaces the outwash
    proxy below (silt beside today's ice) and adds to the desert dust."""
    from . import landform as LF
    from .vegetation import floodplain
    n = grid.n
    elev = np.asarray(elev, float)
    ice = np.zeros(n) if ice is None else np.asarray(ice, float)
    lake_kind = np.zeros(n, int) if lake_kind is None else np.asarray(lake_kind, int)
    wet_lake = np.isin(lake_kind, (OPEN_LAKE, CLOSED_LAKE)) if lake is None else np.asarray(lake).astype(bool)
    ground = is_land(elev, grid=grid)  # (not the sea: ground below it cut off from it too, PW-1229)
    land = ground & (ice <= 0) & ~wet_lake
    rock = np.full(n, 3) if rock is None else np.asarray(rock, int)
    lfm = np.zeros(n, int) if landform is None else np.asarray(landform, int)
    lfa = np.full(n, 9999.0) if landform_age is None else np.asarray(landform_age, float)
    glac = np.full(n, 9999.0) if glaciated_myr is None else np.asarray(glaciated_myr, float)
    cl = _climate(grid.lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, cloud_jul, cloud_jan)
    mi = cl["mi"]
    slope = cell_slope(grid, elev)

    # alluvium on the big rivers' floodplains, aggrading coastal plains
    fp = floodplain(grid, elev, np.zeros(n) if flow is None else flow, None, flood_ratio)
    aggrading = (lfm == LF.COASTAL_PLAIN) & (lfa <= COASTAL_PLAIN_MYR)

    # loess: dust from dry bare ground (salt pans and dune fields most) and glacial outwash
    sea = ~ground
    crystalline = _crystalline(rock)
    bare = _bare(mi, ground, ice)
    # (hot deserts make less loess-sized silt than glaciers grind: Smalley 1995)
    src = DESERT_DUST * bare * (1 + 0.5 * (lfm == LF.DUNES)) + 1.0 * (lake_kind == SALT_PAN)
    gl_now = (ice > 0) | (glac <= TILL_MYR)
    nbr_gl = np.add.reduceat(gl_now[grid.nbr_idx].astype(float), grid.nbr_off[:-1]) > 0
    outwash = ground & (ice <= 0) & ~gl_now & nbr_gl & ~crystalline
    if glacial_loess is None:
        src = src + 1.0 * outwash
    trap = np.clip((mi - 0.1) / 0.4, 0.0, 1.0)  # (bare ground keeps none: what settles is blown on)
    loess_m = np.where(land, loess(grid, src, trap, winds, sea | (ice > 0)), 0.0) if len(winds) else np.zeros(n)
    if glacial_loess is not None:
        loess_m = loess_m + np.where(land, np.asarray(glacial_loess, float), 0.0)
    return _mineral(cl, land, ground, ice, wet_lake, lake_kind, rock, lfm, lfa, glac, temp, t_warm, t_cold, slope,
                    fp / 0.35, aggrading, loess_m, salt_near(grid, lake_kind), memory)


def cell_slope(grid, elev) -> np.ndarray:
    """m per km to the steepest neighbour, the sea counted at sea level: a
    coastal lowland isn't steep for the drop to the sea floor beside it. On a
    grid finer than L7 (a refine), read at the cell scale (vegetation.cell_relief:
    the erosion law and the slope classes are in L7 cells' measure), so a finer
    grid's ground doesn't thin its soils for being finer."""
    from .vegetation import cell_relief, cell_rings
    return cell_relief(grid, np.maximum(np.asarray(elev, float), 0.0)) / (cell_rings(grid) * grid.spacing * R_KM)


def salt_near(grid, lake_kind) -> np.ndarray:
    """Cells with a closed (salt) lake or salt pan in them (PW-330): salt
    soils form where salty groundwater reaches the surface, on the pan's
    floor and fringe, a few to tens of km across; the basin's slopes around
    it (the neighbouring cells) drain to it and stay unsalted. (grid: kept
    for the callers.)"""
    lake_kind = np.asarray(lake_kind, int)
    return np.isin(lake_kind, (CLOSED_LAKE, SALT_PAN))


def _climate(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, cloud_jul, cloud_jan) -> dict:
    """The twelve months (climate.months), the year's rain P, potential
    evaporation, moisture index P/PET and dry months."""
    P = 0.5 * (np.asarray(p_jul, float) + np.asarray(p_jan, float))
    mo = climate.months(lat, np.asarray(temp, float), t_warm, t_cold, p_jul, p_jan, tilt, cloud_jul, cloud_jan)
    pet = mo["pet"].sum(0)
    return dict(P=P, months=mo, pet=pet, mi=P / np.maximum(pet, 1.0),
                dry_months=((mo["p"] < 2 * mo["t"]) & (mo["t"] > 0)).sum(0))


def _crystalline(rock) -> np.ndarray:
    """Hard acid rock (granite, gneiss: the ice scours it bare)."""
    return PARENT_FLAGS["acid"][rock] & ~PARENT_FLAGS["sandy"][rock] & (rock != 10)


def _bare(mi, ground, ice) -> np.ndarray:
    """0..1: dry ground too bare to hold its dust (ground: not the sea)."""
    return np.clip((0.2 - mi) / 0.15, 0, 1) * ground * (ice <= 0)


def _mineral(cl, land, ground, ice, wet_lake, lake_kind, rock, lfm, lfa, glac, temp, t_warm, t_cold, slope, alluv,
             aggrading, loess_m, salt_near, memory=None, h_min: float = H_MIN, colluvium=None) -> dict:
    """Pass 1 per cell or pixel (mineral() and zoom_mineral()): cl from
    _climate; slope in the cells' measure (m per km to the steepest
    neighbour); alluv: the floodplain's share of alluvium (0..1+), aggrading:
    a coastal plain still aggrading; loess_m (m); salt_near: a salt lake or
    pan in or beside it; h_min: the thinnest soil on land (m); colluvium:
    m of soil washed down into a hollow (zoom pixels)."""
    from . import landform as LF
    n = len(land)
    P, mo, pet, mi, dry_months = cl["P"], cl["months"], cl["pet"], cl["mi"], cl["dry_months"]
    temp = np.asarray(temp, float)
    flat = slope < STEEP

    # parent material: the rock, overridden by alluvium, loess and till where they lie
    glaciated = glac <= TILL_MYR
    crystalline = _crystalline(rock)
    till = land & glaciated & flat & ~crystalline  # ice scours hard rock bare, leaves till on soft lowlands
    alluvial = np.where(land, np.maximum(alluv, np.where(aggrading, 0.5, 0.0)), 0.0)  # share of the cell
    alluvial = np.clip(alluvial, 0, 1)
    bare = _bare(mi, ground, ice)
    w_loess = np.clip(loess_m / 1.0, 0, 1) * (1 - alluvial)
    w_till = till * (1 - alluvial - w_loess)
    w_rock = 1 - alluvial - w_loess - w_till

    # fresh volcanic ash: tuff, or a young arc or hotspot volcano nearby
    volcano = np.isin(lfm, (LF.ARC_CLASS, LF.HOTSPOT_CLASS)) & (lfa <= VOLCANIC_MYR)
    andic = land & (PARENT_FLAGS["andic"][rock] | volcano)

    # ages that cap the soil's: glaciation, eruption (fresh lava plains, hotspot islands; a live
    # volcano's ash keeps renewing the ground around it)
    age_cap = np.full(n, np.inf)
    age_cap = np.where(glac < 9999, np.maximum(glac, 0.002) * 1e6, age_cap)
    lava = (lfm == LF.LAVA_PLATEAU) | (lfm == LF.HOTSPOT_CLASS) | volcano
    age_cap = np.where(lava, np.minimum(age_cap, np.maximum(lfa, 0.002) * 1e6), age_cap)

    # depth and age (section 3.2)
    E = np.maximum(erosion_rate(slope, P, bare) * (1 - alluvial), E_MIN)
    p0 = P0_REF * np.exp(0.05 * (temp - 15.0)) * np.clip(mi, 0.05, 1.0)  # mm/yr: weathering needs water
    h_ss = np.maximum(H0 * np.log(np.maximum(p0 / E, 1e-9)), h_min)
    h_grow = H0 * np.log1p(p0 * 1e-3 * np.minimum(age_cap, 1e12) / H0)
    h_rock = np.clip(np.minimum(h_ss, h_grow), 0, H_MAX)
    tau = np.minimum(np.minimum(h_ss / (E * 1e-3), age_cap), AGE_MAX)  # yr
    # the weathering profile under it (PW-329): saprolite depth, and the age of the soil's material since
    # it left the weathering front, which W counts
    r_front = R_SAP * fu_runoff(P, pet) / 1000.0 * np.exp(K_WARM * (temp - 15.0))  # mm/yr
    sap = D_SAP * np.log(np.maximum(r_front / E, 1.0))
    sap = np.where(lava | (glac < 9999), np.minimum(sap, r_front * 1e-3 * np.minimum(age_cap, 1e12)), sap)
    tau_w = np.minimum(np.minimum((h_ss + sap) / (E * 1e-3), age_cap), AGE_MAX)
    # loess, till and alluvium are soft deposits: rootable to their own depth
    # loose to depth: unconsolidated sediment, fresh ash, and sandy ground the wind has winnowed (the
    # silt blown away as loess, the sand left as a loose sheet)
    soft = (PARENT_FLAGS["soft"][rock] | andic | (lfm == LF.DUNES)
            | (PARENT_FLAGS["sandy"][rock] & (bare >= 0.5) & (slope < SAND_SLOPE)))
    h_rock = np.where(soft, np.maximum(h_rock, SOFT_M), h_rock)
    if colluvium is not None:  # (soil washed down into a hollow: as deep as it has piled up)
        h_rock = np.maximum(h_rock, colluvium)
    h = (w_rock * h_rock + w_loess * np.maximum(h_rock, np.minimum(loess_m, H_MAX))
         + w_till * np.maximum(h_rock, 1.5) + alluvial * 2.0)
    h = np.where(land, np.clip(h, 0, H_MAX), 0.0)

    # weathering stage (section 3.3), with the run's climate over the soil's age
    t_eff, p_eff = (temp, P) if memory is None else _remembered(memory, tau_w, temp, P)
    pet_eff = pet * np.maximum(t_eff + 5, 0.5) / np.maximum(temp + 5, 0.5)  # Oudin: PET ~ T + 5
    leach = fu_runoff(p_eff, pet_eff) / 1000.0  # m/yr
    W = np.log10(np.maximum(leach * np.exp(K_WARM * (t_eff - 15.0)) * tau_w, 1.0))
    W = np.where(land, W, 0.0)

    # texture, water and fertility: the parts of the cell mixed
    tx_rock = np.where((W >= 4.5) & (PARENT_TX[rock] != TX_SAND), TX_CLAY, PARENT_TX[rock])
    parts = np.stack([w_rock, w_loess, w_till, alluvial])
    tx = np.choose(np.argmax(parts, 0), [tx_rock, np.full(n, TX_SILT), np.full(n, TX_LOAM), np.full(n, TX_SILT)])
    awc = w_rock * PARENT_AWC[rock] + w_loess * AWC_SILT + w_till * AWC_TILL + alluvial * 0.5 * (AWC_SILT + AWC_LOAM)
    leached = np.exp(-np.maximum(W - W_FRESH, 0) / W_SCALE)
    salty = land & (salt_near | (PARENT_FLAGS["salty"][rock] & (mi < 1.0)))
    salty &= mi < 0.5
    fert = ((w_rock * PARENT_BASE[rock] + w_till * TILL_BASE) * leached + w_loess * LOESS_BASE * leached ** 0.5
            + alluvial * ALLUVIUM_BASE + 0.15 * andic * (W < 5))
    fert = np.where(land, np.clip(fert - 0.4 * salty, 0, 1), 0.0)

    # permafrost (section 3.5): the snow insulates the ground
    cold = mo["t"] < 0
    swe = np.where(cold, mo["snow"], 0).sum(0) / np.maximum(cold.sum(0), 1)
    t_ground = temp + NIVAL * (1 - np.exp(-swe / SWE_REF))
    perm = np.zeros(n, int)
    for k, edge in enumerate(PERMA_EDGES):
        perm = np.where(t_ground < edge, k + 1, perm)
    perm = np.where(ground & ~wet_lake, perm, 0)  # (under ice sheets too: the ground beneath freezes or not)
    perm = np.where(ice > 0, 0, perm)

    # the vegetation's two buckets (0-0.3 m, 0.3-1.5 m): soil, and below a thin soil weathered and
    # fissured rock, which roots reach and which holds some water too (rock moisture)
    cap1 = (awc * np.minimum(h, 0.3) + AWC_ROCK * (0.3 - np.minimum(h, 0.3))) * CAP_SCALE[0]
    cap2 = (awc * np.clip(h - 0.3, 0, 1.2) + AWC_ROCK * (1.2 - np.clip(h - 0.3, 0, 1.2))) * CAP_SCALE[1]
    return dict(land=land, rock=rock, landform=lfm, slope=slope, flat=flat, mi=mi, pet=pet, P=P, temp=temp,
                t_warm=np.maximum(t_warm, t_cold), dry_months=dry_months, months=mo, erosion=E, p0=p0,
                age=tau, age_w=tau_w, saprolite=np.where(land, sap, 0.0), age_cap=age_cap, bare=bare, depth=h, W=W, texture=np.where(land, tx, TX_NONE), awc=awc,
                fertility=fert, salty=salty, andic=andic, alluvial=alluvial, till=till, loess=loess_m,
                w_rock=w_rock, permafrost=perm, t_ground=t_ground, lake_kind=lake_kind, wet_lake=wet_lake,
                ice=ice, cap1=np.where(land, cap1, 0.0), cap2=np.where(land, cap2, 0.0),
                f_soil=np.where(land, (0.85 + 0.25 * fert) / F_NORM, 1.0))


# ---------------------------------------------------------------------------
# Zoom pixels (proposal section 5, step 6; PW-331)
# ---------------------------------------------------------------------------
# The same rules on a zoom's own terrain. The erosion law and the slope
# thresholds (STEEP, the cracking clays') are in the cells' measure (m per km
# to the steepest neighbour, ~55-110 km away), which a pixel's own slope
# exceeds: PX_SLOPE converts (tan x 1000 / PX_SLOPE at 2 km pixels, finer
# pixels steeper by (2 km / res)^PX_SLOPE_EXP: rough ground is self-affine),
# measured on seven 2 km zooms of two L7 worlds (tools/zoom_soil_check.py):
# a pixel's RMS slope is ~4-22x its cell's, and 10 puts the pixels' mean
# erosion near the cell's in hills and on plains (cells beside a hill or the
# sea read steeper than their own ground: their pixels erode less); the
# exponent from 4, 2, 1 and 0.5 km zooms of one region (0.3-0.8). Soils
# have no history, so nothing pulls the pixels back to their cell.
# Coarser than 2 km a pixel's slope falls more slowly, as (2 km / res)^0.3
# (PW-345: 4 vs 2 km zooms of seven regions of an L7 world, 0-0.5, median
# 0.27; finer, 0.4-0.9, median ~0.65): creep there is scaled so a 4 km pixel
# is the mean of finer terrain over it (PW-125), not self-affine noise.
# The pixel/cell ratio itself varies 4-22x with the zoom's own roughness
# (a plain ~6x, a dry range ~13x at 1 km): the zoom's terrain, kept (PW-345 A).
PX_SLOPE, PX_SLOPE_EXP, PX_SLOPE_EXP_COARSE = 10.0, 0.6, 0.3
H_MIN_PX = 0.06  # m: a pixel's thinnest soil on old land (thin stony soil, not bare rock: pockets between the stones)
PLAIN_FULL = 0.5  # a pixel whose floodplain share (zoom.vegetation) is this is all river-laid alluvium
COLLUVIUM_M = 1.0  # m of soil washed down into the wettest hollows and slope feet
FOREFIELD_KM, FOREFIELD_MYR = 4.0, 0.005  # ground this near a zoom glacier was under it this recently (its forefield)


def valley_floor(river_q, river_km, slope, rock, res_km: float) -> np.ndarray | float:
    """The share of each pixel on its nearest river's valley floor: the
    alluvium the river has laid down as it swings across it (fluvisols). Its
    width is the fine zoom's (zoom.fine_floodplain.half_width: FLOOR_W
    channel widths, w = 4 Q^0.5 m, x sqrt of the rock's erodibility),
    narrowing to none on steep ground (slope in the cells' measure, m/km; a
    gorge keeps no floor). It grows with the channel, a power of the flow,
    not with the flow's log, so a big river's own pixels are its floor
    whatever the rain (PW-578: the riparian strip and the flooded share alone
    put a 300-1000 m^3/s river's pixels on the edge of alluvium)."""
    if river_q is None:
        return 0.0
    from .surface import ROCK_K
    from .zoom.fine_floodplain import half_width
    d = np.abs(np.asarray(river_km, float))
    k = ROCK_K[np.clip(np.asarray(rock, int), 0, len(ROCK_K) - 1)]
    w_km = 4.0 * np.sqrt(np.maximum(np.asarray(river_q, float), 0.0)) / 1000.0
    hw = half_width(w_km, np.clip(1.0 - np.asarray(slope, float) / STEEP, 0, 1), k)
    share = (np.minimum(d + 0.5 * res_km, hw) - np.maximum(d - 0.5 * res_km, -hw)) / res_km
    return np.where(np.isfinite(d), np.clip(share, 0, 1), 0.0)


def zoom_slope(slope_tan, res_km: float) -> np.ndarray:
    """A pixel's slope (tan) in the cells' measure (m/km, see PX_SLOPE)."""
    e = PX_SLOPE_EXP if res_km <= 2.0 else PX_SLOPE_EXP_COARSE
    return np.asarray(slope_tan, float) * 1000.0 / (PX_SLOPE * (2.0 / res_km) ** e)


def zoom_mineral(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt: float, cloud_jul, cloud_jan, slope_tan,
                 res_km: float, rock, landform, landform_age, glaciated_myr, plain, strip, hollow, loess_m,
                 salt_near_, ice_km, river_q=None, river_km=None) -> dict:
    """Pass 1 on a zoom's bare land pixels (no sea, lake or glacier), all
    (n,): the pixel's own climate (lapse- and slope-corrected); slope_tan;
    rock: the exposed rock (the zoom's surface_rock); landform,
    landform_age, glaciated_myr: the pixel's coarse cell's; plain: the
    share of the pixel a big river floods (zoom.vegetation), strip: the
    share inside a smaller river's strip (alluvium too); hollow: 0..1, the
    topographic wetness of hollows and valley floors (colluvium there);
    loess_m: the cells' loess, interpolated; salt_near_: a salt lake or pan
    in or beside the pixel's cell; ice_km: km to the nearest zoom glacier
    (its forefield is freshly deglaciated); river_q, river_km: the nearest
    river's discharge (m^3/s) and the km to its centre line (inf without
    one): the river's valley floor, which it has built of its own silt, is
    alluvium too. Returns mineral()'s fields."""
    from . import landform as LF
    n = len(temp)
    slope = zoom_slope(slope_tan, res_km)
    lfm = np.zeros(n, int) if landform is None else np.asarray(landform, int)
    lfa = np.full(n, 9999.0) if landform_age is None else np.asarray(landform_age, float)
    glac = np.full(n, 9999.0) if glaciated_myr is None else np.asarray(glaciated_myr, float)
    glac = np.where(np.asarray(ice_km) <= FOREFIELD_KM, np.minimum(glac, FOREFIELD_MYR), glac)
    flat = slope < STEEP
    alluv = np.maximum(np.asarray(plain, float) / PLAIN_FULL, np.asarray(strip, float))
    alluv = np.maximum(alluv, valley_floor(river_q, river_km, slope, rock, res_km))
    aggrading = (lfm == LF.COASTAL_PLAIN) & (lfa <= COASTAL_PLAIN_MYR) & flat
    loess_px = np.asarray(loess_m, float) * np.clip(2.0 - slope / STEEP, 0, 1)  # (it slides off steep slopes)
    cl = _climate(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, cloud_jul, cloud_jan)
    land = np.ones(n, bool)
    zero = np.zeros(n)
    return _mineral(cl, land, np.ones(n, bool), zero, np.zeros(n, bool), np.zeros(n, int), np.asarray(rock, int), lfm, lfa,
                    glac, temp, t_warm, t_cold, slope, alluv, aggrading, loess_px,
                    np.asarray(salt_near_, bool), h_min=H_MIN_PX, colluvium=COLLUVIUM_M * np.asarray(hollow, float))


# ---------------------------------------------------------------------------
# Pass 2: organic, then the classification
# ---------------------------------------------------------------------------
K10 = 0.04  # /yr: litter-derived soil carbon's decay at 10 C, moist (CENTURY's slow and passive pools together)
GRASS_GAIN = 0.6  # grass puts its litter into the soil as roots: more of it stays (mollic soils)
PEAT_ESCAPE = 0.1  # share of waterlogged litter that escapes the surface layer's decay into the peat
PEAT_ALPHA = 5e-4  # /yr: the peat's own (anoxic) decay at 10 C (Clymo 1984: 1e-4 .. 1e-3)
PEAT_RHO = 50.0  # kg C per m3 of peat
PEAT_SHARE, PEAT_MIN_M = 0.35, 0.4  # a cell is peat where its peatland covers this share, this deep
MOLLIC_C, MOLLIC_DRY_C, GRASS_MOLLIC = 10.5, 7.5, 0.3  # kg C/m2 (black earth, chestnut soil) and the grass share mollic soils need
CALCIC_YR = 2e4  # yr a dry soil takes to build a lime or gypsum layer
W_FERRALSOL, W_ACRISOL, W_LUVISOL, W_PODZOL = 5.5, 4.5, 3.8, 3.0


def _decay_factor(mo: dict) -> np.ndarray:
    """The year's mean decay rate relative to 10 C (Q10 = 2), counting only
    unfrozen months."""
    t = mo["t"]
    return (np.where(t > 0, 2.0 ** ((t - 10.0) / 10.0), 0.0)).mean(0)


def organic(m: dict, vg: dict) -> dict:
    """Soils pass 2 (section 3.4): soil carbon, peat, the classification
    and the final fields, from pass 1 (m) and a vegetation.model result vg."""
    from .vegetation import IDX
    land = m["land"]
    nu = vg["eq"]["nu"]
    npp = np.maximum(vg["sm"]["npp"], 0) / 1000.0  # kg C/m2/yr
    grass = nu[IDX["C3G"]] + nu[IDX["C4G"]]
    conifer_heath = nu[IDX["BoNE"]] + nu[IDX["BoNS"]] + nu[IDX["TeNE"]] + nu[IDX["HthS"]]
    fw = np.where(land, vg["fw"], 0.0)
    dfac = np.maximum(_decay_factor(m["months"]), 0.02)
    moist = 0.5 + 0.5 * np.clip(m["mi"] / 0.6, 0, 1)
    burned = np.clip(vg["eq"]["burned"], 0, 1)
    gain = (1 + GRASS_GAIN * grass) * (1 - 0.5 * burned * (1 - grass))
    soc = np.where(land, npp * gain / (K10 * dfac * moist), 0.0)
    # peat on the flooded share, where the water stays (a surplus of rain), but not on the
    # active floodplain: each flood's silt buries and aerates the litter there (alluvium, not peat;
    # peat forms in the backswamps beyond the levees)
    sat = np.clip((m["mi"] - 0.7) / 0.5, 0, 1)
    escape = PEAT_ESCAPE * (1 + 2 * nu[IDX["Sph"]])
    alpha = PEAT_ALPHA * dfac
    m_star = npp * escape * sat * (1 - m["alluvial"]) / alpha  # kg C/m2 (Clymo's equilibrium)
    age = np.minimum(m["age_cap"], 1e9)
    peat_c = np.where(land & (fw > 0), m_star * (1 - np.exp(-alpha * age)), 0.0)
    peat_d = peat_c / PEAT_RHO
    top_c = (1 - fw) * soc + fw * (np.minimum(peat_d, 1.0) * PEAT_RHO + (1 - np.minimum(peat_d, 1.0)) * soc)
    carbon = np.where(land, top_c, 0.0)

    # classification: ordered rules, the first that holds (section 2.2)
    mi, W, h, T = m["mi"], m["W"], m["depth"], m["temp"]
    rock = m["rock"]
    from . import landform as LF
    out = np.full(len(land), -1)

    def put(mask, tid):
        nonlocal out
        out = np.where((out < 0) & mask, tid, out)

    put(~land | (h < 0.05), NONE)
    put((fw >= PEAT_SHARE) & (peat_d >= PEAT_MIN_M), PEAT)
    put(m["permafrost"] >= 3, FROZEN)
    put(h < 0.25, THIN)
    put(m["salty"], SALT)
    put(m["alluvial"] >= 0.6, ALLUVIUM)
    put(fw >= 0.3, GLEY)
    put(m["andic"] & (mi >= 0.5) & (W < W_ACRISOL), ANDOSOL)
    sandy = PARENT_FLAGS["sandy"][rock] & (m["w_rock"] >= 0.5)
    # dune fields, sandy rock that is dry or young, and loose sediment the wind has winnowed (the silt
    # blown away as loess, the sand left behind)
    # (in the flat lowlands where blown sand comes to rest: SAND_SLOPE)
    deflated = (PARENT_FLAGS["soft"][rock] | PARENT_FLAGS["sandy"][rock]) & (m["bare"] >= 0.5)
    put((m["landform"] == LF.DUNES) | ((sandy & ((mi < 0.5) | (W < W_LUVISOL)) | deflated) & (m["slope"] < SAND_SLOPE)),
        SAND)
    # gypsum and lime pile up where the rain can't wash them out, given time (Gile et al. 1966's stages)
    # (lime needs a source: a base-rich or calcareous parent, or dust; on siliceous rock young brown soils form)
    old = m["age"] >= CALCIC_YR
    lime = (PARENT_BASE[rock] >= 0.5) | (m["loess"] >= 0.5) | (m["w_rock"] < 0.5)
    put(old & (mi < 0.1), GYPSIC)
    put(old & lime & (mi < 0.35), CALCIC)
    put(PARENT_FLAGS["clayey"][rock] & (m["w_rock"] >= 0.5) & (m["slope"] < 3.0) & (m["dry_months"] >= 4)
        & (mi >= 0.35) & (mi < 1.0), VERTISOL)
    # mollic soils need bases (WRB: base saturation >= 50%): not deeply leached, or in a cool climate too
    # dry to wash them out faster than weathering and dust bring them (in the tropics old savanna soils
    # are acid and kaolinitic all the same: Lixisols, Ferralsols)
    base_rich = (W < W_ACRISOL) | ((mi < 1.0) & (T < 18.0))
    put(base_rich & (grass >= GRASS_MOLLIC) & (mi >= 0.35) & (mi < 0.6) & (carbon >= MOLLIC_DRY_C), CHESTNUT)
    put(base_rich & (grass >= GRASS_MOLLIC) & (mi >= 0.6) & (mi < 1.2) & (carbon >= MOLLIC_C), CHERNOZEM)
    # podzols: cool, humid and leached a while, on sand, or on acid rock or till under conifers and heath
    # (their acid litter): on loamy ground without them, brown soils form instead
    acid = (PARENT_FLAGS["acid"][rock] & (m["w_rock"] >= 0.5)) | m["till"]
    put((mi >= 1.0) & (m["t_warm"] < 20) & (W >= W_PODZOL) & (sandy | (acid & (conifer_heath >= 0.5))), PODZOL)
    put(PARENT_FLAGS["calcareous"][rock] & (m["w_rock"] >= 0.5) & (mi >= 0.6) & (h < 0.5), RENDZINA)
    put((T > 18) & (W >= W_FERRALSOL), FERRALSOL)
    put((T > 12) & (W >= W_ACRISOL), ACRISOL)
    put((W >= W_LUVISOL) & (mi >= 0.6), LUVISOL)
    put(np.ones(len(land), bool), CAMBISOL)

    # final fields: drainage, texture with peat, fertility with organic matter and waterlogging
    tx = np.where(out == PEAT, TX_PEAT, m["texture"])
    drain = np.choose(np.clip(tx, 0, 5), [0, 1, 2, 2, 3, 3])
    drain = drain - (m["slope"] > STEEP) + (fw >= 0.15) + (fw >= 0.4) + ((m["permafrost"] >= 2) & m["flat"])
    drain = np.where(out == PEAT, 5, drain)
    drain = np.where(land & (out > 0), np.clip(drain, 1, 5), 0)
    fert = np.clip(m["fertility"] + 0.15 * np.clip(carbon / 20.0, 0, 1) - 0.3 * np.clip(fw / 0.5, 0, 1), 0, 1)
    fert = np.where(out == PEAT, np.minimum(fert, 0.25), fert)
    awc = np.where(out == PEAT, AWC_PEAT, m["awc"])
    water = np.where(land, awc * np.minimum(m["depth"], 1.5), 0.0)
    return dict(types=np.where(land, out, NONE), carbon=carbon, soc=soc, peat_c=peat_c,
                peat_depth=np.where(peat_c > 0, peat_d, 0.0), peat_share=np.where(peat_d >= 0.3, fw, 0.0),
                texture=np.where(land, tx, TX_NONE), drainage=drain, fertility=np.where(land, fert, 0.0),
                water=water)


def world_layers(m: dict, o: dict) -> dict:
    """The world layers (store.LAYERS names) from mineral() and organic()."""
    land = m["land"]
    return {
        "soil": o["types"].astype(int),
        "soil_depth": np.round(np.where(land, m["depth"], 0.0), 2),
        "soil_texture": o["texture"].astype(int),
        "soil_water": np.round(o["water"]).astype(int),
        "soil_fertility": np.round(o["fertility"], 2),
        "soil_drainage": o["drainage"].astype(int),
        "soil_carbon": np.round(o["carbon"], 1),
        "peat_depth": np.round(o["peat_depth"], 2),
        "permafrost": m["permafrost"].astype(int),
        "loess": np.round(m["loess"], 1),
    }


def legend() -> dict:
    """The soils legend every file stores (store.legends 'soils')."""
    return {"types": [{"id": t[0], "key": t[1], "name": t[2], "wrb": t[3], "usda": t[4], "color": t[5],
                       "desc": t[6]} for t in TYPES],
            "textures": TEXTURES, "drainage": DRAINAGE, "permafrost": PERMAFROST}


def geology(extra: dict) -> dict:
    """mineral()'s geology arguments from a world's extra layers (world.finish):
    the exposed stratum (else the exposed rock) and the run's record."""
    rock = extra.get("strata_top", extra.get("surface_rock", extra.get("rock")))
    return {"rock": None if rock is None else np.asarray(rock, int),
            "landform": extra.get("landform"), "landform_age": extra.get("landform_age"),
            "glaciated_myr": extra.get("glaciated_myr"), "glacial_loess": extra.get("glacial_loess")}
