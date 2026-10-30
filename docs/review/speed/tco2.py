"""usage: tco2.py OUT_ROOT ARM_A ARM_B [--png FILE] [--level 6]
-> the T and CO2 histories of two paired.sh arms (PW-247's check on a long climate lag): per paired draw, the
oscillation measures over 0-300 and 300-990 Myr (std of dT and of CO2, the rms of dT's 2 Myr steps, the coldest dT,
the share of steps with land ice over 10%), their paired medians, and a PNG of dT and CO2 against time for the first
three draws. Harness only."""
import argparse
import gzip
import json
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("root")
ap.add_argument("a")
ap.add_argument("b")
ap.add_argument("--png")
ap.add_argument("--level", type=int, default=6)
args = ap.parse_args()
root = Path(args.root)


def runs(arm):
    out = {}
    for d in sorted(root.glob(f"{arm}_r*")):
        key = d.name[len(arm):]
        for p in d.glob(f"seed*_L{args.level}.json.gz"):
            out[(key, p.name)] = json.load(gzip.open(p))
    return out


A, B = runs(args.a), runs(args.b)
keys = sorted(set(A) & set(B))


def measures(r, lo, hi):
    s = [x for x in r["steps"] if lo < x["t"] <= hi]
    dT = np.array([x["dT"] for x in s])
    co2 = np.array([x["co2"] for x in s])
    ice = np.array([x["iced_land_pct"] for x in s])
    return dict(sd_dT=dT.std(), sd_co2=co2.std(), step_dT=np.sqrt(np.mean(np.diff(dT) ** 2)), min_dT=dT.min(),
                iced10=np.mean(ice > 10), secs=r["seconds"])


names = ["sd_dT", "sd_co2", "step_dT", "min_dT", "iced10", "secs"]
for lo, hi in ((0, 300), (300, 990)):
    print(f"--- {lo}-{hi} Myr, {len(keys)} paired draws: median {args.a} | median {args.b} | median paired B-A")
    ma = [measures(A[k], lo, hi) for k in keys]
    mb = [measures(B[k], lo, hi) for k in keys]
    for n in names:
        if n == "secs" and lo:
            continue
        a, b = np.array([m[n] for m in ma]), np.array([m[n] for m in mb])
        print(f"  {n:8s} {np.median(a):9.3f} | {np.median(b):9.3f} | {np.median(b - a):+9.3f}  (B > A in {(b > a).sum()}/{len(a)})")
if args.png and keys:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 2, figsize=(12, 8), sharex=True)
    for i, k in enumerate(keys[:3]):
        for arm, r, c in ((args.a, A[k], "k"), (args.b, B[k], "tab:red")):
            t = [x["t"] for x in r["steps"]]
            ax[i, 0].plot(t, [x["dT"] for x in r["steps"]], c, lw=0.7, label=arm)
            ax[i, 1].plot(t, [x["co2"] for x in r["steps"]], c, lw=0.7, label=arm)
        ax[i, 0].set_ylabel(f"{k[0]} {k[1][:10]}\ndT (C)")
        ax[i, 1].set_ylabel("CO2 index")
    ax[0, 0].legend()
    ax[-1, 0].set_xlabel("Myr")
    ax[-1, 1].set_xlabel("Myr")
    fig.tight_layout()
    fig.savefig(args.png, dpi=90)
    print("wrote", args.png)
