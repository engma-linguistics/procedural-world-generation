"""The runs' own ice response: over 300-1000 Myr, pooled per level, the icehouse share (sea level from ice <=
ICEHOUSE_SL) and mean sea_ice in bins of the step's dT. usage icecurve.py LEVEL FILE..."""
import glob
import gzip
import json
import os
import sys

sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-add5294651351a842")
import numpy as np  # noqa: E402

from tools import ice_criteria as C  # noqa: E402

lev = sys.argv[1]
files = []
for a in sys.argv[2:]:
    files += sorted(glob.glob(a))
dT, si = [], []
for f in files:
    if f"_L{lev}." not in os.path.basename(f):
        continue
    d = json.load(gzip.open(f))
    for s in d["steps"]:
        if s["t"] >= 300:
            dT.append(s["dT_end"])
            si.append(s["sea_ice"])
dT, si = np.array(dT), np.array(si)
print(f"L{lev}: {len(files)} files, {len(dT)} steps, icehouse {100 * (si <= C.ICEHOUSE_SL).mean():.0f}%, "
      f"mean dT {dT.mean():+.2f}")
edges = [-9, -1, 0, 1, 2, 3, 4, 5, 6, 15]
for lo, hi in zip(edges[:-1], edges[1:]):
    m = (dT >= lo) & (dT < hi)
    if m.sum():
        print(f"  dT {lo:+3d}..{hi:+3d}: n {m.sum():5d}  icehouse {100 * (si[m] <= C.ICEHOUSE_SL).mean():5.1f}%  "
              f"sea_ice mean {si[m].mean():7.1f}  median {np.median(si[m]):7.1f}")
