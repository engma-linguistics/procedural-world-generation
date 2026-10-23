"""Resources layer (PW-155): the history's column and the layer vocabulary."""

import numpy as np

from planet import resources as RS
from planet import store as S


def _column(steps, k=RS.K_STACK):
    typ, km, maxd = np.zeros((1, k), np.int8), np.zeros((1, k)), np.zeros((1, k))
    ntop = np.zeros(1, np.int64)
    for dc, lit in steps:
        RS._stack_step(typ, km, maxd, ntop, np.array([dc], float), np.array([lit], np.int8))
    return RS._column_summary(typ, km, maxd, ntop, 6)


def test_column_is_last_in_first_out():
    # 1 km coal, 3 km shale on top (coal buried to 2.5 km at its middle), then 2 km eroded off
    tot, dep, mx, oil, gas, shallow = _column([(1.0, RS.COALY), (3.0, RS.CLASTIC), (-2.0, RS.CLASTIC)])
    assert np.isclose(tot[0, RS.COALY], 1.0) and np.isclose(tot[0, RS.CLASTIC], 1.0)
    assert np.isclose(mx[0, RS.COALY], 3.5)  # the deepest it has been: under 3 km, middle of 1 km
    assert np.isclose(dep[0, RS.COALY], 1.5)  # now under 1 km
    assert np.isclose(oil[0, RS.COALY], 1.0) and np.isclose(shallow[0, RS.COALY], 1.0)
    # erosion eats through the top into the coal
    tot, *_ = _column([(1.0, RS.COALY), (0.5, RS.CLASTIC), (-1.0, RS.CLASTIC)])
    assert np.isclose(tot[0, RS.COALY], 0.5) and tot[0, RS.CLASTIC] == 0


def test_full_column_merges_bottom():
    tot, *_ = _column([(0.1, i % 2) for i in range(3 * RS.K_STACK)])
    assert np.isclose(tot[0].sum(), 3 * RS.K_STACK * 0.1)


def test_vocabulary():
    assert set(RS.NAMES) <= set(S.LAYERS)
    leg = RS.legend()
    assert [r["key"] for r in leg["resources"]] == list(RS.KEYS)
    assert all(r["group"] == "fantasy" for r in leg["resources"] if r["key"].startswith("x_"))
    assert "resources" in S.legends()
