"""usage: hsum.py LABEL=report.md ... -- pooled health numbers per sweep (as lane A23's htable.py reads report.md):
pooled % of keyframes with ice sea level below -150 m (mean over seeds: every seed has the same keyframes), old/new
ice-bar fails, seeds > 10% deep, icehouse % median and mean."""
import sys

import numpy as np


def table(path):
    rows = {}
    for line in open(path):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) == 15 and c[0].isdigit():
            rows[int(c[0])] = dict(dT=c[6], deep=float(c[10]), old=c[12], new=c[13], ice=float(c[14]))
    return rows


print("sweep | seeds | pooled % kf < -150 m | seeds >10% deep | old bar F | new bar F | icehouse % median / mean | per-seed deep%")
for arg in sys.argv[1:]:
    label, rep = arg.split("=", 1)
    t = table(rep)
    deep = [r["deep"] for r in t.values()]
    ice = [r["ice"] for r in t.values()]
    print(f"{label} | {len(t)} | {np.mean(deep):.1f} | {sum(d > 10 for d in deep)} | "
          f"{sum(r['old'] != 'ok' for r in t.values())} | {sum(r['new'] != 'ok' for r in t.values())} | "
          f"{np.median(ice):.1f} / {np.mean(ice):.1f} | " + " ".join(f"{s}:{r['deep']:.1f}" for s, r in sorted(t.items())))
