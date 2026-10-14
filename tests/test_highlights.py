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
    # a range needs ground above 1500 m, which a small, old world may not have
    assert ("mountain_range" in by) == (np.asarray(L["elevation"]).max() > 1500)
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
