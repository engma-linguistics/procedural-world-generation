"""Round 5 (PW-1512, lane 215): option C measured without building it. Runs lane 207's round3/lag.py with arm S's take-up gate
read as "settled, or rules land as a chiefdom or higher in polities.derive within living memory" (the seats of the stored tree's
polities; dragon realms left out). Inventing still needs a town (D62 A). Read-only.
argv: run_id n_draws out.json jobs.  Env: PLANET_DATA = the data root holding runs/."""
import json, os, runpy, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
from planet.lineages import polities as PO, techtree as TT  # noqa: E402

RID = sys.argv[1]
doc = PO.derive(Path(os.environ["PLANET_DATA"]) / "runs" / RID)
RULE: dict = {}  # people -> agos it rules land as a chiefdom or higher
for st, smap in zip(doc["steps"], doc["maps"]):
    for e in smap:
        if e[1] < PO.TIERS.index("dragon realm"):
            rec = doc["polities"][e[0]]
            RULE.setdefault(PO._at([[x[0], x[1]] for x in rec["peoples"]], st["ago"])[1], []).append(st["ago"])
print("rulers", len(RULE), flush=True)


def rules(self, lid, ago):
    w = TT.MEMORY_GENERATIONS * (self.gens.get(lid) or TT.GENERATION_REF_YR) / 1000.0
    return any(ago - 1e-9 <= a <= ago + max(w, 0.1) + 1e-9 for a in RULE.get(lid, ()))


def may_take(self, lid, ago):
    return self.settled(lid, ago) or rules(self, lid, ago)


_can = TT.Calendar.can


def can(self, lid, tid, ago, inventing, needs=True, gate=True):
    if gate and not inventing and tid in self.state and not self.settled(lid, ago) and may_take(self, lid, ago):
        return _can(self, lid, tid, ago, inventing, needs, gate=False)
    return _can(self, lid, tid, ago, inventing, needs, gate)


_keeps, _gated = TT.Calendar.keeps, TT.Calendar.gated


def keeps(self, lid, tid, at):
    if tid in self.state and not self.settled(lid, at) and rules(self, lid, at):
        t = self.techs[tid]
        return self.held(lid, tid, at) and (not t.get("sea") or self.sea[lid] or bool(t.get("traded")))
    return _keeps(self, lid, tid, at)


def gated(self, lid, tid, ago):
    return False if rules(self, lid, ago) else _gated(self, lid, tid, ago)


TT.Calendar.can, TT.Calendar.keeps, TT.Calendar.gated = can, keeps, gated
import multiprocessing  # noqa: E402
multiprocessing.set_start_method("fork")  # (the workers inherit the patched Calendar and RULE)
sys.argv = [str(Path(__file__).resolve().parents[1] / "round3" / "lag.py")] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
