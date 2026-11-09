"""Lane 254 (PW-1597): the stored calendar of a run against the after-run tree rebuilt on the same history (techtree.rebuild: the
whole run's contacts, tracks and present ranges, the ledger's town footprint), so the live tree's inputs can be told from the
history's. Read-only. argv: run_dir [run_dir ...]. Prints the 12 largest peoples' writing (median, round14/measure.py's) and the
dates of the techs a state needs (kingship, law, proto-writing, writing, cities), stored / rebuilt, per people."""
import json
import statistics as st
import sys
from pathlib import Path

from planet.lineages import techtree as TT

TECHS = ("towns", "cities", "kingship", "law", "proto_writing", "writing")
for d in map(Path, sys.argv[1:]):
    m = json.loads((d / "run.json").read_text())["meta"]
    pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in m["lineages"]}
    ks = m["techtree"]["known"]
    kr = TT.rebuild(d)["known"]
    top = sorted([p for p in ks if p in pops], key=lambda p: -pops[p])[:12]

    def med(k):
        w = [x for x in ((k.get(p) or {}).get("writing", [None])[0] for p in top) if x is not None]
        return f"{st.median(w) * 1000:,.0f} ya ({len(w)}/12)" if w else "none"
    print(f"=== {d.name}: writing median, stored {med(ks)} / rebuilt {med(kr)}")
    for p in top:
        cells = []
        for t in TECHS:
            a, b = (ks.get(p) or {}).get(t), (kr.get(p) or {}).get(t)
            f = lambda v: f"{v[0] * 1000:,.0f}" if v else "-"
            cells.append(f"{t} {f(a)}/{f(b)}")
        print(f"  {p[:12]:12s} " + "  ".join(cells))
