"""How continents break up (planet/tectonics/events.py): rifts never cut
off a continental sliver."""

import numpy as np

from planet.grid import build_grid
from planet.tectonics import Params, Simulation, events


def test_rifts_leave_no_continental_slivers(monkeypatch):
    """Every rift leaves each piece with either (almost) no continent or at
    least rift_min_piece of the surface of it."""
    pieces = []
    split = events.split

    def recording_split(sim, k, refs, world, side, toward):
        new = split(sim, k, refs, world, side, toward)
        if new is not None and not toward:
            pieces.append([(sim.w_cont & (sim.owner == j)).mean() for j in (k, new)])
        return new

    monkeypatch.setattr(events, "split", recording_split)
    s = Simulation(build_grid(4), 1, Params(), 2.0)
    s.run(400)
    assert len(pieces) >= 5
    p = s.params.rift_min_piece
    for a, b in pieces:
        for x in (a, b):
            assert x <= 0.1 * p + 1e-9 or x >= p - 1e-9, pieces


def test_piece_rule():
    s = Simulation(build_grid(4), 1, Params(rift_min_piece=0.03), 2.0)
    n = s.grid.n
    assert events.piece_ok(s, 0, 0.5 * n)
    assert events.piece_ok(s, 0.05 * n, 0.04 * n)
    assert not events.piece_ok(s, 0.01 * n, 0.3 * n)
