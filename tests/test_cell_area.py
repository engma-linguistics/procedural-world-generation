"""PW-1043: the cells are not all the same size, so river flow and island / sea sizes add up true areas.
Discharge is pinned against them on a dome of land around a pentagon (the grid's smallest cells), where counting
cells as mean-sized overstates it (by 7% on this L5 dome)."""

import numpy as np
import pytest

from planet import hydrology as Hy
from planet.constants import SEC_PER_YR
from planet.geo import R_KM, is_land
from planet.grid import shared_grid


@pytest.fixture(scope="module")
def g():
    return shared_grid(5)


def test_cell_areas(g):
    a = g.cell_area_km2
    assert a.sum() == pytest.approx(4 * np.pi * R_KM ** 2, rel=1e-9)
    assert a[g.pentagons].max() < a.mean()  # (the pentagons are the smallest cells)
    assert a.min() / a.mean() < 0.75 and a.max() / a.mean() > 1.15
    assert g.area_weight.mean() == pytest.approx(1.0, rel=1e-12)
    assert not a.flags.writeable


def _dome(g, cap=0.97):
    """Land on a cap around a pentagon, sloping down to the sea all round it."""
    d = g.centers @ g.centers[g.pentagons[0]]
    elev = np.where(d > cap, 100.0 + 50_000.0 * (d - cap), -1000.0)
    return elev, d > cap


def test_discharge_true_areas(g):
    """Uniform runoff on the dome: the discharge into the sea is the runoff times the dome's true area."""
    elev, dome = _dome(g)
    land = is_land(elev, grid=g)
    assert np.array_equal(land, dome)
    n = g.n
    runoff = np.full(n, 500.0)  # mm/yr
    lk = Hy.lakes(g, elev, runoff, np.zeros(n), np.zeros(n), land=land)
    flow, down, order, _ = Hy.route(g, elev, lk)
    mouth = land & (down >= 0) & ~land[np.maximum(down, 0)]
    q = Hy.discharge(g, flow[mouth]).sum()
    true = 0.5 * g.cell_area_km2[dome].sum() * 1e6 / SEC_PER_YR
    assert q == pytest.approx(true, rel=1e-9)
    counted = 0.5 * dome.sum() * 4 * np.pi * R_KM ** 2 / n * 1e6 / SEC_PER_YR  # (the old, cells-as-mean answer)
    assert counted / true > 1.05  # (1.07 here)


def test_small_sea_by_true_area(g):
    """is_land's small-sea rule (SEA_MIN_KM2) reads a body's true area."""
    from planet import geo
    a = g.cell_area_km2
    p = g.pentagons[0]
    body = np.zeros(g.n, bool)
    body[p] = True
    body[g.nbr_idx[g.nbr_off[p]:g.nbr_off[p + 1]]] = True
    elev = np.full(g.n, 500.0)
    elev[body] = -50.0
    elev[g.centers @ g.centers[p] < -0.5] = -50.0  # (the world ocean: the far side)
    true = a[body].sum()
    old = geo.SEA_MIN_KM2
    try:
        geo.SEA_MIN_KM2 = 0.5 * (true + body.sum() * a.mean())  # (between the true and the cells-as-mean size)
        assert is_land(elev, grid=g)[body].all()  # its true area is below the bound: a lake
    finally:
        geo.SEA_MIN_KM2 = old
