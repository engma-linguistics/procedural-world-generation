"""PW-307 / PW-197: worlds store the true bed, and grounded ice on a bed below
sea level is land for every consumer (climate, rivers, lakes, coasts, the
sea's layers, the summary), as a run's Simulation.land() has it."""

import numpy as np
import pytest

from planet import climate, coastal, world as W
from planet.geo import is_land, world_land, xyz
from planet.grid import build_grid
from planet.tectonics.isostasy import grounded


@pytest.fixture(scope="module")
def marine():
    """A round continent (~60 deg across, 600 m high) whose middle carries
    an ice sheet 2 km thick, its bed pressed 300 m below the sea in a disc
    (a marine ice sheet), above it in a ring round that."""
    g = build_grid(4)
    c = xyz(np.radians(65.0), np.radians(30.0))
    d = np.degrees(np.arccos(np.clip(g.centers @ c, -1, 1)))
    elev = np.where(d < 30, 600.0, -3500.0)
    sub = d < 10
    elev = np.where(sub, -300.0, elev)
    ice = np.where(d < 16, 2000.0, 0.0)
    w = W.finish(g, elev, {"ice": ice}, {"method": "test", "seed": 0, "level": 4}, erosion=1.0,
                 erosion_iterations=4, ice=ice)
    return g, w, sub, d


def test_grounded_drops_ice_afloat():
    """Ice whose surface doesn't stand above the sea is afloat: left out, so the cell is sea."""
    e = np.array([-300.0, -300.0, 200.0, -50.0])
    ice = np.array([2500.0, 250.0, 100.0, 0.0])
    got = grounded(e, ice)
    assert got.tolist() == [2500.0, 0.0, 100.0, 0.0]
    assert is_land(e, got).tolist() == [True, False, True, False]
    assert np.array_equal(is_land(e), e > 0)


def test_true_bed_under_marine_ice_is_land(marine):
    g, w, sub, d = marine
    L = w["layers"]
    assert sub.sum() > 10
    # the bed is stored as it is, the ice on it
    assert (L["elevation"][sub] <= -250).all() and (L["ice"][sub] == 2000).all()
    land = world_land(L)
    assert land[sub].all() and land.sum() == (d < 30).sum()
    assert W.summarize(w)["land_pct"] == round(100 * land.mean(), 1)
    # the climate: land (ice cap), no sea temperature, salinity or currents there
    assert (L["climate"][sub] != climate.SEA_CLASS).all()
    for k in ("sst", "salinity", "sinking", "upwelling", "current_e", "current_n"):
        assert (L[k][sub] == 0).all(), k
    assert not np.isin(L["biome"][sub], (0, 1, 2)).any()  # (not deep sea, shallow sea or sea ice)


def test_rivers_dont_end_under_the_ice(marine):
    """No river reaches the sea through the ice: the sub-sea bed is no outlet
    and holds no lake (none on the ice); every river from the ice runs on
    to a real coast."""
    g, w, sub, d = marine
    L = w["layers"]
    land = world_land(L)
    down = L["downstream"]
    assert (down[sub] >= 0).all() and (L["lake_kind"][sub] == 0).all()
    for i in np.flatnonzero(sub):
        j, steps = i, 0
        while land[j]:
            assert down[j] >= 0 or L["lake_kind"][j] > 0, j  # (only a closed lake may end it on land)
            if down[j] < 0:
                break
            j, steps = down[j], steps + 1
            assert steps < g.n
        assert not land[j] or L["lake_kind"][j] > 0
    # the largest rivers' mouths are at the real coast (their next cell is sea)
    for r in W.summarize(w)["largest_rivers"]:
        assert not land[down[r["cell"]]]


def test_no_shore_under_the_ice(marine):
    """Waves, tides and coastal life are the sea's: none on the bed under the ice."""
    g, w, sub, d = marine
    L = w["layers"]
    assert (L["wave_power"][sub] == 0).all() and (L["tide_range"][sub] == 0).all()
    for k in coastal.LAYERS:
        assert (L[k][sub] == 0).all(), k
    assert (L["turbidity"][sub] == 0).all()
    # the sea next to the continent still gets them
    sea = ~world_land(L)
    coast = sea & (np.add.reduceat(world_land(L)[g.nbr_idx], g.nbr_off[:-1]) > 0)
    assert (L["tide_range"][coast] > 0).any() and (L["wave_power"][coast] > 0).any()


def test_zoom_builds_its_terrain_on_the_land_view(marine):
    """The zoom's terrain passes take land as ground above the sea, so they
    build on the world with that bed at 1 m and the ice surface kept
    (zoom.land_world), the coastline the world's; how far each cell's true
    bed lies below that is handed back, for the zoom to sink its bed under
    its glaciers (PW-356, tests/test_zoom_ice.py)."""
    from planet.zoom import land_world
    g, w, sub, d = marine
    view, sunk = land_world(w)
    L, Z = w["layers"], view["layers"]
    assert (Z["elevation"][sub] == 1).all()
    assert np.allclose((Z["elevation"] + Z["ice"])[sub], (L["elevation"] + L["ice"])[sub])
    assert np.array_equal(Z["elevation"] > 0, world_land(L))
    assert np.array_equal(Z["elevation"][~sub], L["elevation"][~sub])
    assert np.allclose(Z["elevation"] - sunk, L["elevation"]) and (sunk[~sub] == 0).all()


def test_erode_routes_over_the_ice_surface(monkeypatch):
    """PW-355: the world's erosion (hydrology.erode) routes the water over
    the ice surface under all ice, as rivers_and_lakes does, not along the
    bed: a bed falling east under a sheet whose surface falls west drains
    west (and the cutting is on the bed beneath)."""
    from planet import hydrology, kernels
    g = build_grid(4)
    c = xyz(np.radians(40.0), np.radians(30.0))
    d = np.degrees(np.arccos(np.clip(g.centers @ c, -1, 1)))
    x = (g.lon - 30.0 + 180.0) % 360.0 - 180.0  # deg east of the middle
    elev = np.where(d < 30, 1500.0 - 40.0 * x, -3500.0)  # (all above the sea on the continent)
    ice = np.where(d < 20, np.maximum(4000.0 + 20.0 * x - elev, 0.0), 0.0)
    iced = ice > 0
    assert iced.sum() > 50
    seen = {}
    real = kernels.stream_power

    def spy(h, down, order, f):
        seen.setdefault("down", down.copy())
        return real(h, down, order, f)

    monkeypatch.setattr(kernels, "stream_power", spy)
    n = len(elev)
    clim = {"runoff": np.full(n, 300.0), "aet": np.full(n, 300.0), "lake_evap": np.full(n, 1000.0)}
    out = hydrology.erode(g, elev, clim, iterations=1, ice=ice)
    down, surf = seen["down"], elev + ice
    assert (down[iced] >= 0).all()
    on = np.flatnonzero(iced)
    # every ice cell drains down the ice surface (westward), not down the bed
    assert (surf[down[on]] <= surf[on] + 0.05).all()
    assert (elev[down[on]] >= elev[on]).mean() > 0.5  # (old: along the bed, ~none)
    # the bed under the ice is what is cut (never raised)
    assert (out <= elev + 1e-9).all() and (out[iced] < elev[iced]).any()
