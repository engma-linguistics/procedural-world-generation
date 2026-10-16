"""Soils in the regional zoom (PW-331; docs/proposals/soils.md step 6): the
mineral pass per pixel on the zoom's own terrain, the organic pass after the
zoom vegetation, the zoom's soil layers."""

import numpy as np

from planet import soils as SO
from planet import vegetation as V
from planet import zoom
from planet import zoom_terrain as ZT

from test_zoom_vegetation import veg_world, veg_zoom  # noqa: F401  (fixtures: a synthetic world and its zoom)

SOIL_KEYS = ("soil", "soil_depth", "soil_texture", "soil_water", "soil_fertility", "soil_drainage", "soil_carbon",
             "peat_depth", "permafrost", "loess")


def _pixels(n, **kw):
    """zoom_mineral on n pixels of a temperate humid lowland, with overrides."""
    a = dict(lat=np.full(n, 45.0), temp=np.full(n, 10.0), t_warm=np.full(n, 19.0), t_cold=np.full(n, 1.0),
             p_jul=np.full(n, 800.0), p_jan=np.full(n, 800.0), tilt=23.4, cloud_jul=None, cloud_jan=None,
             slope_tan=np.full(n, 0.01), res_km=2.0, rock=np.full(n, 8), landform=None, landform_age=None,
             glaciated_myr=None, plain=np.zeros(n), strip=np.zeros(n), hollow=np.zeros(n), loess_m=np.zeros(n),
             salt_near_=np.zeros(n, bool), ice_km=np.full(n, np.inf))
    a.update(kw)
    return SO.zoom_mineral(**a)


def _organic(m, grass=0.3, npp=500.0, fw=None):
    n = len(m["depth"])
    nu = np.zeros((V.NP, n))
    nu[V.IDX["C3G"]] = grass
    nu[V.IDX["TeBS"]] = 0.6
    vg = dict(eq=dict(nu=nu, burned=np.zeros(n)), sm=dict(npp=np.full(n, npp)), fw=np.zeros(n) if fw is None else fw)
    return SO.organic(m, vg)


def test_steep_pixels_thinner_floodplains_alluvium():
    tan = np.array([0.005, 0.05, 0.15, 0.3, 0.6, 0.005, 0.005, 0.005])
    plain = np.array([0, 0, 0, 0, 0, 0.6, 0, 0])
    hollow = np.array([0, 0, 0, 0, 0, 0, 1.0, 0])
    m = _pixels(len(tan), slope_tan=tan, plain=plain, hollow=hollow)
    o = _organic(m)
    d = m["depth"]
    assert (np.diff(d[:5]) <= 1e-9).all() and d[4] < 0.25 < d[0], "soil thins with the slope"
    assert o["types"][4] == SO.THIN
    assert o["types"][5] == SO.ALLUVIUM and d[5] >= 1.5, "a floodplain pixel gets deep river-laid alluvium"
    assert m["fertility"][5] > m["fertility"][0]
    assert d[6] >= SO.COLLUVIUM_M - 1e-9, "a hollow collects colluvium"
    assert m["cap1"].min() > 0 and (m["cap2"][5] > m["cap2"][4])
    # finer pixels see steeper slopes: the same tan is a gentler cell-measure slope at 0.5 km
    assert SO.zoom_slope(0.2, 0.5) < SO.zoom_slope(0.2, 2.0)


def test_glacier_forefield_is_young():
    m = _pixels(2, ice_km=np.array([1.0, 50.0]), temp=np.full(2, 4.0))
    assert m["age_cap"][0] <= SO.FOREFIELD_MYR * 1e6 + 1 and not np.isfinite(m["age_cap"][1])
    assert m["W"][0] < m["W"][1]


def test_zoom_soil_layers(veg_zoom):  # noqa: F811
    L = veg_zoom["layers"]
    for k in SOIL_KEYS:
        assert k in L and L[k].shape == L["elevation"].shape, k
        assert k in zoom.LAYER_DOC
    bare = (L["water"] == 0) & (L["ice"] <= 0)
    s = L["soil"]
    assert (s[~bare] == 0).all() and (s[bare] > 0).mean() > 0.99 and s.max() < len(SO.TYPES)
    assert 0 <= L["soil_depth"].min() and L["soil_depth"].max() <= SO.H_MAX + 1e-6
    assert 0 <= L["soil_fertility"].min() and L["soil_fertility"].max() <= 1
    assert L["soil_water"][bare].min() > 0 and L["soil_carbon"][bare].mean() > 1
    assert (L["permafrost"][~bare & (L["water"] > 0)] == 0).all()
    st = veg_zoom["stats"]["vegetation"]["soils"]
    assert sum(st["soil_pct"].values()) > 80 and st["seconds"] < 30
    # steep pixels are thinner than gentle ones; big rivers' plains alluvial or wet
    sea = L["water"] == 1
    tr = ZT.indices(np.where(sea, 0.0, L["elevation"]).ravel().astype(float), (L["water"] == 0).ravel(), sea.ravel(),
                    L["discharge"].ravel().astype(float), L["drainage_area"].ravel().astype(float),
                    np.full(L["elevation"].size, 38.0), L["elevation"].shape[1], L["elevation"].shape[0], 3.0)
    tan = tr["slope"].reshape(L["elevation"].shape)
    steep, gentle = bare & (tan > 0.15), bare & (tan < 0.02)
    if steep.sum() > 20 and gentle.sum() > 20:
        assert L["soil_depth"][steep].mean() < L["soil_depth"][gentle].mean()
    plain = (bare.ravel() & (tr["river_q"] >= 300) & (tr["river_dist"] <= 0)
             & (L["elevation"].ravel() - tr["river_h"] < 3))
    if plain.sum() >= 5:
        wet = np.isin(s.ravel()[plain], (SO.ALLUVIUM, SO.GLEY, SO.PEAT))
        assert wet.mean() > 0.5, "the big rivers' floodplains are alluvium (or gley, peat)"
