"""Earth L6: how deep the water is in the near-land seas the summer bars read (is a 50 m layer deeper than the sea?).
usage: depth.py (from the tree's root or anywhere)"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..")))
from planet import climate  # planet before numpy
import numpy as np
from planet.grid import build_grid
from tools import earth_data

g = build_grid(6)
d = earth_data.earth_on_grid(g)
lat, lon = g.lat, g.lon
e = d["elev"]
oc = e < 0
print("cell km %.0f" % (4 * np.pi * 6371 ** 2 / g.n) ** 0.5)
B = {"North Sea": (51, 61, -4, 9), "Biscay": (43, 48, -10, -1), "Channel/Irish": (49, 55, -11, -3),
     "Baltic": (54, 66, 10, 30), "Yellow/ECS": (25, 41, 117, 128), "Gulf of Maine": (40, 45, -71, -65),
     "Pat shelf": (-52, -38, -68, -56), "Tasman 35-45": (-45, -35, 148, 160), "Agulhas": (-40, -30, 20, 32),
     "NE Atl 45-55": (45, 55, -25, -10)}
for k, (a0, a1, l0, l1) in B.items():
    m = oc & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)
    z = -e[m]
    print(f"{k:14s} n={m.sum():3d} depth p10/50/90 {np.percentile(z, 10):.0f}/{np.percentile(z, 50):.0f}/"
          f"{np.percentile(z, 90):.0f}  <50m {np.mean(z < 50) * 100:.0f}%  <100m {np.mean(z < 100) * 100:.0f}%")
for hemi, m0 in (("N 20-65", (lat >= 20) & (lat < 65)), ("S 20-65", (lat <= -20) & (lat > -65))):
    m = oc & m0
    z = -e[m]
    print(hemi, "ocean cells", m.sum(), "<50m %.1f%% <100m %.1f%%" % (np.mean(z < 50) * 100, np.mean(z < 100) * 100))
