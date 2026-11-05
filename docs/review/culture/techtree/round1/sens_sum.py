"""Summary of sens.py: per code, per nudge, how far dates move against the same code's base draw. argv: sens.json [techs]"""
import json, sys
import numpy as np
R = json.load(open(sys.argv[1]))
T = sys.argv[2].split(",") if len(sys.argv) > 2 else ["writing"]
rows = {(r["code"], r["seed"], r["nudge"]): r for r in R["rows"]}
print("run", R["run"], "draws", len(R["seeds"]))
for t in T:
    print(f"\n{t}: nudge | code | world-first move yr: median, max, draws > 1,000 yr | per-people move yr (peoples known in either): median, p90, max | known in one only")
    for nd in ("border", "pop"):
        for c in ("main", "new"):
            wf, pp, one = [], [], 0
            for s in R["seeds"]:
                b, n = rows[(c, s, "base")]["known"], rows[(c, s, nd)]["known"]
                fb = max([v[t][0] for v in b.values() if v[t][0] is not None], default=None)
                fn = max([v[t][0] for v in n.values() if v[t][0] is not None], default=None)
                if fb is not None and fn is not None:
                    wf.append(abs(fb - fn) * 1000)
                for p in b:
                    x, y = b[p][t][0], (n.get(p) or {}).get(t, [None])[0]
                    if x is None and y is None:
                        continue
                    if (x is None) != (y is None):
                        one += 1
                        continue
                    pp.append(abs(x - y) * 1000)
            wf, pp = np.array(wf), np.array(pp)
            print(f"  {nd} | {c} | {np.median(wf):,.0f}, {wf.max():,.0f}, {(wf > 1000).sum()}/{len(wf)} | "
                  f"{np.median(pp):,.0f}, {np.percentile(pp, 90):,.0f}, {pp.max():,.0f} (n {len(pp)}) | {one}")
    print(f"  base spread over draws (world first {t}, yr ago): " + "; ".join(
        f"{c} median {np.median(v):,.0f} min {min(v):,.0f} max {max(v):,.0f} (in {len(v)}/{len(R['seeds'])})" for c in ("main", "new")
        for v in [[max([q[t][0] for q in rows[(c, s, 'base')]['known'].values() if q[t][0] is not None], default=np.nan) * 1000
                   for s in R["seeds"]]] for v in [[x for x in v if x == x]]))
