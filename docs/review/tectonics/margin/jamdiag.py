"""PW-1317 (lane 119): do kept thin continental margins (15-20 km) jam trenches? envdraw.py's world (the
test_envelopes fixture: L5, Params(run_end=400), dt 2, 0-100 Myr in one call then 4 Myr chunks) for one seed and
shred bound to END Myr, counting every step at motion.boundaries (edges or cells / scale^2):
- sub_n, sub_conv: subducting edges and their summed convergence (cm/yr, clipped 0-15: the slab flux)
- slab: the slab pull's net force summed over them (motion.forces: slab_pull x age factor - slab_drag x conv)
- col_n, col_conv: collision edges (continent against continent) and their convergence
- col_thin, col_thin_conv: collision edges with a thin (< 20 km) continental side; col_thin15: one side 15-20 km
- sub_thin_over: subducting edges whose overriding cell is thin continent (a thin margin taking the other plate's
  ocean floor under it: the polarity it gets as continent)
- thin: thin continental cells (< 20 km), % of the surface; thin_edge: of them, those on a closing plate edge;
  plates: live plates; open_n: opening (spreading) edges; bnd_n: all plate-boundary edges; cont: continental crust %
  of the surface; events (end): sim.events as (t, kind)
- ridge and arc (the CO2 source's parts, as envdraw.py); speed: mean plate speed (cm/yr) every 20 Myr from 100 Myr
- tries, veto, cut_ok: the rifts' stress cuts (below); screens JAM_THICK_PIECE, JAM_THICK_DYN (below)
usage: jamdiag.py SEED SHRED_KM END OUT.json   (run from the checkout). Harness only. Needs crust.SHRED_KM (the 15 km
shred bound, d143c2bc on lane 115's branch; reverted on main): without it the bound argument does nothing.
Notes: docs/review/tectonics/margin/pw1295-note.md section 5."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation, crust, earth, motion  # noqa: E402

seed, shred, end, out = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
assert hasattr(crust, "SHRED_KM"), "needs the 15 km shred bound's code (crust.SHRED_KM)"
crust.SHRED_KM = shred
TRACE = []  # (one dict per step, filled at motion.boundaries)
SPEED = {}
_bd, _gt = motion.boundaries, earth.global_temperature
# (the rifts' stress cuts: per step, trial cuts tried, of them refused by events.piece_ok (a continental sliver on a
# side), and plates whose best admissible cut opens faster than rift_stress (cut_ok). Env JAM_THICK_PIECE=1, a
# counterfactual screen: stress_cut sees only crust >= 20 km as continent (piece_ok's slivers and strength()), so
# kept thin margins can't veto a cut)
from planet.tectonics import events  # noqa: E402
_sc, _po = events.stress_cut, events.piece_ok
CUTS = {"tries": 0, "veto": 0, "cut_ok": 0}
THICK_PIECE = bool(os.environ.get("JAM_THICK_PIECE"))


def piece_ok(sim, a, b):
    o = _po(sim, a, b)
    CUTS["tries"] += 1
    CUTS["veto"] += not o
    return o


def stress_cut(sim, k, cf, rng, tries=12):
    if THICK_PIECE:
        c0 = sim.w_cont
        sim.w_cont = c0 & (sim.w_thick >= 20.0)
        try:
            o = _sc(sim, k, cf, rng, tries)
        finally:
            sim.w_cont = c0
    else:
        o = _sc(sim, k, cf, rng, tries)
    CUTS["cut_ok"] += o[2] > sim.params.rift_stress
    return o


events.stress_cut, events.piece_ok = stress_cut, piece_ok
# (Env JAM_THICK_DYN=1, a second counterfactual screen: the plates' force balance (motion.forces: the continental
# keel's drag and mantle.traction's coupling) and the mantle's insulation (mantle.update) see only crust >= 20 km as
# continent, so the kept thin margins drive the plates and the mantle as the 20 km bound's ocean floor did)
from planet.tectonics import mantle  # noqa: E402
if os.environ.get("JAM_THICK_DYN"):
    def _thick(f):
        def w(sim, *a):
            c0 = sim.w_cont
            sim.w_cont = c0 & (sim.w_thick >= 20.0)
            try:
                return f(sim, *a)
            finally:
                sim.w_cont = c0
        return w
    # (=keel: the force balance only; =mantle: the insulation only; anything else: both)
    if os.environ["JAM_THICK_DYN"] != "mantle":
        motion.forces = _thick(motion.forces)
    if os.environ["JAM_THICK_DYN"] != "keel":
        mantle.update = _thick(mantle.update)


def boundaries(sim):
    bd = _bd(sim)
    if TRACE:
        TRACE[-1].update(CUTS)
    CUTS.update(tries=0, veto=0, cut_ok=0)
    k = 1.0 / sim.scale**2
    p = sim.params
    conv = np.clip(bd.conv, 0, 15)
    t, c = sim.w_thick, sim.w_cont
    thin = c & (t < 20.0)
    thin15 = thin & (t >= 15.0)
    dn, up = bd.sinking, bd.overriding
    cv = bd.at_trenches(conv)
    slab = (p.slab_pull * np.clip(sim.w_age[dn] / 80, 0.3, 1.5) - p.slab_drag * cv)
    col = bd.collision
    ct = col & (thin[bd.a] | thin[bd.b])
    ct15 = col & (thin15[bd.a] | thin15[bd.b])
    closing = bd.conv > 0.5
    edge = np.zeros(sim.grid.n, bool)
    edge[bd.a[closing]] = edge[bd.b[closing]] = True
    TRACE.append(dict(t=round(float(sim.t), 1), sub_n=len(dn) * k, sub_conv=float(cv.sum()) * k,
                      slab=float(slab.sum()) * k, col_n=int(col.sum()) * k, col_conv=float(conv[col].sum()) * k,
                      col_thin=int(ct.sum()) * k, col_thin_conv=float(conv[ct].sum()) * k,
                      col_thin15=int(ct15.sum()) * k, sub_thin_over=int(thin[up].sum()) * k,
                      thin=100 * float(thin.mean()), thin_edge=int((thin & edge).sum()) * k,
                      plates=int(sim.plates.alive.sum()), open_n=int(bd.opening.sum()) * k, bnd_n=len(bd.a) * k,
                      cont=100 * float(c.mean())))
    return bd


def global_temperature(sim, growth, newc, rng, plume=None):
    o = _gt(sim, growth, newc, rng, plume=plume)
    if TRACE:
        TRACE[-1]["ridge"] = newc * (sim.dt / sim.dt_now) / sim.scale**2
        TRACE[-1]["arc"] = 20.0 * float(growth.sum()) / sim.scale**2
    return o


motion.boundaries, earth.global_temperature = boundaries, global_temperature
sim = Simulation(build_grid(5), seed, Params(run_end=400.0), 2.0)
sim.run(min(100.0, end))  # (envdraw.py's chunks: 0-100 Myr in one call, then 4 Myr)
while sim.t < end - 1e-9:
    sim.run(sim.t + 4)
    if int(round(sim.t)) % 20 == 0:
        SPEED[round(float(sim.t), 1)] = round(float(sim.stats()["mean_speed_cmyr"]), 3)
trace = [{k: (round(float(v), 3) if k != "t" else v) for k, v in r.items()} for r in TRACE]
ev = [(round(float(e.t), 1), e.kind) for e in sim.events]
Path(out).write_text(json.dumps({"seed": seed, "shred_km": shred, "speed": SPEED, "trace": trace, "events": ev}))
print(seed, shred, "done", flush=True)
