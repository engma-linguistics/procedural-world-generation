"""cProfile of N steps of a run from a checkpoint, bucketed: numba kernels (by dispatcher), numpy C
calls visible to cProfile, numpy Python wrappers, planet Python functions (tottime: interpreter +
inline numpy operators), other. python cprof2.py RUN AT STEPS"""
import os, sys, cProfile, pstats, time
sys.path.insert(0, os.path.dirname(__file__)); import env  # noqa
from collections import defaultdict
from numba.core.registry import CPUDispatcher
import importlib, pkgutil
from planet import timeline as T
import planet

run, at, steps = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
kern = set()
for m in pkgutil.walk_packages(planet.__path__, "planet."):
    if m.name in ("planet.server", "planet.__main__"):
        continue
    mod = importlib.import_module(m.name)
    for v in vars(mod).values():
        if isinstance(v, CPUDispatcher):
            c = v.py_func.__code__
            kern.add((c.co_filename, c.co_firstlineno, c.co_name))
sim = T.replay(T.find_run(run), at)
sim.step(); sim.step()
pr = cProfile.Profile()
t0 = time.perf_counter()
pr.enable()
for _ in range(steps):
    sim.step()
pr.disable()
wall = time.perf_counter() - t0
st = pstats.Stats(pr).stats
b = defaultdict(lambda: [0.0, 0])
top = defaultdict(list)
for (f, ln, name), (cc, nc, tt, ct, callers) in st.items():
    if (f, ln, name) in kern:
        k = "numba kernels (dispatcher calls)"
    elif f == "~" and ("numpy" in name or "ufunc" in name or "ndarray" in name):
        k = "numpy C calls visible to cProfile (np.where, .sum(), reduceat, ...)"
    elif f == "~":
        k = "other builtins"
    elif "/numpy/" in f:
        k = "numpy Python wrappers (np.clip, np.sum, ... python layer)"
    elif "/planet/" in f:
        k = "planet Python functions (interpreter + inline numpy operators)"
    else:
        k = "other python (stdlib, numba dispatch)"
    b[k][0] += tt
    b[k][1] += nc
    top[k].append((tt, nc, f"{os.path.basename(f)}:{name}"))
tot = sum(v[0] for v in b.values())
print(f"{steps} steps from t={at}: wall {wall:.1f}s (profiled), tottime sum {tot:.1f}s")
for k, (tt, nc) in sorted(b.items(), key=lambda x: -x[1][0]):
    print(f"  {k:<72s} {tt:7.2f}s {100 * tt / tot:5.1f}%  calls/step {nc / steps:9.0f}")
    for tt2, nc2, nm in sorted(top[k], reverse=True)[:8]:
        print(f"      {nm:<60s} {tt2:6.2f}s  calls/step {nc2 / steps:7.0f}")
