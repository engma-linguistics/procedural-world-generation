"""Coastal and shallow-sea life (planet/coastal.py, zoom/coastal.py; PW-188,
PW-209): the rules on hand-made layers, and the layers through world.finish
and the zoom on a small synthetic world."""

import numpy as np
import pytest

from planet import coastal as C
from planet import vegetation as V
from planet import world as W
from planet.zoom import regional as zoom
from planet.zoom import coastal as ZC
from planet.geo import R_KM, xyz
from planet.grid import build_grid


def _dist_km(g, lat, lon):
    return np.arccos(np.clip(g.centers @ xyz(np.radians(lat), np.radians(lon)), -1, 1)) * R_KM


@pytest.fixture(scope="module")
def g4():
    return build_grid(4)


def _layers(g, sst=27.0, swing=1.5, air_cold=22.0, coast_m=5.0, shelf_m=-20.0, wave=2.0, tide=3.0, rain=2000.0,
            salinity=35.0, upwelling=0.0, inland_m=400.0):
    """A round continent (radius 2500 km, centred on the equator) with low
    coastal land (coast_m) inside a shelf (shelf_m, 600 km wide) in a deep
    ocean; uniform sea and air. No rivers."""
    d = _dist_km(g, 0.0, 0.0)
    land = d < 2500
    elev = np.where(land, np.where(d > 2000, coast_m, inland_m), np.where(d < 3100, shelf_m, -4000.0))
    sea = elev <= 0
    n = g.n
    f = lambda v: np.full(n, float(v))  # noqa: E731
    return {"elevation": elev, "downstream": np.full(n, -1), "flow": f(0), "temperature": f(sst - 1),
            "warm_month": f(air_cold + 2 * swing + 4), "cold_month": f(air_cold), "precipitation": f(rain),
            "sst": np.where(sea, sst, 0.0), "sst_jul": np.where(sea, sst + swing, 0.0),
            "sst_jan": np.where(sea, sst - swing, 0.0), "salinity": np.where(sea, salinity, 0.0),
            "upwelling": np.where(sea, upwelling, 0.0), "wave_power": np.where(sea, wave, 0.0),
            "tide_range": np.where(sea, tide, 0.0)}


def _coast_land(g, L):
    sea = L["elevation"] <= 0
    return ~sea & (np.add.reduceat(sea[g.nbr_idx].astype(int), g.nbr_off[:-1]) > 0)


def test_layers_zero_on_land_and_deep_sea(g4):
    L = _layers(g4)
    out = C.world_layers(g4, L)
    sea, land, deep = L["elevation"] <= 0, L["elevation"] > 0, L["elevation"] < -1000
    for k in ("reef", "kelp", "seagrass"):
        assert np.all(out[k][land] == 0) and np.all(out[k][deep] == 0), k
        assert np.all((out[k] >= 0) & (out[k] <= 1)), k
    for k in ("mangrove", "salt_marsh"):
        assert np.all(out[k][sea] == 0), k
    assert out["reef"][sea].max() > 0.05, "a warm, clear, shallow shelf grows reefs"
    assert np.all(out["reef"] + out["kelp"] + out["seagrass"] <= 1 + 1e-9)


def test_no_reef_in_cold_sea(g4):
    assert C.world_layers(g4, _layers(g4, sst=15.0))["reef"].max() == 0
    # coldest month below Kleypas' ~16-18 C limit, though warm on average
    assert C.world_layers(g4, _layers(g4, sst=24.0, swing=8.5))["reef"].max() == 0
    # fresh water
    assert C.world_layers(g4, _layers(g4, salinity=15.0))["reef"].max() == 0


def test_no_living_reef_before_the_reef_builders(g4):
    """PW-892: a world taken before the run's skeletal reef builders (slice --ago 600) has no living reef;
    the flag comes from the world meta (its vegetation block, for a zoom) and defaults to on."""
    L = _layers(g4)
    assert C.world_layers(g4, L)["reef"].max() > 0
    assert C.world_layers(g4, L, {"reef_builders": False})["reef"].max() == 0
    assert C.environment(g4, L, {"vegetation": {"reef_builders": False}})["reef"].max() == 0
    assert C.environment(g4, L, {"vegetation": {"reef_builders": True}})["reef"].max() > 0


def test_mangroves_only_on_tidal_coast_cells(g4):
    L = _layers(g4)
    out = C.world_layers(g4, L)
    coast_land = _coast_land(g4, L)
    assert out["mangrove"][coast_land].max() > 0.05
    assert np.all(out["mangrove"][~coast_land] == 0), "only land cells next to the sea"
    assert np.all(out["salt_marsh"] == 0), "warm: mangroves, not salt marsh"
    # high coasts have little ground between the tides; big tides and shelter give more
    hi = C.world_layers(g4, _layers(g4, coast_m=300.0))["mangrove"][coast_land].mean()
    assert hi < 0.2 * out["mangrove"][coast_land].mean()
    exposed = C.world_layers(g4, _layers(g4, wave=40.0))["mangrove"][coast_land].mean()
    assert exposed < 0.3 * out["mangrove"][coast_land].mean()


def test_salt_marsh_where_too_cold_for_mangroves(g4):
    L = _layers(g4, sst=8.0, air_cold=0.0)
    out = C.world_layers(g4, L)
    coast_land = _coast_land(g4, L)
    assert out["mangrove"].max() == 0
    assert out["salt_marsh"][coast_land].max() > 0.05
    assert np.all(out["salt_marsh"][~coast_land] == 0)


def test_plant_groups_gate_mangroves_marsh_and_seagrass(g4):
    L = _layers(g4)
    none = np.zeros(V.NP, bool)
    out = C.world_layers(g4, L, unlocked=none)
    assert out["mangrove"].max() == 0 and out["seagrass"].max() == 0
    assert out["reef"].max() > 0, "corals don't wait for flowering plants"
    cold = C.world_layers(g4, _layers(g4, sst=8.0, air_cold=0.0), unlocked=V.unlocked_at([0, 0, 0, 0, None, None], 1))
    assert cold["salt_marsh"].max() == 0, "no salt marsh before grasses"


def test_kelp_needs_cool_water_and_rocky_shores(g4):
    rocky = dict(sst=10.0, air_cold=0.0, coast_m=600.0, wave=30.0)
    out = C.world_layers(g4, _layers(g4, **rocky))
    assert out["kelp"].max() > 0.05
    assert C.world_layers(g4, _layers(g4, **{**rocky, "sst": 26.0}))["kelp"].max() == 0
    low = {**rocky, "coast_m": 5.0, "inland_m": 5.0}
    assert C.world_layers(g4, _layers(g4, **low))["kelp"].max() < 0.2 * out["kelp"].max()
    # warm water with upwelling's nutrients: some; without: less
    warm = {**rocky, "sst": 16.5, "swing": 2.0}
    assert (C.world_layers(g4, _layers(g4, **warm, upwelling=3.0))["kelp"].max()
            > 1.5 * C.world_layers(g4, _layers(g4, **warm))["kelp"].max())


def test_river_mud_keeps_reefs_away(g4):
    L = _layers(g4)
    # a big river from high ground reaching the sea at the continent's east coast
    d = _dist_km(g4, 0.0, 21.0)
    mouth = int(np.argmin(np.where(_coast_land(g4, L), d, np.inf)))
    nb = g4.nbr_idx[g4.nbr_off[mouth]:g4.nbr_off[mouth + 1]]
    sea_nb = nb[L["elevation"][nb] <= 0][0]
    L["downstream"][mouth] = sea_nb
    L["elevation"][mouth] = 3000.0
    area = 4 * np.pi * R_KM ** 2 / g4.n
    L["flow"][mouth] = 50000.0 * 3.156e7 / (area * 1e6)  # 50,000 m^3/s
    mouths, load = C.river_loads(g4, L)
    assert list(mouths) == [mouth] and load[0] > 1000.0, load  # kg/s
    ssc = C.turbidity(g4, L)
    sea = L["elevation"] <= 0
    assert ssc[sea_nb] > 2 * C.SSC_BG, ssc[sea_nb]
    assert np.all(ssc[sea & (d > 3000)] < ssc[sea_nb]) and np.all(ssc[~sea] == 0)
    # muddy water (> ~10 mg/L) has no reefs
    muddy = np.where(sea, 20.0, 0.0)
    assert C.environment(g4, L, ssc=muddy)["reef"].max() == 0
    assert C.environment(g4, L, ssc=np.where(sea, C.SSC_BG, 0.0))["reef"].max() > 0.5


def test_resuspension_on_shallow_tidal_shelves(g4):
    """PW-323: a shallow, muddy shelf with a big tide is turbid without
    rivers, and loses most of its seagrass; the same shelf with a small
    tide and calm water, a hard floor, or deep water stays clear."""
    def mud_shelf(**kw):
        L = _layers(g4, sst=15.0, air_cold=8.0, **kw)
        L["sediment_cover"] = np.where(L["elevation"] <= 0, 2.0, 0.5)
        return L
    L = mud_shelf(tide=6.0, wave=5.0, shelf_m=-10.0)
    sea, shelf = L["elevation"] <= 0, (L["elevation"] <= 0) & (L["elevation"] > -100)
    ssc = C.turbidity(g4, L)
    assert np.median(ssc[shelf]) > 10, np.median(ssc[shelf])
    assert np.all(ssc[L["elevation"] < -1000] < 1.0)  # the deep ocean: clear
    assert np.all(ssc[~sea] == 0)
    calm = C.turbidity(g4, mud_shelf(tide=0.3, wave=0.5, shelf_m=-10.0))
    assert np.median(calm[shelf]) < 2.0, np.median(calm[shelf])
    hard = mud_shelf(tide=6.0, wave=5.0, shelf_m=-10.0)
    hard["surface_rock"] = np.full(g4.n, C.HARD_ROCKS[0])
    assert np.median(C.turbidity(g4, hard)[shelf]) < 2.0
    deep = mud_shelf(tide=6.0, wave=5.0, shelf_m=-150.0)  # (the tide's current still stirs a little up)
    assert np.median(C.turbidity(g4, deep)[shelf]) < 0.3 * np.median(ssc[shelf])
    # less light: less seagrass than on the calm shelf
    sg = C.world_layers(g4, L)["seagrass"][shelf].sum()
    sg_calm = C.world_layers(g4, mud_shelf(tide=0.3, wave=0.5, shelf_m=-10.0))["seagrass"][shelf].sum()
    assert sg < 0.5 * sg_calm, (sg, sg_calm)


def test_classifier_names_mangrove_and_salt_marsh():
    n = 4
    s = V.site(np.array([5.0, 5.0, 50.0, 50.0]), np.full(n, 26.0), np.full(n, 28.0), np.full(n, 24.0),
               np.full(n, 2000.0), np.full(n, 2000.0))
    nu = np.zeros((V.NP, n))
    nu[V.IDX["TrBE"]] = 0.9
    sm = dict(shade=nu, tree=np.full(n, 0.9), cover=np.full(n, 0.9), shrub=np.zeros(n), herb=np.zeros(n),
              lai=np.full(n, 5.0))
    coastal = {"mangrove": np.array([0.5, 0.1, 0.0, 0.0]), "salt_marsh": np.array([0.0, 0.0, 0.4, 0.1])}
    t = V.classify(s, {}, sm, np.full(n, 3.0), coastal=coastal)
    assert t[0] == V.T["mangrove forest"] and t[2] == V.T["salt marsh"]
    assert t[1] != V.T["mangrove forest"] and t[3] != V.T["salt marsh"], "under 30% of the cell: its land cover"


# --------------------------------------------------------------------------- through world.finish and the zoom
CENTRE = (8.0, 30.0)


@pytest.fixture(scope="module")
def coast_world():
    """A tropical continent with a wide low coastal plain and a shallow shelf."""
    g = build_grid(5)
    d = _dist_km(g, *CENTRE)
    elev = np.where(d < 1500, 4 + 0.6 * np.maximum(1500 - d, 0) ** 1.0, np.where(d < 1800, -25.0, -4000.0))
    land = elev > 0
    # (a carbonate shelf, as reef shelves are: its floor isn't mud the tides stir up, PW-323)
    from planet import surface as SF
    extra = {"rock": np.full(g.n, 3), "surface_rock": np.where(land, 8, SF.LIMESTONE),
             "sediment_cover": np.where(land, 1.0, 2.0)}
    return W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 5}, erosion=0.0)


def test_world_has_coastal_layers(coast_world):
    L = coast_world["layers"]
    sea = L["elevation"] <= 0
    for k in (*C.LAYERS, "turbidity", "upwelling"):
        assert k in L, k
    for k in ("reef", "kelp", "seagrass"):
        assert np.all(L[k][~sea] == 0), k
    for k in ("mangrove", "salt_marsh"):
        assert np.all(L[k][sea] == 0), k
    assert L["reef"].max() > 0 and L["mangrove"].max() > 0, "a warm shallow shelf and low tidal coast"
    t = np.asarray(L["vegetation"])
    assert np.all((t != V.T["mangrove forest"]) | (L["mangrove"] >= 30)), "named only where >= 30% of the cell"


def test_zoom_places_coastal_life(coast_world):
    lat, lon = CENTRE[0], CENTRE[1] + 1500 / 111.0
    z = zoom.build(coast_world, lat, lon, size_km=400, res_km=2, iterations=4, log=lambda *a: None)
    L = z["layers"]
    life, water = L["coastal_life"], L["water"]
    sea = water == 1
    assert np.all(~np.isin(life, (ZC.REEF, ZC.KELP, ZC.SEAGRASS)) | sea), "reefs, kelp, seagrass at sea"
    assert np.all(~np.isin(life, (ZC.MANGROVE, ZC.SALT_MARSH)) | (water == 0)), "mangroves and marsh on land"
    assert (life == ZC.REEF).any() or (life == ZC.SEAGRASS).any()
    m = life == ZC.MANGROVE
    if m.any():
        assert np.all(L["vegetation"][m] == V.T["mangrove forest"])
        assert np.all(L["coast_dist"][m] * 2 <= ZC.TIDAL_KM + 2)
    deep = sea & (L["elevation"] < -C.REEF_MAX_M)
    assert np.all(life[deep] != ZC.REEF)
    assert z["stats"]["coastal_life"].keys() == {n for k, (n, _) in ZC.LIFE.items() if k}
