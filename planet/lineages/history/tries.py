"""Best-of-N tries of a history."""

from __future__ import annotations

import numpy as np

from .. import recent as R
from .. import spec as SP
from . import bands as B
from .model import History
from .params import LOST_PENALTY
from .summary import present_summary


def simulate(tree: SP.Tree, ps: R.Pass, tries: int = 4, progress=lambda f, msg: None,
             goods: dict | None = None) -> tuple[History, dict, dict]:
    """Best of `tries` seeds by the wishes' score, less LOST_PENALTY per living line lost (e.g. a contact
    hybrid whose parents no longer meet); one try without wishes."""
    best = None
    n = tries if tree.wishes else 1
    scores, tstats = [], []
    for k in range(n):
        progress(k / n, f"try {k + 1}/{n}: recent pass: full climates (kept on disk after the first run)")  # (History.__init__ makes them; PW-743)
        h = History(tree, ps, tree.seed * 1000 + k, goods=goods)
        res = h.run(lambda f, msg, k=k: progress((k + f) / n, f"try {k + 1}/{n}: {msg}"))
        pres = present_summary(h, res["present"])
        sc = pres["wish_score"] if pres["wish_score"] is not None else 0.0
        scores.append(round(float(sc), 3))
        fs = res["frames"][-1]["stats"] if res.get("frames") else {}  # (the present frame; PW-707)
        tstats.append({"wish_score": round(float(sc), 3), "lost": len(pres["lost"]),
                       **{q: fs.get(q) for q in ("empty_land_pct", "two_plus_pct", "lead_share_mean_pct")}})
        key = sc - LOST_PENALTY * len(pres["lost"])  # (a try that keeps every living line is preferred)
        if best is None or key > best[3] + 1e-9:
            best = (h, res, pres, key)
    if B.banded(tree) and tree.band_rounds > 0:  # (lane 78: share bands as soft targets, history.bands)
        seed = best[0].seed

        def run_one(h, k=n):
            res = h.run(lambda f, msg: progress(min(0.999, (n - 1 + f) / n), f"share bands: {msg}"))
            pres = present_summary(h, res["present"])
            return res, pres, round(float(pres["wish_score"] or 0.0), 3)

        h, res, pres = B.calibrate(lambda kn: History(tree, ps, seed, goods=goods, knobs=kn), run_one, tree, best[:2], best[2],
                                   round(float(best[2]["wish_score"] or 0.0), 3))
        best = (h, res, pres, best[3])
    best[2]["tries"] = scores
    best[2]["try_stats"] = tstats
    best[2]["tries_mean"] = {q: round(float(np.mean([t[q] for t in tstats if t[q] is not None])), 3)
                             for q in ("wish_score", "empty_land_pct", "two_plus_pct", "lead_share_mean_pct")
                             if any(t[q] is not None for t in tstats)}
    return best[:3]
