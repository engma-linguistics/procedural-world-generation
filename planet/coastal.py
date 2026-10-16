"""Coastal and shallow-sea life (PW-188): coral reefs, mangroves, salt
marsh, kelp forests and seagrass meadows, as world layers (% of a cell)
and the inputs the regional zoom places them with (zoom_coastal.py).

Each habitat is a suitability from the water and the coast (0..1, the
"environment": warm or cool enough, salty enough, clear enough, sheltered
enough) times the share of the cell where the sea floor or the shore sits
at the right height (the "geometry": shallow enough for light at the bed,
or between the tides). Simple, literature-based limits; none are tuned to
Earth's map (it is the analogue, checked in tools/coastal_check.py).

Inputs: what a world already stores (sea temperature by season, salinity,
tidal range, wave power, the rivers, the climate on land) plus two fields
made here or by the climate:
  upwelling   C: how much upwelling cools the sea surface (climate.upwelling_cooling):
              nutrients for kelp
  turbidity   mg/L of suspended sediment at the surface: each river mouth's
              BQART load (coast.bqart, as the deltas use) spreads over the
              sea with an e-folding distance PLUME_KM and settles at a net
              W_NET (most of the mud is resuspended by waves and tides many
              times before it stays: net settling is a small share of the
              ~0.1-1 mm/s floc settling speed, McCave 1984), over a clear-
              water background SSC_BG. Light falls off with depth as
              e^(-Kd z), Kd = KD_CLEAR + KD_SSC x SSC (Kirk 2011: suspended
              mineral particles add ~0.05-0.1 m^-1 per mg/L).

Geometry (sub-cell, on ~55-110 km cells): the sea floor of a sea cell next
to land falls evenly from the shore to twice the cell's mean depth across
the cell, so the share shallower than z is z / (2 depth); an offshore cell
(a bank) spreads +-50% around its mean depth. A coastal land cell's
heights are taken as exponentially distributed about its mean (much low
ground near the sea, a few hills: the simplest skewed hypsometry), so the
share below the high-tide line h (half the tidal range, plus SETUP for
wind and wave set-up) is 1 - e^(-h / elevation). The zoom (zoom_coastal)
instead uses each pixel's own depth and height.

The habitats (environment x geometry):
  reef        warm (annual SST ramp from the run's reef_temp - 1.5 to reef_temp,
              where the run's reefs drown and start, tectonics/earth.reefs and
              volcanism; coldest month >= ~18 C, warmest <= ~34 C, salinity
              ~25-42 psu: Kleypas, McManus & Menez 1999), clear (SSC under
              ~10 mg/L: Rogers 1990), on the bed shallower than where 10% of
              the light is left (REEF_LIGHT, at most REEF_MAX_M), REEF_SHARE
              of that floor (the rest of a reef tract is sand, rubble and
              seagrass between the reefs). Plus the
              living reefs of the world's volcano table (fringing, barrier,
              atoll rings: REEF_RING_KM wide round each island's shore).
  mangrove    on coastal land between the tides, sheltered (wave power) and
              muddier near rivers, where frost doesn't kill them: the
              absolute minimum air temperature above ~-4 C (BIOME4's estimate
              from the coldest month, vegetation.site; Osland et al. 2017 for
              freeze limits) and the winter sea above ~16-20 C (Duke et al.
              1998), denser with rain (arid coasts: low, sparse stands).
              Flowering trees: only once plant group 4 exists.
  salt marsh  the same intertidal habitat where it is too cold for
              mangroves, with a growing season (warmest month above ~5 C).
              Grasses: only once group 5 exists.
  kelp        cool water (warmest month under ~20 C: Steneck et al. 2002)
              with nutrients (cold water, or upwelling), rocky shores (high
              or rugged coast land, hard rock or recently glaciated, not a
              coastal plain, not muddy), salinity
              above ~15 psu (none in the Baltic proper), little year-round
              sea ice, on the bed above 1% of the light (KELP_LIGHT; Luning
              1990). Brown algae: no plant-group gate.
  seagrass    sheltered (wave power), soft bottoms, salinity above ~5 psu,
              a summer sea above ~4 C (Zostera's polar limit, ~70 N in
              Greenland and Norway; none round Antarctica), not under
              year-round ice, down to Duarte's (1991) depth limit
              Zc = 1.82 Kd^-1.07 m. Flowering plants: group 4.
Shares in a sea cell are taken in that order: reef, then kelp, then
seagrass, from what is left.
"""

from __future__ import annotations

import numpy as np
from numba import njit

from . import coast
from . import surface as SF
from . import vegetation as V
from .geo import R_KM, xyz

# turbidity and light
SSC_BG = 0.5  # mg/L: clear coastal water's suspended matter, away from rivers
W_NET = 1e-5  # m/s: net settling of river mud (see the module docstring)
PLUME_KM = 150.0  # km: e-folding distance a river's mud spreads over the sea
KD_CLEAR = 0.06  # 1/m: light attenuation of clear coastal water (Kirk 2011: ~0.03-0.1)
KD_SSC = 0.07  # 1/m per mg/L of suspended sediment (Kirk 2011: ~0.05-0.1)
# coral reefs
REEF_COLD = (16.0, 18.0)  # C, coldest month's sea surface (Kleypas et al. 1999: ~18 C, rarely 16)
REEF_HOT = (35.0, 33.0)  # C, warmest month's (Kleypas et al. 1999: highest ~34.4 C)
REEF_SALT = ((25.0, 30.0), (44.0, 40.0))  # psu (Kleypas et al. 1999: 23.3-41.8)
REEF_MUD = (10.0, 3.0)  # mg/L suspended sediment (Rogers 1990: reefs normally under ~10)
REEF_LIGHT = 0.10  # reefs build where at least this share of the surface light reaches the bed...
REEF_MAX_M = 50.0  # ... and no deeper than this
REEF_SHARE = 0.25  # at most this share of the suitable shallow floor is reef framework: the rest of a reef
# tract is sand, rubble and seagrass between the reefs (the Great Barrier Reef's ~3000 reefs cover ~7% of its
# 344,000 km2 marine park, GBRMPA; Earth's reefs total ~250,000-285,000 km2, Spalding et al. 2001)
REEF_RING_KM = 1.0  # km: width of a volcano's living reef (fringing flat, barrier or atoll rim)
# the intertidal zone (mangroves, salt marsh)
SETUP = 0.3  # m: wind and wave set-up above the high-tide line (a microtidal coast keeps a fringe)
WAVE_HALF = 8.0  # kW/m: shelter halves here (~1.5 m waves of ~7 s): mangroves and salt marsh are
# low-energy shores, rare on open coasts with bigger waves (Woodroffe 2002, Coasts); at cell scale the
# rest lines its estuaries, creeks and lagoons
MUD = (1.0, 10.0)  # mg/L: from sand or carbonate flats to muddy ones (fine sediment helps both spread)
MANG_TMIN = (-7.0, -2.0)  # C, absolute minimum air temperature (BIOME4's estimate; frost kills below ~-4)
MANG_SEA = (14.0, 18.0)  # C, coldest month's sea surface (Duke et al. 1998: ~20 C, with outliers to ~14)
MANG_RAIN = (250.0, 1500.0)  # mm/yr: arid coasts' mangroves are low and sparse
MARSH_SUMMER = (2.0, 6.0)  # C, warmest month's air: a growing season
# kelp
KELP_HOT = (22.0, 19.0)  # C, warmest month's sea surface (Steneck et al. 2002: kelp forests below ~20 C)
KELP_NUTRIENT = (20.0, 14.0)  # C: water this cold is nitrate-rich (Zimmerman & Kremer 1984: none above ~15 C)...
KELP_UPWELL = (0.5, 3.0)  # C: ... or upwelling cools (and feeds) it this much
KELP_SALT = (12.0, 20.0)  # psu
KELP_ICE = (0.5, 0.95)  # share of the year under sea ice: scour and darkness
KELP_LIGHT = 0.01  # kelp reaches down to ~1% of the surface light (Luning 1990)
KELP_MAX_M = 40.0
ROCK_COAST = (80.0, 500.0)  # m: a coast's land this high or rugged is rocky...
HARD_ROCK = 0.8  # ... and this much where hard rock (crystalline, volcanic, carbonate) or fresh glacial scour
# is at the surface (surface.ROCKS; glaciated within GLACIATED_MYR)
GLACIATED_MYR = 2.0
HARD_ROCKS = (SF.OCEAN, SF.HOTSPOT, SF.ARC, SF.OROGEN, SF.CRATON, SF.LIMESTONE, SF.GRANITE, SF.QUARTZITE,
              SF.FLOOD_BASALT, SF.DOLOMITE, SF.TUFF)
# seagrass
SG_SALT = (3.0, 10.0)  # psu (Zostera holds on in the Baltic at ~5-6)
SG_ICE = (0.3, 0.8)  # share of the year under sea ice
SG_SUMMER = (2.0, 6.0)  # C, warmest month's sea surface
SG_WAVE_HALF = 10.0  # kW/m: meadows thin out with exposure (Fonseca & Bell 1998)
SG_MAX_M = 60.0

LAYERS = ("reef", "mangrove", "salt_marsh", "kelp", "seagrass")  # % of the cell
NAMES = {"reef": "coral reef", "mangrove": "mangrove", "salt_marsh": "salt marsh", "kelp": "kelp forest",
         "seagrass": "seagrass meadow"}


def ramp(x, a, b):
    """0 at a, 1 at b, linear and clipped (a > b: a falling ramp)."""
    return np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0)


def _nbr_mean(grid, v, mask):
    """Mean of v over each cell's neighbours in mask (0 where none), and how many there are."""
    m = mask[grid.nbr_idx].astype(float)
    s = np.add.reduceat(np.asarray(v, float)[grid.nbr_idx] * m, grid.nbr_off[:-1])
    k = np.add.reduceat(m, grid.nbr_off[:-1])
    return np.where(k > 0, s / np.maximum(k, 1), 0.0), k


def _nbr_max(grid, v, mask):
    m = mask[grid.nbr_idx]
    return np.maximum.reduceat(np.where(m, np.asarray(v, float)[grid.nbr_idx], -np.inf), grid.nbr_off[:-1])


# ---------------------------------------------------------------------------
# River mud and light
# ---------------------------------------------------------------------------
def river_loads(grid, L: dict) -> tuple[np.ndarray, np.ndarray]:
    """(mouths, kg/s): every land cell whose river runs into the sea, and
    its BQART sediment load (coast.bqart, with coast.river_sediment's basin
    statistics, vectorised: all basins at once)."""
    elev = np.asarray(L["elevation"], float)
    down = np.asarray(L["downstream"], int)
    n = grid.n
    land = elev > 0
    idx = np.arange(n)
    nxt = np.where(land & (down >= 0), down, idx)
    nxt = np.where(land[np.maximum(nxt, 0)], nxt, idx)  # the last land cell before the sea points to itself
    t = nxt
    while True:  # pointer jumping to each land cell's outlet
        t2 = t[t]
        if np.array_equal(t2, t):
            break
        t = t2
    mouth = land & (down >= 0) & ~land[np.maximum(down, 0)]
    cells = np.flatnonzero(land & mouth[t])
    if not len(cells):
        return np.zeros(0, int), np.zeros(0)
    b = t[cells]
    order = np.lexsort((elev[cells], b))
    cells, b = cells[order], b[order]
    mouths, start, cnt = np.unique(b, return_index=True, return_counts=True)
    pos = 0.98 * (cnt - 1)  # np.percentile(.., 98), linear, per basin
    lo = np.floor(pos).astype(int)
    hi = np.minimum(lo + 1, cnt - 1)
    e = elev[cells]
    relief = e[start + lo] + (pos - lo) * (e[start + hi] - e[start + lo])
    temp = np.add.reduceat(np.asarray(L["temperature"], float)[cells], start) / cnt
    soft = (np.add.reduceat((np.asarray(L["sediment_cover"], float)[cells] > 0.5).astype(float), start) / cnt
            if "sediment_cover" in L else np.full(len(mouths), 0.3))
    ice = np.asarray(L.get("ice", np.zeros(n)), float)
    iced = np.add.reduceat((ice[cells] > 1).astype(float), start) / cnt
    area = 4 * np.pi * R_KM ** 2 / n
    q = np.asarray(L["flow"], float)[mouths] * area * 1e6 / coast.SEC_PER_YR
    return mouths, coast.bqart(q, cnt * area, relief, temp, soft, iced)


@njit(cache=True)
def _plume(src, lam, nbr_off, nbr_idx, sea, iters, tol):
    """Steady state of S_i + sum_j (m_j - m_i) - lam m_i = 0 over the sea
    (Gauss-Seidel): sediment spreading between neighbours while it settles."""
    n = src.shape[0]
    m = np.zeros(n)
    top = max(src.max(), 1e-30)
    for _ in range(iters):
        dmax = 0.0
        for i in range(n):
            if not sea[i]:
                continue
            num = src[i]
            den = lam
            for e in range(nbr_off[i], nbr_off[i + 1]):
                j = nbr_idx[e]
                if sea[j]:
                    num += m[j]
                    den += 1.0
            v = num / den
            d = abs(v - m[i])
            if d > dmax:
                dmax = d
            m[i] = v
        if dmax * lam < tol * top:
            break
    return m


def turbidity(grid, L: dict) -> np.ndarray:
    """mg/L of suspended sediment at the sea surface (0 on land): the
    rivers' loads spread and settled (module docstring) over SSC_BG."""
    elev = np.asarray(L["elevation"], float)
    sea = elev <= 0
    mouths, load = river_loads(grid, L)
    src = np.zeros(grid.n)
    if len(mouths):
        np.add.at(src, np.asarray(L["downstream"], int)[mouths], load)
    lam = (grid.spacing * R_KM / PLUME_KM) ** 2
    m = _plume(src, lam, grid.nbr_off, grid.nbr_idx, sea, 5000, 1e-4)
    area_m2 = 4 * np.pi * (R_KM * 1e3) ** 2 / grid.n
    ssc = SSC_BG + lam * m / (W_NET * area_m2) * 1e3  # kg/m^3 -> mg/L
    return np.where(sea, ssc, 0.0)


def light_depth(kd, share: float) -> np.ndarray:
    """m: the depth where `share` of the surface light is left."""
    return np.log(1.0 / share) / np.maximum(np.asarray(kd, float), KD_CLEAR)


def seagrass_depth(kd) -> np.ndarray:
    """m: Duarte's (1991) seagrass depth limit, log Zc = 0.26 - 1.07 log Kd."""
    return np.minimum(1.82 * np.maximum(np.asarray(kd, float), KD_CLEAR) ** -1.07, SG_MAX_M)


# ---------------------------------------------------------------------------
# Environment (per cell, without the geometry) and the world layers
# ---------------------------------------------------------------------------
def _gate(unlocked, code: str) -> float:
    return 1.0 if unlocked is None or bool(np.asarray(unlocked)[V.IDX[code]]) else 0.0


def reef_temp(meta: dict | None) -> float:
    """The run's reef threshold (params.reef_temp: annual sea surface, C)."""
    from .tectonics.params import Params
    p = ((meta or {}).get("params") or {}).get("tectonics") or {}
    return float(p.get("reef_temp", Params().reef_temp))


def environment(grid, L: dict, meta: dict | None = None, unlocked=None, ssc=None) -> dict:
    """Per cell, 0..1: each habitat's suitability from the water and the
    coast, before the geometry (module docstring), plus the fields they use:
    ssc (mg/L), kd (1/m), rocky (0..1, sea cells next to land), shelter and
    the intertidal habitat's tide (m) and wave power (kW/m) on coastal land
    (the mean over the sea cells next to it). unlocked: the PFTs that exist
    (vegetation.unlocked_at; None: all). ssc: turbidity() if already known."""
    elev = np.asarray(L["elevation"], float)
    n = grid.n
    sea = elev <= 0
    land = ~sea
    ssc = turbidity(grid, L) if ssc is None else np.asarray(ssc, float)
    kd = KD_CLEAR + KD_SSC * ssc
    sst = np.asarray(L["sst"], float)
    sj, sn = np.asarray(L["sst_jul"], float), np.asarray(L["sst_jan"], float)
    s_warm, s_cold = np.maximum(sj, sn), np.minimum(sj, sn)
    sal = np.asarray(L["salinity"], float)
    up = np.asarray(L.get("upwelling", np.zeros(n)), float)
    tw = np.asarray(L["warm_month"], float)
    tc = np.asarray(L["cold_month"], float)
    ice_y = coast.sea_ice_share(grid, elev, {"t_warm": tw, "t_cold": tc}).mean(0)
    wave = np.asarray(L["wave_power"], float)
    tide = np.asarray(L["tide_range"], float)
    # the coast's land: rocky (high or rugged, hard rock or fresh glacial scour, not a coastal
    # plain), as the sea cells next to it see it
    land_rel = _nbr_max(grid, elev, land)
    h_coast = np.where(land, np.maximum(elev, 0.5 * np.maximum(land_rel - elev, 0)), 0.0)
    rocky_l = ramp(h_coast, *ROCK_COAST)
    hard = np.zeros(n, bool)
    if "surface_rock" in L:
        hard = np.isin(np.asarray(L["surface_rock"]), HARD_ROCKS)
    if "glaciated_myr" in L:
        hard |= np.asarray(L["glaciated_myr"], float) < GLACIATED_MYR
    rocky_l = np.maximum(rocky_l, HARD_ROCK * (hard & land))
    if "landform" in L:
        from .landform import COASTAL_PLAIN
        rocky_l *= np.where(np.asarray(L["landform"]) == COASTAL_PLAIN, 0.3, 1.0)
    coastal_sea = sea & (_nbr_mean(grid, np.ones(n), land)[1] > 0)
    rocky = np.where(coastal_sea, _nbr_mean(grid, rocky_l, land)[0], 0.0) * (1 - ramp(ssc, 5.0, 30.0))
    mud = ramp(ssc, *MUD)
    # coral reefs
    t0 = reef_temp(meta)
    reef = (ramp(sst, t0 - 1.5, t0) * ramp(s_cold, *REEF_COLD) * ramp(s_warm, *REEF_HOT)
            * ramp(sal, *REEF_SALT[0]) * ramp(sal, *REEF_SALT[1]) * ramp(ssc, *REEF_MUD))
    # kelp (the water's part, then on rocky shores)
    kelp_w = (ramp(s_warm, *KELP_HOT) * np.maximum(ramp(s_warm, *KELP_NUTRIENT), ramp(up, *KELP_UPWELL))
              * ramp(sal, *KELP_SALT) * (1 - ramp(ice_y, *KELP_ICE)))
    # seagrass (the water's part, then sheltered and on soft bottoms)
    seag_w = ramp(sal, *SG_SALT) * ramp(s_warm, *SG_SUMMER) * (1 - ramp(ice_y, *SG_ICE)) * _gate(unlocked, "TrBE")
    # the intertidal zone, on coastal land: the sea next to it (inland: its own air for the sea's
    # winter, for the zoom's interpolation)
    near = land & (_nbr_mean(grid, np.ones(n), sea)[1] > 0)
    tide_l = np.where(near, _nbr_mean(grid, tide, sea)[0], 0.0)
    wave_l = np.where(near, _nbr_mean(grid, wave, sea)[0], 0.0)
    cold_sea = np.where(sea, s_cold, np.where(near, _nbr_mean(grid, s_cold, sea)[0], tc))
    mud_l = np.where(near, _nbr_max(grid, mud, sea), 0.0)
    ice_l = np.where(sea, ice_y, np.where(near, _nbr_mean(grid, ice_y, sea)[0], 0.0))
    tmin = 0.006 * tc ** 2 + 1.316 * tc - 21.9  # (vegetation.site's BIOME4 estimate)
    warm = ramp(tmin, *MANG_TMIN) * ramp(cold_sea, *MANG_SEA)
    rain = 0.25 + 0.75 * ramp(np.asarray(L["precipitation"], float), *MANG_RAIN)
    no_ice = (np.asarray(L.get("ice", np.zeros(n)), float) <= 0) * (1 - ramp(ice_l, 0.5, 0.95))
    # (climate only: the plants' part, on any cell; times the tidal flats' shelter and mud below)
    mang_c = warm * rain * _gate(unlocked, "TrBE") * no_ice
    marsh_c = (1 - warm) * ramp(tw, *MARSH_SUMMER) * _gate(unlocked, "C3G") * no_ice
    tidal = near * intertidal_habitat(wave_l, mud_l)
    z = np.zeros(n)
    return {"reef": np.where(sea, reef, z), "kelp": np.where(sea, kelp_w * rocky, z),
            "seagrass": np.where(sea, seag_w * sea_shelter(wave, rocky), z),
            "mangrove": np.where(land, tidal * mang_c, z), "salt_marsh": np.where(land, tidal * marsh_c, z),
            "kelp_water": np.where(sea, kelp_w, z), "seagrass_water": np.where(sea, seag_w, z),
            "mangrove_climate": mang_c, "salt_marsh_climate": marsh_c, "mud": np.where(sea, mud, z),
            "ssc": ssc, "kd": np.where(sea, kd, 0.0), "rocky": rocky,
            "tide_land": tide_l, "wave_land": wave_l, "coastal_sea": coastal_sea, "coastal_land": near}


def intertidal_habitat(wave, mud) -> np.ndarray:
    """0..1: how good a shore is for mangroves and salt marsh, besides the
    climate: shelter from the waves (halving at WAVE_HALF kW/m) and mud
    (0..1: fine sediment helps them spread)."""
    return (0.5 + 0.5 * np.asarray(mud, float)) / (1.0 + np.asarray(wave, float) / WAVE_HALF)


def sea_shelter(wave, rocky) -> np.ndarray:
    """0..1: seagrass's sheltered, soft bottom (wave power kW/m; rocky 0..1)."""
    return (1 - 0.7 * np.asarray(rocky, float)) / (1 + np.asarray(wave, float) / SG_WAVE_HALF)


def shallow_share(depth, z, coastal) -> np.ndarray:
    """Share of a sea cell's floor shallower than z m (module docstring:
    a coastal cell's floor ramps from the shore to twice its mean depth; an
    offshore cell's spreads +-50% around it)."""
    d = np.maximum(np.asarray(depth, float), 1.0)
    z = np.asarray(z, float)
    return np.where(coastal, np.clip(z / (2 * d), 0, 1), np.clip((z - 0.5 * d) / d, 0, 1))


def intertidal_share(elev, tide) -> np.ndarray:
    """Share of a coastal land cell below the high-tide line plus SETUP
    (heights exponentially distributed about the cell's mean)."""
    h = 0.5 * np.asarray(tide, float) + SETUP
    return 1.0 - np.exp(-h / np.maximum(np.asarray(elev, float), 1.0))


def volcano_reefs(grid, meta: dict | None, sea: np.ndarray) -> np.ndarray:
    """Share of each sea cell covered by the living reefs of the world's
    volcanoes (meta volcanoes, volcanism.REEF): a REEF_RING_KM ring round
    each island's widest shore (or the atoll's rim), in the volcano's cell,
    or its shallowest sea neighbour where that cell is land."""
    from .tectonics.volcanism import REEF
    out = np.zeros(grid.n)
    vols, cols = (meta or {}).get("volcanoes"), (meta or {}).get("volcano_columns")
    if not vols or not cols:
        return out
    c = {k: i for i, k in enumerate(cols)}
    rows = [v for v in vols if int(v[c["reef"]]) == REEF and float(v[c["shore_km"]]) > 0]
    if not rows:
        return out
    lat = np.radians([float(v[c["lat"]]) for v in rows])
    lon = np.radians([float(v[c["lon"]]) for v in rows])
    cell = grid.locate(xyz(lat, lon))
    area = 2 * np.pi * np.array([float(v[c["shore_km"]]) for v in rows]) * REEF_RING_KM
    for i, a in zip(cell, area):
        if not sea[i]:
            nb = grid.nbr_idx[grid.nbr_off[i]:grid.nbr_off[i + 1]]
            nb = nb[sea[nb]]
            if not len(nb):
                continue
            i = nb[0]
        out[i] += a
    return np.clip(out / (4 * np.pi * R_KM ** 2 / grid.n), 0, 1)


def world_layers(grid, L: dict, meta: dict | None = None, unlocked=None) -> dict:
    """The world's coastal-life layers (0..1 shares of each cell: reef,
    mangrove, salt_marsh, kelp, seagrass) and turbidity (mg/L, sea). L: the
    world's layers (elevation, downstream, flow, temperature, warm_month,
    cold_month, precipitation, sst, sst_jul, sst_jan, salinity, upwelling,
    wave_power, tide_range; sediment_cover, ice, landform if any)."""
    elev = np.asarray(L["elevation"], float)
    sea = elev <= 0
    env = environment(grid, L, meta, unlocked)
    depth = np.where(sea, -elev, 0.0)
    cs, kd = env["coastal_sea"], env["kd"]
    reef = REEF_SHARE * env["reef"] * shallow_share(depth, np.minimum(light_depth(kd, REEF_LIGHT), REEF_MAX_M), cs)
    # (a volcano's living reef is the run's own: warm enough by its reef_temp)
    reef = np.where(sea, np.clip(reef + volcano_reefs(grid, meta, sea), 0, 1), 0.0)
    free = 1 - reef
    kelp = free * env["kelp"] * shallow_share(depth, np.minimum(light_depth(kd, KELP_LIGHT), KELP_MAX_M), cs)
    free = free - kelp
    seag = free * env["seagrass"] * shallow_share(depth, seagrass_depth(kd), cs)
    tid = intertidal_share(elev, env["tide_land"])
    z = np.zeros(grid.n)
    return {"reef": reef, "mangrove": np.where(sea, z, tid * env["mangrove"]),
            "salt_marsh": np.where(sea, z, tid * env["salt_marsh"]),
            "kelp": np.where(sea, kelp, z), "seagrass": np.where(sea, seag, z), "turbidity": env["ssc"]}


def areas_km2(grid, layers: dict, percent: bool = True) -> dict:
    """Total area of each habitat (km^2) from its layer: % of each cell (as
    worlds store them), or shares 0..1 with percent=False."""
    a = 4 * np.pi * R_KM ** 2 / grid.n / (100.0 if percent else 1.0)
    return {k: round(float(np.asarray(layers[k], float).sum() * a)) for k in LAYERS if k in layers}
