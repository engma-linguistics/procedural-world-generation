"""Tree cover of a finished world's climate at several pCO2 (vegetation.model, cheap), read-only."""
import json, sys
import numpy as np
sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-af6c091bd3379671c")
import planet  # noqa
from planet import vegetation as V
from planet.grid import build_grid
wid = sys.argv[1]; pcs = [float(x) for x in sys.argv[2:]]
d = json.load(open(f"/home/daniel/personal/repos/procedural-world-generation/worlds/{wid}.json"))
L = d["layers"]; g = build_grid(d["meta"]["level"])
def A(k):
    v = L[k]
    if isinstance(v, dict):
        v = v.get("data", v.get("values"))
    return np.asarray(v, float)
el, tj, ta = A("elevation"), A("temperature_jul"), A("temperature_jan")
tw, tc = np.maximum(tj, ta), np.minimum(tj, ta)
ice = A("ice")
land = (el > 0) & (ice <= 0)
print(wid, "stored tree", round(100 * float(A("tree_cover")[land].mean()), 1), "pco2", str(d["meta"]["vegetation"])[:30])
for pc in pcs:
    m = V.model(g, el, A("temperature"), tw, tc, A("precipitation_jul"), A("precipitation_jan"), 23.4,
                A("cloud_jul"), A("cloud_jan"), ice=ice, pco2=pc, cheap=False)
    tr = V.tree_cover(m["pot"], m["eq"]["nu"])
    print(f"  pco2 {pc:5.0f}: tree {100 * float(tr[m['land']].mean()):5.1f}%")
    lat = np.abs(np.degrees(g.lat) if np.abs(g.lat).max() < 3.2 else g.lat)
    eqm = m["land"] & (lat < 10)
    print(f"      equatorial tree {100 * float(tr[eqm].mean()):5.1f}%  stored equatorial {float(A('tree_cover')[eqm].mean()):5.1f}")
