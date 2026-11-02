"""The same seed gives the same world at any numba thread count (PW-1324). A parallel kernel that
sums in thread-chunk order would make runs differ between machines and --threads settings."""

import dataclasses
import hashlib

import numba
import numpy as np

from helpers import run_sim


def _digest(sim) -> dict:
    snap = sim.snapshot()
    out = {}
    for f in dataclasses.fields(snap):
        v = getattr(snap, f.name)
        try:
            a = np.ascontiguousarray(np.asarray(v))
            out[f.name] = hashlib.md5(a.tobytes()).hexdigest() if a.dtype != object else repr(v)
        except (ValueError, TypeError):
            out[f.name] = repr(v)
    return out


def test_one_and_many_threads_give_identical_state():
    top = numba.get_num_threads()
    assert top >= 2, "needs NUMBA_NUM_THREADS >= 2 to compare thread counts"
    try:
        numba.set_num_threads(1)
        one = _digest(run_sim(level=4, seed=1, myr=100.0))
        numba.set_num_threads(top)
        many = _digest(run_sim(level=4, seed=1, myr=100.0))
    finally:
        numba.set_num_threads(top)
    assert [k for k in one if one[k] != many[k]] == []
