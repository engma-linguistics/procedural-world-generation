"""python tree.py prof.json [min_share] [maxdepth]: print the inclusive call tree."""
import json, sys
from collections import defaultdict
d = json.load(open(sys.argv[1]))
minf = float(sys.argv[2]) if len(sys.argv) > 2 else 0.01
maxd = int(sys.argv[3]) if len(sys.argv) > 3 else 8
wall = d["wall"]
rows = {tuple(r["path"]): (r["s"], r["n"]) for r in d["rows"]}
kids = defaultdict(list)
for p in rows:
    kids[p[:-1]].append(p)


def show(p, depth):
    for c in sorted(kids[p], key=lambda c: -rows[c][0]):
        s, n = rows[c]
        if s / wall < minf:
            continue
        ch = sum(rows[k][0] for k in kids[c])
        print(f"{'  ' * depth}{c[-1]:<60s} {s:8.2f}s {100 * s / wall:5.1f}%  excl {100 * (s - ch) / wall:5.1f}%  n={n}")
        if depth < maxd:
            show(c, depth + 1)


print("wall", round(wall, 1), "load", d.get("load_before"), d.get("load_after"), "threads", d.get("threads"))
show((), 0)
