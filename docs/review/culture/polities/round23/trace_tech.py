"""Lane 278 (PW-1597, round23.md): one (people, tech)'s invention in the after-run tree rebuilt on a run, with the run's ledger
footprint and with the footprint the live tree read: at each tree step from `from_kyr`, whether it may invent (can), whether the
people is settled (arm S), its town cells read, the ready date and the hazard summed. Read-only.
argv: run_dir live_dump.json people tech from_kyr to_kyr"""
import json
import sys
from pathlib import Path

import numpy as np

from planet.lineages import techspread as TS
from planet.lineages import techtree as TT

d, dump, who, tid, a0, a1 = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4], float(sys.argv[5]), float(sys.argv[6])
fp = json.loads(dump.read_text())
fp = {k: (v if k == "_cell_km2" else (np.array(v[0]), np.array(v[1]))) for k, v in fp.items()}
led = TS.town_footprint(d)
fp["_cell_km2"] = led["_cell_km2"]
_adv = TT.Calendar.advance
rows = {}


def advance(self, to=None):
    tag = self._tag  # (run step by step, logging after each)
    if self.grid is None:
        _adv(self, 1e9)  # (fixes the grid without running a step past the oldest)
    while self.step < len(self.grid):
        ago = float(self.grid[self.step])
        _adv(self, ago)
        if a0 >= ago >= a1:
            tw = self.towns.get(who)
            rows.setdefault(round(ago, 3), {})[tag] = (self.can(who, tid, ago, True), self.settled(who, ago),
                                                       round(TT.town_cells_at(tw, ago), 1), round(self.ready[who].get(tid, -1), 3),
                                                       round(self.hz[who].get(tid, 0.0), 4), self.known[who].get(tid))
    return 0


TT.Calendar.advance = advance
for tag, f in (("ledger", led), ("live", fp)):
    TT.Calendar._tag = tag
    TS.town_footprint = lambda run_dir, f=f: f
    TT.rebuild(d)
print(f"{who} {tid}: (can invent, settled, town cells, ready, hazard summed, known)")
for ago in sorted(rows, reverse=True):
    r = rows[ago]
    print(f"{ago:8.3f}  ledger {r.get('ledger')}\n          live   {r.get('live')}")
