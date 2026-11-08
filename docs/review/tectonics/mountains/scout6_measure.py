"""PW-1497 scout 209: per run, over frames with t >= 100 Myr (about 30 frames), scout1's Andes measure (share of land
above 3 km within 2 L6 / 4 L7 cells of the continental side of a converging ocean-continent plate edge, pooled over
frames) and hypsometry (median over frames of the share of land above 2/3/4 km, top cell). Read-only.
usage: scout6_measure.py RUN_DIR [RUN_DIR ...]"""
import sys
from pathlib import Path

import numpy as np

from planet import timeline as T
from planet.grid import shared_grid


def dilate(g, m, k):
    for _ in range(k):
        m = m | (np.maximum.reduceat(m[g.nbr_idx].astype(np.int8), g.nbr_off[:-1]) > 0)
    return m


def measure(rd):
    r, arr = T.load_frames(Path(rd), ["elevation", "plate", "crust", "plate_boundary"])
    lv = r["meta"]["level"]
    g = shared_grid(lv)
    ea, eb = g.edges[:, 0], g.edges[:, 1]
    k = 4 if lv == 7 else 2
    near_hi = all_hi = 0
    rows = []
    nf = len(r["frames"])
    for i in range(0, nf, max(1, nf // 30)):
        if r["frames"][i]["t"] < 100:
            continue
        e = T.frame(r, arr, "elevation", i).astype(float)
        pl, cr, pb = T.frame(r, arr, "plate", i), T.frame(r, arr, "crust", i) > 0, T.frame(r, arr, "plate_boundary", i)
        oc = (pl[ea] != pl[eb]) & (cr[ea] != cr[eb]) & ((pb[ea] > 0) | (pb[eb] > 0))
        m = np.zeros(g.n, bool)
        m[np.where(cr[ea[oc]], ea[oc], eb[oc])] = True  # the continental side of the trench
        land = e > 0
        zone = dilate(g, m, k) & cr & land
        hi = e > 3000
        near_hi += (hi & zone).sum()
        all_hi += hi.sum()
        le = e[land]
        n = max(len(le), 1)
        rows.append([100 * (le > 2000).sum() / n, 100 * (le > 3000).sum() / n, 100 * (le > 4000).sum() / n, e.max(),
                     100 * (hi & zone).sum() / n])
    med = np.median(np.array(rows), axis=0)
    return dict(name=r["name"], seed=r["meta"]["seed"], andes=100 * near_hi / max(all_hi, 1), gt2=med[0], gt3=med[1],
                gt4=med[2], top=med[3], near3=med[4], nfr=len(rows))


if __name__ == "__main__":
    print("run     name           seed | andes% of >3km | >2km  >3km  >4km (% land, median frames) | margin>3km % land | top m")
    for rd in sys.argv[1:]:
        x = measure(rd)
        print(f"{Path(rd).name} {x['name']:14s} {x['seed']:5d} | {x['andes']:5.1f} | {x['gt2']:5.2f} {x['gt3']:5.2f} {x['gt4']:5.2f}"
              f" | {x['near3']:5.2f} | {x['top']:5.0f}  ({x['nfr']} frames)")
