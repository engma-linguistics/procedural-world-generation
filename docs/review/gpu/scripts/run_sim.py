"""python run_sim.py LEVEL MYR OUT.json [--plain] [--warm MYR] [--seed S]
Times planet simulate (timeline.simulate) with the monkeypatched timers."""
import argparse, os, sys, time, json
sys.path.insert(0, os.path.dirname(__file__)); import env
ap = argparse.ArgumentParser()
ap.add_argument("level", type=int)
ap.add_argument("myr", type=float)
ap.add_argument("out")
ap.add_argument("--plain", action="store_true")
ap.add_argument("--warm", type=float, default=0)
ap.add_argument("--seed", type=int, default=3199)
ap.add_argument("--checkpoint", type=float, default=100)
a = ap.parse_args()

import timers
if not a.plain:
    print("wrapped", timers.install(), flush=True)
from planet import timeline as T, store as S
import numba
params = T.make_params({})
if a.warm:
    o = T.simulate(a.seed, 5, a.warm, 2.0, 4.0, "warm", params, checkpoint_every=0)
    import shutil; shutil.rmtree(o)
    timers.reset()
load0 = os.getloadavg()
t0 = time.perf_counter()
out = T.simulate(a.seed, a.level, a.myr, 2.0, 4.0, "prof", params, checkpoint_every=a.checkpoint)
wall = time.perf_counter() - t0
print("run", out.name, "wall", round(wall, 1), flush=True)
timers.dump(a.out, wall, {"level": a.level, "myr": a.myr, "run": out.name, "load_before": load0,
                         "load_after": os.getloadavg(), "threads": numba.get_num_threads(),
                         "plain": a.plain})
