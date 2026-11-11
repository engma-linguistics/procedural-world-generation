"""PW-1295 round 3 (lane 302): the margin flicker counted cheaply on any world. envdraw.py's world (test_envelopes'
fixture at L5: Params(run_end=END), dt 2, 0-100 Myr in one call then 4 Myr chunks) at any level and length, with
tracediag.py's flicker tags (lane 115): every birth, weld and shred tagged on the plate's own grid; at each event in the
window, the Myr since that cell's last event of the other way. Harness only: reads the sim, changes nothing.
usage: flickdiag.py SEED LEVEL END OUT.json [k=v ...]   (k=v: Params fields, e.g. neck_km=200 rise=1 slope_k=1000)
Window: from WIN0 (env FLICK_WIN0, default 100 Myr) to the end. Counts in cells / scale^2 (L5-equivalent cells):
shreds, quick shreds (<= 10 Myr after a birth or weld of the same crust), births (arc + pile), quick births (<= 10 Myr
after a shred), welds; the mean thickness of the quick shreds. End: T, pCO2, land, cont, thick, plates; the late
(last quarter) means of dT and land."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation, crust  # noqa: E402

seed, level, end_t, out = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
over = {}
for kv in sys.argv[5:]:
    k, v = kv.split("=")
    over[k] = float(v)
WIN0 = float(os.environ.get("FLICK_WIN0") or 100.0)
C = {"shred": 0.0, "shred_q": 0.0, "shred_q_km": 0.0, "birth": 0.0, "birth_q": 0.0, "weld": 0.0}
TAGS = {}
_coh, _birth = crust.coherence, crust.birth_and_cratons


def _tag(sim, cells, other, mine, kq, k):
    pl = sim.plates
    if not TAGS:
        TAGS["up"] = np.full(pl.cont.shape, -np.inf)
        TAGS["down"] = np.full(pl.cont.shape, -np.inf)
    c = np.flatnonzero(cells)
    if not len(c):
        return np.zeros(0)
    kk = sim.owner[c]
    r = pl.idx[kk, c]
    d = float(sim.t) - TAGS[other][kk, r]
    TAGS[mine][kk, r] = float(sim.t)
    if sim.t >= WIN0:
        w = 1.0 / sim.scale**2
        C[k] += len(c) * w
        if kq:
            C[kq] += int((d <= 10.0).sum()) * w
    return d


def coherence(sim, col, trench=None):
    weld, shred = _coh(sim, col, trench)
    d = _tag(sim, shred, "up", "down", "shred_q", "shred")
    if sim.t >= WIN0 and len(d):
        C["shred_q_km"] += float(col.t[np.flatnonzero(shred)][d <= 10.0].sum()) / sim.scale**2
    _tag(sim, weld, "down", "up", None, "weld")
    return weld, shred


def birth_and_cratons(sim, col, arcky, squeezed):
    born = _birth(sim, col, arcky, squeezed)
    _tag(sim, born, "down", "up", "birth_q", "birth")
    return born


crust.coherence, crust.birth_and_cratons = coherence, birth_and_cratons
p = Params(run_end=end_t)
for k, v in over.items():
    if not hasattr(p, k):
        raise SystemExit(f"no Params field {k}")
    setattr(p, k, type(getattr(p, k))(v))
sim = Simulation(build_grid(level), seed, p, 2.0)
late = []
sim.run(min(100.0, end_t))
while sim.t < end_t - 1e-9:
    sim.run(min(sim.t + 4, end_t))
    if sim.t >= 0.75 * end_t:
        late.append((float(sim.dT), 100 * float((sim.w_elev > 0).mean())))
st = sim.stats()
res = {k: round(float(v), 2) for k, v in C.items()}
res["quick_km"] = round(C["shred_q_km"] / max(C["shred_q"], 1e-9), 2)
del res["shred_q_km"]
res.update(T=round(float(st["global_temp_c"]), 2), pco2=round(float(climate.pco2(sim.co2)), 1),
           land=round(100 * float((sim.w_elev > 0).mean()), 2), cont=round(100 * float(sim.w_cont.mean()), 2),
           thick=round(float(sim.w_thick[sim.w_cont].mean()), 2), plates=int(len(np.unique(sim.owner))),
           late_dT=round(float(np.mean([a for a, _ in late])), 2), late_land=round(float(np.mean([b for _, b in late])), 2))
Path(out).write_text(json.dumps({"seed": seed, "level": level, "end": end_t, "set": over, "win0": WIN0, "res": res}))
print(seed, level, end_t, over, res, flush=True)
