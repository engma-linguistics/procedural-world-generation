"""Lane 278 (PW-1597, round23.md): a switch-off run's after-run read-outs made again on the code this runs on, in place: the tech
tree without the town arms, then the settlement ledger and the tree with its footprint, round by round as output._towns_first does
(at most TOWN_PASSES). A switch-off history does not read the tree or the ledger, so this is the run as that code would have made
it, without re-running the history. Keeps run.json and settlements.json as *.l278bak the first time. WRITES into the run dir: use
it only on scratch runs. argv: run_dir [run_dir ...]"""
import json
import shutil
import statistics as st
import sys
from pathlib import Path

from planet import store as S
from planet.lineages import output as OUT
from planet.lineages import settlements as ST
from planet.lineages import techtree as TT

for d in map(Path, sys.argv[1:]):
    for f in ("run.json", "settlements.json"):
        if not (d / f"{f}.l278bak").exists():
            shutil.copy2(d / f, d / f"{f}.l278bak")
    m = json.loads((d / "run.json").read_text())["meta"]
    assert not (d / "polities_live.json").exists(), "a switch-on run: its history read the live tree"
    prev = TT.rebuild(d, arms=TT.arms_without_towns())
    S.update_meta(d, lambda r, tt=prev: r["meta"].__setitem__("techtree", tt))
    for i in range(OUT.TOWN_PASSES):
        ST.write(d, report=False)
        tt = TT.rebuild(d)
        S.update_meta(d, lambda r, tt=tt: r["meta"].__setitem__("techtree", tt))
        if ST.ledger_dates(tt["known"]) == ST.ledger_dates(prev["known"]):
            break
        prev = tt
    pops = {l["id"]: (l.get("track") or [[0, 0, 0, 0, 0]])[-1][4] for l in m["lineages"]}
    top = sorted([p for p in tt["known"] if p in pops], key=lambda p: -pops[p])[:12]
    w = [x for x in ((tt["known"].get(p) or {}).get("writing", [None])[0] for p in top) if x is not None]
    print(f"{d.name}: {i + 1} round(s); writing median of the 12 largest {st.median(w) * 1000:,.0f} ya ({len(w)}/12)", flush=True)
