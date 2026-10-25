"""The test_vegetation ideal climates, desert cover and rainforest stats, for the planet package at PWROOT."""
import os
import sys

sys.path.insert(0, os.environ["PWROOT"])
import numpy as np  # noqa: E402
from planet import vegetation as V  # noqa: E402
from planet.grid import build_grid  # noqa: E402

CLIMATES = {"rainforest": (26.5, 27.5, 25.5, 2600, 2600, 0.5), "savanna": (25, 28, 22, 1900, 100, 0.4),
            "desert": (24, 33, 13, 40, 40, 0.1), "temperate": (10, 19, 1, 800, 700, 0.6),
            "boreal": (-3, 16, -22, 700, 300, 0.6), "tundra": (-12, 6, -28, 400, 150, 0.6)}
g = build_grid(3)
names = list(CLIMATES)
k = np.arange(g.n) % len(names)
arr = np.array([CLIMATES[nm] for nm in names])[k]
elev = np.random.default_rng(1).uniform(100.0, 700.0, g.n)
v = V.model(g, elev, arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3], arr[:, 4], 23.4, arr[:, 5], arr[:, 5])
nu = v["eq"]["nu"]
for nm in names:
    m = k == names.index(nm)
    top = sorted(((float(nu[i, m].mean()), c) for i, c in enumerate(V.CODES)), reverse=True)[:4]
    print(f"{nm:10s} cover med {np.median(v['sm']['cover'][m]):.2f} max {v["sm"]["cover"][m].max():.4f} npp med "
          f"{np.median(v['sm']['npp'][m]):5.0f} tree {np.median(v['sm']['tree'][m]):.2f} tg {v['s']['tg'][m].mean() if 'tg' in v['s'] else 0:.1f} "
          + " ".join(f"{c} {x:.2f}" for x, c in top))
