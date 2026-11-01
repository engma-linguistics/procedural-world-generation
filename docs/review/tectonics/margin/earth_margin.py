"""usage: earth_margin.py LEVEL -> margindiag's ocean-depth numbers for Earth (data/earth/L<LEVEL>.npz 'elev', read-only):
shelf / 200-3000 m / 4000-5000 m shares of the ocean, coast-to-3000 m median (km), coast cells with >3000 m within
1 / 2 hops. Sea = elev <= 0 (inland pits included, as in the run's numbers). Harness only."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet.geo import R_KM  # noqa: E402
from planet.grid import shared_grid  # noqa: E402

lvl = int(sys.argv[1])
e = np.load(f"/data/personal/repos/procedural-world-generation/data/earth/L{lvl}.npz")["elev"].astype(float)
g = shared_grid(lvl)
off, idx = g.nbr_off, g.nbr_idx
src_of = np.repeat(np.arange(g.n), np.diff(off))
sea = e <= 0
se = e[sea]
d = np.full(g.n, -1)
d[e < -3000] = 0
front = np.flatnonzero(d == 0)
for k in range(1, 41):
    m = np.zeros(g.n, bool)
    m[front] = True
    nb = np.unique(idx[m[src_of]])
    nb = nb[d[nb] < 0]
    d[nb] = k
    front = nb
coast = ~sea & np.logical_or.reduceat(sea[idx], off[:-1])
dc = np.where(d[coast] < 0, 41, d[coast])
km = g.spacing * R_KM
print(f"Earth L{lvl} (cell {km:.0f} km): land {100 * (~sea).mean():.1f}%  shelf {100 * (se > -200).mean():.2f}%  "
      f"200-3000 {100 * ((se <= -200) & (se > -3000)).mean():.2f}%  4000-5000 {100 * ((se <= -4000) & (se > -5000)).mean():.2f}%  "
      f"coast->3000 {np.median(dc) * km:.0f} km  near1 {100 * (dc <= 1).mean():.1f}%  near2 {100 * (dc <= 2).mean():.1f}%")
