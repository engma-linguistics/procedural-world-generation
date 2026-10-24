"""Offline estimate for option D: how the source's reference compares with causal long-run alternatives.
usage: dref.py FILE.json.gz ...  (ice_diag outputs). Per run, over 300-1000 Myr: mean ln(source/ref) with the frozen
200-300 Myr reference (as run) and with alternatives; the equivalent CO2 warming shift (steady state, X^0.4 = s/w:
d ln X = d ln s / 0.4; 3 C per doubling)."""
import gzip
import json
import sys

import numpy as np

rows = []
for f in sys.argv[1:]:
    d = json.load(gzip.open(f))
    st = d["steps"]
    t = np.array([s["t"] for s in st])
    raw = np.array([s["source_raw"] for s in st])
    src = np.array([s["src"] for s in st])  # source / ref as run
    ref = raw / src
    w = np.array([s["sink"] for s in st])
    dt = np.diff(t, prepend=0)
    cum = np.cumsum(raw * dt) / np.cumsum(dt)  # mean of the source since t=0 (causal)
    late = t >= 300
    out = {"run": f.split("/")[-2] + "/" + f.split("/")[-1].split("_")[0], "ln_s": np.log(src[late]).mean(),
           "ln_w": np.log(w[late]).mean()}
    for name, r in [("cum0", cum)]:
        out[name] = np.log(raw[late] / r[late]).mean()
    for tau in (300, 500, 1000):
        e = np.empty_like(raw); e[0] = raw[0]
        for i in range(1, len(raw)):
            b = 1 - np.exp(-dt[i] / tau); e[i] = e[i - 1] + b * (raw[i] - e[i - 1])
        out[f"ema{tau}"] = np.log(raw[late] / e[late]).mean()
    # mean of 100-T only (since the start settles), frozen nowhere
    m = t >= 100
    c1 = np.where(m, np.cumsum(raw * dt * m) / np.maximum(np.cumsum(dt * m), 1e-9), np.nan)
    out["cum100"] = np.log(raw[late] / c1[late]).mean()
    rows.append(out)
keys = [k for k in rows[0] if k != "run"]
print(f"{'run':>28} " + " ".join(f"{k:>7}" for k in keys))
for r in rows:
    print(f"{r['run']:>28} " + " ".join(f"{r[k]:+7.3f}" for k in keys))
med = {k: np.median([r[k] for r in rows]) for k in keys}
print(f"{'median':>28} " + " ".join(f"{med[k]:+7.3f}" for k in keys))
print("warming vs as-run (C, steady state, 3 C/doubling): " + ", ".join(
    f"{k} {(med[k] - med['ln_s']) / 0.4 * 3 / np.log(2):+.2f}" for k in keys if k not in ("ln_s", "ln_w")))
