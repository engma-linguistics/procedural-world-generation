"""Who lives in a cell, as a composition (PW-689): the leading people's share, the second's, and an 'other' rest.

Presence (history.py) says which peoples hold ground in a cell; this says how they share it. Not a recipe: the
shares come out of who reaches the cell (their presence there) and who will live with whom (the cohabitation
matrix: each people's openness, the wishes' near/apart, defaults). Before the late mixing (`mixing_start`,
~3 kyr ago) peoples barely intermingle, so a cell is mostly its leader's; the later, the more a cell's other
peoples count, each by its presence times how readily it lives beside the leader.

Also the body flags given as a share of a people (lactase persistence, PW-701) as a share of the cell: each
people's frequency (its groups counted in, by presence) mixed by the cell's composition."""

from __future__ import annotations

import numpy as np

from . import spec as SP

APART_FACTOR = 0.8  # an 'apart' wish of weight 1 cuts the pair's cohabitation by this share, a 'near' one closes this share of the gap to 1
EARLY = 0.2  # before the late mixing every pair counts this much (a little contact, trade, a border village)
SUIT_K = 0.4  # a cell suits a people fully at habitat K >= this (less: in proportion; under the establishing threshold: not at all)
REACH_CELLS = 10  # by the present a people's presence reaches this many cells beyond its range (travel, trade, settlers: ~560 km at L7)...
REACH_DECAY = 0.85  # ...each cell out at this share of the one before, less in closed country...
REACH_CLOSED = 0.3  # ...x (0.7 + 0.3 contact) per cell: forest and mountain slow the settling
MIN_SHARE = 0.03  # a second people below this share is left in the 'other'


def cohabitation(tree: SP.Tree, lines: list, idx: dict) -> np.ndarray:
    """H[i, j] in 0..1: how readily people i lives beside people j. sqrt((1 - insularity_i)(1 - insularity_j)) (0.5 for
    two peoples of default openness, 0.8 for cosmopolitans, 0.15 for insular ones), then the wishes: a 'near' pair
    closes APART_FACTOR x weight of the gap to 1, an 'apart' pair loses that share (weight capped at 1)."""
    n = len(lines)
    t = np.array([1.0 - l.demo("insularity") for l in lines])
    H = np.sqrt(np.outer(t, t))
    for w in tree.wishes:
        if w.want not in ("near", "apart") or w.a not in tree.lines or w.b not in tree.lines:
            continue
        i, j = idx[tree.people_of(w.a)], idx[tree.people_of(w.b)]
        if i == j:
            continue
        f = APART_FACTOR * min(w.weight, 1.0)
        for x, y in ((i, j), (j, i)):
            H[x, y] = H[x, y] + (1 - H[x, y]) * f if w.want == "near" else H[x, y] * (1 - f)
    np.fill_diagonal(H, 1.0)
    return H


def reach(g, Pw: np.ndarray, suit: np.ndarray, corr: np.ndarray, open_land: np.ndarray, ramp: float, est: float) -> np.ndarray:
    """Pw with each people's presence carried over land past its range: settlers, traders and neighbours who live
    beside the others. After i cells it counts REACH_DECAY^i (less through closed country), up to REACH_CELLS x ramp
    cells, and only where the land suits the people (suit 0..1, its habitat). With no mixing yet (ramp 0) it is Pw."""
    R = int(round(REACH_CELLS * ramp))
    out = Pw.copy()
    if R <= 0:
        return out
    step = np.nan_to_num(REACH_DECAY * (1 - REACH_CLOSED + REACH_CLOSED * corr) * open_land)
    for j in np.flatnonzero(Pw.max(1) >= est):
        D = Pw[j].copy()
        for _ in range(R):
            D = np.maximum(D, step * np.maximum.reduceat(D[g.nbr_idx], g.nbr_off[:-1]))
        out[j] = np.maximum(Pw[j], D * suit[j])
    return out


def compose(Pw: np.ndarray, Pr: np.ndarray, H: np.ndarray, ramp: float, est: float, freq=None) -> dict:
    """Pw (lines x cells): each native people's presence (groups folded into their people); Pr: the same with the
    reach added (reach()). ramp 0..1: how far the late mixing has come. Returns uint8 layers: mix_lead_share, mix_second (index; 255 none), mix_second_share,
    mix_other_share (percent of the cell, summing to 100 where anyone lives; the leader is argmax Pw, the layer
    peoples_whole), and, per `freq` ({trait: line x cells share of the line}), body_<trait> (% of the cell)."""
    n, N = Pw.shape
    here = Pw.max(0) >= est
    out = {"mix_lead_share": np.zeros(N, np.uint8), "mix_second": np.full(N, 255, np.uint8),
           "mix_second_share": np.zeros(N, np.uint8), "mix_other_share": np.zeros(N, np.uint8)}
    for k in (freq or {}):
        out["body_" + k] = np.zeros(N, np.uint8)
    cells = np.flatnonzero(here)
    if not len(cells):
        return out
    lead = Pw[:, cells].argmax(0)
    P = np.where(Pr[:, cells] >= 0.5 * est, Pr[:, cells], 0.0)  # (the leader holds the cell; the rest by presence or reach)
    P[lead, np.arange(len(cells))] = Pw[lead, cells]
    rho = EARLY * (1 - ramp) + ramp * H[lead].T  # (lines x cells): how readily each lives beside the leader
    rho[lead, np.arange(len(cells))] = 1.0
    W = P * rho
    tot = W.sum(0)
    a = W[lead, np.arange(len(cells))] / tot
    W2 = W.copy()
    W2[lead, np.arange(len(cells))] = 0
    sec = W2.argmax(0)
    b = W2[sec, np.arange(len(cells))] / tot
    keep = b >= MIN_SHARE
    la = np.round(100 * a).astype(np.int64)
    sb = np.where(keep, np.round(100 * b), 0).astype(np.int64)
    sb = np.minimum(sb, 100 - la)
    out["mix_lead_share"][cells] = la
    out["mix_second"][cells] = np.where(sb > 0, sec, 255)
    out["mix_second_share"][cells] = sb
    out["mix_other_share"][cells] = 100 - la - sb
    S = W / tot  # (the whole composition, for the frequencies)
    for k, f in (freq or {}).items():
        out["body_" + k][cells] = np.round(100 * (S * f[:, cells]).sum(0)).astype(np.uint8)
    return out
