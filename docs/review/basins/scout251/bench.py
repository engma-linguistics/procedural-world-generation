"""bench.py CODE CKPT SEED LEVEL MYR: continue the state MYR Myr with CODE's code (no store), time the whole and
hydrology.lakes' share (every call wrapped)."""
import pickle
import sys
import time
import zlib
from pathlib import Path

code, ck, seed, level, myr = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
sys.path.insert(0, str(Path(code).resolve()))
import planet  # noqa
from planet.grid import build_grid
from planet.tectonics import Params, Simulation
from planet import hydrology as Hy

assert Path(planet.__file__).resolve().is_relative_to(Path(code).resolve())
state = pickle.loads(zlib.decompress(Path(ck).read_bytes()))
for n in Simulation.STATE:
    state.setdefault(n, None)
sim = Simulation.from_state(build_grid(level), seed, Params(run_end=400.0), 2.0, state)
acc = {"n": 0, "s": 0.0}
f0 = Hy.lakes


def lakes(*a, **k):
    t = time.time()
    r = f0(*a, **k)
    acc["n"] += 1
    acc["s"] += time.time() - t
    return r


Hy.lakes = lakes
sim.run(sim.t + 2.0)  # (warm-up: numba caches, the first climate update)
acc.update(n=0, s=0.0)
t0 = time.time()
sim.run(sim.t + myr)
print(f"{Path(code).name}: {myr:g} Myr in {time.time() - t0:.1f} s; lakes() {acc['n']} calls, {acc['s']:.1f} s", flush=True)
