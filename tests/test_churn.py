"""Crust-type coherence and cell churn (PW-108): one-cell inlets and shreds
of crust, carried past the world grid by the plates, showed as cells
flipping between continent and deep sea every few Myr."""

import numpy as np

from planet.grid import build_grid
from planet.tectonics import Params, Simulation, crust
from planet.tectonics.crust import Column


def _column(sim):
    return Column(t=sim.w_thick.copy(), cover=sim.w_cover.copy(), x=sim.w_extra.copy(), cont=sim.w_cont.copy(),
                  rock=sim.w_rock.copy(), rec=sim.w_rec.copy(), lith=sim.w_lith.copy())


def _interior(sim, cont):
    """A cell whose neighbours are all on its plate and all of crust type `cont`."""
    g = sim.grid
    for i in np.random.default_rng(0).permutation(g.n):
        nb = g.neighbors[i]
        if (sim.owner[nb] == sim.owner[i]).all() and (sim.w_cont[nb] == cont).all() and sim.w_cont[i] == cont:
            return i
    raise AssertionError("no interior cell")


def test_coherence_welds_inlets_and_drops_thin_shreds():
    sim = Simulation(build_grid(5), 3, Params(), 2.0)
    col = _column(sim)
    hole = _interior(sim, True)  # a one-cell hole of ocean floor in a continent
    col.cont[hole], col.t[hole] = False, 7.0
    shred = _interior(sim, False)  # a thin shred of continent in the ocean
    col.cont[shred], col.t[shred] = True, 15.0
    isle = shred
    for c in np.random.default_rng(1).permutation(sim.grid.n):
        if c != shred and c not in sim.grid.neighbors[shred] and not sim.w_cont[c] and \
                (sim.owner[sim.grid.neighbors[c]] == sim.owner[c]).all() and not sim.w_cont[sim.grid.neighbors[c]].any():
            isle = c  # a thick one: an island (an arc, a microcontinent) stays
            break
    col.cont[isle], col.t[isle] = True, 30.0
    t0 = col.t.copy()
    weld, drop = crust.coherence(sim, col)
    assert col.cont[hole] and weld[hole]
    assert not col.cont[shred] and drop[shred]
    assert col.cont[isle]
    assert col.t[hole] > 20  # crust flowed in from around it...
    assert abs(col.t.sum() - t0.sum()) < 1e-6  # ...volume kept
    assert col.t[shred] == 15.0 and col.t[isle] == 30.0
    assert weld.sum() + drop.sum() <= 20  # and only on one-cell features


def test_churn_metric_flags_a_flip_back():
    from tools.churn import churn
    g = build_grid(3)
    n = g.n
    base = {"cont": np.ones(n, bool), "plate": np.zeros(n, int), "elev": np.full(n, 500.0),
            "boundary": np.zeros(n, np.int8)}
    flip = {**base, "cont": base["cont"].copy(), "elev": base["elev"].copy()}
    flip["cont"][:10] = False
    flip["elev"][:10] = -4000
    c = churn(g, [base, flip, base])
    assert abs(c["crust"] - 100 * 10 / n) < 1e-2
    assert c["relief"] > 0 and c["plate"] == 0


def test_sediment_piles_are_born_continental_only_against_their_continent():
    """PW-1292: a sediment pile on the ocean floor, however thick, is sediment on
    oceanic crust; it joins a continent only as a margin wedge against
    continental crust of its own plate. An isolated arc of the same thickness is
    still born continental."""
    from planet.surface import SEDIMENT
    sim = Simulation(build_grid(5), 3, Params(), 2.0)
    g, own = sim.grid, sim.owner
    col = _column(sim)
    alone = [c for c in np.random.default_rng(2).permutation(g.n) if not sim.w_cont[c] and
             (own[g.neighbors[c]] == own[c]).all() and not sim.w_cont[g.neighbors[c]].any()]
    pile, arc = alone[0], next(c for c in alone[1:] if c not in g.neighbors[alone[0]])
    wedge = next(c for c in np.random.default_rng(3).permutation(g.n) if not sim.w_cont[c] and
                 (sim.w_cont[g.neighbors[c]] & (own[g.neighbors[c]] == own[c])).any())
    for c in (pile, wedge):
        col.t[c], col.cover[c] = 25.0, 16.0  # (mostly sediment)
    col.t[arc], col.cover[arc] = 25.0, 0.0
    no = np.zeros(g.n, bool)
    born = crust.birth_and_cratons(sim, col, no, no)
    assert not born[pile]
    assert born[wedge] and col.rock[wedge] == SEDIMENT
    assert born[arc]
