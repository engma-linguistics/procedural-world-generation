"""Ice shelves and calving fronts (PW-367) and the ice sheet's sea-level bookkeeping."""

from __future__ import annotations

import numpy as np

from ..grid import Grid
from .params import RHO_I, RHO_W, TZParams


def shelf_viable(t_air: np.ndarray, p: "TZParams") -> np.ndarray:
    """Share (0..1) of floating ice that stays as an ice shelf (PW-367), by
    the annual mean air temperature over the sea (C): a shelf survives
    where its surface doesn't melt through in summer, observed where that
    is below ~-5 C (Morris & Vaughan 2003: the Antarctic Peninsula's
    shelves broke up as that isotherm passed them), in full from
    shelf_cold. Over a frozen sea the air's annual mean is how deeply it
    freezes (the sea state ocean.open_share reads; open_share itself comes
    in whole months and is never 0 beside today's Antarctica at L6, open
    2-6 months a year, as the real Ross and Amundsen seas are 2-4 months
    while their shelves stand)."""
    return np.clip((p.shelf_warm - t_air) / (p.shelf_warm - p.shelf_cold), 0.0, 1.0)


def shelf_cover(grid: Grid, front: np.ndarray, sea: np.ndarray, shelf: np.ndarray, p: "TZParams") -> np.ndarray:
    """Share (0..1) of a grounded front's sea side an ice shelf covers
    (PW-367): the mean over its sea neighbours (open sea or shelf) of their
    shelf ice / shelf_h (a thinner shelf counts for less); 0 off the fronts
    and for a front with no sea beside it (the deep-water rule). Where a
    shelf covers it, a front is not a cliff facing open water: it doesn't
    calve, its ice crosses the grounding line into the shelf, and the
    shelf, confined in its embayment, holds back `buttress` of that flow
    (Fürst et al. 2016: Antarctica's shelves carry most of the resistance
    at the grounding line). shelf: floating ice (m) per cell."""
    w = np.where(sea, np.clip(shelf / p.shelf_h, 0.0, 1.0), 0.0)
    src = grid.nbr_src
    tot = np.bincount(src, weights=w[grid.nbr_idx], minlength=grid.n)
    cnt = np.bincount(src, weights=sea[grid.nbr_idx].astype(float), minlength=grid.n)
    return np.where(front & (cnt > 0), tot / np.maximum(cnt, 1.0), 0.0)


def shelf_step(h0: np.ndarray, q: np.ndarray, melt: np.ndarray, c: float, dt: float, n: int = 20):
    """An ice shelf's thickness over dt years (m): fed at q (m/yr, the
    flow's net delivery, spread evenly over the step), thinning as it
    spreads under its own weight at c h^4 (m/yr; Weertman 1957: strain
    rate A (rho_i g (1 - rho_i/rho_w) h / 4)^3, the ice carried on to the
    shelf's front, where it calves) and melting from below at `melt`
    (m/yr). Implicit sub-steps (the spreading is stiff). Returns (h, spread,
    melted): m of ice that left by each way."""
    h = h0.copy()
    out, gone = np.zeros_like(h), np.zeros_like(h)
    k = dt / n
    for _ in range(n):
        x = np.maximum(h + k * q, 0.0)  # (fed first: what flows out of a cell can't exceed what it holds)
        m = np.minimum(k * melt, x)
        x -= m
        gone += m
        y = x.copy()
        for _ in range(6):  # Newton: y + k c y^4 = x
            y -= (y + k * c * y**4 - x) / (1.0 + 4.0 * k * c * y**3)
        y = np.clip(y, 0.0, x)
        out += x - y
        h = y
    return h, out, gone


def above_flotation(H: np.ndarray, bed: np.ndarray, bed0: np.ndarray, area: np.ndarray, sl: float) -> float:
    """m3 of water equivalent the ice takes from the sea (the usual
    ice-sheet bookkeeping, Goelzer et al. 2020): the grounded ice above
    flotation (ice grounded below sea level only stands in for sea water
    it pushed out, so filling a marine basin with ice lowers the sea far
    less than its volume would) in ocean water, plus the room the bed's
    sinking made below sea level (where ice presses an inland bed below
    the sea, the ice under that level does take water out of the sea).
    bed0: the bed at the start."""
    vaf = float((np.maximum(H - np.maximum(sl - bed, 0.0) * (RHO_W / RHO_I), 0.0) * area).sum())
    pov = float(((np.maximum(-bed, 0.0) - np.maximum(-bed0, 0.0)) * area).sum())
    return RHO_I / RHO_W * vaf + pov
