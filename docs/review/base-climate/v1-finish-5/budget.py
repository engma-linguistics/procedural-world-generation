"""Crust budget and thermostats at a stored run's checkpoints: usage (repo root) budget.py RUN_DIR..."""
import os
import sys

sys.path[:0] = [os.getcwd()]
import planet  # noqa: E402,F401
import json  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

from planet import store  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics.params import Params  # noqa: E402
from planet.tectonics.simulation import Simulation  # noqa: E402

for rd in map(Path, sys.argv[1:]):
    meta = json.loads((rd / "run.json").read_text())["meta"]
    g = build_grid(meta["level"])
    params = Params(**meta["params"])
    ts = sorted(float(p.name.split(".ckpt")[0]) for p in (rd / "state").glob("*.ckpt"))
    prev = {}
    print(rd.name, "seed", meta["seed"], "L", meta["level"])
    for t in ts:
        sim = Simulation.from_state(g, meta["seed"], params, meta["dt"], store.load_checkpoint(rd, t, g))
        b = dict(sim.budget)
        d = {k: b[k] - prev.get(k, 0.0) for k in b}
        prev = b
        frac = float(sim.w_cont.mean())
        vol = float((sim.w_thick * sim.w_cont).mean())
        print(f" t{t:5.0f} cont {frac:.3f} thick {vol / frac:.1f} thermo {np.round(sim.thermo, 3)} co2 {sim.co2:.2f} "
              f"refs {np.round(sim.refs, 1)} | " + " ".join(f"{k}:{v / 1e3:+.0f}" for k, v in sorted(d.items())))
