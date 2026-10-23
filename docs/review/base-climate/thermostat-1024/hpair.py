"""usage: hpair.py LABEL=report.md ... -- health sweeps on the same seeds, per tree: the pooled % of keyframes with ice
sea level below -150 m (mean over seeds +- its standard error), seeds > 10%, old / new ice-bar fails, icehouse %
(median / mean +- SE); then each tree against the first, paired by seed (mean difference +- SE, and t = diff / SE).
Reads report.md as merge-1024/hsum.py does."""
import sys

import numpy as np


def table(path):
    rows = {}
    for line in open(path):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) == 15 and c[0].isdigit():
            rows[int(c[0])] = dict(deep=float(c[10]), old=c[12], new=c[13], ice=float(c[14]))
    return rows


def se(x):
    x = np.asarray(x, float)
    return x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else float("nan")


tabs = [(a.split("=", 1)[0], table(a.split("=", 1)[1])) for a in sys.argv[1:]]
print("tree | seeds | pooled % kf < -150 m (+- SE) | seeds > 10% | old bar F | new bar F | icehouse % median / mean (+- SE)")
for label, t in tabs:
    deep = [r["deep"] for r in t.values()]
    ice = [r["ice"] for r in t.values()]
    print(f"{label} | {len(t)} | {np.mean(deep):.1f} +- {se(deep):.1f} | {sum(d > 10 for d in deep)} | "
          f"{sum(r['old'] != 'ok' for r in t.values())} | {sum(r['new'] != 'ok' for r in t.values())} | "
          f"{np.median(ice):.1f} / {np.mean(ice):.1f} +- {se(ice):.1f}")
base_label, base = tabs[0]
print(f"\npaired against {base_label} (same seeds): mean difference +- SE (t)")
for label, t in tabs[1:]:
    common = sorted(set(base) & set(t))
    dd = [t[s]["deep"] - base[s]["deep"] for s in common]
    di = [t[s]["ice"] - base[s]["ice"] for s in common]
    print(f"{label} - {base_label} | {len(common)} seeds | deep % {np.mean(dd):+.1f} +- {se(dd):.1f} "
          f"(t {np.mean(dd) / se(dd):+.1f}) | icehouse % {np.mean(di):+.1f} +- {se(di):.1f} (t {np.mean(di) / se(di):+.1f})")
print("\nper seed: deep % / icehouse %")
seeds = sorted(set().union(*[set(t) for _, t in tabs]))
print("seed | " + " | ".join(lb for lb, _ in tabs))
for s in seeds:
    print(f"{s} | " + " | ".join(f"{t[s]['deep']:.1f} / {t[s]['ice']:.0f}" if s in t else "-" for _, t in tabs))
