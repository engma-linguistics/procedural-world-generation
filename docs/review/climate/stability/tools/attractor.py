"""Lane 158: one planet, five histories (r0.001 l6c_p 957317: fm, the forked nulls fn and fn2, the pulse runs m3 and
m8). The window statistic the hard bar reads (peak land ice 884-1000) against attractor statistics (means and shares
over 600-1000 and 500-1000 Myr)."""
import numpy as np
from pulse_read import rec, J, S, draw, seed
arms = {"fm": f"{J}/m_{draw}", "fn": f"{J}/n_{draw}", "fn2": f"{J}/n2_{draw}", "pulse-3": f"{S}/l158/pulse/m3",
        "pulse-8": f"{S}/l158/pulse/m8"}
print(f"{'arm':>8} {'pk884':>6} {'mean dT 600-1000':>16} {'mean ice':>8} {'med ice':>7} {'%t ice>=40':>10} {'%t ice>=30':>10} "
      f"{'longest>=40 Myr':>15} {'mean dT 500-1000':>16}")
for k, p in arms.items():
    R = rec(f"{p}/seed{seed}_L6.json.gz")
    ts = sorted(t for t in R if 600 < t <= 1000)
    ice = np.array([R[t]["iced_land_pct"] for t in ts])
    run = best = 0
    for v in ice:
        run = run + 2 if v >= 40 else 0
        best = max(best, run)
    pk = max(R[t]["iced_land_pct"] for t in R if 884 <= t <= 1000)
    print(f"{k:>8} {pk:6.1f} {np.mean([R[t]['dT'] for t in ts]):+16.2f} {ice.mean():8.1f} {np.median(ice):7.1f} "
          f"{100 * (ice >= 40).mean():10.1f} {100 * (ice >= 30).mean():10.1f} {best:15d} "
          f"{np.mean([R[t]['dT'] for t in R if 500 < t <= 1000]):+16.2f}")
