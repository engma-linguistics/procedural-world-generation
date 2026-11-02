import sys, json
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gpu", "scripts"))
from stages import load, stage_of
from collections import defaultdict
fn = sys.argv[1]; top = int(sys.argv[2]) if len(sys.argv) > 2 else 40
d, rows, excl = load(fn)
wall = d["wall"]
pe = defaultdict(float); n = defaultdict(int); st = defaultdict(lambda: defaultdict(float))
for p, e in excl.items():
    if "CheckpointWriter.submit" in p or p == ("timeline.simulate",):
        continue
    if not p[-1].startswith("K:"):
        pe[p[-1]] += e; n[p[-1]] += rows[p][1]; st[p[-1]][stage_of(p)] += e
    else:
        pe["K:" + p[-1][2:]] += 0
print(f"wall {wall:.1f}")
tot = sum(pe.values())
print(f"python-side exclusive total (excl. writer thread): {tot:.1f}s")
for k, v in sorted(pe.items(), key=lambda x: -x[1])[:top]:
    s = max(st[k].items(), key=lambda x: x[1])[0] if st[k] else ""
    print(f"{k:55s}{v:7.2f}s {100*v/wall:4.1f}% n={n[k]:6d} {1000*v/max(n[k],1):7.2f}ms  [{s}]")
