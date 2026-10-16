"""Soils (planet/soils.py, PW-185): the types follow their rules on
synthetic inputs, water capacity stays in bounds, carbon only where plants
grow, loess downwind of its sources, the climate memory, the vegetation
hand-off, and soils on a world."""

import numpy as np
import pytest

from planet import soils as SO
from planet import vegetation as V
from planet.grid import build_grid
from planet.surface import ROCKS

ROCK = {r[1]: r[0] for r in ROCKS}


@pytest.fixture(scope="module")
def g():
    return build_grid(4)


def mineral(g, temp=10.0, p=800.0, elev=None, rock="sediment", **kw):
    """Pass 1 on a uniform climate (temp C, p mm/yr, both half-years alike;
    a 10 C seasonal swing) over flat land at 200 m, unless given."""
    n = g.n
    full = lambda x: np.broadcast_to(np.asarray(x, float), (n,)).copy()  # noqa: E731
    t = full(temp)
    e = full(200.0) if elev is None else np.asarray(elev, float)
    r = np.full(n, ROCK[rock]) if isinstance(rock, str) else np.asarray(rock)
    return SO.mineral(g, e, t, t + 5, t - 5, full(p), full(p), rock=r, **kw)


def veg(n, npp=0.0, grass=0.0, fw=0.0, conifer=0.0, burned=0.0):
    """A stand-in vegetation.model result: NPP (g C/m2/yr), grass and conifer cover, flooded share."""
    nu = np.zeros((V.NP, n))
    nu[V.IDX["C3G"]] = grass
    nu[V.IDX["BoNE"]] = conifer
    full = lambda x: np.broadcast_to(np.asarray(x, float), (n,)).copy()  # noqa: E731
    return {"eq": {"nu": nu, "burned": full(burned)}, "sm": {"npp": full(npp)}, "fw": full(fw)}


def types(g, m, **v):
    return SO.organic(m, veg(g.n, **v))["types"]


def mid(g, m, **v):
    """The types at mid-latitudes (25-55 deg), where a uniform climate means what it says (the
    potential evaporation, so the moisture index, follows the sun)."""
    return types(g, m, **v)[(np.abs(g.lat) >= 25) & (np.abs(g.lat) <= 55)]


def mostly(t, tid, share=0.9):
    return (np.asarray(t) == tid).mean() >= share


# --------------------------------------------------------------------------- the types
def test_no_soil_under_ice_lakes_and_sea(g):
    n = g.n
    elev = np.where(np.arange(n) % 3 == 0, -100.0, 200.0)
    ice = np.where(np.arange(n) % 3 == 1, 500.0, 0.0)
    m = mineral(g, elev=elev, ice=ice)
    t = types(g, m, npp=500)
    assert (t[elev <= 0] == SO.NONE).all() and (t[ice > 0] == SO.NONE).all()
    assert (t[(elev > 0) & (ice <= 0)] != SO.NONE).all()
    lake = np.zeros(n, int)
    lake[::5] = 1
    m = mineral(g, lake_kind=lake)
    assert (types(g, m, npp=500)[lake == 1] == SO.NONE).all()


def test_types_follow_their_rules(g):
    # deep tropical weathering on an old flat shield: leached red tropical soil
    assert mostly(mid(g, mineral(g, 26.0, 2500.0, rock="craton"), npp=900), SO.FERRALSOL)
    # continuous permafrost: frozen tundra soil (a cold, nearly snowless steppe)
    assert mostly(mid(g, mineral(g, -12.0, 200.0), npp=100), SO.FROZEN)
    # steep wet mountains: thin stony soil
    rng = np.random.default_rng(1)
    steep = 1000 + 8000 * rng.random(g.n)  # (~20 m/km between level-4 cells)
    assert mostly(mid(g, mineral(g, 8.0, 2000.0, elev=steep, rock="granite"), npp=500), SO.THIN, 0.6)
    # hyper-arid on basalt: bare rock the wind scours (thin) or desert pavement soil; semi-arid: caliche
    assert np.isin(mid(g, mineral(g, 22.0, 60.0, rock="flood_basalt"), npp=20), (SO.THIN, SO.GYPSIC)).all()
    # hyper-arid on loose sediment: the wind winnows it to loose sand
    assert mostly(mid(g, mineral(g, 22.0, 60.0, rock="sediment"), npp=20), SO.SAND)
    assert mostly(mid(g, mineral(g, 18.0, 300.0, rock="limestone"), npp=150), SO.CALCIC, 0.6)
    # cool, sub-humid grassland with plenty of carbon: black earth; drier: chestnut steppe soil
    assert mostly(mid(g, mineral(g, 6.0, 450.0), npp=500, grass=0.9), SO.CHERNOZEM, 0.6)
    assert mostly(mid(g, mineral(g, 6.0, 300.0), npp=350, grass=0.9), SO.CHESTNUT, 0.6)
    # the same climates under forest: no black earth
    assert not (mid(g, mineral(g, 6.0, 450.0), npp=500, grass=0.0) == SO.CHERNOZEM).any()
    # a wet, cool, waterlogged mire: peat; flooded but dry: no peat
    assert mostly(mid(g, mineral(g, 2.0, 900.0), npp=350, fw=0.6, conifer=0.3), SO.PEAT)
    assert not (mid(g, mineral(g, 25.0, 300.0), npp=300, fw=0.6) == SO.PEAT).any()
    # cool and humid on sandstone: podzol
    assert mostly(mid(g, mineral(g, 4.0, 1200.0, rock="sandstone"), npp=400, conifer=0.7), SO.PODZOL)
    # beside a young arc volcano in a humid climate: volcanic ash soil; old tuff has weathered out of it
    from planet import landform as LF
    arc = dict(landform=np.full(g.n, LF.ARC_CLASS), landform_age=np.full(g.n, 0.01))
    assert mostly(mid(g, mineral(g, 14.0, 1500.0, rock="arc", **arc), npp=600), SO.ANDOSOL)
    assert not (mid(g, mineral(g, 26.0, 2500.0, rock="tuff"), npp=600) == SO.ANDOSOL).any()
    # salt pans: salt-crusted soil
    lk = np.zeros(g.n, int)
    lk[::4] = 3
    t = types(g, mineral(g, 20.0, 150.0, lake_kind=lk), npp=50)
    assert (t[lk == 3] == SO.SALT).all()


def test_steep_ground_thin_shields_deep_and_old(g):
    rng = np.random.default_rng(2)
    rough = 200 + 6000 * rng.random(g.n)
    flat, steep = mineral(g, 15.0, 1000.0, rock="craton"), mineral(g, 15.0, 1000.0, elev=rough, rock="craton")
    assert np.median(steep["depth"]) < 0.5 * np.median(flat["depth"])
    assert np.median(flat["age"]) > 10 * np.median(steep["age"])
    assert (flat["depth"] <= SO.H_MAX).all() and (steep["depth"] >= 0).all()
    # a just-deglaciated shield: thin, young soil
    fresh = mineral(g, 2.0, 800.0, rock="craton", glaciated_myr=np.full(g.n, 0.01))
    assert np.median(fresh["depth"]) < 0.5 * np.median(mineral(g, 2.0, 800.0, rock="craton")["depth"])
    assert (fresh["age"] <= 0.01e6 + 1).all()


def test_water_capacity_bounds(g):
    rng = np.random.default_rng(3)
    for rock in ("sandstone", "shale", "craton", "sediment"):
        for temp, p in ((25, 2000), (10, 600), (20, 100), (-5, 300)):
            m = mineral(g, temp, p, elev=200 + 2000 * rng.random(g.n), rock=rock)
            land = m["land"]
            assert (m["cap1"] >= 0).all() and (m["cap2"] >= 0).all()
            assert (m["cap1"][land] <= SO.AWC_PEAT * 0.3 * SO.CAP_SCALE[0] + 1e-9).all()
            assert (m["cap2"][land] <= SO.AWC_PEAT * 1.2 * SO.CAP_SCALE[1] + 1e-9).all()
            # thin soils hold less than deep ones of the same parent
            thin, deep = m["depth"] < 0.3, m["depth"] > 1.5
            if thin.any() and deep.any():
                assert (m["cap1"] + m["cap2"])[thin].mean() < (m["cap1"] + m["cap2"])[deep].mean()
            o = SO.organic(m, veg(g.n, npp=300))
            assert (o["water"] >= 0).all() and (o["water"] <= SO.AWC_PEAT * 1.5 + 1e-9).all()
            assert ((o["fertility"] >= 0) & (o["fertility"] <= 1)).all()
            assert (o["drainage"][land] >= 1).all() and (o["drainage"][land] <= 5).all()
    # the fertility factor stays mild (decision 6A)
    assert ((m["f_soil"] >= 0.85 / SO.F_NORM - 1e-9) & (m["f_soil"] <= 1.1 / SO.F_NORM + 1e-9)).all()


def test_carbon_only_where_vegetation(g):
    m = mineral(g, 5.0, 900.0)
    o = SO.organic(m, veg(g.n, npp=0.0, fw=0.6))
    assert (o["carbon"] == 0).all() and (o["peat_depth"] == 0).all()
    o = SO.organic(m, veg(g.n, npp=400.0, fw=0.6))
    assert (o["carbon"][m["land"]] > 0).all() and (o["peat_depth"][m["land"]] > 0).all()
    # grass stores more than forest of the same NPP; colder soils more than warm ones
    grass, forest = SO.organic(m, veg(g.n, npp=400, grass=1.0)), SO.organic(m, veg(g.n, npp=400))
    assert (grass["carbon"] > forest["carbon"]).all()
    warm = SO.organic(mineral(g, 25.0, 900.0), veg(g.n, npp=400))
    assert np.median(warm["carbon"]) < np.median(forest["carbon"])


def test_loess_downwind_of_its_source(g):
    n = g.n
    src = np.zeros(n)
    i = int(np.argmin(np.abs(g.lat) + np.abs(g.lon)))  # (0, 0)
    src[i] = 1.0
    east = (np.ones(n), np.zeros(n))  # a steady west wind blowing east
    dep = SO.loess(g, src, np.ones(n), [east])
    near = np.abs(g.lat) < 15
    downwind, upwind = near & (g.lon > 5) & (g.lon < 40), near & (g.lon < -5) & (g.lon > -40)
    assert dep[downwind].sum() > 3 * dep[upwind].sum()
    # it settles over ~LOESS_KM: most of it within ~4 settling lengths
    assert dep[near & (g.lon > -5) & (g.lon < 4 * SO.LOESS_KM / 111)].sum() > 0.8 * dep.sum()
    # nothing settles on bare ground (it is blown on), and none at sea
    assert SO.loess(g, src, np.zeros(n), [east]).max() < 1e-3 * dep.max()
    sea = g.lon > 10
    assert (SO.loess(g, src, np.ones(n), [east], sea=sea)[sea] == 0).all()


def test_climate_memory(g):
    n = g.n
    times = np.arange(0, 41, 4.0)
    const = np.full((len(times), n), 12.0)
    mem = SO.climate_memory(times, const, const * 50, 40.0)
    assert np.allclose(mem["temp"], 12.0) and np.allclose(mem["precip"], 600.0)
    # a climate that warmed 1 C per Myr: the mean over the last 8 Myr is 4 C below today's
    ramp = times[:, None] + np.zeros(n)
    mem = SO.climate_memory(times, ramp, ramp, 40.0)
    k = list(mem["ages"]).index(8)
    assert np.allclose(mem["temp"][k], 36.0) and np.allclose(mem["now_temp"], 40.0)
    # soils remember it in proportion to their age (none for a young one)
    age = np.where(np.arange(n) % 2 == 0, 1e3, 8e6)
    t_eff, _ = SO._remembered(mem, age, np.full(n, 20.0), np.full(n, 500.0))
    assert np.allclose(t_eff[age < 1e4], 20.0, atol=0.01) and np.allclose(t_eff[age > 1e6], 16.0, atol=0.01)
    # with the plates: a cell's past climate is read where its ground was
    lon_field = np.broadcast_to(g.lon, (len(times), n))
    v = np.cross([0.0, 0.0, 0.01], g.centers)  # everything drifts east, 0.01 rad/Myr
    mem = SO.climate_memory(times, lon_field, np.ones((len(times), n)), 40.0, g, v)
    eq = np.abs(g.lat) < 10
    d = (mem["temp"][list(mem["ages"]).index(16)] - mem["now_temp"])[eq & (np.abs(g.lon) < 90)]
    assert np.median(d) < -2.0  # came from the west


def test_vegetation_reads_the_soil(g):
    n = g.n
    t = np.full(n, 22.0)
    p = np.full(n, 900.0)
    e = np.full(n, 200.0)
    m = mineral(g, 22.0, 900.0, rock="sandstone")
    a = V.model(g, e, t, t + 5, t - 5, p, p, soil=m)
    assert np.allclose(a["s"]["cap1"], m["cap1"]) and np.allclose(a["s"]["cap2"], m["cap2"])
    m2 = dict(m, cap1=m["cap1"] * 2, cap2=m["cap2"] * 2)
    b = V.model(g, e, t, t + 5, t - 5, p, p, soil=m2)
    assert b["sm"]["npp"].mean() > a["sm"]["npp"].mean()  # more water held, more growth in a seasonal climate
    m3 = dict(m, f_soil=np.full(n, 1.1))
    c = V.model(g, e, t, t + 5, t - 5, p, p, soil=m3)
    assert c["sm"]["npp"].mean() > V.model(g, e, t, t + 5, t - 5, p, p, soil=dict(m, f_soil=np.full(n, 0.85)))["sm"]["npp"].mean()


@pytest.mark.slow
def test_world_soils(sim4):
    from planet import timeline as T
    w = T.world_from_sim(sim4)
    L = w["layers"]
    land = (L["elevation"] > 0) & (L["ice"] <= 0) & (L["lake"] == 0)
    shore = np.asarray(L["elevation"]) == 0  # (the stored layer rounds: a cell at +0.4 m is land)
    soil = np.asarray(L["soil"])
    assert (soil[~land & ~shore] == SO.NONE).all() and (soil[land] > 0).mean() > 0.95
    assert (np.asarray(L["soil_depth"]) <= SO.H_MAX).all()
    # no one type covers most of the land
    share = np.bincount(soil[land], minlength=len(SO.TYPES)) / land.sum()
    assert share.max() < 0.6
    assert (np.asarray(L["soil_carbon"])[~land & ~shore] == 0).all()
