"""The earth system around the plates: mantle heat, global temperature and
CO2, sea level, the climate model, and the surface processes that run on
its rain (erosion, rivers, sediment).

State it keeps on the simulation (see Simulation.EARTH_STATE): dT, drift,
co2, refs, depth_ridge, depth_ref, sea_level and its parts sea_ice / sea_tect, ice, veg,
removed, the climate fields from climate.compute, the rivers (flow,
down) and the lakes (lake_kind, lake_depth).
"""

from __future__ import annotations

import numpy as np

from .. import climate, hydrology, kernels, surface
from ..geo import R_KM
from ..surface import COAL as COAL_ROCK, EVAPORITE, LIMESTONE, SANDSTONE, SHALE
from . import record
from .isostasy import CARB, COAL, EVAP, MIX, SAND, elevation, isostasy, ocean_depth, sediment_iso, sediment_km

SEA_TECT_MAX = 250.0  # m: the ocean basins' part of sea level levels off toward +-this


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
    # The basins' volume (depth_ridge) follows the mean depth of the floor
    # over ridge_time Myr: a real ridge system waxes and wanes over tens of
    # Myr, while the model's spreading can stop or restart within a few
    # steps of a suture or a rift. It is measured against a slow (300 Myr)
    # average of itself, which starts from the initial sea floor (sea
    # level 0), so only real changes in spreading move the sea, and it
    # levels off smoothly toward +-SEA_TECT_MAX (Phanerozoic sea level has
    # spanned about -100..+250 m).
    ocean = ~sim.w_cont
    depth = float(ocean_depth(sim.w_age[ocean]).mean()) if ocean.any() else 0.0
    if sim.depth_ref is None:  # the starting sea floor defines sea level 0
        sim.depth_ref = sim.depth_ridge = depth
    sim.depth_ridge += (1 - np.exp(-dt / p.ridge_time)) * (depth - sim.depth_ridge)
    sim.depth_ref += (1 - np.exp(-dt / min(300.0, 10.0 + sim.t))) * (sim.depth_ridge - sim.depth_ref)
    sim.sea_tect = SEA_TECT_MAX * float(np.tanh(0.5 * (sim.depth_ridge - sim.depth_ref) / SEA_TECT_MAX))
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
    sim.ice = ice_sheets(sim, land, c["ground"])
    ice = np.where(land, sim.ice, 0.0)
    sim.t_warm, sim.t_cold, sim.temp = climate.ice_surface(*c["ground"], ice, climate.ice_cover(g, ice, land))
    # The water locked up in it lowers the sea everywhere (ice ~0.9 g/cm3).
    vol = (sim.ice / 1000.0).sum() * sim.cell_area * R_KM**2
    ocean_area = (~land).sum() * sim.cell_area * R_KM**2
    sim.sea_ice = -0.9 * vol / max(ocean_area, 1.0) * 1000.0
    sim.sea_level = sim.sea_ice + sim.sea_tect
    sim.koppen = climate.koppen(e, sim.temp, sim.t_warm, sim.t_cold, sim.precip, sim.p_jul,
                                sim.p_jan, g.lat, sim.ice)
    sim.climate_t = sim.t


# Ice sheets (see ice_sheets)
ICE_FEEDBACK = 0.75  # share of a sheet's own height that counts in keeping it alive
ICE_TAU = 50e3  # Pa: yield stress of ice, sets the (Nye) profile of a sheet
ICE_EDGE_KM = 10.0  # km: a sheet's thinnest margin counts as this far in from its edge
ICE_MAX = 4000.0  # m
ICE_SNOW_MIN = 25.0  # mm/yr of snow a sheet needs where it never melts ...
ICE_DDF = 3.0  # ... plus what melts: mm per positive degree-day (snow), days of sd 5 C around the month


def ice_sheets(sim, land, ground):
    """Land ice (m) for the climate just computed. ground: (t_warm, t_cold,
    temp) of the bare ground (climate.compute's, as if there were no ice).
    The real ice comes and goes with ~100 kyr cycles and answers its
    climate within ~10 kyr, far inside a climate step: this is the average
    extent over the cycles, in balance with today's mountains, so an ice
    cap follows its range as it moves or wears down.
      extent     where summers on the ice stay near freezing (warmest month
                 below ice_summer_temp) and enough snow falls to outlast
                 them: ICE_SNOW_MIN plus the year's melt from positive
                 degree-days (~25 mm/yr on a polar plateau, ~100 on a
                 polar sheet's margin; a dry tropical plateau a few C below
                 freezing all year, like the Puna de Atacama, stays bare
                 with ~110 mm/yr). Ice that is already there keeps itself
                 partly: its white top (climate.ice_cooling: ~10 C on a big
                 polar sheet, little on a small or tropical cap) and
                 ICE_FEEDBACK of its height (a 2 km sheet: ~10 C). Cold
                 polar desert with too little snow of its own is covered
                 by ice flowing in from a snowier part of the same cold
                 region (East Antarctica's plateau gets ~50 mm/yr).
      thickness  a sheet's steady (Nye) profile: sqrt(2 tau/(rho g) x the
                 distance in from its edge), ~330 m at the edge, ~1.9 km
                 300 km in, ~3.3 km 1000 km in. Weakly (x accumulation^1/8,
                 Vialov) thinner for dry sheets, and thinner for warm
                 (temperate, softer) ice: a small tropical cap is a few
                 hundred m (Quelccaya ~200 m)."""
    p, g = sim.params, sim.grid
    t_warm, t_cold, temp = ground
    old = np.where(land, sim.ice, 0.0)
    own = ICE_FEEDBACK * climate.LAPSE * old + climate.ice_cooling(old, climate.ice_cover(g, old, land))
    # the summer the ice would feel (melting holds a summer above 0 C on ice down, as climate.ice_surface)
    t_sum = t_warm - own
    t_sum = np.where(old > 0, np.minimum(t_sum, 0.5 * np.maximum(t_sum, 0)), t_sum)
    cold = land & (t_sum < p.ice_summer_temp)
    need = ICE_SNOW_MIN + ICE_DDF * degree_days(t_sum, t_cold - own)
    seed = np.flatnonzero(cold & (sim.precip > need))
    hops, _ = kernels.bfs_within(seed, cold.astype(np.int64), g.nbr_off, g.nbr_idx, 10**6)
    iced = cold & (hops >= 0)
    if not iced.any():
        return np.zeros(g.n)
    edge = np.flatnonzero(iced & (np.add.reduceat(~iced[g.nbr_idx], g.nbr_off[:-1]) > 0))
    hops, _ = kernels.bfs_within(edge, iced.astype(np.int64), g.nbr_off, g.nbr_idx, 10**6)
    d_m = (np.maximum(hops, 0) * g.spacing * R_KM + ICE_EDGE_KM) * 1000.0
    h = np.sqrt(2 * ICE_TAU / (917.0 * 9.81) * d_m)
    # per sheet: its mean snowfall and how cold its ice is
    lab, nk = kernels.components(iced, g.nbr_off, g.nbr_idx)
    k = np.maximum(lab, 0)
    cnt = np.bincount(k, weights=iced, minlength=nk)

    def mean(f):
        return (np.bincount(k, weights=f * iced, minlength=nk) / np.maximum(cnt, 1))[k]

    snow = np.clip((mean(sim.precip) / 300.0) ** 0.125, 0.75, 1.15)
    soft = 1.0 - 0.3 * np.clip((mean(temp - own) + 20.0) / 20.0, 0, 1)  # -20 C or colder: 1; 0 C: 0.7
    return np.where(iced, np.minimum(h * snow * soft, ICE_MAX), 0.0)


def degree_days(t_warm, t_cold, sd=5.0):
    """Positive degree-days in a year whose months run sinusoidally from
    t_cold to t_warm, the days scattered around each month's mean with
    standard deviation sd (C) (Reeh 1991, as the time zoom)."""
    mid, half = 0.5 * (t_warm + t_cold), 0.5 * (t_warm - t_cold)
    total = np.zeros_like(mid)
    for m in range(12):
        t = mid + half * np.cos(2 * np.pi * m / 12)
        x = t / sd
        cdf = 0.5 * (1 + _erf(x / np.sqrt(2)))
        total += (365.25 / 12) * (sd / np.sqrt(2 * np.pi) * np.exp(-0.5 * x * x) + t * cdf)
    return total


def _erf(x):
    """Abramowitz-Stegun 7.1.26 (|error| < 1.5e-7)."""
    s = np.sign(x)
    x = np.abs(x)
    t = 1 / (1 + 0.3275911 * x)
    y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496735) * t + 0.254829592) * t * np.exp(-x * x)
    return s * y


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
    # m of elevation per km: of what erosion takes off the top (the
    # sediment cover if there is one, else the basement), and of the
    # (light) sediment deposited
    sed = sediment_km(cover, x)
    iso_dep = sediment_iso(cont, rock, sed)
    iso = np.where(cover > surface.COVER_SHOWS, iso_dep, isostasy(cont, rock))
    col.t, col.cover, x[:, MIX], sim.removed, dep, sim.flow, sim.down, lk = surface.erode(
        g, elevation(t, sim.w_age, cont, rock, sim.swell - sim.sea_level, sed), t, cover, x[:, MIX],
        rock, cont, sim.precip, sim.runoff, sim.aet, sim.lake_evap, dt, p.hillslope, p.erosion_timescale,
        p.erosion_height, p.incision, sim.scale, iso, k_mult, p.alluvial, p.fan_km, iso_dep)
    sim.book("erosion", t0, col.t, cont)
    # the basement comes up by what's worn off net (the strata: in sediments())
    col.eroded_cover = np.clip(sim.removed, 0, np.maximum(cover, 0))
    col.rec[:, record.EXHUMED] = np.maximum(col.rec[:, record.EXHUMED] + sim.removed - dep, 0)
    sim.lake_kind, sim.lake_depth = lk["kind"], lk["depth"]
    return dep, lk["kind"]


def sediments(sim, col, dep, lake):
    """Which kind of sediment forms where. In place on col.x, and on the
    strata: a cell that lost more cover to erosion than it got loses its
    top, one that got more gains a layer (what rivers lay down on land is
    sandstone, what settles in the sea mud, shale; a deposit passing over
    eroding ground isn't kept). Returns the chemical deposits (km of evaporite and of
    coal per cell), which are added later with the reefs.
      sand       near its source (lakes, rivers, beaches, deltas); farther
                 out only mud settles. Desert winds sort loose cover into dunes.
      evaporite  where water evaporates faster than it arrives: closed
                 lakes and salt pans in warm basins (Dead Sea, Great Salt Lake) and
                 shallow hot seas next to desert (the Persian Gulf)
      coal       warm, wet, low-lying swamps full of plants, if plants
                 exist (none before land plants ~450 Ma on Earth)"""
    p, g, dt = sim.params, sim.grid, sim.dt
    x, cover = col.x, col.cover
    e = elevation(col.t, sim.w_age, col.cont, col.rock, sim.swell - sim.sea_level, sediment_km(col.cover, x))
    land = e > 0
    x[:, SAND] += dep * np.where(land, 0.6, np.where(e > -200, 0.5, 0.15))
    net = dep - col.eroded_cover
    record.remove_top(col.rec, col.lith, np.maximum(-net, 0))
    record.add_top(col.rec, col.lith, np.maximum(net, 0), np.where(land, SANDSTONE, SHALE).astype(np.uint8), sim.t)
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
    return evap, coal


def bury(sim, col):
    """Deep in a thick pile the sediment is cooked into metamorphic rock:
    it stays crust, but it's basement now, not cover (the bottom of the
    strata)."""
    cooked = np.maximum(col.cover - sim.params.metamorphic_depth, 0)
    record.remove_bottom(col.rec, col.lith, cooked)
    col.x[:, MIX] *= (1 - cooked / np.maximum(col.cover, 1e-9))[:, None]
    col.cover = col.cover - cooked


def reefs(sim, col, dep, chem):
    """Reefs: in warm, clear, shallow sea, corals and other carbonate
    makers build up to just below sea level, fast enough to outpace any
    subsidence. A volcanic island that sinks with its ageing sea floor
    becomes an atoll; carried out of the tropics, the reef dies and it
    drowns into a flat-topped seamount (the Darwin point, ~30 deg).
    Muddy water from big rivers stops them (no reefs off the Amazon).
    The chemical sediments (chem: km of evaporite and of coal) join the
    crust here too. All go on top of the strata."""
    p, dt = sim.params, sim.dt
    evap, coal = chem
    chem = evap + coal
    cont, rock = col.cont, col.rock
    sed = sediment_km(col.cover, col.x)
    e = elevation(col.t, sim.w_age, cont, rock, sim.swell - sim.sea_level, sed)
    reef = (e < -5) & (e > -1500) & (sim.temp >= p.reef_temp) & (dep * 1000 < p.reef_mud * dt)
    grow = np.minimum(p.reef_rate * np.exp((e + 5) / 150.0) * dt, -5 - e) * reef  # m of elevation
    carb = grow / sediment_iso(cont, rock, sed)
    col.t, col.cover = col.t + carb, col.cover + carb
    col.x[:, CARB] += carb
    col.t, col.cover = col.t + chem, col.cover + chem
    sim.book("reef+chem", 0, carb + chem, cont)
    n = sim.grid.n
    record.add_top(col.rec, col.lith, evap, np.full(n, EVAPORITE, np.uint8), sim.t)
    record.add_top(col.rec, col.lith, coal, np.full(n, COAL_ROCK, np.uint8), sim.t)
    record.add_top(col.rec, col.lith, carb, np.full(n, LIMESTONE, np.uint8), sim.t)
