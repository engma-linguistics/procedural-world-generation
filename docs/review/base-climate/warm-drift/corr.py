"""usage: corr.py GLOB -> across draws: late (800-990 Myr) dT against the change since the spin-up (250-300 Myr) of
ln supply, ln source_raw, land, w_q; plus each one's correlation and a joint fit."""
import glob
import gzip
import json
import sys

import numpy as np

X = {k: [] for k in ["dT", "co2", "dln_supply", "dln_src", "dland", "dln_q", "dln_supply_per_src", "dln_supply_per_land", "albedo"]}
for f in sorted(glob.glob(sys.argv[1])):
    st = json.load(gzip.open(f))["steps"]
    late = [r for r in st if 800 <= r["t"] <= 990 and int(r["t"]) % 2 == 0 and r["t"] == int(r["t"])]
    sp = [r for r in st if 250 <= r["t"] < 300]
    m = lambda rs, k: float(np.mean([r[k] for r in rs if r.get(k) is not None]))
    X["dT"].append(m(late, "dT"))
    X["co2"].append(m(late, "co2"))
    X["albedo"].append(m(late, "albedo_term"))
    X["dln_supply"].append(np.log(m(late, "w_supply") / m(sp, "w_supply")))
    X["dln_src"].append(np.log(m(late, "source_raw") / m(sp, "source_raw")))
    X["dland"].append(m(late, "land") - m(sp, "land"))
    X["dln_q"].append(np.log(m(late, "w_q") / m(sp, "w_q")))
    X["dln_supply_per_src"].append(X["dln_supply"][-1] - X["dln_src"][-1])
    X["dln_supply_per_land"].append(X["dln_supply"][-1] - np.log(m(late, "w_area") / m(sp, "w_area")))
X = {k: np.array(v) for k, v in X.items()}
print(f"{sys.argv[1]}: {len(X['dT'])} draws")
for k, v in X.items():
    if k in ("dT",):
        continue
    print(f"  {k:>20}: median {np.median(v):+.3f}  corr with late co2 {np.corrcoef(v, X['co2'])[0, 1]:+.2f}, with late dT {np.corrcoef(v, X['dT'])[0, 1]:+.2f}")
