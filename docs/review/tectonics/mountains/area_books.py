"""PW-1683 lane 288 (l7-high-ground.md 2.3): continental AREA gained and lost per process, a run resumed from a
checkpoint for a while (the run's crust books, sim.budget, are volume; this is the area beside them). Read-only on
the run: the resumed simulation is thrown away.

Each process's change in continental cells, as % of the surface per 100 Myr: plate_kernels.resolve + cleanup_ghosts
(the plates' motion sampled onto the world grid, collisions' overlap), subduction erosion, Andean closing,
stretch (rifted margins, necking), coherence (welds + / shreds -), birth (arcs and sediment piles), the events
(sutures, slivers, rifts) and the rest (write-back, erosion's coast).
usage: PYTHONPATH=. area_books.py RUN_DIR T0 MYR"""
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from planet import store as S
from planet.grid import build_grid
from planet.tectonics import crust, events
from planet.tectonics import simulation as simmod
from planet.tectonics.params import Params
from planet.tectonics.simulation import Simulation

AREA = defaultdict(float)
COUNT = defaultdict(int)


def wrap_col(mod, name, label):
    """crust.f(sim, ..., col, ...): area of col.cont before and after (col is found among the args)."""
    f = getattr(mod, name)

    def g(sim, *a, **k):
        col = next(x for x in a if isinstance(x, crust.Column))
        n0 = int(col.cont.sum())
        out = f(sim, *a, **k)
        AREA[label] += (int(col.cont.sum()) - n0) / sim.grid.n
        if name == "coherence":
            AREA["coherence.weld"] += int(out[0].sum()) / sim.grid.n
            AREA["coherence.shred"] -= int(out[1].sum()) / sim.grid.n
        return out

    setattr(mod, name, g)


def wrap_world(cls_or_mod, name, label):
    """A step phase that changes sim.w_cont: area before and after."""
    f = getattr(cls_or_mod, name)

    def g(sim, *a, **k):
        n0 = int(sim.w_cont.sum())
        out = f(sim, *a, **k)
        AREA[label] += (int(sim.w_cont.sum()) - n0) / sim.grid.n
        return out

    setattr(cls_or_mod, name, g)


def main(rd, t0, myr):
    rd = Path(rd)
    m = S.read_header(rd / "run.json")["meta"]
    g = build_grid(m["level"])
    params = Params.from_stored(m["params"])
    for name, label in (("subduction_erosion", "subd.erosion"), ("andean_contraction", "andean"),
                        ("stretch", "stretch"), ("coherence", "coherence")):
        wrap_col(crust, name, label)
    wrap_world(Simulation, "_resolve", "resolve")
    # (the events change the plates; the world view shows it at the step's end: area from write-back to step end)
    f_wb, f_step = Simulation._write_back, Simulation.step
    mark = {}

    def write_back(sim, col, born):
        AREA["birth"] += int((born & ~col.cont).sum()) / sim.grid.n
        n_phys = int(col.cont.sum())
        AREA["physics.rest"] += (n_phys - mark["after_resolve"]) / sim.grid.n
        out = f_wb(sim, col, born)
        mark["after_wb"] = int(sim.w_cont.sum())
        return out

    def step(sim):
        out = f_step(sim)
        AREA["events"] += (int(sim.w_cont.sum()) - mark["after_wb"]) / sim.grid.n
        return out

    f_res = Simulation._resolve

    def resolve(sim):
        out = f_res(sim)
        mark["after_resolve"] = int(sim.w_cont.sum())
        return out

    Simulation._write_back, Simulation.step, Simulation._resolve = write_back, step, resolve
    sim = Simulation.from_state(g, m["seed"], params, m["dt"], S.load_checkpoint(rd, t0, g))
    a0 = float(sim.w_cont.mean())
    shrink = []
    f_th = crust.thermostats

    def th(s):
        out = f_th(s)
        shrink.append(float(out[1]))
        return out

    crust.thermostats = th
    simmod.crust = crust
    sim.run(t0 + myr)
    AREA["physics.rest"] -= sum(AREA[k] for k in ("subd.erosion", "andean", "stretch", "coherence"))
    tot = float(sim.w_cont.mean()) - a0
    known = sum(v for k, v in AREA.items() if k not in ("coherence.weld", "coherence.shred"))
    AREA["rest"] = tot - known
    per = 100.0 / myr * 100  # (fraction -> % of the surface per 100 Myr)
    print(f"# {rd.name} seed {m['seed']} L{m['level']} andean_shortening {params.andean_shortening} "
          f"from {t0} for {myr} Myr: area {100 * a0:.2f} -> {100 * sim.w_cont.mean():.2f}% "
          f"(target {100 * sim.target_fraction():.1f}%); subduction erosion factor mean {np.mean(shrink):.2f}")
    for k in sorted(AREA, key=lambda k: AREA[k]):
        print(f"  {k:24s} {per * AREA[k]:+7.2f} % of the surface per 100 Myr")
    print(f"  {'total':24s} {per * tot:+7.2f}")


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
