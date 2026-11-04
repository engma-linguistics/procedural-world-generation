"""The earth system around the plates: mantle heat, global temperature and
CO2, sea level, the climate model, and the surface processes that run on
its rain (erosion, rivers, sediment).

State it keeps on the simulation (see Simulation.EARTH_STATE): dT, drift,
co2, rates, refs, depth_ridge, depth_ref, sea_level and its parts sea_ice / sea_tect (with sea_cont, cont_water_ref,
sea_sed, sed_water_ref), ice,
the vegetation (veg, veg_frac, veg_lai, npp, veg_type, tree_cover, flora,
veg_niche), removed, the climate fields from climate.compute, the rivers
(flow, down) and the lakes (lake_kind, lake_depth).
"""

from __future__ import annotations

import numpy as np

from .. import climate, hydrology, icemass, kernels, nest, surface, vegetation
from ..constants import GRAV, RHO_ICE
from ..geo import R_KM, is_land
from ..ocean import cell_area_km2 as ocean_area
from ..surface import COAL as COAL_ROCK, EVAPORITE, LIMESTONE, SANDSTONE, SHALE
from . import record
from .isostasy import (CARB, COAL, EVAP, MIX, OCEAN_KM, RHO_MANTLE, RHO_WATER, SAND, VALLEY, elevation, ice_load, iso_rate, land_view,
                       ocean_depth, sediment_iso, sediment_km)

SEA_TECT_MAX = 400.0  # m: the ocean basins' part of sea level levels off toward +-this (PW-293: was 250, which
# shaped the signal; at 400 a Cretaceous-like +250 m passes at +222)
EARTH_ICE = 0.031  # Earth's land ice today, share of the surface (Antarctica and Greenland)
# The ice-albedo term's zero (PW-873): the model's own Earth at dT = 0 (tools/ice_probe.py 0, the ice rule on
# Earth's bed, area-weighted share of the last 4 of 8 climate updates; v1-finish-13 code), per grid level. The
# climate model's dT = 0 is Earth with that ice, so that ice is neutral, not the real 3.1%.
MODEL_EARTH_ICE = {6: 0.0277, 7: 0.0305}


def earth_ice(level: int) -> float:
    """The model's own Earth ice share at dT = 0 at this grid level (the nearest probed level's)."""
    return MODEL_EARTH_ICE[min(MODEL_EARTH_ICE, key=lambda k: abs(k - level))]
WEATHER_K = 0.09  # per C of local temperature: silicate weathering's kinetics (GEOCARB III's ACT, an activation
# energy of ~62 kJ/mol at 288 K; field silicate fluxes ~59 kJ/mol, White & Blum 1995; the 40-60 kJ/mol range is
# 5.8-8.7%/K; PW-235)
WEATHER_RUNOFF = 0.65  # weathering ~ runoff^this (GEOCARB, Berner 1994, from Peters 1984's rivers), on each cell's
# own land runoff from the climate's water balance (sim.runoff against RUNOFF_REF; PW-881: was the global mean
# rain's 3%/C law, while the model's land rain grows 0.5-2.3%/C on generated planets). The erosion supply the sink
# multiplies doesn't carry it (it is set by uplift over Myr: measured -0.008/C, v1-finish-10), so it is a factor of
# its own (v1-finish-11)
RUNOFF_REF = 560.0  # mm/yr: the scale of the runoff factor (the model's Earth at dT 0, ice-free land's mean; it
# cancels against the sink's reference)
RUNOFF_PER_C = 0.016  # ln of sum(runoff^WEATHER_RUNOFF) over the ice-free land per C of dT, the model's Earth (L6,
# dT -3..+3: 0.0163, 0.0154; land runoff itself 2.6%/C): the runoff's small-signal part of climate_coef and of
# the spin-up's shift to the balance climate, where the runoff at another dT isn't computed
WEATHER_CO2_BARE = 0.5  # bare ground weathers ~ pCO2^this (GEOCARB, Berner 1994: carbonic acid from the air)
WEATHER_FERT = 0.4  # planted ground ~ (2X / (1 + X))^this, X pCO2 against the balance (GEOCARB II/III's FERT, Volk
# 1987): the soil's CO2 comes from roots and microbes, so the air's CO2 acts only through the plants' growth, which
# saturates (log-slope 0.2 at the balance, ~0 at high CO2). Before v1-finish-11 one X^0.4 for all ground
PLANT_WEATHER = 3.0  # fully planted ground weathers this many times faster than bare ground at the same climate and
# CO2 (roots, mycorrhizae, soil CO2 and acids, wetter soils): field pairs 2-5x (Moulton & Berner 1998; Moulton, West
# & Berner 2000, Iceland), ~10x in sandboxes (Bormann et al. 1998), < 2x (Drever 1994); GEOCARB's pre-vascular f_E
# 0.25 is 4x (Berner 1994, 2004). 3 is the field pairs' middle
# (how planted a cell counts for weathering is its rooted plant cover, vegetation.rooted_cover, not its NPP: PW-1424 C,
# PW-1332 B. Until then ground counted fully planted at an NPP of 500 g C/m2/yr, so a fix to the plants' growth moved
# the climate by 3-5 C through the weathering, PW-1332)
CO2_MAX = 6.0  # e-folds of CO2 the log forcing levels off toward (+-; smoothly, tanh: ~400x / 0.0025x the
# reference; snowball exits needed ~40-400x, 3.6-6 e-folds, Caldeira & Kasting 1992, Hoffman et al. 2017; was a hard
# clip at 3, PW-558)
CO2_LOG = float(np.log(1.0e5 / 350.0))  # e-folds above climate.PCO2_REF (350 ppm) to ~0.1 bar, to which CO2's forcing
# stays logarithmic (Myhre et al. 1998's form; line-by-line it is log to super-log up to ~0.1 bar, Byrne & Goldblatt
# 2014, GRL 41: 152; Kasting 1993; Feulner 2012's faint-young-Sun CO2 of 0.01-0.1 bar rests on it) (v1-finish-14)
CO2_SAT = float(np.log(10.0))  # e-folds beyond CO2_LOG over which it levels off: CO2's Rayleigh scattering and the
# saturated bands give a maximum greenhouse near ~1 bar (Kasting 1991; Kasting et al. 1993; Wordsworth &
# Pierrehumbert 2013), one decade further
CO2_TAU = 0.4  # Myr: the CO2 stock's residence time at the reference, ocean-atmosphere carbon over outgassing
# (~40,000 GtC over ~0.1 GtC/yr; the weathering feedback's e-folding, ~CO2_TAU / 0.3 ~1 Myr, is Earth's
# few hundred kyr to ~1 Myr: Archer et al. 2009, Colbourn et al. 2015)
REF_MYR = 100.0  # Myr: during the spin-up, the source's and sink's references follow the planet's rates over this
REF_FREEZE = 300.0  # Myr: then they are kept (PW-558/559 B): the planet's own balance once the made-up start has
# settled, the same spin-up the criteria skip. After it the sink's reference is not the learnt one but the source's
# over exp(YARDSTICK) (references)
YARDSTICK = {6: 1.377, 7: 1.542}  # per grid level: ln(source reference / sink reference) after REF_FREEZE (PW-1424
# A). The learnt ratio was a dice roll: it varied about as much between re-runs of one planet (sd 0.16) as between
# planets (0.18), and each 0.1 of it set the planet's whole later climate 1.1 C warmer or colder (docs/review/climate/
# stability/round1.md, round2.md). One constant per level, the mean of the learnt ratio over the judge's draws
# (tools/yardstick.py re-fits it; re-fit whenever a change moves the weathering's or the outgassing's size); the
# source's reference stays the planet's own, so a planet outgassing more also weathers more at its balance. Levels
# without their own take the nearest (round3.md: L7's from the store's stock runs plus L6's shift)
# (a reference that kept following one part of the sink, the ice-free land's erosion, was tried and dropped on the
# mature start: with no relief build-up left to forget, it forgot real changes in erosion; PW-576 stage 3)


def heat(p, t: float) -> float:
    """Mantle heat relative to today's. A young planet is hotter (more
    radioactive decay, leftover heat of formation): more plumes, more
    melting at arcs, a runnier mantle and faster plates. It fades toward
    1 with the given half-life."""
    return 1.0 + (p.heat_start - 1.0) * 0.5 ** (t / p.heat_halflife)


STAR_AGE_NOW = 4570.0  # Myr: the Sun's age today
WPM2_PER_LUM = 238.0  # W/m2 of forcing per unit relative luminosity (S0 / 4 (1 - 0.3))


def star_luminosity(age: float) -> float:
    """A Sun-like star's luminosity against today's Sun's, at age Myr: Gough (1981),
    L / L_now = 1 / (1 + 0.4 (1 - age / 4570 Myr))."""
    return 1.0 / (1.0 + 0.4 * (1.0 - age / STAR_AGE_NOW))


def star_age(p, t: float) -> float:
    """The star's age, Myr, at run time t: today's Sun's at now_myr (the run's end, less star_now_offset_myr);
    star_brightening times the Sun's pace (PW-809)."""
    return STAR_AGE_NOW + p.star_brightening * (t - now_myr(p))


def check_star(p) -> None:
    """Refuse a run that would start before its star formed (PW-813)."""
    if p.star_brightening > 0.0 and star_age(p, 0.0) < 0.0:
        longest = STAR_AGE_NOW / p.star_brightening + p.star_now_offset_myr
        raise ValueError(f"a run of {now_myr(p) + p.star_now_offset_myr:g} Myr would start before its star formed (star age "
                         f"{star_age(p, 0.0):.0f} Myr); at star_brightening {p.star_brightening:g} and "
                         f"star_now_offset_myr {p.star_now_offset_myr:g} runs can be at most {longest:.0f} Myr")


RUN_END_DEFAULT = 1000.0  # Myr: the run's end when a direct Simulation caller hasn't set params.run_end


def now_myr(p) -> float:
    """The run time that is today ("now", Ma 0) for the star and the plant calendar, the one place both read
    it: the run's end (params.run_end; 0: RUN_END_DEFAULT), less star_now_offset_myr (PW-813)."""
    return (p.run_end if p.run_end > 0 else RUN_END_DEFAULT) - p.star_now_offset_myr


def star_forcing(p, t: float) -> float:
    """The star's forcing, C, against TODAY's Sun (PW-809, coordinator ruling B): the run's end is now, so a run
    starts under a fainter young star (negative forcing: -15.5 C raw at the start of a 1 Gyr run, -29 C for 2 Gyr)
    and ends at 0, the climate model's dT = 0 being Earth under today's Sun. The forcing is
    S0 / 4 (1 - 0.3) dL / L = 238 W/m2 x dL / L, at the model's own sensitivity: co2_sensitivity per doubling of
    CO2's 5.35 ln 2 W/m2 (Myhre et al. 1998), ~0.81 C per W/m2. The carbon cycle answers it (the weathering
    thermostat, with references learnt at the balance climate: start_carbon, global_temperature): the faint
    young star is met by high CO2, as Earth's was."""
    if p.star_brightening == 0.0:
        return 0.0
    rel = star_luminosity(star_age(p, t)) - 1.0
    return float(p.co2_sensitivity / (5.35 * np.log(2.0)) * WPM2_PER_LUM * rel)


GOE_MA = (2400.0, 2100.0)  # Ma: the Great Oxidation Event, over which methane falls from its Archean level (Lyons
# et al. 2014, Nature 506: 307; Holland 2006)
NOE_MA = (800.0, 540.0)  # Ma: the Neoproterozoic Oxygenation Event, over which it falls to the Phanerozoic's
# (Och & Shields-Zhou 2012; Lyons et al. 2014)


CH4_PI, N2O_PI = 700.0, 270.0  # ppb: pre-industrial, in the climate model's dT = 0
CH4_Q10, N2O_Q10 = 3.0, 2.0  # the wetlands' methane and the soils' N2O per 10 C of their ground (wetland CH4
# Q10 ~2-4: Walter & Heimann 2000; Gedney et al. 2004 use ~3; soil N2O ~2, Butterbach-Bahl et al. 2013)
GHG_LAND_T = 0.7  # C of the emitting land's temperature per C of dT (temp_response at the wetlands' ~30-60 deg)
CH4_LOG = 5000.0  # ppb above which CH4's forcing goes as ln rather than Myhre's sqrt (its bands saturate; the
# shortwave absorption grows: Byrne & Goldblatt 2014, Clim. Past 10: 1779), with the slope continuous there


def ghg_conc(p, t: float, dT: float, icefree: float) -> tuple[float, float]:
    """(CH4, N2O), ppb, at run time t (PW-859; v1-finish-14): each a steady state of its source over its
    oxidation lifetime (~10 yr for CH4, ~120 yr for N2O: years against the run's Myr steps), so the
    concentration goes as source x lifetime.
      - Source: the wetlands' methane and the soils' N2O, against the pre-industrial's: warmer ground
        (CH4_Q10, N2O_Q10 on GHG_LAND_T dT), wetter (the model's own land runoff, RUNOFF_PER_C), and the
        ice-free land against Earth's (icefree). The LGM check: dT ~-5 gives CH4 ~390 ppb and N2O ~200
        (ice cores ~370 and ~200, Loulergue et al. 2008, Schilt et al. 2010).
      - Lifetime: methane's oxidation is slower under the low-oxygen air before the oxygenation events (less
        OH; Pavlov et al. 2000, Kasting 2005), params.methane_proterozoic / methane_archean x the
        pre-industrial's, falling linearly across each event (GOE_MA, NOE_MA). N2O's deep-time levels are not
        known well enough to count (Roberson et al. 2011: possibly higher in a copper-poor ocean)."""
    ma = now_myr(p) - t

    def ramp(old_young, a, b):  # a before (older than) the event, b after
        old, young = old_young
        return a if ma >= old else b if ma <= young else b + (a - b) * (ma - young) / (old - young)
    life = ramp(NOE_MA, ramp(GOE_MA, p.methane_archean, p.methane_proterozoic), 1.0)
    land = GHG_LAND_T * dT
    wet = np.exp(RUNOFF_PER_C * dT) * icefree
    return (CH4_PI * life * wet * CH4_Q10 ** (land / 10.0), N2O_PI * wet * N2O_Q10 ** (land / 10.0))


def ghg_forcing(p, t: float, dT: float = 0.0, icefree: float = 1.0) -> float:
    """CH4's and N2O's forcing, C, against the pre-industrial's (ghg_conc), at the model's own sensitivity
    (as the star's): Myhre et al. 1998's 0.036 (sqrt M - sqrt M0) and 0.12 (sqrt N - sqrt N0) W/m2 (overlap
    left out), CH4's going over to ln beyond CH4_LOG. Sized so ~30 ppm (the Proterozoic's middle) is ~4 W/m2
    and ~1000 ppm (the Archean's) ~8 W/m2, as the line-by-line work (Byrne & Goldblatt 2014; Haqq-Misra et al.
    2008: ~+10 K)."""
    m, n = ghg_conc(p, t, dT, icefree)

    def ch4(x):
        if x <= CH4_LOG:
            return 0.036 * np.sqrt(x)
        return 0.036 * np.sqrt(CH4_LOG) + 0.018 * np.sqrt(CH4_LOG) * np.log(x / CH4_LOG)
    w = ch4(m) - ch4(CH4_PI) + 0.12 * (np.sqrt(n) - np.sqrt(N2O_PI))
    return float(p.co2_sensitivity / (5.35 * np.log(2.0)) * w)


def drift_source(p, drift: float) -> float:
    """The carbon source's drift factor (PW-819): the walk drift (C, sd climate_drift) as the source change
    that warms the balance planet (planted, at the balance: the reference, v1-finish-11) by that much through
    the weathering thermostat (small signal, the weathering land's START_RESPONSE): ln s = drift (a + c G) / G,
    a = WEATHER_FERT / 2 the planted law's CO2 log-slope at the balance, c = climate_coef(), G =
    co2_sensitivity / ln 2 C per e-fold of CO2."""
    g = p.co2_sensitivity / np.log(2.0)
    return float(np.exp(drift * (0.5 * WEATHER_FERT + climate_coef() * g) / g))


START_RESPONSE = 0.6  # C of weathering-land temperature per C of dT, for start_carbon's first guess and the drift's
# size only (the land isn't made yet): temp_response's 0.5 in the tropics to ~0.8 at 40 deg, where most rock weathers
START_PLANTED = 0.5  # the share of the weathering ground counted as fully planted (rooted cover 1) in start_carbon's
# first guess (from the first step the carbon cycle itself sets the stock, within ~CO2_TAU)


def climate_coef() -> float:
    """ln of the sink per C of dT on the weathering land, small signal: kinetics (WEATHER_K at the land's
    START_RESPONSE) and runoff (RUNOFF_PER_C, the model's own land runoff)."""
    return WEATHER_K * START_RESPONSE + RUNOFF_PER_C


def temp_response(grid) -> np.ndarray:
    """Per cell, C of its annual temperature per C of the climate's dT: climate.compute moves the equator by
    0.5 dT and the poles by 1.5 dT along climate.temperature's latitude shape (polar amplification)."""
    x = np.sin(np.radians(grid.lat)) ** 2
    return 0.5 + (0.156 * x + 2.012 * x**2 - 1.168 * x**3)


def _planted(x, bare: float, starve):
    """(M, dM / d ln X): the planted ground's share of the sink at the balance, (1 - bare), with its plants'
    enhancement (PLANT_WEATHER - 1 of its PLANT_WEATHER) scaled per cell by the C3 plants' starvation below the
    vegetation's CO2 floor (vegetation.starvation, PW-1227; starve: (each cell's planted share of the sink at
    the balance, summing to 1 - bare, its temperature C), or None: no starvation). 1 - bare at and above the
    floor."""
    if starve is None or climate.PCO2_BALANCE * x >= vegetation.CO2_FLOOR:
        return 1.0 - bare, 0.0
    wp, t = starve
    q, dq = vegetation.starvation(t, climate.PCO2_BALANCE * x)
    k = (PLANT_WEATHER - 1.0) / PLANT_WEATHER
    return float((wp * (1.0 - k + k * q)).sum()), float((wp * k * dq).sum())


def co2_law(x, bare: float, starve=None):
    """The weathering sink's CO2 factor at X = x (pCO2 against the balance; 1 there): bare ground's share
    `bare` of the sink (at the balance) ~ X^WEATHER_CO2_BARE, the planted rest ~ (2X / (1 + X))^WEATHER_FERT
    (GEOCARB III, Berner & Kothavala 2001; their mix while plants spread, Berner 2006). Below the plants' CO2
    floor (vegetation.CO2_FLOOR, 124 ppm) the plants starve: their enhancement of the planted ground's
    weathering falls with their C3 quantum yield, cell by cell (_planted, starve; Pagani et al. 2009: "vegetation
    activity is substantially reduced, compromising the capacity to further enhance silicate chemical
    weathering"; GEOCARB's FERT is the same growth response above the floor)."""
    m, _ = _planted(x, bare, starve)
    return bare * x**WEATHER_CO2_BARE + m * (2.0 * x / (1.0 + x)) ** WEATHER_FERT


def co2_slope(x, bare: float, starve=None) -> float:
    """d ln co2_law / d ln X: the sink's CO2 log-slope (0.5 on bare ground; 0.2 planted at the balance, less
    above it; steeper below the plants' CO2 floor, where they starve)."""
    sat = (2.0 * x / (1.0 + x)) ** WEATHER_FERT
    m, dm = _planted(x, bare, starve)
    num = bare * WEATHER_CO2_BARE * x**WEATHER_CO2_BARE + m * WEATHER_FERT * sat / (1.0 + x) + sat * dm
    return float(num / co2_law(x, bare, starve))


def start_weatherability(p) -> tuple[float, float]:
    """(w, bare): the start's sink at the balance climate against the planted reference, and its bare share,
    for start_carbon's first guess: the run's land counted START_PLANTED planted if the land pioneers are
    there from the start (vegetation.group_windows), else bare, which weathers 1 / (1 + (PLANT_WEATHER - 1)
    START_PLANTED) of the planted reference."""
    planted = 1.0 + (PLANT_WEATHER - 1.0) * START_PLANTED
    if vegetation.group_windows(now_myr(p))[0][1] <= 0.0:
        return 1.0, (1.0 - START_PLANTED) / planted
    return 1.0 / planted, 1.0


def balance_co2(p, forcing: float) -> float:
    """The CO2 stock (ln X against PCO2_BALANCE) at which the weathering thermostat balances a lasting
    forcing (C, e.g. the star's against today's Sun) on the run's starting land (start_weatherability: w,
    bare): w co2_law(X) exp(c dT') equals the outgassing, dT' the departure from the balance climate,
    co2_term(ln X) - co2_term(0) + forcing, c = climate_coef(). It is the run's start only: from the first step
    the carbon cycle itself sets the stock. The carbon source's drift and the ice's albedo are left out (they
    start at 0 and at no ice)."""
    w, bare = start_weatherability(p)

    def f(c):
        return (np.log(w * co2_law(np.exp(c), bare))
                + climate_coef() * (co2_term(p, c) - co2_term(p, 0.0) + forcing))
    lo, hi = -30.0, 30.0  # (f increases with c)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) < 0.0 else (lo, mid)
    return 0.5 * (lo + hi)


def start_carbon(p) -> tuple[float, float]:
    """(co2, dT) a run starts from (PW-809): the carbon stock in balance with the star of the run's start, so a
    faint young star starts the planet warm through high CO2 rather than frozen, and the climate that stock
    and that star give (plus climate_offset, the world-builder's shift)."""
    check_star(p)
    f0 = star_forcing(p, 0.0) + ghg_forcing(p, 0.0)
    c = balance_co2(p, f0)
    return c, co2_term(p, c) + f0 + p.climate_offset


STAR_ICEHOUSE_SL = -20.0  # m: an icehouse holds at least this much sea level as land ice (tools/ice_criteria's)


def star_control(sim) -> float:
    """The star thermostat (PW-791), a world-builder's CONTROL, not physics: C of forcing added to the star's.
    Causal and slow: it follows the planet's own running icehouse share (an e-folding mean over star_window Myr of
    whether land ice holds >= 20 m of sea level) and, from star_control_from Myr, moves the star's output by
    star_gain C per Myr per unit of share outside [star_ice_lo, star_ice_hi]: dimmer for a planet that has gone
    without ice (never-ice, hellhole), brighter for one that stays iced (icebox). Inside the band it holds.
    Bounded to +-star_control_max of the luminosity. It never sets CO2: the weathering thermostat answers the
    star's change, keeping more CO2 under a dimmer star. Off (0) unless params.star_thermostat."""
    p = sim.params
    if not p.star_thermostat:
        return 0.0
    iced = 1.0 if sim.sea_ice <= STAR_ICEHOUSE_SL else 0.0
    if sim.ice_share is None:  # (the run's start: the middle of the band, so nothing acts on an empty memory)
        sim.ice_share = 0.5 * (p.star_ice_lo + p.star_ice_hi)
    sim.ice_share += (1 - np.exp(-sim.dt_now / p.star_window)) * (iced - sim.ice_share)
    if sim.t >= p.star_control_from:
        off = min(sim.ice_share - p.star_ice_lo, 0.0) + max(sim.ice_share - p.star_ice_hi, 0.0)
        bound = p.co2_sensitivity / (5.35 * np.log(2.0)) * WPM2_PER_LUM * p.star_control_max
        sim.star_ctl = float(np.clip(sim.star_ctl + p.star_gain * off * sim.dt_now, -bound, bound))
    return sim.star_ctl


def target_fraction(p, t: float) -> float:
    """Share of the surface the continents are steered toward at time t."""
    if p.continental_start < 0:
        return p.continental_fraction
    return p.continental_fraction + (p.continental_start - p.continental_fraction) * np.exp(
        -t / p.continental_growth)


def plant_factor(cover) -> np.ndarray:
    """Per cell, how many times faster than bare ground its plants make it weather, from its rooted plant cover
    (vegetation.rooted_cover, 0..1): 1 bare, PLANT_WEATHER fully covered, in proportion between (PW-1424 C)."""
    return 1.0 + (PLANT_WEATHER - 1.0) * np.clip(np.asarray(cover, float), 0.0, 1.0)


def references(sim):
    """The carbon cycle's [source, sink] references as the stock reads them: the learnt sim.refs up to and at
    REF_FREEZE; after it the source's (the planet's own outgassing) with the sink's set YARDSTICK below it (PW-1424
    A). sim.refs keeps the learnt pair (tools/yardstick.py reads the learnt ratio)."""
    if sim.refs is None or sim.t <= REF_FREEZE + 1e-9:
        return sim.refs
    return np.array([sim.refs[0], sim.refs[0] * np.exp(-yardstick(sim.grid.level))])


def yardstick(level: int) -> float:
    """YARDSTICK at a grid level, or the nearest level's."""
    return YARDSTICK[min(YARDSTICK, key=lambda k: (abs(k - level), k))]


def weathering(sim, land):
    """The silicate weathering sink per cell at the balance's CO2 (model units: km of rock per step, times the
    factors; co2_law gives its CO2 dependence) and its parts, for global_temperature and the diagnostics:
    (sink, supply, climate factor, plant factor, bare part). "Per step" is per step of dt (the run's step):
    a finish-window step (Simulation.step_length) counts its erosion at that rate. The supply is what bare ground
    lost to erosion
    (sim.weathered: not under land ice, where glaciers grind their beds fast but the rock flour hardly
    weathers chemically in the cold, and counting it made a cold era draw down more CO2 the more ice it grew).
    The bare part is the sink of the cell's unplanted ground, which goes as X^WEATHER_CO2_BARE."""
    supply = sim.weathered * land  # (per dt step, as erode keeps it: the references are learnt in those)
    # chemical weathering: faster when warm and when wet (the weathering thermostat, Walker et al. 1981: a cold
    # planet weathers slower, CO2 builds up and warms it back, PW-235): the kinetics on the local temperature,
    # and the cell's own land runoff (WEATHER_RUNOFF; PW-881)
    warm = np.exp(WEATHER_K * (sim.temp - 15.0)) if sim.temp is not None else np.ones_like(supply)
    if sim.runoff is not None:
        warm = warm * (np.maximum(sim.runoff, 0.0) / RUNOFF_REF) ** WEATHER_RUNOFF
    # roots and soil CO2 speed it up, in proportion to the ground rooted plants cover (GEOCARB's f_E, plant_factor;
    # PW-1424 C: was their NPP, so a plant-growth fix moved the climate)
    # (on the run's plants grown at the balance's CO2, sim.cover_w: the CO2 acts on the planted ground through
    # co2_law's FERT, GEOCARB's form of the plants' CO2 response, and counting the plants' own CO2 response too made
    # the planted sink's CO2 slope ~55% too steep, PW-880)
    plants = plant_factor(sim.cover_w)
    v = (plants - 1.0) / (PLANT_WEATHER - 1.0)
    return supply * (warm * plants), supply, warm, plants, supply * warm * (1.0 - v)


def co2_stock(co2, s, w, dt, bare=1.0, steps=4, starve=None):
    """The CO2 stock over a step (PW-558). co2 is ln X, X the stock (pCO2, climate.pco2) relative to the
    reference; s the volcanic source and w the weathering sink at X = 1, each against its reference; bare the
    sink's share on bare ground; starve the planted ground's cells for its plants' starvation below their CO2
    floor (co2_law). Weathering also grows with CO2 itself (carbonic acid; co2_law: X^0.5 on bare
    ground, saturating under plants, falling off where they starve, GEOCARB III), so
        dX/dt = (s - w co2_law(X, bare)) / CO2_TAU.
    Its steady state is w co2_law(X) = s. CO2_TAU is far below a step, so X is about there each step, except
    where the sink is nearly gone (ice over the weathering land): then X grows at s / CO2_TAU, as outgassing
    piled CO2 up under the Cryogenian ice. Backward Euler substeps (stable at any step); each solves
    X + c1 co2_law(X) = c0 by Newton's method in ln X, kept inside a bracket (the function increases)."""
    h = dt / steps
    x = float(np.exp(co2))
    for _ in range(steps):
        c1, c0 = h * w / CO2_TAU, x + h * s / CO2_TAU
        hi = np.log(c0)  # (F(hi) >= 0: co2_law >= 0)
        lo = hi - 80.0
        u = hi
        for _ in range(100):
            eu = np.exp(u)
            law = co2_law(eu, bare, starve)
            fu = eu + c1 * law - c0
            if fu > 0.0:
                hi = u
            else:
                lo = u
            du = fu / (eu + c1 * law * co2_slope(eu, bare, starve))
            un = u - du
            if not lo < un < hi:
                un = 0.5 * (lo + hi)
            if abs(un - u) < 1e-12:
                u = un
                break
            u = un
        x = float(np.exp(u))
    return float(np.log(x))


def co2_term(p, co2):
    """The CO2 stock's warming, C: co2_sensitivity per doubling of pCO2 (climate.pco2; an e-fold is 1 / ln 2
    doublings) above the climate model's dT = 0 (climate.PCO2_REF: the planet's balance, PCO2_BALANCE, is a
    doubling warmer), levelling off smoothly toward +-CO2_MAX e-folds (CO2's forcing is ~logarithmic up to ~0.1 bar
    and grows less beyond)."""
    c = co2 + np.log(climate.PCO2_BALANCE / climate.PCO2_REF)  # e-folds above the climate's dT = 0 (PW-559 B)
    g = p.co2_sensitivity / np.log(2.0)
    if c <= 0.0:
        return g * CO2_MAX * float(np.tanh(c / CO2_MAX))
    # (above the reference: exactly logarithmic up to ~0.1 bar, then levelling off over the next decade toward the
    # maximum greenhouse; a tanh over all of it, as before v1-finish-14, already withheld 8% of the forcing at
    # 20x and 18% at 150x, the faint young Sun's CO2)
    if c <= CO2_LOG:
        return g * c
    return g * (CO2_LOG + CO2_SAT * float(np.tanh((c - CO2_LOG) / CO2_SAT)))


PLUME_CO2 = 3.3  # CO2 per km3 of plume melt (plume heads, their vents and aprons: volcanism.hotspots, before the
# height caps, which decide where lava piles, not how much melt degasses) against the ridges' per km3 of new ocean
# crust (PW-875). Ridges: ~2.2e12 mol C/yr (Marty & Tolstikhin 1998) over ~21 km3/yr of crust (Crisp 1984), ~1e11
# mol/km3, ~0.15 wt% CO2. Plume and flood-basalt melts: ~0.5 wt% (Self et al. 2006's Deccan figure; Black &
# Gibson 2019: plume melts carry recycled carbon, richer than MORB). 0.5 / 0.15. Not counted: the sediments a
# LIP's sills bake (Svensen et al. 2004, Siberia), which the model has no carbon-bearing basin rock for.


def ghg_icefree(sim, ice_frac: float, ice_ref: float) -> float:
    """The ice-free land against Earth's (its ice, earth_ice), for ghg_conc: (land - ice) / (land - Earth's ice),
    planet shares."""
    land = float((sim.land() * ocean_area(sim.grid)).sum() / ocean_area(sim.grid).sum())
    return max(land - ice_frac, 0.0) / max(land - ice_ref, 1e-6)


def continent_water(sim, w) -> float:
    """m of sea level from the water the continents hold (PW-980): the ocean's water is conserved, so the sea
    the drowned continental crust (shelves, drowned margins, flooded interiors) holds at the ice-free sea level
    against the run's start, less of it as the continents rise or thicken, goes into the ocean basins and raises
    the sea there by (rho_m - rho_w) / rho_m of its depth over the ocean (the floor sinks under the load, as for
    the basins' own part). Without it the continents could rise out of the sea with nowhere for their water to
    go: thick crust made land and sea level was only the ocean floor's age (lane 23: land 31 -> 35%, the drowned
    continent's median -1519 -> -819 m). Lagged by a step (the depths are the step before's, at its sea level):
    each step solves it again from depths that already stand at the last rise (a rise floods ~A_submerged /
    A_ocean ~0.1 of its own water back, so the iteration converges geometrically).
    w: the cells' areas. Measured at the ice-free level (w_elev + sea_ice), so the shelves an ice age drains are
    not counted as water set free (sea_ice already took it)."""
    e = sim.w_elev + sim.sea_ice  # m above the ice-free sea level
    held = float((np.where(sim.w_cont, np.maximum(-e, 0.0), 0.0) * w).sum() / w.sum())  # m over the whole surface
    if sim.cont_water_ref is None:  # (the run's start: its continents' sea is the reference)
        sim.cont_water_ref = held
    ocean = max(float(((e < 0) * w).sum() / w.sum()), 1e-3)
    return (RHO_MANTLE - RHO_WATER) / RHO_MANTLE * (sim.cont_water_ref - held) / ocean


def floor_sediment_water(sim, w) -> float:
    """m of sea level from the water the sediment on the oceanic crust displaces (PW-950 lane 100e): the basins'
    part (the age-depth curve) reads the floor without its cover, so sediment carried off a shelf onto the ocean
    floor lowered the sea (the shelf held more water, continent_water) when it should leave it nearly unchanged,
    and the ocean floor's cover (~180 m of floor late in an L6 run) never raised it. Counted as continent_water
    counts the continents: the water the cover keeps out of each oceanic cell (its depth below the ice-free sea
    with the cover, against without it), over the whole surface, against the run's start, spread over the ocean
    and raised by (rho_m - rho_w) / rho_m for the floor's sinking under the water. Lagged by a step, as the
    continents' part is. w: the cells' areas."""
    o = ~sim.w_cont
    sed = sediment_km(sim.w_cover[o], sim.w_extra[o])
    thick, age, rock = sim.w_thick[o], sim.w_age[o], sim.w_rock[o]
    sea = np.zeros(len(sed), bool)  # (oceanic crust)
    lift = elevation(thick, age, sea, rock, 0.0, sed) - elevation(thick - sed, age, sea, rock, 0.0, 0.0 * sed)
    e1 = sim.w_elev[o] + sim.sea_ice  # m above the ice-free sea level, with the cover
    kept = np.maximum(-(e1 - lift), 0.0) - np.maximum(-e1, 0.0)  # m of water the cover keeps out
    shut = float((kept * w[o]).sum() / w.sum())
    if sim.sed_water_ref is None:  # (the run's start: its floor's cover is the reference)
        sim.sed_water_ref = shut
    e = sim.w_elev + sim.sea_ice
    ocean = max(float(((e < 0) * w).sum() / w.sum()), 1e-3)
    return (RHO_MANTLE - RHO_WATER) / RHO_MANTLE * (shut - sim.sed_water_ref) / ocean


def global_temperature(sim, growth, newc, rng, plume=None):
    """The planet's mean temperature, as an offset dT from today's Earth.
    Four things move it, slowly (tens of Myr):
      drift      a random walk that keeps returning toward 0 (all the
                 carbon-cycle and ocean details this model doesn't have),
                 on the carbon source (PW-819: drift_source), so a warm
                 era carries high CO2, as Earth's did, not low
      CO2        a stock (co2_stock): volcanism at ridges, arcs and plumes
                 (PW-875) adds it (warming); fresh rock weathering in warm, wet mountains
                 removes it (cooling, e.g. the Himalaya since 40 Ma). Each
                 is measured against a reference: the source against the
                 planet's own outgassing once its start has settled
                 (REF_FREEZE), the sink against the source's over one
                 constant per grid level (YARDSTICK, references), so
                 lasting changes keep counting. A cold or icy planet weathers slower (the
                 weathering thermostat), so CO2 piles up and warms it back
      ice        ice sheets reflect sunlight (cooling feedback)
      star       the star brightens as it ages (star_forcing; the CO2
                 thermostat draws CO2 down against it, partly)
    Real Earth: a few long icehouse eras (Cryogenian, late Ordovician,
    Permo-Carboniferous, today) between long greenhouse ones.
    growth: the arcs' outgassing this step, as their crust growth at the
    nominal rate (crust.arc_growth's nominal, km/Myr per cell: the melt the
    slabs make, without the crust thermostat's gain, which holds the
    continents' volume on target and is a bookkeeping knob, not a magma
    flux: at L6 it climbed ~1.4 -> ~2.5-3.3 over 300-1000 Myr, at L7 it
    stayed ~1.1-1.8, and the CO2 it added made L6 ~1 C warmer than L7,
    PW-741); newc: number of new ocean-floor cells this step."""
    p, dt = sim.params, sim.dt_now
    a = np.exp(-dt / p.climate_drift_time)
    sim.drift = sim.drift * a + p.climate_drift * np.sqrt(1 - a * a) * rng.normal()
    land = sim.land()
    noise = drift_source(p, sim.drift)
    # (plume: km/Myr of plume melt per cell; as new ocean floor's cells of OCEAN_KM crust per step, times its yield)
    # (the source and the sink are counted per step of dt, the run's step, which the references are learnt in;
    # a finish-window step's per-step amounts are scaled to that: Simulation.step_length)
    melt = float(plume.sum()) * sim.dt / OCEAN_KM if plume is not None else 0.0
    sim.plume_src = PLUME_CO2 * melt / sim.scale**2
    source = (newc * (sim.dt / dt) / sim.scale**2 + 20.0 * growth.sum() / sim.scale**2 + sim.plume_src) * noise
    sink_cells, supply, warm, _, bare_cells = weathering(sim, land)
    sink = float(sink_cells.sum()) / sim.scale**2
    if sink > 0.0:  # (the first step: nothing has eroded yet; the references start from the first real rates)
        now = np.array([max(source, 1e-6), sink])
        sim.rates = now
        # The references: the planet's own balance of outgassing against weathering, followed while the made-up
        # start settles and then kept for the rest of the run (PW-558, PW-559 B). Kept, they let a long cold era's
        # weathering deficit go on piling up CO2 (and a long surplus go on drawing it down), as a real carbon
        # stock does, where baselines that relearned took both up within a few hundred Myr (PW-576).
        # The sink's reference is anchored where the star is, at the run's end (GEOCARB's frame, coordinator
        # ruling v1-finish-11): the planet's weatherability with land plants, at the balance climate. So
        #  - its plants are the potential vegetation of the spin-up's climate with every group there, at the
        #    balance's CO2 (sim.cover_pot, update_vegetation), not the spin-up's own (bare before ~470 Ma), and
        #    bare early land weathers slower than the balance, holding more CO2, until the plants come;
        #  - its climate is the balance's (PW-809): the sink taken back to the balance's dT (co2_term(0), plus
        #    climate_offset, the world-builder's shift) through the weathering's temperature law, each cell by
        #    its own temperature's response to dT (temp_response), and the runoff's, so a cold spin-up under the
        #    faint young star is not learnt as the planet's balance either.
        if sim.t < REF_FREEZE:
            # (the source's reference without its drift: the wander is not learnt as the balance either)
            shift = co2_term(p, 0.0) + p.climate_offset - sim.dT  # C of dT from here to the balance climate
            resp = WEATHER_K * temp_response(sim.grid) + RUNOFF_PER_C
            pot = plant_factor(sim.cover_pot if sim.cover_pot is not None else 0.0)
            at_bal = float((supply * warm * pot * np.exp(resp * shift)).sum()) / sim.scale**2
            learn = np.array([now[0] / noise, max(at_bal, 1e-12)])
            if sim.refs is None:
                sim.refs = learn
            b = 1 - np.exp(-dt / min(REF_MYR, 10.0 + sim.t))
            sim.refs = sim.refs + b * (learn - sim.refs)
        elif sim.refs is None:
            sim.refs = now.copy()
        tot = max(float(sink_cells.sum()), 1e-300)
        starve = None
        if sim.temp is not None:  # (the planted ground's cells, for its plants' starvation below their CO2 floor)
            on = sink_cells > bare_cells
            starve = ((sink_cells - bare_cells)[on] / tot, sim.temp[on])
        ref = references(sim)  # (after the spin-up: the source's own, the sink's one YARDSTICK below it, PW-1424 A)
        sim.co2 = co2_stock(sim.co2, now[0] / ref[0], now[1] / ref[1], dt,
                            bare=float(bare_cells.sum()) / tot, starve=starve)
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
    w = ocean_area(sim.grid)
    sim.sea_cont = continent_water(sim, w)
    sim.sea_sed = floor_sediment_water(sim, w)
    sim.sea_tect += sim.sea_cont + sim.sea_sed
    sim.sea_level = sim.sea_ice + sim.sea_tect
    ice_frac = float(((sim.ice > 0) * w).sum() / w.sum())  # (area-weighted: cells differ by up to ~9%)
    ice_ref = earth_ice(sim.grid.level)
    # (the ice's whiteness levels off: a sheet spreading over more land shades its own cold surroundings,
    # cloudier and dimmer at high latitude, and the snow it would brighten is often white already)
    def albedo(f):
        return p.ice_albedo_max * np.tanh(p.ice_albedo * f / 0.03 / max(p.ice_albedo_max, 1e-9))

    # (measured from the model's own Earth ice, earth_ice: the climate model's dT = 0 is Earth's climate with
    # its ice; before PW-190 any ice cooled from an ice-free planet's, ~1.4 C too cold with Earth's ice)
    target = (co2_term(p, sim.co2) - (albedo(ice_frac) - albedo(ice_ref)) + star_forcing(p, sim.t)
              + ghg_forcing(p, sim.t, sim.dT, ghg_icefree(sim, ice_frac, ice_ref)) + star_control(sim))
    if getattr(sim, "diag", None) is not None:  # (opt-in diagnostics, read only: tectonics/diag.py)
        sim.diag.temperature(sim, source, sink, ice_frac, co2_term(p, sim.co2),
                             -(albedo(ice_frac) - albedo(ice_ref)), target + p.climate_offset)
    sim.dT += (1 - np.exp(-dt / 5.0)) * (target + p.climate_offset - sim.dT)


def finishing(sim) -> bool:
    """The run is in its finish window (Simulation.step_length), counting the 2 Myr step that ends at its start."""
    p = sim.params
    return p.finish_window > 0 and p.run_end > 0 and sim.t >= p.run_end - p.finish_window - 1e-9


def climate_cadence(sim) -> float:
    """Myr between climate updates at this point of the run, before the finish window (PW-247's ramp):
    half Params.climate_every within climate_ramp_fine Myr of the finish window's start, climate_every within
    climate_ramp Myr, doubled for each further factor 10 back, at most climate_every_max. A run without an end
    (run_end 0) keeps climate_every_max."""
    p = sim.params
    k, kmax = p.climate_every, max(p.climate_every_max, p.climate_every)
    if p.run_end <= 0 or p.climate_ramp <= 0:
        return kmax
    left = p.run_end - p.finish_window - sim.t
    if left <= p.climate_ramp_fine:
        return k / 2.0
    if left <= p.climate_ramp:
        return k
    return min(kmax, k * 2.0 ** np.ceil(np.log10(left / p.climate_ramp) - 1e-12))


def climate_due(sim) -> bool:
    """The climate is updated on the first step and then at every multiple of the cadence (climate_cadence);
    from the finish window's start (finishing) at every step. A keyframe between updates shows the last
    update's climate."""
    if finishing(sim) or sim.precip is None:
        return True
    k = climate_cadence(sim)
    return (sim.t + 1e-9) // k > (sim.climate_t + 1e-9) // k or climate_moved(sim) >= 1.0


def climate_moved(sim) -> float:
    """How far the global temperature offset moved since the last update (sim.climate_in), in units of the
    adaptive cadence's threshold (Params.climate_adapt_dT; 0 when it is off)."""
    p, ref = sim.params, sim.climate_in
    if ref is None or p.climate_adapt_dT <= 0:
        return 0.0
    return abs(sim.dT - ref["dT"]) / p.climate_adapt_dT


def climate_interval(sim) -> float:
    """Myr between this climate update and the last."""
    return sim.t - sim.climate_t if sim.t > sim.climate_t else sim.dt_now


def climate_level(sim) -> int:
    """The grid level this climate update is computed on: Params.climate_level when it is coarser than the
    run's grid and the run isn't finishing (PW-247), else the run's own."""
    lv = sim.params.climate_level
    return lv if 0 < lv < sim.grid.level and not finishing(sim) else sim.grid.level


def _climate(sim, e, ice, veg):
    """climate.compute for update_climate, on the run's grid or a coarser nested one (climate_level,
    nest.climate_coarse). sim.rain_state is the last update's rain kernel state on whichever grid it ran: a
    fine update after coarse ones (the finish window's first) starts from it prolonged."""
    g, p = sim.grid, sim.params
    lv = climate_level(sim)
    if lv < g.level:
        return nest.climate_coarse(g, lv, e, sim.dT, p.tilt, ice, veg=veg, rain_start=sim.rain_state)
    rs = sim.rain_state
    if rs is not None and rs["vap"].shape[-1] != g.n:
        rs = nest.prolong_rain_state(g, rs)
    return climate.compute(g, e, sim.dT, p.tilt, ice, veg=veg, rain_start=rs)


def update_climate(sim, e):
    """Temperature, seasons, rain, ice and Koppen class on elevation e
    (m above the current sea level, without ice, and without the ice's
    load: the crust's own height). The bed under the ice is pressed down by
    it (glacial isostasy, sim.ice_sink, settled at once in a run's Myr
    steps): the ice's surface stands lower (warmer), and land the load
    pushes below the sea without ice on it is sea. Grounded ice on a bed
    below sea level stays land (isostasy.land_view)."""
    p, g = sim.params, sim.grid
    bed, crust = e - sim.ice_sink, e
    e, ice0, _ = land_view(bed, np.where(crust > 0, sim.ice, 0.0))
    land = is_land(e, grid=g)
    c = _climate(sim, e, np.where(land, ice0, 0.0), veg_feedback(sim))
    sim.rain_state = c["rain_state"]  # the next update's rain starts from it (PW-387)
    sim.temp, sim.t_warm, sim.t_cold = c["temp"], c["t_warm"], c["t_cold"]
    sim.sst = c["sst"]  # (the sea's own surface temperature: the reefs', PW-876)
    sim.precip, sim.p_jul, sim.p_jan = c["precip"], c["p_jul"], c["p_jan"]
    sim.runoff, sim.aet, sim.lake_evap = c["runoff"], c["aet"], c["lake_evap"]
    sim.wind_jul, sim.wind_jan, sim.current = c["wind_jul"], c["wind_jan"], c["current"]
    sim.wind = 0.5 * (sim.wind_jul + sim.wind_jan)
    marine, info = marine_view(bed, c), {}
    if p.ice_warm_persist:  # (the ice that outlasts the cycle's warm phase seeds the time-mean sheets, PW-1142)
        warm0 = ice0 if sim.ice_warm is None else land_view(bed, np.where(crust > 0, sim.ice_warm, 0.0))[1]
        sim.ice_warm = ice_sheets(sim, land, e, c["ground"], np.where(land, warm0, 0.0), sim.ice_sink, {},
                                  marine=marine, warm=float(p.ice_warm_persist))
        ice0 = sim.ice_warm
    sim.ice = ice_sheets(sim, land, e, c["ground"], ice0, sim.ice_sink, info, marine=marine, reground=c["reground"])
    c["ground"] = info.get("ground", c["ground"])  # (under the settled ice's own carried air, PW-1050)
    ice = np.where(land, sim.ice, 0.0)
    sim.t_warm, sim.t_cold, sim.temp = climate.ice_surface(*c["ground"], ice, icemass.sheet_cover(g, ice, info["air"]),
                                                           g.lat, sim.p_jul, sim.p_jan)
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
    sim.shade_jul, sim.shade_jan = c["shade_jul"], c["shade_jan"]  # (the light's cloud: climate.shade)
    update_vegetation(sim, e)
    sim.ice_sink = ice_load(g, sim.ice)
    sim.climate_t = sim.t


def bed_thawed(ice, t_s, precip, geo=0.065):
    """Share (0..1) of each ice column's bed at the melting point
    (timezoom.kernels.thawed, Robin 1955, vectorised): ice (m) thick, t_s
    (C) the ice surface's annual mean, the accumulation ~ the
    precipitation (mm/yr, as m/yr of ice: on a sheet nearly all of it is
    snow) carrying the surface's cold down, geo (W/m2) geothermal heat (the
    time zoom's geo_flux). 0 where there is no ice."""
    from math import sqrt
    from ..timezoom.kernels import K_ICE, KAPPA_ICE, PMP
    h = np.maximum(np.asarray(ice, float), 0.0)
    acc = np.maximum(np.asarray(precip, float), 0.0) / 1000.0
    g = geo / K_ICE
    L = np.sqrt(2.0 * KAPPA_ICE * h / np.maximum(acc, 1e-6))
    rise = np.where(acc > 1e-6, g * L * (sqrt(np.pi) / 2) * _erf(h / np.maximum(L, 1e-9)), g * h)
    return np.where(h > 0, np.clip(1.0 + (np.asarray(t_s, float) + rise + PMP * h) / 2.0, 0.0, 1.0), 0.0)


def veg_feedback(sim):
    """The vegetation's feedbacks on the climate (climate.compute's veg),
    from the last update's vegetation (one climate step behind): bare land
    before land plants (vegetation.land_plants: the pioneers' arrival), an Earth-like average on the first
    update."""
    if not vegetation.land_plants(sim.flora, sim.t):
        return vegetation.bare(sim.grid.n)
    if sim.veg_frac is None:
        return None
    return vegetation.feedback(sim.veg_frac, sim.veg_lai)


def update_vegetation(sim, e):
    """The vegetation in equilibrium with the climate just computed
    (vegetation.model, the cheap variant: warm-started from the last
    update), and the plant groups that appear (vegetation.flora_update,
    on the niches measured at the last update, on Earth's calendar counted
    back from the run's end: vegetation.group_windows). Sets veg (ground
    cover, which slows erosion), npp, cover_w (the rooted cover of the same
    plants at the balance's CO2, which speeds weathering: PW-880, PW-1424 C), veg_frac,
    veg_lai, veg_type, tree_cover, flora and veg_niche. Before the land
    pioneers arrive the land is bare. During the spin-up it also sets
    cover_pot, the rooted cover of the potential vegetation (every group, the
    balance's CO2) the weathering reference is learnt with (global_temperature)."""
    p, g = sim.params, sim.grid
    n = g.n
    rng = np.random.default_rng([sim.seed, sim.step_no, 11])
    sim.flora = vegetation.flora_update(sim.flora, sim.t, climate_interval(sim), now_myr(p), sim.veg_niche, rng)
    land = is_land(e, grid=g)
    ice = np.where(land, sim.ice, 0.0)
    kind = np.where(land, sim.lake_kind, 0)
    lake = np.isin(kind, (hydrology.OPEN_LAKE, hydrology.CLOSED_LAKE))
    if sim.t < REF_FREEZE:  # the weathering reference's plants (global_temperature): every group, the balance's CO2
        pv = vegetation.model(g, e, sim.temp, sim.t_warm, sim.t_cold, sim.p_jul, sim.p_jan, p.tilt, sim.shade_jul,
                              sim.shade_jan, sim.flow, kind, lake, ice, nu0=sim.pot_frac, lai0=sim.pot_lai,
                              pco2=climate.PCO2_BALANCE, cheap=True, crown=False)
        sim.cover_pot = vegetation.rooted_cover(pv["eq"]["nu"])
        sim.pot_frac, sim.pot_lai = pv["eq"]["nu"].astype(np.float32), pv["pot"]["lai"].astype(np.float32)
    else:
        sim.cover_pot = sim.pot_frac = sim.pot_lai = None
    if not vegetation.land_plants(sim.flora, sim.t):
        sim.veg, sim.npp, sim.tree_cover, sim.cover_w = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
        sim.veg_type = np.where(land, vegetation.T["barren desert (sand or stone)"], 0).astype(np.uint8)
        sim.veg_niche = vegetation.bare_niches()
        return
    v = vegetation.model(g, e, sim.temp, sim.t_warm, sim.t_cold, sim.p_jul, sim.p_jan, p.tilt, sim.shade_jul,
                         sim.shade_jan, sim.flow, kind, lake, ice, nu0=sim.veg_frac, lai0=sim.veg_lai,
                         pco2=climate.pco2(sim.co2), unlocked=vegetation.unlocked_at(sim.flora, sim.t), cheap=True,
                         locked_potential=True, crown=False,  # (crown fire, PW-347: not yet in runs)
                         sky=(sim.cloud_jul, sim.cloud_jan))
    sim.veg_niche = vegetation.niches(v)
    # the same plants at the balance's CO2, for the weathering sink (PW-880; warm-started from its own last update)
    vw = vegetation.model(g, e, sim.temp, sim.t_warm, sim.t_cold, sim.p_jul, sim.p_jan, p.tilt, sim.shade_jul,
                          sim.shade_jan, sim.flow, kind, lake, ice, nu0=sim.wv_frac, lai0=sim.wv_lai,
                          pco2=climate.PCO2_BALANCE, unlocked=vegetation.unlocked_at(sim.flora, sim.t), cheap=True,
                          locked_potential=True, crown=False)
    sim.cover_w = vegetation.rooted_cover(vw["eq"]["nu"])
    sim.wv_frac, sim.wv_lai = vw["eq"]["nu"].astype(np.float32), vw["pot"]["lai"].astype(np.float32)
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
MARGIN_KM = 120.0  # km: a sheet's margin band (margin_band), melting as its edge: the width the rule was set at
# (one ring of L6's ~120 km cells, PW-366); the sub-cell ramp (icemass.margin_ramp, PW-460) is its honest successor
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


def ice_sheets(sim, land, bed, ground, old, sink=None, info=None, *, marine, reground=None, warm=0.0):
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
    and as long to grow into one.) The sheets' own carried air (icemass.air_mass,
    PW-336: a big sheet's cold summer air, carried onto its margins, its
    steepest feedback) settles with them (PW-1050): with reground (climate.compute's:
    the bare ground under another ice's carried air, the rest of the climate
    held), the ground is re-made under the passes' ice every AIR_EVERY passes
    while it moves and whenever it settles, until it settles having moved the
    ice's sea level by less than AIR_SEA_TOL since the last re-making, at most
    Params.ice_air_rounds times (info: "air_rounds", "air_capped" and the last
    "ground"). Without it, an onset took 5-10 updates and the climate's cadence
    decided how icy a planet got (docs/review/base-climate/ice-loop/). The rest
    of the climate (the sheet's albedo, the rain) follows at the next update, as
    CO2 does (computing it all again within the step whenever margins moved cost
    ~+80% of the climate at L5, mostly for a few margin cells shuffling).
    The old
    ice's height still counts: a big sheet keeps itself colder than bare
    ground would be and can outlast the climate that made it (two states,
    hysteresis), but not by tens of Myr of lag. warm (0..1): under the cycle's
    warm phase (icemass.balance's warm, that share of its states) instead of
    its average: the persistent ice (update_climate, PW-1142)."""
    g = sim.grid
    sink = ice_load(g, np.where(land, old, 0.0)) if sink is None else sink

    def settled(ice):  # the bed and its bare ground under this ice's load
        rise = sink - ice_load(g, ice)
        return bed + rise, tuple(t - climate.LAPSE * rise for t in ground)

    info = {} if info is None else info
    # (once per fixed point, on the bed the old ice pressed down, not every pass (PW-514: +39% wall
    # otherwise): what the sea takes from each coastal cell, and where a new cap can start (snow
    # outlasting the summer on bare ground); the passes' settling moves the bed by tens of m at most)
    kw = {"cost": coast_cost(sim, land, bed, marine), "start": _start(sim, land, ground, warm),
          "air": icemass.sheet_air(g, np.where(land, old, 0.0)), "warm": warm}  # (the air its ground was made under)
    ice = _ice_pass(sim, land, bed, ground, old, marine, **kw)
    seen = [np.asarray(old) > 0, ice > 0]
    cap = int(sim.params.ice_air_rounds) if reground is not None else 0
    info["passes"], info["air_rounds"], info["air_capped"] = 1, 0, False
    last, since = ice_sea_level(sim, land, old), 1
    for _ in range(ICE_PASSES):
        new = _ice_pass(sim, land, *settled(ice), ice, marine, **kw)
        info["passes"] += 1
        since += 1
        on = new > 0
        # (settled: as one of the last two passes but for a few margin cells shuffling; PW-514: with
        # coast_loss, exact repeats took ~21 passes per update against ~3.5 before)
        tol = max(2, int(PASS_TOL * on.sum()))
        still = (on != seen[-1]).sum() <= tol or (on != seen[-2]).sum() <= tol
        seen, ice = [seen[-1], on], new
        free = info["air_rounds"] < cap
        if still and not (free and abs(ice_sea_level(sim, land, ice) - last) >= AIR_SEA_TOL):
            info["air_capped"] = cap > 0 and not free
            break
        if free and (still or since >= AIR_EVERY):  # the ground under this ice's own air
            last, since = ice_sea_level(sim, land, ice), 0
            ground = reground(np.where(land, ice, 0.0))
            kw["start"], kw["air"] = _start(sim, land, ground, warm), icemass.sheet_air(g, np.where(land, ice, 0.0))
            info["air_rounds"] += 1
    info["air"] = kw["air"]
    if reground is not None:
        info["ground"] = ground
    return ice


AIR_EVERY = 8  # passes: the moving ice's carried air is re-made this often (and whenever the ice settles) ...
AIR_SEA_TOL = 0.5  # m: ... until the ice settles within this much sea level of its last re-making


def ice_sea_level(sim, land, ice):
    """The sea level change (m) that land ice (m) makes, by its volume over the sea's area (~0.9 g/cm3)."""
    vol = (np.where(land, ice, 0.0) / 1000.0).sum() * sim.cell_area * R_KM**2
    return -0.9 * vol / max((~land).sum() * sim.cell_area * R_KM**2, 1.0) * 1000.0


def margin_band(g, bare):
    """The cells within MARGIN_KM of bare land (bare: land without ice), as hops of the grid's cells, at least
    one: the band of a sheet whose snow and melt are its edge's (_ice_pass). In km, not cells (PW-725): one ring
    at any cell size made the band, which melts as the sheet's outermost 10 km, half as wide at L7 as at L6, so
    the same planet at the same dT grew ~2x the iced land and ~3x the ice at L7 from its first update
    (docs/review/base-climate/v1-finish-3/)."""
    rings = max(1, int(round(MARGIN_KM / (g.spacing * R_KM))))
    band = np.array(bare, dtype=np.bool_)  # (a copy: the rings alternate between two buffers)
    nxt = np.empty_like(band)
    for _ in range(rings):
        kernels.grow(band, g.nbr_off, g.nbr_idx, nxt)
        band, nxt = nxt, band
    return band


def _start(sim, land, ground, warm=0.0):
    """Where a new cap can start: snow outlasting the summer on bare ground,
    on average over the ice-age cycle's orbits (icemass.balance at no ice;
    warm: through its warm phase)."""
    smb0, _ = icemass.balance(sim.grid.lat, land, ground[0], ground[1], sim.p_jul, sim.p_jan, 0.0, 0.0,
                              tilt=sim.params.tilt, warm=warm)
    return smb0 > 0


def _ice_pass(sim, land, bed, ground, old, marine, cost=None, start=None, air=None, warm=0.0):
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
    start = _start(sim, land, ground, warm) if start is None else start
    # (the margin band, old ice within MARGIN_KM of bare land, is a slope from the bare edge up to the
    # interior: its snow and melt are its edge's, as the time zoom's margins (PW-366); at the cell-mean rise,
    # ~800 m at L6, its own thickness would keep it as cold as the interior and the sheet would creep a ring a pass)
    band = margin_band(g, land & (old <= 0))
    h = np.where(old > 0, np.where(band, np.minimum(old, ICE_EDGE_M), old), ICE_EDGE_M)
    air = icemass.sheet_air(g, old) if air is None else air  # (the sheets' own air in the ground: icemass.sheet_cover)
    cover = icemass.sheet_cover(g, old, air=air)
    # (as the time zoom's orbit_k, PW-114/PW-365: the air over bright ice brings the response of the land,
    # sea and ice around, each its own share of the land's: the sea INSOL_SEA, bright ice ICE_ABSORB; before,
    # the open sea counted as fully absorbing land, and coastal ice felt ~2x the time zoom's orbital swing)
    bright = np.where(land, np.clip(old / icemass.SNOW_H, 0, 1), 0.0)
    own = np.where(land, 1.0, icemass.INSOL_SEA)
    mix = climate.smooth_big(g, own * (1 - bright * (1 - icemass.ICE_ABSORB)), icemass.ABSORB_KM)
    absorb = (1 - bright) + bright * mix
    bare_k = float(getattr(sim.params, "ice_bare_absorb", 0.0))
    if bare_k > 0:  # (a melting surface is bare ice: it absorbs bare_k of the change, its warmest month's melting
        # share of the time, icemass.BARE_ABSORB, PW-1142)
        melt = 1.0 - icemass.cold_share(t_warm - climate.LAPSE * h)
        absorb = absorb + melt * np.maximum(bare_k - absorb, 0.0)
    smb, _ = icemass.balance(lat, land, t_warm, t_cold, sim.p_jul, sim.p_jan, h, cover, tilt=tilt, absorb=absorb,
                             warm=warm)
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
    _, _, t_ice = climate.ice_surface(t_warm, t_cold, temp, h, icemass.sheet_cover(g, h, air=air), lat, sim.p_jul,
                                      sim.p_jan)
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
    k_m = 2 * ICE_TAU / (RHO_ICE * GRAV) * g.spacing * R_KM * 1000.0  # m2 per hop

    def rise(d):
        # the profile's mean over the cell, which spans d..d+1 hops in from the edge (PW-366: its inner
        # edge's value left a margin cell ~340 m at L6, the profile's mean over it ~740 m at 50 kPa)
        d = np.asarray(d, float)
        dd = np.where(np.isfinite(d), d, 0.0)  # (cells no margin has reached yet: inf)
        return np.where(np.isfinite(d), (2.0 / 3.0) * np.sqrt(k_m) * ((dd + 1.0) ** 1.5 - dd ** 1.5), np.inf)

    edge = np.empty(n, np.bool_)
    kernels.has_unset_nbr(np.ascontiguousarray(iced, dtype=np.bool_), off, idx, edge)
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
    k_m = 2 * ICE_TAU / (RHO_ICE * GRAV) * g.spacing * R_KM * 1000.0
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
    p, g, dt = sim.params, sim.grid, sim.dt_now
    t, cover, x, cont, rock = col.t, col.cover, col.x, col.cont, col.rock
    # Glaciers grind their beds hard where they slide on meltwater (the
    # 'glacial buzzsaw' that keeps ranges from growing much above the
    # snowline); polar ice frozen to its bed protects it instead. Whether
    # the bed is thawed: the time zoom's rule (Robin's steady column,
    # bed_thawed), on the ice surface's annual mean, the ice's thickness and
    # the snow falling on it (PW-872; was warm month > -8 C, a threshold set
    # on the bare ground's temperatures before PW-277).
    wet = bed_thawed(sim.ice, sim.temp, sim.precip)
    k_mult = np.where(sim.ice > 0, 0.3 + (p.glacial_erosion - 0.3) * wet, 1.0)
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
    col.t, col.cover, x[:, MIX], sim.removed, dep, sim.flow, sim.down, lk, crept = surface.erode(
        g, elevation(t, sim.w_age, cont, rock, sim.datum(), sed), t, cover, x[:, MIX],
        rock, cont, sim.precip, sim.runoff, sim.aet, sim.lake_evap, dt, p.hillslope, p.erosion_timescale,
        p.erosion_height, p.incision, sim.scale, iso, k_mult, p.alluvial, p.fan_km, iso_dep, valley=x[:, VALLEY],
        base_rise=max(-float(sim.sea_ice), 0.0), rise=p.rise > 0, slope_k=p.slope_k)
    sim.book("erosion", t0, col.t, cont)
    # the valleys rivers to the sea run in now (graded to the river they
    # carry: a shrunken river silts up a valley too big for it), and where
    # no such river runs any more the old ones, filling in slowly from their
    # slopes (hydrology.VALLEY_MYR); they ride on with the rock
    x[:, VALLEY] = np.where(lk["incised"] > 0, lk["incised"], x[:, VALLEY] * np.exp(-dt / hydrology.VALLEY_MYR))
    # the basement comes up by what's worn off net (the strata: in sediments())
    col.eroded_cover = np.clip(sim.removed, 0, np.maximum(cover, 0)) + crept  # (+ the sea floor's creep, PW-950)
    col.rec[:, record.EXHUMED] = np.maximum(col.rec[:, record.EXHUMED] + sim.removed - dep, 0)
    # what bare ground lost, for the weathering sink: masked by the ice this erosion ran under (the next
    # step's sink sees the ice after a climate update; ground the ice left in it counted its glacial
    # erosion, the 3x buzzsaw, as weathering, PW-438). Kept per step of dt (the run's step, which the
    # sink's references are learnt in): scaled here, by the length of the step it was eroded in, not where
    # the sink reads it (the next step's global_temperature runs before this step's erosion, so the first
    # short finish-window step read a 2 Myr step's erosion x dt / dt_now = 4: a 4x sink for a step, lane 67)
    sim.weathered = np.where(sim.ice > 0, 0.0, sim.removed) * (sim.dt / dt)
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
    p, g, dt = sim.params, sim.grid, sim.dt_now
    x, cover = col.x, col.cover
    e = elevation(col.t, sim.w_age, col.cont, col.rock, sim.datum(), sediment_km(col.cover, x))
    land = is_land(e, grid=g)
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


REEF_BUILDERS_MA = (545.0, 520.0)  # Ma before now: skeletal reef builders (archaeocyaths, then corals,
# stromatoporoids) arrive within this window, per seed (Cambrian; Wood 1999; Kiessling 2009), on Earth's calendar
# counted back from the run's end like the plant groups (PW-807)
MICROBIAL_REEF = 0.1  # before them: microbial carbonate (stromatolites, thrombolites) builds up at this share of
# reef_rate (Shark Bay's stromatolites accrete ~0.3-0.5 mm/yr, against a few mm/yr for Holocene coral reefs:
# Montaggioni 2005). Crude: it only sets how readily a pre-Cambrian sea's carbonate keeps up with subsidence


def reef_builders_t(sim) -> float:
    """Run time (Myr) from which skeletal reef builders exist: a per-seed draw in REEF_BUILDERS_MA before now."""
    u = np.random.default_rng([sim.seed, 13]).random()
    ma = REEF_BUILDERS_MA[0] + u * (REEF_BUILDERS_MA[1] - REEF_BUILDERS_MA[0])
    return now_myr(sim.params) - ma


def reefs(sim, col, dep, chem):
    """Reefs: in warm, clear, shallow sea, corals and other carbonate
    makers build up to just below sea level, fast enough to outpace any
    subsidence. A volcanic island that sinks with its ageing sea floor
    becomes an atoll; carried out of the tropics, the reef dies and it
    drowns into a flat-topped seamount (the Darwin point, ~30 deg).
    Muddy water from big rivers stops them (no reefs off the Amazon).
    The chemical sediments (chem: km of evaporite and of coal) join the
    crust here too. All go on top of the strata. Before skeletal reef
    builders exist (reef_builders_t), microbial carbonate builds up at
    MICROBIAL_REEF of the rate."""
    p, dt = sim.params, sim.dt_now
    evap, coal = chem
    chem = evap + coal
    cont, rock = col.cont, col.rock
    sed = sediment_km(col.cover, col.x)
    e = elevation(col.t, sim.w_age, cont, rock, sim.datum(), sed)
    reef = (e < -5) & (e > -1500) & (sim.sst >= p.reef_temp) & (dep * 1000 < p.reef_mud * dt)
    rate = p.reef_rate * (1.0 if sim.t >= reef_builders_t(sim) - 1e-9 else MICROBIAL_REEF)
    grow = np.minimum(rate * np.exp((e + 5) / 150.0) * dt, -5 - e) * reef  # m of elevation
    carb = grow / sediment_iso(cont, rock, sed)
    col.t, col.cover = col.t + carb, col.cover + carb
    col.x[:, CARB] += carb
    col.t, col.cover = col.t + chem, col.cover + chem
    sim.book("reef+chem", 0, carb + chem, cont)
    n = sim.grid.n
    record.add_top(col.rec, col.lith, evap, np.full(n, EVAPORITE, np.uint8), sim.t)
    record.add_top(col.rec, col.lith, coal, np.full(n, COAL_ROCK, np.uint8), sim.t)
    record.add_top(col.rec, col.lith, carb, np.full(n, LIMESTONE, np.uint8), sim.t)
