"""PW-054 scout 251: forked runs. Code from CODE_DIR (a frozen copy); store root = $PLANET_DATA (scratch).
  fork_run.py spin CODE_DIR OUT_CKPT --seed S --level L --fork 200 --myr 400
  fork_run.py cont CODE_DIR CKPT --seed S --level L --myr 400 --offset 1e-5 --name NAME
cont continues the state with CODE_DIR's code as a stored run (timeline.simulate, keyframes every 4 Myr from the fork),
params = defaults + run_end=myr + climate_offset=offset (the re-rolled draw: a null offset after the fork only)."""
import argparse
import pickle
import sys
import time
import zlib
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("mode")
ap.add_argument("code")
ap.add_argument("path")
ap.add_argument("--seed", type=int, required=True)
ap.add_argument("--level", type=int, required=True)
ap.add_argument("--fork", type=float, default=200.0)
ap.add_argument("--myr", type=float, default=400.0)
ap.add_argument("--offset", type=float, default=0.0)
ap.add_argument("--name", default="fork")
a = ap.parse_args()
sys.path.insert(0, str(Path(a.code).resolve()))
import planet  # noqa: E402,F401
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402
from planet import timeline as T  # noqa: E402

assert Path(planet.__file__).resolve().is_relative_to(Path(a.code).resolve()), planet.__file__
grid = build_grid(a.level)
t0 = time.time()
if a.mode == "spin":
    sim = Simulation(grid, a.seed, Params(run_end=a.myr), 2.0)
    sim.run(a.fork)
    Path(a.path).write_bytes(zlib.compress(pickle.dumps(sim.state(), protocol=5), 1))
    print(f"spin s{a.seed} L{a.level} to {sim.t:g} in {time.time() - t0:.0f} s", flush=True)
else:
    state = pickle.loads(zlib.decompress(Path(a.path).read_bytes()))
    for n in Simulation.STATE:
        state.setdefault(n, None)  # (the candidate's pet: set at the next climate update)
    params = Params(run_end=a.myr, climate_offset=a.offset)
    sim = Simulation.from_state(grid, a.seed, params, 2.0, state)
    T.Simulation = lambda *args, **kw: sim
    out = T.simulate(a.seed, a.level, a.myr, 2.0, 4.0, a.name, params, checkpoint_every=0)
    print(f"cont {a.name}: {out.name} in {time.time() - t0:.0f} s", flush=True)
