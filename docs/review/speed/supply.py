"""usage: supply.py OUT_ROOT ARM_A ARM_B [--level 6]
-> per window, the paired median of B - A of ln(mean weathering supply), ln(mean raw sink), mean dT and mean CO2:
does the arm's erosion supply relative to its spin-up (where the sink reference is learnt, earth.REF_FREEZE)
differ late? (PW-247's risk 3: a reference learnt from the ramp's 16 Myr cadence erosion.) Harness only."""
import argparse
import gzip
import json
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("a")
ap.add_argument("b")
ap.add_argument("--level", type=int, default=6)
args = ap.parse_args()
root = Path(args.root)


def runs(arm):
    out = {}
    for d in sorted(root.glob(f"{arm}_r*")):
        for p in d.glob(f"seed*_L{args.level}.json.gz"):
            out[(d.name[len(arm):], p.name)] = json.load(gzip.open(p))["steps"]
    return out


A, B = runs(args.a), runs(args.b)
keys = sorted(set(A) & set(B))
wins = ((100, 300), (300, 600), (600, 900), (900, 990), (990, 1000))
print(f"{len(keys)} paired draws; median B - A (B > A count)")
print("| window | ln supply | ln sink_raw | dT | CO2 | ln supply - its 100-300 |")
print("|---|---|---|---|---|---|")
base = {}
for lo, hi in wins:
    row = []
    for f in ("w_supply", "sink_raw", "dT", "co2"):
        d = []
        for k in keys:
            va = np.mean([x[f] for x in A[k] if lo < x["t"] <= hi])
            vb = np.mean([x[f] for x in B[k] if lo < x["t"] <= hi])
            d.append(np.log(vb / va) if f in ("w_supply", "sink_raw") else vb - va)
        d = np.array(d)
        if f == "w_supply":
            if lo == 100:
                base = d
            rel = d - base
        row.append(f"{np.median(d):+.3f} ({(d > 0).sum()})")
    row.append(f"{np.median(rel):+.3f} ({(rel > 0).sum()})")
    print(f"| {lo}-{hi} | " + " | ".join(row) + " |")
