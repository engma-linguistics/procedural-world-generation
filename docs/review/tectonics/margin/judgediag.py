"""PW-1726 (lane 310): margindiag.py (ice_diag + the margin numbers every 50 Myr) with flickdiag.py's flicker tags, for
the shred-gap judge. Every 50 Myr step's `margin` record also gets `plates` (plates owning cells) and `flick`: the
running counts since FLICK_WIN0 (env, default 100 Myr) in L5-equivalent cells (cells / scale^2) of shreds, quick
shreds (<= 10 Myr after a birth or weld of the same crust), births, quick births (<= 10 Myr after a shred), welds,
and the summed km of the quick shreds. Any window's counts are the difference of two records.
Same arguments as ice_diag / margindiag; run from the code checkout being judged (cwd). Reads the sim, changes nothing.
Harness only."""
import os
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet.tectonics import crust, diag  # noqa: E402

WIN0 = float(os.environ.get("FLICK_WIN0") or 100.0)
C = {"shred": 0.0, "shred_q": 0.0, "shred_q_km": 0.0, "birth": 0.0, "birth_q": 0.0, "weld": 0.0}
TAGS = {}
_coh, _birth = crust.coherence, crust.birth_and_cratons


def _tag(sim, cells, other, mine, kq, k):
    """flickdiag._tag: tag the cells' crust (on the plate's own grid) with this event's time; count it in the window."""
    pl = sim.plates
    if "up" not in TAGS or TAGS["up"].shape != pl.cont.shape:
        old = dict(TAGS)
        TAGS["up"] = np.full(pl.cont.shape, -np.inf)
        TAGS["down"] = np.full(pl.cont.shape, -np.inf)
        for key in ("up", "down"):  # plate arrays can grow (new plates); keep the tags of the old rows
            if key in old:
                a = old[key]
                s = tuple(slice(0, min(x, y)) for x, y in zip(a.shape, pl.cont.shape))
                TAGS[key][s] = a[s]
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
_step = diag.Recorder.step


def step(self, sim):
    """The recorder's step, plus `plates` and `flick` on the 50 Myr steps margindiag adds `margin` to."""
    _step(self, sim)
    t = float(sim.t)
    if t < 100 or abs(t / 50 - round(t / 50)) > 1e-6:
        return
    self.steps[-1]["plates"] = int(len(np.unique(sim.owner)))
    self.steps[-1]["flick"] = {k: round(v, 3) for k, v in C.items()}


diag.Recorder.step = step
# margindiag wraps this step with its margin numbers and runs ice_diag as __main__ with this process's arguments
runpy.run_path(str(Path.cwd() / "docs" / "review" / "tectonics" / "margin" / "margindiag.py"), run_name="margindiag_lib")
