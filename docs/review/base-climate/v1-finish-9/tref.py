"""Per-PFT growth temperature (mean of the 3 warmest months) on Earth's model climate, cover-weighted."""
import json, sys
import numpy as np
W = "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a859f6d1291b796bd"
sys.path.insert(0, W)
from planet import vegetation as V
from planet.grid import build_grid
d = json.load(open(f"{W}/worlds/577526.json")); L = d["layers"]; g = build_grid(d["meta"]["level"])
A = lambda k: np.asarray(L[k], float)
el, tj, ta = A("elevation"), A("temperature_jul"), A("temperature_jan"); tw, tc = np.maximum(tj, ta), np.minimum(tj, ta)
m = V.model(g, el, A("temperature"), tw, tc, A("precipitation_jul"), A("precipitation_jan"), 23.4, A("cloud_jul")/100, A("cloud_jan")/100, ice=A("ice"), pco2=350)
twq = np.sort(m["s"]["t"], 0)[-3:].mean(0)
nu = m["eq"]["nu"]; area = np.ones(g.n)
for i, c in enumerate(V.CODES):
    w = nu[i] * m["land"]
    if w.sum() > 0:
        print(c, round(float((w * twq).sum() / w.sum()), 1), "plateau mid", (V.PFTS[i]["temp"][1] + V.PFTS[i]["temp"][2]) / 2, "cover", round(100*float(w.sum()/m["land"].sum()),1))
