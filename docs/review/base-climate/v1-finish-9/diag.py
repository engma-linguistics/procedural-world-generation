"""Offline vegetation diagnosis on a stored world's climate (sign-off method: V.model, rain held)."""
import json, sys, time, os
import numpy as np
W = os.environ.get("PWROOT", "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-a859f6d1291b796bd")
sys.path.insert(0, W)
from planet import vegetation as V
from planet.grid import build_grid
CF = float(os.environ.get("CLOUDF", 1)); wid = sys.argv[1]
runs = [tuple(float(y) for y in x.split(":")) for x in sys.argv[2:]]  # pco2:shift
d = json.load(open(f"/home/daniel/personal/repos/procedural-world-generation/worlds/{wid}.json"))
L = d["layers"]; g = build_grid(d["meta"]["level"])
A = lambda k: np.asarray(L[k], float)
el, tj, ta = A("elevation"), A("temperature_jul"), A("temperature_jan")
tw, tc = np.maximum(tj, ta), np.minimum(tj, ta)
ice = A("ice"); P = A("precipitation")
lat = np.abs(np.degrees(g.lat) if np.abs(g.lat).max() < 3.2 else g.lat)
land0 = (el > 0) & (ice <= 0)
eqw = land0 & (lat < 10) & (P > 2000)
print(wid, "L", d["meta"]["level"], "stored tree", round(100*float(A("tree_cover")[land0].mean()),1) if A("tree_cover").max()>1.5 else round(100*float(A("tree_cover")[land0].mean()),1),
      "stored wet-eq", round(float(A("tree_cover")[eqw].mean()),1), "pco2", d["meta"]["vegetation"].get("pco2"), "n wet-eq", int(eqw.sum()), flush=True)
pown = float(d['meta']['vegetation'].get('pco2') or 350)
for pc, sh in runs:
    pc = pown if pc < 0 else pc
    t0 = time.time()
    m = V.model(g, el, A("temperature") + sh, tw + sh, tc + sh, A("precipitation_jul"), A("precipitation_jan"), 23.4,
                A("cloud_jul") / 100 * CF, A("cloud_jan") / 100 * CF, ice=ice, pco2=pc, cheap=False)
    tr = V.tree_cover(m["pot"], m["eq"]["nu"]); la = m["land"]
    nu = m["eq"]["nu"]
    eq = la & (lat < 10)
    wq = la & (lat < 10) & (P > 2000)
    i = V.IDX
    def mean(a, mk): return 100*float(a[mk].mean()) if mk.any() else float("nan")
    tb = m["types"]
    print(f" pco2 {pc:4.0f} dT {sh:+.0f}: tree {mean(tr,la):5.1f}  eq {mean(tr,eq):5.1f}  wet-eq {mean(tr,wq):5.1f} | wet-eq TrBE {mean(nu[i['TrBE']],wq):4.1f} TrBR {mean(nu[i['TrBR']],wq):4.1f} C4G {mean(nu[i['C4G']],wq):4.1f} C3G {mean(nu[i['C3G']],wq):4.1f}"
          f" | npp TrBE {np.mean(m['pot']['npp'][i['TrBE']][wq]):5.0f} C4G {np.mean(m['pot']['npp'][i['C4G']][wq]):5.0f} ok TrBE {mean(m['pot']['ok'][i['TrBE']].astype(float),wq):3.0f}% burned {mean(m['eq']['burned'],wq):4.1f}  ({time.time()-t0:.0f}s)", flush=True)
