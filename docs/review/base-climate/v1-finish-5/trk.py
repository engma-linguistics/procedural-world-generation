"""track.py outputs per 100 Myr: thermostat gain g, area shrink s, continent share c, thickness h, and the CO2
source as counted (A) and at the arcs' nominal rate (N), each relative to its own 200-300 Myr mean; plus the
300-1000 means of dT and the CO2 term. usage trk.py FILE..."""
import glob
import gzip
import json
import sys

import numpy as np

files = []
for a in sys.argv[1:]:
    files += sorted(glob.glob(a))
for f in files:
    d = json.load(gzip.open(f))
    ex = d["extra"]
    t = np.array([e["t"] for e in ex])
    g = {k: np.array([np.nan if e.get(k) is None else e[k] for e in ex], float)
         for k in ["thermostat", "shrink", "frac", "thick", "src_actual", "src_nominal"]}
    ref = (t >= 200) & (t < 300)
    rows = []
    for lo in range(0, 1000, 100):
        m = (t > lo) & (t <= lo + 100)
        rows.append(f"g{np.nanmean(g['thermostat'][m]):.2f} s{np.nanmean(g['shrink'][m]):.2f} "
                    f"c{np.nanmean(g['frac'][m]):.3f} h{np.nanmean(g['thick'][m]):.1f} "
                    f"A{np.nanmean(g['src_actual'][m]) / np.nanmean(g['src_actual'][ref]):.2f} "
                    f"N{np.nanmean(g['src_nominal'][m]) / np.nanmean(g['src_nominal'][ref]):.2f}")
    st = d["steps"]
    ts = np.array([s["t"] for s in st])
    late = ts >= 300
    dT = np.mean([s["dT"] for s, l in zip(st, late) if l])
    co2 = np.mean([s["co2_term"] for s, l in zip(st, late) if l])
    src = np.mean([s["src"] for s, l in zip(st, late) if l])
    print(f"{f.split('/')[-2]}/{f.split('/')[-1][:-8]} fix={d.get('fix')} 300-1000: dT {dT:+.2f} co2 {co2:+.2f} "
          f"src {src:.2f}")
    for lo, r in zip(range(0, 1000, 100), rows):
        print(f"   {lo:4d}: {r}")
