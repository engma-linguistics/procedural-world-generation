"""Scout 203: tallies over rows203.json (written by scout1_an.py): warm/cold tails per arm and pooled, and whether a
draw's warm finish repeats in its twin (same seed, tag and roll; the arms differ only by the height cap).
usage: python scout1_tally.py ROWS.json"""
import json
import sys

import numpy as np

R = json.load(open(sys.argv[1]))
for a, rows in R.items():
    T = np.array([r["endT"] for r in rows])
    co2 = np.array([r["co2"] for r in rows])
    pco2 = np.array([r["pco2"] for r in rows])
    ice = np.array([r["ice"] for r in rows])
    warm = [r for r in rows if not r["ok"] and r["maxwT"] > 0 and ("temperature" in r["why"] and r["endT"] > 0 or r["ice"] < 1)]
    cold = [r for r in rows if not r["ok"] and r not in warm]
    print(f"{a}: n {len(rows)}; end T median {np.median(T):+.2f} mean {T.mean():+.2f} p10 {np.percentile(T, 10):+.2f} p90 {np.percentile(T, 90):+.2f}")
    print(f"   end T > +3: {(T > 3).sum()}, > +3.5: {(T > 3.5).sum()}, > +5: {(T > 5).sum()}, < -6: {(T < -6).sum()}")
    print(f"   end CO2 index median {np.median(co2):+.2f}; end pCO2 median {np.median(pco2):.0f}; end land ice median {np.median(ice):.1f}%")
    print(f"   warm-side fails {len(warm)}: " + "; ".join(f"{r['name']} {r['endT']:+.1f} ({r['why']}, ice {r['ice']:.1f}%)" for r in warm))
    print(f"   cold-side fails {len(cold)}: " + "; ".join(f"{r['name']} {r['endT']:+.1f} ({r['why']}, ice {r['ice']:.1f}%)" for r in cold))
if len(R) == 2:
    a, b = list(R)
    A = {r["name"]: r for r in R[a]}
    B = {r["name"]: r for r in R[b]}
    names = sorted(set(A) & set(B))
    x = np.array([A[n]["endT"] for n in names])
    y = np.array([B[n]["endT"] for n in names])
    print(f"twins ({len(names)}): corr(end T {a}, end T {b}) {np.corrcoef(x, y)[0, 1]:+.2f}; sd of twin difference {np.std(y - x):.2f} C")
    for n in names:
        if (not A[n]["ok"]) or (not B[n]["ok"]) or A[n]["endT"] > 5 or B[n]["endT"] > 5:
            print(f"   {n}: {a} {A[n]['endT']:+.1f} {'pass' if A[n]['ok'] else 'FAIL'} | {b} {B[n]['endT']:+.1f} {'pass' if B[n]['ok'] else 'FAIL'} | drift {A[n]['drift']:+.2f}")
    # the seed's own drift (the source walk shares its random stream across tags and rolls)
    dr = np.array([A[n]["drift"] for n in names])
    print(f"   corr(drift, end T) {a} {np.corrcoef(dr, x)[0, 1]:+.2f}, {b} {np.corrcoef(dr, y)[0, 1]:+.2f}; drift values: {sorted(set(np.round(dr, 2)))}")
