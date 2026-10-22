"""Surface mass balance of land ice: one rule shared by the run's ice sheets
(tectonics/earth.ice_sheets), the glacial time zoom (timezoom.py, whose
TZParams take these values as defaults) and the regional zoom's glaciers
(zoom.glaciers), so a snowline is set by the same snowfall and summer
warmth everywhere (PW-159, PW-190).

The year: twelve months on a sine between the bare ground's coldest and
warmest month (timezoom_kernels.climate_step), on the ice's surface (h m
higher: the lapse rate). Snow falls in the months below ~0 C; positive
degree-days (Reeh 1991, days scattered with sd PDD_SIGMA around each
month's mean) melt the year's snow first (DDF_SNOW, a share REFREEZE of it
refreezes in the snowpack), then ice (DDF_ICE). On ice:
  - thick ice (ALBEDO_H) is ICE_COOL (2 C) colder all year (inversion,
    katabatic air);
  - where perennial snow lies (bright: last year's snow outlasted the
    summer; bare ice keeps BARE_SHARE of this), temperatures above 0 C are
    scaled by MELT_HOLD (a melting surface holds the air over it near 0 C:
    Greenland's ablation zone ~+3..5 C in July where the tundra beside it at
    the same height has ~+8..10 C), and
  - the summer's warmth above the annual mean is damped by SUMMER_DAMP x
    LOCAL (sheet_cover: the bright surface's own share). A big sheet's own
    cold, bright air mass (Antarctica's coast stays below 0 C in summer) is
    in the climate's air: climate.compute damps the summer of the air over
    the ice by SUMMER_DAMP x air_mass (the share of the surface within
    ~1000 km under ice, away from the tropics) and carries it along the
    winds onto the margins and the land beside (PW-336), while a small cap
    sits in the air of the land around it. Before PW-190 the damping was
    0.6 everywhere on bright snow, so a sheet's margin had a summer ~10 C
    colder than the tundra beside it and kept spreading onto land with
    ~9 C bare summers; before PW-336 the air mass was a local damping of
    each ice cell, and the air reaching a sheet's margins and shelves came
    off the bare ground's summer (+13 C over Antarctica's bed).
"""

from __future__ import annotations

import numpy as np

SNOW_H = 20.0  # m: perennial snow / ice this thick is bright (phased in from 0)
SUMMER_DAMP = 0.6  # share of the summer's warmth above the annual mean taken away (x sheet_cover on the ice's
# surface, x air_mass in the air over a sheet)
MELT_HOLD = 0.5  # temperatures above 0 C on snow / ice are scaled by this
SNOW_W = 30.0  # mm w.e.: lying snow this deep is fully bright
BARE_SHARE = 0.3  # bare ice keeps this share of the snow's effects
ICE_COOL = 2.0  # C: thick ice is this much colder all year (inversion, katabatic air) ...
ALBEDO_H = 800.0  # ... in full from this thickness (m)
SHEET_TAU = 75e3  # Pa: yield stress of ice, sets a sheet's steady (Nye) profile (PW-366: Antarctica's real extent
# and bed hold ETOPO1's 25 Mkm3 at ~75 kPa, 50 kPa gave 20; real sheets fit ~70-100 kPa)
EDGE_H = float(np.sqrt(2 * SHEET_TAU / (917.0 * 9.81) * 10e3))  # m (~400): a sheet's margin (its Nye profile 10 km
# in from its edge): at ~110 km cells a margin cell's snow and melt are its edge's
PDD_SIGMA = 5.0  # C: day-to-day spread of temperature around the monthly mean
DDF_SNOW = 3.0  # mm w.e. melted per positive degree-day, snow (Braithwaite 1995)
DDF_ICE = 8.0  # ... ice
REFREEZE = 0.6  # share of snowmelt that refreezes in the snowpack
PRECIP_K = 0.07  # rain ~ exp(PRECIP_K * dT) (Clausius-Clapeyron)
SHEET_KM = 1000.0  # km: a sheet's own air mass (air_mass) ...
LOCAL = 0.3  # ... and the share of the damping any ice gets, however small its patch (bare ground's lying
# snow gets none: its brightness is in the climate's own snow albedo; PW-275)

# The sea's side of a sheet (PW-367), the time zoom's (TZParams take these as defaults) and the run's
# (coast_loss, PW-465): see TZParams for the sources.
RHO_I, RHO_W = 917.0, 1028.0
FLOW_A = 1e-16  # Pa^-3 yr^-1: Glen's rate factor (~-10 C ice) ...
ENHANCEMENT = 3.0  # ... times this (also stands in for sliding)
D_CAP = 3e8  # m2/yr: cap on the ice diffusivity (unresolved steep margins)
CALVING = 1.0  # per yr: calving speed (m/yr) per m of water depth at a marine ice front
CALVE_DEPTH = 3000.0  # m: grounded ice in deeper water than this calves in place
BUTTRESS = 0.8  # share of a front's flow across its grounding line an ice shelf beside it holds back
SHELF_WARM = -5.0  # C: floating ice is a shelf where the air's annual mean over the sea is below this ...
SHELF_COLD = -10.0  # ... in full below this
MELT_K = 10.0  # m/yr per C: a shelf melts from below where the sea is warmer than freezing


def shelf_viable(t_air, warm: float = SHELF_WARM, cold: float = SHELF_COLD):
    """Share (0..1) of floating ice that stays as an ice shelf, by the
    annual mean air temperature over the sea (C): Morris & Vaughan 2003's
    ~-5 C limit (timezoom.ice.shelf_viable has the story)."""
    return np.clip((warm - np.asarray(t_air, float)) / (warm - cold), 0.0, 1.0)


def coast_loss(h, s, depth, dist, elen, t_air, melt, area):
    """The ice a sheet loses to the sea per coastal cell (m3/yr), by the time
    zoom's rules on the run's still geometry (PW-465). Per side of an iced
    cell facing the sea (arrays per side: h, the cell's ice (m); s, its
    surface above the sea (m); depth, the water's depth beyond (m); dist,
    elen: the side's centre distance and length (m); t_air: the air's annual
    mean over that sea (C); melt: the sea's melt under a shelf there
    (MELT_K x its warmth above freezing, m/yr); area: the sea cell's area):
    the shallow-ice flow across the side (D = gamma h^5 |grad s|^2, capped,
    the sea's side D = 0, so half of it, as timezoom.kernels.sia_flow's
    Mahaffy mean on its first step from the coast). Where the water is deep
    enough for that ice to float, it is an ice shelf or breaks up: the flow
    leaves the sheet (a shelf spreads, calves and melts away whatever it is
    fed), less what a standing shelf holds back (BUTTRESS, where the air
    lets one stand and the sea's melt under one cell of it doesn't outrun
    the flow). Where it would ground, the sheet's front stands in the
    shallow sea and calves (CALVING x depth x h), at most what flows there.
    Measured in a time zoom from the run's ice at I = 0 (L6, 4 moments, 50
    kyr): the sea beside the sheets takes ~1-2e5 m2/yr per m of coast from
    deep water and ~1e3-5e4 from shallow, where the run used to charge 5e4
    everywhere and nothing to a sheet's accumulation zone."""
    gamma = 2 * FLOW_A * ENHANCEMENT * (RHO_I * 9.81) ** 3 / 5
    slope = np.maximum(s, 0.0) / dist
    q = 0.5 * np.minimum(gamma * h ** 5 * slope ** 2, D_CAP) * slope * elen  # m3/yr
    floats = depth * RHO_W > h * RHO_I
    shelf = shelf_viable(t_air) * (melt * area < q)
    deep = q * (1.0 - BUTTRESS * shelf)
    shallow = np.minimum(CALVING * depth * h * elen, q)
    return np.where(floats, deep, shallow)


def air_mass(grid, ice, km: float = SHEET_KM, cold=None):
    """How much (0..1) of the air over each cell of land ice is the sheet's
    own cold, bright air mass: the share of the surface (land and sea)
    within ~km under land ice (m > 1), away from the tropics (none within
    15 deg of the equator, in full from 50 deg, as climate.ice_cover); 0
    off the ice. cold (0..1 per cell, None: 1): the share of each ice
    cell's summer its surface stays frozen (cold_share): an ablating
    surface sits at the melting point and can't chill the air below it, so
    only the frozen share of a sheet makes its cold air (the time zoom's,
    PW-555 stage 1; the run counts all its ice until its own stage). climate.compute damps that air's summer warmth by
    SUMMER_DAMP x this and the winds carry it on (PW-336): katabatic
    outflow, so a big sheet's margins, ice shelves and the land beside it
    get its cold summers, a lone cap's surroundings don't. Antarctica
    ~0.6..1, Greenland ~0.3..0.5, a valley glacier ~0."""
    from . import climate
    on = np.asarray(ice) > 1
    src = on.astype(float) if cold is None else np.where(on, np.clip(cold, 0.0, 1.0), 0.0)
    a = climate.smooth_big(grid, src, km)
    polar = np.clip((np.abs(grid.lat) - 15.0) / 35.0, 0.0, 1.0)
    return np.where(on, np.clip(a, 0.0, 1.0) * polar, 0.0)


def cold_share(t_warm, sigma: float = PDD_SIGMA):
    """The share (0..1) of the warmest month's days an ice surface stays
    below freezing, its days scattered with sd sigma around the month's
    mean t_warm (C; the degree-day rule's own spread): ~0.84 at -5 C, 0.5
    at 0 C, ~0.16 at +5 C (for air_mass's cold)."""
    from .climate import _erf
    return 0.5 * (1.0 - _erf(np.asarray(t_warm, float) / (sigma * np.sqrt(2.0))))


def sheet_cover(grid, ice):
    """How much (0..1) of SUMMER_DAMP an ice surface at each cell gets on
    top of the air it sits in (for ice only: bare ground's snow gets 0, in
    the run, the time zoom and the zoom alike, PW-275): LOCAL, its own
    bright surface, however small the patch. A big sheet's own air mass is
    in the climate's air already (air_mass, carried along the winds,
    PW-336), so it isn't counted here again."""
    return np.full(grid.n, LOCAL)


_NODES = np.array([0.5 - 0.5 / np.sqrt(3.0), 0.5 + 0.5 / np.sqrt(3.0)])  # 2-point Gauss-Legendre on 0..1


def margin_ramp(H, width_m: float):
    """A margin cell (ice next to bare land) as the part of its width the
    sheet's edge covers (PW-460): its ice H (m, the cell's mean) is a Nye
    ramp sqrt(2 tau/(rho g) x) rising from the edge (x = 0) across an iced
    share f of the cell (width_m wide), so H = f x the ramp's mean over it
    (2/3 of its top); a cell with at least the full width's mean (~900 m at
    ~110 km cells) is iced across (f = 1). Returns (f, the ramp's height at
    the two quadrature points of its iced part, shape (2, n)): the cell's
    balance is f x the mean of the balance at those heights (the lower,
    outer part melts faster than the mean height would). Grid-relative: on
    finer cells the ramp is lower (~400 m at 10 km, EDGE_H). The time zoom's
    margins (PW-555 stage 1; the run keeps EDGE_H until its own stage: before
    PW-460 a margin cell's balance was its edge's at any cell size, so a
    ~110 km cell melted as if all of it were its outermost 10 km, PW-115)."""
    H = np.maximum(np.atleast_1d(np.asarray(H, float)), 0.0)
    top = np.sqrt(2 * SHEET_TAU / (917.0 * 9.81) * width_m)
    f = np.clip(H / (2.0 / 3.0 * top), 0.0, 1.0) ** (2.0 / 3.0)
    return f, top * np.sqrt(f)[None, :] * np.sqrt(_NODES)[:, None]


# The orbit's effect on a month's temperature (PW-459): each cell responds to an insolation change as it does
# to the seasons (precession and obliquity change the same annual harmonic of the sun as the seasons do): its
# own warmest - coldest month per the lagged sun's seasonal range at its latitude (seasonal_k; Earth ~0.08-0.09
# C per W/m2 on mid- and high-latitude land, ~0.02 over the sea's deep mixed layer). Near the equator the
# sun's annual range is small (its cycle is half-yearly): the range counts as at least SUN_FLOOR of the
# planet's largest. The time zoom's rule (PW-555 stage 1); the run's cycle average (balance) keeps INSOL_K
# until its own stage.
SUN_FLOOR = 0.25
_SUN = {}


def sun_range(tilt: float) -> np.ndarray:
    """Per latitude band (orbit.BAND_LAT): the seasonal range (W/m2) of the
    top-of-atmosphere sun at the mean (circular) orbit, each month averaged
    with the one before (the ground lags the sun, as cycle_dq). Cached."""
    key = round(float(tilt), 3)
    if key not in _SUN:
        from .orbit import insolation
        q = insolation(tilt, 0.0, 0.0)
        q = 0.5 * (q + np.roll(q, 1, axis=1))
        _SUN[key] = q.max(axis=1) - q.min(axis=1)
    return _SUN[key]


def seasonal_k(lat, t_warm, t_cold, tilt: float) -> np.ndarray:
    """C per W/m2 of insolation change per cell: its own seasonal swing
    (t_warm - t_cold, the bare ground's or the sea's) per the sun's
    (sun_range, at least SUN_FLOOR of the largest band's). Continental
    interiors respond most, coasts less, the sea ~a quarter of the land
    (its mixed layer): from the climate itself, not a calibrated constant
    (INSOL_K: 0.25 on land, 0.3 of that at sea, ~3x the seasons')."""
    from .orbit import BAND_DEG, BAND_LAT
    rng = sun_range(tilt)
    band = np.clip(((np.asarray(lat, float) + 90) / BAND_DEG).astype(np.int64), 0, len(BAND_LAT) - 1)
    r = np.maximum(rng[band], max(SUN_FLOOR * float(rng.max()), 1.0))
    return np.maximum(np.asarray(t_warm, float) - np.asarray(t_cold, float), 0.0) / r


# The ice-age cycle a run's (and a zoom's) ice is the average over: precession at four phases x obliquity
# at +-OBL_AMP/sqrt(2) (the spread of a sine), eccentricity ECC (the rms of the time zoom's), each month's
# insolation change against the mean orbit times INSOL_K (C per W/m2; the time zoom's insol_k, less over
# bright ice: ICE_ABSORB)
OBL_AMP, ECC = 1.2, 0.03
INSOL_K, INSOL_SEA, ICE_ABSORB = 0.25, 0.3, 0.2
ABSORB_KM = 600.0  # km: ... mixed over the air around
_CYCLE = {}


def cycle_dq(tilt: float) -> np.ndarray:
    """(states, latitude bands, 12 months) insolation change (W/m2) over the
    cycle's orbital states against the mean orbit, each month averaged with
    the one before (the ground lags the sun). Cached per tilt."""
    key = round(float(tilt), 3)
    if key not in _CYCLE:
        from .orbit import insolation
        ref = insolation(tilt, 0.0, 0.0)
        out = []
        for d_obl in (-OBL_AMP / np.sqrt(2), OBL_AMP / np.sqrt(2)):
            for peri in (0.0, 90.0, 180.0, 270.0):
                dq = insolation(tilt + d_obl, ECC, peri) - ref
                out.append(0.5 * (dq + np.roll(dq, 1, axis=1)))
        _CYCLE[key] = np.array(out)
    return _CYCLE[key]


def balance(lat, land, t_warm, t_cold, p_jul, p_jan, h, cover, dt_glob=None, tilt: float | None = None,
            absorb=None):
    """m of ice per year each land cell gains (> 0) or loses (< 0) under h m
    of ice (0: bare ground: snow that outlasts the summer). t_warm, t_cold:
    the bare ground's warmest and coldest month (C) at the bed (the ice's
    surface stands h higher); p_jul, p_jan: the half-years' precipitation
    (mm/yr); cover: sheet_cover (0..1). dt_glob: a global temperature
    change (C; the rain scales with it). tilt (deg): the balance averaged
    over the ice-age cycle's orbits (cycle_dq; melt rises faster in a warm
    summer than it falls in a cold one, so the cycle's average ice is less
    than the mean orbit's); None: at the mean orbit. absorb: the share
    (0..1) of an insolation change the surface feels (None: from the ice
    itself, ICE_ABSORB on thick ice). Returns (smb, t_warm on the surface,
    at the mean orbit)."""
    from .timezoom.kernels import climate_step
    lat = np.asarray(lat, float)
    n = len(lat)
    land = np.asarray(land, bool)
    dt_wet = np.zeros(n) if dt_glob is None else np.broadcast_to(np.asarray(dt_glob, float), (n,)).copy()
    (smb, _, t_w, _), args, rest, (f_alb, p_scale, f_sum) = _mean_year(lat, land, t_warm, t_cold, p_jul, p_jan, h,
                                                                        cover, dt_wet)
    if tilt is None:
        return smb, t_w
    from .orbit import BAND_DEG, BAND_LAT
    band = np.clip(((lat + 90) / BAND_DEG).astype(np.int64), 0, len(BAND_LAT) - 1)
    a = 1 - f_alb * (1 - ICE_ABSORB) if absorb is None else np.broadcast_to(np.asarray(absorb, float), (n,))
    k_orb = np.where(land, INSOL_K, INSOL_K * INSOL_SEA) * a
    tot, one, t_x = np.zeros(n), np.zeros(n), np.zeros(n)
    states = cycle_dq(tilt)
    for dq in states:
        climate_step(*args, k_orb, band, dq, *rest, one, t_x, t_x, t_x, p_scale, f_sum)
        tot += one
    return tot / len(states), t_w


def _mean_year(lat, land, t_warm, t_cold, p_jul, p_jan, h, cover, dt_wet):
    """climate_step at the mean orbit: ((smb, t_ann, t_warm, t_cold), its
    arguments, the rule's constants, (f_alb, p_scale, f_sum))."""
    from . import climate
    from .timezoom.kernels import climate_step
    n = len(lat)
    h = np.broadcast_to(np.asarray(h, float), (n,)).copy()
    t_warm, t_cold = np.asarray(t_warm, float), np.asarray(t_cold, float)
    f_ice, f_alb = np.clip(h / ALBEDO_H, 0, 1), np.clip(h / SNOW_H, 0, 1)
    damp = SUMMER_DAMP * np.broadcast_to(np.clip(np.asarray(cover, float), 0, 1), (n,))
    smb, t_ann, t_w, t_c, p_scale, f_sum = (np.zeros(n) for _ in range(6))
    args = (land, lat >= 0, 0.5 * (t_warm + t_cold), 0.5 * np.maximum(t_warm - t_cold, 0),
            np.broadcast_to(np.asarray(p_jul, float), (n,)).copy(), np.broadcast_to(np.asarray(p_jan, float), (n,)).copy(),
            -climate.LAPSE * h + dt_wet, dt_wet)
    rest = (f_ice, f_alb, ICE_COOL, damp, MELT_HOLD, BARE_SHARE, SNOW_W,
            PDD_SIGMA, DDF_SNOW, DDF_ICE, REFREEZE, PRECIP_K)
    climate_step(*args, np.zeros(n), np.zeros(n, np.int64), np.zeros((1, 12)), *rest, smb, t_ann, t_w, t_c,
                 p_scale, f_sum)
    return (smb, t_ann, t_w, t_c), args, rest, (f_alb, p_scale, f_sum)


def surface(lat, t_warm, t_cold, p_jul, p_jan, h, cover):
    """(annual mean, warmest, coldest month) C on the surface of h m of land
    ice, from the bare ground's warmest and coldest month at its bed, by the
    mass balance's own year at the mean orbit (climate_step: the ice's height,
    thick ice ICE_COOL colder all year, the summer damped
    while snow lies by SUMMER_DAMP x cover (sheet_cover), a melting surface
    held near 0 C). The one ice-surface climate of the run's keyframes, the
    worlds and the zooms (climate.ice_surface), the time zoom's frames and
    the ice extent itself (PW-277)."""
    lat = np.asarray(lat, float)
    n = len(lat)
    (_, t_ann, t_w, t_c), *_ = _mean_year(lat, np.ones(n, bool), t_warm, t_cold, p_jul, p_jan, h, cover, np.zeros(n))
    return t_ann, t_w, t_c


def ground_from_surface(lat, tw_s, tc_s, p_jul, p_jan, h, cover, iters: int = 40):
    """The inverse of surface: the bare ground's warmest and coldest month
    at the bed under h m of ice whose surface has warmest / coldest month
    tw_s, tc_s (for a zoom, which gets a world's ice-surface climate and
    needs the ground's). The surface's coldest month depends on the
    ground's coldest only, its warmest on both, each monotonically (lying
    snow switches the summer's damping on and off in steps, so Newton
    stalls): bisection, first the coldest month, then the warmest."""
    from . import climate
    lat = np.asarray(lat, float)
    tw_s, tc_s = np.asarray(tw_s, float), np.asarray(tc_s, float)
    h = np.broadcast_to(np.asarray(h, float), lat.shape)
    up = climate.LAPSE * h + ICE_COOL * np.clip(h / ALBEDO_H, 0, 1)

    def solve(fn, target, lo, hi):
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            below = fn(mid) < target
            lo, hi = np.where(below, mid, lo), np.where(below, hi, mid)
        return 0.5 * (lo + hi)

    top = np.maximum(tw_s, tw_s / MELT_HOLD) + up + 80.0
    gc = solve(lambda x: surface(lat, top, x, p_jul, p_jan, h, cover)[2], tc_s, tc_s + up - 3.0,
               np.maximum(tc_s, tc_s / MELT_HOLD) + up + 3.0)
    gw = solve(lambda x: surface(lat, x, gc, p_jul, p_jan, h, cover)[1], tw_s, np.maximum(gc, tw_s + up - 3.0),
               np.maximum(top, gc))
    return gw, gc
