"""Finer hollow budget: per substage of the step (see hollow_budget.py).
python hollow_budget2.py <code root> level seed myr"""
import sys
sys.path.insert(0, sys.argv[1])
import planet  # noqa
import numpy as np
from planet import kernels, hydrology
from planet.grid import build_grid
from planet.geo import R_KM
from planet.tectonics import Params, Simulation, earth, crust
from planet.tectonics.isostasy import elevation, sediment_km

level, seed, myr = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
g = build_grid(level)
ckm2 = 4 * np.pi * R_KM ** 2 / g.n
acc = {}
order = []
state = {"t": 0.0}


def measure(e):
    e = np.asarray(e, float)
    land = e > 0
    bed = hydrology._bed(g, e, hydrology.MIN_DEPTH, hydrology.MIN_SLOPE)
    sp = kernels.priority_flood(np.asarray(bed, float), g.nbr_off, g.nbr_idx, 0.01)[0]
    d = np.where(land, np.maximum(sp - bed, 0), 0)
    lab, k = g.components(land & (d > 0.5))
    if not k:
        return 0.0, 0.0, 0.0
    area = np.bincount(lab[lab >= 0]) * ckm2 / 1e6
    giant = (lab >= 0) & (area[np.maximum(lab, 0)] >= 1.0)
    return float(d.sum() * ckm2 / 1e3), float(d[giant].sum() * ckm2 / 1e3), float(giant.sum() * ckm2 / 1e6)


def mark(stage, e):
    if stage not in acc:
        acc[stage] = []
        order.append(stage)
    v = measure(e)
    if "last" in state and state["t"] > 50:
        acc[stage].append(tuple(a - b for a, b in zip(v, state["last"])))
    state["last"] = v


def col_elev(sim, col):
    return elevation(col.t, sim.w_age, col.cont, col.rock, sim.datum(), sediment_km(col.cover, col.x))


def wrap_col(mod, name, label=None):
    real = getattr(mod, name)

    def f(sim, *a, **kw):
        out = real(sim, *a, **kw)
        col = next(x for x in a if hasattr(x, "cover") and hasattr(x, "rec"))
        mark(label or name, col_elev(sim, col))
        return out
    setattr(mod, name, f)


real_resolve = Simulation._resolve
real_age = Simulation._age
real_physics = Simulation._physics


def resolve(self):
    out = real_resolve(self)
    mark("resolve", self.w_elev)
    return out


def age(self, dome):
    col = real_age(self, dome)
    mark("age (world view)", col_elev(self, col))
    return col


def physics(self, *a):
    real_physics(self, *a)
    mark("write back", self.w_elev)


Simulation._resolve, Simulation._age, Simulation._physics = resolve, age, physics
for n in ("add_arcs_and_plumes", "stack_collisions", "accrete", "subduction_erosion", "stretch", "flow_and_orogeny",
          "coherence", "birth_and_cratons"):
    wrap_col(crust, n)
real_erode = earth.erode


def erode(sim, col):
    mark("volcanoes+temperature", col_elev(sim, col))
    out = real_erode(sim, col)
    mark("erode", col_elev(sim, col))
    return out


earth.erode = erode
for n in ("sediments", "bury", "reefs"):
    wrap_col(earth, n)
sim = Simulation(g, seed, Params(flora_end=myr), 2.0)


def on(s):
    state["t"] = s.t
    mark("events+climate", s.w_elev)


sim.run(myr, on)
print(f"L{level} seed {seed}, {myr} Myr, per step after 50 Myr: hollow volume change km3 (gross +/-); in giant "
      f"(>= 1 Mkm2) hollows km3 (gross +/-); giant hollow area Mkm2 (gross +)")
for s in order:
    a = np.array(acc[s])
    if not len(a):
        continue
    gp = lambda c: a[:, c][a[:, c] > 0].sum() / len(a)
    gm = lambda c: -a[:, c][a[:, c] < 0].sum() / len(a)
    print(f"  {s:24s} {a[:, 0].mean():+8.0f} (+{gp(0):6.0f} -{gm(0):6.0f})  giant {a[:, 1].mean():+8.0f} "
          f"(+{gp(1):6.0f} -{gm(1):6.0f})  area {a[:, 2].mean():+.3f} (+{gp(2):.3f})")
