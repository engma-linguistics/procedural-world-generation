"""Highlights (planet/highlights.py) on small worlds: sane, deduplicated
places with valid coordinates."""

import json

import numpy as np
import pytest

from planet import highlights as H
from planet import timeline as T
from planet import world as W
from planet.geo import R_KM


@pytest.fixture(scope="module")
def world4(sim4):
    return T.world_from_sim(sim4)


def check(world, feats):
    g, elev = world["grid"], world["layers"]["elevation"]
    assert feats and [f["rank"] for f in feats] == list(range(1, len(feats) + 1))
    assert all(a["score"] >= b["score"] for a, b in zip(feats, feats[1:]))
    for f in feats:
        assert f["title"] and f["blurb"] and f["kind"] in H.PRIORITY
        assert f["category"] in H.CATEGORIES and f["kind"] in H.CATEGORIES[f["category"]]
        assert -90 <= f["lat"] <= 90 and -180 <= f["lon"] <= 180
        # lat/lon is the feature's cell, to the 0.01 degrees the viewer and zoom ids use
        assert abs(f["lat"] - g.lat[f["cell"]]) < 0.01 and abs(f["lon"] - g.lon[f["cell"]]) < 0.01
        assert f["size_km"] in H.ZOOM_SIZES
        for la, lo in f.get("path", []):
            assert -90 <= la <= 90 and -180 <= lo <= 180
    # no two places of the same kind on top of each other
    for a in feats:
        for b in feats:
            if a is not b and a["kind"] == b["kind"]:
                d = np.arccos(np.clip(g.centers[a["cell"]] @ g.centers[b["cell"]], -1, 1)) * R_KM
                assert d > 300, (a["title"], b["title"])
    json.dumps(feats, default=W._np)  # what the cache and the API send
    by = {f["kind"]: f for f in feats}
    assert elev[by["highest_peak"]["cell"]] == elev.max()
    assert elev[by["trench"]["cell"]] == elev.min()
    return by


def test_find_on_sliced_world(world4):
    by = check(world4, H.find(world4))
    L = world4["layers"]
    assert {"largest_river", "continent"} <= set(by)
    # a range needs a few cells (3, bridged across single low cells) of ground
    # above 1500 m, which a small, old world may not have
    elev = np.asarray(L["elevation"])
    land = elev > 0
    high = land & (elev >= max(1500.0, float(np.quantile(elev[land], 0.95))))
    lab, k = world4["grid"].components(high)
    if k and np.bincount(lab[lab >= 0]).max() >= 3:
        assert "mountain_range" in by
    if "mountain_range" in by:
        assert high.sum() >= 3
    # the largest river's cell is a mouth: land draining straight into the sea
    m = by["largest_river"]["cell"]
    assert L["elevation"][m] > 0 and L["elevation"][L["downstream"][m]] <= 0
    if "mountain_range" in by:
        assert by["mountain_range"]["stats"]["length_km"] > 0 and len(by["mountain_range"]["path"]) >= 2
    assert not by["continent"]["zoomable"]


def test_find_on_generated_world():
    """One-shot worlds have no rock, ice or plate-boundary history: detectors
    that need those just don't fire."""
    w = W.generate("plates", seed=2, level=4)
    check(w, H.find(w))


def test_pick_zooms():
    f = lambda lat, lon, size=1000, z=True: {"lat": lat, "lon": lon, "size_km": size, "zoomable": z}
    feats = [f(0, 0), f(0, 1), f(10, 10, z=False), f(0, 20), f(30, 30)]
    assert H.pick_zooms(feats, 2) == [feats[0], feats[3]]  # (0, 1) overlaps (0, 0); (10, 10) not zoomable


# --- round 2 kinds, each on a generated level-4 world with a planted feature
@pytest.fixture
def gen4():
    w = W.generate("plates", seed=2, level=4)
    w["layers"] = {k: np.array(v, copy=True) for k, v in w["layers"].items()}
    return w


def _near(g, c, k):
    """Cells within k links of c."""
    m = np.zeros(g.n, bool)
    m[c] = True
    for _ in range(k):
        m0 = m.copy()
        m[g.edges[m0[g.edges[:, 0]], 1]] = True
        m[g.edges[m0[g.edges[:, 1]], 0]] = True
    return np.flatnonzero(m)


def _inland_cell(w):
    """The land cell farthest (in links) from the sea; at least 3 links."""
    g, e = w["grid"], w["layers"]["elevation"]
    for k in (5, 4, 3):
        for c in np.flatnonzero(e > 0):
            if (e[_near(g, c, k)] > 0).all():
                return int(c)
    raise AssertionError("no inland cell")


def test_plateau_canyon_waterfall(gen4):
    w, g = gen4, gen4["grid"]
    L = w["layers"]
    c = _inland_cell(w)
    L["elevation"][_near(g, c, 2)] = 3000  # a flat upland...
    nb = g.nbr_idx[g.nbr_off[c]:g.nbr_off[c + 1]]
    L["elevation"][c] = 400  # ...with a river 2600 m down in it
    L["downstream"][L["downstream"] == c] = -1
    L["downstream"][c] = nb[0]
    L["flow"][c] = 400.0  # ~2,600 m^3/s on level-4 cells
    by = check(w, H.find(w))
    assert by["plateau"]["stats"]["mean_m"] >= 2000
    cy = [f for f in H.find(w) if f["kind"] == "canyon"]
    assert cy and cy[0]["cell"] == c and cy[0]["stats"]["depth_m"] == 2600
    # the river leaves the canyon over its 3000 m wall: a big drop at the next cell on
    L["elevation"][c] = 3000
    L["elevation"][nb[0]] = 1000
    L["downstream"][nb[0]] = -1
    wf = [f for f in H.find(w) if f["kind"] == "waterfall"]
    assert wf and wf[0]["cell"] == c and wf[0]["stats"]["drop_m"] >= 2000


def test_ice_capped_peak(gen4):
    L = gen4["layers"]
    L["ice"] = np.zeros(gen4["grid"].n)
    top = int(np.argmax(L["elevation"]))
    L["ice"][top] = 600
    by = check(gen4, H.find(gen4))
    free = by["ice_free_peak"]
    assert L["ice"][free["cell"]] == 0 and free["score"] > by["highest_peak"]["score"]
    assert "ice" in by["highest_peak"]["blurb"]


def test_coral_and_rain_shadow(gen4):
    w, g = gen4, gen4["grid"]
    L = w["layers"]
    e = L["elevation"]
    sea = e <= 0
    coast = sea & np.isin(np.arange(g.n), g.edges[np.isin(g.edges, np.flatnonzero(~sea)).any(1)].ravel())
    e[coast] = -40
    L["reef"] = np.where(coast, 5.0, 0.0)  # % of the cell (coastal.py's layer)
    land = e > 0
    shore = land & np.isin(np.arange(g.n), g.edges[np.isin(g.edges, np.flatnonzero(coast)).any(1)].ravel())
    L["mangrove"] = np.where(shore, 4.0, 0.0)
    by = check(w, H.find(w))
    cc = by["coral_coast"]["stats"]
    assert cc["mean_depth_m"] == 40 and cc["length_km"] > 0
    assert cc["reef_km2"] > 0.04 * 4 * np.pi * R_KM ** 2 / g.n
    assert by["mangrove_coast"]["stats"]["mangrove_km2"] > 0
    # a lone summit, wet to its east and dry to its west
    c = _inland_cell(w)
    e[_near(g, c, 4)] = np.minimum(e[_near(g, c, 4)], 500)
    e[c] = 4000
    east = g.centers @ np.cross([0.0, 0.0, 1.0], g.centers[c])
    L["precipitation"][:] = np.where(east > 0, 2000, 100)
    rs = [f for f in H.find(w) if f["kind"] == "rain_shadow"]
    assert rs and rs[0]["cell"] == c and rs[0]["stats"]["ratio"] >= 10


def test_salt_and_inland_basins(gen4):
    w, g = gen4, gen4["grid"]
    L = w["layers"]
    c = _inland_cell(w)
    pan = _near(g, c, 1)
    L["lake"][pan] = 1
    L["lake_kind"][pan] = 2
    L["lake_level"][pan] = L["elevation"][pan].max() + 20
    L["downstream"][pan] = -1  # the lake keeps its water...
    ring = np.setdiff1d(_near(g, c, 2), pan)
    for j in ring:  # ...and what flows into it
        nb = g.nbr_idx[g.nbr_off[j]:g.nbr_off[j + 1]]
        L["downstream"][j] = nb[np.isin(nb, pan)][0]
    by = check(w, H.find(w))
    assert by["salt_lake"]["stats"]["area_km2"] > 0
    assert by["inland_basin"]["stats"]["area_km2"] >= len(_near(g, c, 2)) * 4 * np.pi * R_KM**2 / g.n * 0.99


def test_most_varied(world4):
    v = [f for f in H.find(world4) if f["kind"] == "varied_square"]
    assert len(v) == 1 and v[0]["stats"]["koppen_classes"] >= 2 and v[0]["size_km"] == 1000


def test_finish_moment_is_the_latest_habitable_candidate():
    # PW-866 (owner): the finished world is the latest human-habitable keyframe of the finish window (the
    # finish checks: true mean -6..+3 C of 13.8, land ice 1-25% of land, wet-tropics trees >= 20%), else the end,
    # flagged
    def fr(t, temp=14.0, ice=8.0, wet=40.0):
        return {"t": t, "stats": {"true_temp_c": temp, "iced_land_pct": ice, "wet_eq_trees_pct": wet}}
    frames = [fr(t) for t in range(0, 992, 4)] + [fr(990 + 0.5 * k) for k in range(1, 21)]
    fm = H.finish_moment(frames, 10.0)
    assert fm["t"] == 1000 and fm["passes"] and fm["before_end_myr"] == 0 and fm["candidates"] == 20
    meta = {"params": {"finish_window": 10.0}}
    assert H.representative_time(frames, meta) == 1000
    frames[-1]["stats"]["true_temp_c"] = 19.0  # a hot end
    frames[-2]["stats"]["iced_land_pct"] = 0.0  # no ice
    frames[-3]["stats"]["wet_eq_trees_pct"] = 5.0  # bare tropics
    fm = H.finish_moment(frames, 10.0)
    assert fm["t"] == 998.5 and fm["before_end_myr"] == 1.5 and fm["fails_at_end"] == ["temperature"]
    assert "1.5 Myr before the run's end" in H.representative_note(frames, 998.5, meta)
    assert H.representative_time(frames, {**meta, "finish_moment": fm}) == 998.5
    for f in frames[-20:]:
        f["stats"]["true_temp_c"] = 30.0
    fm = H.finish_moment(frames, 10.0)
    assert fm["t"] == 1000 and not fm["passes"] and "NO human-habitable moment" in fm["why"]
    assert H.finish_moment(frames[:-20] + [fr(992)], 10.0)["t"] == 992  # (a candidate before the window's 990)

def test_ago_time():
    # --ago: Ma before now, now being the run's end less star_now_offset_myr
    frames = [{"t": t, "stats": {}} for t in range(0, 1004, 4)]
    meta = {"params": {"run_end": 1000.0}}
    assert H.ago_time(frames, meta, 70) == 930.0
    assert H.ago_time(frames, {"params": {"run_end": 1000.0, "star_now_offset_myr": 100.0}}, 70) == 830.0
    with pytest.raises(ValueError):
        H.ago_time(frames, meta, 1200)


def test_cli_at_auto():
    from planet.__main__ import _at
    assert _at("auto") == "auto" and _at("120") == 120.0
    with pytest.raises(Exception):
        _at("soon")


def test_travel(gen4):
    """Beach, ski and mild-winter finders on planted places, each in its own
    hemisphere's season; worlds without the July/January layers get none."""
    w, g = gen4, gen4["grid"]
    L = w["layers"]
    e = L["elevation"]
    L["ice"] = np.zeros(g.n)
    L["lake"][:] = 0
    # nowhere is nice: 0 C all year, wet, no waves
    for k in ("temperature_jul", "temperature_jan", "sst_jul", "sst_jan"):
        L[k] = np.zeros(g.n)
    for k in ("precipitation_jul", "precipitation_jan"):
        L[k] = np.full(g.n, 2000.0)
    for k in ("sunshine_jul", "sunshine_jan"):  # and overcast
        L[k] = np.full(g.n, 4.0)
    L["wave_power"] = np.where(e > 0, 0.0, 0.5)
    nb = lambda c: g.nbr_idx[g.nbr_off[c]:g.nbr_off[c + 1]]
    coast = [int(c) for c in np.flatnonzero(e > 0) if (e[nb(c)] <= 0).sum() >= 2 and (e[nb(c)] > 0).any()]
    north = [c for c in coast if g.lat[c] > 15]
    south = [c for c in coast if g.lat[c] < -15]
    assert north and south
    # a beach in the north: warm, sunny July, warm sea, gentle surf
    b = north[0]
    e[b] = 20
    L["temperature_jul"][b], L["precipitation_jul"][b], L["sunshine_jul"][b] = 28, 300, 10.0
    sea = nb(b)[e[nb(b)] <= 0]
    L["sst_jul"][sea], L["wave_power"][sea] = 25, 8.0  # (the sea's own July surface temperature)
    L["temperature_jul"][sea] = 31  # (not the air over it)
    # a southern coast that is warm and sunny in July: its winter, so no beach
    s = south[0]
    L["temperature_jul"][s], L["precipitation_jul"][s], L["sunshine_jul"][s] = 28, 300, 10.0
    sea_s = nb(s)[e[nb(s)] <= 0]
    L["sst_jul"][sea_s], L["wave_power"][sea_s] = 25, 8.0
    # ski country in the north: freezing, snowy January slopes over a town at 2 C
    c = _inland_cell(w)
    town = int(nb(c)[0])
    e[c], e[town] = 2500, 800
    L["temperature_jan"][c], L["temperature_jul"][c], L["precipitation_jan"][c] = -8, 10, 1200
    L["temperature_jan"][town] = 2
    # a mild, sunny winter in the south (July 15 C, 6 h of sun), and a mild but overcast one
    m, dull = south[-1], south[-2]
    e[m] = e[dull] = 100  # (low land)
    L["temperature_jul"][m], L["precipitation_jul"][m], L["sunshine_jul"][m] = 15, 200, 6.0
    L["temperature_jul"][dull], L["precipitation_jul"][dull] = 15, 200
    feats = H.find(w)
    check(w, feats)
    by = lambda k: [f for f in feats if f["kind"] == k]
    assert [f["cell"] for f in by("beach")] == [b]
    assert "July 28 °C, 10 h of sunshine" in by("beach")[0]["blurb"] and by("beach")[0]["stats"]["sea_c"] == 25
    ski = by("ski")
    assert [f["cell"] for f in ski] == [c] and ski[0]["stats"]["town_cell"] == town
    assert ski[0]["stats"]["vertical_m"] > 1000 and "January -8 °C" in ski[0]["blurb"]
    assert [f["cell"] for f in by("mild_winter")] == [m] and "July 15 °C, 6 h of sunshine" in by("mild_winter")[0]["blurb"]
    # a glaciated summit is no ski field; an overcast summer is no beach holiday
    L["ice"][c] = 200
    L["sunshine_jul"][b] = 5.0
    feats = H.find(w)
    assert not [f for f in feats if f["kind"] in ("ski", "beach")]
    # worlds made before the seasonal layers: no travel places, no errors
    for k in H.SEASON_LAYERS:
        del L[k]
    assert not {"beach", "ski", "mild_winter", "year_round"} & {f["kind"] for f in H.find(w)}


def test_vegetation_places(gen4):
    """Great forest, savanna, wetland, maquis coast and treeline finders on
    planted vegetation (vegetation.TYPES ids)."""
    w, g = gen4, gen4["grid"]
    L = w["layers"]
    e = L["elevation"]
    land = e > 0
    L["ice"] = np.zeros(g.n)
    L["vegetation"] = np.where(land, 32, 0)  # short-grass steppe everywhere, no trees, nothing flooded
    L["tree_cover"], L["flooded"] = np.zeros(g.n), np.zeros(g.n)
    nb = lambda c: g.nbr_idx[g.nbr_off[c]:g.nbr_off[c + 1]]
    c = _inland_cell(w)
    taiga = [int(x) for x in _near(g, c, 1) if land[x]]
    L["vegetation"][taiga], L["tree_cover"][taiga] = 37, 85
    # a treeline: krummholz at 2500 m over the taiga at 600 m
    e[taiga] = 600
    e[c] = 2500
    L["vegetation"][c], L["tree_cover"][c] = 48, 5
    # a wetland and a savanna elsewhere inland
    far = [int(x) for x in np.flatnonzero(land) if min(np.arccos(np.clip(g.centers[x] @ g.centers[c], -1, 1)) * R_KM, 9e9) > 2500]
    inner = [x for x in far if land[nb(x)].all()]
    wet = [x for x in _near(g, inner[0], 1) if land[x]]
    L["vegetation"][wet], L["flooded"][wet] = 52, 60
    sav = [x for x in _near(g, inner[-1], 1) if land[x]]
    L["vegetation"][sav] = 9
    # maquis on a coast
    coast = [int(x) for x in np.flatnonzero(land) if (e[nb(x)] <= 0).any()]
    mq = [x for x in _near(g, coast[len(coast) // 2], 1) if land[x] and x not in wet + sav + taiga + [c]]
    L["vegetation"][mq] = 19
    feats = H.find(w)
    check(w, feats)
    by = lambda k: [f for f in feats if f["kind"] == k]
    assert {f["category"] for f in by("great_forest")} == {"vegetation"}
    gf = by("great_forest")
    assert len(gf) == 1 and gf[0]["cell"] in taiga and "boreal spruce-fir taiga" in gf[0]["title"]
    assert [f["cell"] in wet for f in by("wetland")] == [True] and "raised bog" in by("wetland")[0]["title"]
    assert by("savanna")[0]["cell"] in sav and "dry savanna 100%" in by("savanna")[0]["blurb"]
    assert by("maquis_coast")[0]["cell"] in mq
    tl = [f for f in by("treeline") if "Polar" not in f["title"]]
    assert len(tl) == 1 and tl[0]["stats"]["treeline_m"] == 600 and "alpine scrub (krummholz)" in tl[0]["blurb"]
    # worlds without vegetation layers: none of these, no errors
    for k in ("vegetation", "tree_cover", "flooded"):
        del L[k]
    assert not set(H.CATEGORIES["vegetation"]) & {f["kind"] for f in H.find(w)}


def test_island_chain_and_atolls(gen4):
    """Hotspot chains and atoll groups from the volcano table (volcanism.COLUMNS):
    a planted chain of vents along the equator, youngest first, and a group
    of arc atolls far from it."""
    from planet.tectonics import volcanism as V
    w = gen4
    row = lambda lat, lon, kind, age, active, top, reef: dict(
        lat=lat, lon=lon, kind=kind, age=age, active=active, top_m=top, floor_m=-4000.0, height_m=top + 4000.0,
        radius_km=25.0, volume_km3=1e4, reef=reef, shore_km=0.0)
    chain = [row(0.0, 1.0 * k, V.VENT, 2.0 * k, int(k == 0), top, reef) for k, (top, reef) in enumerate(
        [(2000, 0), (1500, 0), (800, 0), (300, 0), (-20, V.REEF), (-30, V.REEF), (-900, V.DROWNED), (-1500, V.DROWNED)])]
    group = [row(0.0, 120.0 + 1.5 * k, V.ARC, 30.0, 0, -10, V.REEF) for k in range(4)]
    w["meta"] = dict(w.get("meta", {}), volcano_columns=list(V.COLUMNS),
                     volcanoes=[[v[c] for c in V.COLUMNS] for v in chain + group])
    feats = H.find(w)
    check(w, feats)
    hs = [f for f in feats if f["kind"] == "hotspot_islands"]
    assert len(hs) == 1
    st = hs[0]["stats"]
    assert (st["volcanoes"], st["islands"], st["atolls"], st["sunk"], st["active"]) == (8, 4, 2, 2, True)
    assert "Island chain: 4 islands, 2 atolls" == hs[0]["title"] and len(hs[0]["path"]) == 8
    assert abs(hs[0]["lat"]) < 2 and -1 < hs[0]["lon"] < 8
    at = [f for f in feats if f["kind"] == "atolls"]
    assert len(at) == 1 and at[0]["stats"]["atolls"] == 4 and 118 < at[0]["lon"] < 127 and at[0]["category"] == "geology"
    # an ocean-wide scatter of atolls ~280 km apart (PW-382): one archipelago at most ARCHIPELAGO_KM across, the rest "beyond"
    ocean = [row(-10.0, -170.0 + 2.5 * k, V.ARC, 30.0, 0, -10, V.REEF) for k in range(30)]
    w["meta"]["volcanoes"] = [[v[c] for c in V.COLUMNS] for v in ocean]
    at = H.atolls(H._Ctx(w), top=1)
    st = at[0]["stats"]
    assert 4 <= st["atolls"] <= 7 and st["extent_km"] <= H.ARCHIPELAGO_KM + 100
    assert st["atolls_beyond"] == 30 - st["atolls"] and "more atolls lie scattered beyond" in at[0]["blurb"]


def test_fastest_plate(world4):
    """The fastest big plate, at its leading edge (converging boundary it
    moves towards); none when its edges don't converge."""
    w = dict(world4, layers=dict(world4["layers"]))
    L = w["layers"]
    plate, speed = np.asarray(L["plate"]), np.asarray(L["plate_speed"], float)
    f = [x for x in H.find(w) if x["kind"] == "fastest_plate"]
    ids, cnt = np.unique(plate, return_counts=True)
    big = ids[cnt >= H.FAST_MIN_SHARE * len(plate)]
    fastest = max(big, key=lambda p: speed[plate == p].mean())
    assert len(f) <= 1
    if f:
        assert f[0]["stats"]["plate"] == fastest and plate[f[0]["cell"]] == fastest and f[0]["category"] == "geology"
        assert f[0]["stats"]["speed_cmyr"] >= f[0]["stats"]["next_cmyr"]
    L["plate_boundary"] = np.zeros_like(L["plate_boundary"])  # nothing converging: nothing to show
    assert not [x for x in H.find(w) if x["kind"] == "fastest_plate"]


def _vrow(lat, lon, kind, age, active, top, floor, reef=0):
    return dict(lat=lat, lon=lon, kind=kind, age=age, active=active, top_m=top, floor_m=floor, height_m=top - floor,
                radius_km=25.0, volume_km3=1e4, reef=reef, shore_km=0.0)


def _with_volcanoes(w, rows, plumes):
    from planet.tectonics import volcanism as V
    w["meta"] = dict(w.get("meta", {}), volcano_columns=list(V.COLUMNS), hotspots=plumes,
                     volcanoes=[[v[c] for c in V.COLUMNS] for v in rows])
    return w


def test_volcano_status():
    """zoom_volcanoes.status: active (fed now); dormant: a hotspot vent off its
    plume but within DORMANT_KM of it; extinct otherwise (and every arc
    volcano past its life)."""
    from planet import zoom_volcanoes as ZV
    from planet.tectonics import volcanism as V
    rows = [_vrow(30, 60.0, V.VENT, 0, 1, 3000, 1500), _vrow(30, 61.2, V.VENT, 1, 0, 3000, 1500),
            _vrow(30, 62.4, V.VENT, 2, 0, 3000, 1500), _vrow(30, 60.2, V.ARC, 9, 0, 2000, 500),
            _vrow(30, 60.3, V.ARC, 2, 1, 2000, 500)]
    w = _with_volcanoes({}, rows, [[30.0, 60.0]])
    assert ZV.statuses(w) == ["active", "dormant", "extinct", "extinct", "active"]
    assert ZV.statuses(_with_volcanoes({}, rows, [])) == ["active", "extinct", "extinct", "extinct", "active"]


def test_volcano_kinds(gen4):
    """A continental plume's caldera track (a supervolcano), an oceanic
    shield 9 km tall with an arc cone beside it (a volcanic field of two
    kinds), and two active arc cones at the same capped summit height (the
    taller above its ground is the highest)."""
    from planet.tectonics import volcanism as V
    rows = [_vrow(30, 60.0 + 1.2 * k, V.VENT, k, int(k == 0), 3000, 1500) for k in range(4)]
    rows += [_vrow(-20, -150.0, V.VENT, 0, 1, 4100, -5000), _vrow(-20, -149.0, V.VENT, 1, 0, 3000, -4800),
             _vrow(-20, -148.0, V.ARC, 2, 1, 3200, 0), _vrow(10, 100.0, V.ARC, 2, 1, 3500, 1000),
             _vrow(10.5, 100.5, V.ARC, 2, 1, 3500, 2000), _vrow(12, 103.0, V.ARC, 12, 0, 3900, 1000)]
    w = _with_volcanoes(gen4, rows, [[30.0, 60.0], [-20.0, -150.0]])
    by = check(w, H.find(w))
    sv = by["supervolcano"]
    assert sv["title"] == "Supervolcano (active)" and sv["category"] == "geology"
    assert (sv["stats"]["active"], sv["stats"]["dormant"], sv["stats"]["extinct"]) == (1, 1, 2)
    assert abs(sv["lat"] - 30) < 5 and len(sv["path"]) == 4 and "Yellowstone" in sv["blurb"]
    st = by["stratovolcano"]["stats"]
    assert (st["top_m"], st["relief_m"]) == (3500, 2500)  # (the extinct 3,900 m cone doesn't count)
    sh = by["shield_volcano"]
    assert sh["stats"]["relief_m"] == 9100 and "Everest" in sh["blurb"] and sh["stats"]["status"] == "active"
    vf = by["volcanic_field"]["stats"]
    assert vf["types"] == 2 and vf["stratovolcano"] == 1 and vf["shield"] == 2 and vf["dormant"] == 1
    # the plume gone: its calderas are all extinct, no supervolcano
    w["meta"]["hotspots"] = [[-20.0, -150.0]]
    rows[0]["active"] = 0
    w["meta"]["volcanoes"] = [[v[c] for c in V.COLUMNS] for v in rows]
    assert not [f for f in H.find(w) if f["kind"] == "supervolcano"]


def test_flood_basalts(gen4):
    from planet import surface as SF
    w, g = gen4, gen4["grid"]
    L = w["layers"]
    c = _inland_cell(w)
    L["surface_rock"] = np.full(g.n, SF.CRATON, np.int16)
    L["surface_rock"][_near(g, c, 1)] = SF.FLOOD_BASALT
    fb = [f for f in H.find(w) if f["kind"] == "flood_basalt"]
    assert len(fb) == 1 and fb[0]["cell"] in _near(g, c, 1) and fb[0]["stats"]["area_km2"] >= H.FLOOD_MIN_KM2
    L["surface_rock"][:] = SF.CRATON
    assert not [f for f in H.find(w) if f["kind"] == "flood_basalt"]


def test_carbonate_bank_and_barrier_reef(gen4):
    """A shallow warm bank in the open ocean (the Bahamas), and reefs on the
    outer half of a big continent's shelf with a lagoon behind them (the Great
    Barrier Reef); neither shown again as a coral coast."""
    w, g = gen4, gen4["grid"]
    L = w["layers"]
    e = L["elevation"]
    ctx = H._Ctx(w)
    L["reef"] = np.zeros(g.n)
    L["sst"] = np.full(g.n, 27.0)
    to_land = H._hops(ctx, ctx.land)
    big = ctx.components(ctx.land)[0]
    assert len(big) * ctx.area >= H.BIG_LAND_KM2
    # the bank: a sea cell far out and its neighbours, 30 m deep
    far = int(np.flatnonzero(to_land >= 4)[0])
    bank = _near(g, far, 1)
    e[bank] = -30
    e[_near(g, far, 2)[~np.isin(_near(g, far, 2), bank)]] = -3000
    L["reef"][bank] = 4.0
    # the barrier: a stretch of the big continent's coast, its coastal sea a 30 m
    # lagoon, the next ring out a reef 20 m deep, then the deep sea
    m = np.zeros(g.n, bool)
    m[big] = True
    coast = np.flatnonzero(ctx.dilate(m) & ~ctx.land & (to_land == 1))
    c0 = int(coast[0])
    zone = _near(g, c0, 3)
    lagoon = zone[(to_land[zone] == 1)]
    reef = zone[(to_land[zone] == 2)]
    e[lagoon], e[reef] = -30, -20
    e[zone[to_land[zone] >= 3]] = -3000
    L["reef"][reef] = 6.0
    ctx2 = H._Ctx(w)
    assert H._landmass_km2(ctx2)[big[0]] >= H.BIG_LAND_KM2
    feats = H.find(w)
    check(w, feats)
    cb = [f for f in feats if f["kind"] == "carbonate_bank"]
    assert len(cb) == 1 and cb[0]["cell"] in bank and cb[0]["stats"]["depth_m"] == 30 and cb[0]["category"] == "water"
    br = [f for f in feats if f["kind"] == "barrier_reef"]
    assert len(br) == 1 and br[0]["cell"] in reef and br[0]["stats"]["length_km"] >= H.BARRIER_MIN_KM
    assert br[0]["stats"]["lagoon_m"] == 30
    assert not [f for f in feats if f["kind"] == "coral_coast"]
    # the same reefs touching the shore are a coral coast, not a barrier reef
    L["reef"][reef] = 0.0
    L["reef"][lagoon] = 6.0
    feats = H.find(w)
    assert not [f for f in feats if f["kind"] == "barrier_reef"]
    assert [f for f in feats if f["kind"] == "coral_coast"]


