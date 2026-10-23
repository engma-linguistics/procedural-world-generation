import json
import sys

import numpy as np

E = sys.argv[1]
R = {k: json.load(open(f"{E}/{k}.json")) for k in sys.argv[2:]}
allr = [r for v in R.values() for r in v]
print("n", len(allr), "pass", sum(r["ok"] for r in allr))
F = np.array([r["F"] for r in allr])
keys = ["run_dT", "snow0", "fs_all", "fs_hi", "fany", "tree_snow", "tree_lo", "tree_hi", "hid", "hid_hi", "mask_mean"]
for k in keys:
    x = np.array([r[k] for r in allr])
    print(f"{k:10s} corr F {np.corrcoef(x, F)[0, 1]:+.2f}  q10/50/90 {np.percentile(x, 10):.3g} {np.percentile(x, 50):.3g} {np.percentile(x, 90):.3g}")
# ratio candidates
for r in allr:
    r["snow_vs_lo"] = r["tree_snow"] / max(r["tree_lo"], 1e-9)
for k in keys + ["snow_vs_lo"]:
    x = np.array([r[k] for r in allr])
    qs = np.percentile(x, [20, 30, 40, 50, 60])
    print(k, " ".join(f"{q:.3g}:{sum(r['ok'] for r in allr if r[k] >= q)}/{sum(1 for r in allr if r[k] >= q)}" for q in qs))
for k, v in R.items():
    print(k, "pass", sum(r["ok"] for r in v), "/", len(v))
print("\nrules per draw: eligible n, pass among eligible / ineligible pass")
for name, rule in [("fs_hi>=0.25", lambda r: r["fs_hi"] >= 0.25), ("snow0>=0.12", lambda r: r["snow0"] >= 0.12),
                   ("hid>=0.26", lambda r: r["hid"] >= 0.26), ("dT<=5", lambda r: r["run_dT"] <= 5)]:
    cells = []
    for k, v in list(R.items()) + [("all", allr)]:
        e = [r for r in v if rule(r)]
        ne = [r for r in v if not rule(r)]
        cells.append(f"{k}:{sum(r['ok'] for r in e)}/{len(e)}|{sum(r['ok'] for r in ne)}/{len(ne)}")
    print(f"{name:12s} " + "  ".join(cells))
