"""Multi-seed fixtures (docs/review/tests/multiseed-fixtures.md). A 300 Myr run is chaotic: any climate or
run-physics change gives another world, so a test on one seed's world passes or fails by that world's draw (PW-623,
PW-638, PW-640). These helpers run a test's unchanged per-seed assertions on a fixed list of seeds and ask that
a share of the eligible ones pass (PASS_RATE_L4 on the L4 worlds, PASS_RATE on the L5 ones; PW-643). Seeds are
chosen up front, never by outcome; a test's eligibility rule reads the world, never the asserted outcome (PW-645).

The worlds are built once per pytest session (a pickle in the session's shared temp dir, behind a lock, so xdist
workers share it) by a small process pool."""

import fcntl
import importlib
import math
import multiprocessing as mp
import os
import pickle
from concurrent.futures import ProcessPoolExecutor

PASS_RATE = 0.7  # the L5 cold-moment drift tests (main passes all of them: 7 of 7)
# The L4 tests' bar (PW-643 ruling): well below main's measured rates (~72% forest before PW-645's eligibility,
# ~69% endings, over 240 worlds), so a re-rolled draw of main itself is green; the deliberate breaks give 0-4 of 24.
PASS_RATE_L4 = 0.5
# A null re-roll for measuring a test's spread: every multi-seed run is built with climate_offset = OFFSET C (the
# same physics, another chaotic draw of the worlds; lane A21's +-0.001). 0 in the suite.
OFFSET = float(os.environ.get("PW_SEED_OFFSET", "0") or 0)
WORKERS = int(os.environ.get("PW_SEED_WORKERS", "8"))  # processes per pool (each with conftest's 4 numba threads)
SEEDS4 = tuple(range(1, 25))  # the L4 300 Myr worlds (the first 24 seeds; seed 1 is sim4's)


def _call(spec, arg):
    mod, name = spec
    return getattr(importlib.import_module(mod), name)(arg)


def pool_map(fn, args):
    """[fn(a) for a in args] in WORKERS spawned processes (fn must be a module-level function)."""
    args = list(args)
    if WORKERS <= 1 or len(args) <= 1:
        return [fn(a) for a in args]
    spec = (fn.__module__, fn.__name__)
    with ProcessPoolExecutor(min(WORKERS, len(args)), mp_context=mp.get_context("spawn")) as ex:
        return list(ex.map(_call, [spec] * len(args), args))


def shared(tmp_path_factory, key, build):
    """build() once per session, shared by the xdist workers."""
    root = tmp_path_factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        root = root.parent
    path = root / f"seeds-{key}.pkl"
    with open(root / f"seeds-{key}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.exists():
            return pickle.loads(path.read_bytes())
        value = build()
        path.write_bytes(pickle.dumps(value))
        return value


def source4(seed):
    """The time zoom's source from the L4 300 Myr run of seed (as sim4 for seed 1)."""
    from helpers import run_sim
    from planet import timezoom as Z
    return Z.source_from_sim(run_sim(seed=seed, climate_offset=OFFSET))


class Ineligible(Exception):
    """A case raises it (before any assertion) when the world lacks the test's prerequisites: that seed is left out of
    the count (PW-645: a rule need not fire where its prerequisites aren't there)."""


def _case_job(job):
    mod, name, seed, arg = job
    out = {}
    try:
        getattr(importlib.import_module(mod), name)(arg, out)
        return seed, True, out
    except Ineligible:
        return seed, None, out
    except AssertionError as e:
        msg = (str(e).splitlines() or [""])[0]
        return seed, False, dict(out, error=msg) if msg else out


def run_case(case, items):
    """case(arg, out) holds a test's unchanged assertions and records its numbers in out; run it on each
    (seed, arg) of items. Returns [(seed, passed, numbers)]; passed is None where the case raised Ineligible."""
    return pool_map(_case_job, [(case.__module__, case.__name__, s, a) for s, a in items])


def check_rate(name, rows, rate=PASS_RATE):
    """At least ceil(rate x n) of the n eligible seeds pass (rows with passed None are ineligible: listed, not
    counted); the message lists every seed's numbers."""
    def fmt(v):
        return f"{v:.3g}" if isinstance(v, float) else str(v)
    n, k = sum(p is not None for _, p, _ in rows), sum(p is True for _, p, _ in rows)
    word = {True: "pass", False: "FAIL", None: "n/a "}
    table = "\n".join(f"  seed {s:>3}: {word[p]}  " + "  ".join(f"{a}={fmt(b)}" for a, b in o.items())
                      for s, p, o in rows)
    need = math.ceil(rate * n - 1e-9)
    print(f"{name}: {k} of {n} eligible seeds pass (bar {need}; {len(rows) - n} not eligible)\n{table}")
    assert n > 0 and k >= need, f"{name}: {k} of {n} eligible seeds pass, the bar is {need} ({rate:.0%})\n{table}"
