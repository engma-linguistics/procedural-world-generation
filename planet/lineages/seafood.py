"""Salt and sea food (PW-732): goods per cell from layers a world already has (resources, springs, lakes, coast forms,
coastal life, tides, upwelling, rivers). Called from land._make_goods; nothing here knows a people.

Salt sources (each 0..1 likelihood, on land cells; land.goods reaches them one ring inland):
    salt_rock    evaporite beds and salt pans of closed hot basins (resources `res_salt`, worked where >= ROCK_MIN)
    salt_lake    salt lakes and playas (hydrology lake_kind 2 closed, 3 salt pan)
    salt_spring  brine springs: a spring on or beside evaporite
    salt_sea     sea salt on coasts: solar pans where the air dries (pet over rain) behind tidal flats and low shores, and
                 salt boiled over wood on any other ice-free coast (a poorer source: it costs fuel) -- both need a salty sea
    salt_lick    sodium-bearing clays (shale, coal, tuff, evaporite) that rivers cut bare: a poor source animals and people use
    salt         the best of the five
(PW-746: salt_lake also holds playas -- the end of a drainage that never reaches the sea, where pet over rain is high --
and salt_spring brine springs over any sedimentary basin, not only beside evaporite.)
    _salt_km     distance over land to the nearest source (km, route-bent; SALT_UNREACHED where the landmass has none)
    _salt_kind   which source is nearest (SALT_KINDS index; 0 none)
Plant ash (potash, vegetable salt) is a marker only (the brief reads the fuel good): a poor-man's salt everywhere trees grow. It is
deliberately not a distance source (it would put salt at 0 km under every forest).

Sea food (0..1 per coastal, river and lake land cell; land.goods scales them to the world's best and reaches inland):
    fish         the best of fish_sea (shelf, upwelling and cool nutrient-rich water, reef/kelp/seagrass nurseries),
                 fish_run (rivers that reach the sea: salmon-like runs in cold ones, shad, sturgeon and eels in warm ones,
                 carried upstream, falling to 1/e over RUN_EFOLD_KM) and fish_lake (big fresh lakes)
    shellfish    marsh, seagrass, reef, tidal flats and mangrove, plus rocky shores in nutrient-rich water
    sea_mammals  seals (coastform's `seals`), whales on upwelling coasts and at the ice edge, dugong-like grazers in warm
                 seagrass lagoons
"""

from __future__ import annotations

import numpy as np

from .. import coastform as CF
from ..coastal import ramp
from ..geo import R_KM
from ..hydrology import discharge
from ..kernels import bfs_within
from .gridops import nbr_reduce

ROCK_MIN = 0.2  # res_salt likelihood below this is not worked
SRC_MIN = 0.25  # a cell with salt at least this is a source for the distance
ROUTE = 1.3  # a road bends: km along the land graph over the straight hops
SALT_UNREACHED = 5000.0  # km: no salt on this landmass (carried by trade or not at all)
SALT_KINDS = ("none", "rock salt", "salt lake", "brine spring", "sea salt", "mineral lick")
PLAYA_ARID = (1.2, 2.5)  # pet / precipitation: a closed basin from this dry gathers its salt in a playa, fully at the second
BRINE = {3: 0.4, 6: 0.3, 7: 0.35, 8: 0.5, 9: 0.7, 10: 0.5, 14: 0.3}  # surface_rock id -> brine spring strength: connate brines of the basin's sediments (evaporite, shale and coal measures best)
BRINE_COVER = (0.2, 1.0)  # km of sediment: a brine needs a basin under it
LICK_ROCK = (3, 8, 9, 10, 15)  # sediment, shale, evaporite, coal, tuff: sodium-bearing clays that rivers cut and animals lick
LICK_Q = 200.0  # m3/s: a river this big cuts banks that lay the clay bare (JUDGEMENT; PW-820: the old 2 cells of runoff at L7, 197 m3/s)
LICK = 0.3  # a lick or seep is a poor source: a place to take salt, not a salt works
SEA_SOLAR = (0.8, 2.0)  # pet / precipitation: solar pans from drier than 0.8, full at 2
SEA_BOIL = 0.35  # boiled sea salt on a damp coast (fuel and labour): this share of a solar coast
SALINITY = (15.0, 30.0)  # psu of the sea next to the coast: a brackish sea (Baltic) makes thin brine
FLATS = {"tidal": 1.0, "low": 0.9, "beach": 0.8, "barrier": 0.9, "delta": 0.5, "mangrove": 0.8, "rocky": 0.4, "cliff": 0.25,
         "fjord": 0.3, "coral": 0.6, "ice": 0.0, "none": 0.0}
SHELF_M = (1500.0, 300.0)  # m: coastal sea cells with mean depth under the second are shelf, over the first deep sea
SEA_REACH_KM = 120.0  # km offshore a coast reads its sea's fish and whales (JUDGEMENT; PW-820: the old 2 rings at L7; 1 ring at L6)
RUN_Q = (300.0, 3000.0)  # m3/s: a river this big carries a run that feeds a people, a full one at the second (JUDGEMENT, a grid floor:
#   real salmon spawn in streams far smaller (Swift 1977, USGS OFR 77-422), but one L6 cell alone sheds ~100 m3/s, so smaller
#   rivers can't be drawn alike at L6 and L7; PW-820: the old 3 and 30 cells of runoff at L7, 296 and 2,959 m3/s)
RUN_EFOLD_KM = 1475.0  # km upstream over which a run falls to 1/e (JUDGEMENT; PW-820: the old 0.96 kept per L7 cell)
RUN_COLD = (20.0, 6.0)  # mean temperature C: salmon-like runs in cold rivers, the warm ones keep RUN_WARM of it
RUN_WARM = 0.35
RUN_FROZEN = (6.0, 11.0)  # months of frozen river: runs fade
LAKE_KM2 = (3150.0, 18700.0)  # km2 of connected lake: a poor, then a full fishery (JUDGEMENT; PW-820: the old 1 and 6 L7 cells.
#   Real lakes of 100 km2 land ~585 t/yr (FAO CIFA, catch = 8.32 area^0.92): lower is a needs-decision, as lakes start at one cell)
WHALE_SST = (10.0, 2.0)  # C warmest-month sea: whales at the cold, ice-edge feeding grounds
DUGONG_SST = (20.0, 24.0)


SALT_PARTS = ("salt_rock", "salt_lake", "salt_spring", "salt_sea", "salt_lick")  # (SALT_KINDS order, after "none")


def cell_km2(g) -> float:
    """The mean cell area of grid g, km2 (PW-820: areas in km2, not cells)."""
    return 4.0 * np.pi * R_KM ** 2 / g.n


def rings_for(g, km: float) -> int:
    """Neighbour rings that span `km` on grid g, at least one (PW-820: the coarsest grid can't do less than a ring)."""
    return max(1, int(round(km / (g.spacing * R_KM))))


def cells_for(g, km2: float) -> int:
    """Cells that cover `km2` on grid g, at least one (PW-1584: people rules sized in km2, not cells, as rings_for for distances)."""
    return max(1, int(round(km2 / cell_km2(g))))


def _kind(L: dict, k: str) -> np.ndarray:
    return np.asarray(L[k]).astype(int)


def _nmax(g, v, mask=None):
    """Max of v over each cell's neighbours (and itself), optionally only neighbours in mask."""
    w = v if mask is None else np.where(mask, v, 0.0)
    return np.maximum(w, nbr_reduce(g, np.maximum, w[g.nbr_idx]))


def _sea_to_coast(g, v, sea, coast, rings=2):
    """The best sea value within `rings` cell rings, taken to each coastal land cell."""
    w = np.where(sea, v, 0.0)
    for _ in range(rings):
        w = _nmax(g, w)
    return np.where(coast, w, 0.0)


def salt(g, L: dict, land: np.ndarray, coast: np.ndarray, f) -> dict:
    sea = ~land
    out = {}
    rs = f("res_salt")
    out["salt_rock"] = np.where(land & (rs >= ROCK_MIN), rs, 0.0)
    lk = _kind(L, "lake_kind") if "lake_kind" in L else np.zeros(g.n, int)
    out["salt_lake"] = np.where(land, np.where(lk == 3, 1.0, np.where(lk == 2, 0.8, 0.0)), 0.0)
    spring = f("spring") > 0
    beds = _nmax(g, _nmax(g, np.where(land & (rs >= 0.05), rs, 0.0)))
    brine = np.zeros(g.n)  # a spring near evaporite, or any spring over a sedimentary basin (connate brine)
    rock = f("surface_rock").astype(int)
    for rid, w in BRINE.items():
        brine[rock == rid] = w
    brine *= ramp(f("sediment_cover"), *BRINE_COVER)
    out["salt_spring"] = np.where(land & spring, np.maximum(0.7 * ramp(beds, 0.05, 0.3), brine), 0.0)
    # playas: the end of a drainage that never reaches the sea, where the air takes more than the rain gives (salts stay)
    aridity = f("pet") / np.maximum(f("precipitation"), 50.0)
    down = np.asarray(L["downstream"]).astype(int) if "downstream" in L else np.full(g.n, 0)
    playa = land & (down < 0) & (f("ice") <= 0)
    out["salt_lake"] = np.maximum(out["salt_lake"], np.where(playa, ramp(aridity, *PLAYA_ARID), 0.0))
    # licks: rivers that cut sodium-bearing clays bare
    out["salt_lick"] = np.where(land & (discharge(g, f("flow")) >= LICK_Q) & np.isin(rock, LICK_ROCK), LICK, 0.0)
    # the sea: salty enough, and dry enough for pans; the coast's form says how easy the flats are
    sal = _sea_to_coast(g, np.where(sea, f("salinity"), 0.0), sea, coast, 1)
    salty = ramp(sal, *SALINITY)
    arid = ramp(f("pet") / np.maximum(f("precipitation"), 50.0), *SEA_SOLAR)
    ct = f("coast_type").astype(int)
    flats = np.zeros(g.n)
    for name, k in CF.KEYS.items():
        flats[ct == k] = FLATS.get(name, 0.3)
    ice_coast = _sea_to_coast(g, np.where(sea, f("sst_jul") < 2.0, False).astype(float), sea, coast, 1) > 0
    solar = arid * flats
    out["salt_sea"] = np.where(coast & ~ice_coast, salty * np.maximum(solar, SEA_BOIL * np.where(ct > 0, 1.0, 0.0)), 0.0)
    out["salt"] = np.maximum.reduce([out[k] for k in SALT_PARTS])
    # distance over land to the nearest source (the sources' own value is a likelihood; the cell counts as a source from SRC_MIN)
    kinds = np.stack([out[k] for k in SALT_PARTS])
    src = np.flatnonzero(land & (kinds.max(0) >= SRC_MIN))
    label = land.astype(np.int64)
    km = np.full(g.n, SALT_UNREACHED)
    kind = np.zeros(g.n, np.int8)
    if len(src):
        hop, origin = bfs_within(src.astype(np.int64), label, g.nbr_off, g.nbr_idx, g.n)
        ok = land & (hop >= 0)
        km[ok] = np.minimum(hop[ok] * g.spacing * R_KM * ROUTE, SALT_UNREACHED)
        # (the nearest source's kind: its strongest, with the ties to the sources listed first)
        kind[ok] = 1 + kinds[:, origin[ok]].argmax(0)
    km[~land] = 0.0
    out["_salt_km"] = km
    out["_salt_kind"] = kind
    return out


def seafood(g, L: dict, land: np.ndarray, coast: np.ndarray, f) -> dict:
    sea = ~land
    n = g.n
    elev = f("elevation")
    depth = np.where(sea, -elev, 0.0)
    up, kelp, grass, reef = f("upwelling"), f("kelp"), f("seagrass"), f("reef")
    s_warm = np.maximum(f("sst_jul"), f("sst_jan"))
    tide = f("tide_range")
    # a sea cell's food: nutrients (upwelling, cool water, tidal mixing) over a shelf, or a nursery (reef, kelp, seagrass)
    prod = np.maximum.reduce([ramp(up, *CF.PROD_UPWELL), ramp(s_warm, *CF.PROD_COLD), 0.6 * ramp(tide, *CF.PROD_TIDE)])
    shelf = ramp(depth, *SHELF_M)
    nursery = np.maximum.reduce([ramp(kelp, 0, 20), ramp(grass, 0, 20), ramp(reef, 0, 20)])
    iced = ramp(f("sst_jan"), 0.5, -1.5)  # (sea ice in winter)
    fish_sea_cell = np.where(sea, np.maximum(prod * (0.35 + 0.65 * shelf), 0.7 * nursery) * (1 - 0.8 * iced), 0.0)
    sea_rings = rings_for(g, SEA_REACH_KM)
    out = {"fish_sea": _sea_to_coast(g, fish_sea_cell, sea, coast, sea_rings)}
    # river runs: large rivers that reach the sea, carried upstream with a loss per km
    flow = discharge(g, f("flow"))  # (m3/s)
    down = np.asarray(L["downstream"]).astype(int) if "downstream" in L else np.full(n, -1)
    frozen = f("river_frozen")
    temp = f("temperature")
    run = ramp(temp, *RUN_COLD)
    run = RUN_WARM + (1 - RUN_WARM) * run
    run = run * ramp(frozen, *RUN_FROZEN[::-1])
    river = land & (flow >= RUN_Q[0]) & (down >= 0)
    mouth = river & ~land[np.maximum(down, 0)]
    val = np.where(mouth, run * ramp(flow, *RUN_Q), 0.0)
    cap = run * (0.5 + 0.5 * ramp(flow, *RUN_Q))
    ups = np.flatnonzero(river & ~mouth)
    keep = np.exp(-g.spacing * R_KM / RUN_EFOLD_KM)  # (kept per step upstream)
    for _ in range(n):  # (up the whole tree, one step a pass, until nothing changes)
        new = val.copy()
        new[ups] = np.maximum(val[ups], np.minimum(val[down[ups]] * keep, cap[ups]))  # (a headwater is as cold as it is, and small)
        if np.array_equal(new, val):
            break
        val = new
    out["fish_run"] = np.where(river, val, 0.0)
    # lakes: fresh lakes by size (salt ones hold little)
    lake = land & (f("lake") > 0)
    lk = _kind(L, "lake_kind") if "lake_kind" in L else np.zeros(n, int)
    lab, k = g.components(lake)
    size = np.bincount(lab[lab >= 0], minlength=max(k, 1)) * cell_km2(g)
    s = ramp(size[np.maximum(lab, 0)], *LAKE_KM2)
    out["fish_lake"] = np.where(lake, np.where(lk == 1, 0.35 + 0.65 * s, 0.1 * s), 0.0)
    out["fish"] = np.maximum.reduce([out["fish_sea"], out["fish_run"], out["fish_lake"]])
    # shellfish: marsh, seagrass beds, reef, flats; mussels and limpets on rocky shores in rich water
    ct = f("coast_type").astype(int)
    flats = np.zeros(n)
    for name in ("tidal", "barrier", "mangrove", "low", "delta"):
        flats[ct == CF.KEYS[name]] = 0.7
    rocky = np.isin(ct, (CF.KEYS["rocky"], CF.KEYS["cliff"], CF.KEYS["fjord"])).astype(float)
    nb = lambda v: _sea_to_coast(g, v, sea, coast, 1)  # noqa: E731 (the shore's own water, its sea neighbours: adjacency on any grid, PW-1627)
    cold = nb(np.where(sea, np.maximum(ramp(up, *CF.PROD_UPWELL), ramp(s_warm, *CF.PROD_COLD)), 0.0))
    shell = np.maximum.reduce([0.9 * ramp(f("salt_marsh"), 1.0, 15.0), 0.8 * nb(ramp(grass, 0, 15)), 0.9 * nb(ramp(reef, 0, 15)),
                               flats * (0.4 + 0.6 * ramp(tide, 0.3, 2.0)), 0.5 * rocky * cold, 0.7 * ramp(f("mangrove"), 1.0, 20.0)])
    out["shellfish"] = np.where(coast, shell, 0.0)
    # sea mammals: seals; whales on upwelling coasts and at the ice edge; dugong-like grazers in warm seagrass
    whale_cell = np.where(sea, np.maximum(0.7 * ramp(up, 0.8, 3.0), 0.8 * ramp(s_warm, *WHALE_SST) * (s_warm > -2)), 0.0)
    dug_cell = np.where(sea, 0.5 * ramp(grass, 0, 15) * ramp(s_warm, *DUGONG_SST), 0.0)
    out["whales"] = _sea_to_coast(g, np.maximum(whale_cell, dug_cell), sea, coast, sea_rings)
    out["sea_mammals"] = np.maximum(f("seals"), out["whales"])
    return out
