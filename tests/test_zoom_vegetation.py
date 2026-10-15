"""Zoom terrain indices (PW-196), seasons (PW-139) and vegetation (PW-214)
on a small synthetic world: a mid-latitude continent with a mountain range
and a dry interior, through world.finish (climate, rivers, vegetation)."""

import numpy as np
import pytest

from planet import vegetation as V
from planet import world as W
from planet import zoom
from planet import zoom_terrain as ZT
from planet import zoom_vegetation as ZVG
from planet.geo import R_KM, xyz
from planet.grid import build_grid

CENTRE = (38.0, 10.0)


def _dist_km(g, lat, lon):
    c = xyz(np.radians(lat), np.radians(lon))
    return np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM


# --------------------------------------------------------------------------- radiation index
def test_radiation_index_by_aspect():
    t = np.tan(np.radians(30))
    # flat; rising north (faces the equator in the north); rising south (faces the pole); faces east
    ge = np.array([0.0, 0.0, 0.0, -t, 0.0])
    gn = np.array([0.0, t, -t, 0.0, -t])
    lat = np.array([45.0, 45.0, 45.0, 45.0, -45.0])
    r = ZT.radiation(ge, gn, lat)
    assert np.allclose(r[:, 0], 1.0)
    jan, jun = r[0], r[5]
    assert jan[1] > 1.4 and jan[2] < 0.5, "a winter sun favours the equator-facing slope strongly"
    assert 0.75 < jun[2] < 1.0 and jun[1] < 1.1, "in summer the slopes differ less"
    assert 0.8 < jun[3] < 1.0 and abs(jan[3] - jun[3]) < 0.2
    # the southern hemisphere: a north-facing slope (rising south) is the sunny one
    assert jun[4] > 1.4


def test_nearest_and_twi():
    nx = ny = 40
    m = np.zeros(nx * ny, bool)
    m[20 * nx:21 * nx] = True  # a river along row 20
    d, src = ZT.nearest(m, nx, ny)
    assert d[20 * nx + 5] == 0 and d[25 * nx + 5] == 5 and src[25 * nx + 5] == 20 * nx + 5
    # a V valley draining along row 20: the floor is wetter than the ridges
    r = np.arange(ny)[:, None] * np.ones(nx)
    h = (np.abs(r - 20) * 30.0 + np.arange(nx)[None, :] * 0.5).ravel()
    area = np.where(m, 400.0, 4.0)
    out = ZT.indices(h, np.ones(nx * ny, bool), np.zeros(nx * ny, bool), np.where(m, 50.0, 0.0), area,
                     np.full(nx * ny, 40.0), nx, ny, 2.0)
    assert out["twi"][20 * nx + 10] > out["twi"][5 * nx + 10] + 3
    assert out["river_dist"][20 * nx + 10] == 0 and out["river_q"][5 * nx + 10] == 50.0


# --------------------------------------------------------------------------- a zoom with vegetation
@pytest.fixture(scope="module")
def veg_world():
    g = build_grid(5)
    d = _dist_km(g, *CENTRE)
    ridge = _dist_km(g, CENTRE[0] + 3.0, CENTRE[1])
    elev = np.where(d < 2200, 250 + 0.15 * (2200 - d) + 2800 * np.exp(-(ridge / 250) ** 2), -3000.0)
    land = elev > 0
    extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2),
             "sediment_cover": np.where(land, 0.2, 6.0)}
    return W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 5}, erosion=0.0)


@pytest.fixture(scope="module")
def veg_zoom(veg_world):
    return zoom.build(veg_world, *CENTRE, size_km=600, res_km=3, iterations=6, log=lambda *a: None)


def test_zoom_has_seasons_vegetation_and_indices(veg_zoom):
    L = veg_zoom["layers"]
    for k in ("temperature_jul", "temperature_jan", "precipitation_jul", "precipitation_jan", "vegetation",
              "tree_cover", "plant_cover", "lai", "canopy_height", "npp", "fire_return", "radiation_index", "twi",
              "river_dist", "coast_dist"):
        assert k in L and L[k].shape == L["elevation"].shape, k
        assert k in zoom.LAYER_DOC
    land = L["water"] == 0
    sea = L["water"] == 1
    # the northern summer is the warm one, lapse-corrected like the annual mean
    assert (L["temperature_jul"][land] > L["temperature_jan"][land]).all()
    hi, lo = land & (L["elevation"] > 1500), land & (L["elevation"] < 400)
    assert L["temperature_jul"][hi].mean() < L["temperature_jul"][lo].mean() - 5
    # rain: the half-years' mean is the year's
    assert np.allclose(0.5 * (L["precipitation_jul"] + L["precipitation_jan"])[land], L["precipitation"][land],
                       rtol=0.05, atol=5)
    # vegetation on the land only; no glacier or lake gets a plant type
    vt = L["vegetation"]
    assert (vt[sea] == 0).all() and (vt[land] > 0).all() and vt.max() < len(V.TYPES)
    assert (L["tree_cover"][~land] == 0).all() and 0 <= L["tree_cover"].min() and L["tree_cover"].max() <= 100 + 1e-6
    assert L["npp"][land].mean() > 50
    # biome is the vegetation's grouping on land
    assert (L["biome"][land] == V.TYPE_BIOME[vt[land]]).all()
    # the mountain has slopes facing both ways
    ri = L["radiation_index"][land]
    assert (ri < 0.95).mean() > 0.005 and (ri > 1.05).mean() > 0.005
    st = veg_zoom["stats"]["vegetation"]
    assert sum(st["vegetation_pct"].values()) > 80


def test_treeline_on_the_mountain(veg_zoom):
    L = veg_zoom["layers"]
    land = (L["water"] == 0) & (L["ice"] == 0)
    h, tc = L["elevation"], L["tree_cover"]
    top, low = land & (h > 2400), land & (h > 300) & (h < 900)
    if top.sum() > 20:
        assert tc[top].mean() < tc[low].mean()


def test_fractions_recomputed_match(data_root, veg_world):
    path = W.save(veg_world, "veg test")
    out = zoom.zoom(str(path), *CENTRE, size_km=300, res_km=3, iterations=6, log=lambda *a: None)
    meta, lay = zoom.load(out, decode=True)
    fr = ZVG.fractions(out)
    assert np.array_equal(fr["vegetation"], lay["vegetation"])
    tot = sum(fr[c] for c in V.CODES)
    land = (lay["water"] == 0) & (lay["ice"] == 0)
    assert tot.max() <= 1.0 + 1e-6 and (tot[land] > 0).mean() > 0.9
    # stored scaled layers decode to real units
    assert lay["lai"].dtype.kind == "f" and lay["lai"].max() < 12
