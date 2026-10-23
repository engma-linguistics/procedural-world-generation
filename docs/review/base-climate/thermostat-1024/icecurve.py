"""usage: icecurve.py LABEL=DIAG_DIR ... -- the ice against dT per seed (steps after 300 Myr), so trees compare with
standard errors over seeds: per seed, the icehouse share (ice SL <= -20 m) and the mean ice sea level in dT windows,
and a logistic fit of P(icehouse) on dT (its 50% point, dT50); mean +- SE over the seeds."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

T0 = 300.0
WIN = ((-3, -1), (-1, 1), (1, 3))


def logit50(x, y):
    a, b = 0.0, -1.0  # P = 1 / (1 + exp(-(a + b x)))
    for _ in range(50):  # Newton on the log-likelihood
        p = 1 / (1 + np.exp(-(a + b * x)))
        w = p * (1 - p) + 1e-9
        H = np.array([[w.sum(), (w * x).sum()], [(w * x).sum(), (w * x * x).sum()]])
        gr = np.array([(y - p).sum(), ((y - p) * x).sum()])
        a, b = np.array([a, b]) + np.linalg.solve(H + 1e-6 * np.eye(2), gr)
    return -a / b


def se(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return v.mean(), v.std(ddof=1) / np.sqrt(len(v)), len(v)


for arg in sys.argv[1:]:
    label, d = arg.split("=", 1)
    per = []
    for p in sorted(Path(d).glob("seed*_L6.json.gz")):
        st = [s for s in json.load(gzip.open(p))["steps"] if s["t"] >= T0 and "dT" in s]
        dT = np.array([s["dT"] for s in st])
        si = np.array([s["sea_ice"] for s in st])
        row = {"dT50": logit50(dT, (si <= -20).astype(float)), "mean_dT": dT.mean()}
        for lo, hi in WIN:
            m = (dT >= lo) & (dT < hi)
            row[f"ih{lo:+d}"] = 100 * (si[m] <= -20).mean() if m.sum() >= 10 else np.nan
            row[f"sl{lo:+d}"] = si[m].mean() if m.sum() >= 10 else np.nan
        per.append(row)
    out = []
    for k in per[0]:
        m, s, n = se([r[k] for r in per])
        out.append(f"{k} {m:+.2f} +- {s:.2f} (n {n})")
    print(f"{label}: " + "; ".join(out))
