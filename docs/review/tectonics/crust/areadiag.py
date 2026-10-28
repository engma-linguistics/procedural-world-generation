"""Area budget diagnostic: per-process change of continental cell count (L5 cells), thermostat state."""
import sys
import planet  # noqa
import numpy as np
from planet.grid import build_grid
from planet.tectonics import crust
from planet.tectonics import simulation as S
from planet.tectonics.params import Params

level, seed, end = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
sets = {k: float(v) for k, v in (kv.split("=") for kv in sys.argv[4:])}
area = {}


def acc(k, v):
    area[k] = area.get(k, 0.0) + v


def wrap_col(name, colarg):
    fn = getattr(crust, name)

    def f(*a, **kw):
        col = a[colarg]
        c0 = col.cont.sum()
        r = fn(*a, **kw)
        acc(name, (col.cont.sum() - c0) / a[0].scale**2)
        return r
    setattr(crust, name, f)


import os
import inspect
import textwrap
EXP = os.environ.get("EXP", "")
if os.environ.get("EXPF"):
    EXP = ";;".join(open(os.path.join(os.path.dirname(__file__), f)).read().rstrip("\n") for f in os.environ["EXPF"].split(","))
if EXP:
    src = textwrap.dedent(inspect.getsource(crust.coherence))
    for rep in EXP.split(";;"):
        a, b = rep.split("=>")
        assert a in src, a
        src = src.replace(a, b)
    ns = vars(crust)
    exec(compile(src, "coh_exp", "exec"), ns)
    print("EXP coherence patched:", EXP, flush=True)
orig_coh = crust.coherence


def coh(sim, col, trench=None):
    from planet.tectonics import record
    t_before = col.t.copy()
    r = orig_coh(sim, col, trench)
    weld, shred = r
    s2 = sim.scale**2
    acc("weld", weld.sum() / s2)
    acc("shred", -shred.sum() / s2)
    if weld.any():
        acc("weld_young", (weld & (sim.w_age < 10)).sum() / s2)
        acc("weld_thin", (weld & (col.t < 20)).sum() / s2)
        acc("weld_wasc", (weld & PREV[0]).sum() / s2)
        acc("weld_vol", float((t_before * weld).sum()) / s2)
        acc("weld_rift", (weld & (sim.t - col.rec[:, record.T_RIFT] < 20)).sum() / s2)
    if shred.any():
        acc("shred_wasoc", (shred & ~PREV[0]).sum() / s2)
        acc("shred_vol", -float((t_before * shred).sum()) / s2)
    return r


crust.coherence = coh
for name, ca in [("subduction_erosion", 3), ("stretch", 1), ("coherence", 1), ("birth_and_cratons", 1)]:
    wrap_col(name, ca)
orig_res = S.Simulation._resolve


PREV = [None]


def res(self):
    PREV[0] = self.w_cont.copy()
    c0 = self.w_cont.sum()
    r = orig_res(self)
    acc("resolve", (self.w_cont.sum() - c0) / self.scale**2)
    return r


S.Simulation._resolve = res
shr = []
orig_th = crust.thermostats


def th(sim):
    r = orig_th(sim)
    shr.append(r)
    return r


crust.thermostats = th
sim = S.Simulation(build_grid(level), seed, Params(run_end=end, **sets), 2.0)
prev = {}
for t in range(20, int(end) + 1, 20):
    c_start = sim.w_cont.sum()
    sim.run(float(t))
    cont = sim.w_cont
    thick = sim.w_thick[cont]
    d = {k[:9]: round(v - prev.get(k, 0.0), 1) for k, v in area.items()}
    prev = dict(area)
    tot = (cont.sum() - c_start) / sim.scale**2
    thin = (thick < 20).mean() * 100
    vol = float((sim.w_thick * cont).mean())
    print(f"t={t} cont%={100*cont.mean():.1f} tgt%={100*sim.target_fraction():.1f} thick={thick.mean():.2f} "
          f"vol/tgt={vol/(sim.target_fraction()*sim.params.continental_thickness):.3f} thin<20%={thin:.1f} "
          f"thermo={np.round(sim.thermo,3).tolist()} gain={shr[-1][0]:.2f} shrink={shr[-1][1]:.2f} dA={tot:.1f} {d}",
          flush=True)
    print("   vol budget (1e3 km x L5 cells, cumulative):", {k: round(v / 1e3, 1) for k, v in sim.budget.items()}, flush=True)
