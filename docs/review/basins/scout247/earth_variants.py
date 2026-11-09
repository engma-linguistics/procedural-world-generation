"""Earth L6 terrain + the model's climate, through hydrology.rivers_and_lakes with no HydroSHEDS data
imposed, under variants; and where HydroSHEDS's real closed basins are lost. Nothing is saved."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import planet  # noqa
import numpy as np
from tools import earth_world as EW
from tools import earth_data as ED
from planet import hydrology as Hy, kernels
from planet.grid import build_grid
from planet.geo import is_land

lvl = int(sys.argv[1]) if len(sys.argv) > 1 else 6
grid = build_grid(lvl)
cap = {}
orig = Hy.rivers_and_lakes


def spy(*a, **k):
    cap.setdefault("args", (a, k))
    return orig(*a, **k)


Hy.rivers_and_lakes = spy
import planet.world as W  # noqa
Hy.DRY_HOLLOWS = False
W.hydrology.rivers_and_lakes = spy
real_closed = ED.earth_closed(grid)
EW.earth_closed = lambda g: None
EW.earth_outlets = lambda g: None
EW.build(lvl)
(a, k) = cap["args"]
g, elev, c = a[0], a[1], a[2]
ice = a[3] if len(a) > 3 else k.get("ice")
valley = k.get("valley")
land = is_land(elev, ice, grid)
free = land & ((ice <= 0) if ice is not None else True)
nf = free.sum()
realc = (real_closed >= 0) & free
print(f"HydroSHEDS closed (>=half the cell drains inland): {100*realc.sum()/nf:.1f}% of ice-free land")

# terrain hollows on Earth's L6 cell means
filled, down0, order0 = kernels.priority_flood(elev.astype(float), ~land, grid.nbr_off, grid.nbr_idx, 0.01)


def through(hollow, down, order):
    p = hollow.copy()
    for i in order:
        d = down[i]
        if d >= 0 and p[d]:
            p[i] = True
    return p


A = through(land & (filled - elev > 1.0), down0, order0)
bed = Hy._bed(grid, elev.astype(float), ~land, Hy.MIN_DEPTH, Hy.MIN_SLOPE)
f2, d2, o2 = kernels.priority_flood(bed, ~land, grid.nbr_off, grid.nbr_idx, 0.01)
B = through(land & (f2 - bed > 1.0), d2, o2)
print(f"real closed area: in a raw hollow's catchment {100*(realc&A).sum()/realc.sum():.0f}%, "
      f"in a kept hollow's {100*(realc&B).sum()/realc.sum():.0f}%")


def run(label, c=c, channel=None, md=None, ms=None):
    dflt = Hy.lakes.__defaults__
    if md is not None:
        d = list(dflt); d[1] = md; d[2] = ms; Hy.lakes.__defaults__ = tuple(d)
    try:
        flow, down, lk = orig(g, elev, c, ice, channel=channel, valley=valley)
    finally:
        Hy.lakes.__defaults__ = dflt
    inl = lk["endorheic"] & free
    print(f"{label:38s} inland {100*inl.sum()/nf:5.1f}% | of real closed: {100*(inl&realc).sum()/realc.sum():4.0f}% "
          f"| inland outside real closed {100*(inl&~realc).sum()/nf:4.1f}% of land", flush=True)
    fp = inl & ~realc
    print(f"{'':38s} false-positive land: arid (obs Koppen B) {100*(fp&arid).sum()/max(1,fp.sum()):.0f}%, "
          f"mean precip {c['precip'][fp].mean() if 'precip' in c and fp.any() else float('nan'):.0f} mm; lat |median| {np.median(np.abs(grid.lat[fp])) if fp.any() else 0:.0f}", flush=True)
    return inl


from tools.scorecard import GROUP
ok = ED.earth_on_grid(grid)["obs_koppen"].astype(int)
arid = (ok >= 0) & (GROUP[np.maximum(ok, 0)] == "B")
Hy.DRY_HOLLOWS = False
inl0 = run("main (DRY_HOLLOWS off)")
miss = realc & ~inl0
print(f"missed real closed {100*miss.sum()/nf:.1f}% of land: not in any raw hollow {100*(miss&~A).sum()/nf:.1f}, "
      f"raw but filtered (MIN_DEPTH/SLOPE) {100*(miss&A&~B).sum()/nf:.1f}, kept hollow that spills {100*(miss&B).sum()/nf:.1f}")
Hy.DRY_HOLLOWS = True
inl1 = run("candidate: dry hollows kept")
c2 = dict(c); c2["lake_evap"] = c["lake_evap"] * 0.8

c3 = dict(c); c3["runoff"] = c["runoff"] * 1.3
run("candidate, runoff x1.3", c=c3)
Hy.DRY_HOLLOWS = False
run("main, runoff x1.3", c=c3)
