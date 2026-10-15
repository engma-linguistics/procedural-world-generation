"""python capture.py RUN_ID AT OUTDIR: replay a run to AT, run one climate update with
climate._rain and timezoom_kernels.climate_step patched to pickle their first call's
arguments and outputs (the CPU reference)."""
import os, sys, pickle, time
sys.path.insert(0, os.path.dirname(__file__)); import env  # noqa
import numpy as np
from planet import timeline as T, climate, timezoom_kernels as TK, icemass
from planet.tectonics import earth

run, at, outdir = sys.argv[1], float(sys.argv[2]), sys.argv[3]
os.makedirs(outdir, exist_ok=True)
sim = T.replay(T.find_run(run), at)
lvl = sim.grid.level
saved = set()


def cap(name, fn, nout_idx=None):
    def w(*a):
        a_in = [x.copy() if isinstance(x, np.ndarray) else x for x in a]
        t0 = time.perf_counter()
        r = fn(*a)
        dt = time.perf_counter() - t0
        if name not in saved:
            saved.add(name)
            out = r if r is not None else [x for x in a]  # in-place kernels: outputs are args
            with open(f"{outdir}/{name}_L{lvl}.pkl", "wb") as f:
                pickle.dump({"args": a_in, "out": out, "cpu_s": dt}, f)
            print("captured", name, round(dt, 3), "s", flush=True)
        return r
    return w


climate._rain = cap("rain", climate._rain)
icemass_cs = TK.climate_step
TK.climate_step = cap("climate_step", icemass_cs)  # icemass imports it inside balance()
earth.update_climate(sim, sim.w_elev)
# also the grid's neighbour arrays for the smoother
g = sim.grid
with open(f"{outdir}/grid_L{lvl}.pkl", "wb") as f:
    pickle.dump({"nbr_off": g.nbr_off, "nbr_idx": g.nbr_idx, "n": g.n}, f)
print("done")
