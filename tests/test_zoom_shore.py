"""Lake shores rise from the water instead of lying as a table (PW-531)."""
import numpy as np

from planet.zoom import regional as Z
from planet.zoom import kernels as ZK


def _plain(n=60, rise=0.2):
    """A lake on the west edge, land draining west to it, a plain rising only `rise` m/km."""
    nx, ny = n, 40
    idx = np.arange(nx * ny)
    col = idx % nx
    lake = col < 4
    h = np.where(lake, 100.0, 100.0 + rise * (col - 3.0))
    rec = np.where(col > 0, idx - 1, -1)
    order = np.argsort(col, kind="stable")
    return nx, ny, idx, lake, h, rec, order


def test_raise_to_run_only_lifts():
    nx, ny, idx, lake, h, rec, order = _plain()
    run = np.where(lake, 0.0, 2.0)
    out = ZK.raise_to_run(h, rec, order, run, np.full(len(h), 0.002))
    assert (out >= h).all()
    assert (out[lake] == h[lake]).all()
    col = idx % nx
    assert np.allclose(out[(col >= 4) & (idx // nx == 3)], 100.0 + 2.0 * (col[(col >= 4) & (idx // nx == 3)] - 3.0))


def test_shore_apron_grades_the_plain_and_keeps_the_lake():
    nx, ny, idx, lake, h, rec, order = _plain()
    res = 1.0
    lakes = [{"px": np.flatnonzero(lake)}]
    held = np.zeros(nx * ny, bool)
    q = np.zeros(nx * ny)
    old_min = Z.SHORE_MIN_KM2
    Z.SHORE_MIN_KM2 = 1.0
    try:
        out, n = Z.shore_apron(h, lake, lakes, ~lake, held, np.zeros(0, np.int64), rec, order, q, nx, ny, res)
    finally:
        Z.SHORE_MIN_KM2 = old_min
    assert n > 0
    assert (out >= h).all() and (out[lake] == h[lake]).all()
    assert (out[rec >= 0] >= out[rec[rec >= 0]]).all()  # still drains to the lake
    row = out.reshape(ny, nx)[20]
    assert np.diff(row[7:11]).min() > 1.0 / res  # no flat table beside the lake: > 1 m per km
