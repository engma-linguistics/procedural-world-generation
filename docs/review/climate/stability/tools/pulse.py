"""Lane 158: the thermostat's compensation and recovery, measured. Continues a lane 144 fork state (300 Myr, code
l144/code/main = 4abc1707, the same code, so the run equals lane 144's fm bit for bit until the pulse) and adds F C
to climate_offset from T0 to T1 Myr (a lasting push on the climate, as a dimmer star would be), then removes it.
Writes OUT/seed<S>_L6.json.gz in tools/ice_diag.py's layout. Nothing under planet/ is changed.
usage: pulse.py CODE_DIR FORK_BASE OUT_DIR F T0 T1"""
import gzip, json, pickle, sys, time, zlib
from pathlib import Path

code, base, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
F, T0, T1 = (float(x) for x in sys.argv[4:7])
sys.path.insert(0, str(Path(code).resolve()))
import planet  # noqa: F401,E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402
from planet.tectonics.diag import Recorder  # noqa: E402

meta = json.loads(gzip.open(f"{base}.json.gz", "rt").read())
state = pickle.loads(zlib.decompress(Path(f"{base}.ckpt").read_bytes()))
grid = build_grid(meta["level"])
sim = Simulation.from_state(grid, meta["seed"], Params(**meta["params"]), meta["dt"], state)
rec = Recorder()
rec.steps, rec.updates = meta["steps"], meta["updates"]
sim.diag = rec
off0, t0 = sim.params.climate_offset, time.time()


def on_step(s):
    # (the push for the NEXT step: global_temperature reads params.climate_offset inside the step)
    s.params.climate_offset = off0 + (F if T0 - 1e-9 <= s.t < T1 - 1e-9 else 0.0)
    s.diag.step(s)
    if int(s.t) % 50 == 0 and abs(s.t - round(s.t)) < 1e-9:
        print(f"  {s.t:g} Myr {time.time() - t0:.0f} s dT {s.dT:+.2f} offset {s.params.climate_offset:+.4f}", flush=True)


sim.run(meta["myr"], on_step)
out.mkdir(parents=True, exist_ok=True)
d = {"seed": meta["seed"], "myr": meta["myr"], "level": meta["level"], "params": meta["params"],
     "pulse": {"F": F, "T0": T0, "T1": T1}, "seconds": round(time.time() - t0), **rec.as_dict()}
with gzip.open(out / f"seed{meta['seed']}_L6.json.gz", "wt") as f:
    json.dump(d, f)
print("done", out)
