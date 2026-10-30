"""kind_country.py MAIN LANE: per dragon kind, its count per run by pocket country (top 4), main -> lane, over the paired runs."""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
A, B = Path(sys.argv[1]), Path(sys.argv[2])
runs = sorted(set(p.stem for p in A.glob("*.json")) & set(p.stem for p in B.glob("*.json")))
def agg(d):
    out = defaultdict(lambda: defaultdict(float))
    for r in runs:
        pres = json.loads(str(np.load(d / r / "RUN.npz")["pres"]))
        for lid, x in pres.get("megafauna", {}).items():
            for p in x["pocket_list"]:
                out[lid][p["country"]] += p["count"] / len(runs)
    return out
M, L = agg(A), agg(B)
for lid in sorted(set(M) | set(L)):
    cs = sorted(set(M[lid]) | set(L[lid]), key=lambda c: -(L[lid].get(c, 0) + M[lid].get(c, 0)))[:5]
    print(f"{lid:>14}: " + "; ".join(f"{c} {M[lid].get(c, 0):,.0f}->{L[lid].get(c, 0):,.0f}" for c in cs))
