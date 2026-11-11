"""Level-2 tiles of two neighbouring cells meeting at their shared cell edge (planet/zoom/lod_build.py, PW-1705;
docs/review/zoom/lod-plan-v2.md 2.3): both fade to ground carved once along the edge on the owner cell's lattice, so
at the edge they differ only as two lattices interpolating the same ground differ. Synthetic: each cell's level 1 is
one function of the place (two matched sections agree as closely) and level 2 is shrunk to 100 km tiles."""

import numpy as np
import pytest

from planet import world as W
from planet.geo import R_KM, xyz
from planet.grid import build_grid
from planet.kernels import accumulate
from planet.zoom import kernels as ZK
from planet.zoom import lod as L
from planet.zoom import lod_build as LB
from planet.zoom import match as ZM
from planet.zoom import regional as Z
from planet.zoom import tiling as T

CENTRE = (38.0, 10.0)
LEVELS = {1: (4.0, 4000.0), 2: (1.0, 100.0), 3: (0.25, 25.0), 4: (0.025, 2.5)}


@pytest.fixture(autouse=True)
def small_tiles(monkeypatch):
    monkeypatch.setattr(L, "LEVELS", LEVELS)


@pytest.fixture(scope="module")
def world():
    g = build_grid(4)
    c = xyz(np.radians(CENTRE[0]), np.radians(CENTRE[1]))
    d = np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM
    elev = np.where(d < 2500, 300 + 0.3 * (2500 - d), -3000.0)
    land = elev > 0
    extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2), "sediment_cover": np.where(land, 0.2, 6.0)}
    return W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 4}, erosion=0.0)


def _height(P):
    """Hills and valleys as a function of the place (km on the sphere), tilted down to the east."""
    X, Y, Zc = (P * R_KM).T
    return np.maximum(900.0 - 0.15 * Y + 180 * np.sin(X / 23.0) * np.cos(Zc / 17.0) + 90 * np.sin((Y + Zc) / 9.0),
                      20.0)


def _section(cell):
    """The cell's level 1 (1000 x 1000 px at 4 km on its plane), its ground _height of the place, routed with D8."""
    s = T.section(cell, L.SQUARE_KM)
    fr = L.frame(cell)
    n, r = 1000, 4.0
    k = np.arange(n) + 0.5
    X, Y = np.meshgrid(-2000 + k * r, 2000 - k * r)
    h = _height(fr.to_sphere(X.ravel(), Y.ravel())).reshape(n, n).astype(np.float32)
    rec, order = ZK.flood_d8(h.ravel().astype(float), (X.ravel() > 1990) | (X.ravel() < -1990), n, n, 1e-3,
                             np.full(n * n, 0.5))[1:3]
    area = accumulate(rec, order, np.full(n * n, r * r))
    q = accumulate(rec, order, np.full(n * n, r * r * 1e6 * 0.4 / 3.15e7))
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
    meta = {"id": f"sec-{cell}", "name": "test world: section", "res_km": r, "nx": n, "ny": n, "section": cell,
            "center": {"lat": s["lat"], "lon": s["lon"], "up": [float(v) for v in s["up"]]}, "size_km": n * r,
            "source_world": {"id": "none", "name": "test world"}, "seed": 1, "stats": {"falls": [], "volcanoes": []}}
    return {L.Key(cell, 1, 0, 0): (meta, layers)}


@pytest.fixture(scope="module")
def pair(world):
    """Cells a (holding CENTRE) and b (its edge neighbour nearest CENTRE), a level-2 tile of each over the point of
    their edge nearest CENTRE, built with a the owner (b's level 1 matched to a's), b's twice, and both without
    the edge's fade (as on main before PW-1705)."""
    mp = pytest.MonkeyPatch()
    mp.setattr(L, "LEVELS", LEVELS)
    c = xyz(np.radians(CENTRE[0]), np.radians(CENTRE[1]))
    a = str(LB._cells_of(c[None, :])[0])
    best = None
    for b in LB.cell_lines(a):
        P = LB._line(a, b)
        d = np.arccos(np.clip(P @ c, -1, 1)).min()
        if best is None or d < best[0]:
            best = (d, b, P[np.argmin(np.arccos(np.clip(P @ c, -1, 1)))])
    _, b, p0 = best
    sa, sb = _section(a), _section(b)
    # (b's tile holding the longest stretch of the edge near CENTRE, a's over the middle of it: they share most of it)
    P = LB._line(a, b)
    P = P[np.arccos(np.clip(P @ c, -1, 1)) * R_KM < np.arccos(np.clip(p0 @ c, -1, 1)) * R_KM + 300]
    x, y = L.frame(b).to_plane(P)
    tiles = [L.tile_at(b, 2, float(u), float(v)) for u, v in zip(x, y)]
    kb = max(sorted(set(tiles)), key=tiles.count)
    on = [i for i, t in enumerate(tiles) if t == kb]
    pm = P[on[len(on) // 2]]
    ka = L.tile_at(a, 2, *(float(v[0]) for v in L.frame(a).to_plane(pm[None, :])))
    quiet = dict(log=lambda *_: None)
    out = {"a": a, "b": b, "ka": ka, "kb": kb, "near": (LB.near_lines(ka), LB.near_lines(kb)),
           "za": LB.build(world, ka, sa, lines={b: (a, sa)}, **quiet),
           "zb": LB.build(world, kb, sb, lines={a: (a, sa)}, **quiet),
           "zb2": LB.build(world, kb, sb, lines={a: (a, sa)}, **quiet),
           "za0": LB.build(world, ka, sa, **quiet), "zb0": LB.build(world, kb, sb, **quiet)}
    mp.undo()
    return out


def _seam(za, zb, a, b, per_edge=LB.LINE_PER_EDGE):
    """(|a - b| at their shared edge's points, the same with b resampled from a: the floor); per_edge sets the points'
    spacing (LINE_PER_EDGE: 1 km)."""
    sa, sb = ZM.source_of(za), ZM.source_of(zb)
    P = LB._line(a, b) if per_edge == LB.LINE_PER_EDGE else LB.cell_line(*sorted((a, b)), per_edge)
    return LB.line_seam(sa, sb, P), LB.line_seam(sa, LB.resampled(sa, sb), P)


def test_tiles_at_a_cell_edge_fade_to_it(pair):
    assert pair["b"] in pair["near"][0] and pair["a"] in pair["near"][1]
    assert LB.near_lines(L.Key(pair["a"], 1, 0, 0)) == []  # (level 1 is matched, match.py)


def test_two_cells_meet_at_their_edge_as_two_lattices_of_one_ground(pair):
    """At the edge the two cells' tiles differ by no more than the owner's tile resampled onto the other's lattice
    differs from itself (within 10%): the same line with no seam (PW-1697's rule, for two lattices); without the
    edge's fade they differ by more."""
    seam, floor = _seam(pair["za"], pair["zb"], pair["a"], pair["b"])
    alone, _ = _seam(pair["za0"], pair["zb0"], pair["a"], pair["b"])
    assert seam["n"] > 40, seam
    assert seam["median"] <= 1.1 * floor["median"] + 0.5 and seam["p90"] <= 1.1 * floor["p90"] + 0.5, (seam, floor)
    assert seam["median"] < 0.5 * alone["median"], (seam, alone)


def test_a_tile_at_a_cell_edge_rebuilds_bit_identical(pair):
    for k, v in pair["zb"]["layers"].items():
        assert np.array_equal(np.asarray(v), np.asarray(pair["zb2"]["layers"][k]), equal_nan=True), k


def test_the_owner_is_the_earlier_cell(data_root):
    import json

    def sec(cell, zid, matched=()):
        d = data_root / "zooms" / zid
        d.mkdir(parents=True)
        (d / "zoom.json").write_text(json.dumps({"id": zid, "section": cell, "res_km": L.res_km(1), "seed": 1,
                                                 "source_world": {"id": "w0"}, "created": zid,
                                                 **({"matched_to": list(matched)} if matched else {})}))
    sec("py.1.1", "z1")
    assert LB.line_owner("w0", "py.0.1", "py.1.1") == "py.1.1"  # (only it built: the other will match it)
    sec("py.0.1", "z2", ["z1"])
    assert LB.line_owner("w0", "py.0.1", "py.1.1") == LB.line_owner("w0", "py.1.1", "py.0.1") == "py.1.1"
    sec("py.1.0", "z3", ["z2", "z1"])  # (a corner's owner: the earliest of its cells, py.0.0 not built)
    assert LB.owner_of("w0", ("py.0.0", "py.0.1", "py.1.0", "py.1.1")) == "py.1.1"


def _saved(z, key, root):
    """A built tile as a parent source (meta, decoded layers): saved under root's zooms/ and loaded back."""
    from planet import store as S
    old = S._root
    S.set_root(root)
    try:
        return Z.load(LB.save(z, "w0", key), decode=True)
    finally:
        S._root = old


@pytest.fixture(scope="module")
def pair3(world, tmp_path_factory):
    """Level 3 at the same edge (PW-1708): a's (the owner's) and b's level-2 tiles under a level-3 tile of each over
    the edge's point nearest CENTRE (both faded to the edge at level 2, as built), then the two level-3 tiles faded to
    the edge's level-3 ground (carved on a's level-3 lattice from a's level-2 tiles), b's twice, and both unfaded."""
    mp = pytest.MonkeyPatch()
    mp.setattr(L, "LEVELS", LEVELS)
    root = tmp_path_factory.mktemp("lod3")
    quiet = dict(log=lambda *_: None)
    c = xyz(np.radians(CENTRE[0]), np.radians(CENTRE[1]))
    a = str(LB._cells_of(c[None, :])[0])
    b = min(LB.cell_lines(a), key=lambda o: np.arccos(np.clip(LB._line(a, o) @ c, -1, 1)).min())
    P = LB._line(a, b)
    pm = P[np.argmin(np.arccos(np.clip(P @ c, -1, 1)))]
    ka, kb = (L.tile_at(cl, 3, *(float(v[0]) for v in L.frame(cl).to_plane(pm[None, :]))) for cl in (a, b))
    sec = {a: _section(a), b: _section(b)}
    need = set(L.parent_sources(ka)) | set(L.parent_sources(kb))
    for k in (ka, kb):
        plan = LB._line_plan(k, b if k.cell == a else a, a)
        need |= {p for bl, _ in plan[4] for p in LB._block_parents(a, 3, bl)}
    l2 = {}
    for k in sorted(need):
        other = b if k.cell == a else a
        lines = {other: (a, sec[a])} if other in LB.near_lines(k) else {}
        l2[k] = _saved(LB.build(world, k, sec[k.cell], lines=lines, **quiet), k, root)
    osrc = {k: v for k, v in l2.items() if k.cell == a}

    def mine(k):
        return {p: l2[p] for p in L.parent_sources(k)}
    out = {"a": a, "b": b, "ka": ka, "kb": kb, "near": (LB.near_lines(ka), LB.near_lines(kb)),
           "za": LB.build(world, ka, mine(ka), lines={b: (a, osrc)}, **quiet),
           "zb": LB.build(world, kb, mine(kb), lines={a: (a, osrc)}, **quiet),
           "zb2": LB.build(world, kb, mine(kb), lines={a: (a, osrc)}, **quiet),
           "za0": LB.build(world, ka, mine(ka), **quiet), "zb0": LB.build(world, kb, mine(kb), **quiet)}
    mp.undo()
    return out


@pytest.mark.slow
def test_level3_tiles_meet_at_their_cell_edge_as_two_lattices_of_one_ground(pair3):
    """PW-1708: as level 2, one level down: within 10% of the same line with no seam, under half the unfaded seam."""
    assert pair3["b"] in pair3["near"][0] and pair3["a"] in pair3["near"][1]
    seam, floor = _seam(pair3["za"], pair3["zb"], pair3["a"], pair3["b"], 16000)  # (points 250 m apart: a pixel)
    alone, _ = _seam(pair3["za0"], pair3["zb0"], pair3["a"], pair3["b"], 16000)
    assert seam["n"] > 40, seam
    assert seam["median"] <= 1.1 * floor["median"] + 0.5 and seam["p90"] <= 1.1 * floor["p90"] + 0.5, (seam, floor)
    assert seam["median"] < 0.5 * alone["median"], (seam, alone)
    for k, v in pair3["zb"]["layers"].items():
        assert np.array_equal(np.asarray(v), np.asarray(pair3["zb2"]["layers"][k]), equal_nan=True), k


def test_every_cell_at_a_corner_names_the_same_corner():
    for cells, P in LB.cell_corners("py.1.1"):
        assert len(cells) in (3, 4) and "py.1.1" in cells
        for o in cells:
            assert dict(LB.cell_corners(o))[cells] == P


@pytest.fixture(scope="module")
def corner(world):
    """The level-2 tiles of the cells meeting at a's corner nearest CENTRE within 22 km of it, faded to their cells'
    edges (every edge's owner the first of its two cells by name) with and without the corner's own ground (owner: the
    first of all by name)."""
    mp = pytest.MonkeyPatch()
    mp.setattr(L, "LEVELS", LEVELS)
    quiet = dict(log=lambda *_: None)
    c = xyz(np.radians(CENTRE[0]), np.radians(CENTRE[1]))
    a = str(LB._cells_of(c[None, :])[0])
    cells, P = min(LB.cell_corners(a), key=lambda cp: np.arccos(np.clip(np.dot(cp[1], c), -1, 1)))
    sec = {cl: _section(cl) for cl in cells}
    out = {"cells": cells, "P": np.array(P), "with": {}, "without": {}}
    for cl in cells:
        x, y = (float(v[0]) for v in L.frame(cl).to_plane(np.array([P])))
        for k in L.covering(cl, 2, (x - 22, x + 22, y - 22, y + 22)):
            lines = {o: (min(cl, o), sec[min(cl, o)]) for o in LB.near_lines(k) if o in cells}
            assert cells in LB.near_corners(k)
            out["with"][k] = LB.build(world, k, sec[cl], lines=lines, corners={cells: (cells[0], sec[cells[0]])},
                                      **quiet)
            out["without"][k] = LB.build(world, k, sec[cl], lines=lines, **quiet)
    mp.undo()
    return out


def _corner_seams(corner, which):
    """{(a, b): (seam, floor)} along each edge of the corner's cells within 20 km of it, pooled over every pair of their
    tiles: |a - b| (lod_build.line_seam), and the same with both sides resampled from the corner owner's tiles (the
    same line with no seam when the ground is on a third lattice: each side interpolates the owner's)."""
    cells, P0 = corner["cells"], corner["P"]
    owner = [ZM.source_of(z) for k, z in corner[which].items() if k.cell == cells[0]]

    def from_owner(s):
        for so in owner:
            s = LB.resampled(so, s)
        return s
    out = {}
    for i, a in enumerate(cells):
        for b in cells[i + 1:]:
            if b not in LB.cell_lines(a):  # (a diagonal: they meet only at the corner)
                continue
            P = LB._line(a, b)
            P = P[np.arccos(np.clip(P @ P0, -1, 1)) * R_KM < 20.0]
            d, f = [], []
            for ka, za in corner[which].items():
                for kb, zb in corner[which].items():
                    if ka.cell == a and kb.cell == b:
                        sa, sb = ZM.source_of(za), ZM.source_of(zb)
                        d.append(LB.line_seam(sa, sb, P)["d"])
                        f.append(LB.line_seam(from_owner(sa), from_owner(sb), P)["d"])
            d, f = np.concatenate(d), np.concatenate(f)
            out[(a, b)] = tuple({"n": len(v), "median": float(np.median(v)) if len(v) else np.nan,
                                 "p90": float(np.percentile(v, 90)) if len(v) else np.nan} for v in (d, f))
    return out


def test_cells_meeting_at_a_corner_blend_one_ground_there(corner):
    """PW-1708: along every edge within 20 km of a corner where three or four cells meet, the two cells' tiles differ
    by no more than both resampled from the corner's owner (within 10%): each cell blends one ground carved round the
    corner. Each blending its own two edges' grounds (no corner ground), the worst edge differs by more."""
    seams, alone = _corner_seams(corner, "with"), _corner_seams(corner, "without")
    assert len(seams) >= 3
    for ab, (seam, floor) in seams.items():
        assert seam["n"] >= 10, (ab, seam)
        assert seam["median"] <= 1.1 * floor["median"] + 0.5 and seam["p90"] <= 1.1 * floor["p90"] + 0.5, \
            (ab, seam, floor)
    assert max(s["p90"] for s, _ in seams.values()) < 0.5 * max(s["p90"] for s, _ in alone.values()), (seams, alone)
