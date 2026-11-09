"""Lane 238 (PW-1575): does the read-out name the live polities? argv: run_dir [--gods]. Read-only.
Prints, for a switch-on run: steps and polities in each, cell-for-cell map agreement per step, the viewer's API (server.polities, in
process) for the present, the five largest polities' cards now, and (--gods) gods.py's rulers now beside the live polities' peoples."""
import json
import sys
from pathlib import Path

import numpy as np

from planet import server as SV
from planet.lineages import polities as PO

d = Path(sys.argv[1])
L = json.loads((d / "polities_live.json").read_text())
D = PO.derive(d)
print(f"=== {d.name}: live {L['format']} {len(L['steps'])} steps {len(L['polities'])} polities | read-out {len(D['steps'])} steps "
      f"{len(D['polities'])} polities, live key {'live' in D}")
pad = len(D["steps"]) - len(L["steps"])
assert all(m == [] for m in D["maps"][:pad])
bad = 0
for k, (lm, dm) in enumerate(zip(L["maps"], D["maps"][pad:])):
    a = [(e[0], e[1], e[2]) for e in lm]
    b = [(e[0], e[1], e[2]) for e in dm]
    bad += a != b
print(f"map steps differing (polity, tier, cells): {bad} of {len(L['maps'])}; first live step {L['steps'][0]['ago'] if L['steps'] else None} kyr ago")
assert [r["key"] for r in L["polities"]] == [r["key"] for r in D["polities"]]
# the viewer's API, in process (what /api/polities returns)
SV.S.find_run = lambda run, d=d: d
summ, code = SV.polities(f"run={d.name}")
view, code2 = SV.polities(f"run={d.name}&ago=0")
print(f"/api/polities: {code}, {len(summ['polities'])} cards; ago=0: {code2}, {len(view['polities'])} polities")
lnow = {e[0]: e for e in L["maps"][-1]} if L["maps"] else {}
for p in sorted(view["polities"], key=lambda p: -len(p["cells"]))[:5]:
    rec = summ["polities"][p["id"]]
    lr = L["polities"][p["id"]]
    same = sorted(p["cells"]) == PO._unpack(lnow[p["id"]][2]).tolist()
    took = [(t[0], summ["polities"][t[1]]["name"], t[3]) for t in rec["took"]][-2:]
    print(f"  #{p['id']} {rec['name']} [{p['tier']}] {len(p['cells'])} cells, same cells as live: {same}; live key {lr['key']} people "
          f"{lnow[p['id']][3]}; rulers {rec['rulers'][-1:]} subjects {len(p['subjects'])}; fell {rec['fell_why']}; took {took}")
tk = [(r["id"], t) for r in D["polities"] for t in r["took"]]
print(f"conquests on the cards: {len(tk)} (live: {sum(len(r['took']) for r in L['polities'])}); fates named: {sum(bool(t[3]) for _, t in tk)}")
fh = {}
for r in D["polities"]:
    fh[r["fell_how"]] = fh.get(r["fell_how"], 0) + 1
print("fell how:", fh)
if "--gods" in sys.argv:
    from planet.lineages import gods as GD
    inp = GD.inputs(d, None)
    rt = GD.rule_table(D, inp["C"], inp["frames"])
    C = inp["C"]
    ids = {e[0] for e in L["maps"][-1]}
    print(f"gods rule_table: {len(rt['steps'])} steps; now {len(rt['now'])} realms, all live polities: {all(x['id'] in ids for x in rt['now'])}")
    for x in rt["now"][:5]:
        print(f"  realm #{x['id']} {x['name']} ruler culture {C[x['ruler']]['name']} ({C[x['ruler']]['people']}); live seat people "
              f"{[e[3] for e in L['maps'][-1] if e[0] == x['id']][0]}")
