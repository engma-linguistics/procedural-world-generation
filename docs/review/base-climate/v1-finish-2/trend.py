"""usage: trend.py DIAG_DIR [EARLY_LO EARLY_HI LATE_LO LATE_HI] -- ice_diag (or srcsplit) runs: where the late
history's cooling comes from. Window means late minus early of dT and its parts (drift, CO2 term, ice albedo), and
of the carbon cycle's logs: the source and the sink's parts (supply = fresh rock eroded on bare land, temperature
factor, plant factor). At steady state WEATHER_CO2 * ln X = ln(src/ref) - ln(sink/ref), so the CO2 change splits
into forcings (source, supply, plants) and the thermostat's answer (the temperature factor). Also land share,
the icehouse share per window, and (srcsplit runs) the source's ridge and arc parts."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

A = 0.4
args = sys.argv[1:]
d = Path(args[0])
e0, e1, l0, l1 = (float(x) for x in args[1:5]) if len(args) >= 5 else (300, 500, 600, 1000)
keys = ["dT", "drift", "co2_term", "albedo_term", "aco2", "lsrc", "lsup", "lplant", "ltemp", "land", "ice%"]
extra = ["lnewc", "larc"]
print(f"late {l0:g}-{l1:g} minus early {e0:g}-{e1:g}; aco2 = {A} x dln X; lsrc - lsup - lplant - ltemp ~ aco2")
print("seed  " + " ".join(f"{k:>7}" for k in keys + extra) + "   ice% early/late")
rows = []
for p in sorted(d.glob("seed*_L6.json.gz"), key=lambda p: int(p.name.split("_")[0][4:])):
    r = json.load(gzip.open(p))
    st = [s for s in r["steps"] if s.get("sink_raw", 0) > 0]
    t = np.array([s["t"] for s in st])

    def f(k):
        return np.array([s.get(k, np.nan) for s in st], float)

    v = {"dT": f("dT"), "drift": f("drift"), "co2_term": f("co2_term"), "albedo_term": f("albedo_term"),
         "aco2": A * f("co2"), "lsrc": np.log(f("source_raw")), "lsup": np.log(f("w_supply")),
         "lplant": np.log(f("w_plant")), "ltemp": np.log(f("w_temp")), "land": f("land"),
         "ice%": 100 * (f("sea_ice") <= -20.0), "lnewc": np.log(np.maximum(f("src_newc"), 1e-3)),
         "larc": np.log(np.maximum(f("src_arc"), 1e-3))}
    E, L = (t >= e0) & (t < e1), (t >= l0) & (t <= l1)
    dd = {k: float(np.nanmean(x[L]) - np.nanmean(x[E])) for k, x in v.items()}
    rows.append(dd)
    print(f"{r['seed']:>5} " + " ".join(f"{dd[k]:+7.2f}" for k in keys + extra)
          + f"   {np.mean(v['ice%'][E]):.0f}/{np.mean(v['ice%'][L]):.0f}")
print("median" + " ".join(f"{np.nanmedian([x[k] for x in rows]):+7.2f}" for k in keys + extra))
print("mean  " + " ".join(f"{np.nanmean([x[k] for x in rows]):+7.2f}" for k in keys + extra))
