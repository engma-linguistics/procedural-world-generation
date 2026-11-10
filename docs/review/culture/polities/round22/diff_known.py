"""Lane 265 (PW-1597, round22.md): where the live tree (stored meta.techtree of a switch-on run) first parts from the after-run tree
rebuilt on the same history with the footprint the live tree read (round19/live_run.py's dump, as round20/rebuild_live_foot.py).
Read-only. argv: run_dir live_dump.json [n] [hold]. hold: the rebuilt tree reads each people's population, density and range
at the stored frame at or before a time, held until the next (as the live tree, which has no later frame yet), not drawn straight
toward the next frame (techtree._at, _area_at). Prints the 12 largest peoples' writing median both ways, then the n oldest (people,
tech) records that differ (date, how, from), oldest first."""
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

from planet.lineages import techspread as TS
from planet.lineages import techtree as TT

d, dump = Path(sys.argv[1]), Path(sys.argv[2])
n = int(sys.argv[3]) if len(sys.argv) > 3 else 30
if "hold" in sys.argv[4:]:
    def _j(a, ago):
        k = np.flatnonzero(np.asarray(a) >= ago - 1e-9)  # (series oldest first: the last frame at or before the time)
        return int(k[-1]) if len(k) else 0

    TT._at = lambda ser, ago: (float(ser[1][_j(ser[0], ago)]), float(ser[2][_j(ser[0], ago)]))
    TT._area_at = lambda ser, ago: None if ser is None else (lambda v: v if v > 0 else None)(float(ser[3][_j(ser[0], ago)]))
    print("rebuilt tree: tracks held at the frame at or before each time")
m = json.loads((d / "run.json").read_text())["meta"]
pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in m["lineages"]}
live_known = m["techtree"]["known"]
top = sorted([p for p in live_known if p in pops], key=lambda p: -pops[p])[:12]
fp = json.loads(dump.read_text())
fp = {k: (v if k == "_cell_km2" else (np.array(v[0]), np.array(v[1]))) for k, v in fp.items()}
fp["_cell_km2"] = TS.town_footprint(d)["_cell_km2"]
TS.town_footprint = lambda run_dir: fp
rb = TT.rebuild(d)["known"]


def med(k):
    w = [x for x in ((k.get(p) or {}).get("writing", [None])[0] for p in top) if x is not None]
    return f"{st.median(w) * 1000:,.0f} ya ({len(w)}/12)" if w else "none"


print(f"=== {d.name}: writing median of the 12 largest: live {med(live_known)}, rebuilt on the live footprint {med(rb)}")
rows = []
for p in sorted(set(live_known) | set(rb)):
    a, b = live_known.get(p) or {}, rb.get(p) or {}
    for t in sorted(set(a) | set(b)):
        x, y = a.get(t), b.get(t)
        if x is None or y is None or abs(x[0] - y[0]) > 1e-6 or x[1] != y[1] or x[2] != y[2]:
            rows.append((max(x[0] if x else -1, y[0] if y else -1), p, t, x, y))
rows.sort(key=lambda r: -r[0])
print(f"{len(rows)} records differ; the oldest {n}:")
for r in rows[:n]:
    print(f"  {r[1]:22s} {r[2]:18s} live {r[3]}  rebuilt {r[4]}")
