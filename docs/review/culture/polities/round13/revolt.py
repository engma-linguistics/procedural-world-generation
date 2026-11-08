"""Round 13 (lane 215, PW-1513): the REVOLT switch's own record in polities_live.json (submissions, risings, retakings), beside
round12/measure.py's fates and heads. argv: run_dir [run_dir ...]."""
import json
import sys
from collections import Counter
from pathlib import Path

for d in map(Path, sys.argv[1:]):
    pl = json.loads((d / "polities_live.json").read_text())
    rv = pl.get("revolt")
    subs = [f for s in pl["steps"] for t in s.get("taken") or [] for f in (t.get("fates") or {}).values() if f[0] == "submitted"]
    print(f"=== {d.name}  submitted (fates) {len(subs)}", end="")
    if rv is None:
        print("  (switch off)")
        continue
    pairs = {(p, r) for _, p, r in rv["submissions"]}
    rose = {(p, r) for _, p, r, _c in rv["revolts"]}
    print(f"  submissions {len(rv['submissions'])} (pairs {len(pairs)})  risings {len(rv['revolts'])} (pairs {len(rose)})"
          f"  retaken {len(rv['punished'])}")
    print("  risings", rv["revolts"])
    fates = Counter(x[3] for x in rv["punished"])
    print("  retaken fates", dict(fates), " heads lost", sum(x[4] for x in rv["punished"]), " moved", sum(x[5] for x in rv["punished"]))
    print("  retaken", rv["punished"])
