"""Simulation parameters (stored in each run's run.json)."""

from __future__ import annotations

from dataclasses import dataclass, fields


@dataclass
class Params:
    n_plates: int = 12
    start: str = "supercontinent"  # or "scattered"
    # starting share of the surface that's continental crust, and the level
    # the thermostat on island-arc growth holds it near (Earth: ~0.41)
    continental_fraction: float = 0.4
    # Growing continents: start with this share instead (< 0: same as
    # continental_fraction) and let the thermostats raise it toward
    # continental_fraction over ~continental_growth Myr (e-folding). With a
    # hot early mantle (heat_start ~2) this gives a mostly-ocean young world
    # whose land emerges over the first Gyr, as Earth's probably did.
    continental_start: float = -1.0
    continental_growth: float = 700.0
    continental_thickness: float = 35.0  # km: the mean the volume thermostat aims for
    # forces (arbitrary units; mobility converts torque to rad/Myr)
    slab_pull: float = 1.0
    # the mantle's resistance to a slab sinking through it, per cm/yr of
    # convergence: an 80 Myr slab alone sinks at slab_pull / slab_drag cm/yr
    # (its terminal speed; 0: no resistance)
    slab_drag: float = 0.1
    ridge_push: float = 0.15
    collision_drag: float = 1.2
    mantle_noise: float = 0.2  # the random part of the basal drag (meandering)
    mantle_timescale: float = 60.0  # Myr: how fast the wandering drag term changes
    # the mantle under the plates (see mantle.py): a temperature anomaly
    # built by cold slabs and warmed under continents, whose flow drags the
    # plates from warm toward cold
    mantle_drag: float = 0.6  # basal traction per unit of temperature gradient
    mantle_memory: float = 200.0  # Myr: how long the mantle remembers (0: no mantle field)
    mantle_scale_km: float = 2500.0  # only features this big and bigger
    slab_cold: float = 0.002  # cooling per Myr from a trench (per unit length, x conv/5 cm/yr x age/80 Myr)
    insulation: float = 0.04  # warming per Myr under a continent that has sat still ~100 Myr
    mantle_eddies: float = 0.3  # rms of the smaller, unresolved convection (random; changes over mantle_timescale)
    velocity_timescale: float = 15.0  # Myr: smoothing on velocity changes (plate inertia, in effect)
    continental_keel: float = 1.5  # extra drag per continental cell
    mobility: float = 0.008
    max_speed: float = 18.0  # cm/yr
    # crust: arcs add new crust above subducting slabs (km/Myr per cm/yr of
    # convergence, before the thermostat); collisions stack crust (see
    # plate_kernels.resolve), which then flows sideways where it's very thick
    arc_growth: float = 0.03
    # per Myr between level-5 neighbours, times (x + x^3), x = (crust - 40 km)/10 km.
    # (At 0.03 the stability clamp in plate_kernels.crust_flow always bound, so plateaus
    # flattened at the numerical limit: ~1 km in 4 Myr from flow alone.)
    crust_flow: float = 0.0006
    # PW-1497 (lane 275, scout9.md): post-orogenic collapse. Crust not squeezed for collapse_delay Myr flows
    # (1 + collapse) x faster (crust.flow_and_orogeny). 0: off. On since lane 275b (30: dead high ground gone 30-60 Myr after its last squeeze).
    collapse: float = 30.0
    collapse_delay: float = 20.0
    # PW-1693 (lane 292, l7-high-ground.md section 4): a dead belt at a continent's edge also spreads into the same
    # plate's neighbouring ocean cells (not at a trench), at collapse_margin x its collapsed rate; a cell filled to
    # BECOMES_CONT_KM becomes thin extended continent, so collapse gives back area shortening took. 0: off.
    collapse_margin: float = 0.0
    # PW-1703 (lane 296, l7-high-ground.md section 8): the thickness that seaward collapse (collapse_margin) runs down
    # to: crust flows across a margin edge where the belt side is over this many km (40: as inland, crust_flow's
    # stop; 35: normal continental crust, isostasy.CONT_KM, where the belt's excess potential energy is gone).
    collapse_margin_km: float = 40.0
    # PW-1287 A (lane 292): continental crust below the sea floats water-loaded (isostasy.elevation's wet): 0 air-loaded
    # (as before), 1 water-loaded (drowned continent 1.46x its air-loaded depth). Simulation.wet.
    water_loaded: float = 0.0
    # tectonic subsidence beyond local isostasy (isostasy.subsidence, PW-054):
    # share of a mountain belt's spread root that drags the plain beside it
    # down (flexural foreland / intermontane basins), and the thermal sag of
    # stretched lithosphere (km after infinite stretching, air-loaded) with
    # its cooling time
    # (0.15 is a calibrated basin-making share, picked on one L7 seed's
    # closed-basin count, not derived: the sound two-sided flexure with alpha
    # from an elastic thickness is unstable on cells as wide as alpha, PW-284)
    flexure: float = 0.15
    rift_sag: float = 2.2
    sag_time: float = 63.0
    # surface (see surface.py): erosion, rivers, sediment, climate
    # km/Myr: ground wears down this x its mean downhill slope (m/km) in m/Myr (PW-282: was 100 km^2/Myr x
    # drop / d^2, which doubled per grid level; this is the same wear at L6, d = 120.32 km)
    hillslope: float = 3.3245
    erosion_timescale: float = 400.0  # Myr e-folding of low ground above base level (weathering)...
    erosion_height: float = 2000.0  # m: ...which gets (1 + (h/this)^2) times faster higher up
    stretching: float = 0.01  # per Myr per cm/yr of opening: continental crust thins near rifts
    # PW-1497 option A (scout 237): share of the overriding continent's own advance toward an ocean-continent trench
    # (cm/yr, at most the convergence) taken up by contracting its edge (crust.andean_contraction; Medvedev et al.
    # 2006: the central Andes shorten 1-1.75 of the foreland's ~3 cm/yr). 0: off. andean_steer: the area thermostat's
    # factor steers it, as it steers subduction erosion (both are the trench's sinks of continental area).
    andean_shortening: float = 0.1
    andean_steer: float = 0.0
    subduction_erosion: float = 0.05  # km/Myr per cm/yr: forearc crust ground away at ocean-continent trenches (over a crust.FOREARC_KM wide forearc)
    accretion: float = 0.5  # share of the sediment arriving at a trench scraped onto the overriding plate
    rift_margin_km: float = 18.0  # ...and the crust it loses floors the opening rift at this thickness (0: lost)
    # km: necking zone of a rifted margin (crust.necking, PW-950): new rift floor next to continent is laid as crust
    # as thick as the edge, paid for by thinning the continent within this distance (0: off, rings from the pool only)
    neck_km: float = 0.0
    incision: float = 0.0064  # river cutting, per Myr per sqrt(flow) (flow of runoff, ~40% of the rain)
    # Myr between climate (rain, ice, sea level) updates before the finish window: a ramp (PW-247, owner 10-29),
    # climate_every in the last climate_ramp Myr before it, twice that up to 10x as far back, and so on up to
    # climate_every_max (4 / 8 Myr: the last 30 Myr, earlier; earth.climate_cadence; a 16 Myr step back from 300 Myr
    # before the window ran colder, with more icebox excursions: docs/review/speed/README.md), and half
    # climate_every (2 Myr, every step) in the last climate_ramp_fine Myr (0: off), so the finished world's last
    # shaping before the window is at the finest cadence (owner 10-29). A keyframe between updates (every 4 Myr)
    # shows the last update's climate, as the run's erosion, weathering and ice saw it.
    climate_every: float = 4.0
    climate_every_max: float = 8.0
    climate_ramp: float = 30.0
    climate_ramp_fine: float = 10.0
    # The adaptive cadence (PW-247): an update comes early, at a step at least, once the global temperature offset
    # dT moved this many C since the last (CO2, the star and the ice's albedo all reach the climate through it; the
    # land's layout and height move steadily, ~4% of the surface and ~170 m a 4 Myr interval at L6, so they set
    # the ramp, not a trigger: docs/review/speed/README.md). The ramp's cadence is the longest interval. 0: off.
    climate_adapt_dT: float = 1.0
    # grid level the climate is computed on before the finish window, when the run's own is finer (PW-247: an L7
    # run's spin-up climate on L6, nest.climate_coarse; ice and plants stay on the run's grid). The finish window,
    # and so every world's own climate, is at the run's level. 0: always the run's level.
    climate_level: int = 6
    # The finish window (PW-866, owner 2026-10-25): the run's last finish_window Myr step finish_step Myr at a
    # time, each with a climate update and a keyframe, so the finished world can be taken at the latest
    # human-habitable one of those candidate moments (highlights.representative_time). 0: none.
    finish_window: float = 10.0
    # Require permanent ice (owner D19, PW-1164): the finish moment must hold permanent ice (highlights.has_permanent_ice);
    # `planet make` re-rolls the seed when no moment of the window does. Off: no behaviour change.
    finish_require_ice: bool = False
    finish_step: float = 0.5
    # climate (see earth.global_temperature)
    tilt: float = 23.4  # deg: axial tilt, sets how strong the seasons are
    climate_offset: float = 0.0  # C: shifts the whole history warmer (+) or colder (-)
    # The star brightens as it ages (earth.star_forcing, PW-809/815): a Sun-like star on Gough's (1981) curve,
    # anchored so the run's END is now (owner 2026-10-24): a run of run_end Myr spans the star's ages
    # 4570 - run_end .. 4570 Myr, so it starts under a fainter young star (-8% at 1 Gyr, -15% at 2 Gyr) and ends
    # under today's Sun. The forcing is counted against today's Sun (negative early, 0 at the end; the climate's
    # dT = 0 is Earth under it); the carbon cycle answers the faint start with high CO2 (earth.start_carbon).
    # star_brightening: times the Sun's rate (1: Gough's Sun; < 1 a slower-evolving, lower-mass star; 0: a star
    # that doesn't change).
    star_brightening: float = 1.0
    # Myr: the run ends this far after today's Sun (> 0: a look into the future, e.g. ~600 Myr ahead of the
    # CO2 collapse; an extension of a run keeps its anchor, so the extended part is this offset)
    star_now_offset_myr: float = 0.0
    # Myr: the run's end, the moment that is "now" (less star_now_offset_myr) for the star and for the plant
    # groups' calendar (vegetation.group_windows; earth.now_myr). 0: the run's length (timeline.simulate sets
    # it; a direct Simulation caller should, else 1000, earth.RUN_END_DEFAULT). An extension keeps it. A run
    # longer than its star's age is refused (earth.check_star).
    run_end: float = 0.0
    # A CONTROL, NOT PHYSICS (PW-791; earth.star_control): the world-builder's star thermostat, opt-in (off in every
    # preset, docs/overview.md). It dims or brightens the star slowly when the planet's running icehouse share (the share of the last
    # ~star_window Myr with land ice holding >= 20 m of sea level) leaves star_ice_band, so a run stays in a
    # "life can live here" state (neither never-ice nor icebox nor hellhole). It moves the star's output only;
    # CO2 stays the carbon cycle's outcome (a dimmer star lets the weathering thermostat keep more of it).
    # Bounded to +-star_control_max of the star's luminosity; it acts from star_control_from Myr.
    star_thermostat: bool = False
    star_ice_lo: float = 0.10  # running icehouse share below which the star dims ...
    star_ice_hi: float = 0.35  # ... and above which it brightens (Earth's Phanerozoic: ~0.25-0.3)
    star_window: float = 100.0  # Myr: the running share's e-folding memory
    star_gain: float = 0.2  # C of forcing per Myr per unit of share outside the band (0 share: -2 C per 100 Myr)
    star_control_max: float = 0.04  # +- share of the star's luminosity (+-7.7 C of forcing at co2_sensitivity 3)
    star_control_from: float = 200.0  # Myr: no control before (the made-up start settles)
    # C: size of the slow random wander of the carbon cycle (PW-819: noise on the carbon source, not on the
    # temperature), as the warming it gives at the balance (earth.drift_source: 1 C is 0.116 e-folds of the
    # source). It stands only for the source terms the model lacks; the ridges' and arcs' outgassing is explicit
    # (its own sd(ln) 0.2-0.45 after 300 Myr, already GEOCARB's f_G spread; the plumes' since PW-875). The lacking terms, sized from the
    # literature (docs/review/base-climate/v1-finish-13/README.md), add in quadrature to sd(ln) ~0.10:
    #  - net organic burial (organic C buried minus weathered and degassed): it is O2's source, so the O2
    #    record bounds it. GEOCARBSULF's Phanerozoic O2 (~15-30%, Berner 2006, 2009; +-30% envelope, Royer et
    #    al. 2014) is +-~7e18 mol of 38e18 (Berner 2004); held over the drift's 40 Myr that is ~0.18e18 mol/Myr,
    #    ~3% of the silicate weathering flux (~6.7e18 mol/Myr, Berner & Kothavala 2001); x2 for pyrite burial
    #    offsetting O2 (Berner & Raiswell 1983): sd(ln) ~0.05. (Royer et al. 2014: the carbonate d13C, which
    #    drives the organic burial, is among the top O2 drivers and not among the CO2 ones.)
    #  - ocean chemistry: carbonate on the subducting plates (GEOCARB's f_C, 0.75 -> 1 as pelagic carbonate
    #    spread, Wilkinson & Walker 1989; Berner 2004), a ln range of 0.29: sd(ln) ~0.08.
    # 0.8 C is sd(ln) 0.093. Was 3 C (sd(ln) ~0.36), which also counted the outgassing the model has explicitly.
    # Not sized to any end-pCO2 band...
    climate_drift: float = 0.8
    climate_drift_time: float = 40.0  # Myr: ...and how long it takes to forget
    # x pre-industrial: methane's lifetime (so its level) under the low-oxygen air (earth.ghg_conc, PW-859): between
    # the Great and the Neoproterozoic Oxygenation Events (~2.1-0.8 Ga) CH4 stood at ~10-300 ppm against today's
    # pre-industrial 0.7 (Pavlov et al. 2003, Geology 31: 87: 100-300 ppm; Roberson et al. 2011, Geobiology 9: 313;
    # Olson et al. 2016, PNAS 113: 11447: <~10 ppm): ~30 ppm, 43x, the middle (~4 W/m2). Before the GOE ~1000 ppm
    # (Pavlov et al. 2000; Kasting 2005; Haqq-Misra et al. 2008), 1400x (~8 W/m2)
    methane_proterozoic: float = 43.0
    methane_archean: float = 1400.0
    co2_sensitivity: float = 3.0  # C per doubling of the CO2 stock (pCO2): Earth's equilibrium sensitivity, ~3
    # (IPCC AR6 2.5-4; the land ice's albedo is its own term); 3 C per e-fold before PW-646 (2.1 per doubling)
    ice_albedo: float = 1.5  # C of cooling per 3% of the planet under land ice (Earth today; dT counts it
    # from Earth's ice, so an ice-free planet is ~1.4 C warmer) ...
    ice_albedo_max: float = 3.0  # ... levelling off toward this many C (Earth's LGM ice sheets: ~2.5-3)
    # times the sheets' carried air is re-made within a climate update's ice passes (earth.ice_sheets, PW-1050):
    # the ice settles with its own air, at most this many re-makings (0: off, the air follows at the next update)
    ice_air_rounds: float = 8.0
    # the ice-age cycle's warm phase (PW-1142): a sheet carried from a cold era outlasts a climate update only
    # where it outlasts the cycle's warm phase (the persistent ice, under each cell's balance averaged over this
    # share of the orbital states, its least first: 0.125 the warmest alone, 0.5 the warm half; seeds the
    # time-mean sheets; 0: off, the time-mean sheets carry themselves) ...
    ice_warm_persist: float = 0.125
    # ... and a melting surface (bare ice) absorbs this share of an insolation change (icemass.BARE_ABSORB,
    # Wehrle et al. 2021's bare-ice albedo; 0: off, all ice as bright as snow, icemass.ICE_ABSORB)
    ice_bare_absorb: float = 1.0 - 0.565
    glacial_erosion: float = 3.0  # erosion multiplier under sliding (temperate) glaciers
    # rocks
    craton_age: float = 1500.0  # Myr: untouched continental crust this old becomes craton
    evaporite_rate: float = 0.02  # km/Myr of salt in a hot, dry closed basin
    coal_rate: float = 0.003  # km/Myr of coal in a warm, wet, low swamp
    alluvial: float = 3000.0  # km of gentle river course over which ~63% of its load settles on land
    fan_km: float = 1000.0  # km of deep sea floor over which ~63% of the load that passes the shelf settles
    rise: float = 0.0  # 1: sediment past the shelf's brink settles first at the slope's foot (continental rise, PW-950; 0: off)
    # km2/Myr: the sea floor's sediment cover creeps down its slope, flux = K grad(elevation), K falling with
    # depth as K d_ref / (d + d_ref) (clinoform diffusion, PW-950: Mitchell & Huthnance 2008; Jordan &
    # Flemings 1991's 100-1000 m2/yr; docs/review/tectonics/margin/diagnosis-foreset.md; 0: off)
    slope_k: float = 0.0
    # km: sediment buried deeper than this is cooked (~500 C) into metamorphic
    # rock and joins the basement (Earth's thickest piles: ~20 km)
    metamorphic_depth: float = 18.0
    # hotspots: mantle plumes fixed in the mantle; plates slide over them
    hotspots: int = 10  # typical number alive at once
    hotspot_life: float = 120.0  # Myr, mean
    hotspot_rate: float = 4.0  # km/Myr of crust added at the centre (a quarter of that under continents)
    hotspot_at_ridges: float = 0.6  # share of new plumes that rise under a ridge or rift
    # a plume opens a new vent every this x the plate's flexural wavelength of
    # plate motion (volcanism.vent_gap: Hawaii ~100 km)
    vent_spacing: float = 1.5
    vent_erosion: float = 10.0  # Myr e-folding of a volcano's height above the sea, at 1500 mm/yr of rain
    volcano_life: float = 8.0  # Myr an arc volcano (or its replacement nearby) stays active
    volcano_spacing: float = 120.0  # km: at most one active volcano per this much arc
    volcano_km3: float = 2000.0  # km3 of crust a new arc volcano adds (to its cell), give or take 50%
    swell_time: float = 12.0  # Myr: the swell decays behind a plume as the plate carries it off
    # reefs: carbonate builds shallow sea floor up to sea level where it's warm and clear
    reef_temp: float = 23.5  # C, annual mean sea surface (reefs reach ~30 deg latitude)
    reef_rate: float = 200.0  # m/Myr of build-up near the surface (much less deeper: light-limited)
    reef_mud: float = 10.0  # m/Myr of river mud deposited is enough to smother reefs
    # mantle heat at the start relative to the end state (1 = steady, today's Earth);
    # scales plume numbers, arc melting and (as sqrt) plate speed. See earth.heat
    heat_start: float = 1.0
    heat_halflife: float = 600.0  # Myr
    ridge_time: float = 30.0  # Myr: the ocean basins' volume (sea level) follows the sea floor's mean depth over this
    hot_sea: float = 600.0  # m of extra sea level per unit of extra mantle heat
    # events
    suture_after: float = 30.0  # Myr of continental collision before plates can weld...
    suture_closing: float = 2.0  # ...once they've (nearly) stopped converging, cm/yr
    suture_max: float = 150.0  # Myr: weld anyway after this long
    rift_timescale: float = 130.0  # Myr: sets the rift hazard for a given excess stress
    stress_min_plate: float = 0.05  # plates larger than this (any crust) can break under stress
    rift_stress: float = 2.0  # cm/yr: how hard the halves must pull apart before it can break
    warm_rift: float = 0.7  # warm mantle weakens the plate above it: strength / (1 + this x anomaly) (events.strength)
    # a rift never cuts off a piece with less continent than this share of
    # the surface (but may split off purely oceanic plate): continents break
    # into a few big blocks, along their weak zones (events.strength)
    rift_min_piece: float = 0.03
    # plume-centred triple junctions (events.triple_rift): a new plume head under a continent on a plate of at
    # least stress_min_plate cracks it along three arms with these odds (/ the rock's strength there), and
    # each arm fails (an aulacogen) with aulacogen_odds
    triple_odds: float = 0.5
    aulacogen_odds: float = 0.3
    settle_time: float = 30.0  # Myr after a plate splits off before it can break under stress (events.split)
    margin_age: float = 120.0  # Myr: ocean floor older than this at a passive margin may start subducting
    max_plates: int = 30

    @classmethod
    def from_stored(cls, d: dict) -> "Params":
        """Params from a stored run.json. A run whose params differ from this
        code's (removed or added since) was made by older code: it raises,
        asking for the run to be deleted and re-run (no backward
        compatibility, PW-1031)."""
        known = {f.name for f in fields(cls)}
        unknown, missing = sorted(set(d) - known), sorted(known - set(d))
        if unknown or missing:
            raise ValueError("this run was made by older code (params "
                             + "; ".join(([f"no longer known: {unknown}"] if unknown else [])
                                         + ([f"missing: {missing}"] if missing else []))
                             + "); delete it and re-run")
        return cls(**d)
