"""Continental crust volume budget per process, per time window (PW-046).

    uv run python docs/review/audit/tectonics-night/budget.py <repo> <level> <seed> <myr> [window] [out.json]

Prints, per window, the volume ratio to the start, area, mean thickness, the
thermostats' integral terms and the change booked by each process
(Simulation.book, km x level-5 cells), plus what no booking explains.
"""
import json
import sys

sys.path.insert(0, sys.argv[1])
import planet  # noqa: E402,F401  (thread caps first)
import numpy as np  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402

level, seed, myr = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
win = float(sys.argv[5]) if len(sys.argv) > 5 else 100.0
out = sys.argv[6] if len(sys.argv) > 6 else None
sim = Simulation(build_grid(level), seed, Params(flora_end=myr), 2.0)
n = sim.grid.n


def vol():
    return float((sim.w_thick * sim.w_cont).sum()) / sim.scale**2


rows = []
v0 = vol()
last = (0.0, v0, dict(sim.budget))
target = sim.target_fraction() * sim.params.continental_thickness * n / sim.scale**2
print(f"start vol {v0:.0f} target {target:.0f} start/target {v0 / target:.3f} area {sim.w_cont.mean() * 100:.1f}% "
      f"thick {(sim.w_thick * sim.w_cont).sum() / sim.w_cont.sum():.2f}", flush=True)


def on_step(s):
    global last
    if abs(s.t / win - round(s.t / win)) > 1e-6:
        return
    _, vp, bp = last
    v = vol()
    d = {k: s.budget.get(k, 0.0) - bp.get(k, 0.0) for k in s.budget}
    unb = (v - vp) - sum(d.values())
    r = dict(t=s.t, vol=v, ratio=v / v0, target_ratio=v / target, area=float(s.w_cont.mean() * 100),
             thick=float((s.w_thick * s.w_cont).sum() / s.w_cont.sum()), thermo=s.thermo.tolist(),
             d={k: round(x) for k, x in d.items()}, unbooked=round(unb), max_elev=float(s.w_elev.max()))
    rows.append(r)
    print(f"{s.t:5.0f} ratio {v / v0:.3f} (target {v / target:.3f}) area {r['area']:.1f} thick {r['thick']:.2f} "
          f"thermo {np.round(s.thermo, 3)} max {r['max_elev']:.0f} | "
          + " ".join(f"{k}={x:+.0f}" for k, x in sorted(r['d'].items(), key=lambda kv: kv[1]))
          + f" unbooked={unb:+.0f}", flush=True)
    last = (s.t, v, dict(s.budget))


sim.run(myr, on_step)
if out:
    json.dump(rows, open(out, "w"))
