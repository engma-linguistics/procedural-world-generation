"""The earth system around the plates: mantle heat, global temperature and
CO2, sea level, the climate model, and the surface processes that run on
its rain (erosion, rivers, sediment).

State it keeps on the simulation (see Simulation.EARTH_STATE): dT, drift,
co2, refs, depth_ref, sea_level and its parts sea_ice / sea_tect, ice, veg,
removed, the climate fields from climate.compute, and the rivers (flow,
down).
"""

from __future__ import annotations

import numpy as np

from .. import climate, hydrology, kernels, surface
from ..geo import R_KM
from .isostasy import CARB, COAL, EVAP, MIX, SAND, elevation, isostasy, ocean_depth


def heat(p, t: float) -> float:
    """Mantle heat relative to today's. A young planet is hotter (more
    radioactive decay, leftover heat of formation): more plumes, more
    melting at arcs, a runnier mantle and faster plates. It fades toward
    1 with the given half-life."""
    return 1.0 + (p.heat_start - 1.0) * 0.5 ** (t / p.heat_halflife)


def target_fraction(p, t: float) -> float:
    """Share of the surface the continents are steered toward at time t."""
    if p.continental_start < 0:
        return p.continental_fraction
    return p.continental_fraction + (p.continental_start - p.continental_fraction) * np.exp(
        -t / p.continental_growth)


def global_temperature(sim, growth, newc, rng):
    """The planet's mean temperature, as an offset dT from today's Earth.
    Three things move it, slowly (tens of Myr):
      drift      a random walk that keeps returning toward 0 (all the
                 carbon-cycle and ocean details this model doesn't have)
      CO2        volcanism at ridges and arcs adds it (warming); fresh
                 rock weathering in warm, wet mountains removes it
                 (cooling, e.g. the Himalaya since 40 Ma). Each is measured
                 against its own slow average, so only changes count.
      ice        ice sheets reflect sunlight (cooling feedback)
    Real Earth: a few long icehouse eras (Cryogenian, late Ordovician,
    Permo-Carboniferous, today) between long greenhouse ones.
    growth: arc crust growth this step (km/Myr per cell); newc: number of
    new ocean-floor cells this step."""
    p, dt = sim.params, sim.dt
    a = np.exp(-dt / p.climate_drift_time)
    sim.drift = sim.drift * a + p.climate_drift * np.sqrt(1 - a * a) * rng.normal()
    land = sim.w_elev > 0
    warm = np.exp(0.06 * (sim.temp - 15.0)) if sim.temp is not None else 1.0  # chemical weathering
    warm = warm * (1 + 0.5 * sim.veg)  # roots and soils speed it up
    source = newc / sim.scale**2 + 20.0 * growth.sum() / sim.scale**2
    sink = float((sim.removed * land * warm).sum()) / sim.scale**2
    now = np.array([max(source, 1e-6), max(sink, 1e-6)])
    if sim.refs is None:
        sim.refs = now.copy()
    # (the baselines learn fast at first: the made-up starting state
    # isn't an equilibrium, and shouldn't jolt the climate)
    b = 1 - np.exp(-dt / min(200.0, 10.0 + sim.t))
    sim.refs = sim.refs + b * (now - sim.refs)
    rel = now / sim.refs
    # smooth the noisy per-step rates over ~10 Myr
    c = 1 - np.exp(-dt / 10.0)
    sim.co2 += c * (np.log(rel[0]) - np.log(rel[1]) - sim.co2)
    # Sea level also follows the ocean basins: young sea floor is hot and
    # shallow, so when ridges are long and fast the water has less room
    # and floods the continents (the Cretaceous, ~200 m higher than now).
    # Halved because the extra water also pushes the sea floor down.
    # Measured against a slow (300 Myr) average of itself, which starts
    # from the initial sea floor (sea level 0), so only real changes in
    # spreading move the sea.
    ocean = ~sim.w_cont
    depth = float(ocean_depth(sim.w_age[ocean]).mean()) if ocean.any() else 0.0
    if sim.depth_ref is None:  # the starting sea floor defines sea level 0
        sim.depth_ref = depth
    sim.depth_ref += (1 - np.exp(-dt / min(300.0, 10.0 + sim.t))) * (depth - sim.depth_ref)
    sim.sea_tect = float(np.clip(0.5 * (depth - sim.depth_ref), -250, 250))
    # A hotter mantle melts more at ridges: thicker, more buoyant ocean
    # crust and shallower ocean basins, so the same water stands higher
    # on the continents (one reason the young Earth was mostly sea).
    sim.sea_tect += p.hot_sea * (sim.heat() - 1.0)
    sim.sea_level = sim.sea_ice + sim.sea_tect
    ice_frac = (sim.ice > 0).mean()
    target = sim.drift + p.co2_sensitivity * np.clip(sim.co2, -1.5, 1.5) - p.ice_albedo * ice_frac / 0.03
    sim.dT += (1 - np.exp(-dt / 5.0)) * (target + p.climate_offset - sim.dT)


def climate_due(sim) -> bool:
    """The climate is updated on the first step and then at every multiple of
    climate_every Myr, so keyframes on those multiples show current climate."""
    k = sim.params.climate_every
    return sim.precip is None or (sim.t + 1e-9) // k > (sim.climate_t + 1e-9) // k


def update_climate(sim, e):
    """Temperature, seasons, rain, ice and Koppen class on elevation e
    (m above the current sea level, without ice)."""
    p, g = sim.params, sim.grid
    land = e > 0
    c = climate.compute(g, e, sim.dT, p.tilt, np.where(land, sim.ice, 0.0))
    sim.temp, sim.t_warm, sim.t_cold = c["temp"], c["t_warm"], c["t_cold"]
    sim.precip, sim.p_jul, sim.p_jan = c["precip"], c["p_jul"], c["p_jan"]
    sim.runoff, sim.aet, sim.lake_evap = c["runoff"], c["aet"], c["lake_evap"]
    sim.wind, sim.current = 0.5 * (c["wind_jul"] + c["wind_jan"]), c["current"]
    # Ice: where summers stay near freezing and there's snow to feed it.
    # The real ice comes and goes with ~100 kyr cycles; this is the
    # average extent over them. Ice sheets thicken inland from their edges.
    iced = land & (sim.t_warm < p.ice_summer_temp) & (sim.precip > 25)
    edge = np.flatnonzero(iced & (np.add.reduceat(~iced[g.nbr_idx], g.nbr_off[:-1]) > 0))
    hops, _ = kernels.bfs_within(edge, iced.astype(np.int64), g.nbr_off, g.nbr_idx, 10**6)
    d_km = np.maximum(hops, 0) * g.spacing * R_KM
    sim.ice = np.where(iced, 300.0 + 2700.0 * (1 - np.exp(-d_km / 600.0)), 0.0)
    # The water locked up in it lowers the sea everywhere (ice ~0.9 g/cm3).
    vol = (sim.ice / 1000.0).sum() * sim.cell_area * R_KM**2
    ocean_area = (~land).sum() * sim.cell_area * R_KM**2
    sim.sea_ice = -0.9 * vol / max(ocean_area, 1.0) * 1000.0
    sim.sea_level = sim.sea_ice + sim.sea_tect
    sim.koppen = climate.koppen(e, sim.temp, sim.t_warm, sim.t_cold, sim.precip, sim.p_jul,
                                sim.p_jan, g.lat, sim.ice)
    sim.climate_t = sim.t


def erode(sim, col):
    """Weather, ice, rivers, erosion, sediment transport (surface.erode) on
    the crust column col, in place. Returns (deposited km, lake class) per
    cell for sediments()."""
    p, g, dt = sim.params, sim.grid, sim.dt
    t, cover, x, cont, rock = col.t, col.cover, col.x, col.cont, col.rock
    # Glaciers grind their beds hard where they slide on meltwater (the
    # 'glacial buzzsaw' that keeps ranges from growing much above the
    # snowline); polar ice frozen to its bed protects it instead.
    k_mult = np.where(sim.ice > 0, np.where(sim.t_warm > -8, p.glacial_erosion, 0.3), 1.0)
    # Plants (once they exist) hold soil on wet ground; bare wet ground
    # washes away faster. Deserts are bare either way.
    wet = np.clip(sim.precip / 800.0, 0, 1)
    sim.veg = (sim.t >= p.plants_from) * wet * np.clip((sim.t_warm - 5) / 10, 0, 1) * (sim.w_elev > 0)
    k_mult = k_mult * (1 + 0.6 * wet * (1 - sim.veg))
    t0 = t
    col.t, col.cover, x[:, MIX], sim.removed, dep, sim.flow, sim.down, lake = surface.erode(
        g, elevation(t, sim.w_age, cont, rock, sim.swell - sim.sea_level), t, cover, x[:, MIX],
        rock, cont, sim.precip, sim.runoff, sim.aet, sim.lake_evap, dt, p.hillslope, p.erosion_timescale,
        p.erosion_height, p.incision, sim.scale, isostasy(cont, rock), k_mult, p.alluvial, p.fan_km)
    sim.book("erosion", t0, col.t, cont)
    return dep, lake


def sediments(sim, col, dep, lake):
    """Which kind of sediment forms where. In place on col.x; returns the
    chemical deposits (km of crust per cell), which are added later with
    the reefs.
      sand       near its source (lakes, rivers, beaches, deltas); farther
                 out only mud settles. Desert winds sort loose cover into dunes.
      evaporite  where water evaporates faster than it arrives: closed
                 lakes and salt pans in warm basins (Dead Sea, Great Salt Lake) and
                 shallow hot seas next to desert (the Persian Gulf)
      coal       warm, wet, low-lying swamps full of plants, if plants
                 exist (none before land plants ~450 Ma on Earth)"""
    p, g, dt = sim.params, sim.grid, sim.dt
    x, cover = col.x, col.cover
    e = elevation(col.t, sim.w_age, col.cont, col.rock, sim.swell - sim.sea_level)
    land = e > 0
    x[:, SAND] += dep * np.where(land, 0.6, np.where(e > -200, 0.5, 0.15))
    shale = np.maximum(cover - x[:, MIX].sum(1), 0)
    dunes = land & (sim.precip < 200)
    x[:, SAND] += np.where(dunes, shale * (1 - np.exp(-0.01 * dt)), 0)
    T, P = sim.temp, sim.precip
    n_land = np.add.reduceat(land[g.nbr_idx], g.nbr_off[:-1])
    salt_lake = ((lake == hydrology.CLOSED_LAKE) | (lake == hydrology.SALT_PAN)) & (T > 10)
    sabkha = ~land & (e > -300) & (n_land > 0) & (T >= 22) & (P < 400)
    evap = (salt_lake * p.evaporite_rate + sabkha * 0.25 * p.evaporite_rate) * dt
    swamp = land & (e < 250) & (P > 1000) & (sim.veg > 0.5)
    coal = swamp * p.coal_rate * dt
    x[:, EVAP] += evap
    x[:, COAL] += coal
    return evap + coal


def bury(sim, col):
    """Deep in a thick pile the sediment is cooked into metamorphic rock:
    it stays crust, but it's basement now, not cover."""
    cooked = np.maximum(col.cover - sim.params.metamorphic_depth, 0)
    col.x[:, MIX] *= (1 - cooked / np.maximum(col.cover, 1e-9))[:, None]
    col.cover = col.cover - cooked


def reefs(sim, col, dep, chem):
    """Reefs: in warm, clear, shallow sea, corals and other carbonate
    makers build up to just below sea level, fast enough to outpace any
    subsidence. A volcanic island that sinks with its ageing sea floor
    becomes an atoll; carried out of the tropics, the reef dies and it
    drowns into a flat-topped seamount (the Darwin point, ~30 deg).
    Muddy water from big rivers stops them (no reefs off the Amazon).
    The chemical sediments (evaporite, coal) join the crust here too."""
    p, dt = sim.params, sim.dt
    cont, rock = col.cont, col.rock
    e = elevation(col.t, sim.w_age, cont, rock, sim.swell - sim.sea_level)
    reef = (e < -5) & (e > -1500) & (sim.temp >= p.reef_temp) & (dep * 1000 < p.reef_mud * dt)
    grow = np.minimum(p.reef_rate * np.exp((e + 5) / 150.0) * dt, -5 - e) * reef  # m of elevation
    carb = grow / isostasy(cont, rock)
    col.t, col.cover = col.t + carb, col.cover + carb
    col.x[:, CARB] += carb
    col.t, col.cover = col.t + chem, col.cover + chem
    sim.book("reef+chem", 0, carb + chem, cont)
