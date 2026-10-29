"""usage: decomp.py ARM_A ARM_B ROLL -> paired per-draw decomposition of the late CO2 (800-990 Myr means, 2 Myr steps):
ln src_rel = ln sink_rel + ln co2_law(X). sink_rel = supply * warm * plants / ref_sink. Prints each term's ln for
both arms and the medians of the B - A differences."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

J = Path(__file__).resolve().parent / "judge"
A, B, R = sys.argv[1:4]


def terms(f):
    st = [r for r in json.load(gzip.open(f))["steps"] if 800 <= r["t"] <= 990 and r["t"] == int(r["t"]) and int(r["t"]) % 2 == 0]
    sp = [r for r in json.load(gzip.open(f))["steps"] if 250 <= r["t"] < 300]
    m = lambda rs, k: float(np.mean([r[k] for r in rs if r.get(k) is not None]))
    ref_sink = m(st, "sink_raw") / m(st, "sink")
    ref_src = m(st, "source_raw") / m(st, "src")
    return {"lnsrc_rel": np.log(m(st, "src")), "ln_ref_src": np.log(ref_src), "ln_src_raw": np.log(m(st, "source_raw")),
            "ln_ref_sink": np.log(ref_sink), "ln_supply": np.log(m(st, "w_supply")), "ln_supply_spin": np.log(m(sp, "w_supply")),
            "ln_warm": np.log(m(st, "w_temp")), "ln_plant": np.log(m(st, "w_plant")), "co2": m(st, "co2"), "dT": m(st, "dT"),
            "land": m(st, "land"), "land_spin": m(sp, "land"), "w_q": m(st, "w_q"), "w_q_spin": m(sp, "w_q"),
            "w_area": m(st, "w_area"), "w_T": m(st, "w_T")}


rows = {}
for arm in (A, B):
    for d in J.glob(f"{arm}_r{R}_*"):
        for f in d.glob("seed*_L6.json.gz"):
            rows.setdefault((d.name.split("_", 2)[2], f.name.split("_")[0]), {})[arm] = terms(f)
keys = sorted(k for k in rows if len(rows[k]) == 2)
names = list(rows[keys[0]][A])
print(f"{len(keys)} paired draws; medians: {A} | {B} | median(B - A)")
for n in names:
    a = [rows[k][A][n] for k in keys]
    b = [rows[k][B][n] for k in keys]
    print(f"  {n:>15}: {np.median(a):9.4f} | {np.median(b):9.4f} | {np.median(np.subtract(b, a)):+9.4f}")
