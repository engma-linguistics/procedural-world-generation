"""Simulation.state() holds everything a run needs to continue: resuming
from it must give exactly the run that never stopped (the basis for
checkpoints)."""

from dataclasses import fields

import numpy as np

from planet.tectonics import Simulation

from helpers import run_sim
from test_golden import sim_digest


def test_resume_from_state_is_bit_identical():
    a = run_sim(level=4, seed=2, myr=30)  # mid-way between climate updates
    st = a.state()
    snap = a.snapshot()
    a.run(50)
    b = Simulation.from_state(a.grid, a.seed, a.params, a.dt, st)
    assert b.t == 30
    # the output-only fields (boundaries, rivers, stale climate) come back too
    snap_b = b.snapshot()
    for f in fields(snap):
        x, y = getattr(snap, f.name), getattr(snap_b, f.name)
        assert np.array_equal(x, y) if isinstance(x, np.ndarray) else x == y, f.name
    b.run(50)
    assert sim_digest(b) == sim_digest(a)
    assert [e.as_dict() for e in b.events] == [e.as_dict() for e in a.events]


def test_dead_plate_slots_cost_no_memory():
    """The plates' (P, n) crust arrays sit on mapped memory: a dead slot's
    rows are handed back (Plates.release: they read as zeros but for the
    edge pages) and the live slots' left alone, and a state put back into a
    simulation writes only the live slots' rows (Plates.mapped_copy,
    PW-1389)."""
    from planet.tectonics.plates import MAPPED, Plates
    pl = Plates.empty(20000, 8, next_label=4)
    pl.alive[:3] = True
    for name in MAPPED:
        getattr(pl, name)[:3] = 1
    pl.release(1)
    for name in MAPPED:
        arr = getattr(pl, name)
        assert (arr[0] == 1).all() and (arr[2] == 1).all(), name
        assert (arr[1] == 0).mean() > 0.5, name  # (rows of >= 20 kB: at most two edge pages kept)
    pl.alive[1] = False
    q = pl.mapped_copy()
    for name in MAPPED:
        a, b = getattr(pl, name), getattr(q, name)
        assert b.dtype == a.dtype and np.array_equal(b[pl.alive], a[pl.alive]) and not b[~pl.alive].any(), name
