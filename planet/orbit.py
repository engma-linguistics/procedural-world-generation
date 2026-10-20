"""Orbit and insolation (Berger 1978), shared by the glacial time zoom
(planet/timezoom/) and the ice-age cycle's mean balance (icemass.cycle_dq).

Parameters p are duck-typed: anything with the time zoom's orbit knobs
(obliquity_amp, obliquity_period, precession_period, ecc_mean, ecc_100,
ecc_400, phases), i.e. a timezoom.TZParams.
"""

from __future__ import annotations

import math

import numpy as np

S0 = 1361.0  # W/m2, the star's light at the planet's mean distance

# Earth's orbit today: obliquity 23.44 deg, eccentricity 0.0167, perihelion
# 283 deg from the March equinox (early January)
EARTH_TODAY = dict(obl=23.44, ecc=0.0167, peri=283.0)

BAND_DEG = 1.0
BAND_LAT = np.arange(-90 + BAND_DEG / 2, 90, BAND_DEG)


def orbit_phases(p, seed: int, earth: bool = False) -> np.ndarray:
    """Phases (deg) of obliquity, perihelion longitude at t=0, the 100 kyr
    and 405 kyr eccentricity terms."""
    mode = ("eemian" if earth else "seed") if p.phases == "auto" else p.phases
    if mode == "zero":
        return np.zeros(4)
    if mode == "eemian":  # (405 kyr term at 0: eccentricity ~0.042, as at 127 ka; both peaks gave 0.052)
        return np.array([0.0, 90.0, 0.0, 90.0])
    if mode == "seed":
        return np.random.default_rng([seed, 7919]).uniform(0, 360, 4)
    return np.array([float(x) for x in p.phases.split(",")])


def orbit_at(t_kyr: float, p, tilt: float, ph: np.ndarray) -> tuple[float, float, float]:
    """(obliquity deg, eccentricity, longitude of perihelion deg) at t."""
    r = np.radians
    obl = tilt + p.obliquity_amp * math.cos(2 * math.pi * t_kyr / p.obliquity_period + r(ph[0]))
    ecc = p.ecc_mean + p.ecc_100 * math.cos(2 * math.pi * t_kyr / 100.0 + r(ph[2])) \
        + p.ecc_400 * math.cos(2 * math.pi * t_kyr / 405.0 + r(ph[3]))
    peri = (ph[1] + 360.0 * t_kyr / p.precession_period) % 360.0
    return obl, max(ecc, 0.0), peri


def insolation(obl: float, ecc: float, peri: float, lat=BAND_LAT) -> np.ndarray:
    """Daily-mean insolation (W/m2) at each latitude and the middle of each
    of 12 equal-time months, month 0 starting at the March equinox.
    peri: true longitude of the perihelion from that equinox (Earth today
    ~283 deg: early January). (Berger 1978.)"""
    e, w = ecc, np.radians(peri)
    # time -> true longitude via Kepler's equation; the equinox (true
    # longitude 0) is at true anomaly -w
    v_eq = -w
    E_eq = 2 * np.arctan(np.sqrt((1 - e) / (1 + e)) * np.tan(v_eq / 2))
    M_eq = E_eq - e * np.sin(E_eq)
    M = M_eq + 2 * np.pi * (np.arange(12) + 0.5) / 12
    E = M.copy()
    for _ in range(8):
        E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
    v = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))
    lam = v + w
    dist2 = ((1 + e * np.cos(v)) / (1 - e * e)) ** 2  # (mean distance / distance)^2
    dec = np.arcsin(np.sin(np.radians(obl)) * np.sin(lam))
    phi = np.radians(lat)[:, None]
    cos_h0 = np.clip(-np.tan(phi) * np.tan(dec)[None, :], -1, 1)
    h0 = np.arccos(cos_h0)
    q = S0 / np.pi * dist2[None, :] * (h0 * np.sin(phi) * np.sin(dec)[None, :]
                                        + np.cos(phi) * np.cos(dec)[None, :] * np.sin(h0))
    return np.maximum(q, 0.0)


def reference_orbit(p, tilt: float, phases: np.ndarray, earth: bool) -> tuple[float, float, float]:
    """The orbit the time zoom's insolation anomalies are measured against
    (p.orbit_ref): 'mean' (tilt, circular orbit), 'start' (the orbit at t=0)
    or 'today' (Earth's); 'auto': 'today' for Earth, else 'mean'."""
    ref = p.orbit_ref if p.orbit_ref != "auto" else ("today" if earth else "mean")
    if ref == "start":
        return orbit_at(0.0, p, tilt, phases)
    if ref == "today":
        return tuple(EARTH_TODAY.values())
    return (tilt, 0.0, 0.0)
