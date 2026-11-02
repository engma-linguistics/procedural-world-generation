"""Share bands as soft targets (lane 78, owner 10-30): each people's share of the world's people kept within [min, max] %.

Never a clamp on the outcome (the owner called hard caps a kludge). When the best try lands a people outside its band, the run
nudges that people's own ecological knob and runs the best try's seed again, up to meta.band_rounds times: its density (people
per km² at full habitat, x the knob; its groups' with it), the lever demography says sets numbers
(docs/review/peoples-demography/report.md section 4). An arrival's `founders` are not a knob: lane 78b measured them on the even_six
tree, and x4 founders moved the elves from 0.7% to 1.0% while x0.25 left the gnomes at 32%; the landing sets where a people starts,
its density sets how many it ends.
The knob moves by target / share (a secant in log space after the first round), the target BAND_INSIDE of the band's width inside
its edge, and stays within BAND_KNOB: a bound on the lever, not on the share. The round with the least total miss is kept (ties:
the wish score). A band that is not met is reported with why.
"""

from __future__ import annotations

import numpy as np

from ..spread import EST

BAND_KNOB = (0.25, 4.0)  # a design judgement: a nudge of at most x4 either way on a people's own number; past it the band is reported unmet
BAND_INSIDE = 0.1  # ...aimed this share of the band's width inside the edge it missed, so the next round lands inside rather than on it
SLOPE_CLIP = (0.2, 5.0)  # the secant's d ln(share) / d ln(knob), kept sane (a share that hardly moves, or leaps)
SECANT_MIN = 0.05  # ...measured only over a move of the knob of at least this in log (5%); below it the step assumes share ~ knob


def peoples(tree) -> list:
    """The peoples a band can be set on: neither overlays, megafauna nor groups (a group counts in its people's share)."""
    return [l for l in tree.lines.values() if not l.overlay and not l.megafauna and l.origin != "group"]


def banded(tree) -> list:
    return [l for l in peoples(tree) if tuple(l.band_pct) != (0.0, 100.0)]


def shares(h, pres: dict) -> dict:
    """{people id: % of the world's people} at the present (its groups counted in), over the peoples and their groups."""
    lines = pres.get("lines", {})
    pop = {lid: v.get("population", 0) for lid, v in lines.items() if not v.get("overlay")
           and not h.tree.lines[lid].megafauna}
    tot = float(sum(pop.values()))
    out = {}
    for l in peoples(h.tree):
        n = pop.get(l.id, 0) + sum(pop.get(g, 0) for g in h.tree.groups_of(l.id))
        out[l.id] = 100.0 * n / tot if tot > 0 else 0.0
    return out


def miss(tree, sh: dict) -> float:
    """Total percentage points by which the banded peoples fall outside their bands."""
    return float(sum(max(0.0, l.band_pct[0] - sh.get(l.id, 0.0)) + max(0.0, sh.get(l.id, 0.0) - l.band_pct[1]) for l in banded(tree)))


def knob_of(h, l) -> str:
    return "kind"


def why_unmet(h, l, share: float, knob: float, warnings: list[str]) -> str:
    """Why a people missed its band, most telling first."""
    lo, hi = l.band_pct
    k = h.idx[l.id]
    rows = [k, *h._groups.get(l.id, [])]
    held = (h.p[rows] >= EST).any(0)
    potential = (h._Kmat[rows] >= 0.3).any(0)
    why = []
    if share < lo and (knob >= BAND_KNOB[1] - 1e-9) or share > hi and (knob <= BAND_KNOB[0] + 1e-9):
        why.append(f"its {knob_of(h, l)} is already x{knob:g}, the most the bands nudge")
    if share < lo and potential.any() and held[potential].mean() >= 0.8:
        why.append(f"it already holds {100 * held[potential].mean():.0f}% of the country it could live in")
    if share < lo and h._crowd[k] >= 0.5:
        why.append(f"crowded: rivals take {100 * h._crowd[k]:.0f}% of its habitat where it lives")
    if share < lo and not held.any():
        why.append("it did not survive to the present")
    why += warnings
    return "; ".join(why) or "the nudges did not reach it within the rounds"


def calibrate(make, run_one, tree, best, best_pres, best_score) -> tuple:
    """Up to tree.band_rounds re-runs of the best try with nudged knobs. make(knobs) -> History; run_one(h) -> (res, pres, score).
    Returns (h, res, pres) of the round kept, with pres['bands'] and pres['band_rounds'] filled in."""
    from .. import spec as SP
    h0, res0 = best
    want = banded(tree)
    if not want:
        return h0, res0, best_pres
    sh = shares(h0, best_pres)
    rounds = [{"round": 0, "miss": round(miss(tree, sh), 3), "wish_score": best_score, "knobs": {},
               "shares": {l.id: round(sh.get(l.id, 0.0), 2) for l in want}}]
    keep = (miss(tree, sh), -best_score, h0, res0, best_pres, sh, {})
    knobs: dict = {}
    hist: dict = {l.id: [(0.0, np.log(max(sh.get(l.id, 0.0), 1e-4)))] for l in want}
    for rd in range(1, tree.band_rounds + 1):
        if miss(tree, sh) <= 0:
            break
        moved = False
        for l in want:
            lo, hi = l.band_pct
            s = sh.get(l.id, 0.0)
            if lo <= s <= hi:
                continue
            target = lo + BAND_INSIDE * (hi - lo) if s < lo else hi - BAND_INSIDE * (hi - lo)
            target = max(target, 1e-3)
            pts = hist[l.id]
            slope = 1.0  # (the secant only over a real move of the people's own knob, and only when the share went its way: the other
            # peoples' knobs move in the same round, so a small own move or a share moving against it is their doing, not this lever's;
            # lane 78b saw a clipped 0.2 slope there throw a x0.4 step and the round's miss double)
            if len(pts) >= 2 and abs(pts[-1][0] - pts[-2][0]) > SECANT_MIN:
                sl = (pts[-1][1] - pts[-2][1]) / (pts[-1][0] - pts[-2][0])
                if sl > 0:
                    slope = float(np.clip(sl, *SLOPE_CLIP))
            lk = pts[-1][0] + (np.log(target) - np.log(max(s, 1e-4))) / slope
            lk = float(np.clip(lk, np.log(BAND_KNOB[0]), np.log(BAND_KNOB[1])))
            if abs(lk - pts[-1][0]) < 1e-6:
                continue
            knobs.setdefault(l.id, {})[knob_of(h0, l)] = float(np.exp(lk))
            pts.append((lk, None))  # (the share is filled in after the run)
            moved = True
        if not moved:
            break
        h = make({k: dict(v) for k, v in knobs.items()})
        res, pres, score = run_one(h)
        sh = shares(h, pres)
        for l in want:
            if hist[l.id][-1][1] is None:
                hist[l.id][-1] = (hist[l.id][-1][0], np.log(max(sh.get(l.id, 0.0), 1e-4)))
        m = miss(tree, sh)
        rounds.append({"round": rd, "miss": round(m, 3), "wish_score": score, "knobs": {k: dict(v) for k, v in knobs.items()},
                       "shares": {l.id: round(sh.get(l.id, 0.0), 2) for l in want}})
        if (m, -score) < keep[:2]:
            keep = (m, -score, h, res, pres, sh, {k: dict(v) for k, v in knobs.items()})
    _, _, h, res, pres, sh, kn = keep
    warn = SP.band_warnings(tree)
    out = {}
    for l in want:
        s = sh.get(l.id, 0.0)
        met = l.band_pct[0] <= s <= l.band_pct[1]
        kname = knob_of(h, l)
        kx = kn.get(l.id, {}).get(kname, 1.0)
        out[l.id] = {"band": list(l.band_pct), "share_pct": round(s, 3), "met": met, "knob": kname, "x": round(kx, 3),
                     **({} if met else {"why": why_unmet(h, l, s, kx, warn)})}
    pres["bands"] = out
    pres["band_rounds"] = rounds
    return h, res, pres
