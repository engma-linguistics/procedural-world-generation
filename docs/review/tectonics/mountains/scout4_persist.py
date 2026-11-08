"""PW-1446 scout 193: how long a draw's climate anomaly lasts, per arm (why the 400 Myr late mean spreads wider when no
133 Myr window does).

    uv run python docs/review/tectonics/mountains/scout4_persist.py JUDGE_DIR

Per arm, over the late window (600-1000 Myr) of the 36 draws: the within-run sd, the lag autocorrelation (after
removing each run's late mean, pooled over draws) at 10/25/50/100/200 Myr of dT, ln source_raw, ln w_supply,
ln(source / sink) and the drift; and the correlation across draws of the three 133 Myr window means of dT
(window 1 vs 2, 2 vs 3, 1 vs 3).
"""
import math
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from scout4_coupling import load, wmean  # noqa: E402

LAGS = (10, 25, 50, 100, 200)


def series(d, k):
    st = [s for s in d["steps"] if 600 <= s["t"] <= 1000 and s.get("w_supply") and s.get("sink_raw")]
    t = np.array([s["t"] for s in st])
    if k == "imb":
        v = np.array([math.log(s["source_raw"] / s["sink_raw"]) for s in st])
    elif k in ("dT", "drift", "co2", "albedo_term"):
        v = np.array([s[k] for s in st])
    else:
        v = np.array([math.log(s[k]) for s in st])
    return t, v


def acf(D, ds, k):
    out, sds = [], []
    for lag in LAGS:
        num = den = 0.0
        for d in ds:
            t, v = series(D[d], k)
            g = np.interp(np.arange(600, 1001, 2.0), t, v)  # (steps are 2 Myr; regular grid for the lags)
            g = g - g.mean()
            n = lag // 2
            num += float((g[:-n] * g[n:]).sum()) / (len(g) - n)
            den += float((g * g).mean())
        out.append(num / den)
    for d in ds:
        sds.append(series(D[d], k)[1].std())
    return out, float(np.mean(sds))


def main():
    arms = {arm: load(sys.argv[1], arm) for arm in ("main", "cap")}
    ds = sorted(set(arms["main"]) & set(arms["cap"]))
    print(f"{len(ds)} draws. autocorrelation at lag " + " / ".join(f"{x}" for x in LAGS) + " Myr; mean within-run sd")
    for k in ("dT", "co2", "albedo_term", "source_raw", "w_supply", "imb", "drift"):
        for arm, D in arms.items():
            r, s = acf(D, ds, k)
            print(f"  {k:12s} {arm:5s} " + " ".join(f"{x:+.2f}" for x in r) + f"   sd {s:.3f}")
    wins = ((600, 733), (733, 866), (866, 1000))
    for arm, D in arms.items():
        m = np.array([[wmean(D[d], "dT", lo, hi, log=False) for lo, hi in wins] for d in ds])
        c = np.corrcoef(m.T)
        print(f"{arm}: corr of window-mean dT across draws: w1-w2 {c[0, 1]:+.2f}, w2-w3 {c[1, 2]:+.2f},"
              f" w1-w3 {c[0, 2]:+.2f}")


if __name__ == "__main__":
    main()
