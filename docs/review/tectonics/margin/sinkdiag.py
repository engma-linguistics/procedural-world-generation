"""tracediag.py plus a tally of where eroded rock ends up (PW-950, lane 100d), per step in the "sinks" dict of the
recorded step (km x level-5 cells, i.e. / scale^2): eroded (land erosion, surface.erode's removed), lake (deposit on
lake cells: lakes and closed basins), flood (deposit on other land: floodplains), shelf (sea cells above -400 m),
brink (deep cells next to land or shelf), fan (other deep cells), creep_off (cover the sea-floor creep took),
accreted (sediment scraped onto the overriding plate) and subducted (what went down with the slab: crust.accrete
scrapes params.accretion of the sediment the trench swallows, so the rest is scraped x (1 - a) / a).
Harness only: wraps surface.erode and crust.accrete, reads their results, changes nothing."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import surface  # noqa: E402
from planet.tectonics import crust, diag  # noqa: E402

T = {}
_erode, _accrete, _step = surface.erode, crust.accrete, diag.Recorder.step


def add(k, v):
    T[k] = T.get(k, 0.0) + float(v)


def erode(grid, elev, *a, **k):
    out = _erode(grid, elev, *a, **k)
    removed, dep, lk = out[3], out[4], out[7]
    land = surface.is_land(elev, grid=grid)
    ocean = ~land
    deep = ocean & (elev <= surface.SHELF_EDGE)
    nb_shallow = np.add.reduceat((~deep)[grid.nbr_idx].astype(int), grid.nbr_off[:-1]) > 0
    brink = deep & nb_shallow
    wet = lk["wet"]
    add("eroded", removed.sum())
    add("lake", dep[land & wet].sum())
    add("flood", dep[land & ~wet].sum())
    add("shelf", dep[ocean & ~deep].sum())
    add("brink", dep[brink].sum())
    add("fan", dep[deep & ~brink].sum())
    add("creep_off", out[8].sum())
    return out


def accrete(sim, bd, conv, col):
    c0 = col.cover.copy()
    _accrete(sim, bd, conv, col)
    d = col.cover - c0
    a = sim.params.accretion
    add("accreted", d[d > 0].sum())
    if a > 0:
        add("subducted", -d[d < 0].sum() * (1 - a) / a)


def step(self, sim):
    _step(self, sim)
    self.steps[-1]["sinks"] = {k: round(v / sim.scale**2, 2) for k, v in T.items()}
    T.clear()


surface.erode, crust.accrete, diag.Recorder.step = erode, accrete, step
here = Path(__file__).resolve().parent
sys.argv = [str(here / "tracediag.py")] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
