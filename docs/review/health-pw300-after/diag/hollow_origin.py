"""python hollow_origin.py <code dir> seed t_before t_after: what changed under the biggest lake of t_after."""
import sys
sys.path.insert(0, sys.argv[1])
import planet  # noqa
import numpy as np
from planet import hydrology
from planet.grid import build_grid
from planet.tectonics import Params, Simulation
from planet.tectonics.isostasy import LIFT

seed, ta, tb = int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
g = build_grid(6)
sim = Simulation(g, seed, Params(flora_end=500.0), 2.0)
snaps = {}
for t in np.arange(ta, tb + 1e-6, 2.0):
    sim.run(t)
    snaps[t] = dict(bed=sim.bed().copy(), thick=sim.w_thick.copy(), lift=sim.w_extra[:, LIFT].copy(),
                    sea=sim.sea_level, sink=sim.ice_sink.copy(), ice=sim.ice.copy(), owner=sim.owner.copy(),
                    cover=sim.w_cover.copy(), elev=sim.w_elev.copy())
c = {"runoff": sim.runoff, "aet": sim.aet, "lake_evap": sim.lake_evap}
bed = sim.bed()
_, down, lk = hydrology.rivers_and_lakes(g, bed, c, np.where(bed > 0, sim.ice, 0.0), valley=sim.valley())
lab, k = g.components(lk["wet"] & sim.land())
cnt = np.bincount(lab[lab >= 0]); m = lab == cnt.argmax()
ring = np.zeros(g.n, bool)
for cidx in np.where(m)[0]:
    ring[g.nbr_idx[g.nbr_off[cidx]:g.nbr_off[cidx + 1]]] = True
ring &= ~m
print(f"lake {m.sum()} cells; rim ring {ring.sum()} cells")
ts = sorted(snaps)
for a, b in zip(ts[:-1], ts[1:]):
    A, B = snaps[a], snaps[b]
    d = lambda key, sel: np.median(B[key][sel] - A[key][sel])
    print(f"{a:g}->{b:g}: sea {B['sea'] - A['sea']:+.0f}  lake floor: bed {d('bed', m):+.0f} elev {d('elev', m):+.0f} "
          f"thick {d('thick', m):+.2f} km lift {d('lift', m):+.0f} cover {d('cover', m):+.3f} ice_sink {d('sink', m):+.0f} | "
          f"rim: bed {d('bed', ring):+.0f} elev {d('elev', ring):+.0f} thick {d('thick', ring):+.2f} lift {d('lift', ring):+.0f} "
          f"ice {np.mean(B['ice'][ring] > 0):.2f} sink {d('sink', ring):+.0f} | owner changed {np.mean(B['owner'][m] != A['owner'][m]):.2f}")
