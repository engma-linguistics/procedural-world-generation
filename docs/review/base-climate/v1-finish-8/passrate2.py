"""usage: passrate2.py DIAG_DIR [...] -- v1-finish-6's passrate.py bar (unchanged: icehouse share <= 40%, no
always-icebox, no hellhole; never-ice < 5% reported only) applied to runs of any length, judged on 300 Myr to the
run's end, plus the same quantities per window (300-1000, 1000-1500, 1500-2000 Myr) so a late hothouse shows.
Also the window means of the star term, the CO2 term and the ice-albedo term (ice_diag's steps). Harness only."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from tools import ice_criteria as C  # noqa: E402

OWNER_BAR = 40.0
WINDOWS = [(300, 1000), (1000, 1500), (1500, 2000.1)]


def judge(t, si, dT, a, b):
    w = (t >= a) & (t < b)
    if not w.any():
        return None
    share = 100 * float((si[w] <= C.ICEHOUSE_SL).mean())
    deep = 100 * float((si[w] < -150).mean())
    med, mx = float(np.median(dT[w])), float(dT[w].max())
    hell = med > 10.5 or mx > 15.5
    icebox = share >= 90 or deep >= 30
    return dict(share=share, deep=deep, med=med, mx=mx, hell=hell, icebox=icebox, never=share < 5,
                ok=share <= OWNER_BAR and not hell and not icebox)


def flags(j):
    return (" HELL" if j["hell"] else "") + (" ICEBOX" if j["icebox"] else "") + (" NEVER-ICE" if j["never"] else "")


for d in sys.argv[1:]:
    for p in sorted(Path(d).glob("seed*_L*.json.gz")):
        raw = C.load(p)
        s = C.series(raw)
        t, si, dT = s["t"], s["sea_ice"], s["dT"]
        steps = [r for r in raw["steps"] if r["t"] > 0]
        st = np.array([r["t"] for r in steps])
        terms = {k: np.array([r.get(k, 0.0) for r in steps], dtype=float) for k in ("star", "co2_term", "albedo_term")}
        allj = judge(t, si, dT, 300, 1e9)
        print(f"{Path(d).name:>12} {p.name.split('_')[0]:>10} 300-{t.max():.0f}: icehouse {allj['share']:4.1f}% deep "
              f"{allj['deep']:4.1f}% dT med {allj['med']:+.1f} max {allj['mx']:+.1f}{flags(allj)} -> "
              f"{'ok' if allj['ok'] else 'F'}")
        for a, b in WINDOWS:
            j = judge(t, si, dT, a, b)
            if j is None:
                continue
            w = (st >= a) & (st < b)
            tm = " ".join(f"{k} {terms[k][w].mean():+.1f}" for k in terms)
            print(f"{'':>24}{a:>4}-{min(b, 2000):.0f}: icehouse {j['share']:4.1f}% deep {j['deep']:4.1f}% dT med "
                  f"{j['med']:+.1f} max {j['mx']:+.1f}{flags(j)} -> {'ok' if j['ok'] else 'F'} | {tm}")
