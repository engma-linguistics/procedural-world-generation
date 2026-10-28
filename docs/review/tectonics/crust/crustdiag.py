"""tools/ice_diag.py with crust and shelf numbers added to the recorded steps (every 10 Myr): shelf (0..-200 m)
% of the ocean, median submerged continental elevation, mean continental thickness, continental and land %,
largest plate %. Same arguments as ice_diag; run from the code checkout being judged (cwd). Harness only."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet.tectonics import diag  # noqa: E402

_step = diag.Recorder.step


def step(self, sim):
    _step(self, sim)
    t = float(sim.t)
    if abs(t / 10 - round(t / 10)) > 1e-6 or t < 100:
        return
    rec = self.steps[-1]
    e, cont = sim.w_elev, sim.w_cont
    sea = e <= 0
    sub = sea & cont
    share = np.bincount(sim.owner, minlength=int(sim.plates.alive.size)) / sim.grid.n
    rec["crust"] = {"shelf": round(100 * float((e[sea] > -200).mean()), 2),
                    "sub_med": int(np.median(e[sub])) if sub.any() else 0,
                    "thick": round(float(sim.w_thick[cont].mean()), 2),
                    "cont": round(100 * float(cont.mean()), 2),
                    "land": round(100 * float((e > 0).mean()), 2),
                    "plate_max": round(100 * float(share.max()), 1),
                    "thin20": round(100 * float((sim.w_thick[cont] < 20).mean()), 1)}


diag.Recorder.step = step
sys.argv = [str(Path.cwd() / "tools" / "ice_diag.py")] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
