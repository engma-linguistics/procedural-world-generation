"""Glacial time zoom (planet/timezoom/): bookkeeping and sanity, on the
session's level-4 simulation (fast)."""

import json
import numpy as np
import pytest

from planet import icemass, orbit as O, timeline as T, timezoom as Z
from planet.timezoom import params as P
from planet.timezoom.forcing import orbit_k, own_k
from planet.timezoom.geometry import geometry
from planet.timezoom.ice import shelf_step

import seeds

NO_ORBIT = dict(obliquity_amp=0.0, ecc_mean=0.0, ecc_100=0.0, ecc_400=0.0, orbit_ref="mean")


@pytest.fixture(scope="module")
def cold_src(sim4):
    """sim4's moment, made an icehouse (8 C colder) so there's ice to move."""
    src = Z.source_from_sim(sim4)
    src["dT"] = src["dT"] - 8.0
    return src


@pytest.fixture(scope="module")
def cold_run(cold_src):
    return Z.simulate(cold_src, kyr=40, step=0.5, every=2.0)


def test_glacial_cooling_turns_forest_to_tundra_and_cools_further(sources4):
    """PW-450: plants grown to balance with the start, then on a climate 4 C colder, lose forest toward the
    pole; the lying snow it no longer hides brightens the ground, which cools the land (the local
    correction) and the planet (the global term, in dTg). On each of the L4 worlds (seeds.SEEDS4) that has a
    boreal forest over seasonal snow (_boreal_snow: the premise's prerequisite, PW-645), at least
    seeds.PASS_RATE_L4 of them (one world is a chaotic run's draw: PW-640, PW-643)."""
    seeds.check_rate("forest to tundra", seeds.run_case(_forest_case, sources4), rate=seeds.PASS_RATE_L4)


# The premise (the boreal forest's loss over lying snow outweighs the darkening below 40 deg as cooling greens the
# low latitudes: PW-645) needs a boreal forest over seasonal snow. Eligible: the start's forest poleward of 40 deg (the
# test's own band) lies under snow at least a season of the year, on its tree-weighted mean. A season is a quarter
# of the year (3 of 12 months). The planet's own snow and forest, read at the start, before the cooling, never F.
# (On main's 120 L4 worlds, seeds 1-24 in three draws and 25-72: 78 of 98 eligible pass, 9 of 22 ineligible.)
SEASON = 3 / 12


def _boreal_snow(g, tilt, c, tree, open_, area):
    """The start's forest poleward of 40 deg: the share of the year it lies under snow (tree-weighted, 0..1)."""
    from planet import climate
    sc = climate.snow_cover(g.lat, tilt, c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"], climate.TUNE)
    m = open_ & (np.abs(g.lat) >= 40)
    w = (tree * area)[m]
    return float((w * sc.mean(0)[m]).sum() / w.sum()) if w.sum() > 0 else 0.0


def _forest_case(src, out):
    """One world's assertions (as the single-seed test on sim4 had them); its numbers in out."""
    from planet import climate
    from planet.timezoom.plants import Plants

    g, tilt = src["grid"], src["tilt"]
    elev, H = np.asarray(src["elev"], float), np.maximum(np.asarray(src["ice"], float), 0.0)
    grounded = (H > 1.0) & (elev > 0)
    surf = np.where(grounded, elev + H, elev)
    area = geometry(g)["area"]
    pl = Plants(g, src, Z.TZParams(), tilt, area)

    def compute(dT):
        return lambda veg: climate.compute(g, surf, src["dT"] + dT, tilt, veg=veg)

    c0 = pl.step(0.0, compute(0.0)(None), surf, grounded, H, 0.0, compute(0.0))
    tree0 = pl.tree.copy()
    out.update(boreal_snow=_boreal_snow(g, tilt, c0, tree0, (surf > 0) & ~grounded, area))
    if out["boreal_snow"] < SEASON:  # (no boreal forest over seasonal snow: the premise's prerequisite is missing)
        raise seeds.Ineligible
    assert pl.series[-1]["F_wm2"] == 0.0  # (the start is the reference)
    c = compute(-4.0)(pl.feedback(grounded))
    t0 = c["temp"].copy()
    c = pl.step(10.0, c, surf, grounded, H, -1.0, compute(-4.0))
    lost = (surf > 0) & ~grounded & (np.abs(g.lat) > 40) & (tree0 - pl.tree > 0.2)
    out.update(run_dT=float(src["dT"]), lost=int(lost.sum()),
               cooling=float((c["temp"] - t0)[lost].mean()) if lost.any() else float("nan"),
               F_wm2=float(pl.series[-1]["F_wm2"]), dT_target=float(pl.dT_target))
    assert lost.sum() >= 5
    assert (c["temp"] - t0)[lost].mean() < -0.1  # the snow it hid now lies open
    assert pl.series[-1]["F_wm2"] < 0 and pl.dT_target < 0


def test_insolation():
    """Global annual mean = S0/4; no tilt and a circular orbit: the poles get
    nothing; Earth today: 65N midsummer ~480-520 W/m2."""
    lat = O.BAND_LAT
    w = np.cos(np.radians(lat))
    q = O.insolation(23.44, 0.0167, 283.0)
    assert abs((q.mean(1) * w).sum() / w.sum() - O.S0 / 4 * (1 / np.sqrt(1 - 0.0167**2))) < 2
    assert O.insolation(0.0, 0.0, 0.0, np.array([90.0, -90.0])).max() < 1e-6
    assert 450 < O.insolation(23.44, 0.0167, 283.0, np.array([65.0]))[0, 2:4].max() < 530


def test_ice_and_sea_level_bookkeeping(cold_src, cold_run):
    r = cold_run
    H = r["state"]["H"]
    assert np.isfinite(H).all() and (H >= 0).all()
    assert (r["data"]["ice"] >= 0).all()
    b = r["budget"]
    # flow conserves ice exactly; volume changes only by mass balance and calving
    assert abs((b["V_end"] - b["V0"]) - (b["smb"] - b["calved"])) < 1e-6 * max(b["V0"], 1e12)
    # sea level is the change of the sea water the ice holds, spread over the starting ocean
    assert b["Vaf0"] <= b["V0"]
    for f in r["frames"]:
        s = f["stats"]
        want = -(s["ice_sea_equiv_mkm3"] * 1e15 - b["Vaf0"]) / b["ocean_area"]
        # (sea level follows the ice one step late: timezoom's fixed point takes one pass per step)
        assert abs(s["sea_level_change_m"] - want) < 0.5 + 1e-3 * abs(want), f["t"]
        assert s["sea_level_m"] == pytest.approx(cold_src["sea_level"] + s["sea_level_change_m"], abs=0.11)
    # something happened (an 8 C colder world grows ice) and sea level followed
    assert r["frames"][-1]["stats"]["sea_level_change_m"] < -1


def test_deterministic(cold_src, cold_run):
    again = Z.simulate(cold_src, kyr=40, step=0.5, every=2.0)
    for k, v in cold_run["data"].items():
        assert np.array_equal(v, again["data"][k]), k
    assert np.array_equal(cold_run["series"], again["series"])


def test_warm_unforced_stays_ice_free(sim4):
    """A greenhouse era with no orbital forcing: no ice appears. High peaks
    are capped first: a 5 km mountain keeps glaciers even in a hothouse."""
    src = Z.source_from_sim(sim4)
    src["elev"] = np.minimum(src["elev"], 1500.0)
    src["dT"] = src["dT"] + 8.0
    src["ice"] = np.zeros_like(src["ice"])
    r = Z.simulate(src, kyr=30, step=0.5, every=10.0, params=Z.TZParams(**NO_ORBIT))
    assert all(f["stats"]["ice_volume_mkm3"] < 0.01 for f in r["frames"])
    assert abs(r["frames"][-1]["stats"]["sea_level_change_m"]) < 0.1


def test_orbit_moves_the_ice(cold_src):
    """Same world with and without orbital cycles: the cycles change the ice."""
    a = Z.simulate(cold_src, kyr=20, step=0.5, every=10.0, params=Z.TZParams(**NO_ORBIT))
    b = Z.simulate(cold_src, kyr=20, step=0.5, every=10.0, params=Z.TZParams(phases="zero", orbit_ref="mean"))
    assert not np.allclose(a["state"]["H"], b["state"]["H"])


def test_saved_run_format(cold_src, cold_run, data_root):
    """Written in the run format the viewer reads, marked as a time zoom."""
    out = Z.save(cold_run, cold_src, kyr=40, step=0.5, every=2.0)
    run, arr = T.load_frames(out)
    m = run["meta"]
    assert run["kind"] == m["kind"] == "timezoom" and m["time_unit"] == "kyr"
    assert m["source_run"] == "sim" and m["kyr"] == 40 and "code" in m
    nf, n = len(run["frames"]), cold_src["grid"].n
    for k in Z.LAYERS:
        assert arr[k].shape == (nf, n), k
    for k in Z.STATIC:
        assert arr[k].shape == (1, n), k
    assert [f["t"] for f in run["frames"]] == [2.0 * i for i in range(nf)]
    for k in ("plates", "land_pct", "landmasses", "largest_landmass_pct", "max_elev_m", "global_temp_c",
              "sea_level_m", "ice_pct", "mean_speed_cmyr", "max_speed_cmyr"):  # what the viewer shows
        assert k in run["frames"][0]["stats"], k
    assert (out / "run.txt").exists()
    idx = json.loads((data_root / "runs" / "index.json").read_text())
    assert idx[0]["kind"] == "timezoom" and idx[0]["at_myr"] == cold_src["at"]
    with pytest.raises(SystemExit):
        T.slice_world(out, 0.0)


def test_glacial_index_cooling(cold_src, cold_run):
    """The zoom's global change is the glacial index's (cycle.py) plus the plants': -I x the cooling, which
    scales with the land poleward of the snowline (and is reported with its sea-level target)."""
    c = cold_run["cycle"]
    assert c["cooling_c"] > 0 and c["target_m"] > 0 and 0 < c["snowline_land_share"] < 1
    for f in cold_run["frames"]:
        s = f["stats"]
        assert 0.0 <= s["glacial_index"] <= 1.0 and s["dT_global"] <= -s["glacial_index"] * c["cooling_c"] + 1.0
    off = Z.simulate(cold_src, kyr=10, step=0.5, every=2.0, params=Z.TZParams(index="off", veg="local"))
    assert all(f["stats"]["dT_global"] == 0.0 and f["stats"]["glacial_index"] == 0.0 for f in off["frames"])


def test_bed_settles_under_the_ice(cold_src, cold_run):
    """Glacial isostasy (PW-189): the bed relaxes (iso_tau 3 kyr) toward the
    settled dip under the ice, the run's isostasy.ice_load (flexure), from a
    start that was already settled under its own ice. A bed relaxing on
    iso_tau under a changing load lags it by about the load change of its
    last iso_tau, so the tolerance takes each cell's own load change over
    the last iso_tau (the frames' grounded ice; median over the cells) on
    top of 5% of the dip. (The lag is the cell's, not the sheet's net
    volume: ice that moves within a sheet of steady volume still leaves
    its beds lagging, PW-680.)"""
    from planet.tectonics.isostasy import ice_load
    s = cold_run["state"]
    g = cold_src["grid"]
    p = Z.TZParams()
    H0 = np.maximum(np.asarray(cold_src["ice"], float), 0.0)
    flt = 1 - P.RHO_I / P.RHO_W
    H = np.where(s["bed"] + s["H"] > s["sl"] + flt * s["H"], s["H"], 0.0)  # (grounded: a shelf floats, PW-367)
    want = cold_src["elev"] + ice_load(g, H0, p.iso_ratio, p.flex_km) - ice_load(g, H, p.iso_ratio, p.flex_km)
    grew = H > H0 + 500
    assert grew.any()
    bed = s["bed"] + s["cut"] - s["till"] - s["rock_iso"]  # (the bed without the glacial carving, PW-037)
    assert (bed[grew] < cold_src["elev"][grew]).all()  # pressed down where the ice grew
    t = np.array([f["t"] for f in cold_run["frames"]])
    ice = np.asarray(cold_run["data"]["ice"], float)  # (each frame's grounded ice: the bed's load)
    tb = t[-1] - p.iso_tau
    k = int(np.searchsorted(t, tb)) - 1
    w = (tb - t[k]) / (t[k + 1] - t[k])
    load_then = (1 - w) * ice_load(g, ice[k], p.iso_ratio, p.flex_km) + w * ice_load(g, ice[k + 1], p.iso_ratio, p.flex_km)
    lag = np.median(np.abs(ice_load(g, ice[-1], p.iso_ratio, p.flex_km) - load_then)[grew])
    tol = 0.05 * np.median((H - H0)[grew]) * p.iso_ratio + lag + 20
    assert np.median(np.abs(bed - want)[grew]) < tol


# --------------------------------------------------------------------------
# Glacial carving (PW-037)
# --------------------------------------------------------------------------
def test_carving_conserves_rock(cold_src, cold_run):
    """What the ice erodes is carried in it or dropped as till (volume
    conserved); it erodes only under a thawed bed; till lies under or beside
    where ice has been; the stored imprint grows frame by frame."""
    from planet.timezoom.kernels import dilate
    s, g = cold_run["state"], cold_src["grid"]
    area = geometry(g)["area"]
    cut, till, debris = (s[k] for k in ("cut", "till", "debris"))
    till = till + s["outwash"] + s["loess"]  # (what the ice took ends as till, outwash or loess, PW-497)
    assert (cut >= 0).all() and (till >= 0).all() and (debris >= 0).all()
    vol = (cut * area).sum()
    assert vol > 0
    assert abs(vol - ((till + debris) * area).sum()) < 1e-9 * vol
    assert not (cut > 0)[s["wet_kyr"] <= 0].any()  # only under a thawed bed
    assert (s["slide_km"] > 0).any()
    # (grounded ice at some step: the frames every 2 kyr miss ice that grounded and calved in between)
    iced = (cold_run["data"]["ice"] > 0).any(0) | (s["wet_kyr"] > 0)
    near = dilate(iced, g.nbr_off, g.nbr_idx, 6)  # (the fan, the meltwater and the wind carry debris a few cells; L4 cells are 480 km)
    assert not (till > 0.1)[~near].any()
    e = cold_run["data"]["glacial_erosion"].astype(int)
    assert (np.diff(e, axis=0) >= 0).all() and e[-1].max() > 0


def test_debris_routing(cold_src):
    """deposit.py: a fan, a sandur and loess spread a point source over several cells (planet-relative
    lengths), the volume exactly conserved, the sea's fan not reaching land, the wind's only downwind."""
    from planet.timezoom.deposit import Deposits
    g = cold_src["grid"]
    G = geometry(g)
    area = G["area"]
    d = Deposits(g, G, area, Z.TZParams())
    i = int(np.argmin(np.abs(g.lat - 45) + np.abs(g.lon - 10)))
    x = np.zeros(g.n)
    x[i] = 100.0
    bed = -500.0 + 300.0 * np.sin(g.lat / 20.0)  # a sloping floor
    fan = d.fan(x, bed, 0.0)
    assert abs((fan * area).sum() - (x * area).sum()) < 1e-9 * (x * area).sum()
    assert (fan > 1.0).sum() >= 3 and fan.max() < 0.7 * x[i]  # spread over cells, not piled in one
    land = bed.copy()
    land[g.lat > 60] = 500.0  # land to the north: the sea's fan stays in the sea
    assert d.fan(x, land, 0.0)[g.lat > 60].sum() == 0
    wind = np.zeros((g.n, 3))
    wind += 5.0 * G_east(g)
    lo = d.wind(x, wind)
    assert abs((lo * area).sum() - (x * area).sum()) < 1e-9 * (x * area).sum()
    shift = (lo * ((g.centers - g.centers[i]) @ G_east(g)[i])).sum() / lo.sum()
    assert shift > 0.0  # (its centroid is east of the source: downwind)
    ow = d.outwash(x, bed + 1000.0 * (g.lat), np.ones(g.n, bool))
    assert abs((ow * area).sum() - (x * area).sum()) < 1e-9 * (x * area).sum()


def G_east(g):
    from planet.climate import _geom
    return _geom(g)["east"]


def test_no_carving(cold_src):
    """carving=False leaves the bed to the ice load alone (no imprint)."""
    r = Z.simulate(cold_src, kyr=6, step=0.5, every=2.0, params=Z.TZParams(carving=False))
    assert not r["state"]["cut"].any() and not r["state"]["till"].any()
    assert not r["data"]["glacial_erosion"].any()


def test_thawed_bed():
    """Robin's column: a thin or temperate column is thawed, a thick one
    under a very cold surface frozen; snow sinking through the ice
    (accumulation) keeps the bed colder; geothermal heat, or the flow's own
    heat at the bed, thaws it."""
    from planet.timezoom.kernels import thawed
    assert thawed(300.0, -2.0, 0.0, 0.065) == 1.0
    assert thawed(1000.0, -45.0, 0.05, 0.065) == 0.0
    assert thawed(3000.0, -30.0, 0.0, 0.065) == 1.0  # conduction alone: 93 C warmer at the bed
    assert thawed(3000.0, -30.0, 0.3, 0.065) < thawed(3000.0, -30.0, 0.0, 0.065)
    assert thawed(1000.0, -25.0, 0.3, 0.065) < 1.0 == thawed(1000.0, -25.0, 0.3, 0.065 + 0.3)  # (fast ice's heat)


def test_glacial_erosion_rule():
    """Erosion = k x erodibility x sliding speed; a basin stops deepening
    where the bed rises toward the ice's way out more than `adverse` x the
    surface falls (supercooling); a frozen bed doesn't erode."""
    from planet.timezoom.kernels import glacial_erosion
    # three cells in a row, 0 - 1 - 2; the ice flows from 0 to 2
    off = np.array([0, 1, 3, 4])
    idx = np.array([1, 0, 2, 1])
    H = np.array([1500.0, 1400.0, 1000.0])
    act = np.arange(3)
    k, dt = 4e-6, 500.0
    u = np.full(3, 100.0) * dt  # (speed x time)
    w = np.zeros(3)
    acc, erod = np.zeros(3), np.ones(3)
    for bed2, ts, deepens in ((-100.0, -1.0, True), (300.0, -1.0, False), (-100.0, -60.0, False)):
        bed = np.array([200.0, 0.0, bed2])  # cell 1's way down is cell 2 (its surface: 1000 + bed2)
        cut, wet = np.zeros(3), np.zeros(3)
        glacial_erosion(H, bed, -1e4, 0.1, act, off, idx, u, w, np.full(3, ts), acc, 0.065, 0.5, erod, k, 1.0, 1.5,
                        dt, 1500.0, cut, wet)
        assert (wet == 1.0).all() == (ts > -10)
        assert (cut[1] > 0) == deepens, (bed2, ts)
        if deepens:
            assert cut[1] == pytest.approx(k * 0.5 * 100.0 * dt)


def test_deep_grounded_ice_stands(sim4):
    """Thick ice grounded in deep water with no open sea beside it stands
    (West Antarctica's true bed, ~1.7-2.3 km deep at L6-L7 under ~3 km of
    ice, PW-361); only an unresolved basin deeper than calve_depth (PW-199's
    ~4 km) breaks up in place."""
    g = sim4.grid
    src = Z.source_from_sim(sim4)
    elev, ice = src["elev"].copy(), np.zeros(g.n)
    nb = lambda i: g.nbr_idx[g.nbr_off[i]:g.nbr_off[i + 1]]
    # two inland cells: their neighbours (and theirs) on land
    inland = [i for i in range(g.n) if elev[i] > 200 and all(elev[j] > 200 and (elev[nb(j)] > 200).all() for j in nb(i))]
    inland.sort(key=lambda i: -abs(g.lat[i]))  # (the coldest first: the ice around shouldn't melt away and drain it)
    a, b = inland[0], next(i for i in inland if not set(nb(i)) & set(nb(inland[0])) and i not in nb(inland[0]))
    for c, depth, h in ((a, 2000.0, 3200.0), (b, 4000.0, 5500.0)):
        elev[c], ice[c] = -depth, h
        ice[nb(c)] = np.maximum(2500.0, h - depth - elev[nb(c)] + 100.0)  # (their surface above the cell's)
    src.update(elev=elev, ice=ice, dT=src["dT"] - 30.0)  # (cold: the ice neither melts nor flows much in one step)
    r = Z.simulate(src, kyr=0.5, step=0.5, every=0.5, params=Z.TZParams(**NO_ORBIT))
    H = r["state"]["H"]
    assert H[a] > 2500, H[a]  # grounded in 2 km of water: stands
    assert H[b] < 0.5 * 5500, H[b]  # in 4 km: breaks up in place


def test_orbit_response_mixes_each_surface_own(sim4):
    """Bright ice feels the air mass around it, each surface at its own
    response: an ice cap on an island in the open sea gets about the sea's
    and the ice's (~0.2-0.3 of the land's), not the land's (PW-114: the old
    mix counted the sea as fully absorbing land); bare land far from ice
    keeps its own response, the open sea its own."""
    g = sim4.grid
    p = Z.TZParams(orbit_resp="seasons")
    centre = int(np.argmin(np.abs(g.lat - 70.0)))
    d = np.degrees(np.arccos(np.clip(g.centers @ g.centers[centre], -1, 1)))
    land = d < 6.0  # an island ~650 km across
    bright = np.where(land, 1.0, 0.0)
    kl, ks = 0.085, 0.025  # (C per W/m2: about Earth's high-latitude land and sea seasons, icemass.seasonal_k)
    own = own_k(p, land, np.where(land, kl, ks))
    k = orbit_k(g, own, land, bright, p)
    assert k[centre] < 0.35 * kl, k[centre] / kl
    far = d > 60
    assert np.allclose(k[far], ks)
    bare = orbit_k(g, own, land, np.zeros(g.n), p)
    assert np.allclose(bare[land], kl)
    # (the run's rule, for the run/zoom check: icemass.INSOL_K on land, INSOL_SEA of it at sea)
    run = own_k(Z.TZParams(orbit_resp="run"), land, None)
    assert np.allclose(run[land], icemass.INSOL_K) and np.allclose(run[far], icemass.INSOL_K * icemass.INSOL_SEA)


def test_seasonal_k_is_the_seasons_response():
    """Each cell's response to the orbit is its seasons' (PW-459): its warmest - coldest month per the
    lagged sun's seasonal range, the range floored near the equator."""
    rng = icemass.sun_range(23.44)
    assert 450 < rng.max() < 560 and rng.min() < 80  # (W/m2: polar ~520, equator ~30, a half-yearly cycle)
    lat = np.array([65.0, 65.0, 0.0])
    k = icemass.seasonal_k(lat, np.array([15.0, 4.0, 27.0]), np.array([-25.0, -4.0, 25.0]), 23.44)
    assert 0.07 < k[0] < 0.1 and k[1] < 0.3 * k[0]  # (a continental interior's 40 C, a maritime 8 C)
    assert k[2] < 0.02  # (2 C at the equator over the floored range, not over its ~30 W/m2)


def test_margin_ramp_scales_with_cells():
    """A margin cell's balance heights are its edge's Nye ramp across the iced part of the cell (PW-460):
    ~110 km cells iced across have ~620 / ~1200 m, a thin margin covers part of its cell, a 10 km cell's
    ramp is the old ~400 m edge."""
    f, h = icemass.margin_ramp(np.array([2000.0, 900.0, 100.0]), 110e3)
    assert f[0] == 1.0 and 0.99 < f[1] <= 1.0 and 0.15 < f[2] < 0.3
    assert 580 < h[0, 0] < 660 and 1150 < h[1, 0] < 1250
    assert h[1, 2] > 100.0  # (the iced part of a thin margin is thicker than the cell's mean)
    _, h10 = icemass.margin_ramp(np.array([1e4]), 10e3)
    assert 0.6 * icemass.EDGE_H < 0.5 * (h10[0, 0] + h10[1, 0]) < 0.8 * icemass.EDGE_H


def test_ramp_rule_means_the_nye_ramp():
    """The ramp's quadrature (icemass.ramp_rule) takes the Nye ramp's mean height, 2/3 of its top: the
    default 2 points in x to 1%, n points in sqrt(x) exactly; the outer edge is sampled lower with more points."""
    for n, tol in ((0, 0.01), (2, 1e-9), (8, 1e-9)):
        x, w = icemass.ramp_rule(n)
        assert abs(w.sum() - 1) < 1e-12 and abs((w * np.sqrt(x)).sum() - 2 / 3) < tol
    assert icemass.ramp_rule(8)[0].min() < 0.01 < icemass.ramp_rule(0)[0].min()


def test_sheet_air_comes_from_its_frozen_summers(sim4):
    """A sheet's carried cold air (icemass.air_mass) comes from the share of its summer its surface stays
    frozen (cold_share, the degree-day rule's spread): a melting margin can't chill the air below it."""
    assert icemass.cold_share(np.array([-5.0, 0.0, 5.0])) == pytest.approx([0.841, 0.5, 0.159], abs=0.002)
    g = sim4.grid
    centre = int(np.argmin(np.abs(g.lat - 70.0)))
    d = np.degrees(np.arccos(np.clip(g.centers @ g.centers[centre], -1, 1)))
    ice = np.where(d < 15.0, 2000.0, 0.0)
    full = icemass.air_mass(g, ice)
    assert np.array_equal(full, icemass.air_mass(g, ice, cold=np.ones(g.n)))
    half = icemass.air_mass(g, ice, cold=np.where(d < 10.0, 1.0, 0.0))  # (its outer ring melting)
    assert (half <= full + 1e-12).all() and half[centre] < full[centre] and (half[ice == 0] == 0).all()


def test_ice_surface_air_grows_with_its_fetch_over_ice(sim4):
    """The ice surface's own effects act on the share of its air that has come over ice (icemass.surface_share,
    surface_air 'fetch'): most of it inside a big sheet, less at its edge, less on a small cap."""
    g = sim4.grid
    centre = int(np.argmin(np.abs(g.lat - 70.0)))
    d = np.degrees(np.arccos(np.clip(g.centers @ g.centers[centre], -1, 1)))
    big = icemass.surface_share(g, np.where(d < 30.0, 2000.0, 0.0))
    cap = icemass.surface_share(g, np.where(d < 3.0, 500.0, 0.0))  # (one L4 cell)
    assert ((big >= 0) & (big <= 1)).all() and big[centre] > 0.9
    edge = (d > 26.0) & (d < 30.0)
    assert big[edge].mean() < big[centre] - 0.2 and cap[centre] < 0.6


def test_start_anchor_leaves_with_the_ice(cold_src, cold_run):
    """The start's climate correction of the ice surface (anchor) applies
    where ice lies: once the starting ice has melted, its cells (and the
    rings around them that no ice reached) have the climate of a zoom with
    no anchor at all (PW-035)."""
    src = dict(cold_src, ice=cold_run["state"]["H"].copy(), dT=cold_src["dT"] + 14.0)
    fixed = dict(NO_ORBIT, index="off", climate_every=1000.0, iso_ratio=0.0)
    a = Z.simulate(src, kyr=10, step=0.5, every=2.0, params=Z.TZParams(anchor="balance", anchor_max=3.0, **fixed))
    b = Z.simulate(src, kyr=10, step=0.5, every=2.0, params=Z.TZParams(anchor="none", **fixed))
    cooled = a["anchor"] < -0.4
    bare = cooled & (a["state"]["H"] < 1) & (b["state"]["H"] < 1)
    assert bare.sum() >= 5, bare.sum()
    # (no more than on bare land the anchor never touched: the two zooms' sea levels differ, and the
    # land's height above them)
    diff = np.abs(a["state"]["t_ann"] - b["state"]["t_ann"])
    land = src["elev"] > 0
    ref = land & (a["anchor"] == 0) & (a["state"]["H"] < 1) & (b["state"]["H"] < 1)
    assert np.median(diff[bare]) <= np.median(diff[ref]) + 0.02, (np.median(diff[bare]), np.median(diff[ref]))
    held = (a["state"]["H"] > 100) & cooled  # where the ice is still there, the anchor still cools it
    if held.any():
        assert (a["state"]["t_ann"] < b["state"]["t_ann"] - 0.3)[held].mean() > 0.5


def test_shelf_buttresses_marine_front(sim4):
    """A marine ice front with an ice shelf around it, in a sea cold enough
    for the shelf to stand, keeps more of its ice than where the shelf
    breaks up (it doesn't calve, and the shelf holds back its flow: PW-367);
    the shelf floats (not in the frames' grounded ice, no sea level).
    Beside a warm sea the shelf breaks up, so it makes no difference."""
    g = sim4.grid
    base = Z.source_from_sim(sim4)
    nb = lambda i: g.nbr_idx[g.nbr_off[i]:g.nbr_off[i + 1]]
    deep = lambda i: base["elev"][i] < -500 and (base["elev"][nb(i)] < -500).all()
    no_shelf = dict(shelf_warm=-200.0, shelf_cold=-201.0)

    def run(lat_ok, dT, **kw):
        c = next(i for i in np.argsort(-np.abs(g.lat) if dT < 0 else np.abs(g.lat)) if lat_ok(g.lat[i]) and deep(i))
        elev, ice = base["elev"].copy(), np.zeros(g.n)
        elev[c], ice[c] = -600.0, 1500.0  # grounded (1.12 x 600 m floats) ...
        ice[nb(c)] = 300.0  # ... with a shelf all around (afloat in > 500 m of water)
        src = dict(base, elev=elev, ice=ice, dT=base["dT"] + dT)
        r = Z.simulate(src, kyr=0.5, step=0.5, every=0.5, params=Z.TZParams(**NO_ORBIT, **kw))
        return r, c

    cold, c = run(lambda la: abs(la) > 60, -25.0)
    bare, _ = run(lambda la: abs(la) > 60, -25.0, **no_shelf)
    st = cold["state"]
    assert st["t_ann"][nb(c)].max() < Z.TZParams().shelf_cold  # (a sea a shelf stands in)
    assert st["H"][c] > bare["state"]["H"][c] + 100, (st["H"][c], bare["state"]["H"][c])
    shelf = nb(c)[st["H"][nb(c)] > 0]
    assert len(shelf) and (cold["data"]["ice"][-1][shelf] == 0).all()  # (floating: not grounded ice)
    assert (st["H"][shelf] * P.RHO_I < (st["sl"] - st["bed"][shelf]) * P.RHO_W).all()
    # the shelf holds no sea water: the sea level is the grounded ice's alone
    vaf = lambda H, bed, sl: (np.maximum(H - np.maximum(sl - bed, 0) * P.RHO_W / P.RHO_I, 0) * geometry(g)["area"]).sum()
    assert vaf(np.where(np.isin(np.arange(g.n), shelf), 0.0, st["H"]), st["bed"], st["sl"]) == vaf(st["H"], st["bed"], st["sl"])
    warm, c2 = run(lambda la: abs(la) < 25, 0.0)
    warm0, _ = run(lambda la: abs(la) < 25, 0.0, **no_shelf)
    assert warm["state"]["t_ann"][nb(c2)].min() > Z.TZParams().shelf_warm
    assert warm["state"]["H"][c2] == warm0["state"]["H"][c2]
    assert warm["state"]["H"][c2] < st["H"][c]  # (the same front beside open sea keeps less)


def test_shelf_spreads_and_melts():
    """An ice shelf fed at q thins toward the steady thickness its spreading
    (c h^4) balances, whatever it starts at, and melts away where the sea
    under it is warm; the ice that leaves is accounted for."""
    c = 1e-16 * (P.RHO_I * 9.81 * (1 - P.RHO_I / P.RHO_W) / 4) ** 3 * 0.2 ** 3
    h0 = np.array([0.0, 2000.0, 300.0, 300.0])
    q = np.array([1.0, 1.0, 0.0, 0.0])
    melt = np.array([0.0, 0.0, 0.0, 10.0])
    h, out, gone = shelf_step(h0, q, melt, c, 20000.0)
    steady = (1.0 / c) ** 0.25
    assert abs(h[0] - steady) < 0.05 * steady and abs(h[1] - steady) < 0.05 * steady
    assert h[2] < 300.0 and h[3] == 0.0
    assert np.allclose(h0 + q * 20000.0 - h - out - gone, 0.0, atol=1e-6)


def test_frames_carry_the_migrating_tree_cover(cold_run, cold_src):
    """PW-213: every frame has the tree cover (%), only on ice-free land; the speed limit changes only the plants."""
    tc = cold_run["data"]["tree_cover"]
    nf, n = len(cold_run["frames"]), cold_src["grid"].n
    assert tc.shape == (nf, n) and tc.dtype == np.uint8 and tc.max() <= 100 and tc.max() > 0
    assert (tc[cold_run["data"]["ice"] > 0] == 0).all()
    assert all(f["stats"]["pco2"] is not None for f in cold_run["frames"])
    free = Z.simulate(cold_src, kyr=40, step=0.5, every=2.0, params=Z.TZParams(veg_speed=0.0))
    assert np.array_equal(free["data"]["ice"], cold_run["data"]["ice"])  # (the ice and climate are the same)
    assert np.array_equal(free["data"]["tree_cover"][0], tc[0])
