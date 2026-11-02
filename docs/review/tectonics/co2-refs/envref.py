"""Lane 135 (PW-1316): lane 115's envdraw.py world (tests/test_envelopes.py's fixture: L5, Params(run_end=400), dt 2,
0-100 Myr in one call then 4 Myr chunks) for one seed, with the CO2 source/sink and their references traced every
4 Myr from 100 Myr. Run from a frozen code copy (cwd = that copy), so main and the candidate run their own code.
usage: (cd CODE && NUMBA_NUM_THREADS=1 PY envref.py SEED OUT.json)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402

seed, out = int(sys.argv[1]), sys.argv[2]
sim = Simulation(build_grid(5), seed, Params(run_end=400.0), 2.0)
trace = []


def sample():
    r = {"t": round(float(sim.t), 1), "dT": round(float(sim.dT), 3), "pco2": round(float(climate.pco2(sim.co2)), 1),
         "land": round(100 * float((sim.w_elev > 0).mean()), 2)}
    if sim.rates is not None:
        r["src"], r["sink"] = [float(v) for v in sim.rates]
    if sim.refs is not None:
        r["src_ref"], r["sink_ref"] = [float(v) for v in sim.refs]
    trace.append(r)


sim.run(100.0)
sample()
for t in range(100, 401, 20):
    while sim.t < t - 1e-9:
        sim.run(sim.t + 4)
        sample()
st = sim.stats()
end = {"T": float(st["global_temp_c"]), "pco2": float(climate.pco2(sim.co2))}
Path(out).write_text(json.dumps({"seed": seed, "end": end, "trace": trace}))
print(seed, end, flush=True)
