"""PW-054 scout 250: Earth terrain + the model's climate through hydrology.rivers_and_lakes, nothing imposed,
main (DRY_HOLLOWS off) against the dry-catchment rule (catchment rain < DRYLAND_AI x Oudin PET).
Read-only (nothing saved). Usage: earth_dry.py LEVEL [AI ...]"""
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
from tools.scorecard import GROUP

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
ok = ED.earth_on_grid(grid)["obs_koppen"].astype(int)
arid = (ok >= 0) & (GROUP[np.maximum(ok, 0)] == "B")
ai = c["precip"] / np.maximum(c["pet"], 1.0)
print(f"L{lvl}: HydroSHEDS closed {100*realc.sum()/nf:.1f}% of ice-free land; obs Koppen B {100*(arid&free).sum()/nf:.1f}%")
for t in (0.3, 0.5, 0.65, 1.0):
    m = free & (ai < t)
    print(f"  model P/PET(Oudin) < {t}: {100*m.sum()/nf:.1f}% of land, of it obs B {100*(m&arid).sum()/max(m.sum(),1):.0f}%, "
          f"mean rain {c['precip'][m].mean():.0f} mm")
print(f"  obs-B land: model P/PET median {np.median(ai[free&arid]):.2f}, p90 {np.percentile(ai[free&arid],90):.2f}; "
      f"real closed land P/PET median {np.median(ai[realc]):.2f}")


def run(label):
    flow, down, lk = orig(g, elev, c, ice, valley=valley)
    inl = lk["endorheic"] & free
    fp = inl & ~realc
    lake = land & lk["wet"]
    lab, kk = grid.components(lake)
    big = np.bincount(lab[lab >= 0]).max() * 510.1e6 / grid.n / 1e6 if kk else 0
    print(f"{label:28s} inland {100*inl.sum()/nf:5.1f}% | of real closed {100*(inl&realc).sum()/realc.sum():3.0f}% "
          f"| false + {100*fp.sum()/nf:4.1f}% of land, obs B {100*(fp&arid).sum()/max(1,fp.sum()):.0f}%, "
          f"rain {c['precip'][fp].mean() if fp.any() else float('nan'):.0f} mm | lakes {100*lake.sum()/land.sum():.2f}% "
          f"largest {big:.2f} Mkm2", flush=True)
    return inl


Hy.DRY_HOLLOWS = False
i0 = run("main")
Hy.DRY_HOLLOWS = True
for arg in (sys.argv[2:] or ["0.65"]):
    # "dig0.65": the hollow kept by deepening its lowest cell (pass 1's way); else its cells reset to the ground
    Hy._DRY_DIG = arg.startswith("dig")
    t = float(arg.removeprefix("dig"))
    Hy.DRYLAND_AI = t
    i1 = run(f"dry catchments AI<{t}{' dig' if Hy._DRY_DIG else ''}")
    add = i1 & ~i0
    print(f"{'':28s} added {100*add.sum()/nf:.1f}% (real closed {100*(add&realc).sum()/max(add.sum(),1):.0f}%, "
          f"rain {c['precip'][add].mean() if add.any() else float('nan'):.0f} mm); lost {100*(i0&~i1).sum()/nf:.1f}%")
