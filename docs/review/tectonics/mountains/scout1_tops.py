"""The highest cells per frame: their crust thickness, rock and the Airy height that thickness alone gives. Read-only."""
import sys
from pathlib import Path

import numpy as np

from planet import timeline as T

for rd in sys.argv[1:]:
    r, arr = T.load_frames(Path(rd), ["elevation", "rock", "crust_thickness"])
    nf = len(r["frames"])
    gt7, n, ex = 0, 0, []
    for i in range(0, nf, max(1, nf // 60)):
        if r["frames"][i]["t"] < 100:
            continue
        e = T.frame(r, arr, "elevation", i).astype(float)
        th = T.frame(r, arr, "crust_thickness", i).astype(float)
        rk = T.frame(r, arr, "rock", i).astype(int)
        j = int(np.argmax(e))
        n += 1
        gt7 += e[j] > 7000
        airy = 250 + 150 * (th[j] - 35)
        ex.append((e[j], th[j], rk[j], e[j] - airy, r["frames"][i]["t"]))
    ex.sort(reverse=True)
    print(f"{Path(rd).name}: frames with a cell > 7 km: {gt7}/{n}; top 5 (elev, crust km, rock, elev - Airy(crust), t):",
          [(int(a), int(b), c, int(d), int(t)) for a, b, c, d, t in ex[:5]])
    print("   median over frames of (highest cell - its Airy height):", int(np.median([x[3] for x in ex])))
