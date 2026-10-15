"""Zoom glaciers (PW-127) on a small synthetic world: a tropical volcano-like
massif with an iced summit rising from warm lowlands. Ice must sit where the
pixel's own summer is cold, reach below that only as tongues, and never
cover the warm valley floors around (the coarse ice used to be smeared over
whole cells, 2-3 km below the summit)."""

import numpy as np
import pytest

from planet import hydrology, zoom
from planet.climate import LAPSE
from planet.geo import R_KM, xyz
from planet.grid import build_grid

PEAK = (2.0, 3.0)  # lat, lon of the summit
WARM_SL = 22.0  # C: warmest month at sea level


def _dist_km(g, lat, lon):
    c = xyz(np.radians(lat), np.radians(lon))
    return np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM


def _zoom(rain):
    g = build_grid(5)
    d0 = _dist_km(g, 0.0, 0.0)
    elev = np.where(d0 < 2500, 200 + 0.1 * (2500 - d0) + 5200 * np.exp(-(_dist_km(g, *PEAK) / 380) ** 2), -3000.0)
    land = elev > 0
    precip = np.full(g.n, rain)
    c = {"runoff": 0.5 * precip, "aet": 0.5 * precip, "lake_evap": np.full(g.n, 300.0)}
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c)
    # the coarse ice where the cell's summer is below 1 C, as earth.ice_sheets would
    # put it; the world's temperatures are on the ice surface (climate.ice_surface,
    # no white-top cooling in the tropics)
    ground = WARM_SL - LAPSE * np.maximum(elev, 0)
    ice = np.where(land & (ground < 1.0), 400.0, 0.0)
    surf = ground - LAPSE * ice
    warm = np.where(ice > 0, np.minimum(surf, 0.5 * np.maximum(surf, 0)), ground)
    layers = {
        "elevation": np.round(elev), "precipitation": precip, "temperature": warm - 4.0,
        "warm_month": warm, "cold_month": warm - 8.0, "flow": flow, "downstream": down,
        "lake": lk["wet"].astype(int), "rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2),
        "climate": np.full(g.n, 2), "ice": ice, "sediment_cover": np.where(land, 0.2, 6.0),
    }
    assert (ice > 0).sum() >= 2, "the synthetic summit should hold coarse ice"
    w = {"grid": g, "layers": layers, "meta": {"level": 5}}
    return zoom.build(w, *PEAK, size_km=900, res_km=3, iterations=6, log=lambda *a: None)


@pytest.fixture(scope="module")
def ice_zoom():
    return _zoom(1800.0)


def test_ice_on_the_cold_summit(ice_zoom):
    L = ice_zoom["layers"]
    h, ice = L["elevation"], L["ice"] > 0
    summer = WARM_SL - LAPSE * np.maximum(h, 0)
    top = (summer < -2) & (L["water"] == 0)
    assert top.sum() > 50
    assert ice[top].mean() > 0.6, "the summit, well above the snowline, is mostly ice"


def test_no_ice_on_the_warm_floor(ice_zoom):
    L = ice_zoom["layers"]
    h, ice = L["elevation"], L["ice"] > 0
    summer = WARM_SL - LAPSE * np.maximum(h, 0)
    assert ice.any()
    # the coarse iced cells reach far down the massif's flanks: none of that is ice
    assert not (ice & (summer > 12)).any(), "no ice on ground with 12 C+ summers"
    # (with 1.8 m of rain a year, snow outlasts summers of up to ~5 C on bare
    # ground, give or take the noise: a maritime snowline, PW-159); below that,
    # only tongues: a small share of the ice
    assert (ice & (summer > 8)).sum() < 0.08 * ice.sum()


def test_snowline_follows_snowfall(ice_zoom):
    """The same massif with a sixth of the rain (it erodes less, so its
    terrain differs): the snow lasts only where the summers are colder (a
    dry, continental snowline; PW-159)."""
    def line(L):
        """The bare-ground summer (C) where half the dry land is ice."""
        h, ice = L["elevation"], L["ice"] > 0
        summer = WARM_SL - LAPSE * np.maximum(h, 0)
        dry_land = L["water"] == 0
        for t in np.arange(-4.0, 14.0, 0.5):
            m = dry_land & (summer >= t) & (summer < t + 1.0)
            if m.sum() > 50 and ice[m].mean() < 0.5:
                return t
        return 14.0

    wet, dry = line(ice_zoom["layers"]), line(_zoom(300.0)["layers"])
    assert 2.0 < wet < 7.0
    assert dry < wet - 2.0


def test_ice_layer_is_thickness(ice_zoom):
    L = ice_zoom["layers"]
    ice = L["ice"]
    assert (ice[ice > 0] >= 1).all()
    assert (L["biome"][ice > 0] == 4).all() and not ((L["biome"] == 4) & (ice <= 0)).any()
