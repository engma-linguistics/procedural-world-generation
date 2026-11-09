"""PW-831 scout 261: the Niger fix on one generated state (fork_run.py's checkpoint): hydrology.lakes as the run's
erosion step calls it (w_elev, the climate fields, pet, the valley memory), with the known channels read (the fix) and
not (main's rule): kept dry-hollow cells, inland % of land, lakes % of land. Usage: same_state.py CKPT SEED LEVEL"""
import pickle
import sys
import zlib
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import numpy as np
from planet import hydrology as Hy
from planet.grid import build_grid
from planet.geo import is_land
from planet.tectonics import Params, Simulation
from planet.tectonics.isostasy import VALLEY

state = pickle.loads(zlib.decompress(Path(sys.argv[1]).read_bytes()))
for n in Simulation.STATE:
    state.setdefault(n, None)
grid = build_grid(int(sys.argv[3]))
sim = Simulation.from_state(grid, int(sys.argv[2]), Params(), 2.0, state)
elev, valley = sim.w_elev, sim.w_extra[:, VALLEY]
land = is_land(elev, grid=grid)
orig = Hy._dry_hollows
kept = {}
for name in ("fix", "main"):
    def spy(*a, chan=None, _n=name):
        r = orig(*a, chan=chan if _n == "fix" else None)
        kept.setdefault(_n, r)
        return r
    Hy._dry_hollows = spy
    lk = Hy.lakes(grid, elev, sim.runoff, sim.aet, sim.lake_evap, valley=valley, land=land, pet_mm=sim.pet)
    flow, down, order, _ = Hy.route(grid, elev, lk)
    inl = Hy.endorheic(down, order, lk["sink"]) & land
    print(f"{name}: kept cells {kept[name].sum()}, inland {100*inl.sum()/land.sum():.2f}% of land, lakes "
          f"{100*(lk['wet']&land).sum()/land.sum():.2f}%, valley > 0 on {(valley > 0).sum()} cells")
