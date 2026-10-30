"""usage: aridwin.py OUT_ROOT LEVEL ARM... -> Arid % and hot desert % of land: mean over the spin-up updates 600-990 Myr vs the finish window's (>= 990, native)."""
import gzip, json, sys
from pathlib import Path
import numpy as np
root, lv = Path(sys.argv[1]), sys.argv[2]
for arm in sys.argv[3:]:
    for p in sorted(root.glob(f"{arm}_r0.0005_*/seed*_L{lv}.json.gz")):
        r = json.load(gzip.open(p)); u = r["updates"]
        sp = [x for x in u if 600 <= x["t"] < 990]; fw = [x for x in u if x["t"] >= 990]
        m = lambda rows, k: np.mean([x[k] for x in rows if x.get(k) is not None])
        print(f"{arm:4s} {p.name.split('_')[0]:11s} spin-up arid {m(sp,'arid_pct'):5.1f} bwh {m(sp,'bwh_pct'):5.1f} rain {m(sp,'land_precip'):6.0f}"
              f" | window arid {m(fw,'arid_pct'):5.1f} bwh {m(fw,'bwh_pct'):5.1f} rain {m(fw,'land_precip'):6.0f}")
