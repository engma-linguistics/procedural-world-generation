"""Lane 137, Q1 A: how full are the cells? Sum of presences per peopled land cell; people per km2 of land vs the rungs."""
import json, sys, time
import numpy as np
sys.path.insert(0, ".")
import tools.peoples_robust as PRB
from planet.lineages import land as LD, recent as R, spec as SP
from planet.lineages.history import model as M
from planet.lineages.spread import EST

specs = [s for s in PRB.plan(families=["base"]) if s["name"].startswith("dnd-s7")]
spec = specs[0]
print(spec["name"], spec["world"])
t0 = time.time()
tree = SP.parse(spec["raw"])
tz, now0, world = R.resolve(spec["world"])
ps = R.Pass(tz, now0, R.RecentParams(kyr=30.0, climate_every=2.0), world_ref=world)
h = M.History(tree, ps, tree.seed * 1000, goods=LD.goods(world))
res = h.run()
P = res["present"]
people = np.array([not (l.megafauna or l.overlay or l.marine) for l in h.lines])
X = np.where(P >= EST, P, 0.0)[people]
land = h.cross.label >= 0
fill = X.sum(0)
pe = land & (fill > 0)
print("peopled land cells", int(pe.sum()), "of land", int(land.sum()))
print("sum of presences per peopled cell: pct10/25/50/75/90", np.round(np.percentile(fill[pe], [10, 25, 50, 75, 90]), 2), "mean", round(float(fill[pe].mean()), 2))
print("peoples per peopled cell: mean", round(float((X > 0).sum(0)[pe].mean()), 2))
D = h._dmap[people]
pop = (X * D).sum(0)  # per km2 of cell
print("people per km2 of peopled land (all peoples)", round(float(pop[pe].mean()), 3))
full = (X * D).sum(0) / np.maximum(fill, 1e-9)  # presence-weighted rung where the cell holds anyone
print("presence-weighted rung, mean over peopled land", round(float(full[pe].mean()), 3), " ratio", round(float(pop[pe].mean() / full[pe].mean()), 2))
# per main-rung of the leading people per cell
lead = np.argmax(X * D, 0)
rung = h.ladder.rung[people][lead, np.arange(X.shape[1])]
from planet.lineages.ladder import RUNGS
for i, nm in enumerate(RUNGS):
    sel = pe & (rung == i)
    if sel.sum() > 20:
        print(f"  cells led on {nm:13s} n={int(sel.sum()):5d} fill med {np.median(fill[sel]):.2f}  people/km2 {pop[sel].mean():.3g}  rung there {full[sel].mean():.3g}")
print("wall", round(time.time() - t0))
