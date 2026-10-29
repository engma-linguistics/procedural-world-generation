"""usage: bins.py GLOB... -> per 100 Myr bin, the median over draws of each draw's bin mean (steps with dt 2 Myr only,
so the finish window's 0.5 Myr steps don't bias per-step amounts)."""
import glob
import gzip
import json
import sys

import numpy as np

K = ["sea_tect", "sea_ice", "land", "w_area", "w_supply", "w_rate", "source_raw", "drift", "co2", "dT"]
for g in sys.argv[1:]:
    fs = sorted(glob.glob(g))
    tab = np.full((len(fs), 10, len(K)), np.nan)
    for i, f in enumerate(fs):
        st = [r for r in json.load(gzip.open(f))["steps"] if 0 < r["t"] <= 990]
        for b in range(10):
            rs = [r for r in st if 100 * b <= r["t"] < 100 * b + 100]
            for j, k in enumerate(K):
                v = [r[k] for r in rs if r.get(k) is not None]
                tab[i, b, j] = np.mean(v) if v else np.nan
    print(f"{g}: {len(fs)} draws")
    print("   t " + " ".join(f"{k[:9]:>9}" for k in K))
    med = np.nanmedian(tab, axis=0)
    for b in range(10):
        print(f"{100 * b:4d} " + " ".join(f"{v:9.4g}" for v in med[b]))
