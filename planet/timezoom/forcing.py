"""Climate forcing of the time zoom: the orbit's temperature anomaly, and the
global temperature change of the glacial index (cycle.py) and the plants.

Forcing.update is the one place per step where the global temperature change
is assembled.
"""

from __future__ import annotations

import math

import numpy as np

from .. import climate
from .. import icemass as M
from ..grid import Grid
from ..orbit import BAND_DEG, BAND_LAT, insolation, reference_orbit
from .cycle import Index
from .params import TZParams


def orbit_anomaly(grid: Grid, orb: tuple[float, float, float], tilt: float, p: TZParams, land: np.ndarray,
                  ice: np.ndarray, own: np.ndarray | None = None, earth: bool = False,
                  phases: np.ndarray | None = None) -> np.ndarray:
    """The temperature anomaly (C) per cell and month (n x 12, month 0 = April)
    that the time zoom gives the orbit orb = (obliquity, eccentricity,
    perihelion) against its reference orbit (p.orbit_ref): each cell's own
    response (own_k: own, icemass.seasonal_k of its climate) to the
    insolation change averaged with the month before (the ground lags the
    sun), less over bright ice (ice_absorb), mixed over absorb_km (orbit_k).
    For climate.compute's orbit_dt (a finished frame, PW-198)."""
    ph = np.zeros(4) if phases is None else np.asarray(phases)
    q_ref = insolation(*reference_orbit(p, tilt, ph, earth))
    dq = insolation(*orb) - q_ref
    dq = 0.5 * (dq + np.roll(dq, 1, axis=1))
    band = np.clip(((grid.lat + 90) / BAND_DEG).astype(np.int64), 0, len(BAND_LAT) - 1)
    k = orbit_k(grid, own_k(p, land, own), land, np.clip(np.where(land, ice, 0.0) / p.snow_h, 0, 1), p)
    return k[:, None] * dq[band]


def own_k(p: TZParams, land: np.ndarray, seasonal: np.ndarray | None) -> np.ndarray:
    """Each cell's own response to an insolation change (C per W/m2), before the bright ice's share:
    p.orbit_resp 'seasons' (PW-459, PW-555 stage 1): its own seasons' (seasonal: icemass.seasonal_k of the
    climate) x insol_gain; 'run': the run's cycle-average rule (icemass.INSOL_K on land, INSOL_SEA of it at
    sea; ~3x the seasons'), for the run/zoom rule check until the run takes the seasons' rule too."""
    if p.orbit_resp == "run":
        return np.where(land, M.INSOL_K, M.INSOL_K * M.INSOL_SEA)
    if p.orbit_resp != "seasons":
        raise SystemExit(f"orbit_resp must be seasons or run, not {p.orbit_resp!r}")
    if seasonal is None:
        raise ValueError("orbit_resp=seasons needs each cell's seasonal response (icemass.seasonal_k)")
    return p.insol_gain * seasonal


def orbit_k(grid: Grid, own: np.ndarray, land: np.ndarray, bright: np.ndarray, p: TZParams) -> np.ndarray:
    """C per W/m2 of insolation change per cell, from each cell's own
    response (own: own_k). Bright snow and ice absorb little (ice_absorb),
    but the air over them brings what the land, sea and ice around absorbed:
    their responses, each its own, mixed over an air mass of absorb_km.
    bright: 0..1 per cell, the land's share under bright snow. (Before
    PW-114's fix the mix was of the absorbed shares, scaled by the land's
    response: the open sea around Greenland counted as fully absorbing land,
    Greenland took ~0.7 of the land's response instead of ~0.35, and an
    Eemian-like orbit took its summer from -8.7 to +4.9 C, melting all of it
    in 2 kyr.)"""
    b = np.where(land, np.clip(bright, 0, 1), 0.0)
    k = own * (1 - b * (1 - p.ice_absorb))
    mix = climate.smooth_big(grid, k, p.absorb_km) if p.absorb_km > 0 else k
    return own * (1 - b) + b * mix


class Forcing:
    """The global temperature change dTg (C, against the run's own): the glacial index's cooling
    (-I x cool, cycle.py; it stands for the ice-age cycle's CO2 and ice-albedo feedbacks, so the zoom
    has none of its own) plus the plants' (plants.py). Until the index is set up (after the first
    full climate, sim._Sim.setup_index) I is 0."""

    def __init__(self, p: TZParams, step: float):
        self.p, self.step = p, step
        self.index: Index | None = None
        self.cool = 0.0  # C: the glacial maximum's global cooling
        self.I = 0.0
        self.co2 = 0.0  # doublings of the plants' CO2 at the index (glacial_pco2; negative in a glacial)
        self.veg = 0.0  # C, the plants' part (plants.py), following ...
        self.veg_target = 0.0  # ... this (set at each full climate)

    def update(self, s_no: int) -> float:
        """The step's dTg."""
        p = self.p
        self.I = 0.0 if self.index is None else float(self.index.I[s_no])
        glacial = -self.I * self.cool
        self.co2 = self.I * (self.cool / p.glacial_cool) * math.log2(p.glacial_pco2)
        self.veg += (1 - math.exp(-self.step / p.veg_lag)) * (self.veg_target - self.veg)
        return glacial + self.veg
