"""Round 25 (lane 281b): round19/live_run.py with the live seat test written out (diagnosis only; the run itself is unchanged).
argv: as live_run.py; env L281_DUMP: the JSON file to write. For every step 3 kyr ago or later, every seat the live polities kept
(prev_cap after the step): its cell, tier, the seat's place (_seat_places), its holder line, and the seat's hemmed share when the
state test read it (_hem_local)."""
import json
import os
import runpy
import sys
from pathlib import Path

from planet.lineages.history import polity_live as PL

out: list = []
_sp, _hem, _step = PL.LivePolities._seat_places, PL.LivePolities._hem_local, PL.LivePolities._step


def seat_places(self, ago, inc):
    r = _sp(self, ago, inc)
    self._dump_sp = r
    self._dump_hem = {}
    return r


def hem_local(self, c, *a, **k):
    v = _hem(self, c, *a, **k)
    self._dump_hem[int(c)] = float(v)
    return v


def step(self, st):
    _step(self, st)
    ago = float(st.ago)
    if ago > 3.0 + 1e-9 or not hasattr(self, "_dump_sp"):
        return
    pop, who = self._dump_sp
    rows = []
    for key, tier in self.prev_cap.items():
        if not key.startswith("c"):
            continue
        c = int(key[1:])
        rows.append([c, tier, round(float(pop[c])), int(who[c]), self._dump_hem.get(c)])
    out.append({"ago": round(ago, 3), "seats": rows, "lines": [l.id for l in self.h.lines] if not out else None})


PL.LivePolities._seat_places, PL.LivePolities._hem_local, PL.LivePolities._step = seat_places, hem_local, step
here = Path(__file__).resolve().parent
sys.argv = [str(here.parent / "round19" / "live_run.py")] + sys.argv[1:]
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
finally:
    with open(os.environ["L281_DUMP"], "w") as f:
        json.dump(out, f)
