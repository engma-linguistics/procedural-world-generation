"""diag_swap.py CODE CKPT SEED LEVEL NEW_HYDROLOGY T [T...]: continue the fork with CODE (offset 0) to each T, then the
frame's lakes (water_now) with CODE's rule, with the rule off, and with NEW_HYDROLOGY's _settle and lakes swapped in
(same terrain and climate: only the rule differs)."""
import ast
import pickle
import sys
import zlib
from pathlib import Path

import numpy as np

code, ck, seed, level, newf = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
sys.path.insert(0, str(Path(code).resolve()))
import planet  # noqa
from planet.grid import build_grid
from planet.geo import is_land
from planet.tectonics import Params, Simulation
from planet.tectonics.output import water_now
from planet import hydrology as Hy

src = Path(newf).read_text()
tree = ast.parse(src)
new_ns = dict(Hy.__dict__)
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in ("_settle", "lakes"):
        exec(compile(ast.Module([node], []), newf, "exec"), new_ns)
old = {k: getattr(Hy, k) for k in ("_settle", "lakes")}
grid = build_grid(level)
ckm = 510.1e6 / grid.n
state = pickle.loads(zlib.decompress(Path(ck).read_bytes()))
for n in Simulation.STATE:
    state.setdefault(n, None)
sim = Simulation.from_state(grid, seed, Params(run_end=400.0), 2.0, state)


def show(T, name):
    w = water_now(sim)
    land = is_land(sim.bed(), grid=grid)
    lake = land & (w["lake_depth"] > 0)
    lab, k = grid.components(lake)
    sz = np.bincount(lab[lab >= 0]) * ckm / 1e6
    b = int(sz.argmax())
    print(f"t={T:g} {name:6s} largest {sz.max():.2f} Mkm2 kinds {np.bincount(w['lake_kind'][lab == b], minlength=4)[1:]}"
          f" P {sim.precip[lab == b].mean():.0f} | lakes {100 * lake.sum() / land.sum():.2f}% | >1 Mkm2 {(sz > 1).sum()}"
          f" | inland-ish sinks {(land & (w['downstream'] < 0)).sum()}", flush=True)


for T in map(float, sys.argv[6:]):
    sim.run(T)
    show(T, "code")
    Hy.DRY_HOLLOWS = False
    show(T, "off")
    Hy.DRY_HOLLOWS = True
    for k in old:
        setattr(Hy, k, new_ns[k])
    new_ns["_settle"] = new_ns["_settle"]
    show(T, "new")
    for k, v in old.items():
        setattr(Hy, k, v)
