"""The tiling of the sphere by land-zoom sections (PW-1319): coverage, margin and neighbours."""
import numpy as np

from planet.zoom import tiling as T
from planet.zoom.regional import Frame


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
