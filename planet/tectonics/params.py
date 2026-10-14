"""Simulation parameters (stored in each run's run.json)."""

from __future__ import annotations

import warnings
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
    continental_thickness: float = 37.0  # km: the mean the volume thermostat aims for
    # forces (arbitrary units; mobility converts torque to rad/Myr)
    slab_pull: float = 1.0
    ridge_push: float = 0.15
    collision_drag: float = 1.2
    mantle_noise: float = 0.35
    mantle_timescale: float = 60.0  # Myr: how fast the wandering drag term changes
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
    # surface (see surface.py): erosion, rivers, sediment, climate
    hillslope: float = 100.0  # km^2/Myr: wearing-down of ground standing above its neighbours
    erosion_timescale: float = 400.0  # Myr e-folding of low ground above base level (weathering)...
    erosion_height: float = 2000.0  # m: ...which gets (1 + (h/this)^2) times faster higher up
    stretching: float = 0.01  # per Myr per cm/yr of opening: continental crust thins near rifts
    subduction_erosion: float = 0.05  # km/Myr per cm/yr: forearc crust ground away at ocean-continent trenches
    accretion: float = 0.5  # share of the sediment arriving at a trench scraped onto the overriding plate
    rift_margin_km: float = 18.0  # ...and the crust it loses floors the opening rift at this thickness (0: lost)
    incision: float = 0.0064  # river cutting, per Myr per sqrt(flow) (flow of runoff, ~40% of the rain)
    climate_every: float = 8.0  # Myr between climate (rain, ice, sea level) updates
    # climate (see earth.global_temperature)
    tilt: float = 23.4  # deg: axial tilt, sets how strong the seasons are
    climate_offset: float = 0.0  # C: shifts the whole history warmer (+) or colder (-)
    climate_drift: float = 3.0  # C: size of the slow random wander in global temperature...
    climate_drift_time: float = 40.0  # Myr: ...and how long it takes to forget
    co2_sensitivity: float = 3.0  # C per e-fold of volcanic CO2 output relative to weathering
    ice_albedo: float = 1.5  # C of cooling per 3% of the planet under land ice (Earth today)
    ice_summer_temp: float = 1.0  # C: land with warmest month below this holds ice
    glacial_erosion: float = 3.0  # erosion multiplier under sliding (temperate) glaciers
    # rocks
    plants_from: float = 0.0  # Myr: land plants exist from this time on (slow erosion, make coal)
    craton_age: float = 1500.0  # Myr: untouched continental crust this old becomes craton
    evaporite_rate: float = 0.02  # km/Myr of salt in a hot, dry closed basin
    coal_rate: float = 0.003  # km/Myr of coal in a warm, wet, low swamp
    alluvial: float = 3000.0  # km of gentle river course over which ~63% of its load settles on land
    fan_km: float = 1000.0  # km of deep sea floor over which ~63% of the load that passes the shelf settles
    # km: sediment buried deeper than this is cooked (~500 C) into metamorphic
    # rock and joins the basement (Earth's thickest piles: ~20 km)
    metamorphic_depth: float = 18.0
    # hotspots: mantle plumes fixed in the mantle; plates slide over them
    hotspots: int = 10  # typical number alive at once
    hotspot_life: float = 120.0  # Myr, mean
    hotspot_rate: float = 4.0  # km/Myr of crust added at the centre (a quarter of that under continents)
    hotspot_at_ridges: float = 0.6  # share of new plumes that rise under a ridge or rift
    volcano_life: float = 8.0  # Myr an arc volcano (or its replacement nearby) stays active
    volcano_spacing: float = 350.0  # km: at most one shown volcano per this much arc
    volcano_km: float = 2.0  # km of crust a new volcano adds to its cell (~300 m on land)
    swell_time: float = 12.0  # Myr: the swell decays behind a plume as the plate carries it off
    # reefs: carbonate builds shallow sea floor up to sea level where it's warm and clear
    reef_temp: float = 23.5  # C, annual mean sea surface (reefs reach ~30 deg latitude)
    reef_rate: float = 200.0  # m/Myr of build-up near the surface (much less deeper: light-limited)
    reef_mud: float = 10.0  # m/Myr of river mud deposited is enough to smother reefs
    # mantle heat at the start relative to the end state (1 = steady, today's Earth);
    # scales plume numbers, arc melting and (as sqrt) plate speed. See earth.heat
    heat_start: float = 1.0
    heat_halflife: float = 600.0  # Myr
    hot_sea: float = 600.0  # m of extra sea level per unit of extra mantle heat
    # events
    suture_after: float = 30.0  # Myr of continental collision before plates can weld...
    suture_closing: float = 2.0  # ...once they've (nearly) stopped converging, cm/yr
    suture_max: float = 150.0  # Myr: weld anyway after this long
    rift_timescale: float = 130.0  # Myr: mean time before a big continental plate rifts
    rift_min_continent: float = 0.07  # fraction of surface
    stress_min_plate: float = 0.05  # plates larger than this (any crust) can break under stress
    rift_stress: float = 3.0  # cm/yr: how hard the halves must pull apart before it can break
    big_plate: float = 0.2  # plates bigger than this fraction of the surface break up more readily
    settle_time: float = 30.0  # Myr after forming before a plate can break under stress
    margin_age: float = 120.0  # Myr: ocean floor older than this at a passive margin may start subducting
    max_plates: int = 30

    @classmethod
    def from_stored(cls, d: dict) -> "Params":
        """Params from a stored run.json. Keys this code no longer knows
        (removed params) are dropped with a warning; params added since the
        run was made take today's defaults, so such a run may not replay
        exactly (see timeline.slice_world's keyframe check)."""
        known = {f.name for f in fields(cls)}
        unknown = sorted(set(d) - known)
        if unknown:
            warnings.warn(f"ignoring params this code doesn't know: {unknown}", stacklevel=2)
        return cls(**{k: v for k, v in d.items() if k in known})
