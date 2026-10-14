"""Evaporation, runoff and lakes: the water balance closes and lakes behave
like lakes (fill and spill where it's wet, end their rivers where it's dry)."""

import numpy as np

from planet import climate, hydrology, timeline as T
from planet.geo import xyz
from planet.grid import build_grid


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
    wet = hydrology.lakes(g, elev, np.where(land, 2000.0, 0.0), aet, lake_evap)
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
