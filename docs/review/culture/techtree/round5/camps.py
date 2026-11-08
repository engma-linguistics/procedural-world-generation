"""Round 5 (PW-1512, lane 215): for the peoples arm S reads as not settled at 0.5 kyr ago (round5/seats.py's JSON), what places do
they hold in the settlement ledger then: how many of any size, their people, and the most people of their own in one cell (a
chiefdom's reach at L7, polities.CHIEF_KM) against the ledger's town size. Read-only. argv: run_id seats.json.
Env: PLANET_DATA = the data root holding runs/."""
import json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))
import numpy as np  # noqa: E402

from planet.lineages.techspread import _holders, _ledger  # noqa: E402

RID, SEATS = sys.argv[1], sys.argv[2]
meta, S, A, sites, pop, town_min = _ledger(Path(os.environ["PLANET_DATA"]) / "runs" / RID)
k = int(np.argmin(np.abs(A - 0.5)))
d = json.loads(Path(SEATS).read_text())
want = {r["p"]: r for r in d["people"] if not r["settled_05"]}
got: dict = {p: {"places": 0, "people": 0.0, "cells": {}} for p in want}
for i, s in enumerate(sites):
    if pop[i, k] <= 0:
        continue
    h = _holders(s, A)[k]
    if h in got:
        g = got[h]
        g["places"] += 1
        g["people"] += float(pop[i, k])
        g["cells"][s["cell"]] = g["cells"].get(s["cell"], 0.0) + float(pop[i, k])
tm = town_min(sites[0] if sites else {}, float(A[k]))
for p, g in got.items():
    best = max(g["cells"].values(), default=0.0)
    print(f"{RID} {p:22s} way={str(want[p]['way']):17s} writes={'y' if want[p]['writing'] else 'n'} places={g['places']:4d} "
          f"people={g['people']:8.0f} best_cell={best:7.0f} town_min={tm:.0f} chief_of_own={'Y' if best >= tm else '-'}")
