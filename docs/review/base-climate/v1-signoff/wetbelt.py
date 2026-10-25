"""Land rain and temperature by latitude band, and tree cover per band, from finished world json (read-only)."""
import json, sys
import numpy as np
sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-af6c091bd3379671c")
from planet.grid import build_grid
for wid in sys.argv[1:]:
    d = json.load(open(f"/home/daniel/personal/repos/procedural-world-generation/worlds/{wid}.json"))
    L = d["layers"]; g = build_grid(d["meta"]["level"])
    A = lambda k: np.asarray(L[k], float)  # noqa: E731
    el, ice, P, T, tr = A("elevation"), A("ice"), A("precipitation"), A("temperature"), A("tree_cover")
    land = (el > 0) & (ice <= 0)
    lat = np.abs(np.degrees(g.lat) if np.abs(g.lat).max() < 3.2 else g.lat)
    row = []
    for a, b in [(0, 10), (10, 25), (25, 45), (45, 65)]:
        m = land & (lat >= a) & (lat < b)
        row.append(f"{a}-{b}: P {np.median(P[m]):5.0f} T {np.mean(T[m]):4.1f} tree {np.mean(tr[m]):4.1f} wet>1500 {100*(P[m]>1500).mean():3.0f}%")
    v = d["meta"].get("vegetation", {})
    pc = v.get("pco2") if isinstance(v, dict) else None
    print(wid, f"pco2 {pc}", " | ".join(row))
