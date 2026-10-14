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


def lakes(grid: Grid, elev: np.ndarray, runoff_mm: np.ndarray, aet_mm: np.ndarray,
          lake_evap_mm: np.ndarray, no_lake: np.ndarray | None = None, min_depth: float = MIN_DEPTH) -> dict:
    """Where water stands. elev m (<= 0 is sea); runoff, actual land
    evaporation and open-water evaporation in mm/yr; no_lake: cells that
    can't hold a lake (ice sheets). A cell's elevation is its mean over
    ~100 km, so a hollow less than min_depth below its spill point is taken
    to be drained by a river channel too small to resolve (water flows on
    through it, no lake). Returns a dict of per-cell arrays:
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
    land = elev > 0
    ground = elev.astype(float)
    if min_depth > 0:
        filled, _, _ = priority_flood(grid, ground)
        elev = np.where(filled - ground < min_depth, filled, ground)
    src = np.where(land, runoff_mm, 0.0) / 1000.0
    loss = np.where(land, np.maximum(lake_evap_mm - aet_mm, 0.0), 0.0) / 1000.0
    wet, open_, out_z, pit, catch = kernels.lakes(elev, grid.nbr_off, grid.nbr_idx, src, loss)
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


def endorheic(down: np.ndarray, order: np.ndarray, sink: np.ndarray) -> np.ndarray:
    """Cells whose water never reaches the sea (it ends in a closed lake or salt pan)."""
    end = sink.copy()
    for i in order:  # outlets first, so each cell's downstream is already known
        if down[i] >= 0:
            end[i] = end[down[i]]
    return end


def rivers_and_lakes(grid: Grid, elev: np.ndarray, c: dict, ice: np.ndarray | None = None):
    """Rivers and lakes for a climate c (climate.compute's dict). Routed
    over the ice surface where there is land ice, with no lakes on it.
    Returns (flow, downstream, lakes dict); the dict also has 'endorheic':
    land that drains to a closed basin rather than the sea."""
    land = elev > 0
    iced = land & (ice > 0) if ice is not None else np.zeros(grid.n, bool)
    surf = elev + np.where(iced, ice, 0.0) if ice is not None else elev
    lk = lakes(grid, surf, c["runoff"], c["aet"], c["lake_evap"], iced)
    flow, down, order, _ = route(grid, surf, lk)
    lk["endorheic"] = endorheic(down, order, lk["sink"]) & land
    lk["level"] = np.where(lk["wet"], lk["level"], elev)  # (no lakes on the ice)
    return flow, down, lk
