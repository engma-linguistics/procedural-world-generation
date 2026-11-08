"""PW-1331 scout 210b: is the hot-desert rise a direct plant effect or the warmer late climate? Paired cand - main
regressions on late dT, and the late means of the weathering and forcing terms.
usage: scout2b_mech.py PAIRED_ROOT  (paired.sh layout, arms `main` and `cand`)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from tools import judge as J  # noqa: E402

a, b = J.arm(sys.argv[1], "main"), J.arm(sys.argv[1], "cand")
ks = sorted(set(a) & set(b))


def g(r, k):
    return J._mean(r["ups"], k)


dT = np.array([b[k]["m"]["late dT"] - a[k]["m"]["late dT"] for k in ks])
dc = np.array([b[k]["m"]["late CO2"] - a[k]["m"]["late CO2"] for k in ks])
print(f"{len(ks)} paired draws")
for key in ("bwh_pct", "arid_pct", "steppe_trees", "savanna_trees", "trees"):
    d = np.array([g(b[k], key) - g(a[k], key) for k in ks])
    s, i = np.polyfit(dT, d, 1)
    print(f"d{key} vs d late dT: r {np.corrcoef(dT, d)[0, 1]:+.2f}, slope {s:+.2f}/C, intercept (at dT 0) {i:+.2f}")
print(f"d late dT vs d late CO2: r {np.corrcoef(dc, dT)[0, 1]:+.2f}")
# (scout 217, PW-1516) the CO2 stock's steady state is sink x co2_law(X) = source: which side carries d late CO2?
# The source (ridges, arcs, plumes, drift) is tectonic; plants reach it only through the runs' chaotic divergence.
for key in ("source_raw", "sink_raw", "w_supply", "w_temp", "w_plant"):
    xa = np.array([J._mean(a[k]["late"], key) for k in ks])
    xb = np.array([J._mean(b[k]["late"], key) for k in ks])
    d = np.log(np.maximum(xb, 1e-12) / np.maximum(xa, 1e-12))
    ok = np.isfinite(d) & np.isfinite(dc)
    if ok.sum() > 3:
        print(f"d late CO2 vs d ln {key}: r {np.corrcoef(d[ok], dc[ok])[0, 1]:+.2f}")
for nm, arm in (("main", a), ("cand", b)):
    x = np.array([arm[k]["m"]["late dT"] for k in ks])
    y = np.array([g(arm[k], "bwh_pct") for k in ks])
    s, i = np.polyfit(x, y, 1)
    print(f"{nm}: BWh vs late dT across draws r {np.corrcoef(x, y)[0, 1]:+.2f}, slope {s:+.2f} pt/C")
print("--- late means (600-1000 Myr steps), paired cand - main: median [bootstrap 95% CI of the median], draws up")
for key in ("w_plant", "w_bare", "w_temp", "w_rate", "w_supply", "w_area", "w_q", "w_a", "w_T", "sink", "sink_raw",
            "source_raw", "albedo_term", "co2_term", "ch4_ppb"):
    xa = np.array([J._mean(a[k]["late"], key) for k in ks])
    xb = np.array([J._mean(b[k]["late"], key) for k in ks])
    d = xb - xa
    lo, hi = J.boot_ci(d)
    print(f"{key:12s} main {np.nanmedian(xa):10.4g} cand {np.nanmedian(xb):10.4g}  d {np.nanmedian(d):+.4g} "
          f"[{lo:+.4g}, {hi:+.4g}] up {(d > 0).sum()}/{len(d)}")
