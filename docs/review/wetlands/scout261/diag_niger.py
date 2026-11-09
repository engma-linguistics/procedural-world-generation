"""PW-831 scout 261: the Niger's course on Earth (earth_capture.py's pickle) with the dry-hollow rule off (it then
reaches the sea): per cell ground, the Earth outlet height, the filled spill level of the uncarved ground, the
kept-hollow mask of the rule, flow. Usage: diag_niger.py PKL [--obsrain]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "docs/review/wetlands/scout260"))
import numpy as np
from planet import hydrology as Hy, kernels
import earth_wet as EWt

cap = []
orig = Hy._dry_hollows
Hy._dry_hollows = lambda *a: cap.append(orig(*a)) or cap[-1]
EWt.run(sys.argv[1], label="rule on", hook=EWt.obs_rain if "--obsrain" in sys.argv else None)
keep = cap[0]
Hy.DRY_HOLLOWS = False
out, d = EWt.run(sys.argv[1], label="rule off", hook=EWt.obs_rain if "--obsrain" in sys.argv else None)
import pickle
D = pickle.load(open(sys.argv[1], "rb"))
g, down, flow, land = d["grid"], d["down"], d["flow"], d["land"]
elev, outlet = D["elev"], D["kw"]["outlet"]
fz = kernels.priority_flood(elev.astype(float), ~land, g.nbr_off, g.nbr_idx, 0.0)[0]
q = Hy.discharge(g, flow)
i = int(np.argmin(np.where(land, (g.lat - 13.95) ** 2 + (g.lon + 5.36) ** 2, np.inf)))
for t in range(45):
    print(f"{t:2d} {g.lat[i]:5.1f} {g.lon[i]:6.1f} z {elev[i]:6.1f} outlet {outlet[i]:6.1f} spill {fz[i]:6.1f} "
          f"kept {int(keep[i])} Q {q[i]:6.0f} P {d['c']['precip'][i]:5.0f} Eo {d['c']['lake_evap'][i]:5.0f}")
    if down[i] < 0 or not land[down[i]]:
        break
    i = int(down[i])
