"""Rivers, lakes and fluvial erosion on the cell graph.

Rivers carry the runoff (rain minus what evaporates back, see
climate.water_balance), not the rain itself.

1. Priority-flood (Barnes et al. 2014): grow inward from the ocean, always
   expanding the lowest known cell next. Each land cell's 'downstream' is
   whichever cell reached it first, so every drop of rain has a route to
   the sea. Cells that had to be raised to drain (pits) are lakes.
2. Flow accumulation: walk from the headwaters down, summing rainfall.
   Big sums = big rivers.
2b. Lakes evaporate (kernels.lakes): a basin fills only until the
   evaporation off the lake matches the water flowing in, or until it
   spills. In dry country that leaves closed, salty lakes (Caspian, Great
   Salt Lake, Lake Chad) or dry salt pans, and their rivers end there.
   A river leaving a lake runs in a valley cut below its cells' mean
   height, deeper the bigger it is, so big through-flowing lakes drain
   down to it (lakes(): channel).
3. Stream-power erosion (Braun & Willett 2013): cut each cell toward its
   downstream neighbour at a rate ~ sqrt(flow). Big rivers carve deep
   valleys, ridges stay sharp. The implicit form used here can't blow up
   numerically, however hard you push it.
"""

from __future__ import annotations

import numpy as np
from numba import njit

from . import kernels
from .constants import SEC_PER_YR
from .geo import R_KM, is_land
from .grid import Grid


def priority_flood(grid: Grid, elev: np.ndarray, eps: float = 0.01, sea: np.ndarray | None = None):
    """Returns (filled, downstream, order). order runs outlet -> headwater.
    sea: where the water ends (default geo.is_land's sea of elev)."""
    sea = ~is_land(elev, grid=grid) if sea is None else sea
    return kernels.priority_flood(elev.astype(float), sea, grid.nbr_off, grid.nbr_idx, eps)


def accumulate(down: np.ndarray, order: np.ndarray, rain: np.ndarray) -> np.ndarray:
    return kernels.accumulate(down, order, rain.astype(float))


def erode(grid: Grid, elev: np.ndarray, c: dict, iterations: int = 12, strength: float = 1.0,
          diffusion: float = 0.08, lake_every: int = 4, ice: np.ndarray | None = None):
    """Carve river valleys with the climate c's runoff (climate.compute's
    dict: runoff, aet, lake_evap, mm/yr). Rivers run as in the run
    (surface.erode): through open lakes and on, ending in closed ones, so a
    closed basin's rim isn't cut by water that never leaves it (the lakes
    are worked out again every lake_every passes; 0: plain priority-flood
    routing, every pit spilling). What it removes isn't deposited: a
    display pass for sub-cell valleys on a keyframe that has already put
    its sediment where it goes (PW-281: routing it filled the keyframe's
    hollows and built deltas). ice: grounded land ice; a bed below the sea
    under it is land (geo.is_land, PW-307). Water routes over the ice's
    surface wherever there is ice, as rivers_and_lakes' (one rule for the
    world's water, PW-355; under a sheet its hydraulic head follows the ice
    surface's slope), and the bed beneath is cut toward its downstream
    cell's bed. Returns new elevation."""
    h = elev.astype(float).copy()
    # finer cells -> more upstream cells; (tuned on rain: runoff is ~40% of
    # it, so 1/sqrt(0.4) keeps the cutting the same on average)
    k = 0.018 * 1.6 * strength * 2 ** (grid.level - 5)
    from .surface import _relief
    iced = ice > 0 if ice is not None else None
    top = np.where(iced, ice, 0.0) if ice is not None else 0.0  # (the ice's thickness, 0 off it)
    lk = None
    for it in range(iterations):
        land = is_land(h, ice, grid)
        hr = h + top  # what the water runs over: the ice surface, the ground off it
        if lake_every and it % lake_every == 0:
            lk = lakes(grid, hr, c["runoff"], c["aet"], c["lake_evap"], iced, land=land, pet_mm=c.get("pet"))
        if lk is None:
            _, down, order = priority_flood(grid, hr, sea=~land)
            flow = accumulate(down, order, np.where(land, c["runoff"], 0.0) / 1000.0)
        else:
            lk["bed"] = np.where(lk["wet"], lk["bed"], hr)
            flow, down, order, _ = route(grid, hr, lk)
        kernels.stream_power(h, down, order, np.where(land, k * np.sqrt(np.maximum(flow, 0)), 0.0))
        # Hillslope creep, as the run's (surface.erode): land wears down toward
        # its lower neighbours; it only lowers ground, so hollows aren't filled
        # (PW-057: a symmetric creep filled the run's lake basins in); gentler
        # with the strength, as the cutting (a run's keyframe is worn already).
        h = np.where(land, h - diffusion * strength * _relief(h, grid.nbr_off, grid.nbr_idx), h)
    return h


# lake_kind values
NO_LAKE, OPEN_LAKE, CLOSED_LAKE, SALT_PAN = 0, 1, 2, 3


MIN_DEPTH = 20.0  # m: shallower hollows in the cell-mean terrain are drained by unresolved channels
# m per km: a wide hollow must also fall at least this steeply from its rim
# to its middle (depth / sqrt(area / pi)), or it is a plain that rivers cross
MIN_SLOPE = 0.1
# A hollow in a dry catchment that no river leaves stays closed however
# shallow or flat (_dry_hollows; PW-054): its catchment's rain is below
# DRYLAND_AI x its potential evaporation (the climate's, Oudin's, over land)
DRY_HOLLOWS = True
DRYLAND_AI = 0.65
# depth of the valley a river runs in below its cells' mean height, m:
# CHANNEL_K x (discharge in m^3/s) ** CHANNEL_B
CHANNEL_K, CHANNEL_B = 0.1, 0.7
CARVE_TRIES = 2  # times the valleys are recut as the rivers they carry move
# Myr e-folding of a valley whose river has stopped (lakes' valley; PW-300):
# an abandoned spillway or wind gap is filled only by its own slopes'
# debris, with no river to bring sediment to it, and stays a gap through
# the divide for tens of Myr (Red Rock Pass, Bonneville's outlet; the wind
# gaps of the Appalachian ridges)
VALLEY_MYR = 20.0


def discharge(grid: Grid, flow: np.ndarray) -> np.ndarray:
    """m^3/s from flow units (cells x m/yr of runoff)."""
    return flow * (4 * np.pi * (R_KM * 1000) ** 2 / grid.n) / SEC_PER_YR


def _bed(grid, ground, sea, min_depth, min_slope):
    """ground with the hollows (and dips in a basin's floor) shallower than
    min_depth, or flatter than min_slope, filled to where they spill; the
    rest of the land drains as priority_flood has it."""
    if min_depth <= 0:
        return ground
    from .ocean import cell_area_km2
    h, keep = kernels.fill_shallow(ground, sea, grid.nbr_off, grid.nbr_idx, float(min_depth),
                                   cell_area_km2(getattr(grid, "base", grid)), float(min_slope))
    return np.where(keep, h, kernels.flood_fill(h, sea, grid.nbr_off, grid.nbr_idx, 0.01))


def _dry_hollows(grid, ground, bed, land, src, loss, rain, pet):
    """Cells of the hollows (below their spill points) in dry catchments
    that no river leaves. _bed's min_depth and min_slope stand for channels
    too small to see that a through-flowing river cuts through a shallow
    rim, or a plain it crosses. A hollow whose own inflow evaporates before
    its lake reaches the rim has no outflowing river to cut that channel,
    so it stays a playa or a terminal lake however shallow (the
    Altiplano-Puna, Tarim, Eyre). Only where its whole catchment is
    dryland, rain under DRYLAND_AI x the potential evaporation (the aridity
    index's bound): a flat hollow in wet country is closed by the lake
    balance only because a lake spread over all of it would evaporate its
    inflow, but there its rivers build the floor up and spill (a swamp or a
    lake a river crosses, as _bed has it). The candidates are the closed
    hollows of the unfiltered ground; their lakes and catchments are then
    taken on bed (_bed's) with them put back, where the shallow hollows
    upstream are filled and pass their rivers on (a hollow gets those too)."""
    sea, rcv, asc = kernels.lake_order(ground, ~land, grid.nbr_off, grid.nbr_idx)
    open0 = kernels.lakes_on(ground, grid.nbr_off, grid.nbr_idx, src, loss, sea, rcv, asc)[1]
    filled = kernels.priority_flood(ground, ~land, grid.nbr_off, grid.nbr_idx, 0.0)[0]
    cand = land & ~open0 & (filled > ground)
    bed1 = np.where(cand, ground, bed)
    sea, rcv, asc = kernels.lake_order(bed1, ~land, grid.nbr_off, grid.nbr_idx)
    wet, open1, _, _, _, basin = kernels.lakes_on(bed1, grid.nbr_off, grid.nbr_idx, src, loss, sea, rcv, asc)
    _, down, order = kernels.priority_flood(bed1, ~land, grid.nbr_off, grid.nbr_idx, 0.0)
    shut = cand & ~open1
    # each closed hollow's catchment: the hollow and the land that drains into it
    catch = _upstream_label(down, order, np.where(shut, basin, -1))
    m = catch >= 0
    dry = (np.bincount(catch[m], rain[m], minlength=grid.n)
           < DRYLAND_AI * np.bincount(catch[m], pet[m], minlength=grid.n))
    # ...and its lake stops short of the rim: some of its floor stays dry (a hollow its lake fills, a cell-mean
    # dip on a big river's course most often, is as likely to spill as not within a cell)
    dry &= np.bincount(basin[shut & ~wet], minlength=grid.n) > 0
    return shut & dry[basin]


@njit(cache=True)
def _upstream_label(down, order, lab):
    """lab carried up the rivers: an unlabelled cell gets its downstream
    cell's label (order: outlets first)."""
    out = lab.copy()
    for t in range(order.shape[0]):
        i = order[t]
        if out[i] < 0 and down[i] >= 0:
            out[i] = out[down[i]]
    return out


def _settle(grid, ground, land, src, loss, min_depth, min_slope, tries=4, dry=None, keep=None, seen=None):
    """kernels.lakes on _bed(ground), made to agree with the rivers.
    kernels.lakes gives each basin the water that runs downhill into it,
    but a lake that spills where its basin meets the sea's drainage can
    send its river on into a lower closed basin next to that spill point
    (route() follows the river there): that basin then gets the river too
    and fills further, and may spill in turn (the Nile into the Nubian
    hollow, PW-122). Returns ((bed, wet, open, out_z, pit, catch, basin),
    (flow, down, order, sink)) of the last try, and the dry hollows kept.
    dry (optional): (rain, potential evaporation) per cell, mm/yr: the dry
    catchments' closed hollows keep their own ground whatever their depth
    (_dry_hollows; keep: those lakes()' earlier carve tries kept, worked
    out once on the uncarved ground: a carved valley only lowers a kept
    hollow's ground, which the lake balance here takes as it is). After
    the rivers settle, a kept hollow is _bed's again if its catchment is
    wet after all or its lake spills (a river flows through it)."""
    bed0 = _bed(grid, ground, ~land, min_depth, min_slope)
    if keep is None:
        keep = (_dry_hollows(grid, ground, bed0, land, src, loss, *dry) if DRY_HOLLOWS and dry is not None
                and min_depth > 0 else np.zeros(grid.n, bool))
    keep = keep.copy()
    for rnd in range(3):
        extra = np.zeros(grid.n)
        bed = np.where(keep, ground, bed0)
        order0 = kernels.lake_order(bed, ~land, grid.nbr_off, grid.nbr_idx)  # (the same bed each try)
        for _ in range(tries):
            wet, open_, out_z, pit, catch, basin = kernels.lakes_on(bed, grid.nbr_off, grid.nbr_idx, src + extra,
                                                                    loss, *order0)
            r = (bed, wet, open_, out_z, pit, catch, basin)
            sink = land & ~open_ & (wet | pit)
            lk0 = dict(wet=wet, level=np.where(wet & open_, out_z, ground), bed=bed, sink=sink,
                       src=src - loss * wet, sea=~land)
            flow, down, order, _ = route(grid, ground, lk0, seen)
            more = kernels.closed_excess(sink, basin, wet, down, flow, src, loss, bed)
            if not more.any():
                break
            extra += more
        if not keep.any() or rnd == 2:
            break
        # a kept hollow whose catchment the rivers made wet after all (a spilling lake's river sent on into it:
        # the Nile into its desert hollows, PW-122) is no dry hollow: _bed's again; nor is the basin of a kept
        # lake that spills (filled to its rim by a wet corner of a mixed catchment, or by the carve tries' new
        # courses): its river flows on through it, a lake on a plain or in a shallow dip, as _bed has it
        lab, k = grid.components(keep)
        up = _upstream_label(down, order, lab)
        m = up >= 0
        ok = (np.bincount(up[m], dry[0][m], minlength=k) < DRYLAND_AI * np.bincount(up[m], dry[1][m], minlength=k))
        drop = keep & ~ok[np.maximum(lab, 0)]
        spill = keep & wet & open_
        if spill.any():
            drop |= keep & np.isin(basin, np.unique(basin[spill]))
        if not drop.any():
            break
        keep &= ~drop
    return r, (flow, down, order, sink), keep


def lakes(grid: Grid, elev: np.ndarray, runoff_mm: np.ndarray, aet_mm: np.ndarray,
          lake_evap_mm: np.ndarray, no_lake: np.ndarray | None = None, min_depth: float = MIN_DEPTH,
          min_slope: float = MIN_SLOPE, channel: float | None = None,
          outlet: np.ndarray | None = None, valley: np.ndarray | None = None,
          land: np.ndarray | None = None, pet_mm: np.ndarray | None = None) -> dict:
    """Where water stands. elev m; land: what isn't sea (default
    geo.is_land of elev: ground below 0 cut off from the sea is land, a
    hollow these lakes fill or leave dry); runoff, actual land
    evaporation and open-water evaporation in mm/yr; no_lake: cells that
    can't hold a lake (ice sheets); pet_mm (optional): the climate's
    potential evaporation over land, mm/yr: with it a closed hollow in a dry
    catchment is kept however shallow or flat (_dry_hollows). A cell's elevation is its mean over
    ~100 km, so a hollow less than min_depth below its spill point is taken
    to be drained by a river channel too small to resolve (water flows on
    through it, no lake). That holds inside basins too: a dip in a basin's
    floor less than min_depth below the saddle to the rest of the basin is
    part of the floor, not a pit with a lake of its own (kernels.fill_shallow),
    so a lake on a flat, rough floor is one level body of water. A wide
    hollow must also be at least min_slope (m per km) x its radius deep,
    radius = sqrt(area / pi) at its rim: one flatter than a big lowland
    river's gradient is a plain that rivers cross (or that they incise and
    fill), so it drains too. And a river leaving a basin runs in a valley
    cut below its cells' mean height, deeper the bigger the river
    (channel_depth, channel: its scale): a basin a big river flows out of
    drains down to that valley's level, so through-flowing lakes are only
    as big as the hollow below it (the outlet has cut down: PW-055); a
    closed basin has no outflowing river and keeps its water. outlet
    (optional, m, NaN where unknown): the height of each cell's river
    where it enters the cell, from finer data (the Earth world's,
    earth_data.earth_outlets): a river runs no higher than that, so its
    valley is cut down to it too (a cell's mean stands as a dam where a
    river crosses it in a gorge narrower than the cell). Generated worlds
    have none: their rivers cut their own valleys. valley (optional, m):
    how deep each cell's valley already is from rivers that ran there
    before (the run's memory of the 'incised' this returns, carried with
    the rock): a cut valley outlasts its river, so a basin that used to
    spill keeps the outlet it cut, and its lake rises no higher than that
    gap once the climate dries (it spills again through it if its inflow
    still beats the evaporation off a lake that big). Without it, a basin
    that just stopped spilling would fill its whole uncut hollow, which is
    far bigger than the lake that spilled: the lake would flip between a
    small open lake and a giant closed one (PW-300). Returns a dict of
    per-cell arrays:
      wet    under a lake
      kind   NO_LAKE, OPEN_LAKE (fresh: spills, its river flows on),
             CLOSED_LAKE (salty: ends its river, evaporation balances the
             inflow), SALT_PAN (a closed basin's dry floor whose inflow
             would cover only part of it: a playa / ephemeral lake)
      level  lake surface, m (same datum as elev); elev where no lake
      bed    elev with the shallow hollows filled (what route() flows over)
      sink   cells where rivers end (closed lakes and the pits of closed basins)
      src    water each cell adds to its river, flow units (m/yr per cell;
             negative under a lake that evaporates more than its rain)
      incised  m the rivers that reach base level (the sea, or through
             open lakes to it) cut their valleys below the cells' mean
             height now (0 elsewhere and with channel 0)"""
    channel = CHANNEL_K if channel is None else channel
    land = is_land(elev, grid=grid) if land is None else land
    ground = elev.astype(float)
    src = np.where(land, runoff_mm, 0.0) / 1000.0
    loss = np.where(land, np.maximum(lake_evap_mm - aet_mm, 0.0), 0.0) / 1000.0
    carved = ground
    dry = None if pet_mm is None else (np.where(land, runoff_mm + aet_mm, 0.0), np.where(land, pet_mm, 0.0))
    keep = None  # (the dry hollows: worked out on the uncarved ground, once, and kept across the carve tries)
    seen = []  # (the floods route() has run, to reuse)
    for k in range(CARVE_TRIES + 1 if channel > 0 else 1):
        (elev, wet, open_, out_z, pit, catch, _), (flow, down, order, sink), keep = _settle(
            grid, carved, land, src, loss, min_depth, min_slope, dry=dry, keep=keep, seen=seen)
        if k == CARVE_TRIES or channel <= 0:
            break
        # the same with the rivers' valleys cut in (only where they reach the
        # sea: a closed basin's rivers end in it whatever their valleys);
        # again while that changes where they run (a drained lake's floor is
        # a river's course now, a lake that spills now has an outlet to cut)
        reach = land & ~endorheic(down, order, sink)
        cut = channel * discharge(grid, flow) ** CHANNEL_B * reach
        if outlet is not None:  # (closed basins' too: the data's river crosses them)
            low = land & (outlet < ground)  # (NaN compares False)
            cut = np.where(low, np.maximum(cut, ground - np.where(low, outlet, 0.0)), cut)
        if valley is not None:  # (closed basins' too: the valley outlasts its river)
            cut = np.maximum(cut, np.where(land, valley, 0.0))
        if no_lake is not None:
            cut = cut * ~no_lake
        new = np.minimum(carved, kernels.carve(ground, down, order, cut))
        if k and np.abs(new - carved).max() < 1.0:
            break
        carved = new
    incised = np.zeros(grid.n)
    if channel > 0:
        # (a cut valley flooded below its cell's mean height is no lake)
        wet &= ~(open_ & (out_z <= ground))
        incised = channel * discharge(grid, flow) ** CHANNEL_B * (land & ~endorheic(down, order, sink))
        if no_lake is not None:
            incised = incised * ~no_lake
    if no_lake is not None:
        wet &= ~no_lake
    closed = land & ~open_
    kind = np.zeros(grid.n, np.int8)
    kind[wet & open_] = OPEN_LAKE
    kind[wet & closed] = CLOSED_LAKE
    pan = pit & closed & ~wet & (catch > 0) & (catch >= 0.1 * loss)
    kind[pan if no_lake is None else pan & ~no_lake] = SALT_PAN
    level = np.where(wet & open_, out_z, ground)
    # a closed lake's surface: between its highest wet cell and its lowest dry shore
    lab, k = grid.components(wet & closed)
    if k:
        m = lab >= 0
        top = np.full(k, -np.inf)
        np.maximum.at(top, lab[m], elev[m])
        shore = np.full(k, np.inf)
        a = np.concatenate([grid.edges[:, 0], grid.edges[:, 1]])
        b = np.concatenate([grid.edges[:, 1], grid.edges[:, 0]])
        sel = (lab[a] >= 0) & ~wet[b] & land[b]
        np.minimum.at(shore, lab[a][sel], elev[b][sel])
        lvl = np.where(np.isfinite(shore), 0.5 * (top + np.maximum(shore, top)), top)
        level[m] = np.maximum(lvl[lab[m]], ground[m])
        # (a river valley cut below its cell's mean height, flooded by the lake, is no lake; nor is a cell the
        # surface only reaches, its top level with its lowest shore)
        dry = m & (lvl[np.maximum(lab, 0)] <= ground)
        wet[dry], kind[dry], level[dry] = False, NO_LAKE, ground[dry]
    sink = land & closed & (wet | pit)
    if channel > 0 and valley is not None:
        # a dry pit that only the remembered valleys make (one its river has
        # moved off, or that rode off with the rock) is no closed basin:
        # rivers fill it and run on, over the cells' mean heights. (Not with
        # outlet: the finer data's gorges and basins are real.)
        spill = kernels.priority_flood(ground, ~land, grid.nbr_off, grid.nbr_idx, 0.01)[0]
        valley_pit = sink & ~wet & (spill <= ground + 1.0)
        sink &= ~valley_pit
        kind[valley_pit & (kind == SALT_PAN)] = NO_LAKE
    return dict(wet=wet, kind=kind, level=level, sink=sink, src=src - loss * wet, bed=np.asarray(elev, float),
                incised=incised, sea=~land)


FLOOD_EPS = 0.01  # m: route()'s priority flood's lift per cell across a filled pit


def _same_flood(surf, outlet, prev):
    """Whether priority_flood_to(surf, outlet) would give prev's result (outlet, filled, down, order of an earlier
    flood). The flood reads a cell's height only as max(height, its discoverer's level + eps), so a cell whose
    height changed but whose filled level does not (a pit's floor, filled to its rim before and after) leaves the
    whole run, and so its result, as it was."""
    o0, f0, d0, s0 = prev
    if not np.array_equal(outlet, o0):
        return False
    ch = np.flatnonzero(surf != s0)
    if ch.size == 0:
        return True
    dc = d0[ch]
    if outlet[ch].any() or (dc < 0).any():
        return False
    z = f0[dc] + FLOOD_EPS
    return bool((np.where(surf[ch] < z, z, surf[ch]) == f0[ch]).all())


def route(grid: Grid, elev: np.ndarray, lk: dict, seen: list | None = None):
    """Rivers over the lake surfaces, ending at the sea (lk's: lakes()') or a
    closed lake. Returns (flow, downstream, order, filled). seen (optional): a
    list the calls of one lakes() share, to reuse a flood that the surfaces
    since have left as it was (_same_flood: _settle's rechecks, after a
    dropped hollow, often change nothing the rivers see)."""
    surf = np.where(lk["wet"], lk["level"], lk["bed"]).astype(float)
    outlet = lk["sea"] | lk["sink"]
    res = None
    if seen is not None:
        for prev in reversed(seen):
            if _same_flood(surf, outlet, prev[:4]):
                res = prev[4:]
                break
    if res is None:
        res = kernels.priority_flood_to(surf, outlet, grid.nbr_off, grid.nbr_idx, FLOOD_EPS)
        if seen is not None:
            seen.append((outlet, res[0], res[1], surf, *res))
            del seen[:-6]
    filled, down, order = res
    flow = kernels.accumulate_lakes(down, order, lk["src"], lk["wet"])
    return flow, down, order, filled


BASEFLOW = 0.5  # share of a river's water that comes through the ground, spread over the unfrozen months
FROZEN_BASEFLOW = 0.05  # ...where the ground is frozen most of the year (permafrost: little groundwater)
FROZEN_C = -2.0  # C: a month this cold has its rivers and ground frozen


def seasonal_flow(grid: Grid, down: np.ndarray, order: np.ndarray, runoff_mm: np.ndarray, wet: np.ndarray,
                  c: dict) -> dict:
    """The rivers' year, month by month (PW-028). Each cell's runoff is
    spread over the months by what reaches its ground (climate.months'
    water: rain, and snow when it melts: a cold country's whole winter of
    snow comes off in a month or two of spring flood), part of it through
    the ground instead (BASEFLOW, spread over the months it isn't frozen;
    little where the ground is frozen most of the year), then gathered
    down the rivers like the annual flow. A lake stores a flood and lets it
    out slowly: at its outlet the profile is flattened toward its mean, the
    more the bigger the lake for its catchment (the St Lawrence barely
    floods). c: climate.compute's dict (lat-free fields temp, t_warm,
    t_cold, p_jul, p_jan). Returns
      flood_ratio  the peak month's flow over the mean month's (1 = steady;
                   ~1.5 for a rain-fed tropical giant, 3-5 for an Arctic
                   river's June flood)
      flood_month  the peak month, 1-12
      frozen       months a year the river is frozen (its cell below FROZEN_C)"""
    from . import climate
    mo = climate.months(grid.lat, c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"])
    w = mo["water"]
    share = w / np.maximum(w.sum(0), 1e-9)
    frozen = mo["t"] < FROZEN_C
    nf = frozen.sum(0)
    open_m = np.where(nf < 12, ~frozen / np.maximum(12 - nf, 1), 1 / 12)
    b = np.where(nf >= 6, FROZEN_BASEFLOW, BASEFLOW)
    src = np.maximum(runoff_mm, 0) / 1000.0 * 12 * ((1 - b) * share + b * open_m)
    # lake outlets: lake cells draining out of the lake, damped by lake area / catchment area
    lab, k = grid.components(wet)
    damp = np.zeros(grid.n)
    if k:
        upstream = kernels.accumulate(down, order, np.ones(grid.n))
        size = np.bincount(lab[lab >= 0], minlength=k).astype(float)
        out = wet & (down >= 0) & ~wet[np.maximum(down, 0)]
        damp[out] = np.clip(3.0 * size[lab[out]] / np.maximum(upstream[out], 1), 0, 0.9)
    q = kernels.accumulate_months(down, order, src, damp)
    mean = q.mean(0)
    ratio = np.where(mean > 1e-12, q.max(0) / np.maximum(mean, 1e-12), 1.0)
    return dict(flood_ratio=ratio, flood_month=q.argmax(0) + 1, frozen=nf)


def endorheic(down: np.ndarray, order: np.ndarray, sink: np.ndarray) -> np.ndarray:
    """Cells whose water never reaches the sea (it ends in a closed lake or salt pan)."""
    return _endorheic(down, order, sink.astype(np.bool_))


@njit(cache=True)
def _endorheic(down, order, sink):
    end = sink.copy()
    for t in range(order.shape[0]):  # outlets first, so each cell's downstream is already known
        i = order[t]
        if down[i] >= 0:
            end[i] = end[down[i]]
    return end


def walled(grid: Grid, region: np.ndarray) -> Grid:
    """grid with only the links between cells of the same region (an int
    per cell): no water crosses a region's edge, whatever the heights."""
    from dataclasses import replace
    keep = region[grid.edges[:, 0]] == region[grid.edges[:, 1]]
    src = np.repeat(np.arange(grid.n), np.diff(grid.nbr_off))
    ok = region[src] == region[grid.nbr_idx]
    off = np.concatenate([[0], np.cumsum(np.bincount(src[ok], minlength=grid.n))]).astype(grid.nbr_off.dtype)
    idx = np.ascontiguousarray(grid.nbr_idx[ok])
    nb = [idx[off[i]:off[i + 1]].tolist() for i in range(grid.n)]
    w = replace(grid, edges=grid.edges[keep], nbr_off=off, nbr_idx=idx, neighbors=nb, _raster=None)
    w.base = grid  # (its geometry: cell areas)
    return w


def rivers_and_lakes(grid: Grid, elev: np.ndarray, c: dict, ice: np.ndarray | None = None,
                     channel: float | None = None, outlet: np.ndarray | None = None,
                     closed: np.ndarray | None = None, valley: np.ndarray | None = None):
    """Rivers and lakes for a climate c (climate.compute's dict). Routed
    over the ice surface where there is land ice, with no lakes on it
    (channel, outlet, valley: as in lakes()). closed (optional; the Earth
    world's, earth_data.earth_closed): each cell's closed basin by finer
    data (an id, -1 for none). No river crosses a basin's edge (walled()),
    so each ends its rivers in its own lakes and pans, however the cell
    means slope, and its lake rises no higher than its rim (its lowest
    pass out: a wetter climate than the data's spills over it). A closed
    basin's rim is often a divide inside a cell, or its floor too flat for
    ~100 km cells to hold. Generated worlds have none: their closed basins
    are their own hollows.
    ice: grounded land ice (its surface above the sea, isostasy.grounded);
    a bed below the sea under it is land (geo.is_land, PW-307), so its
    water runs on over the ice and doesn't end there as at a coast.
    Returns (flow, downstream, lakes dict); the dict also has 'endorheic':
    land that drains to a closed basin rather than the sea, and 'order':
    the cells from the outlets up (route's)."""
    land = is_land(elev, ice, grid)
    iced = land & (ice > 0) if ice is not None else np.zeros(grid.n, bool)
    surf = elev + np.where(iced, ice, 0.0) if ice is not None else elev
    if closed is not None:
        basin = np.where(land, closed, -1)
        a = np.concatenate([grid.edges[:, 0], grid.edges[:, 1]])
        b = np.concatenate([grid.edges[:, 1], grid.edges[:, 0]])
        grid = walled(grid, basin)
        lab, k = grid.components(basin >= 0)  # (each connected piece of a basin)
        # each piece's rim: its lowest pass out (the higher of the two cells
        # either side; the divide, unresolved, is between them)
        rim = np.full(k, np.inf)
        sel = (basin[a] >= 0) & (basin[a] != basin[b])
        np.minimum.at(rim, lab[a][sel], np.maximum(surf[a], surf[b])[sel])
    lk = lakes(grid, surf, c["runoff"], c["aet"], c["lake_evap"], iced, channel=channel, outlet=outlet,
               valley=valley, land=land, pet_mm=c.get("pet"))
    if closed is not None and k:
        # a lake fills its basin no higher than the rim: what more its
        # rivers bring (a wetter climate than the data's) spills over the
        # divide and is lost
        top = np.where(lab >= 0, rim[np.maximum(lab, 0)], np.inf)
        dry = lk["wet"] & (surf >= top)
        lk["wet"] &= ~dry
        lk["kind"][dry] = NO_LAKE
        lk["level"] = np.where(lk["wet"], np.minimum(lk["level"], top), surf)
        lk["src"] = np.where(dry, np.where(land, c["runoff"], 0.0) / 1000.0, lk["src"])
    flow, down, order, _ = route(grid, surf, lk)
    lk["endorheic"] = endorheic(down, order, lk["sink"]) & land
    lk["level"] = np.where(lk["wet"], lk["level"], elev)  # (no lakes on the ice)
    lk["order"] = order
    return flow, down, lk
