"""PW-1497 lane 275 (scout9.md): how long thickened crust and high ground last once shortening stops. Read-only.

Reads a run's checkpoints (run with --checkpoint-every 20) at t >= 100 Myr. For each:
- the land above 3 km, split by the time since its cell was last squeezed (record T_FOLD: the last step a
  collision or, with scout7_andean.patch, Andean contraction stacked crust on it), and whether it lies within
  2 L6 cells of a live ocean-continent margin (scout6_measure's zone, from the keyframe at that time);
- the decay of excess crust in dead belts: plate-frame cells (they ride with their plate) that are continental
  at t and t + 20 Myr, were not squeezed in between, and are at least 20 Myr past their last squeeze with crust
  > 45 km at t. The e-folding time of their excess over 35 km, from the pooled excess at both times.
usage: PYTHONPATH=. scout9_decay.py RUN_DIR [RUN_DIR ...]"""
import sys
from pathlib import Path

import numpy as np

from planet import store as S
from planet import timeline as T
from planet.grid import build_grid
from planet.tectonics.params import Params
from planet.tectonics.record import NEVER, T_FOLD
from planet.tectonics.simulation import Simulation

sys.path.insert(0, str(Path(__file__).parent))
from scout6_measure import dilate  # noqa: E402

BINS = [(0, 10), (10, 30), (30, 60), (60, 100), (100, 1e9)]


def margin_zone(r, arr, g, t):
    i = int(np.argmin([abs(f["t"] - t) for f in r["frames"]]))
    ea, eb = g.edges[:, 0], g.edges[:, 1]
    pl, cr, pb = T.frame(r, arr, "plate", i), T.frame(r, arr, "crust", i) > 0, T.frame(r, arr, "plate_boundary", i)
    oc = (pl[ea] != pl[eb]) & (cr[ea] != cr[eb]) & ((pb[ea] > 0) | (pb[eb] > 0))
    m = np.zeros(g.n, bool)
    m[np.where(cr[ea[oc]], ea[oc], eb[oc])] = True
    return dilate(g, m, 2) & cr


def run(rd):
    rd = Path(rd)
    hdr = S.read_header(rd / "run.json")
    m = hdr["meta"]
    g = build_grid(m["level"])
    params = Params.from_stored(m["params"])
    r, arr = T.load_frames(rd, ["plate", "crust", "plate_boundary"])
    ts = [t for t in S.checkpoints(rd) if t >= 100]
    hist = np.zeros(len(BINS) + 1)  # land > 3 km by time since squeezed (+ never squeezed)
    near = np.zeros(len(BINS) + 1)
    land_n = 0
    prev = None
    x0 = x1 = 0.0
    ncell = 0
    for t in ts:
        sim = Simulation.from_state(g, m["seed"], params, m["dt"], S.load_checkpoint(rd, t, g))
        e, rec = sim.w_elev, sim.w_rec
        land = e > 0
        land_n += land.sum()
        hi = e > 3000
        zone = margin_zone(r, arr, g, t)
        age = np.where(rec[:, T_FOLD] <= NEVER / 2, np.inf, t - rec[:, T_FOLD])
        for j, (a, b) in enumerate(BINS):
            sel = hi & (age >= a) & (age < b)
            hist[j] += sel.sum()
            near[j] += (sel & zone).sum()
        hist[-1] += (hi & ~np.isfinite(age)).sum()
        near[-1] += (hi & ~np.isfinite(age) & zone).sum()
        pl = sim.plates
        cur = dict(t=t, owned=pl.owned.copy(), cont=pl.cont.copy(), thick=pl.thick.copy(),
                   tf=pl.rec[..., T_FOLD].copy(), alive=pl.alive.copy(), label=pl.label.copy())
        if prev is not None and abs(t - prev["t"] - 20) < 1e-6:
            same = prev["alive"] & cur["alive"] & (prev["label"] == cur["label"])
            ok = (same[:, None] & prev["owned"] & cur["owned"] & prev["cont"] & cur["cont"]
                  & (prev["tf"] == cur["tf"]) & (prev["tf"] > NEVER / 2) & (prev["t"] - prev["tf"] >= 20)
                  & (prev["thick"] > 45))
            x0 += (prev["thick"][ok] - 35).sum()
            x1 += np.maximum(cur["thick"][ok] - 35, 0).sum()
            ncell += ok.sum()
        prev = cur
    tot = max(hist.sum(), 1)
    tau = 20 / np.log(x0 / x1) if x1 > 0 and x0 > x1 else np.inf
    return dict(seed=m["seed"], share=params.__dict__.get("andean_shortening", 0.0), hi=100 * hist / tot,
                near=100 * near / np.maximum(hist, 1), gt3=100 * hist.sum() / max(land_n, 1), tau=tau, ncell=ncell,
                mean_x0=x0 / max(ncell, 1), mean_x1=x1 / max(ncell, 1), nck=len(ts))


if __name__ == "__main__":
    labels = [f"{a}-{b}" if b < 1e8 else f">{a}" for a, b in BINS] + ["never"]
    print("run seed share | >3km % land | share of >3 km land by Myr since last squeezed: " + " ".join(labels)
          + " | of each, % near a live margin | dead-belt excess crust: cells, mean km at t, t+20, e-fold Myr")
    for rd in sys.argv[1:]:
        x = run(rd)
        print(f"{Path(rd).name} {x['seed']:5d} {x['share']:.2f} | {x['gt3']:5.2f} | "
              + " ".join(f"{v:5.1f}" for v in x["hi"]) + " | " + " ".join(f"{v:5.1f}" for v in x["near"])
              + f" | {x['ncell']:6d} {x['mean_x0']:5.1f} {x['mean_x1']:5.1f} {x['tau']:6.0f}  ({x['nck']} ckpts)")
