"""PW-1584: the people rules that counted cells and rings are in km / km2 now, and give the old counts at L7 (so L7 output is
unchanged) while an L8 refine keeps the same physical reach (twice the rings, four times the cells)."""
from types import SimpleNamespace

import pytest

from planet.grid import build_grid
import numpy as np

from planet.lineages import animals as AN, compose as CO, demes as DM, ladder as LA, polities as PO, settlements as ST, trade_flow as TF
from planet.lineages.history import polity_live as PL, tags as TG
from planet.lineages.history import params as PM
from planet.lineages.seafood import cells_for, rings_for, SEA_REACH_KM
from planet.lineages.land import REACH_KM as LAND_REACH_KM

# (constant, ring/cell helper, the old L7 count, the L8 count)
RINGS = [(LA.RAID_REACH_KM, 2, 4), (LA.BARTER_REACH_KM, 1, 2), (CO.REACH_KM, 10, 20), (PM.CHAIN_KM, 4, 8),
         (PM.ARRIVAL_POCKET_KM, 3, 6), (SEA_REACH_KM, 2, 4), (LAND_REACH_KM, 1, 2),
         # PW-1627: the settled history's own reaches (a town's and a city's hinterland, pit spacing, a coastal boat's reach,
         # the hemmed-in seat's ring)
         (ST.CONST["TOWN_KM"], 1, 2), (ST.CONST["CITY_KM"], 2, 4), (ST.CONST["PIT_KM"], 1, 2), (TF.COAST_BOAT_KM, 2, 4),
         (PO.HEMMED_KM, 2, 4),
         # PW-1630/1631: the river valley's watered width (ladder: WATER_MAX of one L7 cell) and the country the wild's richness is read over
         (LA.WATER_CELL_KM, 1, 2), (LA.RICH_KM, 1, 2)]
CELLS = [(DM.MIN_KM2, 40, 161), (DM.ADAPT_MIN_KM2, 20, 80), (AN.OVERLAP_MIN_KM2, 3, 12), (PO.SUBJECT_KM2, 3, 12),
         (TG.ISLAND_FLOOR_KM2, 3, 12)]


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


def _old_two_ring_pairs(g):
    """polity_live's two-ring table as it was built before PW-1627 (the L7 reference)."""
    off, idx, src = np.asarray(g.nbr_off, np.int64), np.asarray(g.nbr_idx, np.int64), np.asarray(g.nbr_src, np.int64)
    deg = np.diff(off)
    e = np.repeat(np.arange(len(idx)), deg[idx])
    dn = deg[idx]
    far = idx[off[idx[e]] + np.arange(len(e)) - np.repeat(np.cumsum(dn) - dn, dn)]
    pairs = np.unique(np.concatenate([np.stack([np.arange(g.n), np.arange(g.n)], 1), np.stack([src, idx], 1),
                                      np.stack([src[e], far], 1)]), axis=0)
    return pairs[:, 0], pairs[:, 1]


def test_ring_pairs_is_the_old_two_ring_table_and_any_ring_count(g7):
    """PW-1627: the live history's ring table in km keeps the old two-ring table at L7 exactly (same pairs, same order) and reads
    the same cells as the ledger's rings for any count (an L8 refine's four)."""
    a, b = PL.ring_pairs(g7.nbr_off, g7.nbr_idx, 2)
    a0, b0 = _old_two_ring_pairs(g7)
    assert np.array_equal(a, a0) and np.array_equal(b, b0)
    g = build_grid(3)
    for r in (1, 3, 4):
        a, b = PL.ring_pairs(g.nbr_off, g.nbr_idx, r)
        off = np.searchsorted(a, np.arange(g.n + 1))
        for c in range(0, g.n, 37):
            assert sorted(b[off[c]:off[c + 1]].tolist()) == sorted(ST._rings(g, c, r).tolist())


def test_ladder_reads_rivers_and_richness_in_km(g7):
    """PW-1630/1631: at L7 the richness is the cell's own (the same array, L7 unchanged); on a finer grid it is averaged over about one L7
    cell (a single rich cell among poor ones reads poorer), and the watered share of a river cell scales with the rings so the watered
    km2 per km of river stay WATER_MAX x one L7 cell's width."""
    x = np.random.default_rng(1).random(g7.n)
    assert LA.domain_mean(g7, x, LA.RICH_KM) is x
    g = build_grid(5)
    spike = np.zeros(g.n)
    spike[123] = 9.0
    m = LA.domain_mean(g, spike, 4 * g.spacing * 6371.0)  # (four cells wide: three passes)
    assert m[123] < 9.0 and m.max() == m[123] and (m > 0).sum() > 7  # (spread out, still peaked on the rich cell)
    g8 = _l8(g7)
    assert min(1.0, LA.WATER_MAX * rings_for(g8, LA.WATER_CELL_KM)) * (g8.spacing) == pytest.approx(LA.WATER_MAX * g7.spacing, rel=0.01)
