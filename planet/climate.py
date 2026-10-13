"""Toy climate: temperature, prevailing wind, rainfall, then biomes.

Not a real climate model, but it has the three effects that make maps
look plausible:

- Latitude: hot equator, cold poles. Altitude: -6.5 degC per km.
- Earth-like wind bands: easterly trade winds below ~30 deg, westerlies
  from 30 to 60, polar easterlies above. Moisture is picked up over the
  ocean and carried downwind.
- Warm air holds more water than cold air (roughly +7% per degC). When
  wind pushes air up a mountain it cools, can't hold its water, and
  rains. That gives wet windward slopes and dry 'rain shadow' deserts
  behind ranges, with no special-case code.
"""

from __future__ import annotations

import numpy as np

from numba import njit

from . import kernels
from .grid import Grid

LAPSE = 6.5 / 1000  # degC per metre
R_KM = 6371.0


def temperature(grid: Grid, elev: np.ndarray, equator_temp: float = 28.0,
                pole_temp: float = -22.0) -> np.ndarray:
    s = np.abs(np.sin(np.radians(grid.lat)))
    # Exponent fitted by eye to Earth's zonal means (~27C at the equator,
    # ~0C at 60 deg, ~-20C at the poles).
    t = equator_temp + (pole_temp - equator_temp) * s**3.5
    return t - LAPSE * np.maximum(elev, 0)


def seasons(grid: Grid, elev: np.ndarray, temp: np.ndarray, tilt: float = 23.4):
    """Warmest- and coldest-month temperatures around the annual mean.
    The swing grows with latitude (the tilt makes summer days long and
    winter days short) and with distance from the sea, which evens
    temperatures out (Vancouver: 4 to 18 C; Yakutsk, 62 N inland: -39 to +19).
    Returns (t_warm, t_cold)."""
    land = elev > 0
    coast = np.flatnonzero(land & (np.add.reduceat(~land[grid.nbr_idx], grid.nbr_off[:-1]) > 0))
    hops, _ = kernels.bfs_within(coast, land.astype(np.int64), grid.nbr_off, grid.nbr_idx, 10**6)
    dist = np.where(land, np.maximum(hops, 0) * grid.spacing * R_KM + 50.0, 0.0)
    dist = np.where(land & (hops < 0), 3000.0, dist)  # land with no coast at all
    continental = 1 - np.exp(-dist / 800.0)
    half_range = (4.0 + 28.0 * continental) * np.abs(np.sin(np.radians(grid.lat))) * (tilt / 23.4)
    half_range += 1.0 * land  # even the tropics have a small swing on land
    return temp + half_range, temp - half_range


def wind(grid: Grid, shift: float = 0.0) -> np.ndarray:
    """Unit-ish tangent wind vector per cell from the three-cell model.
    shift (deg) moves the bands north, as in the northern summer."""
    p = grid.centers
    east = np.cross([0.0, 0.0, 1.0], p)
    east /= np.maximum(np.linalg.norm(east, axis=1, keepdims=True), 1e-9)
    north = np.cross(p, east)
    lat = grid.lat - shift
    a = np.abs(lat)
    hemi = np.sign(lat)[:, None]
    # (east component, poleward component) per band
    ue = np.where(a < 30, -1.0, np.where(a < 60, 1.0, -0.8))[:, None]
    un = np.where(a < 30, -0.35, np.where(a < 60, 0.35, -0.35))[:, None]
    return ue * east + un * hemi * north


def _qsat(t):
    return np.exp(0.07 * t)


@njit(cache=True)
def _rain(qs, ocean, base_rate, src, dst, out_w, deg, iterations, diffusion):
    """Humidity carried along the wind, raining out what it can't hold plus a
    steady drizzle; averaged over the last quarter of the iterations."""
    n = qs.shape[0]
    m = np.zeros(n)
    for i in range(n):
        if ocean[i]:
            m[i] = qs[i]
    acc = np.zeros(n)
    moved = np.empty(n)
    mixed = np.empty(n)
    tail = max(iterations // 4, 1)
    for it in range(iterations):
        for i in range(n):
            if ocean[i] and qs[i] > m[i]:
                m[i] = qs[i]
            excess = max(m[i] - qs[i], 0.0)
            r = excess + base_rate[i] * (m[i] - excess)
            m[i] -= r
            if it >= iterations - tail:
                acc[i] += r
        moved[:] = 0.0
        mixed[:] = 0.0
        for e in range(src.shape[0]):
            moved[dst[e]] += m[src[e]] * out_w[e]
            mixed[dst[e]] += m[src[e]]
        for i in range(n):
            m[i] = (1 - diffusion) * moved[i] + diffusion * mixed[i] / deg[i]
    return acc / tail


_TRANSPORT = {}


def _transport(grid: Grid, shift: float):
    """Wind-transport weights along every directed edge, and the background
    rain rate per cell. Depends only on the grid and the season, so cached."""
    key = (id(grid), grid.n, round(shift, 3))
    if key in _TRANSPORT:
        return _TRANSPORT[key]
    n = grid.n
    w = wind(grid, shift)
    src = np.concatenate([grid.edges[:, 0], grid.edges[:, 1]])
    dst = np.concatenate([grid.edges[:, 1], grid.edges[:, 0]])
    d = grid.centers[dst] - grid.centers[src]
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    out_w = np.maximum((w[src] * d).sum(1), 0)
    out_w /= np.maximum(np.bincount(src, out_w, n)[src], 1e-9)
    deg = np.bincount(src, minlength=n).astype(np.float64)

    # Large-scale circulation: rising air at the equator and ~55 deg is
    # rainy; sinking air at ~25 deg (Sahara, Australia) and the poles is dry.
    lat = np.abs(grid.lat - shift)
    belt = 0.35 + 0.9 * np.exp(-((lat / 12) ** 2)) + 0.45 * np.exp(-(((lat - 55) / 12) ** 2)) \
        - 0.25 * np.exp(-(((lat - 25) / 8) ** 2))
    base_rate = 0.05 * np.clip(belt, 0.05, None)
    if len(_TRANSPORT) > 12:
        _TRANSPORT.clear()
    _TRANSPORT[key] = (src, dst, out_w, deg, base_rate)
    return _TRANSPORT[key]


def precipitation(grid: Grid, elev: np.ndarray, temp: np.ndarray,
                  iterations: int | None = None, diffusion: float = 0.15, shift: float = 0.0,
                  scale: float | None = None):
    """Advect humidity along the wind and rain it out. Returns mm/year.
    shift (deg) moves the wind and rain belts north (northern summer) or
    south. scale: mm/yr per model unit; by default it's set so a warm wet
    coast gets ~2000 mm/yr, and returned as a second value."""
    n = grid.n
    ocean = elev <= 0
    src, dst, out_w, deg, base_rate = _transport(grid, shift)

    qs = _qsat(temp)
    if iterations is None:
        iterations = int(50 * 2 ** (grid.level - 5))
    rain = _rain(qs, ocean, base_rate, src, dst, out_w, deg, iterations, diffusion)
    if scale is not None:
        return np.clip(rain * scale, 0, 6000)
    # Scale so a warm, wet coast lands near ~2000 mm/yr.
    ref = np.quantile(rain[~ocean], 0.9) if (~ocean).any() else rain.max()
    return np.clip(rain / max(ref, 1e-9) * 2000, 0, 6000), 2000 / max(ref, 1e-9)


def seasonal_precipitation(grid: Grid, elev: np.ndarray, temp: np.ndarray, t_warm: np.ndarray,
                           t_cold: np.ndarray, tilt: float = 23.4, wetness: float = 1.0):
    """Rain in the northern summer and winter halves of the year, with the
    wind and rain belts following the sun (the tropical rain belt swings
    ~8 deg; monsoons, Mediterranean dry summers). Returns mm/yr rates
    (annual, northern-summer half, northern-winter half). wetness scales it
    all (a warmer world is a wetter one)."""
    shift = 8.0 * tilt / 23.4
    north = grid.lat >= 0
    t_jul = np.where(north, t_warm, t_cold)
    t_jan = np.where(north, t_cold, t_warm)
    annual, scale = precipitation(grid, elev, temp)
    jul = precipitation(grid, elev, t_jul, shift=shift, scale=scale)
    jan = precipitation(grid, elev, t_jan, shift=-shift, scale=scale)
    # keep the annual total from the annual-mean pass; seasons set the split
    tot = np.maximum(jul + jan, 1e-9)
    annual = annual * wetness
    return annual, 2 * annual * jul / tot, 2 * annual * jan / tot


# --------------------------------------------------------------------------
# Koppen climate classes (Peel et al. 2007 rules; colours from their map)
# --------------------------------------------------------------------------
KOPPEN = [
    # id, code, name, colour
    (0, "Af", "tropical rainforest", "#0000fe"),
    (1, "Am", "tropical monsoon", "#0077ff"),
    (2, "Aw", "tropical savanna", "#46a9fa"),
    (3, "BWh", "hot desert", "#fe0000"),
    (4, "BWk", "cold desert", "#fe9695"),
    (5, "BSh", "hot steppe", "#f5a301"),
    (6, "BSk", "cold steppe", "#ffdb63"),
    (7, "Csa", "Mediterranean, hot summer", "#ffff00"),
    (8, "Csb", "Mediterranean, warm summer", "#c6c700"),
    (9, "Csc", "Mediterranean, cool summer", "#969600"),
    (10, "Cwa", "subtropical, dry winter", "#96ff96"),
    (11, "Cwb", "subtropical highland, dry winter", "#63c764"),
    (12, "Cwc", "subpolar highland, dry winter", "#329633"),
    (13, "Cfa", "humid subtropical", "#c6ff4e"),
    (14, "Cfb", "oceanic", "#66ff33"),
    (15, "Cfc", "subpolar oceanic", "#33c701"),
    (16, "Dsa", "continental, dry hot summer", "#ff00fe"),
    (17, "Dsb", "continental, dry warm summer", "#c600c7"),
    (18, "Dsc", "subarctic, dry summer", "#963295"),
    (19, "Dsd", "subarctic, dry summer, severe winter", "#966495"),
    (20, "Dwa", "continental, dry winter, hot summer", "#abb1ff"),
    (21, "Dwb", "continental, dry winter, warm summer", "#5a77db"),
    (22, "Dwc", "subarctic, dry winter", "#4c51b5"),
    (23, "Dwd", "subarctic, dry winter, severe", "#320087"),
    (24, "Dfa", "humid continental, hot summer", "#00ffff"),
    (25, "Dfb", "humid continental, warm summer", "#38c7ff"),
    (26, "Dfc", "subarctic", "#007e7d"),
    (27, "Dfd", "subarctic, severe winter", "#00455e"),
    (28, "ET", "tundra", "#b2b2b2"),
    (29, "EF", "ice cap", "#686868"),
    (30, "-", "sea", "#1d3f6e"),
]
SEA_CLASS = 30


def koppen(elev, temp, t_warm, t_cold, p_ann, p_jul, p_jan, lat, ice=None):
    """Koppen class per cell. Monthly values aren't modelled, so they're
    estimated from the two half-years assuming a smooth (sinusoidal) annual
    cycle of temperature and of rain."""
    north = lat >= 0
    p_sum = np.where(north, p_jul, p_jan) / 12  # monthly mean, summer half (mm)
    p_win = np.where(north, p_jan, p_jul) / 12
    # rain(month) = mean * (1 + a cos): the half-year means are mean*(1 +- 2a/pi),
    # the extremes mean*(1 +- a), and where the halves meet it's the mean
    mean = (p_sum + p_win) / 2
    a = np.clip((p_sum - p_win) / np.maximum(p_sum + p_win, 1e-9) * np.pi / 2, -1, 1)
    lo, hi = mean * (1 - np.abs(a)), mean * (1 + np.abs(a))
    summer_dry = a < 0
    dry_s, wet_s = np.where(summer_dry, lo, mean), np.where(summer_dry, mean, hi)
    dry_w, wet_w = np.where(summer_dry, mean, lo), np.where(summer_dry, hi, mean)
    driest = lo
    P, T = p_ann, temp
    # months above 10 C on a sinusoidal year
    amp = np.maximum((t_warm - t_cold) / 2, 1e-6)
    m10 = 12 * np.arccos(np.clip((10 - T) / amp, -1, 1)) / np.pi
    out = np.full(len(elev), -1)

    def put(mask, cid):
        sel = mask & (out < 0)
        out[sel] = cid[sel] if np.ndim(cid) else cid

    sea = elev <= 0
    out[sea] = SEA_CLASS
    if ice is not None:
        put(ice > 0, 29)
    put(t_warm < 0, 29)
    put(t_warm < 10, 28)
    summer_share = p_sum / np.maximum(p_sum + p_win, 1e-9)
    pth = 20 * T + np.where(summer_share >= 0.7, 280, np.where(summer_share >= 0.3, 140, 0))
    hot = T >= 18
    put(P < 0.5 * pth, np.where(hot, 3, 4))
    put(P < pth, np.where(hot, 5, 6))
    trop = t_cold >= 18
    put(trop & (driest >= 60), 0)
    put(trop & (driest >= 100 - P / 25), 1)
    put(trop, 2)
    s_ = (dry_s < 40) & (dry_s < wet_w / 3)
    w_ = (dry_w < wet_s / 10)
    third = np.where(t_warm >= 22, 0, np.where(m10 >= 4, 1, np.where(t_cold < -38, 3, 2)))
    third_c = np.minimum(third, 2)  # C climates have no 'd'
    temperate = t_cold > -3
    put(temperate & s_, 7 + third_c)
    put(temperate & w_, 10 + third_c)
    put(temperate, 13 + third_c)
    put(s_, 16 + third)
    put(w_, 20 + third)
    put(np.ones(len(elev), bool), 24 + third)
    return out


# --------------------------------------------------------------------------
# Biomes: a rough Whittaker diagram (mean annual temperature x rainfall)
# --------------------------------------------------------------------------
BIOMES = [
    # id, name, ascii char, colour
    (0, "deep ocean", "~", "#1d3f6e"),
    (1, "shallow sea", "-", "#3a6ea5"),
    (2, "sea ice", "=", "#d8e6ef"),
    (3, "lake", "o", "#4f8fcf"),
    (4, "ice sheet", "I", "#f4f7fa"),
    (5, "tundra", "t", "#9aa58a"),
    (6, "boreal forest", "B", "#3f6b4d"),
    (7, "cold desert", "c", "#b7ad8f"),
    (8, "temperate grassland", "g", "#a9b964"),
    (9, "temperate forest", "F", "#4d8a3a"),
    (10, "temperate rainforest", "R", "#2f6e4a"),
    (11, "hot desert", "d", "#e0c68a"),
    (12, "savanna", "s", "#c2b553"),
    (13, "tropical seasonal forest", "S", "#6a9a2f"),
    (14, "tropical rainforest", "J", "#2a7a2a"),
    (15, "alpine / bare rock", "^", "#8b8178"),
]


def biomes(elev: np.ndarray, temp: np.ndarray, precip: np.ndarray,
           lake: np.ndarray | None = None) -> np.ndarray:
    t, p = temp, precip
    b = np.full(len(elev), -1)
    land = elev > 0

    def land_rule(mask, bid):
        sel = land & mask & (b < 0)
        b[sel] = bid

    if lake is not None:
        b[land & lake] = 3
    land_rule(t < -9, 4)
    land_rule((elev > 3200) & (t < 3), 15)
    land_rule(t < -2, 5)
    land_rule((t < 6) & (p < 250), 7)
    land_rule(t < 6, 6)
    land_rule((t < 18) & (p < 300), 7)
    land_rule((t < 18) & (p < 700), 8)
    land_rule((t < 18) & (p < 1800), 9)
    land_rule(t < 18, 10)
    land_rule(p < 350, 11)
    land_rule(p < 1000, 12)
    land_rule(p < 1900, 13)
    land_rule(np.ones_like(land), 14)

    sea = ~land
    b[sea & (t < -10)] = 2
    b[sea & (b < 0) & (elev < -1500)] = 0
    b[sea & (b < 0)] = 1
    return b
