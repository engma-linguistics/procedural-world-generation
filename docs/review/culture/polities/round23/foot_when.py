"""Lane 278 (PW-1597, round23.md): one people's town cells, the footprint the live tree read (round19/live_run.py's dump) against
the same run's settlement ledger (techspread.town_footprint), at every century step between two times; and the total over all
peoples. Read-only. argv: live_dump.json run_dir people from_kyr to_kyr"""
import json
import sys
from pathlib import Path

import numpy as np

from planet.lineages.techtree import town_cells_at
from planet.lineages.techspread import town_footprint

live = json.loads(Path(sys.argv[1]).read_text())
led = town_footprint(Path(sys.argv[2]))
who, a0, a1 = sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
ppl = [k for k in set(live) | set(led) if k != "_cell_km2"]
print(f"{'kyr ago':>8} {who + ' live':>14} {'ledger':>8} {'all live':>9} {'ledger':>8}")
for ago in np.round(np.arange(a0, a1 - 1e-9, -0.1), 3):
    lv, ld = town_cells_at(live.get(who), ago), town_cells_at(led.get(who), ago)
    tl = sum(town_cells_at(live.get(p), ago) for p in ppl)
    td = sum(town_cells_at(led.get(p), ago) for p in ppl)
    print(f"{ago:8.1f} {lv:14.0f} {ld:8.0f} {tl:9.0f} {td:8.0f}")
