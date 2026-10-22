"""The zoom's own first-year mass balance on sim4 at -4 C (index off, 2 kyr) under each variant's climate."""
import sys, os, numpy as np
WT = "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-abbf08ba762366c44"
sys.path.insert(0, WT); sys.path.insert(0, WT + "/tests")
from helpers import run_sim
from planet import timezoom as Z
sim = run_sim(); src = Z.source_from_sim(sim); g = src["grid"]
src["dT"] = src["dT"] - 4.0
land = src["elev"] > 0
edges = [-90, -75, -65, -55, -45, 45, 55, 65, 75, 90]
VAR = {"main": dict(S3_REACH="0", S3_FETCH="0", S3_SPLIT="0", S3_MTN="0"), "a2": dict(S3_FBASE="old"), "new": {},
       "nofetch": dict(S3_FETCH="0"), "nosplit": dict(S3_SPLIT="0", S3_FBASE="old"), "noreach": dict(S3_REACH="0", S3_FBASE="old")}
sel = sys.argv[1:] or list(VAR)
print("bands", edges, "land per band", [int((land & (g.lat >= a) & (g.lat < b)).sum()) for a, b in zip(edges[:-1], edges[1:])])
for name in sel:
    env = VAR[name]
    for k in ("S3_REACH", "S3_FETCH", "S3_SPLIT", "S3_MTN"):
        os.environ[k] = env.get(k, "1")
    os.environ["S3_FBASE"] = env.get("S3_FBASE", "new")
    r = Z.simulate(src, kyr=2, step=0.5, every=2.0, params=Z.TZParams(index="off", glacial_dt=6.0, veg="local", phases="0,90,0,90"))
    st = r["state"]
    for key in ("smb", "t_warm", "t_ann", "p_ann", "f_snow"):
        x = st[key]
        row = []
        for a, b in zip(edges[:-1], edges[1:]):
            m = land & (g.lat >= a) & (g.lat < b)
            row.append(f"{x[m].mean():7.2f}")
        print(f"{name:8s} {key:6s} {' '.join(row)}")
    row = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = land & (g.lat >= a) & (g.lat < b)
        row.append(f"{100 * (st['smb'][m] > 0).mean():7.0f}")
    print(f"{name:8s} smb>0% {' '.join(row)}")
