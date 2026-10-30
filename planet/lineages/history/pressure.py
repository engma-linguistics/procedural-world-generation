"""The pure rules of competition between peoples: the founding window, frontier invasion, crowding."""

from __future__ import annotations

import numpy as np

from .params import EXPANSE_FILL, EXPANSE_FROM, EXPANSE_PRESS, EXPANSE_SPAN, INTEGRATE, INVADE, INVADE_FLOOR, PIONEER_KYR, PIONEER_Q, SQUEEZE_FILL


def pioneer_factors(age_kyr: float | None, explore: float, held_cells: int, potential_cells: int) -> tuple[float, float]:
    """(the multiplier on the competition a people feels, the share of its founding window left) (PW-869). A newcomer, `age_kyr` since it
    started (None: a deep step, no pioneering), feels PIONEER_Q less competition at first, ramping back over PIONEER_KYR, and its founders are
    not displaced meanwhile (the second number, 1 -> 0). An expansive people (`explore` from EXPANSE_FROM) that holds a small share of the
    country it could hold (K >= 0.3: `potential_cells`; full at EXPANSE_FILL of it) presses into country others hold: that much less."""
    if age_kyr is None:
        return 1.0, 0.0
    pio = max(0.0, 1.0 - age_kyr / PIONEER_KYR)
    m = 1.0 - PIONEER_Q * pio
    expansive = min(1.0, max(0.0, (explore - EXPANSE_FROM) / EXPANSE_SPAN))
    if expansive > 0:
        unfilled = min(1.0, max(0.0, 1.0 - held_cells / (EXPANSE_FILL * max(1, potential_cells))))
        m *= 1.0 - EXPANSE_PRESS * expansive * unfilled
    return m, pio


def invasion_weights(dens: np.ndarray, k: int) -> np.ndarray:
    """What each rival j weighs in line k's competition on the cells next to k's own range: 1 for a rival as dense or denser than k,
    exp(-INVADE x ln(dens_k / dens_j)) (not under INVADE_FLOOR) for a thinner one. Every people by the same rule (PW-887)."""
    adv = np.log(np.maximum(dens[k], 1e-9) / np.maximum(dens, 1e-9))
    return np.clip(np.exp(-INVADE * np.maximum(adv, 0.0)), INVADE_FLOOR, 1.0)


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
