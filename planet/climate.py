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


# --------------------------------------------------------------------------
# Grid helpers: smoothing, gradients, transport along a vector field
# --------------------------------------------------------------------------
_GEOM = {}


def _geom(grid: Grid):
    """Per-grid constants: local east/north unit vectors, directed edges and
    their tangent directions. Cached."""
    key = (id(grid), grid.n)
    if key not in _GEOM:
        p = grid.centers
        east = np.cross([0.0, 0.0, 1.0], p)
        east /= np.maximum(np.linalg.norm(east, axis=1, keepdims=True), 1e-9)
        north = np.cross(p, east)
        src = np.concatenate([grid.edges[:, 0], grid.edges[:, 1]])
        dst = np.concatenate([grid.edges[:, 1], grid.edges[:, 0]])
        d = p[dst] - p[src]
        d -= (d * p[src]).sum(1, keepdims=True) * p[src]
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        deg = np.bincount(src, minlength=grid.n).astype(np.float64)
        if len(_GEOM) > 4:
            _GEOM.clear()
        _GEOM[key] = dict(east=east, north=north, src=src, dst=dst, d=d, deg=deg)
    return _GEOM[key]


@njit(cache=True)
def _smooth(f, nbr_off, nbr_idx, iters, w):
    f = f.copy()
    g = np.empty_like(f)
    for _ in range(iters):
        for i in range(f.shape[0]):
            s = 0.0
            for e in range(nbr_off[i], nbr_off[i + 1]):
                s += f[nbr_idx[e]]
            g[i] = (1 - w) * f[i] + w * s / (nbr_off[i + 1] - nbr_off[i])
        f[:] = g
    return f


def smooth(grid: Grid, f: np.ndarray, km: float) -> np.ndarray:
    """Blur a field over roughly `km` (Gaussian-ish sigma)."""
    h = grid.spacing * R_KM
    iters = int(round(4 * (km / h) ** 2))
    if iters <= 0:
        return f.astype(np.float64)
    return _smooth(np.ascontiguousarray(f, np.float64), grid.nbr_off, grid.nbr_idx, iters, 0.5)


def gradient(grid: Grid, f: np.ndarray) -> np.ndarray:
    """Tangent gradient per cell, units of f per km."""
    G = _geom(grid)
    df = f[G["dst"]] - f[G["src"]]
    g = np.zeros((grid.n, 3))
    np.add.at(g, G["src"], G["d"] * df[:, None])
    h = grid.spacing * R_KM
    return g * (2.0 / (G["deg"][:, None] * h))


def _edge_weights(grid: Grid, v: np.ndarray, allowed: np.ndarray | None = None):
    """Share of each cell's outflow along each directed edge, for flow v.
    allowed: optional per-edge mask (e.g. sea-to-sea only for currents)."""
    G = _geom(grid)
    src = G["src"]
    w = np.maximum((v[src] * G["d"]).sum(1), 0)
    if allowed is not None:
        w = w * allowed
    tot = np.bincount(src, w, grid.n)
    return w / np.maximum(tot[src], 1e-12), tot > 1e-12


@njit(cache=True)
def _relax_along(a, b, src, dst, out_w, deg, nbr_off, nbr_idx, iters, diffusion):
    """Steady state of x = a + b * (upstream x): each cell sees the
    flow-weighted mean of the cells feeding it (its own value if none), mixed
    a little with its neighbours. Used to carry heat with ocean currents and
    sea air inland."""
    n = a.shape[0]
    x = a.copy()
    num = np.empty(n)
    den = np.empty(n)
    for _ in range(iters):
        num[:] = 0.0
        den[:] = 0.0
        for e in range(src.shape[0]):
            num[dst[e]] += out_w[e] * x[src[e]]
            den[dst[e]] += out_w[e]
        for i in range(n):
            up = (num[i] + 1e-3 * x[i]) / (den[i] + 1e-3)
            s = 0.0
            for e in range(nbr_off[i], nbr_off[i + 1]):
                s += x[nbr_idx[e]]
            up = (1 - diffusion) * up + diffusion * s / deg[i]
            num[i] = a[i] + b[i] * up
        x[:] = num
    return x


def carry(grid: Grid, v: np.ndarray, a: np.ndarray, b: np.ndarray, km: float = 8000.0,
          diffusion: float = 0.1, allowed=None) -> np.ndarray:
    """Solve x = a + b * (upstream x) along flow v, far enough for signals
    to travel ~km."""
    G = _geom(grid)
    out_w, _ = _edge_weights(grid, v, allowed)
    iters = int(km / (grid.spacing * R_KM)) + 10
    return _relax_along(a.astype(np.float64), b.astype(np.float64), G["src"], G["dst"], out_w, G["deg"],
                        grid.nbr_off, grid.nbr_idx, iters, diffusion)


def zonal_mean(grid: Grid, f: np.ndarray, mask: np.ndarray | None = None, width: float = 3.0):
    """Mean of f in latitude bands `width` deg wide, given back per cell."""
    bins = np.clip(((grid.lat + 90) // width).astype(int), 0, int(180 // width) - 1)
    m = np.ones(grid.n, bool) if mask is None else mask
    nb = int(180 // width)
    tot = np.bincount(bins[m], f[m], nb)
    cnt = np.bincount(bins[m], minlength=nb)
    allm = np.bincount(bins, f, nb) / np.maximum(np.bincount(bins, minlength=nb), 1)
    zm = np.where(cnt > 0, tot / np.maximum(cnt, 1), allm)
    return zm[bins]


# --------------------------------------------------------------------------
# Wind
# --------------------------------------------------------------------------
def wind(grid: Grid, shift: float = 0.0) -> np.ndarray:
    """The planet-wide three-cell pattern, the same at every longitude:
    easterly trade winds below ~30 deg, westerlies from 30 to 60, polar
    easterlies above. shift (deg) moves the bands north (northern summer)."""
    G = _geom(grid)
    lat = grid.lat - shift
    a = np.abs(lat)
    hemi = np.sign(lat)[:, None]
    # east component: trades strongest ~12 deg, calm 'horse latitudes' ~30,
    # westerlies strongest ~48, weak polar easterlies; poleward component:
    # toward the equator under the trades, poleward under the westerlies
    ue = (-0.9 * np.exp(-((a - 12) / 14) ** 2) + 1.0 * np.exp(-((a - 48) / 13) ** 2)
          - 0.4 * np.exp(-((a - 78) / 10) ** 2))[:, None]
    un = (-0.3 * np.sin(np.radians(6 * np.minimum(a, 90))))[:, None]
    return ue * G["east"] + un * hemi * G["north"]


def monsoon_wind(grid: Grid, t_sl: np.ndarray, shift: float, strength: float = 1.0):
    """Zonal bands plus the winds made by land-sea temperature contrasts.
    Air over ground warmer than its latitude's average rises (low pressure),
    over cooler ground it sinks (high pressure). Away from the equator the
    Earth's spin turns the flow around the lows and highs (counter-clockwise
    around lows in the north): summer continents pull in moist sea air
    (monsoons) and the cooler oceans hold subtropical highs whose western
    sides send warm moist air up the east coasts (Florida, China) while
    their eastern sides blow dry along the west coasts (California, Chile).
    Winter continents push cold dry air out (Siberian high). t_sl: surface
    temperature reduced to sea level, C. Returns (wind, warmth): warmth is
    the smoothed temperature excess, C (>0: rising air, <0: sinking)."""
    anom = t_sl - zonal_mean(grid, t_sl)
    warmth = smooth(grid, anom, 900.0)
    P = -warmth  # warm -> low pressure
    g = gradient(grid, P) * 1000.0  # per 1000 km
    up = grid.centers
    geo = np.cross(up, g) * np.sign(grid.lat)[:, None]
    w = np.clip(np.abs(grid.lat) / 15.0, 0, 1)[:, None]
    v = w * (0.9 * geo - 0.45 * g) - (1 - w) * g
    v = strength * 0.3 * v
    # The land-sea circulation is shallow; it never fully overrides the big
    # wind belts, least of all in the strong mid- and high-latitude westerlies.
    m = np.linalg.norm(v, axis=1, keepdims=True)
    cap = 0.7 * strength * np.clip((65 - np.abs(grid.lat)) / 25, 0.3, 1)[:, None]
    v = v * np.minimum(1, cap / np.maximum(m, 1e-9))
    return wind(grid, shift) + v, warmth


def speed(v):
    return np.linalg.norm(v, axis=1)


# --------------------------------------------------------------------------
# Ocean currents and sea-surface temperature
# --------------------------------------------------------------------------
def currents(grid: Grid, ocean: np.ndarray, wind_v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Surface currents, as the big wind-driven gyres make them: the wind's
    east-west push (westward under the trade winds, eastward under the
    westerlies), plus currents along the coasts that close each gyre. In the
    subtropical gyres water runs poleward along the western side of an ocean
    (east coasts of continents: the warm Gulf Stream, Kuroshio, Brazil
    current) and back toward the equator along its eastern side (west
    coasts: the cold California, Humboldt, Canary, Benguela currents);
    poleward of ~45 deg the subpolar gyres turn the other way (cold
    Labrador and Oyashio currents, the mild North Atlantic drift reaching
    Norway). Only seas wide enough for a gyre get the coastal currents.
    Returns (current vectors, unit vectors pointing away from nearest land)."""
    G = _geom(grid)
    up = grid.centers
    ue = smooth(grid, np.where(ocean, (wind_v * G["east"]).sum(1), 0.0), 300.0)
    v = ue[:, None] * G["east"]
    coast = np.flatnonzero(ocean & (np.add.reduceat(~ocean[grid.nbr_idx], grid.nbr_off[:-1]) > 0))
    hops, _ = kernels.bfs_within(coast, ocean.astype(np.int64), grid.nbr_off, grid.nbr_idx, 8)
    dl = np.where(ocean, np.where(hops >= 0, hops + 1.0, 9.0), 0.0)
    away = gradient(grid, smooth(grid, dl, 150.0))
    away /= np.maximum(np.linalg.norm(away, axis=1, keepdims=True), 1e-9)
    near = ocean & (hops >= 0)
    # which side of its ocean a cell is on: +1 western side (land to the west)
    side = np.clip(3 * (away * G["east"]).sum(1), -1, 1)
    a = np.abs(grid.lat)
    band = np.clip((45 - a) / 6, -1, 1) * np.clip((80 - a) / 6, 0, 1) * np.clip((a - 3) / 5, 0, 1)
    wide = np.clip((smooth(grid, ocean.astype(float), 1200.0) - 0.45) / 0.3, 0, 1)
    poleward = side * band * wide * np.exp(-np.maximum(hops, 0) / 2.5) * near
    hemi = np.sign(grid.lat)[:, None]
    v = v + 1.5 * poleward[:, None] * hemi * G["north"]
    into = np.minimum((v * away).sum(1, keepdims=True), 0)
    v = np.where((near & (hops <= 2))[:, None], v - into * away, v)
    v -= (v * up).sum(1, keepdims=True) * up
    return np.where(ocean[:, None], v, 0.0), np.where((near & (hops <= 2))[:, None], away, 0.0)


def sea_surface(grid: Grid, ocean: np.ndarray, t_eq: np.ndarray, wind_v: np.ndarray,
                relax_km: float = 2500.0, upwelling: float = 5.0) -> tuple[np.ndarray, np.ndarray]:
    """Sea-surface temperature: the latitude's temperature t_eq, moved by the
    currents (warm water poleward along the western side of each ocean, cold
    water toward the equator along the eastern side), plus coastal upwelling
    where the wind pushes surface water away from a coast (Peru, California,
    Namibia). Each band's average is kept. Returns (sst, current)."""
    G = _geom(grid)
    cur, away = currents(grid, ocean, wind_v)
    # Ekman transport: 90 deg to the right of the wind in the north, left in the south
    ek = np.cross(wind_v, grid.centers) * np.sign(grid.lat)[:, None]
    off = np.clip((ek * away).sum(1), 0, 1.5)
    lat_ok = np.clip((np.abs(grid.lat) - 5) / 8, 0, 1) * np.clip((45 - np.abs(grid.lat)) / 8, 0, 1)
    cold = upwelling * off * lat_ok
    src = G["src"]
    allowed = (ocean[src] & ocean[G["dst"]]).astype(np.float64)
    keep = np.exp(-grid.spacing * R_KM / relax_km)
    a = np.where(ocean, (1 - keep) * (t_eq - cold), t_eq)
    b = np.where(ocean, keep, 0.0)
    sst = carry(grid, cur, a, b, km=3 * relax_km, diffusion=0.15, allowed=allowed)
    anom = np.where(ocean, sst - t_eq, 0.0)
    anom -= np.where(ocean, zonal_mean(grid, anom, ocean), 0.0)
    return t_eq + anom, cur


# --------------------------------------------------------------------------
# Rain
# --------------------------------------------------------------------------
def _qsat(t, k=0.07):
    return np.exp(k * t)


@njit(cache=True)
def _rain(qs, src_q, ocean, base_rate, fex, recycle, move, src, dst, out_w, deg, nbr_off, nbr_idx,
          iterations, diffusion, rh_c, rh_pow):
    """Humidity carried along the wind. Over the sea the air takes up water
    to src_q. Everywhere it rains a share fex of what it can't hold (qs)
    plus a share base_rate of the rest, which needs the air to be fairly
    humid (relative humidity m/qs near rh_c or more: hot desert air carries
    plenty of water but rarely rains it); on land part of the rain
    evaporates again (recycle). move: share of the air that moves on per
    iteration (slow winds linger). Averaged over the last quarter."""
    n = qs.shape[0]
    m = src_q.copy()
    acc = np.zeros(n)
    moved = np.empty(n)
    tail = max(iterations // 4, 1)
    for it in range(iterations):
        for i in range(n):
            if ocean[i] and src_q[i] > m[i]:
                m[i] = src_q[i]
            excess = max(m[i] - qs[i], 0.0)
            rh = min(m[i] / max(qs[i], 1e-12) / rh_c, 1.0)
            r = fex * excess + base_rate[i] * (m[i] - excess) * rh**rh_pow
            m[i] -= r * (1 - recycle[i])
            if it >= iterations - tail:
                acc[i] += r
        for i in range(n):
            moved[i] = (1 - move[i]) * m[i]
        for e in range(src.shape[0]):
            moved[dst[e]] += move[src[e]] * m[src[e]] * out_w[e]
        for i in range(n):
            s = 0.0
            for e in range(nbr_off[i], nbr_off[i + 1]):
                s += moved[nbr_idx[e]]
            m[i] = (1 - diffusion) * moved[i] + diffusion * s / deg[i]
    return acc / tail


TUNE = dict(
    rh=0.85,  # sea air's humidity relative to saturation at the sea surface
    q_k=0.06,  # per C: how much more water warm air holds (Clausius-Clapeyron ~0.07)
    lapse_q=0.5,  # share of the cooling with height that wrings water out of rising air
    fex=0.25,  # share of the oversaturated water that rains out in one cell (rest further on)
    base=0.035,  # background rain-out per cell, times the belt pattern
    recycle=0.35,  # share of land rain that evaporates back into the air (warm, wet land)
    belt_shift=10.0,  # deg the tropical rain belt follows the sun (times tilt/23.4)
    monsoon=1.0,  # strength of the land-sea pressure winds
    belt_dry=0.3,  # how dry the subtropics are everywhere (the land-sea pattern adds more where it applies)
    convect=0.4,  # per C of warmth excess: more rain where air rises over warm ground
    storm=0.6,  # rain from the mid-latitude storm tracks (~50 deg)
    rh_c=0.8,  # relative humidity above which the background rain runs at full rate...
    rh_pow=3.0,  # ...and how fast it falls off below it
    continental=20.0,  # C: extra seasonal swing (times sin lat) far from sea air
    mean_mm=1000.0,  # global mean precipitation, mm/yr (Earth ~1000)
)


def _belt(lat, shift, dry=0.25, storm=0.45, rise=None):
    """Large-scale rising (wet) and sinking (dry) air by latitude: the
    tropical rain belt, the dry subtropics (~25 deg), the mid-latitude
    storm tracks (~50 deg), dry poles."""
    a = np.abs(lat - shift)
    # (where the land-sea pattern makes air rise, e.g. a summer monsoon,
    # it overrides the subtropical sinking)
    sink = dry if rise is None else dry * np.clip(1 - rise / 4.0, 0, 1)
    return np.clip(0.45 + 0.85 * np.exp(-((lat - shift) / 10) ** 2) + storm * np.exp(-((a - 50) / 14) ** 2)
                   - sink * np.exp(-((a - 25) / 9) ** 2), 0.1, None)


def rain_season(grid: Grid, elev, t_air, sst, v, shift, rise=None, tune=TUNE):
    """Rain rate (model units) for one season. rise: warmth excess (C) from
    monsoon_wind; air rises (and rains) over ground warmer than its
    latitude, sinks (dry) over cooler ground."""
    G = _geom(grid)
    ocean = elev <= 0
    # rising air cools, but less than the ground does: only part of the
    # cooling with height wrings water out (plateau edges otherwise strip it all)
    land_t = t_air + (1 - tune["lapse_q"]) * LAPSE * np.maximum(elev, 0)
    qs = np.where(ocean, _qsat(sst, tune["q_k"]), _qsat(land_t, tune["q_k"]))
    src_q = np.where(ocean, tune["rh"] * qs, 0.0)
    out_w, _ = _edge_weights(grid, v)
    move = np.clip(speed(v), 0.25, 1.0)
    rec = np.where(ocean, 0.0, tune["recycle"] * np.clip(t_air / 15.0, 0, 1))
    base = tune["base"] * _belt(grid.lat, shift, tune["belt_dry"], tune["storm"], rise)
    if rise is not None:
        base = base * np.clip(1 + tune["convect"] * rise, 0.25, 3.0)
    iters = int(60 * 2 ** (grid.level - 5)) + 40
    return _rain(qs, src_q, ocean, base, tune["fex"], rec, move, G["src"], G["dst"], out_w, G["deg"],
                 grid.nbr_off, grid.nbr_idx, iters, 0.12, tune["rh_c"], tune["rh_pow"])


def precipitation(grid: Grid, elev: np.ndarray, temp: np.ndarray, **_):
    """Annual rain without seasons (generators' quick path). Returns
    (mm/yr, scale)."""
    r = rain_season(grid, elev, temp, temp, wind(grid), 0.0)
    scale = TUNE["mean_mm"] / max(r.mean(), 1e-12)
    return np.clip(r * scale, 0, 6000), scale


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


def compute(grid: Grid, elev: np.ndarray, dT: float = 0.0, tilt: float = 23.4,
            ice: np.ndarray | None = None, tune: dict | None = None) -> dict:
    """The whole climate for one moment: elevation (m above the current sea
    level; <= 0 is sea), the global temperature offset dT from today's Earth,
    axial tilt and land ice (m). Returns a dict of per-cell arrays:
      temp, t_warm, t_cold   C: annual mean, warmest and coldest month
      precip, p_jul, p_jan   mm/yr: annual, and the rate in each half-year
      koppen                 KOPPEN id
      sst                    C: sea-surface temperature (annual)
      wind_jul, wind_jan     tangent vectors, ~1 = a steady trade wind
      current                tangent vectors of the surface ocean currents
    Order: a first guess of temperatures by latitude, height and distance
    from the sea -> seasonal winds from the land-sea contrast -> ocean
    currents and sea-surface temperature -> sea air carried inland sets how
    mild each place is -> rain in each half-year."""
    tune = {**TUNE, **(tune or {})}
    n = grid.n
    ocean = elev <= 0
    land = ~ocean
    ice = np.zeros(n) if ice is None else ice
    surf = elev + ice
    tilt_adj = (tilt - 23.4) * 0.3  # more tilt: milder poles, slightly cooler tropics
    eq, pole = 28.0 + 0.5 * dT - 0.3 * tilt_adj, -22.0 + 1.5 * dT + tilt_adj
    temp0 = temperature(grid, surf, eq, pole)
    t_sea = temperature(grid, np.zeros(n), eq, pole)  # the latitude's temperature at sea level
    warm0, cold0 = seasons(grid, elev, temp0, tilt)
    north = grid.lat >= 0
    lift = LAPSE * np.maximum(surf, 0)  # back to sea level, for pressure
    shift = tune["belt_shift"] * tilt / 23.4
    v_jul, rise_jul = monsoon_wind(grid, np.where(north, warm0, cold0) + lift, shift, tune["monsoon"])
    v_jan, rise_jan = monsoon_wind(grid, np.where(north, cold0, warm0) + lift, -shift, tune["monsoon"])
    v_ann = 0.5 * (v_jul + v_jan)

    sst, cur = sea_surface(grid, ocean, t_sea, v_ann)
    anom = np.where(ocean, sst - t_sea, 0.0)
    # How much sea air reaches each place, and the sea's temperature
    # anomaly it brings (west coasts in the westerlies are mild, east coasts
    # and interiors get continental extremes).
    keep = np.exp(-grid.spacing * R_KM / 900.0)
    sea_air = carry(grid, v_ann, ocean.astype(float), np.where(ocean, 0.0, keep), diffusion=0.25)
    brought = carry(grid, v_ann, anom, np.where(ocean, 0.0, keep), diffusion=0.25)
    # also mild right at any coast (sea breezes, fog)
    coast_air = np.where(land, 0.35 * (np.add.reduceat(ocean[grid.nbr_idx].astype(float), grid.nbr_off[:-1])
                                       / np.diff(grid.nbr_off)), 1.0)
    sea_air = np.clip(np.maximum(sea_air, coast_air), 0, 1)
    temp = np.where(ocean, sst, temp0 + brought)
    s = np.abs(np.sin(np.radians(grid.lat))) * (tilt / 23.4)
    half = (np.where(ocean, 3.0, 4.0 + tune["continental"] * (1 - sea_air)) * s + 1.0 * land)
    # the sea's warmth matters most in winter (Norway vs Labrador)
    t_warm = temp + half - 0.4 * np.maximum(brought, 0)
    t_cold = temp - half + 0.4 * np.maximum(brought, 0)
    t_jul = np.where(north, t_warm, t_cold)
    t_jan = np.where(north, t_cold, t_warm)
    sst_jul = sst + np.where(north, 1, -1) * 3.0 * s
    sst_jan = sst - np.where(north, 1, -1) * 3.0 * s

    r_jul = rain_season(grid, elev, t_jul, sst_jul, v_jul, shift, rise_jul, tune)
    r_jan = rain_season(grid, elev, t_jan, sst_jan, v_jan, -shift, rise_jan, tune)
    wet = np.exp(0.03 * dT)  # a warmer world is a wetter one
    scale = tune["mean_mm"] * wet / max(0.5 * (r_jul + r_jan).mean(), 1e-12)
    p_jul, p_jan = np.clip(r_jul * scale, 0, 8000), np.clip(r_jan * scale, 0, 8000)
    precip = 0.5 * (p_jul + p_jan)
    k = koppen(elev, temp, t_warm, t_cold, precip, p_jul, p_jan, grid.lat, ice)
    return dict(temp=temp, t_warm=t_warm, t_cold=t_cold, precip=precip, p_jul=p_jul, p_jan=p_jan, koppen=k,
                sst=sst, wind_jul=v_jul, wind_jan=v_jan, current=cur)
