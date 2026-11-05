"""measure.py summary. argv: m.json [people,people|big12] [techs]"""
import json, sys
import numpy as np
R = json.load(open(sys.argv[1]))
rows = {(r["var"], r["seed"]): r["known"] for r in R["rows"]}
T = (sys.argv[3] if len(sys.argv) > 3 else "huts,villages,towns,chiefdoms,tokens,proto_writing,writing,cities,kingship").split(",")
K0 = rows[(R["vars"][0], R["seeds"][0])]
peoples = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] != "all" else list(K0)
yr = lambda x: "-" if x is None or x != x else f"{x * 1000:,.0f}"
print("run", R["run"], "draws", len(R["seeds"]))
for p in peoples:
    print(f"\n{p}: tech | " + " | ".join(f"{v}: in, median yr ago (own inventions)" for v in R["vars"]))
    for t in T:
        cells = []
        for v in R["vars"]:
            xs = [rows[(v, s)].get(p, {}).get(t, [None, None]) for s in R["seeds"]]
            d = [x[0] for x in xs if x[0] is not None]
            own = sum(1 for x in xs if x[1] == "invented")
            cells.append(f"{len(d)}/{len(xs)}, {yr(np.median(d)) if d else '-'} ({own})")
        print(f"  {t} | " + " | ".join(cells))
print("\nworld first (any people): tech | " + " | ".join(f"{v}: median, min-max; peoples inventing it themselves, median" for v in R["vars"]))
for t in T:
    cells = []
    for v in R["vars"]:
        f = [max([q[t][0] for q in rows[(v, s)].values() if q[t][0] is not None], default=None) for s in R["seeds"]]
        f = [x for x in f if x is not None]
        inv = [sum(1 for q in rows[(v, s)].values() if q[t][1] == "invented") for s in R["seeds"]]
        cells.append(f"{yr(np.median(f)) if f else '-'}, {yr(min(f)) if f else '-'}-{yr(max(f)) if f else '-'}; {np.median(inv):g}")
    print(f"  {t} | " + " | ".join(cells))
