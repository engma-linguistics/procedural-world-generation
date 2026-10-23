"""usage (from a tree root, PYTHONPATH=.): lowtail.py [level] -- lane A23 (PW-646): Earth's plants at the run's low
CO2 tail, on today's climate (dT 0) and on a warm one (dT +3: a weathering surplus draws CO2 down in warm eras).

For each pCO2 (ppm, as the run now hands it, climate.pco2), the full plant model (vegetation.model) on Earth's
time-zoom source (timezoom.source_earth): global NPP, tree area at |lat| < 15 deg, the forest / savanna-grass /
desert biome areas, and the hot-month C3 failures: land cell-months with a monthly mean of 5 C or more where a C3
plant's quantum yield (vegetation._q3, Ci = 0.7 Ca, Ca held >= 124 ppm) is under a quarter of today's, and where it
is zero (Ci <= G*), as a share of those growing cell-months."""
import sys

import planet  # noqa: F401  (before numpy)
import numpy as np

from planet import climate
from planet import timezoom as Z
from planet import vegetation as V
from planet.timezoom.geometry import geometry

level = int(sys.argv[1]) if len(sys.argv) > 1 else 6
src = Z.source_earth(level)
g, tilt = src["grid"], src["tilt"]
elev, H = src["elev"], np.maximum(src["ice"], 0.0)
grounded = (H > 1) & (elev > 0)
surf = np.where(grounded, elev + H, elev)
area = geometry(g)["area"] / 1e6  # km2
land = (surf > 0) & ~grounded
al = np.abs(g.lat)
FOREST, OPEN, DESERT = {6, 9, 10, 13, 14}, {8, 12}, {7, 11}
print(f"Earth L{level}: pCO2 | global NPP Pg C/yr | trees |lat|<15 Mkm2 | forest / savanna-grass / desert Mkm2 |"
      f" C3 q < 1/4 of today's / q = 0, % of growing land cell-months")
for dT in (0.0, 3.0):
    c = climate.compute(g, surf, dT, tilt, ice=np.where(grounded, H, 0))
    for ppm in (350.0, 280.0, 190.0, 171.0, 150.0, 124.0):
        v = V.model(g, surf, c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"], tilt, c["cloud_jul"],
                    c["cloud_jan"], ice=np.where(grounded, H, 0), pco2=ppm)
        nu = v["eq"]["nu"]
        trees = float((nu[V.TREES].sum(0) * area * land * (al < 15)).sum()) / 1e6
        npp = float((np.asarray(v["sm"]["npp"], float) * area * 1e6 * land).sum()) / 1e15
        biome = V.biome_of(v["types"], 0)
        mk = lambda s: float((np.isin(biome, list(s)) * area * land).sum()) / 1e6
        tm = np.asarray(v["s"]["t"])  # (12, n) monthly means
        ca = max(ppm, V.CA_REF * 2 ** -V.CO2_RANGE)
        grow = (tm >= 5.0) & land[None, :]
        q = np.maximum(V._q3(tm, 0.7 * ca), 0.0) / V._q3(tm, V.CI_REF)
        print(f"dT {dT:+.0f} {ppm:4.0f} ppm | {npp:6.1f} | {trees:5.1f} | {mk(FOREST):5.1f} / {mk(OPEN):5.1f} /"
              f" {mk(DESERT):5.1f} | {100 * (grow & (q < 0.25)).sum() / grow.sum():5.2f} /"
              f" {100 * (grow & (q <= 0)).sum() / grow.sum():5.2f}", flush=True)
