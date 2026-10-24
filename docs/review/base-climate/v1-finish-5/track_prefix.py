"""ice_diag-style run (in memory) that also records the crust thermostats and the CO2 source's parts per step:
the source as counted, and the source the arcs would give at their nominal rate (thermostat 1: the subduction flux).
Recording only (bit-identical run) unless FIX=1, which counts the nominal arc source in the CO2 source.
usage (repo root): [FIX=1] track.py SEED LEVEL MYR OUT_DIR [k=v ...]"""
import os
import sys

sys.path[:0] = [os.getcwd()]
import planet  # noqa: E402,F401
import gzip  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation, crust, earth  # noqa: E402
from planet.tectonics import simulation as S  # noqa: E402
from planet.tectonics.diag import Recorder  # noqa: E402
sys.path.insert(0, os.getcwd())
from tools.ice_diag import parse_sets  # noqa: E402

seed, level, myr, out = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), Path(sys.argv[4])
sets = {"flora_end": myr, **parse_sets(sys.argv[5:])}
FIX = os.environ.get("FIX") == "1"
out.mkdir(parents=True, exist_ok=True)
state = {}
_arc = crust.arc_growth


def arc_growth(sim, bd, conv, thermostat):
    g = _arc(sim, bd, conv, thermostat)
    state["nominal"] = _arc(sim, bd, conv, 1.0) if np.ndim(thermostat) == 0 else g
    state["thermostat"] = float(thermostat)
    return g


crust.arc_growth = arc_growth
_th = crust.thermostats


def thermostats(sim):
    th, sh = _th(sim)
    state["shrink"] = float(sh)
    return th, sh


crust.thermostats = thermostats
_gt = earth.global_temperature


def global_temperature(sim, growth, newc, rng):
    state["src_actual"] = (newc + 20.0 * float(growth.sum())) / sim.scale**2
    state["src_nominal"] = (newc + 20.0 * float(state["nominal"].sum())) / sim.scale**2
    return _gt(sim, state["nominal"] if FIX else growth, newc, rng)


S.earth.global_temperature = global_temperature
sim = Simulation(build_grid(level), seed, Params(**sets), 2.0)
sim.diag = Recorder()
extra = []
t0 = time.time()


def on_step(s):
    s.diag.step(s)
    frac = float(s.w_cont.mean())
    vol = float((s.w_thick * s.w_cont).mean())
    extra.append({"t": round(float(s.t), 3), "thermostat": round(state.get("thermostat", 1.0), 4),
                  "shrink": round(state.get("shrink", 1.0), 4), "thermo": [round(float(x), 4) for x in s.thermo],
                  "frac": round(frac, 4), "thick": round(vol / max(frac, 1e-9), 3),
                  "target": round(float(s.target_fraction()), 4),
                  "src_actual": state.get("src_actual"), "src_nominal": state.get("src_nominal"),
                  "budget": {k: round(v, 1) for k, v in s.budget.items()}})
    if int(s.t) % 100 == 0 and abs(s.t - round(s.t)) < 1e-9:
        print(f"  {s.t:g} Myr {time.time() - t0:.0f} s ice {s.sea_ice:.0f} dT {s.dT:+.1f}", flush=True)


sim.run(myr, on_step)
d = {"seed": seed, "myr": myr, "level": level, "params": sets, "fix": FIX, "seconds": round(time.time() - t0),
     **sim.diag.as_dict(), "extra": extra}
tag = f"seed{seed}_L{level}"
with gzip.open(out / f"{tag}.json.gz", "wt") as f:
    json.dump(d, f)
print("done", out / f"{tag}.json.gz")
