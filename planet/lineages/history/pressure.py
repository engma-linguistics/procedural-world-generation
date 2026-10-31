"""The pure rules of competition between peoples: the momentum edge, the expansive press, crowding."""

from __future__ import annotations

import numpy as np

from .params import (EXPANSE_FILL, EXPANSE_FROM, EXPANSE_PRESS, EXPANSE_SPAN, INTEGRATE, SQUEEZE_FILL, SURGE_FULL, SURGE_KYR,
                     SURGE_LATE_FROM_KYR, SURGE_Q)


def expanse_factor(explore: float, held_cells: int, potential_cells: int) -> float:
    """The multiplier on the competition an expansive people feels (PW-869): one with `explore` from EXPANSE_FROM that holds a small
    share of the country it could hold (K >= 0.3: `potential_cells`; full at EXPANSE_FILL of it) presses into country others hold."""
    expansive = min(1.0, max(0.0, (explore - EXPANSE_FROM) / EXPANSE_SPAN))
    if expansive <= 0:
        return 1.0
    unfilled = min(1.0, max(0.0, 1.0 - held_cells / (EXPANSE_FILL * max(1, potential_cells))))
    return 1.0 - EXPANSE_PRESS * expansive * unfilled


def surge(mass: float, ref: float, dt: float) -> tuple[float, float]:
    """(a people's momentum 0..1, its updated reference mass) (owner 10-30, lane 73). The reference is the people's range mass (the sum
    of its presence) lagged with SURGE_KYR e-folding; the momentum is how far the mass stands above it, full at x SURGE_FULL:
    clip(ln(mass / ref) / ln(SURGE_FULL), 0, 1). A people on the upswing (a newcomer, its reference still 0, or a people spreading
    fast) has it; it fades as the reference catches up once its growth stalls, and a shrinking people has none."""
    ref = ref + (mass - ref) * (1.0 - np.exp(-dt / SURGE_KYR))
    if mass <= 0:
        return 0.0, ref
    if ref <= 0:
        return 1.0, ref
    return float(np.clip(np.log(mass / ref) / np.log(SURGE_FULL), 0.0, 1.0)), ref


def surge_q(early: float, late: float, ago_kyr: float) -> float:
    """The strength of the momentum edge at a time (meta.surge_early, meta.surge_late, SURGE_X): early until SURGE_LATE_FROM_KYR ago,
    blended linearly to late by the present (the farming eras on: the owner's one dial per era, modelled on the megafauna press)."""
    w = min(1.0, max(0.0, 1.0 - ago_kyr / SURGE_LATE_FROM_KYR))
    return min(1.0, max(0.0, SURGE_Q * ((1 - w) * early + w * late)))


def squeeze(crowd: float, held_cells: int, potential_cells: int) -> float:
    """How squeezed a people is, 0..1 (PW-889): its crowding (the share of its habitat rivals take) x how little of the country it could
    hold (K >= 0.3: `potential_cells`) it holds (1 - held / (SQUEEZE_FILL x potential), 0 once it holds that share). A large crowded people
    (the humans on a full continent) is not squeezed; a thin people pushed into a corner of its country is."""
    if potential_cells <= 0 or crowd <= 0:
        return 0.0
    small = min(1.0, max(0.0, 1.0 - held_cells / (SQUEEZE_FILL * potential_cells)))
    return float(min(1.0, max(0.0, crowd)) * small)


def integration_weights(cohab_row: np.ndarray, sq: float) -> np.ndarray:
    """What each rival weighs in a squeezed people's competition (PW-889): 1 - INTEGRATE x squeeze x how readily the two live side by
    side (the cohabitation matrix row, compose.cohabitation, 0..1): a friendly neighbour's land is shared, an enemy's hardly."""
    return 1.0 - INTEGRATE * sq * np.clip(cohab_row, 0.0, 1.0)


def crowding(K: np.ndarray, room: np.ndarray, held: np.ndarray) -> float:
    """How crowded a people is, 0..1: the mean share of its habitat (K) over its held cells that rivals take (1 - room / K)."""
    if not held.any():
        return 0.0
    return float(np.clip(1.0 - room[held] / np.maximum(K[held], 1e-9), 0.0, 1.0).mean())
