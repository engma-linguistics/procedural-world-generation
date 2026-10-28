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
            # (checked on the world cells before the split; the plate's own
            # grid doesn't map onto them one to one, so allow a few cells)
            assert x <= 0.1 * p + 3 / s.grid.n or x >= 0.95 * p, pieces


def test_triple_junction_splits_a_plate_three_or_two_ways():
    """PW-952: a plume-centred rift cracks a big plate into three pieces
    around the plume (two if one arm fails), each a real share of the plate
    and none with a continental sliver; the pieces meet near the plume."""
    s = Simulation(build_grid(5), 1, Params(), 2.0)
    g = s.grid
    k = int(np.argmax(np.bincount(s.owner, minlength=events.P_MAX)))
    on = s.owner == k
    cells = np.flatnonzero(on & s.w_cont)
    c = g.centers[cells].mean(0)
    c = g.centers[cells[np.argmax(g.centers[cells] @ c)]]  # a continental cell near the plate's continent's centre
    for failed, want in ((np.zeros(3, bool), 3), (np.array([False, True, False]), 2)):
        t = Simulation(build_grid(5), 1, Params(), 2.0)
        n0 = t.plates.alive.sum()
        ok = any(events.triple_split(t, k, c, failed, np.random.default_rng(i)) for i in range(6))
        assert ok
        assert t.plates.alive.sum() == n0 + want - 1
        pieces = list(np.unique(t.owner[on]))
        assert len(pieces) == want, pieces
        lo, hi = 0.1 * t.params.rift_min_piece * g.n, t.params.rift_min_piece * g.n
        for j in pieces:
            assert ((t.owner == j) & on).sum() >= 0.1 * on.sum() - 3
            x = ((t.owner == j) & on & t.w_cont).sum()
            # (judged on the world cells before the split; allow a few cells)
            assert x <= lo + 3 or x >= 0.95 * hi, (j, x)
        # every piece reaches to within a few cells of the plume
        near = g.centers @ c > np.cos(4 * g.spacing)
        assert set(np.unique(t.owner[near & on])) == set(pieces)


def test_piece_rule():
    s = Simulation(build_grid(4), 1, Params(rift_min_piece=0.03), 2.0)
    n = s.grid.n
    assert events.piece_ok(s, 0, 0.5 * n)
    assert events.piece_ok(s, 0.05 * n, 0.04 * n)
    assert not events.piece_ok(s, 0.01 * n, 0.3 * n)


def test_margin_subduction_breaks_off_one_basin():
    """When old floor starts to sink at a passive margin, what breaks off is
    the ocean in front of that stretch of margin, not the plate's whole
    ocean (which wraps around every continent on it), and the islands in
    it go along instead of being left as holes in the new plate."""
    s = Simulation(build_grid(5), 1, Params(), 2.0)
    g = s.grid
    cont = np.bincount(s.owner, weights=s.w_cont, minlength=events.P_MAX)
    k = int(np.argmax(cont))
    on = s.owner == k
    s.w_age = np.where(s.w_cont, s.w_age, 300.0)  # every margin old
    refs = np.flatnonzero(s.plates.owned[k])
    world = g.centers[refs] @ s.plates.Q[k].T
    side, trench = events.margin_side(s, k, world)
    wside = np.zeros(g.n, bool)
    wside[g.locate(world[side])] = True
    wside &= on
    ocean = on & ~s.w_cont
    assert trench.any() and (trench <= ocean).all()
    assert 0.02 * ocean.sum() < wside.sum() < 0.8 * ocean.sum()
    # the old plate keeps no small pieces stranded inside the new one
    rest, _ = g.components(on & ~wside)
    sizes = np.bincount(rest[rest >= 0])
    for j in np.flatnonzero(sizes < 0.1 * s.params.rift_min_piece * g.n):
        nb = g.nbr_idx[np.isin(np.repeat(np.arange(g.n), np.diff(g.nbr_off)), np.flatnonzero(rest == j))]
        assert not (wside | (rest == j))[nb].all(), j


def _column(s):
    from planet.tectonics.crust import Column
    return Column(t=s.w_thick.copy(), cover=s.w_cover.copy(), x=s.w_extra.copy(), cont=s.w_cont.copy(),
                  rock=s.w_rock.copy(), rec=s.w_rec.copy(), lith=s.w_lith.copy())


def test_crust_being_stacked_is_not_rifted():
    """PW-172: a collision belt cell next to an opening edge was stretched and
    dated as rifting on every step while the collision stacked it back up,
    so its rift strain (and thermal uplift) grew without the crust thinning.
    Crust being stacked this step is shortening: not thinned, not dated."""
    from planet.tectonics import crust, record
    s = Simulation(build_grid(4), 1, Params(), 2.0)
    col = _column(s)
    n = s.grid.n
    stack = np.where(np.arange(n) % 2 == 0, 1.0, 0.0)  # km stacked this step on every other cell
    t0, rift0 = col.t.copy(), col.rec[:, record.T_RIFT].copy()
    crust.stretch(s, col, np.full(n, 0.05), np.zeros(n), np.zeros(n, bool), stack_add=stack)
    thin = s.w_cont & (t0 * np.exp(-0.05 * s.dt) > 22)  # (room to thin a whole step above stretch's 22 km floor)
    squeezed, free = thin & (stack > 0), thin & (stack == 0)
    assert squeezed.any() and free.any()
    assert np.array_equal(col.t[squeezed], t0[squeezed])
    assert np.array_equal(col.rec[squeezed, record.T_RIFT], rift0[squeezed])
    assert (col.t[free] < t0[free]).all() and (col.rec[free, record.T_RIFT] == s.t).all()


def test_rift_pool_decays_into_its_flanks():
    """PW-287: the stretched crust a rift never takes up goes back into the
    plate's rifted continent (none rifted: all of it), not out of the world."""
    from planet.tectonics import crust, record
    s = Simulation(build_grid(4), 1, Params(), 2.0)
    col = _column(s)
    k = int(np.argmax(np.bincount(s.owner, s.w_cont)))
    on = (s.owner == k) & col.cont
    rifted = on & (np.arange(s.grid.n) % 3 == 0)
    col.rec[:, record.T_RIFT] = np.where(rifted, s.t, record.NEVER)
    s.plates.rift_pool[:] = 0.0
    s.plates.rift_pool[k] = 50.0
    t0 = col.t.copy()
    crust.flanks(s, col, col.cont)
    back = 50.0 - s.plates.rift_pool[k]
    assert back > 0
    assert np.isclose((col.t - t0).sum(), back)
    assert np.allclose((col.t - t0)[rifted], back / rifted.sum()) and (col.t == t0)[~rifted].all()
