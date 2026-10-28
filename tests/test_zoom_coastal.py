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


def _reef_coast(shelf_km):
    """A tropical carbonate coast (test_coastal's) whose shelf at 25 m is shelf_km wide."""
    from test_coastal import CENTRE, _dist_km
    from planet import surface as SF
    from planet import world as W
    from planet.grid import build_grid
    g = build_grid(5)
    d = _dist_km(g, *CENTRE)
    elev = np.where(d < 1500, 4 + 0.6 * np.maximum(1500 - d, 0), np.where(d < 1500 + shelf_km, -25.0, -4000.0))
    land = elev > 0
    extra = {"rock": np.full(g.n, 3), "surface_rock": np.where(land, 8, SF.LIMESTONE),
             "sediment_cover": np.where(land, 1.0, 2.0)}
    return W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 5}, erosion=0.0)


def _reef_zoom(w):
    from test_coastal import CENTRE
    return zoom.build(w, CENTRE[0], CENTRE[1] + 1500 / 111.0, size_km=400, res_km=2, iterations=4,
                      log=lambda *a: None)


@pytest.fixture(scope="module")
def reef_coasts():
    narrow, wide = _reef_coast(30.0), _reef_coast(150.0)
    real = ZCL.place

    def flat(*a, **k):  # (the same reefs, not raised: for the cell means)
        r = real(*a, **k)
        r["reef_top"] = np.full_like(r["reef_top"], np.nan)
        return r

    try:
        ZCL.place = flat
        wide0 = _reef_zoom(wide)
    finally:
        ZCL.place = real
    return _reef_zoom(narrow), _reef_zoom(wide), wide0


def test_reefs_are_terrain_fringing_or_barrier(reef_coasts):
    """PW-326: reef pixels stand at a reef flat 1-3 m below the sea; a
    narrow shelf has a fringing reef along its shore, a wide one a barrier
    reef along its outer edge with the shelf behind it (the lagoon) a
    little deeper; each cell keeps its mean."""
    narrow, wide, wide0 = reef_coasts
    for z in (narrow, wide):
        L = z["layers"]
        reef = L["coastal_life"] == ZCL.REEF
        assert reef.any() and np.all(L["elevation"][reef] >= -3.0 - 1e-6) and np.all(L["elevation"][reef] <= -0.5)
    fn, fw = narrow["stats"]["reef_forms"], wide["stats"]["reef_forms"]
    assert fn["fringing"] > 500 and fn["barrier"] == 0, fn
    assert fw["barrier"] > 300, fw
    sea, reef = (wide["layers"]["water"] == 1), (wide["layers"]["coastal_life"] == ZCL.REEF)
    lagoon = sea & ~reef & (wide0["layers"]["elevation"] > -40)
    assert np.median(wide["layers"]["elevation"][lagoon]) < np.median(wide0["layers"]["elevation"][lagoon]) - 2
    assert abs(wide["stats"]["cell_mean_bias_m"] - wide0["stats"]["cell_mean_bias_m"]) < 2
    assert abs(wide["stats"]["cell_mean_rms_error_m"] - wide0["stats"]["cell_mean_rms_error_m"]) < 5


def test_forearc_island_keeps_part_of_its_mean_in_its_sea():
    """PW-362: a lone land cell (+194 m) between -500 m shelf cells and a -4,800 m trench. Its sea pixels
    took the depth of the cells beyond it (the trench's), so its land stood as a mesa high enough to keep
    the cell's mean (land p90 ~950 m here, 1,600 m on world fac2af); now its sea first takes what the mean
    lacks, a shelf round the island, and the land stands lower (p90 ~630 m)."""
    from planet import world as W
    from planet.geo import R_KM, xyz
    from planet.grid import build_grid
    g = build_grid(5)
    k = int(np.argmax(g.centers @ xyz(0.0, np.radians(20.0))))
    d = np.arccos(np.clip(g.centers @ g.centers[k], -1, 1)) * R_KM
    lon = np.degrees(np.arctan2(g.centers[:, 1], g.centers[:, 0]))
    elev = np.where(d < 1200, np.where(np.abs(lon - 17.0) < 1.2, -4800.0, -500.0), -4000.0)
    elev[k] = 194.0
    land = elev > 0
    extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2), "sediment_cover": np.where(land, 0.1, 1.0)}
    w = W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 5}, erosion=0.0)
    w["layers"]["elevation"] = np.round(elev)
    nb = elev[g.nbr_idx[g.nbr_off[k]:g.nbr_off[k + 1]]]
    assert (nb == -4800).sum() >= 1 and (nb == -500).sum() >= 1
    c = g.centers[k]
    z = zoom.build(w, np.degrees(np.arcsin(c[2])), np.degrees(np.arctan2(c[1], c[0])), size_km=600, res_km=2,
                   iterations=6, log=lambda *a: None)
    nx, ny, res = z["nx"], z["ny"], z["res"]
    cc, rr = np.meshgrid(np.arange(nx), np.arange(ny))
    own = g.locate(z["frame"].to_sphere(((cc + 0.5 - nx / 2) * res).ravel(), ((ny / 2 - rr - 0.5) * res).ravel()))
    h = z["layers"]["elevation"].ravel().astype(float)
    on = z["layers"]["water"].ravel() == 0
    m = own == k
    assert 0.3 < on[m].mean() < 0.9 and h[m].mean() > 140  # (an island; the cell's mean held as before, ~170 m)
    p90, sea = np.percentile(h[m & on], 90), h[m & ~on].mean()
    assert p90 < 750 and sea > -450, (p90, sea)


def test_lone_deep_sea_cell_among_high_ground_keeps_to_its_depth():
    """PW-844: a lone -4,400 m sea cell inside 3 km high ground. The fine coast leaves it mostly land, and
    the mean correction drove its few sea pixels to -23 km (zoom 1ab4c4); now its floor stays within the
    coarse cells' range (less the sea floor's detail)."""
    from planet import world as W
    from planet.geo import xyz
    from planet.grid import build_grid
    g = build_grid(5)
    k = int(np.argmax(g.centers @ xyz(0.0, np.radians(20.0))))
    elev = np.full(g.n, 3000.0)
    elev[k] = -4400.0
    extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2), "sediment_cover": np.full(g.n, 0.1)}
    w = W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 5}, erosion=0.0)
    w["layers"]["elevation"] = np.round(elev)
    c = g.centers[k]
    z = zoom.build(w, np.degrees(np.arcsin(c[2])), np.degrees(np.arctan2(c[1], c[0])), size_km=400, res_km=2,
                   iterations=4, log=lambda *a: None)
    assert (z["layers"]["water"] == 1).any()
    assert z["layers"]["elevation"].min() > -4400 - 1000  # (the sea floor's detail reaches ~800 m at that depth)
