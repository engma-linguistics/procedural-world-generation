"""Lane 265 (PW-1597 R, round22.md): logs what a tech tree reads for one people at each of its steps (learners: regions reached,
strengths; the population and range it reads), so the live tree and the after-run tree on the same history can be laid side by side.
Two uses:
  live:    trace.py live OUT.jsonl PEOPLE -- <round19/live_run.py args>   (a switch-on run with the live tree traced)
  rebuilt: trace.py rebuilt OUT.jsonl PEOPLE -- run_dir live_dump.json    (techtree.rebuild on that footprint, traced)
Read-only on stored runs (the live use writes its run to the data root, as live_run.py)."""
import json
import runpy
import sys
from pathlib import Path

import numpy as np

from planet.lineages import techtree as TT

mode, out, who = sys.argv[1], sys.argv[2], sys.argv[3]
rest = sys.argv[sys.argv.index("--") + 1:]
fh = open(out, "w")
_learners = TT.Calendar.learners


def learners(self, lid, ago):
    r = _learners(self, lid, ago)
    if lid == who:
        ser = self.series[lid]
        n, dens = TT._at(ser, ago) if ser is not None else (None, None)
        fh.write(json.dumps({"ago": round(float(ago), 4), "learners": [[round(a, 4), round(b, 4), round(c, 4)] for a, b, c in r],
                             "regions": self.regions_at(ago).get(lid), "reached": self.reached.get(lid), "pop": n, "dens": dens,
                             "known": len(self.known[lid]), "hz": {k: round(v, 5) for k, v in self.hz[lid].items()}}) + "\n")
    return r


TT.Calendar.learners = learners
if mode == "live":
    sys.argv = ["live_run.py"] + rest
    runpy.run_path(str(Path(__file__).parent.parent / "round19" / "live_run.py"), run_name="__main__")
else:
    from planet.lineages import techspread as TS
    d, dump = Path(rest[0]), Path(rest[1])
    fp = json.loads(dump.read_text())
    fp = {k: (v if k == "_cell_km2" else (np.array(v[0]), np.array(v[1]))) for k, v in fp.items()}
    fp["_cell_km2"] = TS.town_footprint(d)["_cell_km2"]
    TS.town_footprint = lambda run_dir: fp
    TT.rebuild(d)
fh.close()
