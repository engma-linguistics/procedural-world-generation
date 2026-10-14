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
