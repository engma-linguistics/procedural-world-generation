"""Vegetation (planet/vegetation.py, PW-187): the shared months, the
productivity and cover on idealised climates, the named types, the plant
groups' timeline, and the vegetation in runs and worlds."""

import numpy as np
import pytest

from planet import climate
from planet import vegetation as V
from planet.grid import build_grid


# --------------------------------------------------------------------------- months (PW-194)
def test_months_add_up():
    rng = np.random.default_rng(0)
    n = 200
    lat = rng.uniform(-80, 80, n)
    t_cold = rng.uniform(-40, 25, n)
    t_warm = t_cold + rng.uniform(0, 40, n)
    temp = 0.5 * (t_warm + t_cold) + rng.uniform(-1, 1, n)
    p_jul, p_jan = rng.uniform(0, 3000, n), rng.uniform(0, 3000, n)
    m = climate.months(lat, temp, t_warm, t_cold, p_jul, p_jan)
    # each half-year's months add up to its rate / 2 (mm/yr -> mm in six months)
    assert np.allclose(m["p"][3:9].sum(0), 0.5 * p_jul, rtol=1e-9, atol=1e-6)
    assert np.allclose(m["p"].sum(0) - m["p"][3:9].sum(0), 0.5 * p_jan, rtol=1e-9, atol=1e-6)
    assert (m["p"] >= 0).all()
    # PET is water_balance's
    wb = climate.water_balance(lat, temp, t_warm, t_cold, p_jul, p_jan)
    assert np.allclose(m["pet"].sum(0), wb["pet"])
    assert np.array_equal(m["pet"], climate.pet_months(lat, temp, t_warm, t_cold))
    # snow only where it freezes; what reaches the soil is at most the precipitation (+ melt of the pack)
    warm = t_cold > 3
    assert (m["snow"][:, warm] == 0).all()
    assert np.allclose(m["water"][:, warm], m["p"][:, warm])
    assert (m["gdd5"] >= 0).all() and (m["par"] > 0).any()


# --------------------------------------------------------------------------- idealised climates
CLIMATES = {  # temp, t_warm, t_cold, p_jul, p_jan (northern hemisphere cells), cloud
    "rainforest": (26.5, 27.5, 25.5, 2600, 2600, 0.5),
    "savanna": (25, 28, 22, 1900, 100, 0.4),
    "desert": (24, 33, 13, 40, 40, 0.1),
    "temperate": (10, 19, 1, 800, 700, 0.6),
    "boreal": (-3, 16, -22, 700, 300, 0.6),
    "tundra": (-12, 6, -28, 400, 150, 0.6),
}


@pytest.fixture(scope="module")
def ideal():
    """Every cell of a level-3 grid gets one of CLIMATES by its index (all
    land, flat, at mid-latitude geometry of their own cells)."""
    g = build_grid(3)
    names = list(CLIMATES)
    k = np.arange(g.n) % len(names)
    arr = np.array([CLIMATES[nm] for nm in names])[k]
    lat = np.asarray(g.lat)
    # (keep each climate on cells of a sensible latitude for its daylight: use |lat| bands)
    elev = np.random.default_rng(1).uniform(100.0, 700.0, g.n)  # hilly: no wide flat, waterlogged plains
    v = V.model(g, elev, arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3], arr[:, 4], 23.4, arr[:, 5], arr[:, 5])
    return g, k, names, v, lat


def _cells(ideal, name, band=(0, 90)):
    g, k, names, v, lat = ideal
    return (k == names.index(name)) & (np.abs(lat) >= band[0]) & (np.abs(lat) < band[1])


def test_npp_and_types_on_ideal_climates(ideal):
    g, k, names, v, lat = ideal
    npp, tree, cover = v["sm"]["npp"], v["sm"]["tree"], v["sm"]["cover"]
    nu = v["eq"]["nu"]
    rf = _cells(ideal, "rainforest", (0, 25))
    assert 600 < np.median(npp[rf]) < 1600 and np.median(tree[rf]) > 0.6
    assert (nu[V.IDX["TrBE"], rf] > nu[V.IDX["C4G"], rf]).mean() > 0.8
    assert np.isin(v["types"][rf], [1, 2, 3]).mean() > 0.8  # tropical forests
    de = _cells(ideal, "desert")
    assert np.median(npp[de]) < 120 and (cover[de] < 0.3).all()
    bo = _cells(ideal, "boreal", (45, 75))
    assert 100 < np.median(npp[bo]) < 600 and np.median(tree[bo]) > 0.5
    assert (nu[V.TREES][:, bo].argmax(0) >= 5).mean() > 0.8  # boreal tree types (BoNE, BoNS, BoBS)
    tu = _cells(ideal, "tundra", (55, 90))
    assert np.median(tree[tu]) < 0.1 and np.median(npp[tu]) < 250
    sv = _cells(ideal, "savanna", (5, 25))
    # a long dry season with grass burns; forest and savanna are both stable there (history decides)
    burns = v["eq"]["burned"][sv] > 0.02
    assert 0.2 < burns.mean() and (v["sm"]["tree"][sv][burns] < 0.4).all()
    assert np.median(nu[V.IDX["C4G"], sv]) > np.median(nu[V.IDX["C3G"], sv])
    te = _cells(ideal, "temperate", (35, 60))
    assert np.median(tree[te]) > 0.5 and 300 < np.median(npp[te]) < 1000


def test_envelopes_respected(ideal):
    g, k, names, v, lat = ideal
    env = V.envelope(v["s"])
    assert not ((v["eq"]["nu"] > 0) & ~env).any()
    # no tropical trees where winters freeze, no boreal ones in the tropics
    cold = v["s"]["tc"] < 10
    assert (v["eq"]["nu"][V.IDX["TrBE"], cold] == 0).all()
    assert (v["eq"]["nu"][V.IDX["BoNE"], v["s"]["tc"] > 0] == 0).all()
    assert ((v["eq"]["nu"].sum(0)) <= 1 + 1e-9).all()


def test_ice_lake_and_sea_cells():
    g = build_grid(3)
    n = g.n
    elev = np.where(np.arange(n) % 5 == 0, -100.0, 300.0)
    ice = np.where(np.arange(n) % 5 == 1, 500.0, 0.0)
    lake = np.arange(n) % 5 == 2
    t = np.full(n, 15.0)
    v = V.model(g, elev, t, t + 8, t - 8, np.full(n, 900.0), np.full(n, 700.0), lake=lake, ice=ice)
    assert (v["types"][elev <= 0] == 0).all()
    assert (v["types"][(ice > 0) & (elev > 0)] == V.T["ice"]).all()
    assert (v["types"][lake & (elev > 0)] == V.T["lake"]).all()
    assert (v["eq"]["nu"][:, (ice > 0) | lake | (elev <= 0)] == 0).all()
    L = V.world_layers(v)
    assert set(f"veg_{c}" for c in V.CODES) <= set(L)
    assert (L["plant_cover"] <= 100).all() and (L["tree_cover"] <= L["plant_cover"] + 1).all()


def test_legend_and_biome_grouping():
    leg = V.legend()
    assert [t["id"] for t in leg["types"]] == list(range(len(V.TYPES)))
    assert len(leg["pfts"]) == V.NP == 19
    ids = {b[0] for b in climate.BIOMES}
    assert set(V.TYPE_BIOME) <= ids
    assert V.biome_of(np.array([0, V.T["ice"], V.T["lake"]]), np.array([0, 0, 0])).tolist() == [0, 4, 3]


# --------------------------------------------------------------------------- plant groups (decision 3)
def test_group_windows_and_timeline():
    for end in (600.0, 1000.0, 2000.0):
        win = V.group_windows(0.0, end)
        d = end - max(16.0, 0.05 * end)
        assert win[0] == (0.0, 0.0)
        assert all(a <= b <= d + 1e-9 for a, b in win)
        assert all(win[k][0] <= win[k + 1][0] for k in range(len(win) - 1))
        # with no niche at all, each group still appears, at the latest by its window's end
        times = [float("nan")] * len(V.GROUPS)
        rng = np.random.default_rng(0)
        for t in np.arange(0, end + 4, 4.0):
            times = V.flora_update(times, t, 4.0, 0.0, end, np.zeros(len(V.GROUPS)), rng)
        assert all(np.isfinite(times)) and max(times) <= d + 4
        assert all(times[k] <= times[k + 1] for k in range(len(times) - 1))
        for (a, b), tg in zip(win, times):
            assert a - 4 <= tg <= b + 4
    # a big niche makes a group appear early in its window; draws are seeded
    times = [0.0, 40.0, 100.0, float("nan"), float("nan"), float("nan")]
    a, b = V.group_windows(0.0, 1000.0)[3]
    got = []
    for seed in range(20):
        rng, tt, t = np.random.default_rng(seed), list(times), a
        while not np.isfinite(tt[3]):
            tt = V.flora_update(tt, t, 4.0, 0.0, 1000.0, np.array([0, 0, 0, 0.8, 0, 0]), rng)
            t += 4.0
        got.append(tt[3])
    assert np.median(got) < 0.5 * (a + b)


def test_standins_fill_locked_niches():
    unlocked = V.unlocked_at([0.0, 50.0, 100.0, float("nan"), float("nan"), float("nan")], 200.0)
    assert unlocked[V.IDX["TeNE"]] and not unlocked[V.IDX["TrBE"]] and not unlocked[V.IDX["C3G"]]
    sub = V.standin_map(unlocked)
    assert sub[V.IDX["TeNE"], V.IDX["TrBE"]] and sub[V.IDX["Moss"], V.IDX["C3G"]]
    g = build_grid(3)
    n = g.n
    t = np.full(n, 26.0)
    v = V.model(g, np.full(n, 100.0), t, t + 1, t - 1, np.full(n, 2500.0), np.full(n, 2500.0), unlocked=unlocked)
    nu = v["eq"]["nu"]
    assert (nu[~unlocked] == 0).all()
    # conifer-like forest stands in for the rainforest: archaic, not bare
    low = np.abs(g.lat) < 25
    assert np.median(nu[V.IDX["TeNE"], low]) > 0.3 and np.median(v["sm"]["tree"][low]) > 0.3


# --------------------------------------------------------------------------- runs and worlds
def test_run_vegetation(sim4_60):
    sim = sim4_60
    land = sim.w_elev > 0
    assert sim.veg_frac.shape == (V.NP, sim.grid.n)
    assert (sim.npp[land] >= 0).all() and sim.npp[land].mean() > 50
    assert np.isfinite(sim.flora[0]) and sim.flora[0] <= 2.0
    assert ((sim.veg >= 0) & (sim.veg <= 1)).all()
    snap = sim.snapshot()
    assert (snap.vegetation[~land] == 0).all() and (snap.vegetation[land] > 0).mean() > 0.95
