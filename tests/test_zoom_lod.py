"""The level-of-detail tile pyramid (planet/zoom/lod.py; docs/review/zoom/lod-plan-v2.md section 1)."""
import numpy as np
import pytest

from planet import api
from planet.zoom import fine as ZF
from planet.zoom import lod as L
from planet.zoom import tiling as T


def test_ladder_nests_and_steps_within_the_fine_rules():
    assert L.SQUARE_KM == api.SECTION_KM
    for k in sorted(L.LEVELS):
        r, t = L.LEVELS[k]
        assert abs(L.tile_px(k) * r - t) < 1e-9  # whole pixels per tile
        assert abs(L.per_side(k) * t - L.SQUARE_KM) < 1e-9  # whole tiles per square
        if k < L.FINEST:
            step = r / L.res_km(k + 1)
            assert ZF.MIN_STEP <= step <= ZF.MAX_STEP  # each level is a legal fine zoom of the one above
            assert ZF.PARENT_RES[0] <= r <= ZF.PARENT_RES[1]
            assert abs(L.branching(k) * L.tile_km(k + 1) - t) < 1e-9  # a tile is exactly n x n children
            assert L.tile_px(k + 1) <= ZF.MAX_PX


def test_siblings_share_one_lattice_and_children_tile_their_parent():
    a, b = L.Key("px.1.1", 3, 10, 7), L.Key("px.1.1", 3, 11, 7)
    xa, ya = L.lattice(a)
    xb, yb = L.lattice(b)
    n, r = L.tile_px(3), L.res_km(3)
    # b's first column is one pixel east of a's last, same rows: one grid
    np.testing.assert_allclose(xb.reshape(n, n)[:, 0] - xa.reshape(n, n)[:, -1], r)
    np.testing.assert_allclose(yb.reshape(n, n)[:, 0], ya.reshape(n, n)[:, -1])
    # with a halo, the halo pixels are the neighbour's own pixels
    xh, yh = L.lattice(a, halo_px=2)
    m = n + 4
    np.testing.assert_allclose(xh.reshape(m, m)[2, -2:], xb.reshape(n, n)[0, :2])
    # children cover the parent exactly, and point back to it
    p = L.Key("px.1.1", 2, 3, 4)
    kids = L.children(p)
    assert len(kids) == L.branching(2) ** 2
    assert all(L.parent(k) == p for k in kids)
    x0, x1, y0, y1 = L.rect(p)
    assert min(L.rect(k)[0] for k in kids) == pytest.approx(x0) and max(L.rect(k)[1] for k in kids) == pytest.approx(x1)
    assert min(L.rect(k)[2] for k in kids) == pytest.approx(y0) and max(L.rect(k)[3] for k in kids) == pytest.approx(y1)
    assert sum((L.rect(k)[1] - L.rect(k)[0]) * (L.rect(k)[3] - L.rect(k)[2]) for k in kids) == pytest.approx((x1 - x0) * (y1 - y0))
    assert L.ancestors(L.Key("px.1.1", 4, 133, 201))[-1] == L.Key("px.1.1", 1, 0, 0)
    assert str(L.Key.parse("py.0.2/3/5/6")) == "py.0.2/3/5/6"
    with pytest.raises(ValueError):
        L.Key("px.1.1", 2, L.per_side(2), 0)


def test_a_point_of_the_planet_has_one_owner_tile_and_lands_where_the_tiling_says():
    rng = np.random.default_rng(3)
    p = rng.normal(size=(40, 3))
    p /= np.linalg.norm(p, axis=1, keepdims=True)
    n = T.choose_n(L.SQUARE_KM, 190.0)
    f, i, j = T.locate(p, n)
    names = list(T.FACES)
    for k in range(len(p)):
        cell = f"{names[f[k]]}.{i[k]}.{j[k]}"
        x, y = L.frame(cell).to_plane(p[k:k + 1])
        assert L.in_cell(cell, x, y)[0]  # the plane outline agrees with tiling.locate
        for lev in (2, 3, 4):
            key = L.tile_at(cell, lev, float(x[0]), float(y[0]))
            assert L.exists(key)
            x0, x1, y0, y1 = L.rect(key)
            assert x0 <= x[0] < x1 and y0 < y[0] <= y1
            # the tile's pixels map back onto the sphere where the tiling's frame puts them
            q = L.to_sphere(key, x, y)
            np.testing.assert_allclose(q[0], p[k], atol=1e-9)


def test_tiles_exist_only_near_their_cell_and_parents_cover_children():
    cell = "pz.1.0"
    ex = [L.Key(cell, 2, tx, ty) for ty in range(L.per_side(2)) for tx in range(L.per_side(2))]
    have = [k for k in ex if L.exists(k)]
    assert 0 < len(have) < len(ex)  # the square's far corners hold no tile of this cell
    # every existing tile's centre is inside the cell or within its own size of it
    for k in have:
        assert L.cell_distance(cell, L.rect(k)) <= L.PAD_PX * L.res_km(2)
    # a child that exists has a parent that exists, and its build window's sources exist and cover its own square
    for k in have[:6]:
        for c in L.children(k)[::5]:
            if not L.exists(c):
                continue
            src = L.parent_sources(c)
            assert L.parent(c) in src
            x0, x1, y0, y1 = L.rect(c)
            assert min(L.rect(s)[0] for s in src) <= x0 and max(L.rect(s)[1] for s in src) >= x1
    # a child at its parent's west edge reads the western neighbour too (when that one exists)
    mid = L.tile_at(cell, 2, 0.0, 0.0)
    c = L.Key(cell, 3, mid.tx * L.branching(2), mid.ty * L.branching(2) + 1)
    assert {s.tx for s in L.parent_sources(c)} == {mid.tx - 1, mid.tx}


def test_covering_a_view_and_ids():
    cell = "px.1.1"
    r = (-300.0, 300.0, -100.0, 200.0)
    ks = L.covering(cell, 3, r)
    assert len(ks) == len({k for k in ks})
    xs = np.linspace(r[0] + 1, r[1] - 1, 9)
    ys = np.linspace(r[2] + 1, r[3] - 1, 9)
    for x in xs:
        for y in ys:
            assert L.tile_at(cell, 3, x, y) in ks
    a = L.tile_id("dba204", ks[0])
    assert a == L.tile_id("dba204", ks[0]) and len(a) == 6
    assert a != L.tile_id("dba204", ks[1]) and a != L.tile_id("dba204", ks[0], seed=2)
    assert [d["px"] for d in L.describe()] == [L.tile_px(k) for k in sorted(L.LEVELS)]
