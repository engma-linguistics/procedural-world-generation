"""PW-359: how much of a step's change is lost when the world view is
written back to the plates (Simulation._scatter: several world cells can
sample one plate cell, and the last write wins), and where.

    uv run python docs/review/audit/tectonics-night/writeback.py <repo> <level> <seed> <myr>

Per step after 50 Myr: the world view's crust right after _physics against
what the plates hold for the same cells after _scatter: km x cells lost or
gained (thickness), as a share of the step's gross change of land cells;
and of the cells whose fill (deposit) was lost, the share that sat in a
closed hollow (lakes' filter) before the step's erosion.
"""
import sys

sys.path.insert(0, sys.argv[1])
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402

level, seed, myr = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
g = build_grid(level)
rows = []
real_scatter = Simulation._scatter
real_age = Simulation._age
state = {}


def age(self, dome):
    col = real_age(self, dome)
    state["t0"] = self.w_thick.copy()
    return col


def scatter(self):
    real_scatter(self)
    if self.t <= 50 or "t0" not in state:
        return
    pl = self.plates
    held = pl.thick[self.owner, self.w_ref]
    want = self.w_thick
    land = self.w_elev > 0
    lost = want - held  # >0: a gain the plates didn't keep
    gross = np.abs(want - state["t0"])
    rows.append(dict(
        lost_gain=float(lost[land & (lost > 0)].sum()), lost_loss=float(-lost[land & (lost < 0)].sum()),
        gross=float(gross[land].sum()), cells=float((land & (np.abs(lost) > 1e-6)).mean() / max(land.mean(), 1e-9))))


Simulation._scatter, Simulation._age = scatter, age
sim = Simulation(g, seed, Params(flora_end=myr), 2.0)
sim.run(myr)
a = {k: np.array([r[k] for r in rows]) for k in rows[0]}
print(f"L{level} seed {seed}: per step on land, the change the plates didn't keep: gains {a['lost_gain'].mean():.0f}, "
      f"losses {a['lost_loss'].mean():.0f} km x cells, of a gross change {a['gross'].mean():.0f} "
      f"({(a['lost_gain'] + a['lost_loss']).mean() / a['gross'].mean() * 100:.1f}%); land cells affected "
      f"{a['cells'].mean() * 100:.1f}%")
