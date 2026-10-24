"""Summarise tzlevel.py outputs: per variant, the ice at the start, its glacial maximum and interglacial minimum (the
largest and smallest ice volume after the first 20 kyr) and the means. Usage: tzsummary.py OUT1.json OUT2.json ..."""
import json
import sys

import numpy as np

print("| variant | ice vol start / max / min / mean (Mkm3) | iced cells % max / min / mean | sea level change min / max (m) |"
      " glacial index max | dT_global min |")
print("|---|---|---|---|---|---|")
for path in sys.argv[1:]:
    d = json.load(open(path))
    fr = d["frames"]
    t = np.array([f["t"] for f in fr])
    v = np.array([f["ice_volume_mkm3"] for f in fr])
    a = np.array([f["ice_pct"] for f in fr])
    sl = np.array([f["sea_level_change_m"] for f in fr])
    late = t >= 20
    print(f"| {d['run']} @{d['t']:g} {d['variant']} | {v[0]:.1f} / {v[late].max():.1f} / {v[late].min():.1f} / "
          f"{v[late].mean():.1f} | {a[late].max():.2f} / {a[late].min():.2f} / {a[late].mean():.2f} | "
          f"{sl.min():.0f} / {sl.max():.0f} | {max(f['glacial_index'] for f in fr):.2f} | "
          f"{min(f['dT_global'] for f in fr):.2f} |")
