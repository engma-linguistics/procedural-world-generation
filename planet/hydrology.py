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

from . import kernels
from .grid import Grid


def priority_flood(grid: Grid, elev: np.ndarray, eps: float = 0.01):
    """Returns (filled, downstream, order). order runs outlet -> headwater."""
    return kernels.priority_flood(elev.astype(float), grid.nbr_off, grid.nbr_idx, eps)


def accumulate(down: np.ndarray, order: np.ndarray, rain: np.ndarray) -> np.ndarray:
    return kernels.accumulate(down, order, rain.astype(float))


def erode(grid: Grid, elev: np.ndarray, runoff_mm: np.ndarray, iterations: int = 12,
          strength: float = 1.0, diffusion: float = 0.08):
    """Carve river valleys with the runoff (mm/yr). Returns new elevation."""
    h = elev.astype(float).copy()
    rain = runoff_mm / 1000.0  # metres/yr; flow then ~ 'cells x m/yr'
    # finer cells -> more upstream cells; (tuned on rain: runoff is ~40% of
    # it, so 1/sqrt(0.4) keeps the cutting the same on average)
    k = 0.018 * 1.6 * strength * 2 ** (grid.level - 5)
    a, b = grid.edges[:, 0], grid.edges[:, 1]
    deg = np.bincount(np.concatenate([a, b]), minlength=grid.n)
    for _ in range(iterations):
        _, down, order = priority_flood(grid, h)
        flow = accumulate(down, order, rain)
        kernels.stream_power(h, down, order, k * np.sqrt(flow))
        # Hillslope creep: land relaxes a bit toward its neighbours.
        land = h > 0
        nb_mean = (np.bincount(a, h[b], grid.n) + np.bincount(b, h[a], grid.n)) / deg
        h = np.where(land, (1 - diffusion) * h + diffusion * np.maximum(nb_mean, 1.0), h)
    return h


# lake_kind values
NO_LAKE, OPEN_LAKE, CLOSED_LAKE, SALT_PAN = 0, 1, 2, 3


MIN_DEPTH = 20.0  # m: shallower hollows in the cell-mean terrain are drained by unresolved channels
# m per km: a wide hollow must also fall at least this steeply from its rim
# to its middle (depth / sqrt(area / pi)), or it is a plain that rivers cross
MIN_SLOPE = 0.1
# depth of the valley a river runs in below its cells' mean height, m:
# CHANNEL_K x (discharge in m^3/s) ** CHANNEL_B
CHANNEL_K, CHANNEL_B = 0.1, 0.7
CARVE_TRIES = 2  # times the valleys are recut as the rivers they carry move


def discharge(grid: Grid, flow: np.ndarray) -> np.ndarray:
    """m^3/s from flow units (cells x m/yr of runoff)."""
    return flow * (4 * np.pi * 6.371e6**2 / grid.n) / 3.156e7


def _fill(grid, ground, src, loss, min_depth, min_slope):
    """fill_shallow then kernels.lakes on ground: (bed, wet, open, out_z, pit, catch, basin)."""
    elev = ground
    if min_depth > 0:
        # hollows (and dips in a basin's floor) shallower than min_depth, or
        # flatter than min_slope, fill to where they spill; the rest of the land drains as priority_flood has it
        from .ocean import cell_area_km2
        h, keep = kernels.fill_shallow(ground, grid.nbr_off, grid.nbr_idx, float(min_depth),
                                       cell_area_km2(grid), float(min_slope))
        elev = np.where(keep, h, priority_flood(grid, h)[0])
    return (elev, *kernels.lakes(elev, grid.nbr_off, grid.nbr_idx, src, loss))


def _settle(grid, ground, land, src, loss, min_depth, min_slope, tries=4):
    """_fill, made to agree with the rivers. kernels.lakes gives each basin
    the water that runs downhill into it, but a lake that spills where its
    basin meets the sea's drainage can send its river on into a lower
    closed basin next to that spill point (route() follows the river
    there): that basin then gets the river too and fills further, and may
    spill in turn (the Nile into the Nubian hollow, PW-122). Returns
    (_fill's tuple, (flow, down, order, sink)) of the last try."""
    extra = np.zeros(grid.n)
    for _ in range(tries):
        bed, wet, open_, out_z, pit, catch, basin = r = _fill(grid, ground, src + extra, loss, min_depth, min_slope)
        sink = land & ~open_ & (wet | pit)
        lk0 = dict(wet=wet, level=np.where(wet & open_, out_z, ground), bed=bed, sink=sink, src=src - loss * wet)
        flow, down, order, _ = route(grid, ground, lk0)
        more = kernels.closed_excess(sink, basin, wet, down, flow, src, loss, bed)
        if not more.any():
            break
        extra += more
    return r, (flow, down, order, sink)


def lakes(grid: Grid, elev: np.ndarray, runoff_mm: np.ndarray, aet_mm: np.ndarray,
          lake_evap_mm: np.ndarray, no_lake: np.ndarray | None = None, min_depth: float = MIN_DEPTH,
          min_slope: float = MIN_SLOPE, channel: float | None = None) -> dict:
    """Where water stands. elev m (<= 0 is sea); runoff, actual land
    evaporation and open-water evaporation in mm/yr; no_lake: cells that
    can't hold a lake (ice sheets). A cell's elevation is its mean over
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
    closed basin has no outflowing river and keeps its water. Returns a
    dict of per-cell arrays:
      wet    under a lake
      kind   NO_LAKE, OPEN_LAKE (fresh: spills, its river flows on),
             CLOSED_LAKE (salty: ends its river, evaporation balances the
             inflow), SALT_PAN (a closed basin's dry floor whose inflow
             would cover only part of it: a playa / ephemeral lake)
      level  lake surface, m (same datum as elev); elev where no lake
      bed    elev with the shallow hollows filled (what route() flows over)
      sink   cells where rivers end (closed lakes and the pits of closed basins)
      src    water each cell adds to its river, flow units (m/yr per cell;
             negative under a lake that evaporates more than its rain)"""
    channel = CHANNEL_K if channel is None else channel
    land = elev > 0
    ground = elev.astype(float)
    src = np.where(land, runoff_mm, 0.0) / 1000.0
    loss = np.where(land, np.maximum(lake_evap_mm - aet_mm, 0.0), 0.0) / 1000.0
    carved = ground
    for k in range(CARVE_TRIES + 1 if channel > 0 else 1):
        (elev, wet, open_, out_z, pit, catch, _), (flow, down, order, sink) = _settle(grid, carved, land, src, loss,
                                                                                  min_depth, min_slope)
        if k == CARVE_TRIES or channel <= 0:
            break
        # the same with the rivers' valleys cut in (only where they reach the
        # sea: a closed basin's rivers end in it whatever their valleys);
        # again while that changes where they run (a drained lake's floor is
        # a river's course now, a lake that spills now has an outlet to cut)
        cut = channel * discharge(grid, flow) ** CHANNEL_B * (land & ~endorheic(down, order, sink))
        if no_lake is not None:
            cut = cut * ~no_lake
        new = np.minimum(carved, kernels.carve(ground, down, order, cut))
        if k and np.abs(new - carved).max() < 1.0:
            break
        carved = new
    if channel > 0:
        # (a cut valley flooded below its cell's mean height is no lake)
        wet &= ~(open_ & (out_z <= ground))
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
        # (a river valley cut below its cell's mean height, flooded by the lake, is no lake)
        dry = m & (lvl[np.maximum(lab, 0)] < ground)
        wet[dry], kind[dry], level[dry] = False, NO_LAKE, ground[dry]
    sink = land & closed & (wet | pit)
    return dict(wet=wet, kind=kind, level=level, sink=sink, src=src - loss * wet, bed=np.asarray(elev, float))


def route(grid: Grid, elev: np.ndarray, lk: dict):
    """Rivers over the lake surfaces, ending at the sea or a closed lake.
    Returns (flow, downstream, order, filled)."""
    surf = np.where(lk["wet"], lk["level"], lk["bed"]).astype(float)
    filled, down, order = kernels.priority_flood_to(surf, (surf <= 0) | lk["sink"], grid.nbr_off,
                                                    grid.nbr_idx, 0.01)
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
    end = sink.copy()
    for i in order:  # outlets first, so each cell's downstream is already known
        if down[i] >= 0:
            end[i] = end[down[i]]
    return end


def rivers_and_lakes(grid: Grid, elev: np.ndarray, c: dict, ice: np.ndarray | None = None,
                     channel: float | None = None):
    """Rivers and lakes for a climate c (climate.compute's dict). Routed
    over the ice surface where there is land ice, with no lakes on it
    (channel: as in lakes()).
    Returns (flow, downstream, lakes dict); the dict also has 'endorheic':
    land that drains to a closed basin rather than the sea, and 'order':
    the cells from the outlets up (route's)."""
    land = elev > 0
    iced = land & (ice > 0) if ice is not None else np.zeros(grid.n, bool)
    surf = elev + np.where(iced, ice, 0.0) if ice is not None else elev
    lk = lakes(grid, surf, c["runoff"], c["aet"], c["lake_evap"], iced, channel=channel)
    flow, down, order, _ = route(grid, surf, lk)
    lk["endorheic"] = endorheic(down, order, lk["sink"]) & land
    lk["level"] = np.where(lk["wet"], lk["level"], elev)  # (no lakes on the ice)
    lk["order"] = order
    return flow, down, lk
