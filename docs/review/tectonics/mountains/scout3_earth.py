"""PW-1446 (b) scout 190: Earth's L6 and L7 cell-mean hypsometry in the screen's terms (read-only on data/earth).
usage: scout3_earth.py DATA_EARTH_DIR"""
import sys
import numpy as np

for lv in (6, 7):
    z = np.load(f"{sys.argv[1]}/L{lv}.npz")
    keys = list(z.keys())
    e = np.asarray(z["elev"], float)  # (the bed, as the runs' bed())
    if e is None:
        print(lv, keys); continue
    land = e > 0
    n = land.sum()
    print(f"Earth L{lv} (keys {keys[:8]}): land > 2/3/4 km "
          + " / ".join(f"{100 * (e > 1000 * k).sum() / n:.2f}%" for k in (2, 3, 4))
          + f"; cells > 5/6/7 km {(e > 5000).sum()} / {(e > 6000).sum()} / {(e > 7000).sum()}; highest {e.max():.0f} m")
