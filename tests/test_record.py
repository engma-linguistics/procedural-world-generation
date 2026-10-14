"""The per-cell geological record (tectonics/record.py): the strata stack's
rules, and that strata and history ride with the crust in a simulation."""

import numpy as np

from planet.surface import DOLOMITE, FLOOD_BASALT, LIMESTONE, QUARTZITE, SANDSTONE, SHALE
from planet.tectonics import record as R

from helpers import run_sim


def stack(n=1):
    return R.empty((n,))


def put(rec, lith, km, rock, t):
    R.add_top(rec, lith, np.array([km] * len(rec)), np.array([rock] * len(rec), np.uint8), t)


def layers(rec, lith, i=0):
    return [(int(lith[i, j]), round(float(rec[i, j]), 4), float(rec[i, R.K + j])) for j in range(R.K) if rec[i, j] > 0]


def test_same_rock_continues_the_top_layer():
    rec, lith = stack()
    put(rec, lith, 0.3, SHALE, 10.0)
    put(rec, lith, 0.2, SHALE, 12.0)
    assert layers(rec, lith) == [(SHALE, 0.5, 12.0)]


def test_new_rock_starts_a_layer_and_a_thin_growing_top_is_absorbed():
    rec, lith = stack()
    put(rec, lith, 0.5, SHALE, 10.0)
    put(rec, lith, 0.2, LIMESTONE, 12.0)  # new layer
    assert layers(rec, lith) == [(LIMESTONE, 0.2, 12.0), (SHALE, 0.5, 10.0)]
    rec, lith = stack()
    put(rec, lith, 0.5, SHALE, 10.0)
    put(rec, lith, 0.01, SANDSTONE, 12.0)  # thin...
    put(rec, lith, 0.03, SHALE, 14.0)  # ...and absorbed by the thicker deposit
    assert layers(rec, lith) == [(SHALE, 0.04, 14.0), (SHALE, 0.5, 10.0)]


def test_hiatus_closes_a_layer():
    rec, lith = stack()
    put(rec, lith, 0.5, SANDSTONE, 10.0)
    put(rec, lith, 0.1, SANDSTONE, 10.0 + R.HIATUS + 2)
    assert [x[1] for x in layers(rec, lith)] == [0.1, 0.5]


def test_full_stack_merges_the_bottom_two():
    rec, lith = stack()
    for k, (km, rock) in enumerate([(2.0, SHALE), (0.5, SANDSTONE), (0.3, LIMESTONE), (0.4, FLOOD_BASALT)]):
        put(rec, lith, km, rock, 10.0 * k)
    got = layers(rec, lith)
    assert [g[0] for g in got] == [FLOOD_BASALT, LIMESTONE, SHALE]  # shale 2.0 + sandstone 0.5: shale
    assert got[-1][1] == 2.5
    assert np.isclose(rec[0, R.KM].sum(), 3.2)


def test_erosion_from_the_top_burial_from_the_bottom():
    rec, lith = stack()
    put(rec, lith, 1.0, SHALE, 0.0)
    put(rec, lith, 0.3, LIMESTONE, 30.0)
    R.remove_top(rec, lith, np.array([0.4]))
    assert layers(rec, lith) == [(SHALE, 0.9, 0.0)]
    put(rec, lith, 0.3, SANDSTONE, 60.0)
    R.remove_bottom(rec, lith, np.array([0.5]))
    assert layers(rec, lith) == [(SANDSTONE, 0.3, 60.0), (SHALE, 0.4, 0.0)]


def test_reconcile_makes_strata_add_up_to_the_cover():
    rec, lith = stack(3)
    put(rec, lith, 1.0, SHALE, 0.0)
    R.reconcile(rec, lith, np.array([1.5, 0.2, 0.0]), np.full(3, SANDSTONE, np.uint8), 5.0)
    assert np.allclose(rec[:, R.KM].sum(1), [1.5, 0.2, 0.0])
    assert lith[2, 0] == 0 and rec[2, 0] == 0
    rec, lith = stack()
    R.reconcile(rec, lith, np.array([0.7]), np.array([SANDSTONE], np.uint8), 5.0)
    assert layers(rec, lith) == [(SANDSTONE, 0.7, 5.0)]


def test_folding_dates_the_strata_and_cooks_sandstone_in_thick_crust():
    rec, lith = stack(2)
    put(rec, lith, 1.0, SANDSTONE, 0.0)
    R.fold(rec, lith, np.array([True, True]), np.array([1.0, 1.0]), np.array([1.0, 1.0]),
           np.array([40.0, 60.0]), 50.0)
    assert list(lith[:, 0]) == [SANDSTONE, QUARTZITE]
    assert np.all(rec[:, R.T_FOLD] == 50.0) and np.all(rec[:, R.FOLD_KM] == 1.0)
    rock, km, folded, t, below = R.top(rec, lith, np.zeros(2, np.uint8))
    assert folded.all()
    put(rec, lith, 0.2, SHALE, 60.0)  # deposited on the unconformity: flat
    rock, km, folded, t, below = R.top(rec, lith, np.zeros(2, np.uint8))
    assert not folded.any() and list(below) == [SANDSTONE, QUARTZITE]


def test_buried_limestone_becomes_dolomite():
    rec, lith = stack()
    put(rec, lith, 0.5, LIMESTONE, 0.0)
    put(rec, lith, 0.6, SHALE, 30.0)
    R.diagenesis(rec, lith)
    assert lith[0, 1] == LIMESTONE
    put(rec, lith, 0.5, SHALE, 32.0)
    R.diagenesis(rec, lith)
    assert lith[0, 1] == DOLOMITE


def test_strata_ride_with_the_crust_and_add_up(sim4):
    """In a 300 Myr run: every plate cell's strata add up to its cover;
    rifting, folding and flood basalts have left their marks; and the
    record sits on the plate, under the same crust as it moves."""
    pl = sim4.plates
    live = np.flatnonzero(pl.alive)
    for k in live:
        own = pl.owned[k]
        assert np.allclose(pl.rec[k, own][:, R.KM].sum(1), pl.cover[k, own], atol=1e-3)
    rec = sim4.w_rec
    t = sim4.t
    assert ((rec[:, R.T_RIFT] > 0) & sim4.w_cont).any()
    assert (rec[:, R.T_FOLD] > 0).any()
    assert (sim4.w_lith == FLOOD_BASALT).any() or (sim4.w_extra[:, 2] > 0).sum() == 0
    # the world view is the owner's plate record
    o, r = sim4.owner, sim4.w_ref
    assert np.array_equal(pl.rec[o, r], rec)
    assert (rec[:, R.T_RIFT] <= t).all() and (rec[:, R.T_FOLD] <= t).all()


def test_record_moves_with_its_plate():
    """Mark the record of one plate's crust; after the plates have moved,
    the mark shows only on that plate's crust (wherever it is now), never
    on cells another plate's crust has moved into."""
    sim = run_sim(level=4, seed=3, myr=10)
    pl = sim.plates
    k = int(np.bincount(sim.owner).argmax())
    pl.rec[k, pl.owned[k], R.T_RIFT] = -5.0
    sim._world_view()
    marked0 = sim.w_rec[:, R.T_RIFT] == -5.0
    sim.run(30)
    marked = sim.w_rec[:, R.T_RIFT] == -5.0
    assert marked.sum() > 0.5 * marked0.sum()
    # (on plate k, or on a piece that rifted off it and took its record along)
    label = int(pl.label[k])
    heirs = {label} | {e.plates[1] for e in sim.events if e.kind in ("rift", "subduction") and e.plates[0] == label}
    assert set(pl.label[sim.owner[marked]].tolist()) <= heirs
    assert np.any(marked & ~marked0)  # it moved with the plate (the plate moves ~1 cell in 20 Myr)
