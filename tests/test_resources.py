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


def test_running_mean_and_streaks():
    a = np.array([[0.0], [0.1], [0.0], [0.1], [0.0]])
    m = RS._running_mean(a, 3)
    assert np.allclose(m[1:4, 0], [1 / 30, 2 / 30, 1 / 30])
    ok = np.array([[1], [1], [0], [1], [1], [1]], bool)
    dt = np.full(6, 4.0)
    age = np.array([20.0, 16, 12, 8, 4, 0])
    # the run still going (12 Myr) beats the older one (8 Myr, discounted)
    assert RS._streaks(ok, dt, age, 60.0)[0] == 12.0


def test_zoom_receivers_and_box():
    from planet import zoom_resources as ZR
    slots = np.array([[4, 6], [255, 1]], np.uint8)  # E, S; none, N
    rec = ZR._receivers(slots, 2, 2)
    assert rec.tolist() == [1, 3, -1, 1]
    a = np.arange(25.0).reshape(5, 5)
    b = ZR._box(a, 1)
    assert np.isclose(b[2, 2], a[1:4, 1:4].mean())


def test_zoom_models_cover_resources():
    from planet import zoom_resources as ZR
    assert set(ZR.KEYS) <= set(RS.KEYS)
    assert abs(ZR.SIZE_P.sum() - 1) < 1e-9
    for k, (form, *_rest) in ZR.MODELS.items():
        assert form in ZR.FORM_NOTE, k
