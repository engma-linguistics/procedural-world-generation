"""usage: iceprobe.py OUT_ROOT ARM... -> Per arm, 300-990 Myr: the ice's sea level change per climate update and per Myr, the albedo term and ice share."""
import gzip, json, sys
from pathlib import Path
import numpy as np
root = Path(sys.argv[1])
for arm in sys.argv[2:]:
    per_up, per_myr, alb, frac, deep = [], [], [], [], []
    for p in sorted(root.glob(f"{arm}_r0.0005_*/seed*_L6.json.gz")):
        r = json.load(gzip.open(p))
        u = [x for x in r["updates"] if 300 <= x["t"] < 990]
        t = np.array([x["t"] for x in u]); s = np.array([x["sea_ice"] for x in u])
        d = np.abs(np.diff(s)); dt = np.diff(t)
        per_up.append(np.median(d[d > 0.5]) if (d > 0.5).any() else 0)
        per_myr.append(np.abs(np.diff(s)).sum() / (t[-1] - t[0]))
        st = [x for x in r["steps"] if 300 <= x["t"] < 990]
        alb.append(np.mean([x["albedo_term"] for x in st])); frac.append(np.mean([x["ice_frac"] for x in st]))
        deep.append(np.mean([x["sea_ice"] < -150 for x in st]))
    f = lambda v: f"{np.median(v):+.3f}"
    print(f"{arm:5s} n={len(alb)} |d sea_ice| per update (moving ones) {f(per_up)} m, path per Myr {f(per_myr)} m/Myr,"
          f" albedo term {f(alb)} C, ice_frac {f(frac)}, share of steps < -150 m {f(deep)}")
