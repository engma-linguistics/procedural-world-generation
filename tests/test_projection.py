"""Map projections (PW-477): known points and round trips, pure numpy."""

import numpy as np
import pytest

from planet import projection as PJ
from planet.geo import R_KM, latlon, xyz


def rand_points(n=2000, seed=0):
    r = np.random.default_rng(seed).normal(size=(n, 3))
    return r / np.linalg.norm(r, axis=1, keepdims=True)


@pytest.mark.parametrize("name", PJ.NAMES)
@pytest.mark.parametrize("center", [(0, 0), (48.5, -2.0), (-70, 150), (90, 10), (-90, 0)])
def test_round_trip(name, center):
    pr = PJ.Projection(name, *center)
    p = rand_points()
    x, y = pr.project(p)
    ok = np.isfinite(x)
    assert ok.sum() > 100
    back, valid = pr.unproject(x[ok], y[ok])
    assert valid.all()
    assert np.abs(back - p[ok]).max() < 1e-6


@pytest.mark.parametrize("name", PJ.NAMES)
def test_centre_is_origin_and_north_is_up(name):
    pr = PJ.Projection(name, 35, 120)
    x, y = pr.forward(35, 120)
    assert abs(x) < 1e-12 and abs(y) < 1e-12
    x2, y2 = pr.forward(40, 120)  # (a little north: straight up)
    assert abs(x2) < 1e-9 and y2 > 0
    x3, _ = pr.forward(35, 125)  # east: right
    assert x3 > 0


def test_known_points():
    e = np.pi
    # Equal Earth (R = 1): equator end, pole (Savric et al. 2018)
    ee = PJ.Projection("equal-earth")
    assert ee.forward(0, 180) == pytest.approx((2.7066, 0.0), abs=1e-3)
    assert ee.forward(90, 0)[1] == pytest.approx(1.3174, abs=1e-3)
    assert ee.full_extent()[0] == pytest.approx(2.7066, abs=1e-3)
    # Mollweide: x = 2 sqrt2 at the equator end, y = sqrt2 at the pole
    mo = PJ.Projection("mollweide")
    assert mo.forward(0, 180)[0] == pytest.approx(2 * np.sqrt(2))
    assert mo.forward(90, 0)[1] == pytest.approx(np.sqrt(2))
    th = np.arcsin(mo.forward(45, 0)[1] / np.sqrt(2))  # 2 theta + sin 2 theta = pi sin(lat)
    assert 2 * th + np.sin(2 * th) == pytest.approx(np.pi * np.sin(np.radians(45)), abs=1e-9)
    # azimuthal ones, 90 degrees east of the centre
    assert PJ.Projection("laea").forward(0, 90) == pytest.approx((np.sqrt(2), 0), abs=1e-12)
    assert PJ.Projection("aeqd").forward(0, 90) == pytest.approx((e / 2, 0), abs=1e-12)
    assert PJ.Projection("ortho").forward(0, 90) == pytest.approx((1, 0), abs=1e-12)
    assert PJ.Projection("stereo").forward(0, 90) == pytest.approx((2, 0), abs=1e-12)
    # equirect: degrees in radians
    assert PJ.Projection("equirect").forward(30, -45) == pytest.approx((-e / 4, e / 6))
    # aeqd distance from the centre is the great-circle distance
    x, y = PJ.Projection("aeqd", 10, 20).forward(10, 30)
    d = np.arccos(np.sin(np.radians(10)) ** 2 + np.cos(np.radians(10)) ** 2 * np.cos(np.radians(10)))
    assert np.hypot(x, y) == pytest.approx(d)


def test_oblique_places_any_latitude_centrally():
    # equirect centred on 60N: the centre is the map origin and the pole is straight up, 30 deg away
    pr = PJ.Projection("equirect", 60, 25)
    assert pr.forward(60, 25) == pytest.approx((0, 0), abs=1e-12)
    x, y = pr.forward(90, 0)
    assert abs(x) < 1e-9 and y == pytest.approx(np.radians(30))


def test_off_globe_is_invalid():
    o = PJ.Projection("ortho", 0, 0)
    assert np.isnan(o.forward(0, 120)[0])
    assert not o.unproject(np.array([1.2]), np.array([0.0]))[1][0]
    s = PJ.Projection("stereo", 0, 0)
    assert np.isnan(s.forward(0, 180)[0])
    mo = PJ.Projection("mollweide")
    assert not mo.unproject(np.array([2.9]), np.array([0.0]))[1][0]
    assert not mo.unproject(np.array([0.0]), np.array([1.5]))[1][0]


def test_pixel_grid_and_sizes():
    pr = PJ.Projection("laea", 20, 30)
    g = PJ.pixel_grid(pr, 64)
    assert g["height"] == 64 and g["valid"].shape == (64, 64)
    # a disc: corners are off, the middle is on, area fraction ~ pi/4
    assert not g["valid"][0, 0] and g["valid"][32, 32]
    assert g["valid"].mean() == pytest.approx(np.pi / 4, abs=0.03)
    # centre pixel is next to the centre point
    lat, lon = latlon(g["pts"].reshape(64, 64, 3)[32, 32])
    assert abs(lat - 20) < 3 and abs(lon - 30) < 3
    dx, dy = PJ.pixel_size_m(g["pts"], g["valid"], (64, 64))
    # laea: scale is ~1 at the centre: pixel = step * R
    assert dx[32, 32] == pytest.approx(g["step"] * R_KM * 1000, rel=0.05)
    # a regional extent
    g2 = PJ.pixel_grid(PJ.Projection("aeqd", 0, 0), 100, PJ.parse_extent("1000x500km"))
    assert (g2["width"], g2["height"]) == (100, 50) and g2["valid"].all()


def test_parse():
    assert PJ.parse_center("48.5, -2") == (48.5, -2.0)
    with pytest.raises(ValueError):
        PJ.parse_center("95,0")
    assert PJ.parse_extent("2000km") == (2000, 2000)
    assert PJ.parse_extent("3000x2000km") == (3000, 2000)
    w, h = PJ.parse_extent("10x5deg")
    assert w == pytest.approx(R_KM * np.radians(10)) and h == pytest.approx(R_KM * np.radians(5))
    with pytest.raises(ValueError):
        PJ.parse_extent("100")


def test_proj_strings():
    assert "+proj=laea +lat_0=10 +lon_0=20" in PJ.Projection("laea", 10, 20).proj_string()
    assert PJ.Projection("mollweide", 0, 30).proj_string().startswith("+proj=moll +lon_0=30")
    assert PJ.Projection("equal-earth", 45, 0).proj_string() is None
    assert "oblique" in PJ.Projection("equal-earth", 45, 0).describe()["proj_note"]
