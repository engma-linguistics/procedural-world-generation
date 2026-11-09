"""Lane 258 (PW-1608, PW-1597): the after-run tree rebuilt on a switch-on run's history (techtree.rebuild), once with the run's ledger
footprint (as stored for an off run) and once with the footprint the live tree read (round19/live_run.py's dump), so the
footprint's share of the live/after-run calendar gap can be told from the rest. Read-only.
argv: run_dir live_dump.json. Prints the 12 largest peoples' writing median (round14/measure.py's), stored / rebuilt on each."""
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

from planet.lineages import techspread as TS
from planet.lineages import techtree as TT

d, dump = Path(sys.argv[1]), Path(sys.argv[2])
m = json.loads((d / "run.json").read_text())["meta"]
pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in m["lineages"]}
top = sorted([p for p in m["techtree"]["known"] if p in pops], key=lambda p: -pops[p])[:12]


def med(k):
    w = [x for x in ((k.get(p) or {}).get("writing", [None])[0] for p in top) if x is not None]
    return f"{st.median(w) * 1000:,.0f} ya ({len(w)}/12)" if w else "none"


live = json.loads(dump.read_text())
live = {k: (v if k == "_cell_km2" else (np.array(v[0]), np.array(v[1]))) for k, v in live.items()}
ledger = TS.town_footprint(d)
live["_cell_km2"] = ledger["_cell_km2"]
out = {"stored (live tree)": m["techtree"]["known"]}
_fp = TS.town_footprint
for name, fp in (("rebuilt, ledger footprint", ledger), ("rebuilt, live footprint", live)):
    TS.town_footprint = lambda run_dir, fp=fp: fp
    out[name] = TT.rebuild(d)["known"]
TS.town_footprint = _fp
print(f"=== {d.name}: writing median of the 12 largest")
for k, v in out.items():
    print(f"  {k:28s} {med(v)}")
