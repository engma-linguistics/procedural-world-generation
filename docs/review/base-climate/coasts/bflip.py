"""usage: bflip.py [--level L] k=v ... -> which Earth land cells leave or join Koppen B when climate.TUNE takes the
overrides k=v (against the defaults), split by whether Kottek calls them B, by continent box (lane 26b, PW-998
round 2: what a candidate's B loss is made of). Harness only."""
import sys
from pathlib import Path
W = str(Path(__file__).resolve().parents[4])
sys.path.insert(0, W)
import planet  # noqa
import numpy as np
from planet import climate
from tools import earth_check as E, earth_data
from tools.earth_data import cell_areas

level = 6
args = sys.argv[1:]
if args and args[0] == "--level":
    level = int(args[1]); args = args[2:]
base = dict(climate.TUNE)
out = []
for over in ({}, dict(kv.split("=") for kv in args)):
    climate.TUNE.clear(); climate.TUNE.update(base)
    climate.TUNE.update({k: float(v) for k, v in over.items()})
    grid, d, c, _, rec = E.run(level)
    out.append(E.group_of(np.asarray(c["koppen"])) == E.GROUPS.index("B"))
w = cell_areas(grid)
land = earth_data.land_of(d) & (grid.lat > -60)
ok = d["obs_koppen"].astype(int)
obsB = (E.group_of(ok) == E.GROUPS.index("B")) & (ok >= 0)
tot = w[land].sum() / 100
a, b = out
lonw = (grid.lon + 180) % 360 - 180
BOX = {"N America": (15, 75, -170, -50), "S America": (-60, 15, -90, -30), "Europe/Med": (30, 75, -15, 45),
       "Africa": (-40, 30, -20, 55), "Arabia/Mid East": (12, 42, 35, 65), "C Asia": (35, 55, 45, 90),
       "E Asia": (20, 55, 90, 150), "Australia": (-45, -10, 110, 155)}
print(f"{' '.join(args)}: B {100 * w[land & a].sum() / w[land].sum():.1f} -> {100 * w[land & b].sum() / w[land].sum():.1f}"
      f"; % of land: lost (Kottek B / not), gained (Kottek B / not)")
for nm, (a0, a1, o0, o1) in BOX.items():
    m = land & (grid.lat >= a0) & (grid.lat < a1) & (lonw >= o0) & (lonw < o1)
    f = lambda x: w[m & x].sum() / tot  # noqa: E731
    print(f"{nm:>16}  lost {f(a & ~b & obsB):5.2f} / {f(a & ~b & ~obsB):5.2f}   gained {f(~a & b & obsB):5.2f} / "
          f"{f(~a & b & ~obsB):5.2f}")
f = lambda x: w[land & x].sum() / tot  # noqa: E731
print(f"{'all':>16}  lost {f(a & ~b & obsB):5.2f} / {f(a & ~b & ~obsB):5.2f}   gained {f(~a & b & obsB):5.2f} / "
      f"{f(~a & b & ~obsB):5.2f}")
