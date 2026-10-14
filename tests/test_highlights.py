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
    L["cold_month"][sea] = 24.0
    by = check(w, H.find(w))
    assert by["coral_coast"]["stats"]["mean_depth_m"] <= 250 and by["coral_coast"]["stats"]["length_km"] > 0
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


def test_representative_time():
    # a run that alternates dispersed (many small landmasses) and assembled
    # (one big one) eras after 300 Myr: the pick is a typical in-between frame
    def fr(t, land, big, n):
        return {"t": t, "stats": {"land_pct": land, "largest_landmass_pct": big, "landmasses": n}}
    frames = [fr(t, 5, 1, 200) for t in range(0, 300, 20)]  # start-up: ignored
    frames += [fr(300, 30, 5, 60), fr(320, 30, 28, 3), fr(340, 30, 14, 20), fr(360, 30, 15, 22),
               fr(380, 30, 16, 19), fr(400, 30, 6, 55), fr(420, 31, 27, 4)]
    assert H.representative_time(frames) in (340, 360, 380)
    # a short run: the last two thirds
    assert H.representative_time(frames[:6]) >= 100 / 3


def test_cli_at_auto():
    from planet.__main__ import _at
    assert _at("auto") == "auto" and _at("120") == 120.0
    with pytest.raises(Exception):
        _at("soon")
