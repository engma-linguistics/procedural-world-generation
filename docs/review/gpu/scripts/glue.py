"""Per stage: kernel time vs Python-side (numpy + interpreter) exclusive time. python glue.py prof.json scale"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from collections import defaultdict
from stages import load, stage_of
d, rows, excl = load(sys.argv[1])
sc = float(sys.argv[2])
k, g = defaultdict(float), defaultdict(float)
for p, e in excl.items():
    (k if p[-1].startswith("K:") else g)[stage_of(p)] += e
print(f"{sys.argv[1]} (x{sc:g}): stage, numba kernels s, python-side (numpy + interpreter + unwrapped nested kernels) s")
for s in sorted(set(k) | set(g), key=lambda s: -(k[s] + g[s])):
    print(f"  {s:<45s} {k[s] * sc:7.1f} {g[s] * sc:7.1f}")
print(f"  {'total':<45s} {sum(k.values()) * sc:7.1f} {sum(g.values()) * sc:7.1f}")
