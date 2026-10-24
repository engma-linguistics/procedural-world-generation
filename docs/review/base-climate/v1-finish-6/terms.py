"""usage: terms.py DIR... : pooled medians over 300-1000 Myr of the global temperature's parts (drift, CO2 term, albedo
term, ln source/ref) and of the drift's sd, per directory tree (ice_diag outputs, recursive)."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

for d in sys.argv[1:]:
    acc = {k: [] for k in ("drift", "co2_term", "albedo_term", "lnsrc", "dT", "drift_sd")}
    for f in sorted(Path(d).rglob("seed*_L6.json.gz")):
        st = json.load(gzip.open(f))["steps"]
        t = np.array([s["t"] for s in st]); late = t >= 300
        g = lambda k: np.array([s[k] for s in st])[late]  # noqa: E731
        for k in ("drift", "co2_term", "albedo_term", "dT"):
            acc[k].append(g(k).mean())
        acc["lnsrc"].append(np.log(g("src")).mean())
        acc["drift_sd"].append(g("drift").std())
    print(f"{Path(d).name:>6} n={len(acc['dT'])}: " + ", ".join(f"{k} {np.median(v):+.2f}" for k, v in acc.items()))
