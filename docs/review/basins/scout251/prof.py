"""prof.py CODE CKPT: continue the L7 seed-11 state 6 Myr with CODE, capture the erosion step's hydrology.lakes
arguments, then profile that call (5 repeats)."""
import cProfile
import pickle
import pstats
import sys
import time
import zlib
from pathlib import Path

code, ck = sys.argv[1], sys.argv[2]
sys.path.insert(0, str(Path(code).resolve()))
import planet  # noqa
from planet.grid import build_grid
from planet.tectonics import Params, Simulation
from planet import hydrology as Hy

state = pickle.loads(zlib.decompress(Path(ck).read_bytes()))
for n in Simulation.STATE:
    state.setdefault(n, None)
sim = Simulation.from_state(build_grid(7), 11, Params(run_end=400.0), 2.0, state)
cap = {}
f0 = Hy.lakes


def lakes(*a, **k):
    cap.setdefault("n", []).append(k.get("pet_mm") is not None)
    if k.get("pet_mm") is not None:
        cap["a"], cap["k"] = a, k
    return f0(*a, **k)


Hy.lakes = lakes
sim.run(sim.t + 12.0)
print(cap["n"])
Hy.lakes = f0
a, k = cap["a"], cap["k"]
for pet in (None, k["pet_mm"]):
    kk = {**k, "pet_mm": pet}
    f0(*a, **kk)
    t = time.time()
    for _ in range(3):
        f0(*a, **kk)
    print(f"pet {'on' if pet is not None else 'off'}: {(time.time() - t) / 3:.3f} s per call", flush=True)
pr = cProfile.Profile()
pr.enable()
for _ in range(3):
    f0(*a, **k)
pr.disable()
pstats.Stats(pr).sort_stats("cumulative").print_stats(25)
