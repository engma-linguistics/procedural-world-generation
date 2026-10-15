"""Evaporation, runoff and lakes: the water balance closes and lakes behave
like lakes (fill and spill where it's wet, end their rivers where it's dry)."""

import numpy as np

from planet import climate, hydrology, kernels, timeline as T
from planet.geo import xyz
from planet.grid import build_grid
from planet.ocean import cell_area_km2


def test_water_balance_limits():
    """Runoff is never negative or more than the rain; a cold wet place
    sheds most of its rain, a hot dry one almost none."""
    lat = np.array([60.0, 25.0, 0.0])
    temp, t_warm, t_cold = np.array([2.0, 25.0, 26.0]), np.array([12.0, 34.0, 27.0]), np.array([-8.0, 15.0, 25.0])
    p = np.array([1200.0, 100.0, 2500.0])
    wb = climate.water_balance(lat, temp, t_warm, t_cold, p, p)
    assert (wb["runoff"] >= 0).all() and (wb["runoff"] <= p + 1e-9).all()
    assert np.allclose(wb["runoff"] + wb["aet"], p)
    assert wb["runoff"][0] > 0.6 * p[0]
    assert wb["runoff"][1] < 0.05 * p[1]
    assert wb["pet"][2] > wb["pet"][0] and (wb["lake_evap"] > wb["pet"]).all()


def _bowl():
    """A round continent (~35 deg across, 1500 m high) with a basin in the
    middle: 1000 m deep in the centre, rim at ~1500 m, one low notch (1300
    m) toward the coast."""
    g = build_grid(4)
    c = xyz(np.radians(20.0), np.radians(30.0))
    d = np.degrees(np.arccos(np.clip(g.centers @ c, -1, 1)))
    elev = np.where(d < 35, 1500.0, -3000.0)
    basin = d < 12
    elev = np.where(basin, 500.0 + 1000.0 * d / 12, elev)
    notch = (d >= 12) & (d < 30) & (np.abs(g.lat - 20) < 3) & (g.lon > 30)
    elev = np.where(notch, 1300.0 - 20 * (d - 12), elev)
    return g, elev, basin


def test_lake_spills_where_wet_and_closes_where_dry():
    g, elev, basin = _bowl()
    land = elev > 0
    aet = np.full(g.n, 300.0)
    lake_evap = np.full(g.n, 1500.0)
    # wet: a lot of runoff, the basin fills to its notch and the river flows on to the sea
    # (with the outlet's valley not cut down: test_big_river_cuts_its_outlet_down)
    wet = hydrology.lakes(g, elev, np.where(land, 2000.0, 0.0), aet, lake_evap, channel=0.0)
    flow, down, order, _ = hydrology.route(g, elev, wet)
    assert (wet["kind"][basin] == hydrology.OPEN_LAKE).sum() >= 0.8 * basin.sum()
    assert not wet["sink"].any()
    out = land & (down >= 0) & ~land[np.maximum(down, 0)]
    # the river leaving through the notch carries the basin's runoff less the lake's evaporation
    assert flow[out].max() > 0.9 * (2000.0 - (1500.0 - 300.0)) / 1000 * basin.sum()
    lv = wet["level"][wet["wet"]]
    assert np.allclose(lv, lv[0]) and (lv >= elev[wet["wet"]]).all()
    # dry: little runoff, the lake stops where its evaporation matches what flows in
    dry = hydrology.lakes(g, elev, np.where(land, 30.0, 0.0), aet, lake_evap)
    flow, down, order, _ = hydrology.route(g, elev, dry)
    closed = dry["kind"] == hydrology.CLOSED_LAKE
    assert 0 < closed.sum() < 0.5 * basin.sum()
    assert dry["sink"][closed].all()
    assert (dry["level"][closed] >= elev[closed]).all()
    endo = hydrology.endorheic(down, order, dry["sink"])
    assert endo[basin].all()  # nothing from the basin reaches the sea
    # water balance of the closed lake: inflow ~ evaporation off it (to within a cell)
    catch = (endo & land).sum() * 30.0 / 1000
    lost = closed.sum() * (1500.0 - 300.0) / 1000
    assert abs(catch - lost) <= (1500.0 - 300.0) / 1000


def test_big_river_cuts_its_outlet_down():
    """A river leaving a lake runs in a valley cut below its cells' mean
    height, deeper the bigger it is (PW-055): the wet bowl's lake drains
    down below its notch, more so with more water; the dry bowl's closed
    lake has no outlet and stays."""
    g, elev, basin = _bowl()
    land = elev > 0
    aet, lake_evap = np.full(g.n, 300.0), np.full(g.n, 1500.0)
    wet = []
    for runoff in (1000.0, 2000.0):
        lk = hydrology.lakes(g, elev, np.where(land, runoff, 0.0), aet, lake_evap)
        assert not lk["sink"].any() and (lk["level"][lk["wet"]] >= elev[lk["wet"]]).all()
        wet.append((lk["wet"] & basin).sum())
        if wet[-1]:
            assert (lk["kind"][lk["wet"] & basin] == hydrology.OPEN_LAKE).all()
            assert lk["level"][lk["wet"] & basin].max() < 1500.0 - 100  # (it spills over the rim, 1500 m, uncut)
    uncut = hydrology.lakes(g, elev, np.where(land, 1000.0, 0.0), aet, lake_evap, channel=0.0)
    assert 0 < wet[0] < 0.5 * (uncut["wet"] & basin).sum() and wet[1] < wet[0]
    dry = [hydrology.lakes(g, elev, np.where(land, 30.0, 0.0), aet, lake_evap, channel=ch) for ch in (0.0, None)]
    c0, c1 = ((d["kind"] == hydrology.CLOSED_LAKE) & basin for d in dry)
    assert c1.sum() >= 0.6 * c0.sum() > 0  # (a few cells at the divide can drain out to a cut valley instead)


def test_closed_lake_on_a_flat_floor_is_one_lake():
    """A deep basin whose floor is flat but rough (dips a few m deep between
    low saddles): the dips are part of the floor, not pits of their own, so
    a closed lake on it is one body of water, level, not a scatter of
    single-cell lakes (PW-058)."""
    g, elev, basin = _bowl()
    rng = np.random.default_rng(3)
    elev = np.where(basin, 500.0 + rng.uniform(0, 15, g.n), elev)  # 1000 m below the rim, rough to 15 m
    land = elev > 0
    lk = hydrology.lakes(g, elev, np.where(land, 100.0, 0.0), np.full(g.n, 300.0), np.full(g.n, 1500.0), channel=0.0)
    closed = (lk["kind"] == hydrology.CLOSED_LAKE) & basin  # (the notch ends in a pit of its own)
    assert 5 <= closed.sum() < 0.5 * basin.sum()
    assert g.components(closed)[1] == 1
    lv = lk["level"][closed]
    assert np.allclose(lv, lv[0])
    # every cell of the floor the lake's surface is above is under it
    assert not (basin & ~closed & (lk["bed"] < lv[0] - 0.5)).any()


def test_fill_shallow_fills_only_shallow_hollows():
    g = build_grid(4)
    rng = np.random.default_rng(0)
    e = np.where(np.arange(g.n) < 40, -100.0, rng.uniform(1, 200, g.n))
    a = np.ones(g.n)
    h, keep = kernels.fill_shallow(e, g.nbr_off, g.nbr_idx, 1e9, a, 0.0)  # every hollow: priority flood
    assert np.allclose(h, hydrology.priority_flood(g, e)[0], atol=0.1) and not keep.any()
    h, keep = kernels.fill_shallow(e, g.nbr_off, g.nbr_idx, 20.0, a, 0.0)
    assert (h >= e).all() and (h - e < 20.0 + 1.0).all()
    assert keep.any() and (h[keep] == e[keep]).sum() > 0.5 * keep.sum()


def test_fill_shallow_drains_wide_flat_basins():
    """Two bowls 40 m deep: a narrow one holds water, a wide one (flatter than
    min_slope from rim to middle) is a plain and drains."""
    g = build_grid(5)
    area = cell_area_km2(g)
    mid = np.array([[np.cos(0.35), 0, np.sin(0.35)], [0, np.cos(0.35), np.sin(0.35)]])  # 20 N; 0 E, 90 E
    d = np.arccos(np.clip(g.centers @ mid.T, -1, 1)) * 6371  # km from the bowls' middles
    e = 500.0 + 0.01 * (g.lat + 60)  # land falling gently south to the sea
    e[g.lat < -60] = -100.0
    e = np.where(d[:, 0] < 300, 460 + 40 * d[:, 0] / 300, e)  # ~300 km across radius: 0.13 m/km
    e = np.where(d[:, 1] < 900, 460 + 40 * d[:, 1] / 900, e)  # ~900 km radius: 0.044 m/km
    for slope, narrow, wide in ((0.0, True, True), (0.1, True, False)):
        h, keep = kernels.fill_shallow(e, g.nbr_off, g.nbr_idx, 20.0, area, slope)
        assert keep[np.argmin(d[:, 0])] == narrow and keep[np.argmin(d[:, 1])] == wide
        assert (h[d[:, 1] < 900] > 500).all() != wide  # drained: filled to the rim


def test_world_water_layers(sim4):
    w = T.world_from_sim(sim4)
    L = w["layers"]
    e, lv, kind = np.asarray(L["elevation"]), np.asarray(L["lake_level"]), np.asarray(L["lake_kind"])
    assert (lv >= e).all()
    assert set(np.unique(kind)) <= {0, 1, 2, 3}
    assert ((kind == 1) | (kind == 2))[np.asarray(L["lake"]) == 1].all()
    assert (lv[kind == 0] == e[kind == 0]).all()
    land = e > 0
    r, p = np.asarray(L["runoff"]), np.asarray(L["precipitation"])
    assert (r[land] <= p[land] + 1).all() and (r >= 0).all()
    assert 0.15 < r[land].sum() / max(p[land].sum(), 1) < 0.7
