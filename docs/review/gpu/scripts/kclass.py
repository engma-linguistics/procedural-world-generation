"""Kernel time by parallel flag: python kclass.py prof.json [per_myr]"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__)); import env  # noqa
import importlib
from collections import defaultdict
from numba.core.registry import CPUDispatcher

fn = sys.argv[1]
per = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
d = json.load(open(fn))
k = defaultdict(lambda: [0.0, 0])
for r in d["rows"]:
    if r["path"][-1].startswith("K:"):
        k[r["path"][-1]][0] += r["s"]
        k[r["path"][-1]][1] += r["n"]
tot = defaultdict(float)
rows = []
for name, (s, n) in k.items():
    mod, f = name[2:].rsplit(".", 1)
    disp = getattr(importlib.import_module("planet." + mod), f)
    par = bool(disp.targetoptions.get("parallel"))
    tot["parallel" if par else "serial"] += s
    rows.append((s, name, par, n))
wall = d["wall"]
print(f"{fn}: wall {wall:.1f}s, scale {per:g} -> parallel kernels {tot['parallel'] * per:.1f}s "
      f"({100 * tot['parallel'] / wall:.1f}%), serial kernels {tot['serial'] * per:.1f}s ({100 * tot['serial'] / wall:.1f}%)")
for s, name, par, n in sorted(rows, reverse=True)[:30]:
    print(f"  {'P' if par else 'S'} {name:<50s} {s * per:7.2f}s {100 * s / wall:5.1f}%  n={n}")
