"""PW-1726 (lane 310): the shred gap's side measures from judgediag.py output, paired per draw.
usage: shredjudge.py OUT_ROOT ARM_A ARM_B   (OUT_ROOT/<ARM>_r<roll>_<tag>/seed*_L6.json.gz, as paired_margin.sh lays out)
Per draw: quick shreds / quick births / all shreds / births over 100-1000 and 200-1000 Myr (L5-equivalent cells),
the late (600-1000 Myr) means of the margin record's land %, continental crust %, mean continental thickness and the
plate count, the 100-300 Myr mean plate count (the spin-up, PW-1318), the plates at 1 Gyr, and the end T (true global mean at the last step). Then per measure: the median of
B - A, the number of draws with B > A / B < A, and the exact two-sided sign test. Harness only."""
import gzip
import json
import math
import sys
from pathlib import Path

import numpy as np

root, A, B = Path(sys.argv[1]), sys.argv[2], sys.argv[3]


def load(p):
    r = json.load(gzip.open(p))
    ss = r["steps"]
    m = {s["t"]: s for s in ss if "flick" in s}
    late = [m[t] for t in m if 600 <= t <= 1000]
    f1000, f100, f200 = m[max(m)]["flick"], m[100.0]["flick"], m[200.0]["flick"]
    out = {}
    for k in ("shred_q", "birth_q", "shred", "birth"):
        out[k + " 100-1000"] = f1000[k] - f100[k]
        out[k + " 200-1000"] = f1000[k] - f200[k]
    out["land % (late)"] = float(np.mean([s["margin"]["land"] for s in late]))
    out["cont crust % (late)"] = float(np.mean([s["margin"]["cont"] for s in late]))
    out["thick km (late)"] = float(np.mean([s["margin"]["thick"] for s in late]))
    out["plates (100-300 mean)"] = float(np.mean([m[t]["plates"] for t in m if 100 <= t <= 300]))  # the spin-up (PW-1318)
    out["plates (late mean)"] = float(np.mean([s["plates"] for s in late]))
    out["plates at 1 Gyr"] = m[max(m)]["plates"]
    last = ss[-1]
    out["end T (C)"] = float(last.get("true_temp_c", float("nan")))
    out["late T (C)"] = float(np.mean([s["true_temp_c"] for s in ss if s["t"] >= 600 and "true_temp_c" in s]))
    return out


def arm(name):
    d = {}
    for p in sorted(root.glob(f"{name}_r*_*/seed*_L6.json.gz")):
        d[(p.parent.name[len(name):], p.name)] = load(p)
    return d


def sign_p(d):
    d = [x for x in d if x != 0]
    n, k = len(d), sum(x > 0 for x in d)
    if n == 0:
        return 1.0
    k = min(k, n - k)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2**n)


ra, rb = arm(A), arm(B)
keys = sorted(set(ra) & set(rb))
print(f"{len(keys)} paired draws ({A} {len(ra)}, {B} {len(rb)})")
print(f"| measure | {A} median | {B} median | median {B} - {A} | {B} > {A} | {B} < {A} | sign p |")
print("|---|---|---|---|---|---|---|")
for m in ra[keys[0]]:
    a = np.array([ra[k][m] for k in keys])
    b = np.array([rb[k][m] for k in keys])
    d = b - a
    print(f"| {m} | {np.median(a):.2f} | {np.median(b):.2f} | {np.median(d):+.2f} | {(d > 0).sum()} | {(d < 0).sum()} "
          f"| {sign_p(list(d)):.3f} |")
if "--table" in sys.argv:
    for k in keys:
        print(k, {m: (round(ra[k][m], 2), round(rb[k][m], 2)) for m in ("shred_q 100-1000", "land % (late)", "end T (C)")})
