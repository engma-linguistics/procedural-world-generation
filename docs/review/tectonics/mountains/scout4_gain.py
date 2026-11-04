"""PW-1446 scout 193: the CO2 thermostat's gain per draw on both judge arms (tools/ice_diag.gain, instrumented on the
drift, which is the same random walk in both arms), paired.

    uv run python docs/review/tectonics/mountains/scout4_gain.py JUDGE_DIR [--a main --b cap]

Per draw: co2_hp (C of CO2 warming per C of cooling, 200 Myr trends out; bar 0.35-0.9), g (d ln sink / dT on the
drift), its parts (supply, temp, plant), dT/drift (how much of the drift reaches dT: 1 = no brake). Prints the arm
medians and means, the paired differences with a bootstrap CI, and whether the change in gain tracks the change in
|late dT - arm mean|.
"""
import argparse
import glob
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools import ice_criteria as C  # noqa: E402
from tools.ice_diag import gain  # noqa: E402


def rows(dirpath, arm):
    out = {}
    for p in sorted(glob.glob(os.path.join(dirpath, f"{arm}_r0.0005_*", "seed*_L6.json.gz"))
                    + glob.glob(os.path.join(dirpath, f"{arm}_r0.001_*", "seed*_L6.json.gz"))):
        grp = os.path.basename(os.path.dirname(p))[len(arm) + 1:]
        seed = os.path.basename(p)[4:].split("_")[0]
        d = C.load(p)
        k = gain(d)
        late = [s["dT"] for s in d["steps"] if 600 <= s["t"] <= 1000]
        out[f"{grp}:{seed}"] = {"co2_hp": k["iv"]["co2_hp"], "co2": k["iv"]["co2"], "g": k["iv"]["g"],
                                "sup": k["iv"]["parts"]["supply"], "temp": k["iv"]["parts"]["temp"],
                                "plant": k["iv"]["parts"]["plant"], "dT_drift": k["dT_drift"],
                                "g_ols": k["g"], "late": float(np.mean(late))}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--a", default="main")
    ap.add_argument("--b", default="cap")
    a = ap.parse_args()
    A, B = rows(a.dir, a.a), rows(a.dir, a.b)
    ds = sorted(set(A) & set(B))
    la, lb = np.array([A[d]["late"] for d in ds]), np.array([B[d]["late"] for d in ds])
    dev = np.abs(lb - lb.mean()) - np.abs(la - la.mean())
    rng = np.random.default_rng(2)
    print(f"{len(ds)} paired draws")
    print(f"{'':9s} {'med a':>7s} {'med b':>7s} {'mean a':>7s} {'mean b':>7s} {'paired':>7s}  95% CI          r(d, d|dev|)")
    for k in ("co2_hp", "co2", "g", "sup", "temp", "plant", "dT_drift", "g_ols"):
        x, y = np.array([A[d][k] for d in ds]), np.array([B[d][k] for d in ds])
        dd = y - x
        bs = [dd[rng.integers(0, len(dd), len(dd))].mean() for _ in range(4000)]
        lo, hi = np.percentile(bs, [2.5, 97.5])
        print(f"{k:9s} {np.median(x):7.3f} {np.median(y):7.3f} {x.mean():7.3f} {y.mean():7.3f} {dd.mean():7.3f}"
              f"  [{lo:6.3f}, {hi:6.3f}]  {np.corrcoef(dd, dev)[0, 1]:5.2f}")
    print("\nper draw: late dT a b | co2_hp a b | g a b | dT/drift a b")
    for d in ds:
        print(f"{d:24s} {A[d]['late']:6.2f} {B[d]['late']:6.2f} | {A[d]['co2_hp']:5.2f} {B[d]['co2_hp']:5.2f} |"
              f" {A[d]['g']:6.3f} {B[d]['g']:6.3f} | {A[d]['dT_drift']:5.2f} {B[d]['dT_drift']:5.2f}")


if __name__ == "__main__":
    main()
