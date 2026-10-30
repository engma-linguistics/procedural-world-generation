"""The glacial landforms of the regional zoom (zoom.glacial, PW-092): kernels, the ice's flow
from the imprint, and the Glaciated synthesiser on a synthetic valley."""

import numpy as np

from planet.zoom import landforms as ZL
from planet.zoom import glacial as ZG
from planet.grid import build_grid


def test_nearest_feature_and_downstream_distance():
    nx = ny = 40
    m = np.zeros(nx * ny, bool)
    m[5 * nx + 7] = m[30 * nx + 33] = True
    idx, d = ZG.nearest_feature(m, nx, ny)
    r, c = np.divmod(np.arange(nx * ny), nx)
    want = np.minimum(np.hypot(r - 5, c - 7), np.hypot(r - 30, c - 33))
    assert np.allclose(d, want, atol=1e-9) and np.all(m[idx])
    # a column of pixels draining south: the distance from a source grows along it
    rec = np.where(r < ny - 1, (r + 1) * nx + c, -1)
    order = np.argsort(-r, kind="stable")  # outlets first
    src = np.zeros(nx * ny, bool)
    src[10 * nx + 3] = True
    dd = ZG.downstream_dist(rec, order, src, nx, 2.0)
    assert dd[10 * nx + 3] == 0 and np.isclose(dd[15 * nx + 3], 10.0) and np.isinf(dd[5 * nx + 3])


def test_ice_flow_runs_down_the_surface_of_the_ice():
    g = build_grid(3)
    lat = np.degrees(np.arcsin(g.centers[:, 2]))
    ice = np.where(lat > 40, 1000.0 + 30.0 * (lat - 40), 0.0)  # (a dome on the pole)
    L = {"elevation": np.zeros(g.n), "ice_max": ice}
    f = ZG.ice_flow(g, L)
    mid = (lat > 55) & (lat < 80)
    # the thick ice is at the pole: it flows south where it is thick; nothing where there was no ice
    assert np.mean(f["ice_fn"][mid]) < -0.3
    assert np.all(f["ice_fe"][ice == 0] == 0) and np.all(f["ice_fn"][ice == 0] == 0)


def _valley(nx=60, ny=60, res=0.5, sea_rows=0):
    """A V valley (floor along column nx/2, falling south) with a side valley joining it from the east."""
    r, c = np.divmod(np.arange(nx * ny), nx)
    floor = 400.0 - 4.0 * r  # (m; falls to 160 m at the south edge)
    h = floor + 25.0 * np.abs(c - nx // 2) + 0.0 * r
    rec = np.where(r < ny - 1, (r + 1) * nx + np.where(c < nx // 2, c + 1, np.where(c > nx // 2, c - 1, c)), -1)
    # (every pixel flows down its own row to the axis, then south along it)
    rec = np.where((c != nx // 2) & (r < ny - 1), r * nx + c + np.where(c < nx // 2, 1, -1), rec)
    chan = (c == nx // 2)
    order = np.argsort(-(r * 1000 - np.abs(c - nx // 2)), kind="stable")
    q = np.where(chan, 40.0, 1.0)
    return nx, ny, res, r, c, h, rec, order, chan, q


def _ctx(nx, ny, res, h, rec, order, chan, q, E):
    n = nx * ny
    km = np.arange(n)
    Pk = np.column_stack([6371.0 + 0 * km, (km % nx) * res, (km // nx) * res])
    land = np.ones(n, bool)
    cx = ZL.Ctx(nx, ny, res, 60.0, np.zeros(n), np.zeros(n), Pk, 7, land, h.copy())
    cx.w = np.ones(n)
    cx.prm = {"glacial_erosion": np.full(n, E), "glacial_till": np.full(n, 8.0), "ice_max": np.full(n, 1500.0),
              "iced": np.ones(n), "ice_fe": np.full(n, 0.6), "ice_fn": np.full(n, -0.8), "wind_e": np.ones(n),
              "wind_n": np.zeros(n)}
    cx.rec, cx.order, cx.q, cx.chan = rec, order, q, chan
    return cx


def test_trough_is_lowered_u_shaped_and_scales_with_the_erosion():
    nx, ny, res, r, c, h, rec, order, chan, q = _valley()
    g = ZG.Glaciated()
    out = {}
    for E in (0.0, 20.0, 60.0):
        cx = _ctx(nx, ny, res, h, rec, order, chan, q, E)
        out[E] = g.shape(cx, h)
    assert np.all(np.abs(out[0.0][chan]) < 1.0)  # (no erosion, no trough)
    low20, low60 = -out[20.0][chan].mean(), -out[60.0][chan].mean()
    assert low20 > 20.0 and low60 > 1.5 * low20  # the floor is lowered, more where the ice eroded more
    # the surface after: a flat floor and walls steepening outwards (a power law, not a V)
    z = h + out[60.0]
    row = z.reshape(ny, nx)[30]
    axis = nx // 2
    wall = row[axis + 1:axis + 6] - row[axis]
    assert np.all(np.diff(wall) >= -1e-6)
    # (the trough opens only as wide as its depth asks: a wall steeper than the valley's V (25 m / px), then the V again)
    assert wall[1] - wall[0] > 25.0 + 1.0 and wall[4] - wall[3] <= 25.0 + 1e-6


def test_a_trough_that_reaches_the_sea_is_flooded():
    nx, ny, res, r, c, h, rec, order, chan, q = _valley()
    g = ZG.Glaciated()
    cx = _ctx(nx, ny, res, h, rec, order, chan, q, 60.0)
    dz = g.shape(cx, h)
    z = h + dz
    z = np.where(r >= 55, np.minimum(z, -50.0), z)  # (the southern rows are the sea)
    sea = r >= 55
    # land pixels the trough left below the sea level and joined to it
    zone = cx.cache["zone_trough"]
    z = np.where(zone & ~sea & (r > 40), np.minimum(z, -20.0), z)
    drowned = g.drown(cx, z, sea)
    assert drowned is not None and drowned[(c == nx // 2) & (r > 41) & (r < 54)].all()
    assert not drowned[r < 20].any()  # (the head of the valley stays dry land)
    # without a connection to the sea nothing is flooded
    assert not g.drown(cx, z, np.zeros(nx * ny, bool)).any()


def test_trough_width_follows_its_depth_and_a_moraine_dams_a_stream():
    nx, ny, res, r, c, h, rec, order, chan, q = _valley(res=0.5)
    g = ZG.Glaciated()
    cx = _ctx(nx, ny, res, h, rec, order, chan, q, 60.0)
    dz = g.shape(cx, h)
    trunk, t, x, w_t, ok, delta, wh, _ = cx.cache["trough_geom"]
    on = chan & (r > 5) & (r < ny - 5)
    # the rim-to-rim width is a few times the depth (the floor lowering plus the valley's relief up to the rim)
    wd = 2000.0 * wh[on] / np.maximum(delta[on], 1.0)
    assert np.all(wd > 1.0) and np.median(wd) < 7.0
    # the ice margin crosses the valley halfway: across the stream the belt is one unbroken ridge, a dam
    cx2 = _ctx(nx, ny, res, h, rec, order, chan, q, 60.0)
    cx2.prm["iced"] = np.where(r < ny // 2, 1.0, 0.0) * 1.0
    g.shape(cx2, h)
    mor = cx2.cache["mor"]
    belt = mor.reshape(ny, nx)
    assert belt[:, nx // 2].max() >= ZG.DAM_M[0] * 0.8
    assert g.lakes(cx2).reshape(ny, nx)[ny // 2 - 3, nx // 2] > 0.5  # (lakes may form behind it, up the valley)
