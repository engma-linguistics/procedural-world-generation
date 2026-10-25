import json, sys, os
import numpy as np
W = "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a859f6d1291b796bd"
sys.path.insert(0, W)
from planet import vegetation as V
from planet.grid import build_grid
d = json.load(open(f"{W}/worlds/{sys.argv[1]}.json")); L = d["layers"]; g = build_grid(d["meta"]["level"])
A = lambda k: np.asarray(L[k], float)
el, tj, ta = A("elevation"), A("temperature_jul"), A("temperature_jan"); tw, tc = np.maximum(tj, ta), np.minimum(tj, ta)
ice = A("ice"); P = A("precipitation"); lat = np.abs(np.degrees(g.lat))
wq = (el > 0) & (ice <= 0) & (lat < 10) & (P > 2000)
print("wet-eq T mean", A("temperature")[wq].mean().round(1), "Twarm", tw[wq].mean().round(1))
for sh in (0, 3, 6):
    T = A("temperature") + sh
    s = V.site(g.lat, T, tw + sh, tc + sh, A("precipitation_jul"), A("precipitation_jan"), 23.4, A("cloud_jul")/100, A("cloud_jan")/100)
    via = np.zeros((V.NP, g.n), bool); via[V.IDX["TrBE"]] = wq; via[V.IDX["C4G"]] = wq
    for pc in (350, 180, 1000):
        p = V.potential(s, via, np.ones((V.NP, g.n)), pc)
        i = V.IDX["TrBE"]; gpp = p["gpp"][i][wq]; npp = p["npp"][i][wq]; lai = p["lai"][i][wq]
        resp = gpp - np.where(npp > 0, npp / 0.75, npp)
        print(f"dT {sh:+d} pco2 {pc}: TrBE GPP {np.median(gpp):5.0f} R {np.median(resp):5.0f} NPP {np.median(npp):5.0f} LAI {np.median(lai):3.1f} alpha {np.median(p['alpha'][i][wq]):.2f} | C4G NPP {np.median(p['npp'][V.C4][wq]):4.0f}")
