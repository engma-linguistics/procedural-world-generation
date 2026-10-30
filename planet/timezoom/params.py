"""Time zoom constants, the per-frame layer layout and the knobs (TZParams)."""

from __future__ import annotations

from dataclasses import dataclass

from .. import icemass as M
from .. import store as S
from ..geo import R_KM
from ..tectonics.isostasy import FLEX_KM, ICE_SINK

R_M = R_KM * 1000.0
RHO_I, RHO_W = M.RHO_I, M.RHO_W

LAYERS = {  # per frame: store.LAYERS names and encodings, as runs
    "elevation": S.LAYERS["elevation"],  # m, surface (ice included) above that frame's sea level
    # 1 m steps in 16 bits (domes on big polar continents pass 5.1 km), so a finished world (finish.py)
    # gets the bed back from any frame as elevation - ice to a metre
    "ice": {**S.LAYERS["ice"], "dtype": "<u2", "scale": 1},
    "temperature": S.LAYERS["temperature"],  # C, annual mean
    "climate": S.LAYERS["climate"],  # climate.KOPPEN id
    # the glacial imprint so far (PW-037; the elevation already has it): m of bed eroded, m of till dropped
    "glacial_erosion": S.LAYERS["glacial_erosion"],
    "glacial_till": S.LAYERS["glacial_till"],
    "glacial_outwash": S.LAYERS["glacial_outwash"],
    "glacial_loess": S.LAYERS["glacial_loess"],
    # the tree cover of the migrating plants (plants.py, PW-213), under the ice and sea of its frame; only with veg on
    "tree_cover": S.LAYERS["tree_cover"],
}
STATIC = ("plate", "crust", "crust_age", "plate_boundary")  # stored once

@dataclass
class TZParams:
    """Knobs (--set key=value). Times in kyr."""
    # orbit (Earth-like ranges by default; the planet's tilt is the mean obliquity)
    obliquity_amp: float = 1.2  # deg: obliquity swings +- this around the tilt ...
    obliquity_period: float = 41.0  # ... with this period
    precession_period: float = 23.0  # perihelion goes once around the seasons
    ecc_mean: float = 0.027  # eccentricity = mean + two cycles, clipped to >= 0
    ecc_100: float = 0.015  # amplitude of the ~100 kyr cycle
    ecc_400: float = 0.010  # amplitude of the 405 kyr cycle
    phases: str = "auto"  # 'auto': for Earth 'eemian', else 'seed'; 'seed': from the source run's seed
    # and time; 'eemian': start like the last interglacial (obliquity and eccentricity high, perihelion
    # in northern summer); 'zero'; or 'a,b,c,d' = obliquity phase, perihelion longitude at t=0,
    # 100k and 405k eccentricity phases (deg)
    orbit_ref: str = "auto"  # anomalies against 'mean' (tilt, circular orbit), 'start' (the orbit at t=0)
    # or 'today' (Earth's, which the climate model is calibrated to); 'auto': 'today' for Earth, else 'mean'
    orbit_resp: str = "run"  # each cell's response to an insolation change (C per W/m2, month by month,
    # ~2 weeks' lag; forcing.own_k): 'seasons', its own seasons' (icemass.seasonal_k: precession and obliquity
    # change the same annual harmonic of the sun as the seasons; ~0.08-0.09 on mid- and high-latitude land, ~0.02
    # at sea; PW-459), x insol_gain; 'run': the run's rule (icemass.INSOL_K 0.25 on land, INSOL_SEA 0.3 of it at
    # sea, ~3x the seasons'), for the run/zoom rule check until the run takes the seasons' rule (PW-555 stage 3)
    insol_gain: float = 1.0
    # climate
    climate_every: float = 10.0  # kyr between full climate.compute calls
    baseline: str = "model"  # Earth only: 'obs' = observed climate + the model's changes from today
    # (the 'delta method' of paleo ice-sheet modelling: takes the climate model's regional biases out)
    # ice surfaces (the surface mass balance's defaults are icemass's, shared with the run and the zoom)
    snow_h: float = M.SNOW_H  # m: perennial snow/ice this thick is bright (phased in from 0):
    summer_damp: float = M.SUMMER_DAMP  # its summer warmth (above the annual mean) is damped by this share
    # x the surface's own share (icemass.sheet_cover; a big sheet's own air mass is in the full climate's air,
    # icemass.air_mass, carried along the winds: PW-336),
    melt_hold: float = M.MELT_HOLD  # temperatures above 0 C are scaled by this (as climate.compute),
    ice_absorb: float = 0.2  # and it feels this share of an insolation change (it absorbs little) ...
    absorb_km: float = 600.0  # ... the land's, sea's and ice's responses mixed over this scale (km; the air
    # mass, orbit_k), 0 = locally
    snow_w: float = M.SNOW_W  # mm w.e.: lying snow this deep is fully bright (the surface is bright while the
    # year's snow lies, then bare: icemass)
    bare_share: float = M.BARE_SHARE  # bare ice keeps this share of the snow's effects
    ice_cool: float = M.ICE_COOL  # C: thick ice is this much colder on the year's mean (in winter: none at midsummer) ...
    albedo_h: float = M.ALBEDO_H  # ... in full from this thickness (m)
    sheet_air: str = "all"  # the air the sheets make (climate.compute's ice_air, icemass.air_mass, PW-336):
    # 'cold', from the share of each ice cell's summer its surface stays frozen (icemass.cold_share: an ablating
    # surface sits at the melting point and can't chill the air below it; PW-439, PW-555 stage 1); 'all': from
    # all the ice (the run's rule until its own stage)
    surface_air: str = "all"  # the ice surface's own effects on its air (ice_cool's inversion and the summer
    # damping of its bright surface, summer_damp x icemass.LOCAL): 'fetch', on the share of the air touching it
    # that has come over ice for its last surface_km (icemass.surface_share: air off the bare land or open sea
    # beside a margin or a small sheet hasn't cooled to the ice's yet; Antarctica's interior gets ~0.75-1 of
    # them, Greenland's ~0.5, its margins ~0.35; PW-555 stage 1: Earth today's Greenland margins -6.1 -> -3.9 C,
    # obs ~-2.7 on their ice, inland -8.0 -> -6.2, obs -4.9; Antarctica +4.9 -> +3.3 C too warm, its base bias);
    # 'all': all of them on every ice cell (the run's rule until its own stage; Greenland ~4 C below observed)
    surface_km: float = M.SURFACE_KM  # km: 'fetch''s scale (icemass.surface_share)
    margin: str = "edge"  # a margin cell's (ice next to bare land) surface balance: 'ramp', over the sheet's Nye
    # ramp across the part of the cell its ice covers (icemass.margin_ramp, PW-460; ~900 m mean at ~110 km cells);
    # 'edge': its edge's, at most edge_h thick, over the run's margin band (earth.margin_band: the ice within
    # MARGIN_KM of bare land, PW-736; earth.ICE_EDGE_M), the run's rule until it takes the ramp (PW-555 stage 3)
    ramp_n: int = 0  # the ramp's quadrature (icemass.ramp_rule): 0, 2-point Gauss-Legendre in x; n > 0, n points in
    # sqrt(x) (PW-555 stage 1c: 8 points move Earth's Greenland margins by 0.01 m/yr, the yardstick by 0.01: not a cause)
    front: str = "edge"  # bare land the flow reaches (new_ice_rates): 'ramp', the sheet's outermost edge_km of its
    # ramp (0 to edge_h high), sampled like a margin's ramp (ramp_rule) with the ice surface's own effects on the
    # share of its air that has come over ice (surface_share), as every other ice cell (PW-555 stage 1c: Earth
    # today, Greenland's front cells +0.26 -> -0.08 m/yr, RACMO2.3p3's outer 11 km -0.29; the dT-0 ice +30% -> +16%);
    # 'edge', a bright edge edge_h high with all of them (PW-366; the run's new-margin rule until its own stage)
    edge_km: float = 10.0
    edge_h: float = M.EDGE_H  # m: a sheet's edge (its Nye profile 10 km in): bare land the flow reaches is a new
    # edge this high, and 'edge' margins at most this thick
    anchor: str = "auto"  # the starting ice's climate correction (start_anchor): 'obs' (Earth: the model's
    # summer on the ice cooled to the observed one), 'balance' (the smallest cooling that keeps each starting
    # ice cell from melting), 'none' (a run's ice is the same mass balance's mean-orbit extent already);
    # 'auto': obs for Earth, none for a run
    anchor_max: float = 15.0  # C: largest cooling ...
    anchor_rings: int = 3  # ... spread this many cells beyond the ice
    # the glacial index (cycle.py, PW-471): the ice-age cycle as a scripted cooling paced by the orbit; it stands
    # for the cycle's CO2 and ice-albedo feedbacks, so the zoom has none of its own
    index: str = "on"  # 'off': I stays 0 (the run's climate, with the orbit's own anomaly only)
    # (excluding the plants' albedo, which plants.measure adds itself: ~5% of the LGM total, Kohler et al. 2010, PW-879)
    glacial_cool: float = 6.2  # C global cooling at a glacial maximum (Earth's LGM 4.5-6 C) for a planet with ...
    glacial_f: float = 0.035  # ... this share of its surface ice-free land poleward of its snowline (Earth's at L6,
    # cycle.snowline_land), in proportion to the planet's own share ...
    glacial_cap: float = 1.6  # ... at most this x glacial_cool
    glacial_dt: float = -1.0  # C: the glacial maximum's cooling set by hand (>= 0), instead of the above
    # the plants' CO2 at a glacial maximum against the interglacial's (PW-828): Earth's LGM ~190 / 280 ppm
    # (EPICA Dome C, Luthi et al. 2008), at a planet's glacial_cool-sized cooling, in proportion to its own
    # (was a 0.5 share of the cooling as CO2's warming, which gave 0.47x)
    glacial_pco2: float = 0.68
    build_kyr: float = 36.0  # kyr: a glacial takes I toward 1 with this e-folding time ...
    build_orb: float = 0.5  # ... faster in a weak summer and slower in a strong one: 1 +- this per half the
    # summer sun's 10-90 percentile spread from its median
    ig_kyr: float = 10.0  # an interglacial (I = 0) lasts at least this long (kyr) ...
    build_q: float = 0.4  # ... then building starts when the summer sun falls below this percentile of its series
    end_min: float = 0.85  # an ending needs I at least this ...
    bar_hi: float = 0.95  # ... and a summer sun above a bar falling from this percentile ...
    bar_lo: float = 0.6  # ... to this one at ...
    glacial_kyr: float = 100.0  # ... this age (the orbit's short eccentricity period)
    end_kyr: float = 8.0  # an ending takes I back to 0 in this long (kyr)
    backstop: float = 2.0  # x glacial_kyr: past this age the next sunshine peak ends the glacial (counted)
    sheet_h: float = 2000.0  # m: the glacial maximum's sea-level target (a diagnostic) is this much ice over the
    # land poleward of the snowline
    # vegetation (plants.py, PW-450): the run's model grown on each full climate
    veg: str = "on"  # 'on': it feeds back on the climate locally (as in the run: Budyko w, the surface's
    # albedo with snow hidden under forest) and globally (its albedo's change since the start, in dTg);
    # 'local': the local part only; 'off': none (climate.compute's Earth-like average surface)
    veg_toa: float = 0.4  # the planet's albedo changes by this x a change of the surface's (the air's and
    # the clouds' share of the light, both ways: Qu & Hall 2006, ~0.3-0.5 outside the tropics) ...
    veg_lambda: float = 0.8  # ... and the climate by this many C per W/m2 of it (the fast feedbacks inside:
    # Hansen et al. 2008 0.75) ...
    veg_speed: float = 250.0  # m/yr: how fast the plants take new ground (the frames' cover, plants.py: migration;
    # trees spread 100-500 m/yr after the ice, Davis & Shaw 2001; ~1 L6 cell per 480 yr); 0 = at once, in balance
    veg_lag: float = 2.0  # ... following the plants this slowly (kyr: a biome shift takes centuries to a
    # few kyr; the plants themselves are grown afresh on each full climate)
    precip_k: float = M.PRECIP_K  # rain ~ exp(precip_k * dT) (Clausius-Clapeyron)
    # mass balance
    pdd_sigma: float = M.PDD_SIGMA  # C: day-to-day spread of temperature around the monthly mean
    ddf_snow: float = M.DDF_SNOW  # mm w.e. melted per positive degree-day, snow
    ddf_ice: float = M.DDF_ICE  # ... ice
    refreeze: float = M.REFREEZE  # share of snowmelt that refreezes in the snowpack
    # flow, bed, sea
    flow_a: float = M.FLOW_A  # Pa^-3 yr^-1: Glen's rate factor (~-10 C ice) ...
    enhancement: float = M.ENHANCEMENT  # ... times this (common for ice-age ice sheets; also stands in for sliding)
    d_cap: float = M.D_CAP  # m2/yr: cap on the ice diffusivity (unresolved steep margins)
    cfl: float = 0.15  # explicit time step safety factor
    iso_ratio: float = ICE_SINK  # bedrock sinks this x ice thickness (ice/mantle density) ...
    flex_km: float = FLEX_KM  # ... spread over this (km, lithospheric flexure) ...
    iso_tau: float = 3.0  # ... with this e-folding time (kyr)
    calving: float = M.CALVING  # per yr: calving speed (m/yr) per m of water depth at a marine ice front ...
    calve_depth: float = M.CALVE_DEPTH  # m: ... and wherever grounded ice stands in deeper water than this, even
    # with no open sea beside it (a deep basin the grid can't resolve: ice flowing into it would float,
    # break up and melt in the sea water under it, not fill it 10 km thick; PW-199: ~4 km basins). Deeper
    # than real grounded ice stands: Earth's deepest grounded beds are ~2.5 km (the Bentley Subglacial
    # Trench; ETOPO1's cell means reach 1.7 km at L6, 2.3 km at L7), and at 1.5 km the true bed's
    # deepest cells under West Antarctica's 3 km of ice calved in place from the start (PW-361)
    buttress: float = M.BUTTRESS  # share of a grounded front's flow across its grounding line an ice shelf beside it holds
    # back (shelf_cover, PW-367; Fürst et al. 2016: Antarctica's shelves carry most of the resistance at the
    # grounding line, only ~13% of their area is 'passive'; Larsen B's tributaries sped up 2-8x once it broke up,
    # Rignot et al. 2004); the same confinement slows the shelf's own spreading (x (1 - buttress)^3); a front
    # beside a shelf doesn't calve, in full beside one this thick (m) ...
    shelf_h: float = 100.0
    shelf_warm: float = M.SHELF_WARM  # C: ... floating ice is a shelf where the air's annual mean over the sea is below this
    shelf_cold: float = M.SHELF_COLD  # (in full below this; Morris & Vaughan 2003's limit of ice-shelf viability), else
    # it breaks up; a shelf spreads under its own weight (Weertman 1957, held back by the same buttressing) ...
    melt_k: float = M.MELT_K  # m/yr per C: ... and melts from below where the sea is warmer than freezing (Holland
    # et al. 2008, Jenkins et al. 2018: ~10 m/yr per degree of thermal forcing)
    # glacial erosion (PW-037, docs/proposals/glacial_carving.md)
    carving: bool = True  # the ice erodes its bed, carries the debris and drops it where it melts
    glacial_k: float = 4e-6  # erosion (m/yr) = glacial_k x erodibility (surface.ROCK_K) x sliding speed (m/yr)
    glacial_l: float = 1.0  # ^ this (Hallet 1979's abrasion law). glacial_k: at this model's cell-mean speeds,
    # the observed range (Hallet et al. 1996, Koppes et al. 2015): ~0.01-0.3 mm/yr under slow or cold-based
    # sheets, ~1 mm/yr at 250 m/yr of sliding, ~5 mm/yr under the fastest outlets
    slide_share: float = 0.5  # share of a thawed bed's ice speed that is sliding ...
    tau_y: float = 1.0e5  # Pa: ... at a basal shear stress of at most this, the bed's yield stress (Nye's plastic
    # bed; ice sheets' basal stresses are 50-150 kPa, Cuffey & Paterson 2010): where the grid's slope asks more,
    # the extra fall is an unresolved margin, not faster sliding (the speed goes as tau^3)
    geo_flux: float = 0.065  # W/m2: geothermal heat into the ice's base (Robin's column: is the bed thawed?)
    adverse: float = 1.5  # no erosion where the bed rises downstream > this x the ice surface falls
    # (supercooling, Alley et al. 2003: the bound on an overdeepened basin)
    # where the debris goes (deposit.py; e-folding lengths as shares of the planet's radius, 0.04 = 255 km on Earth)
    fan_km_r: float = 0.08  # debris dropped in the sea spreads down the sea floor: a grounding-zone fan (PW-495)
    fan_flat: float = 1000.0  # m: ... over every sea neighbour no more than this above it (debris flows spill over a rim)
    outwash_share: float = 0.5  # of the debris melted out on land, the share that goes on in the meltwater (PW-497) ...
    outwash_km_r: float = 0.025  # ... down the bare ground as a sandur, falling off over this length ...
    silt_share: float = 0.5  # ... its silt (glacial flour) is lifted off the plain ...
    loess_km_r: float = 0.05  # ... and carried downwind (the cold season's wind) over this length as loess
    rock_ratio: float = 0.82  # the bed rises by this x the net rock removed (rho_rock / rho_mantle), spread
    # by flexure over flex_km and relaxing with iso_tau like the ice load
