"""The zoom's shoreface (PW-327) and reefs as terrain (PW-326)."""

import numpy as np
import pytest

from planet import zoom
from planet import zoom_coastal as ZCL
from planet import zoom_kernels as ZK


def test_dean_profile_and_closure_depth():
    """Dean's profile for fine sand: ~10 m at 1 km, ~21 m at 3 km, down to
    the closure depth (6.75 x the mean significant wave height: ~11 m for
    10 kW/m of 8 s waves), then the inner shelf at SHELF_GRAD."""
    d = ZCL.shoreface_depth(np.array([1.0, 3.0]), np.array([1e6, 1e6]))  # (huge waves: closure at its cap)
    assert abs(d[0] - 10.0) < 0.1 and abs(d[1] - 20.8) < 0.2
    hc, xc = ZCL.closure(np.array([10.0]))
    assert 9.5 < hc[0] < 12.0 and abs(ZCL.DEAN_A * (1000 * xc[0]) ** (2 / 3) - hc[0]) < 1e-6
    far = ZCL.shoreface_depth(np.array([xc[0] + 4.0]), np.array([10.0]))
    assert abs(far[0] - (hc[0] + 4.0 * ZCL.SHELF_GRAD)) < 1e-6


def _straight_coast(rocky):
    nx = ny = 60
    col = np.tile(np.arange(nx), ny)
    sea = col >= 20
    h = np.where(sea, -40.0, 5.0)
    out, reach = ZCL.shoreface(h, sea, np.full(nx * ny, rocky), np.full(nx * ny, 10.0), nx, ny, 0.5)
    return col, sea, h, out, reach


def test_sandy_shore_shoals_rocky_one_keeps_its_deep_water():
    col, sea, h, out, reach = _straight_coast(0.0)
    assert np.all(out[sea & (col <= 21)] > -10.0)  # (within 1 km: < 10 m deep)
    assert np.all(out[sea] >= h[sea]) and np.all(out[sea] <= -0.5)
    assert np.all(np.diff(out.reshape(60, 60)[30, 20:40]) <= 1e-9)  # deepening offshore
    assert np.allclose(out[col >= 50], -40.0) and np.all(reach[col >= 50] == 0)  # (out past the shelf's fade)
    _, _, h2, out2, _ = _straight_coast(1.0)
    assert np.allclose(out2, h2)


@pytest.fixture(scope="module")
def low_coast():
    """A low plain (60 m, falling west) facing 10 kW/m waves; with and without the shoreface."""
    from test_zoom_landforms import _plain_world
    w, land = _plain_world(60.0, -0.02, 0.0, precip=1000.0, thick_gy=0.0)
    w["layers"]["wave_power"] = np.where(land, 0.0, 10.0)
    w["layers"]["tide_range"] = np.where(land, 0.0, 1.0)
    kw = dict(size_km=300, res_km=1.0, iterations=6, log=lambda *a: None)
    z = zoom.build(w, 0.0, 22.4, **kw)
    real = ZCL.shoreface
    try:
        ZCL.shoreface = lambda h, sea, *a, **k: (h, np.zeros_like(h))
        z0 = zoom.build(w, 0.0, 22.4, **kw)
    finally:
        ZCL.shoreface = real
    return z, z0


def test_zoom_sea_floor_shoals_to_the_shore_and_keeps_the_cell_means(low_coast):
    """PW-327: the sea floor 1.5-3 km off the shore was ~130 m deep (the
    coarse floor's interpolation); now ~20 m. Each cell's mean is kept by
    the floor further out."""
    for z, lo, hi in ((low_coast[0], 5.0, 30.0), (low_coast[1], 100.0, 1e9)):
        h = z["layers"]["elevation"].ravel()
        sea = z["layers"]["water"].ravel() == 1
        d = ZK.inside_distance(sea, z["nx"], z["ny"], False) * z["res"]
        band = sea & (d > 1.5) & (d <= 3.0)
        assert lo < np.median(-h[band]) < hi
    b, b0 = (z["stats"]["cell_mean_bias_m"] for z in low_coast)
    r, r0 = (z["stats"]["cell_mean_rms_error_m"] for z in low_coast)
    assert abs(b - b0) < 5 and r < r0 + 10, (b, b0, r, r0)
