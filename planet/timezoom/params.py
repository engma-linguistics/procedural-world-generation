"""Time zoom constants, the per-frame layer layout and the knobs (TZParams)."""

from __future__ import annotations

from dataclasses import dataclass

from .. import icemass as M
from .. import store as S
from ..geo import R_KM
from ..tectonics.isostasy import FLEX_KM, ICE_SINK

R_M = R_KM * 1000.0
RHO_I, RHO_W = 917.0, 1028.0

LAYERS = {  # per frame: store.LAYERS names and encodings, as runs
    "elevation": S.LAYERS["elevation"],  # m, surface (ice included) above that frame's sea level
    # 1 m steps in 16 bits (domes on big polar continents pass 5.1 km), so a finished world (finish.py)
    # gets the bed back from any frame as elevation - ice to a metre
    "ice": {**S.LAYERS["ice"], "dtype": "<u2", "scale": 1},
    "temperature": S.LAYERS["temperature"],  # C, annual mean
    "climate": S.LAYERS["climate"],  # climate.KOPPEN id
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
    insol_k: float = 0.25  # C per W/m2 of insolation change, on land (month by month, ~2 weeks' lag)
    insol_sea: float = 0.3  # share of that over the sea (deep mixed layer)
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
    ice_cool: float = M.ICE_COOL  # C: thick ice is this much colder all year ...
    albedo_h: float = M.ALBEDO_H  # ... in full from this thickness (m)
    edge_h: float = M.EDGE_H  # m: a margin cell's surface balance is its edge's, at most this thick
    anchor: str = "auto"  # the starting ice's climate correction (start_anchor): 'obs' (Earth: the model's
    # summer on the ice cooled to the observed one), 'balance' (the smallest cooling that keeps each starting
    # ice cell from melting), 'none' (a run's ice is the same mass balance's mean-orbit extent already);
    # 'auto': obs for Earth, none for a run
    anchor_max: float = 15.0  # C: largest cooling ...
    anchor_rings: int = 3  # ... spread this many cells beyond the ice
    # global feedbacks
    co2_cool: float = 2.5  # C global cooling per 120 m of sea level locked in extra ice (CO2 drawdown) ...
    co2_max: float = 1.0  # ... saturating at this many times that (glacial CO2 bottoms out, Earth ~180 ppm)
    start: str = "auto"  # where the start sits in the ice-age cycle: 'interglacial' (Earth today: the CO2
    # feedback has its full room to a glacial maximum) or 'average' (a run's moment:
    # its ice is the mean extent over the cycles and its dT already has that ice's albedo and part of
    # the glacial CO2 drop, so only average_room of its cap is left; the ice albedo levels off by itself);
    # 'auto': interglacial for Earth
    average_room: float = 0.5  # (Earth: 230 ppm on average over the last cycles, 280 interglacial, 185 glacial)
    co2_lag: float = 3.0  # kyr: CO2 follows the ice this slowly
    ice_albedo: float = 1.5  # C global cooling per 3% of the planet under land ice, levelling off toward ...
    ice_albedo_max: float = 3.0  # ... this many C: the main run's rule (earth.py), as the change from the start's
    # ice (PW-030: before, half the run's, capped at 2 C and for a run's moment at average_room of that; the
    # run's ice surfaces have their own local climate too, so the halving had no reason)
    # the ice-age cycle (cycle.py, PW-440): between ice ages / building / ending
    cycle: str = "on"  # 'off': no cycle state (the feedbacks above alone)
    sheet_h: float = 2000.0  # m: the sheet scale is the sea-level equivalent of this much ice ...
    sheet_share: float = 0.1  # ... over this share of the planet's land
    build_q: float = 0.4  # building starts when the summer sun falls below this percentile of its series
    end_min: float = 0.4  # an ending needs this much extra ice (x the sheet scale) ...
    bar_hi: float = 0.95  # ... and a summer sun above a bar falling from this percentile ...
    bar_lo: float = 0.6  # ... to this one at ...
    glacial_kyr: float = 100.0  # ... this age (the orbit's short eccentricity period)
    backstop: float = 2.0  # x glacial_kyr: past this age the next sunshine peak ends the glacial (counted)
    end_e: float = 0.1  # an ending runs until the extra ice is below this (x the sheet scale)
    cycle_tau: float = 3.0  # kyr: the ending's boosts ramp in this fast
    melt_max: float = 1.8  # the extra ice's degree-day factors, at most this x ...
    calve_max: float = 2.0  # ... its marine fronts' calving x this ...
    release: float = 0.9  # ... and a CO2 release of this x co2_cool (Earth ~90 ppm), up to the interglacial's
    precip_k: float = M.PRECIP_K  # rain ~ exp(precip_k * dT) (Clausius-Clapeyron)
    # mass balance
    pdd_sigma: float = M.PDD_SIGMA  # C: day-to-day spread of temperature around the monthly mean
    ddf_snow: float = M.DDF_SNOW  # mm w.e. melted per positive degree-day, snow
    ddf_ice: float = M.DDF_ICE  # ... ice
    refreeze: float = M.REFREEZE  # share of snowmelt that refreezes in the snowpack
    # flow, bed, sea
    flow_a: float = 1e-16  # Pa^-3 yr^-1: Glen's rate factor (~-10 C ice) ...
    enhancement: float = 3.0  # ... times this (common for ice-age ice sheets; also stands in for sliding)
    d_cap: float = 3e8  # m2/yr: cap on the ice diffusivity (unresolved steep margins)
    cfl: float = 0.15  # explicit time step safety factor
    iso_ratio: float = ICE_SINK  # bedrock sinks this x ice thickness (ice/mantle density) ...
    flex_km: float = FLEX_KM  # ... spread over this (km, lithospheric flexure) ...
    iso_tau: float = 3.0  # ... with this e-folding time (kyr)
    calving: float = 1.0  # per yr: calving speed (m/yr) per m of water depth at a marine ice front ...
    calve_depth: float = 3000.0  # m: ... and wherever grounded ice stands in deeper water than this, even
    # with no open sea beside it (a deep basin the grid can't resolve: ice flowing into it would float,
    # break up and melt in the sea water under it, not fill it 10 km thick; PW-199: ~4 km basins). Deeper
    # than real grounded ice stands: Earth's deepest grounded beds are ~2.5 km (the Bentley Subglacial
    # Trench; ETOPO1's cell means reach 1.7 km at L6, 2.3 km at L7), and at 1.5 km the true bed's
    # deepest cells under West Antarctica's 3 km of ice calved in place from the start (PW-361)
    buttress: float = 0.8  # share of a grounded front's flow across its grounding line an ice shelf beside it holds
    # back (shelf_cover, PW-367; Fürst et al. 2016: Antarctica's shelves carry most of the resistance at the
    # grounding line, only ~13% of their area is 'passive'; Larsen B's tributaries sped up 2-8x once it broke up,
    # Rignot et al. 2004); the same confinement slows the shelf's own spreading (x (1 - buttress)^3); a front
    # beside a shelf doesn't calve, in full beside one this thick (m) ...
    shelf_h: float = 100.0
    shelf_warm: float = -5.0  # C: ... floating ice is a shelf where the air's annual mean over the sea is below this
    shelf_cold: float = -10.0  # (in full below this; Morris & Vaughan 2003's limit of ice-shelf viability), else
    # it breaks up; a shelf spreads under its own weight (Weertman 1957, held back by the same buttressing) ...
    melt_k: float = 10.0  # m/yr per C: ... and melts from below where the sea is warmer than freezing (Holland
    # et al. 2008, Jenkins et al. 2018: ~10 m/yr per degree of thermal forcing)
