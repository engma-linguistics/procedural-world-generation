"""Round 27 (lane 281d, PW-1687): round19/live_run.py with the live dragon cultures logged: per step, per dragon people, its cultures
(DragonCultures.step) and how many of them seat a realm. Diagnosis only. env L281D_DC: the log file (JSON lines). argv: as live_run."""
import json
import os
import runpy
import sys
from pathlib import Path

from planet.lineages.history import polity_live as PL

_dc = PL.LivePolities._dragon_cultures
_step = PL.LivePolities._step


def _dc_log(self, step):
    _dc(self, step)
    if float(step.ago) <= 12.0 and step.epoch == "recent":
        with open(os.environ["L281D_DC"], "a") as f:
            f.write(json.dumps({"ago": round(float(step.ago), 3), "cultures": {self.h.lines[k].id: len(v) for k, v in self.dregions.items()},
                                "pieces": {self.h.lines[k].id: sum(1 for x in self.dcul.info.get(k, []) if x[0] is None and x[4] is None and x[3] >= 0)
                                           for k in self.dregions}}) + "\n")


PL.LivePolities._dragon_cultures = _dc_log
sys.argv = [str(Path(__file__).parent.parent / "round19" / "live_run.py")] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
