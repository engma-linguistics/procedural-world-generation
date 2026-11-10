"""The split history on a refined world (PW-1265, lane 267: history.handover): the deep and glacial history on the time zoom's grid,
the settled window on the finer grid. On the fake level-3 time zoom with a level-4 fine grid."""

from __future__ import annotations

import numpy as np
import pytest

from planet.geo import cell_area_km2
from planet.grid import build_grid
from planet.lineages import output as O
from planet.lineages import recent as R
from planet.lineages import spec as SP
from planet.lineages.history import History
from planet.lineages.history import handover as HO
from planet.lineages.history.summary import present_summary
from planet.lineages.spread import EST
from tests.test_lineages import _raw, faketz  # noqa: F401 (the fixture)


def test_regrid_keeps_categories_means_and_totals():
    g3, g4 = build_grid(3), build_grid(4)
    Rg = HO.Regrid(g3, g4)
    rng = np.random.default_rng(1)
    x = rng.random((2, g3.n))
    assert np.allclose(Rg.split(x).sum(1), x.sum(1), rtol=1e-12)  # (an amount: totals kept)
    assert np.allclose(Rg.mean(np.full(g3.n, 3.5)), 3.5)  # (a quantity per area: a flat field stays flat)
    kept = Rg.keep(np.arange(g3.n))
    assert np.array_equal(kept[:g3.n], np.arange(g3.n))  # (a kept cell is its own parent)
    m = Rg.mean(x)
    assert np.array_equal(m[:, :g3.n], x)  # (...and keeps its own value)


def test_heads_split_conserves_every_people_and_leaves_none_under_the_floor():
    """Each line's people (presence >= EST x density x the grid's cell area) are the same after the split, to rounding; no fine cell
    holds a presence under EST (those heads go back to the parent's own cell)."""
    g3, g4 = build_grid(3), build_grid(4)
    Rg = HO.Regrid(g3, g4)
    rng = np.random.default_rng(7)
    P = np.where(rng.random((5, g3.n)) < 0.4, rng.uniform(EST, 1.0, (5, g3.n)), 0.0)
    P[0, :] = np.where(P[0] > 0, EST * 1.05, 0.0)  # (a thin line: its midpoints would fall under EST)
    D = rng.uniform(0.01, 2.0, (5, g3.n))
    D[3] = 0.4  # (a line with one density)
    Pf, Df = HO.heads_split(Rg, P, D)
    before = (np.where(P >= EST, P, 0) * D).sum(1) * cell_area_km2(g3.n)
    after = (np.where(Pf >= EST, Pf, 0) * Df).sum(1) * cell_area_km2(g4.n)
    assert np.allclose(after, before, rtol=1e-12)
    assert not ((Pf > 0) & (Pf < EST)).any()
    assert ((Pf >= EST).sum(1) >= (P >= EST).sum(1)).all()  # (a people keeps at least its coarse cells)


@pytest.mark.slow
def test_split_history_hands_over_at_the_first_farming_and_keeps_the_coarse_past(faketz):
    """The split run equals the coarse run up to the cut (its stored frames, cell for cell from their parents), hands over once at
    the earliest drawn first cultivation with the people conserved, and ends on the fine grid; output.save writes it."""
    params = dict(kyr=20, seed=1)
    tree = SP.parse(_raw())
    ps3 = R.Pass(faketz, 40.0, R.RecentParams(**params))
    ps4 = R.Pass(faketz, 40.0, R.RecentParams(**params), level=4)
    assert ps4.grid.n > ps3.grid.n and ps4.rain0.shape == (ps4.grid.n,)
    hc = History(tree, ps3, 1)
    rc = hc.run()
    hs = History(SP.parse(_raw()), R.Pass(faketz, 40.0, R.RecentParams(**params)), 1, fine=(ps4, None))
    rs = hs.run()
    ho = hs.handover
    assert ho is not None and ho["coarse"] == 3 and ho["fine"] == 4
    cut = HO.cut_kyr(hs)
    assert cut is not None and abs(ho["cut_kyr"] - cut) < 1e-9 and ho["step_ago"] <= cut + 1e-9
    assert abs(ho["people_after"] - ho["people_before"]) <= 1e-9 * max(ho["people_before"], 1.0)
    assert hs.grid.n == ps4.grid.n and rs["present"].shape == (len(hs.lines), ps4.grid.n)
    Rg = HO.Regrid(ps3.grid, ps4.grid)
    pre = [f for f in rc["frames"] if f["ago"] > ho["step_ago"] + 1e-9]
    assert pre and len(rs["frames"]) == len(rc["frames"])
    for a, b in zip(pre, rs["frames"]):
        assert a["ago"] == b["ago"]
        assert np.array_equal(Rg.keep(a["peoples"]), b["peoples"])  # (the coarse past, unchanged)
    assert all(f["peoples"].shape == (ps4.grid.n,) for f in rs["frames"])
    out = O.save(hs, rs, present_summary(hs, rs["present"]), name="split test")
    assert out.exists()
