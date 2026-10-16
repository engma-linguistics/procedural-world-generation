"""PW-387: warm-started rain kernel vs cold 20 d and a cold 60 d reference, along a run."""
import sys, time
import numpy as np
sys.path.insert(0, ".")
from planet import climate
from planet.grid import build_grid
from planet.tectonics import Simulation, Params

level, myr = int(sys.argv[1]), float(sys.argv[2])
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
if len(sys.argv) > 4:
    climate.RAIN_WARM_DAYS = float(sys.argv[4])
real = climate._rain
rows = []


def cold_args(a, days):
    a = list(a)
    qs, src_q, ocean = a[0], a[1], a[2]
    a[-3] = np.where(ocean, src_q, climate.RAIN_INIT * qs)
    a[-2] = np.zeros_like(qs)
    a[-1] = False
    a[15] = int(days * 86400.0 / a[16]) + 20
    return a


def err(x, ref, land):
    x, ref = x[:, land].sum(0), ref[:, land].sum(0)  # annual land rain
    d = np.abs(x - ref) / np.maximum(ref, 1e-3 * ref.mean())
    return float(np.abs(x - ref).sum() / ref.sum()), float(np.percentile(d, 99))


def wrapped(*a):
    t0 = time.perf_counter()
    out = real(*a)
    tw = time.perf_counter() - t0
    if a[-1]:
        t0 = time.perf_counter()
        c20 = real(*cold_args(a, 20.0))
        tc = time.perf_counter() - t0
        ref = real(*cold_args(a, 60.0))
        land = ~a[2]
        rows.append((a[15], tw, tc, *err(out[0], ref[0], land), *err(c20[0], ref[0], land)))
        print("steps %d warm %.2fs cold %.2fs | warm vs ref: L1 %.4f p99 %.3f | cold20 vs ref: L1 %.4f p99 %.3f"
              % rows[-1], flush=True)
    return out


climate._rain = wrapped
sim = Simulation(build_grid(level), seed, Params(flora_end=myr), 2.0)
sim.run(myr)
r = np.array(rows)
print("mean:", np.round(r.mean(0), 4))
