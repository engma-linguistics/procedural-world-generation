"""usage: a22pool.py (in laneA22/): F taken apart on seeds 1-24, main (lane A21's fdiag_main*, the same planet/ as
main 69db596) against this lane, on the harness's worlds and the null draws +-0.001 C. Also the pass counts of the
forest test's three assertions on fdiag's own numbers."""
import json

import numpy as np

T = {"main": ["fdiag_main", "fdiag_main_eps", "fdiag_main_epsm"], "A22": ["fdiag_a22", "fdiag_a22_eps", "fdiag_a22_epsm"]}
R = {f: json.load(open(f + ".json")) for v in T.values() for f in v}


def ok(r):
    return r["F"] < 0 and r["lost"] >= 5 and r["cooling"] < -0.1


for tree, fs in T.items():
    print(tree, "passes:", " ".join(f"{f.split('_', 1)[1]} {sum(ok(r) for r in R[f])}/24" for f in fs))
K = ["F", "F_all_lo_free", "F_all_lo_snow", "F_all_hi_snow", "F_all_hi_free", "F_loss_snow", "F_gain_free",
     "F_rest_free", "dtree_lo40", "dtree_hi40", "run_dT", "snow0_land", "tree0_lo40", "tree0_hi50", "co2"]
print(f"\n{'mean over 72 worlds':22s} {'main':>8s} {'A22':>8s}")
for k in K:
    m = [r[k] for f in T["main"] for r in R[f]]
    a = [r[k] for f in T["A22"] for r in R[f]]
    print(f"{k:22s} {np.nanmean(m):+8.3f} {np.nanmean(a):+8.3f}")
print("\nper draw, F below 40 deg (snow-free) and F, main / A22:")
for fm, fa in zip(T["main"], T["A22"]):
    lo = [np.mean([r["F_all_lo_free"] for r in R[f]]) for f in (fm, fa)]
    F = [np.mean([r["F"] for r in R[f]]) for f in (fm, fa)]
    print(f"  {fa:16s} lo {lo[0]:+.3f} / {lo[1]:+.3f}   F {F[0]:+.3f} / {F[1]:+.3f}")
