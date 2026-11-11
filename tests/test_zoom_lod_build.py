"""Level-of-detail tiles built seam-true (planet/zoom/lod_build.py; docs/review/zoom/lod-plan-v2.md 2.2, PW-1689):
two sibling tiles of a synthetic level-1 section, built apart, on one pixel lattice; their edge steps against their
inside steps, the rivers crossing their shared edge, and a rebuild bit-identical. Level 2 is shrunk to 100 km tiles
(100 px) so the builds take seconds; the ladder's rules are lod.py's."""

import numpy as np
import pytest

from planet import world as W
from planet.geo import R_KM, xyz
from planet.grid import build_grid
from planet.kernels import accumulate
from planet.zoom import fine as ZF
from planet.zoom import kernels as ZK
from planet.zoom import lod as L
from planet.zoom import lod_build as LB
from planet.zoom import regional as Z
from planet.zoom import tiling as T

CENTRE = (38.0, 10.0)
LEVELS = {1: (4.0, 4000.0), 2: (1.0, 100.0), 3: (0.25, 25.0), 4: (0.025, 2.5)}


@pytest.fixture(autouse=True)
def small_tiles(monkeypatch):
    monkeypatch.setattr(L, "LEVELS", LEVELS)


def _cell():
    n = T.choose_n(L.SQUARE_KM, 190.0)
    f, i, j = T.locate(xyz(np.radians(CENTRE[0]), np.radians(CENTRE[1]))[None, :], n)
    return f"{list(T.FACES)[f[0]]}.{i[0]}.{j[0]}"


@pytest.fixture(scope="module")
def world():
    g = build_grid(4)
    c = xyz(np.radians(CENTRE[0]), np.radians(CENTRE[1]))
    d = np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM
    elev = np.where(d < 2500, 300 + 0.3 * (2500 - d), -3000.0)
    land = elev > 0
    extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2), "sediment_cover": np.where(land, 0.2, 6.0)}
    return W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 4}, erosion=0.0)


@pytest.fixture(scope="module")
def section():
    """A level-1 section (1000 x 1000 px at 4 km) of the cell holding CENTRE: hills on a plain tilted east, a broad
    valley running east along y = y0 (rivers cross the tiles' east edges), routed with the zooms' D8."""
    cell = _cell()
    s = T.section(cell, L.SQUARE_KM)
    fr = L.frame(cell)
    x0, y0 = (float(v[0]) for v in fr.to_plane(xyz(np.radians(CENTRE[0]), np.radians(CENTRE[1]))[None, :]))
    n, r = 1000, 4.0
    k = np.arange(n) + 0.5
    X, Y = np.meshgrid(-2000 + k * r, 2000 - k * r)
    h = (900.0 - 0.6 * (X - x0) + 6.0 * np.abs(Y - y0) + 180 * np.sin(X / 23.0) * np.cos(Y / 17.0)
         + 90 * np.sin((X + Y) / 9.0))
    h = np.maximum(h, 20.0).astype(np.float32)
    rec, order = ZK.flood_d8(h.ravel().astype(float), np.zeros(n * n, bool) | (X.ravel() > 1990), n, n, 1e-3,
                             np.full(n * n, 0.5))[1:3]
    area = accumulate(rec, order, np.full(n * n, r * r))
    q = accumulate(rec, order, np.full(n * n, r * r * 1e6 * 0.4 / 3.15e7))  # (400 mm/yr of runoff)
    z0 = np.zeros((n, n), np.float32)
    layers = {
        "elevation": h, "water": np.zeros((n, n), np.uint8), "lake_depth": z0, "lake_kind": np.zeros((n, n), np.uint8),
        "discharge": q.reshape(n, n), "drainage_area": area.reshape(n, n),
        "receiver": Z.d8_slots(rec, n).reshape(n, n), "precipitation": np.full((n, n), 800.0),
        "precipitation_jul": np.full((n, n), 500.0), "precipitation_jan": np.full((n, n), 1100.0),
        "temperature": np.full((n, n), 12.0), "ice": z0, "tide_range": z0, "wave_power": z0,
        "rock": np.full((n, n), 2, np.uint8), "surface_rock": np.full((n, n), 2, np.uint8),
        "climate": np.full((n, n), 14, np.uint8), "biome": np.full((n, n), 3, np.uint8),
        "landform": np.zeros((n, n), np.uint8), "wetland": np.zeros((n, n), np.uint8),
        "coastal_life": np.zeros((n, n), np.uint8),
    }
    meta = {"id": "sec001", "name": "test world: section", "res_km": r, "nx": n, "ny": n, "section": cell,
            "center": {"lat": s["lat"], "lon": s["lon"], "up": [float(v) for v in s["up"]]}, "size_km": n * r,
            "source_world": {"id": "none", "name": "test world"}, "seed": 1,
            "stats": {"falls": [], "volcanoes": []}}
    return cell, (x0, y0), meta, layers


@pytest.fixture(scope="module")
def siblings(section, world):
    mp = pytest.MonkeyPatch()
    mp.setattr(L, "LEVELS", LEVELS)
    cell, (x0, y0), meta, layers = section
    a = L.tile_at(cell, 2, x0 - 1.0, y0)  # (the valley's river crosses a's east edge into b)
    b = L.Key(cell, 2, a.tx + 1, a.ty)
    src = {L.Key(cell, 1, 0, 0): (meta, layers)}
    za = LB.build(world, a, src, log=lambda *_: None)
    zb = LB.build(world, b, src, log=lambda *_: None)
    za2 = LB.build(world, a, src, log=lambda *_: None)
    mp.undo()
    return a, b, za, zb, za2


def test_tiles_lie_on_their_levels_lattice(section):
    cell = section[0]
    k = L.Key(cell, 2, 17, 21)
    fr = L.tile_frame(k)
    n, r = L.tile_px(2), L.res_km(2)
    xs = (np.arange(n) + 0.5 - n / 2) * r
    X, Y = np.meshgrid(xs, xs[::-1])
    P = fr.to_sphere(X.ravel(), Y.ravel())
    lx, ly = L.lattice(k)
    np.testing.assert_allclose(L.frame(cell).to_sphere(lx, ly), P, atol=1e-12)
    # zoom.json's centre rebuilds the same frame (regional.center_of / frame_of)
    c = Z.center_of(fr, *Z._latlon(fr.c))
    f2 = Z.frame_of(c)
    np.testing.assert_allclose(f2.to_sphere(X.ravel(), Y.ravel()), P, atol=1e-12)


def test_siblings_read_the_same_parent(section):
    cell, (x0, y0), meta, layers = section
    a = L.tile_at(cell, 2, x0 - 1.0, y0)
    b = L.Key(cell, 2, a.tx + 1, a.ty)
    src = {L.Key(cell, 1, 0, 0): (meta, layers)}
    (ma, la), (mb, lb) = L.parent_mosaic(a, src), L.parent_mosaic(b, src)
    ca, cb = ma["mosaic"]["window_px"], mb["mosaic"]["window_px"]
    lo, hi = max(ca[0], cb[0]), min(ca[1], cb[1])
    assert hi - lo >= 2 * L.parent_margin_px()  # (the windows overlap round the shared edge)
    for k in ("elevation", "discharge", "receiver"):  # (a window's own border: its water leaves it there)
        np.testing.assert_array_equal(la[k][1:-1, lo - ca[0] + 1:hi - ca[0] - 1], lb[k][1:-1, lo - cb[0] + 1:hi - cb[0] - 1])


def test_rebuilt_tile_is_bit_identical(siblings):
    _, _, za, _, za2 = siblings
    for k, v in za["layers"].items():
        np.testing.assert_array_equal(np.asarray(v), np.asarray(za2["layers"][k]), err_msg=k)


def test_rivers_cross_the_shared_edge_with_the_same_discharge(siblings):
    _, _, za, zb, _ = siblings
    pa, pb = za["layers"]["river_phase"], zb["layers"]["river_phase"]
    qa, qb = za["layers"]["discharge"][:, -1], zb["layers"]["discharge"][:, 0]
    ia, ib = np.flatnonzero(np.isfinite(pa[:, -1])), np.flatnonzero(np.isfinite(pb[:, 0]))
    cross = [(i, min(abs(qa[i] - qb[j]) / max(qa[i], qb[j]) for j in ib if abs(i - j) <= 1))
             for i in ia if (np.abs(ib - i) <= 1).any()]
    assert cross, "no imposed river crosses the edge"
    big = max(cross, key=lambda c: qa[c[0]])
    assert qa[big[0]] > 10.0 and big[1] <= 0.05  # (the valley's river: the parent's water on both sides)
    assert np.mean([d <= 0.05 for _, d in cross]) >= 0.9


def _steps(siblings):
    _, _, za, zb, _ = siblings
    ha, hb = za["layers"]["elevation"], zb["layers"]["elevation"]
    off = ~(np.isfinite(za["layers"]["river_phase"][:, -1]) | np.isfinite(zb["layers"]["river_phase"][:, 0]))
    across, inside = LB.edge_steps(ha, hb, 1, band=(16, 48))
    return across[off], inside  # (land off the imposed courses: their beds are the parent's on both sides)


def test_no_cliff_along_the_shared_edge(siblings):
    across, inside = _steps(siblings)
    assert across.max() < 4 * np.percentile(inside, 99)
    assert np.percentile(across, 90) < 1.5 * np.percentile(inside, 90)


def test_edge_steps_like_the_inside(siblings, section, world):
    """The edge is carved like the inside (PW-1694): the steps across the shared edge are those the same line has
    with no seam at all (one block carved over both tiles, lod_build.carve_block), within 10% (median and p90). The
    inside band 16-48 px away is not the reference: on single lines inside dba204 tiles (no seam) its ratio to the
    band ran 0.4-1.4 (median) and 0.6-1.9 (p90)
    (lod-plan-v2.md State, lane 293)."""
    a, b, za, zb, _ = siblings
    across, inside = _steps(siblings)
    cell, _, meta, layers = section
    src = {L.Key(cell, 1, 0, 0): (meta, layers)}
    n, m = L.tile_px(2), 40
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(L, "LEVELS", LEVELS)
        hw = LB.carve_block(world, a, src, (a.tx * n - m, (b.tx + 1) * n + m, a.ty * n, (a.ty + 1) * n))
    off = ~(np.isfinite(za["layers"]["river_phase"][:, -1]) | np.isfinite(zb["layers"]["river_phase"][:, 0]))
    ref, ref_in = LB.edge_steps(hw[:, :m + n], hw[:, m + n:], 1, band=(16, 48))
    ref = ref[off]
    r_med = (np.median(across) / np.median(inside)) / (np.median(ref) / np.median(ref_in))
    r_90 = (np.percentile(across, 90) / np.percentile(inside, 90)) / (np.percentile(ref, 90) / np.percentile(ref_in, 90))
    assert 0.9 <= r_med <= 1.1, (r_med, r_90)
    assert 0.9 <= r_90 <= 1.1, (r_med, r_90)


@pytest.fixture(scope="module")
def volcano_siblings(section, world):
    """The siblings with a volcano on their shared edge (PW-1695): a cone 1500 m high on the section, its vent on the
    lattice line between them, 20 km north of the valley."""
    mp = pytest.MonkeyPatch()
    mp.setattr(L, "LEVELS", LEVELS)
    cell, (x0, y0), meta, layers = section
    a = L.tile_at(cell, 2, x0 - 1.0, y0)
    b = L.Key(cell, 2, a.tx + 1, a.ty)
    xv, yv = L.rect(a)[1], y0 + 20.0
    n, r = 1000, 4.0
    k = np.arange(n) + 0.5
    X, Y = np.meshgrid(-2000 + k * r, 2000 - k * r)
    h = layers["elevation"] + (1500.0 * np.exp(-((X - xv) ** 2 + (Y - yv) ** 2) / (2 * 16.0 ** 2))).astype(np.float32)
    lat, lon = Z._latlon(L.frame(cell).to_sphere(np.array([xv]), np.array([yv]))[0])
    ic, ir = int((xv + 2000) / r), int((2000 - yv) / r)
    top = float(h[ir - 2:ir + 3, ic - 2:ic + 3].max()) + 50.0
    vol = {"lat": lat, "lon": lon, "top_m": top, "height_m": 1500.0, "kind": "arc", "status": "active"}
    m2 = {**meta, "id": "sec002", "stats": {"falls": [], "volcanoes": [vol]}}
    src = {L.Key(cell, 1, 0, 0): (m2, {**layers, "elevation": h})}
    za = LB.build(world, a, src, log=lambda *_: None)
    zb = LB.build(world, b, src, log=lambda *_: None)
    mp.undo()
    return a, za, zb


def test_a_volcano_on_an_edge_is_drawn_by_both_tiles(volcano_siblings):
    a, za, zb = volcano_siblings
    va, vb = za["stats"]["volcanoes"], zb["stats"]["volcanoes"]
    assert len(va) == 1 and len(vb) == 1  # (listed by both: finer levels find it whichever parent they read)
    assert va[0]["owner"] + vb[0]["owner"] == 1  # (owned by the tile whose pixels hold its vent)
    assert va[0]["vent_px"][0] == vb[0]["vent_px"][0] and va[0]["vent_px"][1] - vb[0]["vent_px"][1] == L.tile_px(2)
    ha, hb = za["layers"]["elevation"].astype(float), zb["layers"]["elevation"].astype(float)
    row = va[0]["vent_px"][0]
    rows = slice(max(row - 12, 0), row + 13)
    # the cone stands on both sides of the edge (not cut off at it)
    assert np.median(ha[rows, -3:]) > np.median(ha[rows, -40]) + 300
    assert np.median(hb[rows, :3]) > np.median(hb[rows, 40]) + 300


def test_no_cliff_over_a_volcano_on_an_edge(volcano_siblings):
    a, za, zb = volcano_siblings
    ha, hb = za["layers"]["elevation"].astype(float), zb["layers"]["elevation"].astype(float)
    row = za["stats"]["volcanoes"][0]["vent_px"][0]
    rows = slice(max(row - 12, 0), row + 13)
    across = np.abs(hb[rows, 0] - ha[rows, -1])
    inside = np.concatenate([np.abs(np.diff(ha[rows, -24:], axis=1)).ravel(),
                             np.abs(np.diff(hb[rows, :24], axis=1)).ravel()])
    assert across.max() <= inside.max()
    assert np.median(across) <= 1.5 * np.median(inside)
