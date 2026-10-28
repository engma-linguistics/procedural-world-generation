"""Human-use layers (PW-099, humanuse.py) on small synthetic rasters: each rule on a landscape built to show it."""

import numpy as np

from planet import humanuse as HU


def raster(z, receiver=None, res=2.0):
    ny, nx = z.shape
    return HU.Net.raster(ny, nx, res, receiver)


def slots_east(ny, nx):
    """D8 slots of a raster whose every pixel drains east (slot 4)."""
    rec = np.full((ny, nx), 4, np.uint8)
    rec[:, -1] = 255
    return rec


def test_months_below_matches_a_sine_year():
    assert HU.months_below(20.0, 10.0, 0.0) == 0
    assert HU.months_below(-5.0, -15.0, 0.0) == 12
    assert abs(HU.months_below(10.0, -10.0, 0.0) - 6) < 1e-9  # (a symmetric year spends half of it below the mean)


def test_navigable_rivers_by_depth_and_gradient_and_falls():
    ny, nx = 5, 60
    net = raster(np.zeros((ny, nx)), slots_east(ny, nx))
    x = np.arange(nx)
    z = np.tile(100.0 - 0.05 * x, (ny, 1)).ravel()  # 0.025 m/km: a lowland river
    land = np.ones(ny * nx, bool)
    row = np.zeros((ny, nx))
    row[2] = 6000.0
    cls, grad, openm, conn = HU.river_nav(net, z, row.ravel(), land, np.zeros(ny * nx))
    assert (cls.reshape(ny, nx)[2, :-1] == 3).all() and cls.reshape(ny, nx)[0].max() == 0  # (only the river's row)
    # a mountain torrent of the same flow has rapids: no ships, no barges
    steep = np.tile(3000.0 - 40.0 * x, (ny, 1)).ravel()  # 20 m/km
    cls2, *_ = HU.river_nav(net, steep, row.ravel(), land, np.zeros(ny * nx))
    assert cls2.reshape(ny, nx)[2, :-1].max() == 0
    # a trickle floats nothing; a small river floats skiffs only
    small = np.zeros((ny, nx))
    small[2] = 40.0
    cls3, *_ = HU.river_nav(net, z, small.ravel(), land, np.zeros(ny * nx))
    assert set(np.unique(cls3.reshape(ny, nx)[2, :-1])) == {1}
    # a fall breaks the reach; ice shuts it
    falls = np.zeros(ny * nx, bool)
    falls[2 * nx + 30] = True
    cls4, *_ = HU.river_nav(net, z, row.ravel(), land, np.zeros(ny * nx), falls)
    assert cls4[2 * nx + 30] == 0 and cls4[2 * nx + 29] == 3
    cls5, _, openm5, _ = HU.river_nav(net, z, row.ravel(), land, np.full(ny * nx, 10.0))
    assert cls5.max() == 0 and openm5.max() == 2
    # the river reaches the sea only along navigable water
    sea = land.copy().reshape(ny, nx)
    sea[:, -1] = False
    cls6, _, _, conn6 = HU.river_nav(net, z, row.ravel(), sea.ravel(), np.zeros(ny * nx))
    assert conn6.reshape(ny, nx)[2, 0] and not conn6.reshape(ny, nx)[0].any()


def test_harbour_needs_shelter_and_deep_water():
    ny = nx = 60
    land = np.ones((ny, nx), bool)
    yy, xx = np.mgrid[:ny, :nx]
    land[xx >= 40] = False  # open sea to the east of a straight coast
    land[(np.hypot(yy - 30, xx - 22) < 7)] = False  # a round bay cut into the coast, joined to the sea by a gap
    land[28:33, 22:42] = False
    net = raster(land.astype(float))
    ok = np.isfinite(HU.dist_from(net, land.ravel(), 8.0)) & ~land.ravel()
    fe, reach = HU.fetch_raster(land, np.flatnonzero(ok), 2.0, 50.0)
    shelter = np.zeros(ny * nx)
    shelter[ok] = 1 - fe / reach
    sh = shelter.reshape(ny, nx)
    assert sh[30, 18] > 0.65 and sh[10, 41] < 0.55  # (bay vs open coast)
    deep = np.full(ny * nx, 20.0)
    cls, _ = HU.harbours(net, deep, land.ravel(), np.zeros(ny * nx), np.zeros(ny * nx), fe, reach, ok)
    assert cls.reshape(ny, nx)[30, 18] >= 1 and cls.reshape(ny, nx)[10, 41] == 0
    shoal, = [np.full(ny * nx, 2.0)]
    cls2, _ = HU.harbours(net, shoal, land.ravel(), np.zeros(ny * nx), np.zeros(ny * nx), fe, reach, ok)
    assert cls2.max() == 0  # no draught
    cls3, _ = HU.harbours(net, deep, land.ravel(), np.full(ny * nx, 11.0), np.zeros(ny * nx), fe, reach, ok)
    assert cls3.max() == 0  # ice-bound
    # a big river mouth lifts an estuary a class
    qm = np.zeros(ny * nx)
    qm[30 * nx + 18] = 5000.0
    cls4, _ = HU.harbours(net, deep, land.ravel(), np.zeros(ny * nx), qm, fe, reach, ok)
    assert cls4[30 * nx + 18] > cls[30 * nx + 18]


def test_no_harbour_in_a_sea_pit_cut_off_inside_a_zoom():
    """PW-844: an ice-ringed polar zoom listed 581 harbour pixels, all in pits of 'sea' among high
    ground that no ship reaches: a zoom's harbours need water joined to its edge (or a sea of its own)."""
    ny = nx = 60
    land = np.ones((ny, nx), bool)
    yy, xx = np.mgrid[:ny, :nx]
    land[np.hypot(yy - 30, xx - 20) < 5] = False  # a pit, 10 px across
    land[:, 55:] = False  # the open sea along the east edge
    sea = ~land
    open_ = HU.open_sea(sea, 1.0)
    assert open_[:, 55:].all() and not open_[30, 20]
    assert HU.open_sea(sea, 10.0)[30, 20]  # (at 10 km/px the pit is a 100 km sea of its own)
    L = {"elevation": np.where(land, 2000.0, -800.0), "water": sea.astype(np.uint8)}
    out, _ = HU.analyse_zoom(L, 1.0)
    h = out["harbour"]
    assert not h[np.hypot(yy - 30, xx - 20) < 8].any()


def test_pass_is_the_lowest_saddle_of_a_range():
    ny, nx = 40, 60
    yy, xx = np.mgrid[:ny, :nx]
    z = 100.0 + 3000.0 * np.exp(-((xx - 30) ** 2) / 30.0)  # a N-S range
    z -= 1400.0 * np.exp(-((yy - 20) ** 2) / 12.0) * np.exp(-((xx - 30) ** 2) / 40.0)  # with a gap in the middle
    z = z + 0.01 * xx  # (no flats)
    # drainage: each side collects at one outlet on its own edge (row 20, col 0 / col 59)
    rec = np.full((ny, nx), 255, np.uint8)
    for tc in (0, nx - 1):
        side = xx < 30 if tc == 0 else xx >= 30
        dr, dc = np.sign(20 - yy), np.sign(tc - xx)
        slot = 3 * (dr + 1) + (dc + 1)
        slot = np.where(slot > 4, slot - 1, slot)
        rec = np.where(side & ~((yy == 20) & (xx == tc)), slot, rec).astype(np.uint8)
    net = raster(z, rec, res=5.0)
    land = np.ones(ny * nx, bool)
    ps = HU.passes(net, z.ravel(), land, np.full(ny * nx, 15.0), np.full(ny * nx, 2.0), np.full(ny * nx, 800.0))
    assert len(ps) == 1
    r, c = divmod(ps[0]["node"], nx)
    assert 15 <= r <= 25 and 28 <= c <= 32  # at the gap in the crest
    assert 1000 < ps[0]["height"] < 2000 and ps[0]["open_months"] == 12
    cold = HU.passes(net, z.ravel(), land, np.full(ny * nx, 5.0), np.full(ny * nx, -20.0), np.full(ny * nx, 800.0))
    assert cold[0]["open_months"] < 8 and HU.pass_class(cold[0]["open_months"]) >= 2


def test_fertile_ranks_good_ground_over_poor():
    n = 5
    ones, zeros = np.ones(n), np.zeros(n)
    fert = np.array([0.9, 0.9, 0.9, 0.9, 0.1])
    moist = np.array([0.9, 0.9, 0.1, 0.9, 0.9])
    grow = np.array([8.0, 8.0, 8.0, 2.0, 8.0])
    slope = np.array([1.0, 30.0, 1.0, 1.0, 1.0])
    score, cls = HU.fertile(fert, ones, moist, grow, slope, ones.astype(bool), zeros, zeros, zeros, zeros)
    assert cls[0] == 4 and score[0] > max(score[1:])
    assert cls[1] == 0  # a cliff
    assert score[2] < 0.6 * score[0] and score[3] < 0.8 * score[0] and score[4] < score[0]
    _, cls_ice = HU.fertile(fert, ones, moist, grow, slope, ones.astype(bool), ones * 100, zeros, zeros, zeros)
    assert cls_ice.max() == 0


def test_fresh_water_reach_and_springs():
    ny = nx = 30
    net = raster(np.zeros((ny, nx)), res=2.0)
    src = np.zeros(ny * nx, bool)
    src[15 * nx + 15] = True
    cls, km = HU.fresh_reach(net, src)
    c = cls.reshape(ny, nx)
    assert c[15, 15] == 3 and c[15, 16] == 3 and c[15, 19] == 2 and c[15, 24] == 1 and c[0, 0] == 0
    assert abs(km.reshape(ny, nx)[15, 18] - 6.0) < 1e-6
    # a spring where dry ground meets a wet mountain's foot
    z = np.zeros((ny, nx))
    z[:, 20:] = 600.0
    supply = np.zeros((ny, nx))
    supply[:, 20:] = 500.0
    sp = HU.springs(net, z.ravel(), supply.ravel(), np.ones(ny * nx, bool))
    assert sp.reshape(ny, nx)[:, 16:20].any() and not sp.reshape(ny, nx)[:, :10].any()


def test_zoom_and_world_analyses_run_on_partial_inputs():
    el = np.linspace(500, -50, 40 * 30).reshape(40, 30)
    out, tab = HU.analyse_zoom({"elevation": el, "water": (el <= 0).astype(np.uint8)}, 2.0)
    assert set(out) <= set(HU.NAMES) and out["fresh_water"].shape == el.shape and out["harbour"].dtype == np.uint8
    assert tab["net"].n == el.size


def test_inland_zoom_still_has_every_class_map():
    """PW-545: a zoom with no sea used to lack the harbour map, and the viewer (which indexes it) failed to load it."""
    el = np.linspace(500, 20, 40 * 30).reshape(40, 30)
    out, _ = HU.analyse_zoom({"elevation": el, "water": np.zeros(el.shape, np.uint8)}, 2.0)
    assert out["harbour"].shape == el.shape and out["harbour"].dtype == np.uint8 and not out["harbour"].any()


def test_finished_world_carries_the_layers_and_they_are_what_the_export_recomputes():
    from planet import world as W
    w = W.generate("plates", seed=2, level=4)
    L, grid = w["layers"], w["grid"]
    assert set(HU.NAMES) <= set(L)
    again, tab = HU.analyse_world(grid, L)
    for k in HU.NAMES:
        assert np.array_equal(again[k], L[k]), k
    for k in HU.CLASS_MAPS:
        assert L[k].max() < len(HU.LEGEND[k])
    land = L["elevation"] > 0
    assert not L["harbour"][land].any() and not L["fertile"][~land].any()  # (harbours are at sea, farms on land)
    assert L["pass_height"][L["pass"] > 0].min() > 0 and not L["pass"][~land].any()
    assert (L["fresh_km"] >= 0).all() and (L["fresh_water"][L["fresh_km"] == 0] == 3).all()
