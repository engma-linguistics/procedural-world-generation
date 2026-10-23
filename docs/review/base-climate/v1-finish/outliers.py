"""usage: outliers.py LABEL=sweep_dir ... -- the north-star count per sweep (health --quick folders: report.md +
frames.json.gz): per seed, the keyframes' global mean temperature (median, max), the share of keyframes with ice sea
level below -150 m, the icehouse share (report.md) and the bars; then which seeds are outliers:
  hellhole  median temp > 25 C, or any keyframe > 30 C (beyond the Cretaceous / PETM hothouse, ~20-28 C)
  icebox    deep ice (< -150 m) on >= 30% of keyframes, or icehouse >= 90% of the time (an always-glacial world)
and the pass share (no outlier), with the health bars' pass shares beside it. Pools every LABEL=dir given; a label
used twice (e.g. two seed sets of one tree) pools into one row."""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def table(path):
    """report.md's run rows (as merge-1024/hsum.py reads them)."""
    rows = {}
    for line in open(path):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) == 15 and c[0].isdigit():
            rows[int(c[0])] = dict(dT=c[6], deep=float(c[10]), old=c[12], new=c[13], ice=float(c[14]))
    return rows


def seeds(d):
    d = Path(d)
    rep = table(d / "report.md")
    sw = json.load(open(d / "sweep.json"))
    frames = json.load(gzip.open(d / "frames.json.gz"))
    runs = sw["runs"] if isinstance(sw, dict) and "runs" in sw else sw
    out = {}
    for r in runs:
        s, rid = r.get("seed"), r.get("run") or r.get("id")
        if s not in rep or rid not in frames:
            continue
        f = frames[rid]
        T = np.array([k["temp"] for k in f if k.get("temp") is not None])
        out[s] = dict(rep[s], tmed=float(np.median(T)), tmax=float(T.max()), tmin=float(T.min()))
    return out


rows = defaultdict(dict)
for arg in sys.argv[1:]:
    label, d = arg.split("=", 1)
    rows[label].update(seeds(d))
print("tree | seeds | hellhole | icehouse > 40% (owner's bar) | always-icebox (icehouse >= 90% or deep >= 30%) | pass owner's bar | icehouse % median / mean | old bar ok | new bar ok | temp median / max | failing seeds")
print("|".join(["---"] * 11))
for label, t in rows.items():
    hot = [s for s, r in t.items() if r["tmed"] > 25 or r["tmax"] > 30]
    ice = [s for s, r in t.items() if r["ice"] > 40]
    box = [s for s, r in t.items() if r["deep"] >= 30 or r["ice"] >= 90]
    bad = set(hot) | set(ice) | set(box)
    n = len(t)
    icev = [r["ice"] for r in t.values()]
    print(f"{label} | {n} | {len(hot)} | {len(ice)} | {len(box)} | {n - len(bad)} ({100 * (n - len(bad)) / n:.0f}%) | "
          f"{np.median(icev):.0f} / {np.mean(icev):.0f} +- {np.std(icev, ddof=1) / np.sqrt(n):.0f} | "
          f"{sum(r['old'] == 'ok' for r in t.values())} | {sum(r['new'] == 'ok' for r in t.values())} | "
          f"{np.median([r['tmed'] for r in t.values()]):.1f} / {max(r['tmax'] for r in t.values()):.1f} | "
          + " ".join(f"{s}({'hot ' if s in hot else ''}{'BOX ' if s in box else ''}ice {t[s]['ice']:.0f}%, "
                     f"deep {t[s]['deep']:.0f}%)" for s in sorted(bad)))
