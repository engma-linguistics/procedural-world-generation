"""python run_misc.py OUT.json slice RUN AT | zoom WORLD LAT LON RES SIZE | timezoom RUN AT KYR | finish TZ KYR
Timed with the monkeypatched timers (each job runs twice in one process: the first warms caches, the
second is recorded) unless --once."""
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__)); import env  # noqa
import numba
import timers
once = "--once" in sys.argv
argv = [a for a in sys.argv[1:] if a != "--once"]
timers.install()
from planet import timeline as T, zoom as Z, timezoom as TZ, finish as F, store as S
out, what, *a = argv


def job():
    if what == "slice":
        return T.slice_world(T.find_run(a[0]), float(a[1]), force=True)
    if what == "zoom":
        return Z.zoom(a[0], float(a[1]), float(a[2]), float(a[4]), float(a[3]), 1, 15, log=lambda *x: None)
    if what == "timezoom":
        return TZ.timezoom(a[0], float(a[1]), float(a[2]), progress=False)
    if what == "finish":
        return F.finish_timezoom(a[0], float(a[1]))


made = []
if not once:
    made.append(job())
    timers.reset()
load0 = os.getloadavg()
t0 = time.perf_counter()
made.append(job())
wall = time.perf_counter() - t0
print("made", [str(p) for p in made], "wall", round(wall, 2), flush=True)
timers.dump(out, wall, {"what": what, "args": a, "made": [str(p) for p in made], "load_before": load0,
                       "load_after": os.getloadavg(), "threads": numba.get_num_threads()})
