import sys, os, numpy as np
WT = "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-abbf08ba762366c44"
sys.path.insert(0, WT)
from planet import store as S
from planet.grid import build_grid
from planet.timezoom.sim import LAYERS
OUT = os.path.dirname(os.path.abspath(__file__)) + "/out"
g = build_grid(4)
dec = lambda a, k="ice": S.decode(a, LAYERS[k]).astype(float)
edges = [-90, -75, -65, -55, -45, 45, 55, 65, 75, 90]
for tag in sys.argv[1:]:
    d = np.load(f"{OUT}/end_{tag}.npz")
    i, j = int(d["i"]), int(d["j"])
    print(tag, "frames t", d["t"][i], d["t"][j])
    for lab, k in (("on@i", ("ice_on", i)), ("off@i", ("ice_off", i)), ("on@j", ("ice_on", j)), ("off@j", ("ice_off", j))):
        H = dec(d[k[0]][k[1]])
        row = []
        for a, b in zip(edges[:-1], edges[1:]):
            m = (g.lat >= a) & (g.lat < b)
            row.append(f"{H[m].sum() / 1000:6.1f}")
        print(f"  {lab:6s} ice-km-sum by band {' '.join(row)}")
print("bands", edges)
