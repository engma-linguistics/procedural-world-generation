"""Surface processes inside the tectonic loop: rock, rivers, erosion, sediment.

Every cell has a *basement* rock class (how its crust formed) and a layer of
sediment *cover* on top (km). Erosion strips the cover first, then attacks
the basement at that rock's rate. Eroded rock travels down the river network
and is deposited in closed basins (lakes) or at the river mouth, where it
spreads out into a shelf/delta. Isostasy (in tectonics.elevation) turns
removed or added crust into lower or higher ground.

Erosion at a 120-240 km cell size can't resolve individual valleys, so it has
two parts:
  denudation  the ground as a whole wears down, faster the higher it is
              (dh/dt = -(h/tau)(0.5 + h/2 km)), scaled by rock and rainfall
  incision    rivers cut down toward the next cell downstream at a rate
              ~ sqrt(water flow) (stream power), so big rivers keep their
              valleys low and drainage divides stay high

The rock table is meant to grow: more classes (limestone, sandstone vs shale,
evaporite, coal...) can be added as rows plus a rule for where they form.
"""

from __future__ import annotations

import numpy as np
from numba import njit

from . import kernels

# id, key, name, erodibility (relative), colour
ROCKS = [
    (0, "ocean", "oceanic basalt", 1.0, "#2b4a6f"),
    (1, "hotspot", "hotspot basalt", 1.6, "#8c2f39"),
    (2, "arc", "volcanic arc (andesite, granite)", 0.8, "#d1495b"),
    (3, "sediment", "sedimentary rock", 1.5, "#e9c46a"),
    (4, "orogen", "metamorphic belt (gneiss, schist)", 0.6, "#8e7dbe"),
    (5, "craton", "ancient shield (granite, gneiss)", 0.3, "#6c757d"),
]
OCEAN, HOTSPOT, ARC, SEDIMENT, OROGEN, CRATON = range(6)
ROCK_K = np.array([r[3] for r in ROCKS])
COVER_K = 2.0  # loose-ish sedimentary cover erodes fastest
COVER_SHOWS = 0.05  # km of cover before it, not the basement, is what's exposed


def rain_factor(precip_mm):
    """Wetter ground erodes faster, but only weakly (relief matters more)."""
    return np.clip(np.sqrt(np.maximum(precip_mm, 0) / 800.0), 0.25, 2.0)


@njit(cache=True)
def _route(down, order, sed, pit_room, is_ocean):
    """Carry eroded rock (km of crust per cell) down the river network,
    headwaters first. Closed basins keep what fits; everything else ends at
    the ocean cell where the river meets the sea."""
    n = sed.shape[0]
    dep = np.zeros(n)
    flux = sed.copy()
    for t in range(order.shape[0] - 1, -1, -1):
        i = order[t]
        if is_ocean[i]:
            dep[i] += flux[i]
            continue
        if pit_room[i] > 0:
            keep = min(flux[i], pit_room[i])
            dep[i] += keep
            flux[i] -= keep
        d = down[i]
        if d >= 0:
            flux[d] += flux[i]
        else:
            dep[i] += flux[i]
    return dep


@njit(cache=True)
def _spread(dep, ea, eb, k, n_sub):
    """Spread sea-floor deposits out from river mouths (deltas, shelves)."""
    d = dep.copy()
    flux = np.empty(len(ea))
    for _ in range(n_sub):
        for e in range(len(ea)):
            flux[e] = k * (d[eb[e]] - d[ea[e]])
        for e in range(len(ea)):
            d[ea[e]] += flux[e]
            d[eb[e]] -= flux[e]
    return d


def erode(grid, elev, thick, cover, rock, cont, precip, dt, tau, incision, scale, iso_land, iso_sea):
    """One step of erosion + sediment transport on the world view.
    Returns (thick, cover, removed_km, flow, downstream)."""
    n = grid.n
    land = elev > 0
    filled, down, order = kernels.priority_flood(elev.astype(float), grid.nbr_off, grid.nbr_idx, 0.01)
    rain_m = np.where(land, precip, 0) / 1000.0
    flow = kernels.accumulate(down, order, rain_m)

    K = np.where(cover > COVER_SHOWS, COVER_K, ROCK_K[rock]) * rain_factor(precip)
    # denudation toward base level (continental interiors settle ~200 m up)
    base = np.where(cont, 200.0, 0.0)
    above = np.maximum(elev - base, 0) * land
    h = elev - above + above / (1 + dt / tau * K * (0.5 + above / 2000.0))
    # river incision toward the next cell downstream (implicit, unconditionally stable)
    h = h.astype(float)
    kernels.stream_power(h, down, order, np.where(land, incision * K * np.sqrt(flow) * dt, 0.0))
    removed = np.maximum(elev - h, 0) * land / iso_land  # km of rock

    from_cover = np.minimum(cover, removed)
    cover = cover - from_cover
    thick = thick - removed

    # route it: lakes keep what fits, the rest reaches the sea
    pit_room = np.where(land, np.maximum(filled - elev - 5, 0) / iso_land, 0.0)
    dep = _route(down, order, removed, pit_room, ~land)
    ocean = ~land
    ea, eb = grid.edges[:, 0], grid.edges[:, 1]
    sea = ocean[ea] & ocean[eb]
    dep_sea = _spread(np.where(ocean, dep, 0.0), ea[sea], eb[sea], 0.15, int(round(4 * scale**2)))
    dep = np.where(ocean, dep_sea, dep)
    thick = thick + dep
    cover = cover + dep
    return thick, cover, removed, flow, down
