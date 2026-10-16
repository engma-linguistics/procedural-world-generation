"""The polar climate (PW-332, PW-335, PW-336, PW-337): the air over frozen
seas, the ice sheets' own air carried along the winds, and the water vapour
reaching polar coasts and ice sheets."""

import numpy as np
import pytest

from planet import climate, icemass
from planet.climate import _geom
from planet.grid import build_grid


@pytest.fixture(scope="module")
def g4():
    return build_grid(4)


def _polar_continent(g):
    """A south polar continent (bed 300 m, poleward of 66 S) under a 2.5 km
    sheet poleward of 72 S, a bare margin between, sea elsewhere."""
    land = g.lat < -66
    elev = np.where(land, 300.0, -4000.0)
    ice = np.where(g.lat < -72, 2500.0, 0.0)
    return elev, ice


def test_frozen_sea_summer_air_near_freezing(g4):
    """PW-335: the summer air over a frozen sea is the summer sea surface
    open_share sees, never below freezing; over the permanently frozen polar
    sea of an ocean planet it is within a few C of freezing, not the old
    -10 C (or the land carry's +4 C)."""
    elev = np.full(g4.n, -4000.0)
    c = climate.compute(g4, elev, 0.0)
    assert (c["t_warm"] >= climate.FREEZE - 1e-9).all()
    pole = np.abs(g4.lat) > 80
    assert c["t_warm"][pole].max() < climate.FREEZE + 3.0


def test_sea_ice_air_levels_off(g4):
    """PW-337: in a deep icehouse the air over sea ice levels off (the
    surface inversion saturates) instead of cooling 4.5 C per C of the
    latitude's would-be sea temperature below freezing."""
    elev = np.full(g4.n, -4000.0)
    cold = climate.compute(g4, elev, -15.0)
    colder = climate.compute(g4, elev, -20.0)
    pole = np.abs(g4.lat) > 80
    assert cold["t_cold"].min() > -70.0  # (linear: ~-134 C)
    assert (colder["t_cold"][pole] < cold["t_cold"][pole]).all()  # still colder, but not without limit
    drop = cold["t_cold"][pole].mean() - colder["t_cold"][pole].mean()
    assert drop < 2.5 * 5.0  # (linear: 4.5 x 1.5 x 5 C ~ 34 C)


def test_sheet_air_is_carried(g4):
    """PW-336: a big polar sheet's own cold air is in the climate's air and
    the winds carry it on: its ground summers and the bare margin beside it
    are colder than with the ice's air left out (ice_air = 0), while the
    surface's own damping is just LOCAL."""
    elev, ice = _polar_continent(g4)
    with_air = climate.compute(g4, elev, 0.0, ice=ice)
    without = climate.compute(g4, elev, 0.0, ice=ice, ice_air=np.zeros(g4.n))
    on = ice > 0
    margin = (elev > 0) & ~on
    assert on.sum() > 10 and margin.sum() > 5
    tw_with, tw_without = with_air["ground"][0], without["ground"][0]
    assert (tw_with[on] - tw_without[on]).mean() < -5.0
    assert (tw_with[margin] - tw_without[margin]).mean() < -0.5
    assert np.allclose(icemass.sheet_cover(g4, ice), icemass.LOCAL)
    m = icemass.air_mass(g4, ice)
    assert (m[~on] == 0).all() and m[on].max() <= 1.0 and m[on].mean() > 0.3


def test_polar_drift_is_the_polar_cells_meridional_part(g4):
    """PW-332: polar_drift is wind()'s equatorward drift poleward of 60 deg
    and nothing else, so the vapour's wind (wind - drift) has no meridional
    part there and is unchanged equatorward of it."""
    north = _geom(g4)["north"]
    d = climate.polar_drift(g4)
    vn = (d * north).sum(1)
    a = np.abs(g4.lat)
    assert (vn[a < 60] == 0).all()
    assert (vn[a > 62] * np.sign(g4.lat[a > 62]) < 0).all()  # equatorward
    w = climate.wind(g4) - d
    assert np.abs((w * north).sum(1)[a > 61]).max() < 1e-9


def test_ice_sheet_lifts_the_rain(g4):
    """PW-332: the rain kernel sees an ice sheet's surface, not its bed. The
    surface air (t_air, on the ice) reduced to sea level is LAPSE x the
    surface height warmer, not just x the bed's (the air mass over a dome
    was ~16 C too cold for 2.5 km of ice), the moist static energy counts
    the height."""
    elev, ice = _polar_continent(g4)
    t_air = np.full(g4.n, -20.0)
    sst = np.full(g4.n, 2.0)
    v = climate.wind(g4)
    t_sl = np.zeros(g4.n)
    bed = climate._season_inputs(g4, elev, t_air, sst, v, 0.0, t_sl, climate.TUNE)
    top = climate._season_inputs(g4, elev, t_air, sst, v, 0.0, t_sl, climate.TUNE, surf=elev + ice)
    on = ice > 0
    assert np.allclose(top["t_sl"][on] - bed["t_sl"][on], climate.LAPSE * ice[on])
    assert (top["mse_t"][on] - bed["mse_t"][on] > 20.0).all()
    sea = elev <= 0
    assert np.array_equal(bed["qs"][sea], top["qs"][sea])
