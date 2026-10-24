"""The earth system around the plates: mantle heat, global temperature and
CO2, sea level, the climate model, and the surface processes that run on
its rain (erosion, rivers, sediment).

State it keeps on the simulation (see Simulation.EARTH_STATE): dT, drift,
co2, rates, refs, depth_ridge, depth_ref, sea_level and its parts sea_ice / sea_tect, ice,
the vegetation (veg, veg_frac, veg_lai, npp, veg_type, tree_cover, flora,
veg_niche), removed, the climate fields from climate.compute, the rivers
(flow, down) and the lakes (lake_kind, lake_depth).
"""

from __future__ import annotations

import numpy as np

from .. import climate, hydrology, icemass, kernels, surface, vegetation
from ..geo import R_KM
from ..surface import COAL as COAL_ROCK, EVAPORITE, LIMESTONE, SANDSTONE, SHALE
from . import record
from .isostasy import (CARB, COAL, EVAP, MIX, RHO_MANTLE, RHO_WATER, SAND, VALLEY, elevation, ice_load, iso_rate, land_view,
                       ocean_depth, sediment_iso, sediment_km)

SEA_TECT_MAX = 400.0  # m: the ocean basins' part of sea level levels off toward +-this (PW-293: was 250, which
# shaped the signal; at 400 a Cretaceous-like +250 m passes at +222)
EARTH_ICE = 0.031  # Earth's land ice today, share of the surface (Antarctica and Greenland)
WEATHER_K = 0.09  # per C: silicate weathering's temperature sensitivity (GEOCARB III's activation energy; its
# runoff part, ~0.03, is already in the erosion rate the sink multiplies, PW-278; 0.06 before PW-235, 0.12 after)
WEATHER_CO2 = 0.4  # silicate weathering ~ pCO2^this (GEOCARB's f(CO2) for vascular plants ~0.4, without 0.5)
CO2_MAX = 6.0  # e-folds of CO2 the log forcing levels off toward (+-; smoothly, tanh: ~400x / 0.0025x the
# reference; snowball exits needed ~40-400x, 3.6-6 e-folds, Caldeira & Kasting 1992, Hoffman et al. 2017; was a hard
# clip at 3, PW-558)
CO2_TAU = 0.4  # Myr: the CO2 stock's residence time at the reference, ocean-atmosphere carbon over outgassing
# (~40,000 GtC over ~0.1 GtC/yr; the weathering feedback's e-folding, CO2_TAU / WEATHER_CO2 ~1 Myr, is Earth's
# few hundred kyr to ~1 Myr: Archer et al. 2009, Colbourn et al. 2015)
REF_MYR = 100.0  # Myr: during the spin-up, the source's and sink's references follow the planet's rates over this
REF_FREEZE = 300.0  # Myr: then they are kept (PW-558/559 B): the planet's own balance once the made-up start has
# settled, the same spin-up the criteria skip
# (a reference that kept following one part of the sink, the ice-free land's erosion, was tried and dropped on the
# mature start: with no relief build-up left to forget, it forgot real changes in erosion; PW-576 stage 3)


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


def weathering(sim, land):
    """The silicate weathering sink per cell (model units: km of rock per step, times the factors) and
    its parts, for global_temperature and the diagnostics: (sink, supply, temperature factor, plant
    factor). The supply is what bare ground lost to erosion (sim.weathered: not under land ice, where
    glaciers grind their beds fast but the rock flour hardly weathers chemically in the cold, and
    counting it made a cold era draw down more CO2 the more ice it grew)."""
    supply = sim.weathered * land
    # chemical weathering: faster when warm (and so wetter); the weathering thermostat (Walker et al.
    # 1981): a cold planet weathers slower, CO2 builds up and warms it back (PW-235)
    warm = np.exp(WEATHER_K * (sim.temp - 15.0)) if sim.temp is not None else np.ones_like(supply)
    # roots and soil CO2 speed it up, in proportion to how much grows there
    # (GEOCARB's biological weathering factor)
    plants = 1 + 0.5 * np.clip(sim.npp / 800.0, 0, 1.5)
    return supply * (warm * plants), supply, warm, plants


def co2_stock(co2, s, w, dt, steps=4):
    """The CO2 stock over a step (PW-558). co2 is ln X, X the stock (pCO2, climate.pco2) relative to the reference; s the
    volcanic source and w the weathering sink, each against its reference. Weathering also grows with CO2
    itself (~pCO2^WEATHER_CO2: carbonic acid in soils, GEOCARB's f(CO2)), so
        dX/dt = (s - w X^WEATHER_CO2) / CO2_TAU.
    Its steady state is X^WEATHER_CO2 = s / w (the old ratio rule: a weathering deficit raises CO2 1 /
    WEATHER_CO2 times further than the bare ratio). CO2_TAU is far below a step, so X is about there each
    step, except where the sink is nearly gone (ice over the weathering land): then X grows at s / CO2_TAU, as
    outgassing piled CO2 up under the Cryogenian ice. Backward Euler substeps (stable at any step); each
    solves X + c1 X^a = c0 by Newton's method in ln X from above (the function is convex and increasing)."""
    a, h = WEATHER_CO2, dt / steps
    x = float(np.exp(co2))
    for _ in range(steps):
        c1, c0 = h * w / CO2_TAU, x + h * s / CO2_TAU
        u = np.log(c0)
        for _ in range(40):
            eu, eau = np.exp(u), c1 * np.exp(a * u)
            du = (eu + eau - c0) / (eu + a * eau)
            u -= du
            if abs(du) < 1e-10:
                break
        x = float(np.exp(u))
    return float(np.log(x))


def co2_term(p, co2):
    """The CO2 stock's warming, C: co2_sensitivity per doubling of pCO2 (climate.pco2; an e-fold is 1 / ln 2
    doublings) above the climate model's dT = 0 (climate.PCO2_REF: the planet's balance, PCO2_BALANCE, is a
    doubling warmer), levelling off smoothly toward +-CO2_MAX e-folds (CO2's forcing is ~logarithmic up to ~0.1 bar
    and grows less beyond)."""
    c = co2 + np.log(climate.PCO2_BALANCE / climate.PCO2_REF)  # e-folds above the climate's dT = 0 (PW-559 B)
    return p.co2_sensitivity / np.log(2.0) * CO2_MAX * float(np.tanh(c / CO2_MAX))


def global_temperature(sim, growth, newc, rng):
    """The planet's mean temperature, as an offset dT from today's Earth.
    Three things move it, slowly (tens of Myr):
      drift      a random walk that keeps returning toward 0 (all the
                 carbon-cycle and ocean details this model doesn't have)
      CO2        a stock (co2_stock): volcanism at ridges and arcs adds
                 it (warming); fresh rock weathering in warm, wet mountains
                 removes it (cooling, e.g. the Himalaya since 40 Ma). Each
                 is measured against the planet's own balance once its
                 start has settled (REF_FREEZE), so lasting changes keep
                 counting. A cold or icy planet weathers slower (the
                 weathering thermostat), so CO2 piles up and warms it back
      ice        ice sheets reflect sunlight (cooling feedback)
    Real Earth: a few long icehouse eras (Cryogenian, late Ordovician,
    Permo-Carboniferous, today) between long greenhouse ones.
    growth: arc crust growth this step (km/Myr per cell); newc: number of
    new ocean-floor cells this step."""
    p, dt = sim.params, sim.dt
    a = np.exp(-dt / p.climate_drift_time)
    sim.drift = sim.drift * a + p.climate_drift * np.sqrt(1 - a * a) * rng.normal()
    land = sim.land()
    source = newc / sim.scale**2 + 20.0 * growth.sum() / sim.scale**2
    sink = float(weathering(sim, land)[0].sum()) / sim.scale**2
    if sink > 0.0:  # (the first step: nothing has eroded yet; the references start from the first real rates)
        now = np.array([max(source, 1e-6), sink])
        sim.rates = now
        if sim.refs is None:
            sim.refs = now.copy()
        # The references: the planet's own balance of outgassing against weathering, followed while the made-up
        # start settles and then kept for the rest of the run (PW-558, PW-559 B). Kept, they let a long cold era's
        # weathering deficit go on piling up CO2 (and a long surplus go on drawing it down), as a real carbon
        # stock does, where baselines that relearned took both up within a few hundred Myr (PW-576).
        if sim.t < REF_FREEZE:
            b = 1 - np.exp(-dt / min(REF_MYR, 10.0 + sim.t))
            sim.refs = sim.refs + b * (now - sim.refs)
        sim.co2 = co2_stock(sim.co2, now[0] / sim.refs[0], now[1] / sim.refs[1], dt)
    # Sea level also follows the ocean basins: young sea floor is hot and
    # shallow, so when ridges are long and fast the water has less room
    # and floods the continents (the Cretaceous, ~200 m higher than now).
    # The basins' volume (depth_ridge) follows the mean depth of the floor
    # over ridge_time Myr: a real ridge system waxes and wanes over tens of
    # Myr, while the model's spreading can stop or restart within a few
    # steps of a suture or a rift. It is measured against a fixed reference,
    # the starting sea floor's mean depth (setup makes it the model's own
    # long-run ocean, mean age 54 Myr at the start, PW-293, PW-549: sea level 0 is the
    # model's mean, and excursions are breakups and assemblies), so a
    # lasting change in the basins (an ocean that stays young or old) keeps the sea up or down
    # (PW-288: a baseline that relearned the floor over 300 Myr hid a
    # persistently young ocean). The water displaced also loads the floor,
    # which sinks by rho_w / (rho_m - rho_w) of the water's rise, so the sea
    # rises by (rho_m - rho_w) / rho_m ~ 0.69 of the floor's shallowing.
    # It levels off smoothly toward +-SEA_TECT_MAX, well beyond the
    # Phanerozoic's span (about -100..+250 m), so the limiter only stops
    # runaways and doesn't shape ordinary highstands (PW-293).
    ocean = ~sim.w_cont
    depth = float(ocean_depth(sim.w_age[ocean]).mean()) if ocean.any() else 0.0
    if sim.depth_ref is None:  # the starting sea floor defines sea level 0
        sim.depth_ref = sim.depth_ridge = depth
    sim.depth_ridge += (1 - np.exp(-dt / p.ridge_time)) * (depth - sim.depth_ridge)
    rise = (RHO_MANTLE - RHO_WATER) / RHO_MANTLE * (sim.depth_ridge - sim.depth_ref)
    sim.sea_tect = SEA_TECT_MAX * float(np.tanh(rise / SEA_TECT_MAX))
    # A hotter mantle melts more at ridges: thicker, more buoyant ocean
    # crust and shallower ocean basins, so the same water stands higher
    # on the continents (one reason the young Earth was mostly sea).
    sim.sea_tect += p.hot_sea * (sim.heat() - 1.0)
    sim.sea_level = sim.sea_ice + sim.sea_tect
    ice_frac = (sim.ice > 0).mean()
    # (the ice's whiteness levels off: a sheet spreading over more land shades its own cold surroundings,
    # cloudier and dimmer at high latitude, and the snow it would brighten is often white already)
    def albedo(f):
        return p.ice_albedo_max * np.tanh(p.ice_albedo * f / 0.03 / max(p.ice_albedo_max, 1e-9))

    # (measured from Earth's today, ~3% of the surface: the climate model's dT = 0 is Earth's climate with
    # its ice; before PW-190 any ice cooled from an ice-free planet's, ~1.4 C too cold with Earth's ice)
    target = sim.drift + co2_term(p, sim.co2) - (albedo(ice_frac) - albedo(EARTH_ICE))
    if getattr(sim, "diag", None) is not None:  # (opt-in diagnostics, read only: tectonics/diag.py)
        sim.diag.temperature(sim, source, sink, ice_frac, co2_term(p, sim.co2),
                             -(albedo(ice_frac) - albedo(EARTH_ICE)), target + p.climate_offset)
    sim.dT += (1 - np.exp(-dt / 5.0)) * (target + p.climate_offset - sim.dT)


def climate_due(sim) -> bool:
    """The climate is updated on the first step and then at every multiple of
    climate_every Myr, so keyframes on those multiples show current climate."""
    k = sim.params.climate_every
    return sim.precip is None or (sim.t + 1e-9) // k > (sim.climate_t + 1e-9) // k


def update_climate(sim, e):
    """Temperature, seasons, rain, ice and Koppen class on elevation e
    (m above the current sea level, without ice, and without the ice's
    load: the crust's own height). The bed under the ice is pressed down by
    it (glacial isostasy, sim.ice_sink, settled at once in a run's Myr
    steps): the ice's surface stands lower (warmer), and land the load
    pushes below the sea without ice on it is sea. Grounded ice on a bed
    below sea level stays land (isostasy.land_view)."""
    p, g = sim.params, sim.grid
    bed = e - sim.ice_sink
    e, ice0, _ = land_view(bed, np.where(e > 0, sim.ice, 0.0))
    land = e > 0
    c = climate.compute(g, e, sim.dT, p.tilt, np.where(land, ice0, 0.0), veg=veg_feedback(sim),
                        rain_start=sim.rain_state)
    sim.rain_state = c["rain_state"]  # the next update's rain starts from it (PW-387)
    sim.temp, sim.t_warm, sim.t_cold = c["temp"], c["t_warm"], c["t_cold"]
    sim.precip, sim.p_jul, sim.p_jan = c["precip"], c["p_jul"], c["p_jan"]
    sim.runoff, sim.aet, sim.lake_evap = c["runoff"], c["aet"], c["lake_evap"]
    sim.wind_jul, sim.wind_jan, sim.current = c["wind_jul"], c["wind_jan"], c["current"]
    sim.wind = 0.5 * (sim.wind_jul + sim.wind_jan)
    marine, info = marine_view(bed, c), {}
    sim.ice = ice_sheets(sim, land, e, c["ground"], ice0, sim.ice_sink, info, marine=marine)
    ice = np.where(land, sim.ice, 0.0)
    sim.t_warm, sim.t_cold, sim.temp = climate.ice_surface(*c["ground"], ice, icemass.sheet_cover(g, ice), g.lat,
                                                           sim.p_jul, sim.p_jan)
    # The water locked up in it lowers the sea everywhere (ice ~0.9 g/cm3).
    vol = (sim.ice / 1000.0).sum() * sim.cell_area * R_KM**2
    ocean_area = (~land).sum() * sim.cell_area * R_KM**2
    sim.sea_ice = -0.9 * vol / max(ocean_area, 1.0) * 1000.0
    sim.sea_level = sim.sea_ice + sim.sea_tect
    if getattr(sim, "diag", None) is not None:  # (opt-in diagnostics, read only: tectonics/diag.py)
        sim.diag.climate_update(sim, land, e, c, marine, info)
    sim.koppen = climate.koppen(e, sim.temp, sim.t_warm, sim.t_cold, sim.precip, sim.p_jul,
                                sim.p_jan, g.lat, sim.ice)
    sim.cloud_jul, sim.cloud_jan = c["cloud_jul"], c["cloud_jan"]
    update_vegetation(sim, e)
    sim.ice_sink = ice_load(g, sim.ice)
    sim.climate_t = sim.t


def veg_feedback(sim):
    """The vegetation's feedbacks on the climate (climate.compute's veg),
    from the last update's vegetation (one climate step behind): bare land
    before land plants, an Earth-like average on the first update."""
    if sim.t < sim.params.plants_from - 1e-9:
        return vegetation.bare(sim.grid.n)
    if sim.veg_frac is None:
        return None
    return vegetation.feedback(sim.veg_frac, sim.veg_lai)


FLORA_END = 1000.0  # Myr: the plant groups' timeline when the run's end isn't known (params.flora_end = 0)


def update_vegetation(sim, e):
    """The vegetation in equilibrium with the climate just computed
    (vegetation.model, the cheap variant: warm-started from the last
    update), and the plant groups that appear (vegetation.flora_update,
    on the niches measured at the last update). Sets veg (ground cover,
    which slows erosion), npp (which speeds weathering), veg_frac,
    veg_lai, veg_type, tree_cover, flora and veg_niche."""
    p, g = sim.params, sim.grid
    n = g.n
    if sim.t < p.plants_from - 1e-9:
        sim.veg, sim.npp, sim.tree_cover = np.zeros(n), np.zeros(n), np.zeros(n)
        sim.veg_type = np.where(e > 0, vegetation.T["barren desert (sand or stone)"], 0).astype(np.uint8)
        return
    end = p.flora_end if p.flora_end > 0 else FLORA_END
    rng = np.random.default_rng([sim.seed, sim.step_no, 11])
    sim.flora = vegetation.flora_update(sim.flora, sim.t, p.climate_every, p.plants_from, end, sim.veg_niche, rng)
    land = e > 0
    ice = np.where(land, sim.ice, 0.0)
    kind = np.where(land, sim.lake_kind, 0)
    lake = np.isin(kind, (hydrology.OPEN_LAKE, hydrology.CLOSED_LAKE))
    v = vegetation.model(g, e, sim.temp, sim.t_warm, sim.t_cold, sim.p_jul, sim.p_jan, p.tilt, sim.cloud_jul,
                         sim.cloud_jan, sim.flow, kind, lake, ice, nu0=sim.veg_frac, lai0=sim.veg_lai,
                         pco2=climate.pco2(sim.co2), unlocked=vegetation.unlocked_at(sim.flora, sim.t), cheap=True,
                         locked_potential=True, crown=False)  # (crown fire, PW-347: not yet in runs)
    sim.veg_niche = vegetation.niches(v)
    sim.veg_frac = v["eq"]["nu"].astype(np.float32)
    sim.veg_lai = v["pot"]["lai"].astype(np.float32)
    sim.veg = vegetation.ground_cover(v)
    sim.npp = v["sm"]["npp"]
    sim.tree_cover = v["sm"]["tree"]
    sim.veg_type = v["types"].astype(np.uint8)


# Ice sheets (see ice_sheets)
ICE_TAU = icemass.SHEET_TAU  # Pa: yield stress of ice, sets the (Nye) profile of a sheet
ICE_EDGE_M = icemass.EDGE_H  # m: ~400, a sheet's thinnest margin (its profile 10 km in from its edge)
ICE_MAX = 4000.0  # m
ICE_RINGS = 40  # at most this many rings of ablation zone around a sheet
PASS_TOL = 0.002  # ... once the iced cells repeat but for this share of them (a few margin cells flickering)
ICE_PASSES = 200  # a sheet settles in at most this many passes (a sheet's retreat or advance is ~1 cell a pass)


def marine_view(bed, c):
    """The sea's side of the ice sheets (PW-465), for the time zoom's calving
    and shelf rules (icemass.coast_loss): the water's depth (m; under the
    marine beds land_view floors too), the air's annual mean (C) and the
    melt under an ice shelf (m/yr: MELT_K x the winter sea's warmth above
    freezing, as the time zoom's). bed: the true bed (m above sea level,
    pressed down by the ice); c: climate.compute's result."""
    sst_w = np.minimum(c["sst_jul"], c["sst_jan"])
    return {"depth": np.maximum(-np.asarray(bed, float), 0.0), "t_air": c["temp"],
            "melt": icemass.MELT_K * np.maximum(sst_w - climate.FREEZE, 0.0)}


def ice_sheets(sim, land, bed, ground, old, sink=None, info=None, *, marine):
    """Land ice (m) for the climate just computed. ground: (t_warm, t_cold,
    temp) of the bare ground (climate.compute's, as if there were no ice,
    on the bed as the old ice pressed it down: a sheet sits lower and
    warmer than it would on unloaded crust, PW-189); old: the ice that
    climate saw (m, on that bed); sink: m the bed is pressed down by
    (default: old's settled load, isostasy.ice_load); info: a dict that
    gets "passes", how many passes it took (2: the ice moved at most a ring
    from old).
    The real ice comes and goes with ~100 kyr cycles and answers its
    climate within ~10-100 kyr, far inside a climate step: this is the
    extent the flowing sheets settle to under the surface mass balance
    averaged over the cycle's orbits (icemass.balance, the time zoom's own,
    PW-190; a warm summer melts more than a cold one saves), in balance
    with today's mountains, so an ice cap follows its range as it moves or
    wears down. One pass (_ice_pass) moves a sheet's margin about a cell:
    the balance of the old ice's height decides where it accumulates, and
    the new margins' lower Nye surface is the next pass's height. So the
    passes repeat, under this climate, until the iced cells repeat (a
    fixed point, or a margin cell or two flickering between two passes).
    Each pass stands on the bed as its ice presses it down (glacial
    isostasy settles in ~10 kyr too), its bare ground warmer or colder by
    the lapse rate. (Before PW-364 a run made one pass per climate update:
    a sheet took ~20 updates, ~80 Myr, to shrink back after its cold era,
    and as long to grow into one.) The rest of the climate (the sheet's
    carried air, its albedo, the rain) follows at the next update, as CO2
    does (computing it again within the step whenever margins moved cost
    ~+80% of the climate at L5, mostly for a few margin cells shuffling).
    The old
    ice's height still counts: a big sheet keeps itself colder than bare
    ground would be and can outlast the climate that made it (two states,
    hysteresis), but not by tens of Myr of lag."""
    g = sim.grid
    sink = ice_load(g, np.where(land, old, 0.0)) if sink is None else sink

    def settled(ice):  # the bed and its bare ground under this ice's load
        rise = sink - ice_load(g, ice)
        return bed + rise, tuple(t - climate.LAPSE * rise for t in ground)

    info = {} if info is None else info
    # (once per fixed point, on the bed the old ice pressed down, not every pass (PW-514: +39% wall
    # otherwise): what the sea takes from each coastal cell, and where a new cap can start (snow
    # outlasting the summer on bare ground); the passes' settling moves the bed by tens of m at most)
    kw = {"cost": coast_cost(sim, land, bed, marine), "start": _start(sim, land, ground)}
    ice = _ice_pass(sim, land, bed, ground, old, marine, **kw)
    seen = [np.asarray(old) > 0, ice > 0]
    info["passes"] = 1
    for _ in range(ICE_PASSES):
        new = _ice_pass(sim, land, *settled(ice), ice, marine, **kw)
        info["passes"] += 1
        on = new > 0
        # (settled: as one of the last two passes but for a few margin cells shuffling; PW-514: with
        # coast_loss, exact repeats took ~21 passes per update against ~3.5 before)
        tol = max(2, int(PASS_TOL * on.sum()))
        if (on != seen[-1]).sum() <= tol or (on != seen[-2]).sum() <= tol:
            return new
        seen = [seen[-1], on]
        ice = new
    return ice


def _start(sim, land, ground):
    """Where a new cap can start: snow outlasting the summer on bare ground,
    on average over the ice-age cycle's orbits (icemass.balance at no ice)."""
    smb0, _ = icemass.balance(sim.grid.lat, land, ground[0], ground[1], sim.p_jul, sim.p_jan, 0.0, 0.0,
                              tilt=sim.params.tilt)
    return smb0 > 0


def _ice_pass(sim, land, bed, ground, old, marine, cost=None, start=None):
    """One pass of ice_sheets: the ice under its climate given the old
    ice's extent and height.
      accumulation  where snow outlasts the summer: on bare ground (a new
                 cap starts where the year's snow lasts, so the snowline
                 depends on the snowfall as well as the summer, PW-159), and
                 on ice (the old ice's own thickness, or a margin's ~400 m:
                 the old ice next to bare land and a new margin are the
                 sheet's edge, as the time zoom's margins; its height and,
                 on a big sheet, its own bright air mass,
                 which the climate carries along the winds onto its margins
                 (ground: the old ice's air, PW-336), keep it colder)
                 connected to such a start or to old ice;
      ablation zone  each sheet then spreads ring by ring onto the land
                 around it, the least-melting cells first, as long as its
                 snow surplus pays for their melt (and for what the sea
                 takes where it reaches the sea, the time zoom's flow onto
                 shelves and calving, which the accumulation zone pays too,
                 PW-465): a big snowy sheet has a wide ablation
                 zone, a small or dry one hardly any. Cold polar desert
                 with too little snow of its own costs nothing to cover
                 (East Antarctica's plateau gets ~50 mm/yr);
      thickness  a sheet's steady (Nye) surface: sqrt(2 tau/(rho g) x the
                 distance in from its edge) above the bed at that edge
                 (PW-276; tau 75 kPa, PW-366), each cell its mean over the
                 cell (~800 m on a margin cell at L6), ~2 km 300 km in,
                 ~3.7 km 1000 km in; the ice is that surface less the cell's own bed
                 (bed: m above sea level, as the old ice pressed it down),
                 at least a margin's: thinner over high ground inside the
                 sheet (the ice drains off it; a sheet's surface stops near
                 4 km, not at its range's height plus its profile), thicker
                 over a basin. Weakly (x accumulation^1/8, Vialov) lower for
                 dry sheets, and for warm (temperate, softer) ice: a small
                 tropical cap is a few hundred m (Quelccaya ~200 m)."""
    g = sim.grid
    t_warm, t_cold, temp = ground
    old = np.where(land, old, 0.0)
    lat = g.lat
    # snow that outlasts the summer on bare ground, and on ice (the old ice, or a new margin's), on
    # average over the ice-age cycle's orbits (bright ice feels less of them, mixed over the air around)
    tilt = sim.params.tilt
    start = _start(sim, land, ground) if start is None else start
    # (a margin cell, old ice next to bare land, is a slope from the bare edge up to its inner neighbour: its
    # snow and melt are its edge's, as the time zoom's margins (PW-366); at the cell-mean rise, ~800 m at L6,
    # its own thickness would keep it as cold as the interior and the sheet would creep a ring a pass)
    bare_nb = np.add.reduceat((land & (old <= 0))[g.nbr_idx], g.nbr_off[:-1]) > 0
    h = np.where(old > 0, np.where(bare_nb, np.minimum(old, ICE_EDGE_M), old), ICE_EDGE_M)
    cover = icemass.sheet_cover(g, old)
    # (as the time zoom's orbit_k, PW-114/PW-365: the air over bright ice brings the response of the land,
    # sea and ice around, each its own share of the land's: the sea INSOL_SEA, bright ice ICE_ABSORB; before,
    # the open sea counted as fully absorbing land, and coastal ice felt ~2x the time zoom's orbital swing)
    bright = np.where(land, np.clip(old / icemass.SNOW_H, 0, 1), 0.0)
    own = np.where(land, 1.0, icemass.INSOL_SEA)
    mix = climate.smooth_big(g, own * (1 - bright * (1 - icemass.ICE_ABSORB)), icemass.ABSORB_KM)
    absorb = (1 - bright) + bright * mix
    smb, _ = icemass.balance(lat, land, t_warm, t_cold, sim.p_jul, sim.p_jan, h, cover, tilt=tilt, absorb=absorb)
    acc_ok = land & (smb > 0)
    seed = np.flatnonzero(acc_ok & (start | (old > 0)))
    hops, _ = kernels.bfs_within(seed, acc_ok.astype(np.int64), g.nbr_off, g.nbr_idx, 10**6)
    iced = acc_ok & (hops >= 0)
    if not iced.any():
        return np.zeros(g.n)
    iced = ablation_zone(sim, land, iced, smb, cost=coast_cost(sim, land, bed, marine) if cost is None else cost)
    bed_edge, nye = sheet_surface(g, iced, bed)
    h = np.maximum(bed_edge + nye - bed, ICE_EDGE_M)
    # per sheet: its mean snowfall and how cold its ice is
    lab, nk = kernels.components(iced, g.nbr_off, g.nbr_idx)
    k = np.maximum(lab, 0)
    cnt = np.bincount(k, weights=iced, minlength=nk)

    def mean(f):
        return (np.bincount(k, weights=f * iced, minlength=nk) / np.maximum(cnt, 1))[k]

    snow = np.clip((mean(sim.precip) / 300.0) ** 0.125, 0.75, 1.15)
    h = np.where(iced, h, 0.0)
    _, _, t_ice = climate.ice_surface(t_warm, t_cold, temp, h, icemass.sheet_cover(g, h), lat, sim.p_jul, sim.p_jan)
    soft = 1.0 - 0.3 * np.clip((mean(t_ice) + 20.0) / 20.0, 0, 1)  # -20 C or colder: 1; 0 C: 0.7
    fac = snow * soft
    surf = np.maximum(bed + ICE_EDGE_M * fac, bed_edge + nye * fac)
    return np.where(iced, np.minimum(surf - bed, ICE_MAX), 0.0)


def sheet_surface(g, iced, bed):
    """(bed at the margin, Nye rise above it) per iced cell (PW-276): a
    sheet's steady surface rises from its margin by sqrt(2 tau/(rho g) x
    the distance in from it) (each cell: its mean over the cell, from d to
    d + 1 hops in, d its hops from the margin cells), and the ice drains toward whichever margin
    keeps it lowest, so the surface is the least over the sheet's margin
    cells (iced cells next to ground or sea without ice) of their bed plus
    the profile at the distance (hops through the sheet) from them. On a
    flat bed this is the nearest margin; a margin on a high ridge doesn't
    hold the ice of the basin behind it above the basin's other, lower
    margins. Bellman-Ford over the sheet's cells (each round carries the
    best margin one hop further in)."""
    n = g.n
    off, idx = g.nbr_off, g.nbr_idx
    k_m = 2 * ICE_TAU / (917.0 * 9.81) * g.spacing * R_KM * 1000.0  # m2 per hop

    def rise(d):
        # the profile's mean over the cell, which spans d..d+1 hops in from the edge (PW-366: its inner
        # edge's value left a margin cell ~340 m at L6, the profile's mean over it ~740 m at 50 kPa)
        d = np.asarray(d, float)
        dd = np.where(np.isfinite(d), d, 0.0)  # (cells no margin has reached yet: inf)
        return np.where(np.isfinite(d), (2.0 / 3.0) * np.sqrt(k_m) * ((dd + 1.0) ** 1.5 - dd ** 1.5), np.inf)

    edge = iced & (np.add.reduceat(~iced[idx], off[:-1]) > 0)
    src = np.repeat(np.arange(n), np.diff(off))
    ok = iced[src] & iced[idx]
    a, b = src[ok], idx[ok]
    be = np.where(edge, bed, np.inf)
    dd = np.where(edge, 0.0, np.inf)
    v = np.where(edge, bed + rise(0.0), np.inf)
    for _ in range(n):
        cand = be[a] + rise(dd[a] + 1)
        better = np.flatnonzero(cand < v[b] - 1e-6)
        if len(better) == 0:
            break
        o = better[np.lexsort((cand[better], b[better]))]
        first = np.r_[True, b[o][1:] != b[o][:-1]]
        pick = o[first]
        j, i = b[pick], a[pick]
        be[j], dd[j], v[j] = be[i], dd[i] + 1, cand[pick]
    be = np.where(iced, be, bed)
    return be, np.where(iced, rise(np.where(iced, dd, 0.0)), 0.0)


def coast_cost(sim, land, bed, marine):
    """m/yr per land cell: the ice it would lose to the sea beside it as a
    sheet's margin (icemass.coast_loss: the time zoom's flow across the coast,
    shelves and calving, PW-465), at a margin cell's Nye thickness (the
    profile's mean over the cell, as sheet_surface gives it on a flat bed).
    Its surface is on the true bed (a marine bed land_view floored stands
    `depth` below the sea: the time zoom sees the run's ice there). Also
    the cells whose margin ice would float or stands deeper than
    CALVE_DEPTH (the time zoom loses them at once)."""
    from ..timezoom.geometry import geometry
    g = sim.grid
    G = geometry(g)
    k_m = 2 * ICE_TAU / (917.0 * 9.81) * g.spacing * R_KM * 1000.0
    h = (2.0 / 3.0) * np.sqrt(k_m)
    depth = marine["depth"]
    true_bed = np.where(land & (depth > 0), -depth, bed)
    lost = land & (depth > 0) & ((depth * icemass.RHO_W > h * icemass.RHO_I) | (depth > icemass.CALVE_DEPTH))
    sea = ~land | lost
    src, dst = g.nbr_src, g.nbr_idx
    side = land[src] & ~lost[src] & sea[dst]
    i, j = src[side], dst[side]
    q = icemass.coast_loss(np.full(len(i), h), true_bed[i] + h, depth[j], G["dist"][side], G["elen"][side],
                           marine["t_air"][j], marine["melt"][j], G["area"][j])
    return np.bincount(i, weights=q, minlength=g.n) / G["area"], lost


def ablation_zone(sim, land, iced, smb, rings=ICE_RINGS, *, cost):
    """Spread each sheet (a connected accumulation zone) ring by ring onto
    the land around it, the cheapest cells first (melt: -smb under a
    margin's ice; plus what the sea takes where it is next to them,
    coast_cost), while its snow surplus (its smb > 0, less what the sea
    takes from it) pays for them. First (PW-465) the sea's own toll on the
    accumulation zones, as the time zoom charges it: margin cells that would
    float go, and a sheet whose snow can't pay for its coast gives up its
    dearest coastal cells (their loss less their own snow) until it can;
    before, a coastal accumulation zone paid nothing for its coast and the
    time zoom shed ~20-100 m of the run's ice in 50 kyr. iced: the
    accumulation zones (in place); cost: coast_cost's (m/yr, lost)."""
    g = sim.grid
    off, idx = g.nbr_off, g.nbr_idx
    src = np.repeat(np.arange(g.n), np.diff(off))
    calve, lost = cost
    iced &= ~lost
    land = land & ~lost
    for _ in range(rings):
        lab, nk = kernels.components(iced, off, idx)
        k = np.maximum(lab, 0)
        budget = np.bincount(k, weights=np.where(iced, smb - calve, 0.0), minlength=nk)
        short = np.flatnonzero(iced & (budget[k] < 0) & (calve > 0))
        if len(short) == 0:
            break
        gain = calve[short] - smb[short]  # (what dropping the cell saves its sheet)
        short, gain = short[gain > 0], gain[gain > 0]
        if len(short) == 0:
            break
        o = np.lexsort((-gain, k[short]))
        short, gain = short[o], gain[o]
        cum = np.cumsum(gain)
        ks = k[short]
        start = np.searchsorted(ks, ks, side="left")
        before = cum - gain - np.where(start > 0, cum[start - 1], 0.0)
        iced[short[before < -budget[ks]]] = False  # (each sheet: its dearest cells until the rest pays)
    cost = np.maximum(-smb, 0.0) + calve
    lab, nk = kernels.components(iced, off, idx)
    budget = np.bincount(np.maximum(lab, 0), weights=np.where(iced, smb - calve, 0.0), minlength=nk)
    open_ = budget > 0
    for _ in range(rings):
        nb_lab = np.where(iced[idx], lab[idx], -1)
        cand = np.full(g.n, -1)
        np.maximum.at(cand, src, nb_lab)
        cand = np.where(land & ~iced & (cand >= 0), cand, -1)
        cand = np.where(cand >= 0, np.where(open_[np.maximum(cand, 0)], cand, -1), -1)
        cells = np.flatnonzero(cand >= 0)
        if len(cells) == 0:
            break
        k, c = cand[cells], cost[cells]
        o = np.lexsort((c, k))
        cells, k, c = cells[o], k[o], c[o]
        cum = np.cumsum(c)
        start = np.searchsorted(k, k, side="left")
        before = cum - c - np.where(start > 0, cum[start - 1], 0.0)
        take = before + c <= budget[k]
        cells, k, c = cells[take], k[take], c[take]
        if len(cells) == 0:
            break
        spent = np.bincount(k, weights=c, minlength=nk)
        took = np.bincount(k, minlength=nk)
        ring = np.bincount(cand[cand >= 0], minlength=nk)
        budget -= spent
        open_ &= (took == ring) & (budget > 0)
        iced[cells] = True
        lab[cells] = k
        if not open_.any():
            break
    return iced


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
    # washes away faster (vegetation's ground cover: canopy, herbs, moss and
    # crust). Deserts are bare either way.
    wet = np.clip(sim.precip / 800.0, 0, 1)
    k_mult = k_mult * (1 + 0.6 * wet * (1 - sim.veg * (sim.w_elev > 0)))
    t0 = t
    # m of elevation per km: of what erosion takes off the top (the
    # sediment cover if there is one, else the basement), and of the
    # (light) sediment deposited
    sed = sediment_km(cover, x)
    iso_dep = sediment_iso(cont, rock, sed)
    iso = np.where(cover > surface.COVER_SHOWS, iso_dep, iso_rate(cont, rock, t))
    col.t, col.cover, x[:, MIX], sim.removed, dep, sim.flow, sim.down, lk = surface.erode(
        g, elevation(t, sim.w_age, cont, rock, sim.datum(), sed), t, cover, x[:, MIX],
        rock, cont, sim.precip, sim.runoff, sim.aet, sim.lake_evap, dt, p.hillslope, p.erosion_timescale,
        p.erosion_height, p.incision, sim.scale, iso, k_mult, p.alluvial, p.fan_km, iso_dep, valley=x[:, VALLEY],
        base_rise=max(-float(sim.sea_ice), 0.0))
    sim.book("erosion", t0, col.t, cont)
    # the valleys rivers to the sea run in now (graded to the river they
    # carry: a shrunken river silts up a valley too big for it), and where
    # no such river runs any more the old ones, filling in slowly from their
    # slopes (hydrology.VALLEY_MYR); they ride on with the rock
    x[:, VALLEY] = np.where(lk["incised"] > 0, lk["incised"], x[:, VALLEY] * np.exp(-dt / hydrology.VALLEY_MYR))
    # the basement comes up by what's worn off net (the strata: in sediments())
    col.eroded_cover = np.clip(sim.removed, 0, np.maximum(cover, 0))
    col.rec[:, record.EXHUMED] = np.maximum(col.rec[:, record.EXHUMED] + sim.removed - dep, 0)
    # what bare ground lost, for the weathering sink: masked by the ice this erosion ran under (the next
    # step's sink sees the ice after a climate update; ground the ice left in it counted its glacial
    # erosion, the 3x buzzsaw, as weathering, PW-438)
    sim.weathered = np.where(sim.ice > 0, 0.0, sim.removed)
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
    e = elevation(col.t, sim.w_age, col.cont, col.rock, sim.datum(), sediment_km(col.cover, x))
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
    e = elevation(col.t, sim.w_age, cont, rock, sim.datum(), sed)
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
