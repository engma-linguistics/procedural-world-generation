"""PW-846 scout 171. (1) Where Earth's >3 km regions are (L7). (2) In runs: share of >3 km land that lies near an ocean-continent
trench (within 4 L7 cells / 2 L6 cells ~ 250 km of a converging continent-ocean plate edge), and the 95th
percentile height of such margin land. Read-only."""
import sys
from pathlib import Path

import numpy as np

from planet import timeline as T
from planet.grid import shared_grid

MAIN = Path("/home/daniel/personal/repos/procedural-world-generation")


def dilate(g, m, k):
    for _ in range(k):
        m = m | (np.maximum.reduceat(m[g.nbr_idx].astype(np.int8), g.nbr_off[:-1]) > 0)
    return m


if sys.argv[1] == "earth":
    d = np.load(MAIN / "data/earth/L7.npz")
    g = shared_grid(7)
    e = np.where((d["surface"] > 0) & (d["ice"] < 10), d["elev"].astype(float), -1)
    lab, n = g.components(e > 3000)
    size = np.bincount(lab[lab >= 0])
    lat, lon = g.lat, g.lon
    for k in np.argsort(-size)[:4]:
        s = lab == k
        print(f"Earth >3km region {size[k] * 3600 / 1e3:.0f}k km2 centre lat {lat[s].mean():.0f} lon {lon[s].mean():.0f}")
    sys.exit()

for rd in sys.argv[1:]:
    r, arr = T.load_frames(Path(rd), ["elevation", "plate", "crust", "plate_boundary"])
    lv = r["meta"]["level"]
    g = shared_grid(lv)
    ea, eb = g.edges[:, 0], g.edges[:, 1]
    k = 4 if lv == 7 else 2
    near_hi, all_hi, p95 = 0, 0, []
    nf = len(r["frames"])
    for i in range(0, nf, max(1, nf // 30)):
        if r["frames"][i]["t"] < 100:
            continue
        e = T.frame(r, arr, "elevation", i).astype(float)
        pl, cr, pb = T.frame(r, arr, "plate", i), T.frame(r, arr, "crust", i) > 0, T.frame(r, arr, "plate_boundary", i)
        oc = (pl[ea] != pl[eb]) & (cr[ea] != cr[eb]) & ((pb[ea] > 0) | (pb[eb] > 0))
        m = np.zeros(g.n, bool)
        m[np.where(cr[ea[oc]], ea[oc], eb[oc])] = True  # the continental side of the trench
        zone = dilate(g, m, k) & cr & (e > 0)
        hi = e > 3000
        near_hi += (hi & zone).sum()
        all_hi += hi.sum()
        if zone.any():
            p95.append(np.percentile(e[zone], 95))
    print(f"{Path(rd).name} L{lv}: >3km land near ocean-continent trenches {100 * near_hi / max(all_hi, 1):.0f}%;"
          f" margin land p95 height median {np.median(p95):.0f} m")
