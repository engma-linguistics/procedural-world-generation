"""PW-054 scout 250: where the land the dry-hollow rule adds to inland drainage on Earth lies, and whether it
ends in a kept hollow. Earth terrain + the model's climate, nothing imposed. Read-only. Usage: LEVEL"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import planet  # noqa
import numpy as np
from tools import earth_world as EW
from tools import earth_data as ED
from planet import hydrology as Hy
from planet.grid import build_grid
from planet.geo import is_land

lvl = int(sys.argv[1]) if len(sys.argv) > 1 else 6
grid = build_grid(lvl)
cap = {}
orig = Hy.rivers_and_lakes


def spy(*a, **k):
    cap.setdefault("args", (a, k))
    return orig(*a, **k)


import planet.world as W  # noqa
Hy.rivers_and_lakes = spy
W.hydrology.rivers_and_lakes = spy
real_closed = ED.earth_closed(grid)
EW.earth_closed = lambda g: None
EW.earth_outlets = lambda g: None
Hy.DRY_HOLLOWS = False
EW.build(lvl)
(a, k) = cap["args"]
g, elev, c = a[0], a[1], a[2]
ice = a[3] if len(a) > 3 else k.get("ice")
valley = k.get("valley")
land = is_land(elev, ice, grid)
free = land & ((ice <= 0) if ice is not None else True)
nf = free.sum()
realc = (real_closed >= 0) & free
_, _, lk0 = orig(g, elev, c, ice, valley=valley)
i0 = lk0["endorheic"] & free
Hy.DRY_HOLLOWS = True
kept = np.zeros(grid.n, bool)
dh = Hy._dry_hollows


def spy_dh(*a, **k):
    r = dh(*a, **k)
    kept[:] |= r
    return r


Hy._dry_hollows = spy_dh
flow, down, lk = orig(g, elev, c, ice, valley=valley)
i1 = lk["endorheic"] & free
add = i1 & ~i0
to_kept = Hy.endorheic(down, lk["order"], lk["sink"] & kept) & add
print(f"L{lvl} added {100*add.sum()/nf:.1f}% of land; ends in a kept hollow {100*to_kept.sum()/max(add.sum(),1):.0f}% "
      f"(rain {c['precip'][to_kept].mean():.0f} mm), elsewhere rain {c['precip'][add&~to_kept].mean() if (add&~to_kept).any() else 0:.0f} mm")
lab, kk = grid.components(add)
sz = np.bincount(lab[lab >= 0])
ck = 510.1e6 / grid.n
for b in np.argsort(-sz)[:12]:
    m = lab == b
    ai = c["precip"][m].sum() / c["pet"][m].sum()
    print(f"  {sz[b]*ck/1e3:7.0f} kkm2 at lat {grid.lat[m].mean():6.1f} lon {grid.lon[m].mean():7.1f}: rain {c['precip'][m].mean():5.0f} mm, "
          f"P/PET {ai:.2f}, real closed {100*realc[m].mean():3.0f}%, kept cells {kept[m].sum()}, lake cells {(lk['wet'][m]).sum()}")
