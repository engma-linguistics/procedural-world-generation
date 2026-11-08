"""What drives the slow tail (round 3, PW-1490): the lag from ready of the taken cases against the taker's border with its first
holder neighbour, its range and its insularity (the factors of techtree.contact_rate's front). python tail.py a.json [b.json ...]"""
import json, sys

import numpy as np


def bins(x, y, edges, label):
    print(f"\n| {label} | cases | median lag (yr) | lag >= 1,000 yr |")
    print("|---|---|---|---|")
    for lo, hi in zip(edges[:-1], edges[1:]):
        k = (x >= lo) & (x < hi)
        if k.sum():
            print(f"| {lo:g}-{hi:g} | {int(k.sum()):,} | {np.median(y[k]):,.0f} | {(y[k] >= 1000).mean():.0%} |")


for f in sys.argv[1:]:
    D = json.loads(open(f).read())
    km, area, ins, lag, era = [], [], [], [], []
    for d in D["draws"]:
        P = d["people"]
        for p, t, k, E, tp, rd, how, ekm in d["cases"]:
            if rd is None or tp is None or tp >= rd:
                continue
            km.append(ekm)
            area.append(P[p]["area"] or np.nan)
            ins.append(P[p]["ins"] if P[p]["ins"] is not None else np.nan)
            lag.append((rd - tp) * 1000)
            era.append(rd)
    km, area, ins, lag, era = map(np.asarray, (km, area, ins, lag, era))
    print(f"\n### {D['run']}: taken cases, lag from ready ({len(lag):,} cases, {len(D['draws'])} draws)")
    bins(km, lag, [0, 100, 300, 750, 1500, 1e9], "border with the first holder (km, at the present)")
    bins(area, lag, [0, 1, 3, 10, 30, 1e9], "taker's range now (Mkm2)")
    bins(ins, lag, [0, 0.3, 0.5, 0.7, 1.01], "taker's insularity")
    bins(era, lag, [0, 2, 5, 10, 20, 1e9], "ready date (kyr ago)")
