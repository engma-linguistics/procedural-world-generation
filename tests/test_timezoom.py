"""Glacial time zoom (planet/timezoom/): bookkeeping and sanity, on the
session's level-4 simulation (fast)."""

import json
import numpy as np
import pytest

from planet import orbit as O, timeline as T, timezoom as Z
from planet.timezoom import params as P
from planet.timezoom.forcing import orbit_k
from planet.timezoom.geometry import geometry
from planet.timezoom.ice import shelf_step

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


def test_glacial_cooling_turns_forest_to_tundra_and_cools_further(sim4):
    """PW-450: plants grown to balance with the start, then on a climate 4 C colder, lose forest toward the
    pole; the lying snow it no longer hides brightens the ground, which cools the land (the local
    correction) and the planet (the global term, in dTg)."""
    from planet import climate
    from planet.timezoom.plants import Plants

    src = Z.source_from_sim(sim4)
    g, tilt = src["grid"], src["tilt"]
    elev, H = np.asarray(src["elev"], float), np.maximum(np.asarray(src["ice"], float), 0.0)
    grounded = (H > 1.0) & (elev > 0)
    surf = np.where(grounded, elev + H, elev)
    pl = Plants(g, src, Z.TZParams(), tilt, geometry(g)["area"])

    def compute(dT):
        return lambda veg: climate.compute(g, surf, src["dT"] + dT, tilt, veg=veg)

    pl.step(0.0, compute(0.0)(None), surf, grounded, H, 0.0, compute(0.0))
    tree0 = pl.tree.copy()
    assert pl.series[-1]["F_wm2"] == 0.0  # (the start is the reference)
    c = compute(-4.0)(pl.feedback(grounded))
    t0 = c["temp"].copy()
    c = pl.step(10.0, c, surf, grounded, H, -1.0, compute(-4.0))
    lost = (surf > 0) & ~grounded & (np.abs(g.lat) > 40) & (tree0 - pl.tree > 0.2)
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
    iso_tau under a growing load lags it by about the load of its last
    iso_tau, so the tolerance takes the ice volume grown over the last
    iso_tau (a share of all grown) on top of 5% of the dip."""
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
    t = [f["t"] for f in cold_run["frames"]]
    v = [f["stats"]["ice_volume_mkm3"] for f in cold_run["frames"]]
    lag = (v[-1] - np.interp(t[-1] - p.iso_tau, t, v)) / max(v[-1] - v[0], 1e-9)
    tol = (0.05 + max(lag, 0.0)) * np.median((H - H0)[grew]) * p.iso_ratio + 20
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
    assert (cut >= 0).all() and (till >= 0).all() and (debris >= 0).all()
    vol = (cut * area).sum()
    assert vol > 0
    assert abs(vol - ((till + debris) * area).sum()) < 1e-9 * vol
    assert not (cut > 0)[s["wet_kyr"] <= 0].any()  # only under a thawed bed
    assert (s["slide_km"] > 0).any()
    # (grounded ice at some step: the frames every 2 kyr miss ice that grounded and calved in between)
    iced = (cold_run["data"]["ice"] > 0).any(0) | (s["wet_kyr"] > 0)
    near = dilate(iced, g.nbr_off, g.nbr_idx, 2)
    assert not (till > 0.1)[~near].any()
    e = cold_run["data"]["glacial_erosion"].astype(int)
    assert (np.diff(e, axis=0) >= 0).all() and e[-1].max() > 0


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
    keeps the land's full insol_k, the open sea its insol_sea share."""
    g = sim4.grid
    p = Z.TZParams()
    centre = int(np.argmin(np.abs(g.lat - 70.0)))
    d = np.degrees(np.arccos(np.clip(g.centers @ g.centers[centre], -1, 1)))
    land = d < 6.0  # an island ~650 km across
    bright = np.where(land, 1.0, 0.0)
    k = orbit_k(g, land, bright, p)
    assert k[centre] < 0.35 * p.insol_k, k[centre] / p.insol_k
    far = d > 60
    assert np.allclose(k[far], p.insol_k * p.insol_sea)
    bare = orbit_k(g, land, np.zeros(g.n), p)
    assert np.allclose(bare[land], p.insol_k)


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
