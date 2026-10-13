"""Surface processes inside the tectonic loop: rock, rivers, erosion, sediment.

Every cell has a *basement* rock class (how its crust formed) and a layer of
sediment *cover* on top (km). Erosion strips the cover first, then attacks
the basement at that rock's rate. Eroded rock travels down the river network
and is deposited in closed basins (lakes) or at the river mouth, where it
spreads out into a shelf/delta. Isostasy (in tectonics.elevation) turns
removed or added crust into lower or higher ground.

Erosion at a 60-240 km cell size can't resolve individual valleys, so it has
three parts, all scaled by rock and rainfall:
  hillslope   ground wears down in proportion to how far it stands above its
              neighbours (Ahnert 1970: denudation ~ local relief). Steep range
              fronts and plateau edges go fast; a plateau's flat interior and
              broad old uplands barely change. Like a diffusion (rate ~
              kappa * drop / spacing^2), so it's the same at any resolution.
  weathering  everything above base level also wears down, slowly when low
              and much faster when high (dh/dt = -(h/tau)(1 + (h/h0)^2), h
              above base): high ground has deep valleys, frost and glaciers
              below the cell scale, so young ranges are cut down quickly
              while old ones linger at 1-2 km (Montgomery & Brandon 2002)
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
    (6, "limestone", "limestone (reefs, carbonate platforms)", 1.0, "#a8dadc"),
]
OCEAN, HOTSPOT, ARC, SEDIMENT, OROGEN, CRATON, LIMESTONE = range(7)
ROCK_K = np.array([r[3] for r in ROCKS])
# Cover is a well-mixed column: ordinary sediment plus some km of carbonate
# and lava (tectonics.EXTRA); its erodibility is the mix of theirs.
COVER_K = 2.0  # loose-ish sand and mud erode fastest
CARB_K, LAVA_K = ROCK_K[LIMESTONE], ROCK_K[HOTSPOT]
COVER_SHOWS = 0.05  # km of cover before it, not the basement, is what's exposed


R_KM = 6371.0


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


def surface_rock(rock, cover, carb, lava):
    """What's exposed at the surface: the basement, unless sediment covers it."""
    sed = np.where(carb > 0.5 * cover, LIMESTONE, np.where(lava > 0.5 * cover, HOTSPOT, SEDIMENT))
    return np.where(cover > COVER_SHOWS, sed, rock).astype(np.uint8)


def erode(grid, elev, thick, cover, carb, lava, rock, cont, precip, dt, hillslope, tau, h0, incision, scale, iso,
          k_mult=1.0):
    """One step of erosion + sediment transport on the world view. Eroded
    cover takes its carbonate and lava with it pro rata; what's deposited
    is ordinary sediment. iso: m of elevation per km of crust, per cell;
    k_mult: extra erodibility factor per cell (glaciers).
    Returns (thick, cover, carb, lava, removed_km, deposited_km, flow, downstream)."""
    n = grid.n
    land = elev > 0
    filled, down, order = kernels.priority_flood(elev.astype(float), grid.nbr_off, grid.nbr_idx, 0.01)
    rain_m = np.where(land, precip, 0) / 1000.0
    flow = kernels.accumulate(down, order, rain_m)

    c = np.maximum(cover, 1e-9)
    k_cover = (COVER_K * (cover - carb - lava) + CARB_K * carb + LAVA_K * lava) / c
    K = np.where(cover > COVER_SHOWS, k_cover, ROCK_K[rock]) * rain_factor(precip) * k_mult
    # hillslope: relax toward the neighbours (4/d^2 * mean drop is the
    # Laplacian on this grid; exponential form can't overshoot)
    d_km = grid.spacing * R_KM
    relief = _relief(elev.astype(float), grid.nbr_off, grid.nbr_idx) * land
    h = elev - relief * (1 - np.exp(-4 * hillslope * K * dt / d_km**2))
    # weathering toward base level (continental interiors settle ~200 m up)
    base = np.where(cont, 200.0, 0.0)
    above = np.maximum(h - base, 0) * land
    h = h - above * (1 - np.exp(-K * dt / tau * (1 + (above / h0) ** 2)))
    # river incision toward the next cell downstream (implicit, unconditionally stable)
    h = h.astype(float)
    kernels.stream_power(h, down, order, np.where(land, incision * K * np.sqrt(flow) * dt, 0.0))
    removed = np.minimum(np.maximum(elev - h, 0) * land / iso, np.maximum(thick, 0))  # km of rock

    from_cover = np.clip(removed, 0, np.maximum(cover, 0))
    keep = 1 - from_cover / c
    carb, lava = carb * keep, lava * keep
    cover = cover - from_cover
    thick = thick - removed

    # route it: lakes keep what fits, the rest reaches the sea
    pit_room = np.where(land, np.maximum(filled - elev - 5, 0) / iso, 0.0)
    dep = _route(down, order, removed, pit_room, ~land)
    ocean = ~land
    ea, eb = grid.edges[:, 0], grid.edges[:, 1]
    sea = ocean[ea] & ocean[eb]
    dep_sea = _spread(np.where(ocean, dep, 0.0), ea[sea], eb[sea], 0.15, int(round(4 * scale**2)))
    dep = np.where(ocean, dep_sea, dep)
    thick = thick + dep
    cover = cover + dep
    return thick, cover, carb, lava, removed, dep, flow, down
