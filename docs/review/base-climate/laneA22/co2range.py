"""usage (from a tree root): co2range.py -- the runs' CO2 index (frames' stats co2, ln of the stock) in the store:
min / median / max per run, and pooled percentiles. How far a run's plants are from today's CO2 (PW-644's
water-use efficiency scales with it)."""
import glob
import json

import numpy as np

allv = []
for p in sorted(glob.glob("runs/*/run.json")):
    o = json.load(open(p))
    fr = o.get("frames", []) if isinstance(o, dict) else o
    c = [f.get("stats", {}).get("co2") for f in fr if isinstance(f, dict)]
    c = [x for x in c if x is not None]
    if c:
        allv += c
        print(f"{p.split('/')[1]} L{o.get('level', '?')} n={len(c)} min {min(c):+.2f} med {np.median(c):+.2f} "
              f"max {max(c):+.2f}")
if allv:
    print("pooled percentiles 5/25/50/75/95:", np.round(np.percentile(allv, [5, 25, 50, 75, 95]), 2))
