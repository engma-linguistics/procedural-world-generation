"""usage: passrate.py DIAG_DIR [DIAG_DIR ...] -- ice_diag runs over 1 Gyr against the owner's v1 bar, judged on
300-1000 Myr (tools/ice_criteria.evaluate): icehouse share <= 40% (OWNER_BAR), no always-icebox (icehouse >= 90%,
or ice below -150 m on >= 30% of the climate updates), no hellhole (median dT > 10.5, i.e. 25 C, or any > 15.5,
30 C). Per seed, then per directory and pooled: the pass rate, the icehouse share's median, the early (300-500)
and late (600-1000) shares, and N1-N4."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from tools import ice_criteria as C  # noqa: E402

OWNER_BAR = 40.0
pooled = []
for d in sys.argv[1:]:
    rows = []
    for p in sorted(Path(d).glob("seed*_L6.json.gz"), key=lambda p: int(p.name.split("_")[0][4:])):
        raw = C.load(p)
        r = C.evaluate(raw)
        s = C.series(raw)
        t, si, dT = s["t"], s["sea_ice"], s["dT"]
        late = t >= 300
        share = r["icehouse"]["share_pct"]
        deep = 100 * float((si[late] < -150).mean())
        hell = float(np.median(dT[late])) > 10.5 or float(dT[late].max()) > 15.5
        icebox = share >= 90 or deep >= 30
        ok = share <= OWNER_BAR and not hell and not icebox
        e = 100 * float((si[(t >= 300) & (t < 500)] <= C.ICEHOUSE_SL).mean())
        lt = 100 * float((si[t >= 600] <= C.ICEHOUSE_SL).mean())
        rows.append(dict(seed=p.name.split("_")[0][4:], share=share, early=e, late=lt, deep=deep, hell=hell,
                         icebox=icebox, ok=ok, n=r["pass"], tmax=float(dT[late].max())))
    for x in rows:
        print(f"{Path(d).name:>8} seed {x['seed']:>5}: icehouse {x['share']:5.1f}% (300-500 {x['early']:3.0f}%, "
              f"600-1000 {x['late']:3.0f}%), deep {x['deep']:4.1f}%, dT max {x['tmax']:+.1f}"
              f"{' HELL' if x['hell'] else ''}{' ICEBOX' if x['icebox'] else ''} -> {'ok' if x['ok'] else 'F'}"
              f" | N1-N4 {'ok' if x['n'] else 'F'}")
    pooled += rows
    k = sum(x["ok"] for x in rows)
    print(f"{Path(d).name}: owner's bar {k}/{len(rows)} ({100 * k / max(len(rows), 1):.0f}%), icehouse median "
          f"{np.median([x['share'] for x in rows]):.0f}% (early {np.median([x['early'] for x in rows]):.0f}, late "
          f"{np.median([x['late'] for x in rows]):.0f}), always-icebox {sum(x['icebox'] for x in rows)}, hellhole "
          f"{sum(x['hell'] for x in rows)}, N1-N4 {sum(x['n'] for x in rows)}/{len(rows)}\n")
if len(sys.argv) > 2:
    k = sum(x["ok"] for x in pooled)
    print(f"pooled: owner's bar {k}/{len(pooled)} ({100 * k / len(pooled):.0f}%), icehouse median "
          f"{np.median([x['share'] for x in pooled]):.0f}%, always-icebox {sum(x['icebox'] for x in pooled)}, "
          f"hellhole {sum(x['hell'] for x in pooled)}, N1-N4 {sum(x['n'] for x in pooled)}/{len(pooled)}")
