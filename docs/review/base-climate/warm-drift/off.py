"""usage: off.py FILE... -> the climate's true mean T minus (13.8 + dT_end) against land share, steps after 300 Myr."""
import gzip
import json
import sys

import numpy as np

xs, ys, ds = [], [], []
for f in sys.argv[1:]:
    st = [r for r in json.load(gzip.open(f))["steps"] if r["t"] >= 300 and r.get("true_temp_c") is not None]
    xs += [r["land"] for r in st]
    ys += [r["true_temp_c"] - 13.8 - r["dT_end"] for r in st]
    ds += [r["dT_end"] for r in st]
x, y, d = map(np.array, (xs, ys, ds))
A = np.c_[np.ones_like(x), x, d]
c = np.linalg.lstsq(A, y, rcond=None)[0]
print(f"n {len(x)}: offset = {c[0]:+.2f} {c[1]:+.2f} land {c[2]:+.3f} dT; mean offset {y.mean():+.2f}, land {x.mean():.3f}")
print(f"  -> +3.5 points of land: {0.035 * c[1]:+.2f} C at fixed dT")
