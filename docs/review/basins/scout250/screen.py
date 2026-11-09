"""PW-054 scout 250: per run, frames after 50 Myr (health's measures): inland median (p10-p90), lakes % of
land (mean), largest lake median Mkm2, giant-lake frames (largest > 1 Mkm2) %. Read-only.
Usage: screen.py DATA_ROOT RUN_ID..."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import planet  # noqa
import numpy as np
from tools import health as Hh

root = Path(sys.argv[1])
for rid in sys.argv[2:]:
    r = Hh.measure_run(root / "runs" / rid)
    fr = [f for f in r["frames"] if f["t"] >= 50 and f["inland_pct"] is not None]
    v = np.array([f["inland_pct"] for f in fr])
    mx = np.array([f["lake_max_mkm2"] for f in fr])
    print(f"{rid} L{r['level']} s{r['seed']} {r['myr']:.0f} Myr n={len(fr)}: inland {np.median(v):.1f} "
          f"({np.percentile(v, 10):.1f}-{np.percentile(v, 90):.1f}) | lakes {np.mean([f['lake_pct'] for f in fr]):.2f}% "
          f"| largest lake med {np.median(mx):.2f} Mkm2 | giant frames {100*(mx > 1).mean():.1f}% "
          f"| dry {np.median([f['dry_pct'] for f in fr]):.1f} land {np.median([f['land_pct'] for f in fr]):.1f} "
          f"| {r['checks']}", flush=True)
