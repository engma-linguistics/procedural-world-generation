"""The tiling of the sphere by land-zoom sections (PW-1319): coverage, margin and neighbours."""
import numpy as np
import pytest

from planet import world as W
from planet.geo import R_KM, xyz
from planet.grid import build_grid
from planet.zoom import regional as RG
from planet.zoom import tiling as T
from planet.zoom.regional import Frame
from planet.zoom.terrain import en_to_grid


def _centre(s):
    lat, lon = np.radians(s["lat"]), np.radians(s["lon"])
    return np.array([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])


def test_tiling_covers_sphere_with_margin():
    ss = T.sections(None, 4000.0, 190.0)
    assert len(ss) == 54  # 6 faces x 3 x 3
    assert min(s["margin_km"][0] for s in ss) >= 95.0  # every cell inside its square with room on every side
    assert min(s["overlap_km"] for s in ss) >= 190.0  # any two neighbours overlap by at least this
    rng = np.random.default_rng(1)
    p = rng.normal(size=(2000, 3))
    p /= np.linalg.norm(p, axis=1, keepdims=True)
    f, i, j = T.locate(p, 3)
    by = {s["id"]: s for s in ss}
    names = list(T.FACES)
    for k in range(len(p)):  # each point is inside its home section's square, clear of the square's edge
        s = by[f"{names[f[k]]}.{i[k]}.{j[k]}"]
        x, y = T.frame_of(_centre(s), s["up"]).to_plane(p[k:k + 1])
        assert max(abs(x[0]), abs(y[0])) <= 2000.0 - 95.0


def test_neighbours_are_symmetric():
    ss = {s["id"]: s for s in T.sections(None)}
    for s in ss.values():
        assert 3 <= len(s["neighbours"]) <= 8
        for k in s["neighbours"]:
            assert s["id"] in ss[k]["neighbours"]
    assert len(ss["px.1.1"]["neighbours"]) == 8  # a face's middle cell: four edge and four corner neighbours


def test_frame_up_orientation():
    f = Frame(10.0, 20.0, up=np.array([0.0, 0.0, 1.0]))
    g = Frame(10.0, 20.0)
    assert np.allclose(f.n, g.n) and np.allclose(f.e, g.e)  # up = the pole is the default north
    f = Frame(0.0, 0.0, up=np.array([0.0, 1.0, 0.0]))  # at (0, 0), up along +y (east)
    assert np.allclose(f.n, [0, 1, 0]) and np.allclose(np.cross(f.e, f.n), f.c)


# ---- turned sections (PW-1338) ------------------------------------------------------------------------------
def test_section_lookup_and_poles():
    s = T.section("pz.1.1")
    assert abs(s["lat"]) > 89.99  # the polar face's middle cell sits on the pole
    f = Frame(s["lat"], s["lon"], up=s["up"])
    x, y = f.to_plane(f.to_sphere(np.array([300.0, -1200.0]), np.array([800.0, 50.0])))
    assert np.allclose(x, [300.0, -1200.0]) and np.allclose(y, [800.0, 50.0])
    assert np.allclose(f.up, f.n) and abs(f.up @ f.c) < 1e-12
    with pytest.raises(SystemExit):
        T.section("px.9.9")


def test_up_of_bearing_and_ids():
    assert RG.up_of(10.0, 20.0, None) is None
    u = RG.up_of(10.0, 20.0, 90.0)  # up = east
    assert np.allclose(u, Frame(10.0, 20.0).e)
    assert RG._bearing(Frame(10.0, 20.0, up=u)) == 90.0
    assert RG.frame_of({"lat": 10.0, "lon": 20.0, "up": list(u)}).up is not None
    assert RG.frame_of({"lat": 10.0, "lon": 20.0}).up is None
    a = RG.zoom_id("w", 10.0, 20.0, 4000, 4, 1)
    assert a == RG.zoom_id("w", 10.0, 20.0, 4000, 4, 1, up=None)  # north-up ids are unchanged
    assert a != RG.zoom_id("w", 10.0, 20.0, 4000, 4, 1, up=list(u))


def test_en_to_grid_turns_with_the_frame():
    for up, want in ((None, (0.0, 1.0)), (90.0, (-1.0, 0.0))):  # north, in a north-up and an east-up square
        f = Frame(30.0, 40.0, up=RG.up_of(30.0, 40.0, up))
        xs = (np.arange(5) - 2.0) * 10.0
        X, Y = np.meshgrid(xs, -xs)
        P = f.to_sphere(X.ravel(), Y.ravel()) * R_KM
        gx, gy = en_to_grid(P, 5, 5, np.zeros(25), np.ones(25))
        assert np.allclose((gx[12], gy[12]), want, atol=1e-6)


def test_turned_zoom_saves_its_orientation(data_root):
    """A zoom turned 90 degrees keeps its orientation in zoom.json, its corners turn with it, and it shows the same
    ground as the north-up zoom of the same centre (both are built from the same coarse world)."""
    g = build_grid(5)
    c = xyz(np.radians(38.0), np.radians(10.0))
    d = np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM
    elev = np.where(d < 2200, 250 + 0.5 * (2200 - d), -3000.0)
    extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2), "sediment_cover": np.where(elev > 0, 0.2, 6.0)}
    path = W.save(W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 5}, erosion=0.0), "turn test")
    quiet = dict(size_km=240, res_km=4, iterations=4, log=lambda *a: None)
    o0 = RG.zoom(str(path), 38.0, 10.0, **quiet)
    o1 = RG.zoom(str(path), 38.0, 10.0, up=90.0, **quiet)
    assert o0.name != o1.name
    m0, L0 = RG.load(o0, decode=True)
    m1, L1 = RG.load(o1, decode=True)
    assert "up" not in m0["center"] and m1["projection"]["up_bearing_deg"] == 90.0
    assert np.allclose(m1["center"]["up"], Frame(38.0, 10.0).e, atol=1e-5)
    # turned 90 degrees clockwise: its north-west corner is the north-up square's north-east one
    assert np.allclose(m1["projection"]["corners_latlon"]["nw"], m0["projection"]["corners_latlon"]["ne"], atol=1e-3)
    # the same ground: the north-up array turned a quarter (np.rot90 k=1: anticlockwise) is the turned one
    h0, h1 = L0["elevation"], L1["elevation"]
    assert np.corrcoef(np.rot90(h0, 1).ravel(), h1.ravel())[0, 1] > 0.9
