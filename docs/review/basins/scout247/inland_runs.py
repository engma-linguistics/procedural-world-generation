"""Inland drainage share per stored run (read-only): median over frames after 50 Myr, and last."""
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
    v = np.array([f["inland_pct"] for f in fr]); raw = np.array([f["inland_raw_pct"] for f in fr])
    dry = np.array([f["dry_pct"] for f in fr]); lake = np.array([f["lake_pct"] for f in fr])
    print(f"{rid} L{r['level']} s{r['seed']} {r['myr']:.0f}Myr n={len(fr)} inland med {np.median(v):.2f} "
          f"p10 {np.percentile(v,10):.2f} p90 {np.percentile(v,90):.2f} last {v[-1]:.2f} raw med {np.median(raw):.2f} "
          f"| dry {np.median(dry):.1f} lakes {np.median(lake):.2f} land {np.median([f['land_pct'] for f in fr]):.1f} "
          f"T {np.median([f['temp'] for f in fr]):.1f} maxlake {np.median([f['lake_max_mkm2'] for f in fr]):.3f} "
          f"| {r['checks']}", flush=True)
