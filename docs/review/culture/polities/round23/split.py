"""Lane 278 (PW-1597, round23.md): splits an on/off calendar gap into its two parts on the same code.
  history:    the after-run tree on the switch-on history against the switch-off run's (both rebuilt alike: ledger footprint);
  accounting: the live tree (stored meta.techtree of the switch-on run) against the after-run tree rebuilt on that same history,
              with the ledger's footprint and with the footprint the live tree read (round19/live_run.py's dump).
Also: the first stored frame at which the two histories part (any line's track), and the n oldest differing (people, tech)
records of each comparison. Read-only. argv: on_dir off_dir live_dump.json [n] [hold]"""
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

from planet.lineages import techspread as TS
from planet.lineages import techtree as TT

on, off, dump = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
if "hold" in sys.argv[5:]:  # (the after-run tree reads the footprint's sample at or before each time, not drawn toward the next)
    def _hold(tw, ago):
        if tw is None:
            return 0.0
        a = np.asarray(tw[0], float)
        k = np.flatnonzero(a >= ago - 1e-9)
        return float(np.asarray(tw[1], float)[k[-1]]) if len(k) else 0.0
    TT.town_cells_at = _hold
    print("footprint held at the sample at or before each time")
n = int(sys.argv[4]) if len(sys.argv) > 4 else 12
M = {k: json.loads((d / "run.json").read_text())["meta"] for k, d in (("on", on), ("off", off))}


def top12(m):
    pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in m["lineages"]}
    return sorted([p for p in m["techtree"]["known"] if p in pops], key=lambda p: -pops[p])[:12]


tops = {k: top12(m) for k, m in M.items()}


def med(k, top):
    w = [x for x in ((k.get(p) or {}).get("writing", [None])[0] for p in top) if x is not None]
    return f"{st.median(w) * 1000:,.0f} ({len(w)}/12)" if w else "none"


# ---- the histories: first stored frame where any line's track differs
tr = {k: {l["id"]: [tuple(round(float(v), 4) for v in r) for r in (l.get("track") or [])] for l in m["lineages"]} for k, m in M.items()}
first = None
for lid in tr["on"]:
    a, b = tr["on"][lid], tr["off"].get(lid, [])
    for i in range(max(len(a), len(b))):
        x, y = (a[i] if i < len(a) else None), (b[i] if i < len(b) else None)
        if x != y:
            t = (x or y)[0]
            if first is None or t > first[0]:
                first = (t, lid, x, y)
            break
print("first track difference (kyr ago, line, on, off):", first)
st_on = {l["id"]: l.get("started_kyr") for l in M["on"]["lineages"]}
st_off = {l["id"]: l.get("started_kyr") for l in M["off"]["lineages"]}
print("lines whose start differs:", [(k, st_on[k], st_off.get(k)) for k in st_on if st_on[k] != st_off.get(k)][:10])

# ---- the calendars
live = M["on"]["techtree"]["known"]
offk = M["off"]["techtree"]["known"]
rb_off = TT.rebuild(off)["known"]
rb_on = TT.rebuild(on)["known"]
fp = json.loads(dump.read_text())
fp = {k: (v if k == "_cell_km2" else (np.array(v[0]), np.array(v[1]))) for k, v in fp.items()}
fp["_cell_km2"] = TS.town_footprint(on)["_cell_km2"]
_tf = TS.town_footprint
TS.town_footprint = lambda run_dir: fp
rb_on_live = TT.rebuild(on)["known"]
TS.town_footprint = _tf
cals = {"live (on, stored)": live, "rebuilt on-history, live footprint": rb_on_live, "rebuilt on-history, ledger footprint": rb_on,
        "rebuilt off-history (ledger)": rb_off, "off (stored)": offk}
for name, k in cals.items():
    print(f"  {name:40s} writing median, on's 12 largest {med(k, tops['on'])}; off's 12 largest {med(k, tops['off'])}")


def diff(a, b, label, n):
    rows = []
    for p in sorted(set(a) | set(b)):
        x0, y0 = a.get(p) or {}, b.get(p) or {}
        for t in sorted(set(x0) | set(y0)):
            x, y = x0.get(t), y0.get(t)
            if x is None or y is None or abs(x[0] - y[0]) > 1e-6 or x[1] != y[1] or x[2] != y[2]:
                rows.append((max(x[0] if x else -1, y[0] if y else -1), p, t, x, y))
    rows.sort(key=lambda r: -r[0])
    print(f"=== {label}: {len(rows)} records differ; the oldest {n}:")
    for r in rows[:n]:
        print(f"  {r[1]:22s} {r[2]:18s} {r[3]}  |  {r[4]}")
    w = [r for r in rows if r[2] == "writing"]
    print(f"  writing differs for {len(w)} peoples; oldest: {[(r[1], r[3], r[4]) for r in w[:4]]}")


diff(live, offk, "live (on) vs off (stored)", n)
diff(rb_on, rb_off, "HISTORY: rebuilt on-history vs rebuilt off-history (same tree, ledger footprints)", n)
diff(live, rb_on_live, "ACCOUNTING (tree): live vs rebuilt on-history with the live footprint", n)
diff(rb_on_live, rb_on, "ACCOUNTING (footprint): rebuilt on-history, live vs ledger footprint", n)
