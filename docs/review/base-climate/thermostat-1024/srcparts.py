"""usage: srcparts.py DIAG_DIR -- srcsplit.py runs: per seed after 300 Myr, the arc share of the volcanic source,
the arc gain (the continental-volume thermostat's factor) median and range, and each part's answer on the drift
(trends out, as decomp.py: sens x iv(ln part) / WEATHER_CO2, C per C), with the newc / arc split of ln src's iv
(iv(ln src) = share-weighted iv of ln newc and ln arc, to first order). Also corr(ln arc gain, ln arc part)."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

T0, TREND, WEATHER_CO2 = 300.0, 200.0, 0.4


def hp(y, n):
    pad = np.r_[np.full(n, y[:n].mean()), y, np.full(n, y[-n:].mean())]
    return y - np.convolve(pad, np.ones(2 * n + 1) / (2 * n + 1), "same")[n:-n]


rows = []
for p in sorted(Path(sys.argv[1]).glob("seed*_L6.json.gz")):
    r = json.load(gzip.open(p))
    sens = r.get("params", {}).get("co2_sensitivity", 3.0) / np.log(2.0)
    st = [s for s in r["steps"] if s["t"] >= T0 and s.get("src_arc") is not None and s.get("sink_raw", 0) > 0]
    f = lambda k: np.array([s[k] for s in st], float)
    t, dT, drift = f("t"), f("dT"), f("drift")
    newc, arc, gain, src = f("src_newc"), f("src_arc"), f("arc_gain"), f("source_raw")
    n = max(1, int(round(TREND / 2 / float(np.median(np.diff(t))))))
    dh = hp(drift, n)
    cdh = float(np.cov(hp(dT, n), dh)[0, 1])
    iv = lambda y: sens / WEATHER_CO2 * float(np.cov(hp(y, n), dh)[0, 1]) / cdh
    share = float(np.mean(arc / src))
    nz = newc > 0
    rows.append(dict(seed=p.name.split("_")[0][4:], arc_share=share, gain_med=float(np.median(gain)),
                     gain_lo=float(np.percentile(gain, 5)), gain_hi=float(np.percentile(gain, 95)),
                     at_clip=float(np.mean(gain >= 4.999)), src=iv(np.log(src)), arc=iv(np.log(arc)),
                     gain=iv(np.log(gain)), newc=iv(np.log(np.maximum(newc, 1.0))),
                     arc_wo_gain=iv(np.log(arc / gain)),
                     c=float(np.corrcoef(hp(np.log(gain), n), hp(np.log(arc), n))[0, 1])))
keys = ["arc_share", "gain_med", "gain_lo", "gain_hi", "at_clip", "src", "arc", "gain", "arc_wo_gain", "newc", "c"]
print("seed " + " ".join(keys))
for r in rows:
    print(f"{r['seed']:>5} " + " ".join(f"{r[k]:+.2f}" for k in keys))
print("median " + " ".join(f"{k} {np.median([r[k] for r in rows]):+.2f}" for k in keys))
