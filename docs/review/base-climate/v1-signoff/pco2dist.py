"""pCO2 (ppm, climate.pco2 of the run's stock) percentiles per window from ice_diag json; args are globs."""
import glob, gzip, json, sys
import numpy as np
for pat in sys.argv[1:]:
    for f in sorted(glob.glob(pat)):
        st = json.load(gzip.open(f))["steps"]
        t = np.array([r["t"] for r in st]); c = 500 * np.exp(np.array([r["co2"] for r in st]))
        out = []
        for a, b in [(300, 1000), (1000, 2001)]:
            m = (t >= a) & (t < b)
            if m.any():
                out.append(f"{a}-{min(b, 2000)}: p10 {np.percentile(c[m], 10):.0f} med {np.median(c[m]):.0f} "
                           f"p90 {np.percentile(c[m], 90):.0f} <180ppm {100 * (c[m] < 180).mean():.0f}%")
        print(f.split('/')[-2], f.split('/')[-1].split('.')[0], " | ".join(out))
