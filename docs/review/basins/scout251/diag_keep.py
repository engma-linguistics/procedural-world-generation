"""diag_keep.py CODE CKPT SEED LEVEL T: continue the fork with CODE (offset 0) to T; for the frame's largest lake
(water_now), the kept dry hollows (_settle's keep, last try) under it: their component, its sinks, open/wet cells,
and its catchment's rain / PET on the final routing."""
import pickle
import sys
import zlib
from pathlib import Path

import numpy as np

code, ck, seed, level, T = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
sys.path.insert(0, str(Path(code).resolve()))
import planet  # noqa
from planet.grid import build_grid
from planet.geo import is_land
from planet.tectonics import Params, Simulation
from planet.tectonics.output import water_now
from planet import hydrology as Hy

grid = build_grid(level)
ckm = 510.1e6 / grid.n
state = pickle.loads(zlib.decompress(Path(ck).read_bytes()))
for n in Simulation.STATE:
    state.setdefault(n, None)
sim = Simulation.from_state(grid, seed, Params(run_end=400.0), 2.0, state)
sim.run(T)
cap = []
f0 = Hy._settle


def settle(*a, **k):
    out = f0(*a, **k)
    cap.append((a, k, out))
    return out


Hy._settle = settle
w = water_now(sim)
land = is_land(sim.bed(), grid=grid)
lake = land & (w["lake_depth"] > 0)
lab, nl = grid.components(lake)
sz = np.bincount(lab[lab >= 0])
L = lab == int(sz.argmax())
print(f"t={T:g} largest lake {L.sum() * ckm / 1e6:.2f} Mkm2, kinds {np.bincount(w['lake_kind'][L], minlength=4)[1:]}, "
      f"P {sim.precip[L].mean():.0f} PET {sim.pet[L].mean():.0f}; _settle calls {len(cap)}")
for i, (a, k, out) in enumerate(cap):
    (bed, wet, open_, out_z, pit, catch, basin), (flow, down, order, sink), keep = out
    kl, kn = grid.components(keep)
    ids = np.unique(kl[L & keep])
    print(f" try {i}: lake cells kept {(L & keep).sum()}/{L.sum()}; kept comps under it {ids.tolist()}")
    rain, pet = k["dry"]
    for c in ids:
        if c < 0:
            continue
        m = kl == c
        up = Hy._upstream_label(down, order, np.where(m, 0, -1)) == 0
        print(f"   comp {c}: {m.sum()} cells ({m.sum() * ckm / 1e6:.2f} Mkm2), sinks {(m & sink).sum()}, wet {(m & wet).sum()}"
              f" (open {(m & wet & open_).sum()}), catchment {up.sum()} cells P/PET {rain[up].sum() / max(pet[up].sum(), 1):.2f};"
              f" lake's own basin ids {np.unique(basin[L])[:5].tolist()}, open there {(L & open_).sum()}")
