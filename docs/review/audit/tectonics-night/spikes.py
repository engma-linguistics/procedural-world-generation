"""Grid-scale crust spikes (PW-284's prerequisite): continental cells whose
crust stands far above their continental neighbours'.

    uv run python docs/review/audit/tectonics-night/spikes.py <repo> <level> <seed> <myr> [every]

Per sample: how many continental cells exceed the mean of their continental
neighbours by > 10 / 15 / 20 km, the largest excess, and the setting of the
>15 km ones: share on a plate boundary (a neighbour on another plate), on a
converging boundary (w_boundary), with few same-plate continental
neighbours (<= 3), and their thickness.
"""
import sys

sys.path.insert(0, sys.argv[1])
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402

level, seed, myr = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
every = float(sys.argv[5]) if len(sys.argv) > 5 else 20.0
sim = Simulation(build_grid(level), seed, Params(flora_end=myr), 2.0)
g = sim.grid
src = np.repeat(np.arange(g.n), np.diff(g.nbr_off))
nb = g.nbr_idx
tot = {"n15": 0, "bnd": 0, "conv": 0, "few": 0}


def excess(s):
    t, c = s.w_thick, s.w_cont
    okc = c[nb]
    st = np.add.reduceat(np.where(okc, t[nb], 0.0), g.nbr_off[:-1])
    nc = np.add.reduceat(okc.astype(int), g.nbr_off[:-1])
    mean = st / np.maximum(nc, 1)
    return np.where(c & (nc > 0), t - mean, 0.0), nc


def on_step(s):
    if abs(s.t / every - round(s.t / every)) > 1e-6:
        return
    ex, nc = excess(s)
    own = s.owner
    other = np.add.reduceat((own[nb] != own[src]).astype(int), g.nbr_off[:-1]) > 0
    same_c = np.add.reduceat(((own[nb] == own[src]) & s.w_cont[nb]).astype(int), g.nbr_off[:-1])
    big = ex > 15
    k = int(big.sum())
    tot["n15"] += k
    tot["bnd"] += int((big & other).sum())
    tot["conv"] += int((big & (s.w_boundary > 0)).sum())
    tot["few"] += int((big & (same_c <= 3)).sum())
    print(f"{s.t:5.0f} >10 {int((ex > 10).sum()):4d} >15 {k:4d} >20 {int((ex > 20).sum()):4d} max {ex.max():5.1f} | "
          f">15: boundary {int((big & other).sum())} conv {int((big & (s.w_boundary > 0)).sum())} "
          f"few-same {int((big & (same_c <= 3)).sum())} thick med {np.median(s.w_thick[big]) if k else 0:.0f} | "
          f"cont thick p99 {np.percentile(s.w_thick[s.w_cont], 99):.0f} max elev {s.w_elev.max():.0f}", flush=True)


sim.run(myr, on_step)
print("totals", tot)
