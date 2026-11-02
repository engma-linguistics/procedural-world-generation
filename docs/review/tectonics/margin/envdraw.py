"""PW-1295 round 2 (lane 115): tests/test_envelopes.py's world fixture (L5, Params(run_end=400), dt 2, run to 400 Myr
in the fixture's own chunks: 0-100 in one call, then 4 Myr) for one seed and shred bound, with a trace every 4 Myr. Harness only.
usage: envdraw.py SEED SHRED_KM OUT.json   (run from the checkout; SHRED_KM sets crust.SHRED_KM, 20 = main's bound)
Trace: t, dT, pCO2 (ppm), land % (w_elev > 0), continental crust % and mean thickness (km), the CO2 source and sink
(sim.rates) and their references (sim.refs), the weathering supply on land (km x cells / scale^2), the thermostats
(sim.thermo), the source's parts (ridge, arc, plume) and the thermostats' gains (arc_gain, shrink), mean plate speed every 20 Myr (cm/yr), and the continental budget so far (sim.budget). End: sim.stats() global T, pCO2, land, cont, ice."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "tests"))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation, crust  # noqa: E402

seed, shred, out = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
from planet.tectonics import earth  # noqa: E402
STASH = {}
_gt, _th = earth.global_temperature, crust.thermostats


def global_temperature(sim, growth, newc, rng, plume=None):
    # (the CO2 source's parts this step, as tracediag.py: ridge, arc (20 x nominal growth), plume)
    o = _gt(sim, growth, newc, rng, plume=plume)
    STASH["parts"] = (newc * (sim.dt / sim.dt_now) / sim.scale**2, 20.0 * float(growth.sum()) / sim.scale**2,
                      float(sim.plume_src))
    return o


def thermostats(sim):
    o = _th(sim)
    STASH["gain"] = o
    return o


earth.global_temperature, crust.thermostats = global_temperature, thermostats
crust.SHRED_KM = shred
sim = Simulation(build_grid(5), seed, Params(run_end=400.0), 2.0)
trace = []


def sample():
    land = sim.w_elev > 0
    r = {"t": round(float(sim.t), 1), "dT": round(float(sim.dT), 3), "pco2": round(float(climate.pco2(sim.co2)), 1),
         "land": round(100 * float(land.mean()), 2), "cont": round(100 * float(sim.w_cont.mean()), 2),
         "thick": round(float(sim.w_thick[sim.w_cont].mean()), 2),
         "thin_cont": round(100 * float((sim.w_cont & (sim.w_thick < 20)).mean()), 2),
         "thermo": [round(float(v), 3) for v in np.ravel(sim.thermo)]}
    if sim.rates is not None:
        r["src"], r["sink"] = [round(float(v), 4) for v in sim.rates]
    if sim.refs is not None:
        r["src_ref"], r["sink_ref"] = [round(float(v), 4) for v in sim.refs]
    if sim.weathered is not None:
        r["supply"] = round(float((np.asarray(sim.weathered) * land).sum()) / sim.scale**2, 4)
    if sim.temp is not None:
        r["t_land"] = round(float(np.mean(sim.temp[land])), 2) if land.any() else None
    if "parts" in STASH:
        r["ridge"], r["arc"], r["plume"] = [round(float(v), 2) for v in STASH["parts"]]
        r["arc_gain"], r["shrink"] = [round(float(v), 3) for v in STASH["gain"]]
    if int(round(sim.t)) % 20 == 0:
        r["speed"] = round(float(sim.stats()["mean_speed_cmyr"]), 2)
    r["budget"] = {k: round(float(v), 1) for k, v in sim.budget.items()}
    trace.append(r)


sim.run(100.0)  # (as run_sim(myr=100): one call; chunking could change the run)
sample()
for t in range(100, 401, 20):  # (the fixture's chunks)
    while sim.t < t - 1e-9:
        sim.run(sim.t + 4)
        sample()
st = sim.stats()
end = {k: st[k] for k in ("global_temp_c", "ice_pct", "sea_level_m") if k in st}
end.update(pco2=round(float(climate.pco2(sim.co2)), 1), land=round(100 * float((sim.w_elev > 0).mean()), 2),
           cont=round(100 * float(sim.w_cont.mean()), 2), thick=round(float(sim.w_thick[sim.w_cont].mean()), 2))
Path(out).write_text(json.dumps({"seed": seed, "shred_km": shred, "end": end, "trace": trace}))
print(seed, shred, end, flush=True)
