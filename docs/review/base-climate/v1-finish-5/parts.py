"""Compare ice_diag tracks' temperature parts across levels: usage parts.py FILE..."""
import glob
import gzip
import json
import sys

import numpy as np

keys = ["dT", "drift", "co2_term", "albedo_term", "ice_frac", "iced_land", "src", "sink", "w_temp", "w_plant",
        "ero_bare", "bare", "runoff", "cont", "land", "bed_mean", "bed_p90", "sea_ice", "sea_tect"]
files = []
for a in sys.argv[1:]:
    files += sorted(glob.glob(a))
for f in files:
    d = json.load(gzip.open(f))
    st = d["steps"]
    t = np.array([s["t"] for s in st])
    for lo, hi in [(0, 300), (300, 1000)]:
        m = (t >= lo) & (t < hi)
        vals = []
        for k in keys:
            v = np.array([np.nan if s.get(k) is None else s[k] for s in st], float)
            vals.append(f"{k}={np.nanmean(v[m]):.3g}")
        print(f"{f.split('/')[-2]}/{f.split('/')[-1][:-8]} {lo}-{hi}: " + " ".join(vals))
