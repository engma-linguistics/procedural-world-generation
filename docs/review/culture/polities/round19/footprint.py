"""Lane 254 (PW-1597): the town footprint the live tech tree read (live_run.py's dump) against the settlement ledger's
(techspread.town_footprint) of a run, people by people, at a few times. Read-only.
argv: live_dump.json run_dir [run_dir ...]  (each run's ledger footprint is a column)."""
import json
import sys
from pathlib import Path

from planet.lineages.techtree import town_cells_at
from planet.lineages.techspread import town_footprint

AGOS = (8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0)
live = json.loads(Path(sys.argv[1]).read_text())
leds = [town_footprint(Path(d)) for d in sys.argv[2:]]
peoples = sorted({k for f in [live, *leds] for k in f if k != "_cell_km2"},
                 key=lambda p: -max(town_cells_at(f.get(p), 3.0) for f in [live, *leds]))
print("town cells: live / " + " / ".join(Path(d).name for d in sys.argv[2:]))
print(f"{'people':24s}" + "".join(f"{a:>16.0f}" for a in AGOS))
for p in ["ALL"] + peoples[:15]:
    row = []
    for a in AGOS:
        vals = []
        for f in [live, *leds]:
            vals.append(sum(town_cells_at(f.get(q), a) for q in f if q != "_cell_km2") if p == "ALL" else town_cells_at(f.get(p), a))
        row.append("/".join(f"{v:.0f}" for v in vals))
    print(f"{p[:24]:24s}" + "".join(f"{r:>16s}" for r in row))
first = lambda f, p: next((a for a, c in zip(*f[p]) if c >= 1), None) if p in f else None
print("first town cell (kyr ago): " + ", ".join(f"{p}: {first(live, p)} / " + " / ".join(str(first(l, p)) for l in leds) for p in peoples[:12]))
