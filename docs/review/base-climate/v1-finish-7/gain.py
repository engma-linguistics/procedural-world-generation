"""usage: gain.py BASE_ROOT RUN_ROOT : paired (same seed-draw) differences over 600-1000 Myr, run - base: offset,
dT, co2_term, ln w_temp (the weathering's temperature factor), w_T; the thermostat's realised gain
-dco2_term/ddT and the passed share ddT/doffset."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np


def load(f):
    st = json.load(gzip.open(f))["steps"]
    t = np.array([s["t"] for s in st])
    m = t >= 600
    g = lambda k: np.array([s.get(k) if s.get(k) is not None else np.nan for s in st], float)[m]  # noqa: E731
    out = {k: np.nanmean(g(k)) for k in ("offset", "dT", "co2_term", "w_T", "albedo_term", "drift")}
    out["lnw"] = np.nanmean(np.log(g("w_temp")))
    return out


rows = []
for f in sorted(Path(sys.argv[2]).rglob("seed*_L6.json.gz")):
    b = Path(sys.argv[1]) / f.parent.name / f.name
    if not b.exists():
        continue
    r, q = load(f), load(b)
    rows.append({k: r[k] - q[k] for k in r})
for k in rows[0]:
    print(k, f"{np.median([x[k] for x in rows]):+.3f}")
med = lambda f: np.median([f(x) for x in rows])  # noqa: E731
print("n", len(rows), "gain -dco2/ddT", f"{med(lambda x: -x['co2_term'] / x['dT']):.2f}",
      "passed ddT/doff", f"{med(lambda x: x['dT'] / x['offset']):.2f}",
      "dlnw/dwT", f"{med(lambda x: x['lnw'] / x['w_T']):.3f}", "dwT/ddT", f"{med(lambda x: x['w_T'] / x['dT']):.2f}")
