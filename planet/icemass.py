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


def air_mass(grid, ice, km: float = SHEET_KM):
    """How much (0..1) of the air over each cell of land ice is the sheet's
    own cold, bright air mass: the share of the surface (land and sea)
    within ~km under land ice (m > 1), away from the tropics (none within
    15 deg of the equator, in full from 50 deg, as climate.ice_cover); 0
    off the ice. climate.compute damps that air's summer warmth by
    SUMMER_DAMP x this and the winds carry it on (PW-336): katabatic
    outflow, so a big sheet's margins, ice shelves and the land beside it
    get its cold summers, a lone cap's surroundings don't. Antarctica
    ~0.6..1, Greenland ~0.3..0.5, a valley glacier ~0."""
    from . import climate
    on = np.asarray(ice) > 1
    a = climate.smooth_big(grid, on.astype(float), km)
    polar = np.clip((np.abs(grid.lat) - 15.0) / 35.0, 0.0, 1.0)
    return np.where(on, np.clip(a, 0.0, 1.0) * polar, 0.0)


def sheet_cover(grid, ice):
    """How much (0..1) of SUMMER_DAMP an ice surface at each cell gets on
    top of the air it sits in (for ice only: bare ground's snow gets 0, in
    the run, the time zoom and the zoom alike, PW-275): LOCAL, its own
    bright surface, however small the patch. A big sheet's own air mass is
    in the climate's air already (air_mass, carried along the winds,
    PW-336), so it isn't counted here again."""
    return np.full(grid.n, LOCAL)


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
