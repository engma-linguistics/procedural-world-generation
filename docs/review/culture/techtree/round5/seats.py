"""Round 5 (PW-1512, lane 215): are polities.derive's chiefdoms a reading beyond the town footprint? Read-only on a stored run.
For each people with hands alive today: settled at 0.5 kyr ago (arm S's own reading, Calendar.settled over the ledger's town
footprint), and whether it rules land as a chiefdom or higher in polities.derive (stored tree) within its living memory of 0.5 kyr
ago, and at any step. argv: run_id [out.json].  Env: PLANET_DATA = the data root holding runs/ (the main checkout)."""
import json, os, sys, warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from planet.lineages import polities as PO, techtree as TT  # noqa: E402
from planet.lineages.techspread import town_footprint  # noqa: E402

RID = sys.argv[1]
R = Path(os.environ["PLANET_DATA"]) / "runs" / RID
m = json.loads((R / "run.json").read_text())["meta"]
known = (m.get("techtree") or {}).get("known") or {}
lines = TT.with_generations(m["lineages"], m.get("tree"))
towns = town_footprint(R)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    c = TT.Calendar(lines, m.get("mode", "fantasy"), m.get("era"), 0, None, m.get("gods_mode", "faith_made"), towns, "S")
L = {l["id"]: l for l in lines}
hand = [p for p, v in known.items() if len(v) > 30 and p in c.kind and L[p].get("ended_kyr") is None]
doc = PO.derive(R)
rule: dict = {}  # people -> {ago: best tier index} of the polities whose capital it holds (dragon realms left out)
for st, smap in zip(doc["steps"], doc["maps"]):
    a = st["ago"]
    for e in smap:
        if e[1] >= PO.TIERS.index("dragon realm"):
            continue
        rec = doc["polities"][e[0]]
        ppl = PO._at([[x[0], x[1]] for x in rec["peoples"]], a)[1]
        rule.setdefault(ppl, {})[a] = max(rule.get(ppl, {}).get(a, -1), e[1])
AT = 0.5
rows = []
for p in hand:
    tw = towns.get(p)
    mem = c.memory(p, tw) if tw is not None else TT.MEMORY_GENERATIONS * (c.gens.get(p) or TT.GENERATION_REF_YR) / 1000.0
    r = rule.get(p, {})
    rows.append({"p": p, "way": L[p].get("way"), "settled_05": bool(c.settled(p, AT)),
                 "rules_05": any(AT - 1e-9 <= a <= AT + mem + 1e-9 for a in r), "rules_ever": bool(r), "rule_steps": len(r),
                 "rule_no_town_steps": sum(1 for a in r if not c.settled(p, a)),  # (steps it rules land that arm S reads as unsettled)
                 "writing": (known[p].get("writing") or [None])[0]})
ns = [r for r in rows if not r["settled_05"]]
out = {"run": RID, "n_hand": len(rows), "settled_05": len(rows) - len(ns), "not_settled_05": len(ns),
       "rules_05": sum(r["rules_05"] for r in rows), "rules_05_not_settled": sum(r["rules_05"] for r in ns),
       "rules_ever": sum(r["rules_ever"] for r in rows), "rule_steps": sum(r["rule_steps"] for r in rows),
       "rule_steps_no_town": sum(r["rule_no_town_steps"] for r in rows),
       "not_settled_ways": sorted({str(r["way"]) for r in ns}), "derive_s": doc["made_s"], "people": rows}
print(json.dumps({k: v for k, v in out.items() if k != "people"}))
Path(sys.argv[2] if len(sys.argv) > 2 else f"seats_{RID}.json").write_text(json.dumps(out))
