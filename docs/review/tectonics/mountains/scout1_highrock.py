"""Basement rock under high ground (> 3 km cell mean), pooled over frames t >= 100 Myr (read-only)."""
import sys
from pathlib import Path

import numpy as np

from planet import timeline as T

KEYS = ["ocean", "hotspot", "arc", "sediment", "orogen", "craton", "lime", "sand", "shale", "evap", "coal", "granite",
        "quartzite", "fbasalt", "dolomite", "tuff"]
for rd in sys.argv[1:]:
    r, arr = T.load_frames(Path(rd), ["elevation", "rock", "crust_thickness"])
    nf = len(r["frames"])
    cnt3, cnt4, allland = np.zeros(16), np.zeros(16), np.zeros(16)
    th_c, th_o = [], []
    for i in range(0, nf, max(1, nf // 40)):
        if r["frames"][i]["t"] < 100:
            continue
        e = T.frame(r, arr, "elevation", i)
        rk = T.frame(r, arr, "rock", i).astype(int)
        th = T.frame(r, arr, "crust_thickness", i)
        cnt3 += np.bincount(rk[e > 3000], minlength=16)[:16]
        cnt4 += np.bincount(rk[e > 4000], minlength=16)[:16]
        allland += np.bincount(rk[e > 0], minlength=16)[:16]
    def top(c):
        s = c.sum()
        return ", ".join(f"{KEYS[k]} {100 * c[k] / s:.0f}%" for k in np.argsort(-c)[:4] if c[k] > 0) if s else "-"
    print(f"{Path(rd).name} ({r['name']}): land: {top(allland)} | >3km: {top(cnt3)} | >4km: {top(cnt4)}")
