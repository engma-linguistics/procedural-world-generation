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
  - thick ice (ALBEDO_H) is ALBEDO_SHARE x climate.TUNE['ice_cooling'] (2 C)
    colder all year (inversion, katabatic air);
  - where perennial snow lies (bright: last year's snow outlasted the
    summer; bare ice keeps BARE_SHARE of this), temperatures above 0 C are
    scaled by MELT_HOLD (a melting surface holds the air over it near 0 C:
    Greenland's ablation zone ~+3..5 C in July where the tundra beside it at
    the same height has ~+8..10 C), and
  - the summer's warmth above the annual mean is damped by SUMMER_DAMP x
    the sheet's cover (climate.ice_cover: the share of the land within
    ~300 km under ice, away from the tropics): a big sheet makes its own
    cold, bright air mass (Antarctica's coast stays below 0 C in summer),
    while a margin or small cap sits in the air of the land around it.
    Before PW-190 the damping was 0.6 everywhere on bright snow, so a sheet's
    margin had a summer ~10 C colder than the tundra beside it and kept
    spreading onto land with ~9 C bare summers.
"""

from __future__ import annotations

import numpy as np

SNOW_H = 20.0  # m: perennial snow / ice this thick is bright (phased in from 0)
SUMMER_DAMP = 0.6  # share of the summer's warmth above the annual mean taken away on a big sheet (x cover)
MELT_HOLD = 0.5  # temperatures above 0 C on snow / ice are scaled by this
SNOW_W = 30.0  # mm w.e.: lying snow this deep is fully bright
BARE_SHARE = 0.3  # bare ice keeps this share of the snow's effects
ALBEDO_SHARE = 0.2  # thick ice is this x climate.TUNE['ice_cooling'] colder all year ...
ALBEDO_H = 800.0  # ... in full from this thickness (m)
EDGE_H = float(np.sqrt(2 * 50e3 / (917.0 * 9.81) * 10e3))  # m (~330): a sheet's margin (a steady Nye profile
# with a 50 kPa yield stress, 10 km in from its edge): at ~110 km cells a margin cell's snow and melt are its edge's
PDD_SIGMA = 5.0  # C: day-to-day spread of temperature around the monthly mean
DDF_SNOW = 3.0  # mm w.e. melted per positive degree-day, snow (Braithwaite 1995)
DDF_ICE = 8.0  # ... ice
REFREEZE = 0.6  # share of snowmelt that refreezes in the snowpack
PRECIP_K = 0.07  # rain ~ exp(PRECIP_K * dT) (Clausius-Clapeyron)
SHEET_KM = 1000.0  # km: a sheet's own air mass (sheet_cover) ...
LOCAL = 0.3  # ... and the share of the damping any bright snow gets, however small its patch


def sheet_cover(grid, ice, km: float = SHEET_KM):
    """How much (0..1) of SUMMER_DAMP the ice surface gets: the share of
    the surface (land and sea) within ~km under land ice (m > 1), away from
    the tropics (none within 15 deg of the equator, in full from 50 deg, as
    climate.ice_cover). Antarctica ~0.6..1 (its summer is ~11..17 C colder
    than the climate model's bare ground there), Greenland ~0.3..0.5 (~4..5 C),
    a valley glacier or a lone cap ~0."""
    from . import climate
    a = climate.smooth_big(grid, (np.asarray(ice) > 1).astype(float), km)
    polar = np.clip((np.abs(grid.lat) - 15.0) / 35.0, 0.0, 1.0)
    return LOCAL + (1 - LOCAL) * np.clip(a, 0.0, 1.0) * polar


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
        from .timezoom import insolation
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
    from . import climate
    from .timezoom_kernels import climate_step
    n = len(lat)
    h = np.broadcast_to(np.asarray(h, float), (n,)).copy()
    land = np.asarray(land, bool)
    t_warm, t_cold = np.asarray(t_warm, float), np.asarray(t_cold, float)
    dt_wet = np.zeros(n) if dt_glob is None else np.broadcast_to(np.asarray(dt_glob, float), (n,)).copy()
    f_ice, f_alb = np.clip(h / ALBEDO_H, 0, 1), np.clip(h / SNOW_H, 0, 1)
    damp = SUMMER_DAMP * np.broadcast_to(np.clip(np.asarray(cover, float), 0, 1), (n,))
    smb, t_ann, t_w, t_c, p_scale, f_sum = (np.zeros(n) for _ in range(6))
    lat = np.asarray(lat, float)
    args = (land, lat >= 0, 0.5 * (t_warm + t_cold), 0.5 * np.maximum(t_warm - t_cold, 0),
            np.asarray(p_jul, float), np.asarray(p_jan, float), -climate.LAPSE * h + dt_wet, dt_wet)
    rest = (f_ice, f_alb, climate.TUNE["ice_cooling"] * ALBEDO_SHARE, damp, MELT_HOLD, BARE_SHARE, SNOW_W,
            PDD_SIGMA, DDF_SNOW, DDF_ICE, REFREEZE, PRECIP_K)
    climate_step(*args, np.zeros(n), np.zeros(n, np.int64), np.zeros((1, 12)), *rest, smb, t_ann, t_w, t_c,
                 p_scale, f_sum)
    if tilt is None:
        return smb, t_w
    from .timezoom import BAND_DEG, BAND_LAT
    band = np.clip(((lat + 90) / BAND_DEG).astype(np.int64), 0, len(BAND_LAT) - 1)
    a = 1 - f_alb * (1 - ICE_ABSORB) if absorb is None else np.broadcast_to(np.asarray(absorb, float), (n,))
    k_orb = np.where(land, INSOL_K, INSOL_K * INSOL_SEA) * a
    tot, one = np.zeros(n), np.zeros(n)
    states = cycle_dq(tilt)
    for dq in states:
        climate_step(*args, k_orb, band, dq, *rest, one, t_ann, t_c, t_c, p_scale, f_sum)
        tot += one
    return tot / len(states), t_w
