"""crusttally.py DIR... : the crust fields crustdiag.py records, per arm (directory prefix before _r), as medians
over draws of each draw's 600-1000 Myr mean, plus the values at 1000 Myr."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

arms = {}
for d in map(Path, sys.argv[1:]):
    arm = d.name.split("_r")[0]
    for p in sorted(d.glob("seed*_L*.json.gz")):
        steps = [s for s in json.load(gzip.open(p))["steps"] if "crust" in s]
        late = [s["crust"] for s in steps if 600 <= s["t"] <= 1000]
        if not late:
            continue
        arms.setdefault(arm, []).append(({k: np.mean([c[k] for c in late]) for k in late[0]}, steps[-1]["crust"]))
keys = ["shelf", "sub_med", "thick", "cont", "land", "plate_max", "thin20"]
for arm, rows in arms.items():
    print(f"{arm} ({len(rows)} draws)")
    print("  600-1000 Myr mean, median over draws:", {k: round(float(np.median([r[0][k] for r in rows])), 2) for k in keys})
    print("  at the end, median over draws:     ", {k: round(float(np.median([r[1][k] for r in rows])), 2) for k in keys})
    print("  sub_med within -100..-500 at the end:", sum(-500 <= r[1]["sub_med"] <= -100 for r in rows), "of", len(rows),
          "; shelf >= 3% at the end:", sum(r[1]["shelf"] >= 3 for r in rows))
