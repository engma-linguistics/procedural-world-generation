"""Climate forcing of the time zoom: the orbit's temperature anomaly, and the
global feedbacks (CO2 and ice albedo) that follow the ice.

PW-440's ice-age cycle hooks in here: Forcing.update is the one place per
step where the global temperature change is assembled.
"""

from __future__ import annotations

import math

import numpy as np

from .. import climate
from ..grid import Grid
from ..orbit import BAND_DEG, BAND_LAT, insolation, reference_orbit
from .cycle import Cycle
from .params import TZParams


def orbit_anomaly(grid: Grid, orb: tuple[float, float, float], tilt: float, p: TZParams, land: np.ndarray,
                  ice: np.ndarray, earth: bool = False, phases: np.ndarray | None = None) -> np.ndarray:
    """The temperature anomaly (C) per cell and month (n x 12, month 0 = April)
    that the time zoom gives the orbit orb = (obliquity, eccentricity,
    perihelion) against its reference orbit (p.orbit_ref): insol_k C per
    W/m2 on land (insol_sea of that over the sea), averaged with the month
    before (the ground lags the sun), less over bright ice (ice_absorb),
    mixed over absorb_km (orbit_k). For climate.compute's orbit_dt (a finished frame,
    PW-198)."""
    ph = np.zeros(4) if phases is None else np.asarray(phases)
    q_ref = insolation(*reference_orbit(p, tilt, ph, earth))
    dq = insolation(*orb) - q_ref
    dq = 0.5 * (dq + np.roll(dq, 1, axis=1))
    band = np.clip(((grid.lat + 90) / BAND_DEG).astype(np.int64), 0, len(BAND_LAT) - 1)
    k = orbit_k(grid, land, np.clip(np.where(land, ice, 0.0) / p.snow_h, 0, 1), p)
    return k[:, None] * dq[band]


def orbit_k(grid: Grid, land: np.ndarray, bright: np.ndarray, p: TZParams) -> np.ndarray:
    """C per W/m2 of insolation change per cell. Bare land feels insol_k,
    the sea insol_sea of it (its deep mixed layer). Bright snow and ice
    absorb little (ice_absorb), but the air over them brings what the land,
    sea and ice around absorbed: their responses, each its own, mixed over
    an air mass of absorb_km. bright: 0..1 per cell, the land's share under
    bright snow. (Before PW-114's fix the mix was of the absorbed shares,
    scaled by the land's insol_k: the open sea around Greenland counted as
    fully absorbing land, Greenland took ~0.7 of the land's response instead
    of ~0.35, and an Eemian-like orbit took its summer from -8.7 to +4.9 C,
    melting all of it in 2 kyr.)"""
    b = np.where(land, np.clip(bright, 0, 1), 0.0)
    own = np.where(land, p.insol_k, p.insol_k * p.insol_sea)
    k = own * (1 - b * (1 - p.ice_absorb))
    mix = climate.smooth_big(grid, k, p.absorb_km) if p.absorb_km > 0 else k
    return own * (1 - b) + b * mix


def albedo(p: TZParams, f: float) -> float:
    """C of global cooling by land ice over a share f of the planet (the main run's rule, earth.py:
    it levels off, so a planet already icy gains less cooling from more ice)."""
    return p.ice_albedo_max * math.tanh(p.ice_albedo * f / 0.03 / max(p.ice_albedo_max, 1e-9))


class Forcing:
    """The global temperature change dTg (C, against the run's own) the ice
    gives: CO2 follows the ice volume (lagged), ice albedo follows its area,
    and in an ice age's ending (cycle.Cycle) CO2 is released.
    room: the share of the CO2 feedback's cap left (1 for an interglacial
    start); ice_frac0: the start's ice area share."""

    def __init__(self, p: TZParams, step: float, room: float, ice_frac0: float, cycle: Cycle):
        self.p, self.step, self.room, self.ice_frac0, self.cycle = p, step, room, ice_frac0, cycle
        self.co2 = 0.0  # C, the lagged CO2 part of the global change
        self.veg = 0.0  # C, the plants' part (plants.py), following ...
        self.veg_target = 0.0  # ... this (set at each full climate)

    def co2_target(self, sl: float) -> float:
        p = self.p
        excess = -sl / 120.0  # 1 = an Earth-LGM-sized extra ice volume
        return -p.co2_cool * float(np.clip(excess, -0.5, p.co2_max * self.room))

    def update(self, sl: float, ice_frac: float, s_no: int = 0) -> float:
        """The step's dTg, from the sea level sl (m, change since the start) and the ice area share
        (the cycle's state steps first)."""
        p, cyc = self.p, self.cycle
        cyc.step(s_no, sl)
        target = cyc.co2_target(self.co2_target(sl), sl)
        self.co2 += (1 - math.exp(-self.step / p.co2_lag)) * (target - self.co2)
        self.veg += (1 - math.exp(-self.step / p.veg_lag)) * (self.veg_target - self.veg)
        return self.co2 + self.veg - (albedo(p, ice_frac) - albedo(p, self.ice_frac0))
