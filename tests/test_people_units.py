"""PW-1584: the people rules that counted cells and rings are in km / km2 now, and give the old counts at L7 (so L7 output is
unchanged) while an L8 refine keeps the same physical reach (twice the rings, four times the cells)."""
from types import SimpleNamespace

import pytest

from planet.grid import build_grid
from planet.lineages import animals as AN, compose as CO, demes as DM, ladder as LA, polities as PO, trade_flow as TF
from planet.lineages.history import params as PM
from planet.lineages.seafood import cells_for, rings_for, SEA_REACH_KM
from planet.lineages.land import REACH_KM as LAND_REACH_KM

# (constant, ring/cell helper, the old L7 count, the L8 count)
RINGS = [(LA.RAID_REACH_KM, 2, 4), (LA.BARTER_REACH_KM, 1, 2), (CO.REACH_KM, 10, 20), (PM.CHAIN_KM, 4, 8),
         (PM.ARRIVAL_POCKET_KM, 3, 6), (SEA_REACH_KM, 2, 4), (LAND_REACH_KM, 1, 2)]
CELLS = [(DM.MIN_KM2, 40, 161), (DM.ADAPT_MIN_KM2, 20, 80), (AN.OVERLAP_MIN_KM2, 3, 12), (PO.SUBJECT_KM2, 3, 12)]


@pytest.fixture(scope="module")
def g7():
    return build_grid(7)


def _l8(g7):
    """An L8 grid's size and spacing without building it (its spacing measured: 30.081 km against L7's 60.161)."""
    return SimpleNamespace(n=4 * (g7.n - 2) + 2, spacing=g7.spacing * 30.081 / 60.161)


def test_rings_and_cells_give_the_old_counts_at_l7(g7):
    for km, old, _ in RINGS:
        assert rings_for(g7, km) == old, km
    for km2, old, _ in CELLS:
        assert cells_for(g7, km2) == old, km2
    assert TF.pool_hops(g7) == 1.5  # (the old POOL_HOPS)
    assert (CO.REACH_KM / rings_for(g7, CO.REACH_KM)) / CO.REACH_STEP_KM == 1.0  # (reach's decay per ring exactly as before)


def test_rings_and_cells_keep_the_physical_scale_at_l8(g7):
    g8 = _l8(g7)
    for km, _, l8 in RINGS:
        assert rings_for(g8, km) == l8, km
    for km2, _, l8 in CELLS:
        assert cells_for(g8, km2) == l8, km2
    assert TF.pool_hops(g8) == 3.0
