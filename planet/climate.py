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

from .grid import Grid

LAPSE = 6.5 / 1000  # degC per metre


def temperature(grid: Grid, elev: np.ndarray, equator_temp: float = 28.0,
                pole_temp: float = -22.0) -> np.ndarray:
    s = np.abs(np.sin(np.radians(grid.lat)))
    # Exponent fitted by eye to Earth's zonal means (~27C at the equator,
    # ~0C at 60 deg, ~-20C at the poles).
    t = equator_temp + (pole_temp - equator_temp) * s**3.5
    return t - LAPSE * np.maximum(elev, 0)


def wind(grid: Grid) -> np.ndarray:
    """Unit-ish tangent wind vector per cell from the three-cell model."""
    p = grid.centers
    east = np.cross([0.0, 0.0, 1.0], p)
    east /= np.maximum(np.linalg.norm(east, axis=1, keepdims=True), 1e-9)
    north = np.cross(p, east)
    lat = grid.lat
    a = np.abs(lat)
    hemi = np.sign(lat)[:, None]
    # (east component, poleward component) per band
    ue = np.where(a < 30, -1.0, np.where(a < 60, 1.0, -0.8))[:, None]
    un = np.where(a < 30, -0.35, np.where(a < 60, 0.35, -0.35))[:, None]
    return ue * east + un * hemi * north


def _qsat(t):
    return np.exp(0.07 * t)


def precipitation(grid: Grid, elev: np.ndarray, temp: np.ndarray,
                  iterations: int | None = None, diffusion: float = 0.15) -> np.ndarray:
    """Advect humidity along the wind and rain it out. Returns mm/year."""
    n = grid.n
    ocean = elev <= 0
    w = wind(grid)
    src = np.concatenate([grid.edges[:, 0], grid.edges[:, 1]])
    dst = np.concatenate([grid.edges[:, 1], grid.edges[:, 0]])
    d = grid.centers[dst] - grid.centers[src]
    d /= np.linalg.norm(d, axis=1, keepdims=True)
    out_w = np.maximum((w[src] * d).sum(1), 0)
    out_w /= np.maximum(np.bincount(src, out_w, n)[src], 1e-9)
    deg = np.bincount(src, minlength=n)

    # Large-scale circulation: rising air at the equator and ~55 deg is
    # rainy; sinking air at ~25 deg (Sahara, Australia) and the poles is dry.
    lat = np.abs(grid.lat)
    belt = 0.35 + 0.9 * np.exp(-((lat / 12) ** 2)) + 0.45 * np.exp(-(((lat - 55) / 12) ** 2)) \
        - 0.25 * np.exp(-(((lat - 25) / 8) ** 2))
    base_rate = 0.05 * np.clip(belt, 0.05, None)

    qs = _qsat(temp)
    if iterations is None:
        iterations = int(50 * 2 ** (grid.level - 5))
    m = np.where(ocean, qs, 0.0)
    rain_acc = np.zeros(n)
    tail = max(iterations // 4, 1)
    for it in range(iterations):
        m = np.where(ocean, np.maximum(m, qs), m)
        excess = np.maximum(m - qs, 0)
        rain = excess + base_rate * (m - excess)
        m = m - rain
        if it >= iterations - tail:
            rain_acc += rain
        moved = np.bincount(dst, m[src] * out_w, n)
        mixed = np.bincount(dst, m[src], n) / deg
        m = (1 - diffusion) * moved + diffusion * mixed
    rain = rain_acc / tail
    # Scale so a warm, wet coast lands near ~2000 mm/yr.
    ref = np.quantile(rain[~ocean], 0.9) if (~ocean).any() else rain.max()
    return np.clip(rain / max(ref, 1e-9) * 2000, 0, 6000)


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
