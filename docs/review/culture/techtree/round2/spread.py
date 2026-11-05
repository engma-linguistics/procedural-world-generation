"""Arm A/B/T (D53) spread summary from measure.py output. argv: m.json tech people[,people]
Per variant over the draws: peoples knowing the tech today (median), the median lag (yr) from the world's first to each people that
TOOK it by contact, and each named people's date (median yr ago, and draws known)."""
import json, sys
import numpy as np
R = json.load(open(sys.argv[1])); t = sys.argv[2]; named = sys.argv[3].split(",")
rows = {(r["var"], r["seed"]): r["known"] for r in R["rows"]}
print("run", R["run"], "draws", len(R["seeds"]), "tech", t)
print("| variant | peoples knowing it today, median | lag first -> each contact taker, median yr | " + " | ".join(named) + " |")
for v in R["vars"]:
    n, lags, per = [], [], {p: [] for p in named}
    for s in R["seeds"]:
        K = rows[(v, s)]
        d = [q[t][0] for q in K.values() if q[t][0] is not None]
        if not d:
            n.append(0); continue
        f = max(d); n.append(len(d))
        lags += [(f - q[t][0]) * 1000 for q in K.values() if q[t][0] is not None and q[t][1] == "contact"]
        for p in named:
            if K.get(p, {}).get(t, [None])[0] is not None:
                per[p].append(K[p][t][0] * 1000)
    cell = lambda xs: f"{np.median(xs):,.0f} ({len(xs)}/{len(R['seeds'])})" if xs else f"- (0/{len(R['seeds'])})"
    print(f"| {v} | {np.median(n):g} | {np.median(lags) if lags else float('nan'):,.0f} | " + " | ".join(cell(per[p]) for p in named) + " |")
