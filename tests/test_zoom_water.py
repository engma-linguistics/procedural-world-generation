"""Zoom lakes and deltas on a small synthetic world: a domed continent with
a basin that fills into an open lake, and radial rivers to the sea."""

import numpy as np
import pytest

from planet import hydrology, zoom
from planet.geo import R_KM, xyz
from planet.grid import build_grid

LAKE_AT = (5.0, 8.0)  # lat, lon of the basin


def _dist_km(g, lat, lon):
    c = xyz(np.radians(lat), np.radians(lon))
    return np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM


@pytest.fixture(scope="module")
def water_world():
    g = build_grid(5)
    d0 = _dist_km(g, 0.0, 0.0)
    elev = np.where(d0 < 2500, 60 + 0.3 * (2500 - d0), -3000.0)
    elev = elev - np.where(d0 < 2300, 500 * np.exp(-(_dist_km(g, *LAKE_AT) / 500) ** 2), 0)
    precip = np.full(g.n, 1200.0)
    # wet enough that the basin overflows: an open lake
    c = {"runoff": 0.5 * precip, "aet": 0.5 * precip, "lake_evap": np.full(g.n, 300.0)}
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c)
    lake = lk["wet"]
    land = elev > 0
    layers = {
        "elevation": np.round(elev), "precipitation": precip, "temperature": np.full(g.n, 22.0),
        "warm_month": np.full(g.n, 26.0), "flow": flow, "downstream": down, "lake": lake.astype(int),
        "lake_level": np.maximum(np.round(lk["level"]), np.round(elev)), "lake_kind": lk["kind"].astype(int),
        "runoff": c["runoff"],
        "rock": np.zeros(g.n, int), "surface_rock": np.zeros(g.n, int), "climate": np.full(g.n, 2),
        "ice": np.zeros(g.n), "sediment_cover": np.where(land, 0.5, 6.0),
    }
    assert lake.sum() >= 3, "the synthetic basin should hold a coarse lake"
    return {"grid": g, "layers": layers, "meta": {"level": 5}}


@pytest.fixture(scope="module")
def lake_zoom(water_world):
    return zoom.build(water_world, *LAKE_AT, size_km=1600, res_km=8, iterations=6, log=lambda *a: None)


def test_lake_passes_its_water_on(lake_zoom):
    lk = lake_zoom["stats"]["largest_lakes"][0]
    assert lk["outlet"] is not None
    assert lk["inflow_m3s"] > 0
    assert lk["inflow_m3s"] <= lk["outflow_m3s"] < 1.1 * lk["inflow_m3s"]


def test_lake_rim_holds_the_water(lake_zoom):
    Lr = lake_zoom["layers"]
    water, h = Lr["water"], Lr["elevation"].astype(float)
    surf = np.where(water == 2, h + Lr["lake_depth"], -np.inf)
    level = np.full(surf.shape, -np.inf)  # highest lake surface next to each pixel
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            level = np.maximum(level, zoom._shift(surf, dr, dc, -np.inf))
    low = (water == 0) & np.isfinite(level) & (h < level - 0.01)
    edge = np.zeros_like(low)
    edge[[0, -1], :] = edge[:, [0, -1]] = True
    orow, ocol = lake_zoom["stats"]["largest_lakes"][0]["outlet"]
    rr, cc = np.nonzero(low & ~edge)
    # only the outlet channel may sit below the water
    assert np.all(np.maximum(np.abs(rr - orow), np.abs(cc - ocol)) <= 2), list(zip(rr, cc))


def test_lake_depth_varies(lake_zoom):
    d = lake_zoom["layers"]["lake_depth"][lake_zoom["layers"]["water"] == 2]
    assert len(d) > 50
    assert d.std() > 0.25 * d.mean()
    assert d.max() > 1.5 * np.median(d)


def test_delta_plain_and_distributaries(water_world):
    g, L = water_world["grid"], water_world["layers"]
    down, flow, elev = L["downstream"], L["flow"], L["elevation"]
    mouths = np.flatnonzero((elev > 0) & (down >= 0))
    mouths = mouths[elev[down[mouths]] <= 0]
    i = mouths[np.argmax(flow[mouths])]
    p = g.centers[i] + g.centers[down[i]]
    lat, lon = np.degrees(np.arcsin(p[2] / np.linalg.norm(p))), np.degrees(np.arctan2(p[1], p[0]))
    z = zoom.build(water_world, float(lat), float(lon), size_km=1600, res_km=8, iterations=6, log=lambda *a: None)
    dl = z["stats"]["deltas"][0]
    assert dl["discharge_m3s"] >= zoom.DELTA_MIN_Q
    n = z["nx"]
    xs = (np.arange(n) + 0.5 - n / 2) * z["res"]
    X, Y = np.meshgrid(xs, -xs)
    near = (np.hypot(X - dl["mouth_km"][0], Y - dl["mouth_km"][1]) < 0.4 * dl["plain_radius_km"])
    land = near & (z["layers"]["water"] == 0)
    assert land.sum() > 10
    assert np.median(z["layers"]["elevation"][land]) < 10
    # distributaries: the river reaches the sea through several channels
    water, q = z["layers"]["water"], z["layers"]["discharge"]
    coast = (water == 0) & zoom._dilate(water == 1, 1)
    near = np.hypot(X - dl["mouth_km"][0], Y - dl["mouth_km"][1]) < dl["plain_radius_km"]
    assert z["stats"]["distributary_splits"] >= 1
    assert (coast & near & (q > 0.1 * q[near].max())).sum() >= 2
