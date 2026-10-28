"""Surface processes inside the tectonic loop: rock, rivers, erosion, sediment.

Every cell has a *basement* rock class (how its crust formed) and a layer of
sediment *cover* on top (km). Erosion strips the cover first, then attacks
the basement at that rock's rate. Eroded rock travels down the river network
and is deposited in closed basins (lakes) or at the river mouth, where it
spreads out into a shelf/delta. Isostasy (in tectonics.elevation) turns
removed or added crust into lower or higher ground.

Erosion at a 60-240 km cell size can't resolve individual valleys, so it has
three parts, all scaled by rock and rainfall:
  hillslope   ground wears down in proportion to how steeply it stands above
              its neighbours (Ahnert 1970: denudation ~ local relief, here
              per km: the mean drop to the lower neighbours over the cell
              spacing, a mean downhill slope). Steep range fronts and plateau
              edges go fast; a plateau's flat interior and broad old uplands
              barely change. A slope is the same at any resolution, so the
              wear is too (PW-282: the old drop / spacing^2 doubled per level).
  weathering  everything above base level also wears down, slowly when low
              and much faster when high (dh/dt = -(h/tau)(1 + (h/h0)^2), h
              above base): high ground has deep valleys, frost and glaciers
              below the cell scale, so young ranges are cut down quickly
              while old ones linger at 1-2 km (Montgomery & Brandon 2002)
  incision    rivers cut down toward the next cell downstream at a rate
              ~ sqrt(water flow) (stream power), so big rivers keep their
              valleys low and drainage divides stay high. The flow is the
              runoff (rain minus evaporation), and evaporating lakes can
              end a river (hydrology.lakes)

Where the load ends up:
  land        closed basins and lakes keep what reaches them, up to their
              room (a full basin spills over its rim and its rivers' load
              runs on); on gentle ground rivers drop part of it (floodplains)
  sea         near the shore first: the delta and the shelf fill up to
              their level (the delta top just above the sea, so the coast
              builds out: progradation), and what's left goes down the
              slope (turbidity currents) and spreads over the deep sea floor
              over ~fan_km (submarine fans) before it settles

The cover rocks (limestone, sandstone, shale, evaporite, coal, flood basalt,
tuff) are in ROCKS, plus dolomite and quartzite, which only the strata make
(tectonics/record.py). What shows at the surface is the cover's top stratum
(surface_rock); erosion still uses the cover's well-mixed erodibility.
The table can grow further: a new class is a row plus a rule for where it
forms.
"""

from __future__ import annotations

import numpy as np
from numba import njit

from . import hydrology, kernels
from .geo import R_KM

# id, key, name, erodibility (relative), colour
ROCKS = [
    (0, "ocean", "oceanic basalt", 1.0, "#2b4a6f"),
    (1, "hotspot", "hotspot basalt", 1.6, "#8c2f39"),
    (2, "arc", "volcanic arc (andesite, granite)", 0.8, "#d1495b"),
    (3, "sediment", "sedimentary rock", 1.5, "#e9c46a"),
    (4, "orogen", "metamorphic belt (gneiss, schist)", 0.6, "#8e7dbe"),
    (5, "craton", "ancient shield (granite, gneiss)", 0.3, "#6c757d"),
    (6, "limestone", "limestone (reefs, carbonate platforms)", 1.0, "#a8dadc"),
    (7, "sandstone", "sandstone (rivers, beaches, dunes)", 1.2, "#f4a259"),
    (8, "shale", "shale and mudstone", 1.6, "#9c8f7a"),
    (9, "evaporite", "evaporites (salt, gypsum)", 3.0, "#f1faee"),
    (10, "coal", "coal measures (shale, sandstone, coal)", 1.6, "#2b2d42"),
    (11, "granite", "granite (exhumed plutons: batholiths, domes)", 0.5, "#e8a0a8"),
    (12, "quartzite", "quartzite (sandstone folded deep in a collision)", 0.4, "#d8cfc0"),
    (13, "flood_basalt", "flood basalt (continental traps, lava plains)", 1.0, "#5a4a5e"),
    (14, "dolomite", "dolomite (buried limestone: a hard carbonate caprock)", 0.7, "#6fa8b8"),
    (15, "tuff", "volcanic tuff (ignimbrite and ash from arcs)", 0.9, "#c98b6b"),
]
(OCEAN, HOTSPOT, ARC, SEDIMENT, OROGEN, CRATON, LIMESTONE, SANDSTONE, SHALE, EVAPORITE, COAL, GRANITE, QUARTZITE,
 FLOOD_BASALT, DOLOMITE, TUFF) = range(16)
ROCK_K = np.array([r[3] for r in ROCKS])
# Cover is a well-mixed column: mud (shale) plus some km of each of
# MIX_ROCKS (tectonics.EXTRA, columns 1..); its erodibility is the mix of theirs.
MIX_ROCKS = np.array([LIMESTONE, FLOOD_BASALT, EVAPORITE, COAL, SANDSTONE, TUFF])
MIX_K = ROCK_K[MIX_ROCKS]
COVER_K = ROCK_K[SHALE]
COVER_SHOWS = 0.05  # km of cover before it, not the basement, is what's exposed




def rain_factor(precip_mm):
    """Wetter ground erodes faster; deserts barely erode (little runoff to
    carry anything away, so their mountains and plateaus last)."""
    return np.clip((np.maximum(precip_mm, 0) / 800.0) ** 0.8, 0.1, 2.5)


@njit(cache=True)
def _relief(h, nbr_off, nbr_idx):
    """Mean height each cell stands above its neighbours (lower ones only;
    the sea counts as 0 m), m."""
    n = h.shape[0]
    out = np.zeros(n)
    for i in range(n):
        s = 0.0
        for k in range(nbr_off[i], nbr_off[i + 1]):
            hj = max(h[nbr_idx[k]], 0.0)
            if h[i] > hj:
                s += h[i] - hj
        out[i] = s / (nbr_off[i + 1] - nbr_off[i])
    return out


@njit(cache=True)
def _route(down, order, sed, pit_room, pool, pool_room, is_ocean, h, d_km, drop, fp_room):
    """Carry eroded rock (km of crust per cell) down the river network,
    headwaters first. Closed basins keep what fits; an open lake (pool >= 0,
    its id) keeps what fits anywhere in it (pool_room: km per lake), as the
    river drops its load where it slows into the lake; on gentle ground
    rivers drop some of their load (floodplains, the plains in front of
    mountain ranges): a share 1 - exp(-d_km / drop) per cell, less on steep
    ground, up to fp_room (km per cell: inside a hollow its room below the
    spill point, so a floodplain on a basin's slopes doesn't build its rim
    up: PW-299; inf on open ground, where plains aggrade freely); the rest
    runs on down to the basin's floor. Everything else ends at the ocean
    cell where the river meets the sea."""
    n = sed.shape[0]
    dep = np.zeros(n)
    flux = sed.copy()
    for t in range(order.shape[0] - 1, -1, -1):
        i = order[t]
        if is_ocean[i]:
            dep[i] += flux[i]
            continue
        p = pool[i]
        if p >= 0:
            keep = min(flux[i], pool_room[p])
            pool_room[p] -= keep
            dep[i] += keep
            flux[i] -= keep
        elif pit_room[i] > 0:
            keep = min(flux[i], pit_room[i])
            dep[i] += keep
            flux[i] -= keep
        d = down[i]
        if d >= 0 and not is_ocean[d] and p < 0:
            slope = max(h[i] - h[d], 0.0) / d_km  # m per km
            keep = flux[i] * (1 - np.exp(-d_km / drop)) * np.exp(-slope / 2.0)
            keep = min(keep, max(fp_room[i] - dep[i], 0.0))
            dep[i] += keep
            flux[i] -= keep
        if d >= 0:
            flux[d] += flux[i]
        else:
            dep[i] += flux[i]
    return dep


@njit(cache=True)
def _spread(dep, ea, eb, k, n_sub):
    """Spread sea-floor deposits out sideways (currents, waves along the coast)."""
    d = dep.copy()
    flux = np.empty(len(ea))
    for _ in range(n_sub):
        for e in range(len(ea)):
            flux[e] = k * (d[eb[e]] - d[ea[e]])
        for e in range(len(ea)):
            d[ea[e]] += flux[e]
            d[eb[e]] -= flux[e]
    return d


DELTA_TOP = 2.0  # m: a delta builds its top just above the sea
SHELF_TOP = -60.0  # m: farther out, sediment builds up to about wave base
SHELF_EDGE = -400.0  # m: below this it's the slope and the deep sea floor


@njit(cache=True)
def _offshore(load, elev, iso, ocean, coast, nbr_off, nbr_idx, d_km, fan_km):
    """Where the rivers' load (km of crust arriving at each sea cell) settles.
    Shallowest first: each cell on the shelf keeps what fits below its
    target level (DELTA_TOP next to land, SHELF_TOP farther out) and passes
    the rest to its deepest neighbour. At the shelf's brink (a deep cell
    next to land or to the shelf: the slope just off it) the load drops as
    a clinoform's foreset and fills the cell toward the shelf's level, so a
    supplied shelf builds out over the slope (progradation; PW-818: most of
    a margin's sediment stays in its shelf-slope wedge, Steckler et al.
    1999). Beyond that (the deep sea floor) a share 1 - exp(-d_km / fan_km)
    settles per cell passed (submarine fans). A sea-floor low (a trench, an
    enclosed basin) keeps whatever reaches it."""
    n = elev.shape[0]
    dep = np.zeros(n)
    flux = load.copy()
    idx = np.argsort(-elev)
    for t in range(n):
        i = idx[t]
        if not ocean[i] or flux[i] <= 0:
            continue
        if elev[i] > SHELF_EDGE:
            keep = min(flux[i], max((DELTA_TOP if coast[i] else SHELF_TOP) - elev[i], 0.0) / iso[i])
        else:
            brink = False
            for e in range(nbr_off[i], nbr_off[i + 1]):
                j = nbr_idx[e]
                if not ocean[j] or elev[j] > SHELF_EDGE:
                    brink = True
                    break
            share = 1.0 if brink else 1 - np.exp(-d_km / fan_km)
            keep = min(flux[i] * share, (SHELF_TOP - elev[i]) / iso[i])
        dep[i] += keep
        f = flux[i] - keep
        lo, bz = -1, elev[i]
        for e in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[e]
            if ocean[j] and elev[j] < bz:
                lo, bz = j, elev[j]
        if lo >= 0:
            flux[lo] += f
        else:
            dep[i] += f
    return dep


BASIN_PASSES = 8  # closed basins an overflow may fill in turn on its way down (the Nile into the Nubian hollow)


def _closed_basins(grid, elev, land, sink, lake_room, in_pool, dep, iso_dep, flood):
    """Closed basins keep what reaches them up to their room (PW-280).
    Rivers end at a closed lake or a closed basin's pit (route), so _route
    leaves all their load there. A basin holds it up to its spill point,
    the lowest rim crossing toward the sea (priority-flood of the terrain):
    a closed lake's floor takes it first, each cell in proportion to the
    water over it (lake_room: km per cell, up to the lake's surface), so
    the deepest fill most; once the lake is full of sediment, the rest is
    spread over the whole hollow in proportion to each cell's room (spill
    - 5 m - ground, less what it got already), as an open lake's is: the
    basin fills up from the bottom and nothing rises above the rim. What
    doesn't fit spills over the rim and runs on down the priority-flood's
    path to the sea, into the next hollow on it if there is one (which
    keeps what fits in turn), else into the sea. After BASIN_PASSES
    basins, what is still over stays on the last one's floor. Open lake
    cells (in_pool) take no share here: their room is _route's pool_room.
    flood: (spill, pf_down) of the terrain's priority-flood (erode's).
    Returns dep (km per cell)."""
    spill, pf_down = flood
    hol, nh = grid.components(land & (spill > elev))
    at = sink & (hol >= 0) & (dep > 0)
    if not at.any():
        return dep
    inh = hol >= 0
    room0 = np.where(inh & ~in_pool, np.maximum(spill - 5.0 - elev, 0) / iso_dep, 0.0)
    load = np.bincount(hol[at], dep[at], nh)
    dep = dep - np.where(at, dep, 0.0)
    low = np.full(nh, -1, np.int64)  # each hollow's lowest cell
    ci = np.flatnonzero(inh)
    ci = ci[np.argsort(-elev[ci], kind="stable")]
    low[hol[ci]] = ci
    # where a hollow's overflow goes: down the priority-flood path from its
    # spill point to the first cell outside it that is sea or in another hollow
    dest = np.full(nh, -2, np.int64)  # (-2: not worked out yet; -1: nowhere, it stays)
    for k in range(BASIN_PASSES + 1):
        if k == BASIN_PASSES:
            np.add.at(dep, low[load > 0], load[load > 0])
            break
        over = load
        for cap in (lake_room, room0):  # (the lake's floor first, then the whole hollow)
            room = np.where(inh, np.maximum(cap - dep, 0), 0.0)
            rsum = np.bincount(hol[inh], room[inh], nh)
            share = np.minimum(over / np.maximum(rsum, 1e-30), 1.0)
            dep = dep + np.where(inh, share[np.maximum(hol, 0)] * room, 0.0)
            over = over - share * rsum
        load = np.zeros(nh)
        for c in np.flatnonzero(over > 1e-15):
            if dest[c] == -2:
                t = low[c]
                while t >= 0 and land[t] and hol[t] in (c, -1):
                    t = pf_down[t]
                dest[c] = t if t >= 0 and (not land[t] or hol[t] >= 0) else -1
            t = dest[c]
            if t < 0:
                dep[low[c]] += over[c]
            elif not land[t]:
                dep[t] += over[c]
            else:
                load[hol[t]] += over[c]
        if not load.any():
            break
    return dep


def surface_rock(rock, cover, top, top_km):
    """What's exposed at the surface: the cover's exposed stratum (top,
    top_km: tectonics.record.top through landform.VENEER_KM, i.e. the
    landform layers' strata_top / strata_top_km), so a thin hard caprock
    shows over the soft rock under it; the basement where less than
    COVER_SHOWS km of cover lies on it (soil and a veneer of sediment: the
    basement shows through). Cover made only of veneers counts as shale.
    Display and the zoom only: erosion still uses the cover's mix (erode)."""
    sed = np.where(top_km > 0, top, SHALE)
    return np.where(cover > COVER_SHOWS, sed, rock).astype(np.uint8)


def erode(grid, elev, thick, cover, mix, rock, cont, precip, runoff, aet, lake_evap, dt, hillslope, tau, h0,
          incision, scale, iso, k_mult=1.0, alluvial=3000.0, fan_km=1000.0, iso_dep=None, valley=None,
          base_rise=0.0):
    """One step of erosion + sediment transport on the world view. Eroded
    cover takes its ingredients (mix: km of each of MIX_ROCKS per cell) with
    it pro rata; what's deposited is plain clastic sediment (the caller
    decides how much of it is sand). precip, runoff, aet (actual evaporation)
    and lake_evap in mm/yr; iso: m of elevation per km of crust eroded, per
    cell; iso_dep: per km of sediment deposited (default: iso);
    k_mult: extra erodibility factor per cell (glaciers); alluvial: km of
    gentle river course over which ~63% of the load settles on land; fan_km:
    km of deep sea floor over which ~63% of what passes the shelf settles.
    valley: m the cells' valleys are already cut (hydrology.lakes').
    base_rise: m the continents' base level stands above the sea (the run's
    ice: how far it has lowered the sea).
    Returns (thick, cover, mix, removed_km, deposited_km, flow, downstream,
    lakes): lakes is hydrology.lakes' dict (on the terrain before this
    step's erosion) plus 'depth', m of water (level - elev; 0 off lakes)."""
    land = elev > 0
    lk = hydrology.lakes(grid, elev, runoff, aet, lake_evap, valley=valley)
    flow, down, order, filled = hydrology.route(grid, elev, lk)

    c = np.maximum(cover, 1e-9)
    k_cover = (COVER_K * np.maximum(cover - mix.sum(1), 0) + mix @ MIX_K) / c
    K0 = np.where(cover > COVER_SHOWS, k_cover, ROCK_K[rock]) * k_mult
    K = K0 * rain_factor(precip)
    # a river cuts with its catchment's rain, not just the rain where it
    # runs: a big river crossing a desert (or a polar desert lake's outlet)
    # still incises (PW-055)
    up = kernels.accumulate(down, order, land.astype(float))
    p_up = kernels.accumulate(down, order, np.where(land, precip, 0.0)) / np.maximum(up, 1.0)
    K_river = K0 * np.maximum(rain_factor(precip), rain_factor(p_up))
    # hillslope: ground wears down at hillslope (km/Myr) x K x its mean
    # downhill slope (relief / d_km, m per km), in m/Myr; the exponential
    # form can't take a cell below its lower neighbours' mean
    d_km = grid.spacing * R_KM
    relief = _relief(elev.astype(float), grid.nbr_off, grid.nbr_idx) * land
    h = elev - relief * (1 - np.exp(-hillslope * K * dt / d_km))
    # weathering toward base level (continental interiors settle ~200 m up). The height above it stands in
    # for relief (PW-279), so it is counted from the sea without the ice's fall (base_rise): a glacial
    # lowstand lifts every plain against the sea but steepens no interior slope (its rivers' new reach to
    # the shore is stream power's below); counting it made a cold era's plains wear down ~5x faster and the
    # weathering sink rise as the planet cooled (PW-438)
    base = np.where(cont, 200.0 + base_rise, 0.0)
    above = np.maximum(h - base, 0) * land
    h = h - above * (1 - np.exp(-K * dt / tau * (1 + (above / h0) ** 2)))
    # river incision toward the next cell downstream (implicit, unconditionally stable)
    h = h.astype(float)
    kernels.stream_power(h, down, order, np.where(land, incision * K_river * np.sqrt(flow) * dt, 0.0))
    removed = np.minimum(np.maximum(elev - h, 0) * land / iso, np.maximum(thick, 0))  # km of rock

    from_cover = np.clip(removed, 0, np.maximum(cover, 0))
    keep = 1 - from_cover / c
    mix = mix * keep[:, None]
    cover = cover - from_cover
    thick = thick - removed

    # route it: lakes and hollows keep what fits, closed basins up to their spill point, the rest reaches the sea
    if iso_dep is None:
        iso_dep = iso
    pit_room = np.where(land, np.maximum(filled - elev - 5, 0) / iso_dep, 0.0)
    # an open lake traps what its rivers bring (up to its whole room, PW-055:
    # a big lake on a river fills in, unless its basin sinks faster) and
    # spreads it over its floor, deepest most
    pool, n_pool = grid.components(lk["wet"] & ~lk["sink"])
    m = pool >= 0
    pool_room = np.bincount(pool[m], pit_room[m], n_pool) if n_pool else np.zeros(0)
    pool_left = pool_room.copy()
    # a hollow's room below its spill point (as _closed_basins fills it):
    # what a floodplain inside it may keep (PW-299)
    spill, pf_down, _ = kernels.priority_flood(elev.astype(float), grid.nbr_off, grid.nbr_idx, 0.01)
    fp_room = np.where(land & (spill > elev), np.maximum(spill - 5.0 - elev, 0) / iso_dep, np.inf)
    dep = _route(down, order, removed, pit_room, pool, pool_left, ~land, h, d_km, alluvial, fp_room)
    lake_room = np.where(lk["wet"] & lk["sink"], np.maximum(lk["level"] - elev, 0) / iso_dep, 0.0)
    dep = _closed_basins(grid, elev, land, lk["sink"], lake_room, m, dep, iso_dep, (spill, pf_down))
    if n_pool:
        share = np.bincount(pool[m], dep[m], n_pool) / np.maximum(pool_room, 1e-30)  # (<= 1)
        dep[m] = share[pool[m]] * pit_room[m]
    ocean = ~land
    coast = ocean & (np.add.reduceat(land[grid.nbr_idx], grid.nbr_off[:-1]) > 0)
    dep_sea = _offshore(np.where(ocean, dep, 0.0), elev.astype(float), np.asarray(iso_dep, float), ocean, coast,
                        grid.nbr_off, grid.nbr_idx, d_km, fan_km)
    # then currents spread it sideways: a little along the shelf, more over
    # the deep sea floor (turbidity currents fan out)
    ea, eb = grid.edges[:, 0], grid.edges[:, 1]
    shelf = ocean & (elev > SHELF_EDGE)
    deep = ocean & ~shelf
    on_shelf = np.where(shelf, dep_sea, 0.0)
    dep_sea = (_spread(on_shelf, ea[shelf[ea] & shelf[eb]], eb[shelf[ea] & shelf[eb]], 0.15, int(round(scale**2)))
               + _spread(dep_sea - on_shelf, ea[deep[ea] & deep[eb]], eb[deep[ea] & deep[eb]], 0.15,
                         int(round(4 * scale**2))))
    dep = np.where(ocean, dep_sea, dep)
    thick = thick + dep
    cover = cover + dep
    lk["depth"] = np.where(lk["wet"], np.maximum(lk["level"] - elev, 0.0), 0.0)
    return thick, cover, mix, removed, dep, flow, down, lk
