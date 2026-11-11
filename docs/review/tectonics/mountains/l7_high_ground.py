"""PW-1683 lane 288 (l7-high-ground.md): why an L7 run holds more land above 3 km than L6. Read-only, per checkpoint.

Per checkpoint (t >= 100 Myr), beside andes_late_series' high ground and Andes share:
- continental area (% of the surface) against the target (earth.target_fraction), and the crust volume against
  target x continental_thickness: the two thermostats' errors (crust.thermostats). Mean continental thickness is
  volume / area, so a thicker continent means volume above target or area below it;
- the thermostats' factors now (arc growth x, subduction erosion x; 1 = nominal, floor 0.1 / 0.2);
- land area and mean land elevation; land above 2/3/4 km; the 90th and 99th percentile of land elevation;
- the run's crust books since the run's start (sim.budget: km x L5 cells per process) at the checkpoint, so the
  area sinks (andean.closed, subd.erosion) can be compared between levels.
usage: PYTHONPATH=. l7_high_ground.py RUN_DIR [RUN_DIR ...]   (--every N: every Nth checkpoint)"""
import sys
from pathlib import Path

import numpy as np

from planet import store as S
from planet.grid import build_grid
from planet.tectonics import crust
from planet.tectonics.params import Params
from planet.tectonics.simulation import Simulation

sys.path.insert(0, str(Path(__file__).parent))
from andes_late_series import zones  # noqa: E402

from planet import timeline as T  # noqa: E402

BOOKS = ("andean.closed", "subd.erosion", "arc", "born", "margin", "coherence", "erosion", "flow+cap", "clip")


def series(rd, every=1):
    rd = Path(rd)
    m = S.read_header(rd / "run.json")["meta"]
    g = build_grid(m["level"])
    params = Params.from_stored(m["params"])
    try:  # (a run still going has no layers yet: no Andes share)
        r, arr = T.load_frames(rd, ["plate", "crust", "plate_boundary"])
    except KeyError:
        r = arr = None
    f = 2 if m["level"] >= 7 else 1
    rows = []
    for t in [t for t in S.checkpoints(rd) if t >= 100][::every]:
        sim = Simulation.from_state(g, m["seed"], params, m["dt"], S.load_checkpoint(rd, t, g))
        e, cont = sim.w_elev, sim.w_cont
        land = e > 0
        nl = max(land.sum(), 1)
        target = sim.target_fraction()
        vol = float((sim.w_thick * cont).mean())
        th = sim.thermo.copy()
        sim.dt_now = 0.0  # (thermostats() integrates dt_now: read the factors without moving the memory)
        grow, shrink = crust.thermostats(sim)
        sim.thermo = th
        zone = zones(r, arr, g, t, 2 * f, 5 * f, 3 * f)[0] if r is not None else None
        h3 = e > 3000
        el = e[land]
        rows.append(dict(t=t, cont=100 * cont.mean(), target=100 * target,
                         volr=vol / (target * params.continental_thickness), thick=float(sim.w_thick[cont].mean()),
                         grow=float(grow), shrink=float(shrink), land=100 * land.mean(), mland=float(el.mean()),
                         gt2=100 * (e > 2000).sum() / nl, gt3=100 * h3.sum() / nl, gt4=100 * (e > 4000).sum() / nl,
                         p90=float(np.percentile(el, 90)), p99=float(np.percentile(el, 99)),
                         andes3=100 * (h3 & zone).sum() / max(h3.sum(), 1) if zone is not None else np.nan,
                         **{b: float(sim.budget.get(b, 0.0)) for b in BOOKS}))
    return m, params, rows


KEYS = ("cont", "target", "volr", "thick", "grow", "shrink", "land", "mland", "gt2", "gt3", "gt4", "p90", "p99", "andes3")

if __name__ == "__main__":
    args = sys.argv[1:]
    every = 1
    if "--every" in args:
        i = args.index("--every")
        every = int(args[i + 1])
        del args[i:i + 2]
    for rd in args:
        m, p, rows = series(rd, every)
        print(f"# {Path(rd).name} seed {m['seed']} L{m['level']} andean_shortening {p.andean_shortening} collapse {p.collapse}")
        print("   t | cont% target% vol/tgt thick | grow shrink | land% mean_m | >2km >3km >4km | p90 p99 | andes% of >3km | books: " + " ".join(BOOKS))
        for x in rows:
            print(f"{x['t']:4.0f} | {x['cont']:4.1f} {x['target']:4.1f} {x['volr']:5.3f} {x['thick']:4.1f} | {x['grow']:4.2f} {x['shrink']:4.2f} |"
                  f" {x['land']:4.1f} {x['mland']:5.0f} | {x['gt2']:5.2f} {x['gt3']:4.2f} {x['gt4']:4.2f} | {x['p90']:5.0f} {x['p99']:5.0f} | {x['andes3']:5.1f} | "
                  + " ".join(f"{x[b]:.3g}" for b in BOOKS))
        for t0, t1 in ((100, 600), (600, 1000)):
            a = [x for x in rows if t0 <= x["t"] <= t1]
            if a:
                print(f"{t0}-{t1} median:", " ".join(f"{k} {np.median([x[k] for x in a]):.3g}" for k in KEYS))
                print(f"{t0}-{t1} mean:  ", " ".join(f"{k} {np.mean([x[k] for x in a]):.3g}" for k in KEYS))
