"""The peoples' land use on a regional zoom (zoom_peoples.py, PW-667), on the synthetic world of test_zoom_vegetation:
fields on flat fertile ground, villages at water, trees out where land is cleared, and a zoom without peoples as it was."""

import numpy as np
import pytest

from planet import satellite as SAT
from planet import vegetation as V
from planet import world as W
from planet import zoom
from planet import zoom_peoples as ZP
from planet.geo import R_KM, xyz
from planet.grid import build_grid

CENTRE = (38.0, 10.0)


def _dist_km(g, lat, lon):
    c = xyz(np.radians(lat), np.radians(lon))
    return np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM


@pytest.fixture(scope="module")
def world():
    g = build_grid(5)
    d = _dist_km(g, *CENTRE)
    ridge = _dist_km(g, CENTRE[0] + 3.0, CENTRE[1])
    elev = np.where(d < 2200, 250 + 0.15 * (2200 - d) + 2800 * np.exp(-(ridge / 250) ** 2), -3000.0)
    extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2), "sediment_cover": np.where(elev > 0, 0.2, 6.0)}
    return W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 5}, erosion=0.0)


@pytest.fixture(scope="module")
def overlay(world):
    n = world["grid"].n
    land = np.asarray(world["layers"]["elevation"]) > 0
    lay = {"crop": np.where(land, 0.30, 0.0), "pasture": np.where(land, 0.20, 0.0), "burned": np.where(land, 0.05, 0.0),
           "managed": np.where(land, 0.10, 0.0), "people": np.where(land, 15.0, 0.0)}
    return {"id": "test00", "name": "test peoples", "world": "w", "layers": lay, "summary": {}, "cells": n}


@pytest.fixture(scope="module")
def plain(world):
    return zoom.build(world, *CENTRE, size_km=600, res_km=3, iterations=6, log=lambda *a: None)


@pytest.fixture(scope="module")
def settled(world, overlay):
    return zoom.build(world, *CENTRE, size_km=600, res_km=3, iterations=6, log=lambda *a: None, peoples=overlay)


def test_a_zoom_without_peoples_has_no_land_use(plain):
    assert "land_use" not in plain["layers"] and "peoples" not in plain["stats"]


def test_land_use_follows_the_run_where_the_ground_allows(plain, settled):
    L, W0 = settled["layers"], plain["layers"]
    lu = L["land_use"]
    land = (L["water"] == 0) & (L["ice"] == 0)
    assert (lu[~land] == 0).all(), "nothing on water or ice"
    crop = lu == ZP.CROP
    assert 0.05 < crop[land].mean() < 0.30, "cropland: some of the 30% the run asks for (ground that can't be ploughed is spared)"
    # fields lie on the better and flatter ground than the land's average
    assert L["fertile_score"][crop].mean() > L["fertile_score"][land].mean() + 2  # (percent)
    gy, gx = np.gradient(np.where(L["water"] == 0, L["elevation"], 0.0), 3000.0)  # (the ground, ice-covered too, as the code reads it)
    assert np.hypot(gx, gy)[crop].max() < ZP.SLOPE_CROP + 1e-9
    # villages are a few of the pixels, nearer rivers than the land is
    town = lu == ZP.TOWN
    assert 0 < town[land].mean() < 1.5 * ZP.TOWN_MAX
    assert L["river_dist"][town].mean() < L["river_dist"][land].mean()
    # the plants follow: fewer trees, fields bare of trees, the same wild ground elsewhere unchanged
    assert L["tree_cover"][land].mean() < W0["tree_cover"][land].mean() - 1.0
    assert L["tree_cover"][crop].max() <= 0.05 * W0["tree_cover"][crop].max() + 1e-6 or L["tree_cover"][crop].mean() < 3.0
    wild = land & (lu == 0)
    assert np.allclose(L["tree_cover"][wild], W0["tree_cover"][wild])
    assert (L["plant_cover"][crop] > 70).all() and (L["lai"][crop] == 2.0).all()
    assert (L["vegetation"][~land] == W0["vegetation"][~land]).all()
    assert (L["biome"][land] == V.TYPE_BIOME[L["vegetation"][land]]).all()
    # a managed wood keeps 70% of its canopy
    man = (lu == ZP.MANAGED) & (W0["tree_cover"] > 5)
    if man.any():
        assert np.allclose(L["tree_cover"][man] / W0["tree_cover"][man], 1 - ZP.LU.THIN, atol=0.02)
    st = settled["stats"]["peoples"]
    assert st["run"] == "test00" and st["cropland_km2"] > 0


def test_satellite_paints_the_cleared_land(plain, settled):
    sp, ss = plain["satellite"]["year"], settled["satellite"]["year"]
    assert sp.shape == ss.shape
    lu = settled["layers"]["land_use"]
    crop = lu == ZP.CROP
    assert np.abs(ss.astype(int) - sp.astype(int))[crop].mean() > 5, "fields change the colours"
    wild = (lu == 0) & (settled["layers"]["water"] == 0) & (settled["layers"]["tree_cover"] == plain["layers"]["tree_cover"])
    assert (ss[wild] == sp[wild]).all(), "wild ground keeps its colours"


def test_parcel_tone_is_blocky_and_deterministic():
    t = SAT.parcel_tone(30, 40, 1.0, 3.0).reshape(30, 40)
    assert np.array_equal(t, SAT.parcel_tone(30, 40, 1.0, 3.0).reshape(30, 40))
    assert (t[0:3, 0:3] == t[0, 0]).all() and t.std() > 0.2 and 0 <= t.min() and t.max() <= 1


def test_rank_selection_takes_the_share_per_cell():
    rng = np.random.default_rng(1)
    own = np.repeat(np.arange(4), 250)
    score = rng.random(1000)
    ok = np.ones(1000, bool)
    pick = ZP._select(score, ok, own, np.full(1000, 0.2), np.full(1000, 250.0))
    assert [int(pick[own == c].sum()) for c in range(4)] == [50] * 4
    assert score[pick].min() > np.sort(score[own == 0])[-60]  # the best-scoring ones
