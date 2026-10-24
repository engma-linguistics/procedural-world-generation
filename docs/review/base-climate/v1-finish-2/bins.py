"""usage: bins.py DIAG_DIR [KEY ...] -- ice_diag runs: per 100 Myr bin, the median over seeds of each key's bin mean
(log for the carbon cycle's raw rates). Shows when a trend starts and whether the start (REF_FREEZE 300 Myr) had settled."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

d = Path(sys.argv[1])
keys = sys.argv[2:] or ["dT", "drift", "co2_term", "albedo_term", "source_raw", "w_supply", "w_plant", "w_temp",
                        "land", "sea_ice"]
LOG = {"source_raw", "sink_raw", "w_supply", "w_plant", "w_temp", "src_newc", "src_arc"}
edges = np.arange(0, 1001, 100)
tab = {k: [] for k in keys}
for p in sorted(d.glob("seed*_L6.json.gz")):
    st = [s for s in json.load(gzip.open(p))["steps"] if s.get("sink_raw", 0) > 0]
    t = np.array([s["t"] for s in st])
    for k in keys:
        x = np.array([s.get(k, np.nan) for s in st], float)
        x = np.log(np.maximum(x, 1e-6)) if k in LOG else x
        tab[k].append([np.nanmean(x[(t >= a) & (t < b)]) for a, b in zip(edges[:-1], edges[1:])])
print("bin(Myr) " + " ".join(f"{k[:9]:>9}" for k in keys) + "   (ln for " + ", ".join(sorted(LOG & set(keys))) + ")")
for i, a in enumerate(edges[:-1]):
    print(f"{a:4.0f}-{a + 100:<4.0f} " + " ".join(f"{np.nanmedian([r[i] for r in tab[k]]):+9.3f}" for k in keys))
