"""Inclusive time (all call sites, outermost only) of named functions. python funcs.py prof.json scale name..."""
import json, sys
d = json.load(open(sys.argv[1]))
scale = float(sys.argv[2])
for nm in sys.argv[3:]:
    s = n = 0
    for r in d["rows"]:
        p = r["path"]
        if p[-1] == nm and nm not in p[:-1]:
            s += r["s"]; n += r["n"]
    print(f"  {nm:<50s} {s * scale:7.2f}s  n={n}")
