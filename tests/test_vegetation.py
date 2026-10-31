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
    elev = np.where(g.lat < -20, -100.0, 300.0)  # (the sea: one body, PW-1229)
    ice = np.where((np.arange(n) % 5 == 1) & (elev > 0), 500.0, 0.0)
    lake = (np.arange(n) % 5 == 2) & (elev > 0)
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
    """Plant groups on Earth's calendar counted back from the run's end (PW-807): each within its window in Ma
    before now, by its deadline; a group whose window is before the run's start is there from the start."""
    for end in (300.0, 600.0, 1000.0, 2000.0):
        win = V.group_windows(end)
        assert all(a <= b for a, b in win)
        assert all(win[k][0] <= win[k + 1][0] for k in range(len(win) - 1))
        assert [round(end - b) for a, b in win] == [470, 420, 375, 120, 60, 25]  # the latest ages, Ma
        # with no niche at all, each group still appears, at the latest by its window's end
        times = [float("nan")] * len(V.GROUPS)
        rng = np.random.default_rng(0)
        for t in np.arange(0, end + 4, 4.0):
            times = V.flora_update(times, t, 4.0, end, np.zeros(len(V.GROUPS)), rng)
        assert all(np.isfinite(times)) and max(times) <= end - 25 + 4
        assert all(times[k] <= times[k + 1] for k in range(len(times) - 1))
        for (a, b), tg in zip(win, times):
            assert max(a, 0.0) - 4 <= tg <= max(b, 0.0) + 4
        assert V.land_plants(times, end) and not (end > 500 and V.land_plants(times, 0.0))
    # a 300 Myr run starts with land plants and forests already there
    times = V.flora_update([float("nan")] * 6, 0.0, 4.0, 300.0, np.zeros(6), np.random.default_rng(0))
    assert times[:3] == [0.0, 0.0, 0.0] and not np.isfinite(times[3])
    # a big niche makes a group appear early in its window; draws are seeded
    times = [0.0, 40.0, 100.0, float("nan"), float("nan"), float("nan")]
    a, b = V.group_windows(1000.0)[3]
    got = []
    for seed in range(20):
        rng, tt, t = np.random.default_rng(seed), list(times), a
        while not np.isfinite(tt[3]):
            tt = V.flora_update(tt, t, 4.0, 1000.0, np.array([0, 0, 0, 0.8, 0, 0]), rng)
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
    land = sim.land()  # (the snapshot's: also grounded ice whose bed has sunk below the sea since the last climate)
    assert (snap.vegetation[~land] == 0).all() and (snap.vegetation[land] > 0).mean() > 0.95


# --------------------------------------------------------------------------- fire (PW-234)
def test_fire_rate_fuel_age():
    """fire_rate: grass fuel is ready every year (the old GlobFIRM-like rate);
    shrubs' slowly built dead fuel adds the years to rebuild it."""
    w = 0.1
    assert V.fire_rate(0.0, 0.0, 0.3, w) == 0.0 and V.fire_rate(800.0, 0.0, 0.3, 0.0) == 0.0
    assert V.fire_rate(200.0, 40.0, 0.3, w) == 0.0  # never enough fuel
    assert np.isclose(V.fire_rate(800.0, 0.0, 0.3, w), w)  # fully fuelled grass: the weather's rate
    assert np.isclose(V.fire_rate(V.FUEL_MIN + 0.5 * V.FUEL_SPAN, 0.0, 0.3, w), 0.5 * w)
    # a shrubland whose fuel is mostly its own dead wood burns less often than a
    # grassland of the same fuel (years to rebuild it), but it does burn
    shrub = V.fire_rate(100.0, 500.0, 0.1, w)
    assert 0 < shrub < V.fire_rate(600.0, 0.0, 0.1, w)
    ready = -np.log(1 - (V.FUEL_MIN - 100.0) / 500.0) / 0.1
    assert np.isclose(1 / shrub, ready + 1 / w)


def test_mediterranean_scrub_burns_and_stays_scrub():
    """A summer-dry climate's sclerophyll scrub of low productivity burns
    every few decades to centuries (its fuel builds up) and stays
    shrub-dominated."""
    g = build_grid(3)
    n = g.n
    lat = np.abs(np.asarray(g.lat))
    elev = np.random.default_rng(2).uniform(100.0, 700.0, n)
    # hot dry summers, mild wet winters (Koppen Csa), 450 mm/yr (both hemispheres: p_jul is July's half-year)
    north = np.asarray(g.lat) >= 0
    p_s, p_w = np.full(n, 60.0), np.full(n, 840.0)
    v = V.model(g, elev, np.full(n, 16.0), np.full(n, 24.0), np.full(n, 9.0), np.where(north, p_s, p_w),
                np.where(north, p_w, p_s), 23.4, np.full(n, 0.3), np.full(n, 0.3))
    m = (lat > 30) & (lat < 42)
    sm, nu = v["sm"], v["eq"]["nu"]
    assert (v["types"][m] == V.T["Mediterranean scrub (maquis, chaparral, fynbos)"]).mean() > 0.5
    ret = sm["fire_return"][m]
    assert 10 < np.median(ret) < 400  # (none at all before PW-234)
    assert np.median(nu[V.IDX["SclS"], m]) > np.median((nu[V.IDX["C3G"]] + nu[V.IDX["C4G"]])[m])


# --------------------------------------------------------------------------- C3 and C4 grasses (PW-231)
def test_c3_quantum_yield():
    """C3 grass's efficiency falls with temperature (photorespiration) and
    rises with CO2; it equals C4 grass's at QY_CROSS today."""
    ci = 0.7 * V.CA_REF
    q = [V._q3(t, ci) for t in (10, 20, 30)]
    assert q[0] > q[1] > q[2] > 0
    assert V._q3(25, 2 * ci) > V._q3(25, ci) > V._q3(25, 0.5 * ci)
    c4 = V._KP[V.C4, 0] * V._ft_np(V.QY_CROSS, *V.PFTS[V.C4]["temp"])
    c3 = V._KP[V.C3, 0] * V._ft_np(V.QY_CROSS, *V.PFTS[V.C3]["temp"]) * V._q3(V.QY_CROSS, ci)
    assert np.isclose(c3, c4)


def test_c4_grass_follows_the_rain_season():
    """Same temperatures (warm summers, cool winters), different rain
    seasons: summer-rain grassland is mostly C4, winter-rain mostly C3
    (Still et al. 2003)."""
    g = build_grid(3)
    n = g.n
    lat = np.asarray(g.lat)
    north = lat >= 0
    elev = np.random.default_rng(3).uniform(100.0, 700.0, n)
    m = (np.abs(lat) > 25) & (np.abs(lat) < 35)
    out = {}
    for name, (p_s, p_w) in {"summer": (700.0, 100.0), "winter": (100.0, 700.0)}.items():
        pj, pa = np.where(north, p_s, p_w), np.where(north, p_w, p_s)
        v = V.model(g, elev, np.full(n, 18.0), np.full(n, 26.0), np.full(n, 10.0), pj, pa, 23.4,
                    np.full(n, 0.3), np.full(n, 0.3))
        nu = v["eq"]["nu"]
        c3, c4 = nu[V.C3, m], nu[V.C4, m]
        out[name] = np.median(c4 / np.maximum(c3 + c4, 1e-9))
    assert out["summer"] > 0.7 and out["winter"] < 0.5 and out["summer"] - out["winter"] > 0.3, out


def test_sclerophylls_need_a_dry_summer():
    """SclS (hard-leaved evergreen shrubs) is a summer-drought plant: it can't
    establish where most rain falls in the warm half-year (thorn savanna,
    steppe and forest instead), dry or humid, but it can where the summer is dry."""
    n = 3
    lat = np.full(n, 30.0)
    t, tw, tc = np.full(n, 17.0), np.full(n, 25.0), np.full(n, 9.0)
    p_jul = np.array([700.0, 80.0, 2400.0])  # dry summer-rain, dry winter-rain, humid summer-rain
    p_jan = np.array([80.0, 700.0, 1400.0])
    s = V.site(lat, t, tw, tc, p_jul, p_jan)
    ok = V.envelope(s)[V.IDX["SclS"]]
    assert list(ok) == [False, True, False]


# --------------------------------------------------------------------------- migration (PW-213)
def _hops(g, start):
    """Cells' graph distance from the start cells."""
    d = np.full(g.n, -1)
    d[start] = 0
    front = np.asarray(start)
    k = 0
    while len(front):
        k += 1
        nb = np.unique(np.concatenate([g.nbr_idx[g.nbr_off[i]:g.nbr_off[i + 1]] for i in front]))
        front = nb[d[nb] < 0]
        d[front] = k
    return d


def test_trees_spread_one_cell_per_step_and_stay_put():
    """PW-213: with the trees migration-limited a stand takes new ground only beside its own stands (one cell
    per step); without, seeds make forest everywhere at once; held, it doesn't spread at all."""
    g = build_grid(4)
    n = g.n
    t = np.full(n, 16.0)
    args = (g, np.full(n, 100.0), t, t + 6, t - 6, np.full(n, 1200.0), np.full(n, 1200.0))
    start = np.flatnonzero(g.lat > 70)
    nu0 = V.start_from_tree_cover(np.where(g.lat > 70, 0.8, 0.0))
    free = V.model(*args, nu0=V.start_from_tree_cover(np.zeros(n)), cheap=True)
    assert (free["sm"]["tree"] > 0.3).mean() > 0.8  # (nothing keeps it from being forest)
    hops = _hops(g, start)
    for steps in (1, 3):
        v = V.model(*args, nu0=nu0, cheap=True, steps=((steps, 480.0),), migrate=V.SPREAD, substeps=12)
        tree, seeds = v["eq"]["nu"][V.TREES].sum(0), v["eq"]["nu_raw"][V.TREES].sum(0)
        assert (tree[start] > 0.3).all()
        assert seeds[hops > steps].max() == 0, steps  # (not even a seed beyond one cell per step)
        assert tree[hops == steps].max() > 0.3  # (and the stand on the new ground grows up within the step)
    held = V.model(*args, nu0=nu0, cheap=True, steps=V.HELD_STEPS, migrate=V.HELD)
    assert held["eq"]["nu"][V.TREES].sum(0)[hops > 0].max() == 0
