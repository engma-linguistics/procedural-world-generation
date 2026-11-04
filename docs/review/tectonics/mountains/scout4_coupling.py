"""PW-1446 scout 193: does the outgassing co-vary with the erosion supply across planets, per arm, and is it stable?

    uv run python docs/review/tectonics/mountains/scout4_coupling.py JUDGE_DIR [SCREEN_DIR]

For each arm (main, cap) and each sub-window of the late window (and the whole of it), the correlation across the 36
draws of the window means of ln source_raw and ln w_supply, and of ln source_raw against ln w_rate (erosion per eroding
cell, the relief/uplift part of the supply) and ln w_area (the ice-free land, the climate's part). With SCREEN_DIR (the
8-draw screen, where both arms carry the hypsometry), also corr(ln source, land above 2/3/4 km) per arm.
"""
import glob
import gzip
import json
import math
import os
import sys

import numpy as np

WINDOWS = ((300, 600), (600, 733), (733, 866), (866, 1000), (600, 1000))


def load(d, arm):
    out = {}
    pats = [f"{arm}_r0.0005_*", f"{arm}_r0.001_*"] if "judge36" in d else [f"{arm}_r*"]
    for pat in pats:
        for p in sorted(glob.glob(os.path.join(d, pat, "seed*_L6.json.gz"))):
            out[os.path.basename(os.path.dirname(p))[len(arm) + 1:] + ":" + os.path.basename(p)[4:].split("_")[0]] = \
                json.load(gzip.open(p))
    return out


def wmean(d, k, lo, hi, log=True, rows="steps"):
    v = [s[k] for s in d[rows] if lo <= s["t"] <= hi and s.get(k)]
    return float(np.mean([math.log(x) for x in v] if log else v))


def main():
    j = sys.argv[1]
    arms = {arm: load(j, arm) for arm in ("main", "cap")}
    ds = sorted(set(arms["main"]) & set(arms["cap"]))
    print(f"{len(ds)} draws; r across draws of window means")
    print(f"{'window':>10s} {'arm':>5s} {'r(src,sup)':>10s} {'r(src,rate)':>11s} {'r(src,area)':>11s} {'sd(src-sup)':>11s}")
    for lo, hi in WINDOWS:
        for arm, D in arms.items():
            s = np.array([wmean(D[d], "source_raw", lo, hi) for d in ds])
            w = np.array([wmean(D[d], "w_supply", lo, hi) for d in ds])
            r = np.array([wmean(D[d], "w_rate", lo, hi) for d in ds])
            a = np.array([wmean(D[d], "w_area", lo, hi) for d in ds])
            print(f"{lo:4d}-{hi:4d} {arm:>5s} {np.corrcoef(s, w)[0, 1]:10.2f} {np.corrcoef(s, r)[0, 1]:11.2f}"
                  f" {np.corrcoef(s, a)[0, 1]:11.2f} {(s - w).std(ddof=1):11.3f}")
    # how steady the spread itself is: per window, sd across draws of dT and of the imbalance ln(source / sink), and
    # a permutation test of the sd ratio: swap the arms' labels draw by draw (paired), 4000 times; p two-sided.
    # And the same on |dT - median| (Brown-Forsythe's measure, robust to the tails)
    rng = np.random.default_rng(3)

    def perm(x, y, stat):
        obs = stat(y) / stat(x)
        hits = 0
        for _ in range(4000):
            s = rng.random(len(x)) < 0.5
            xa, ya = np.where(s, y, x), np.where(s, x, y)
            r = stat(ya) / stat(xa)
            hits += abs(math.log(r)) >= abs(math.log(obs)) - 1e-12
        return obs, hits / 4000

    def sd(v):
        return v.std(ddof=1)

    def mad(v):
        return np.mean(np.abs(v - np.median(v)))

    print(f"\n{'window':>10s}  sd dT main / cap   sd ln(src/sink) main / cap   sd ratio  p    mean|dev| ratio  p")
    for lo, hi in WINDOWS:
        dT, net = [], []
        for arm, D in arms.items():
            dT.append(np.array([wmean(D[d], "dT", lo, hi, log=False) for d in ds]))
            net.append(np.array([wmean(D[d], "source_raw", lo, hi) - wmean(D[d], "sink_raw", lo, hi) for d in ds]))
        r1, p1 = perm(dT[0], dT[1], sd)
        r2, p2 = perm(dT[0], dT[1], mad)
        print(f"{lo:4d}-{hi:4d}  {dT[0].std(ddof=1):5.2f} / {dT[1].std(ddof=1):5.2f}"
              f"        {net[0].std(ddof=1):6.3f} / {net[1].std(ddof=1):6.3f}           {r1:5.2f} {p1:6.3f}"
              f"   {r2:5.2f} {p2:6.3f}")
    print(f"corr of late dT between the arms, draw by draw: {np.corrcoef(dT[0], dT[1])[0, 1]:+.2f}")
    if len(sys.argv) > 2:
        sc = {arm: load(sys.argv[2], arm) for arm in ("main", "cap")}
        dd = sorted(set(sc["main"]) & set(sc["cap"]))
        print(f"\nscreen ({len(dd)} draws), late window: r(ln source, land above 2/3/4 km), r(ln supply, same)")
        for arm, D in sc.items():
            s = np.array([wmean(D[d], "source_raw", 600, 1000) for d in dd])
            w = np.array([wmean(D[d], "w_supply", 600, 1000) for d in dd])
            hs = [np.array([wmean(D[d], k, 600, 1000, log=False, rows="hyps") for d in dd]) for k in ("p2", "p3", "p4")]
            print(f"  {arm:5s} src: " + " ".join(f"{np.corrcoef(s, h)[0, 1]:+.2f}" for h in hs)
                  + "   sup: " + " ".join(f"{np.corrcoef(w, h)[0, 1]:+.2f}" for h in hs)
                  + f"   r(src,sup) {np.corrcoef(s, w)[0, 1]:+.2f}")


if __name__ == "__main__":
    main()
