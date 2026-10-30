"""maps.py MAIN_RUN.npz LANE_RUN.npz OUT.png TITLE: where each dragon kind lives at the present, main (left) against lane 50 (right),
one row per kind, on an equirectangular lat/lon map (land grey, the kind's presence coloured by density share)."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from planet.grid import build_grid

EST = 0.12
a, b = np.load(sys.argv[1]), np.load(sys.argv[2])
out, title = sys.argv[3], sys.argv[4]
g = build_grid(int(a["level"]))
v = g.centers
lat, lon = np.degrees(np.arcsin(v[:, 2])), np.degrees(np.arctan2(v[:, 1], v[:, 0]))
KINDS = [("red_dragon", "#c0392b"), ("blue_dragon", "#2e6fd8"), ("green_dragon", "#2e8b3a"), ("black_dragon", "#222222"),
         ("white_dragon", "#7fb3d5"), ("gold_dragon", "#d4a017"), ("silver_dragon", "#8e9aa6"), ("bronze_dragon", "#a0662b"),
         ("copper_dragon", "#d35400"), ("brass_dragon", "#b8a040")]
fig, ax = plt.subplots(len(KINDS), 2, figsize=(13, 2.6 * len(KINDS)), constrained_layout=True)
for col, z in enumerate((a, b)):
    ids = [str(x) for x in z["ids"]]
    land = z["land"]
    rich = land & (z["prey"] >= 3)
    for row, (kid, c) in enumerate(KINDS):
        A = ax[row, col]
        A.scatter(lon[land], lat[land], s=0.15, c="#dddddd", linewidths=0)
        A.scatter(lon[rich], lat[rich], s=0.15, c="#c8e0b8", linewidths=0)
        n = 0
        if kid in ids:
            P = z["P"][ids.index(kid)]
            h = P >= EST
            n = int(h.sum())
            A.scatter(lon[h], lat[h], s=0.6, c=c, alpha=np.clip(P[h], 0.25, 1), linewidths=0)
        cnt = json_count = None
        A.set_title(f"{['main', 'lane 50'][col]}: {kid.replace('_', ' ')}s, {n:,} cells", fontsize=9)
        A.set_xlim(-180, 180); A.set_ylim(-90, 90); A.set_xticks([]); A.set_yticks([])
fig.suptitle(title + "  (grey land, pale green: rich land >= 3 t/km2 of prey)", fontsize=11)
fig.savefig(out, dpi=50)
print("wrote", out)
