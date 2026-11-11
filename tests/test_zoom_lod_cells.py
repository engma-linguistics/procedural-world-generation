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


def _seam(za, zb, a, b):
    sa, sb = ZM.source_of(za), ZM.source_of(zb)
    P = LB._line(a, b)
    return LB.line_seam(sa, sb, P), LB.line_seam(sa, LB.resampled(sa, sb), P)


def test_tiles_at_a_cell_edge_fade_to_it(pair):
    assert pair["b"] in pair["near"][0] and pair["a"] in pair["near"][1]
    assert LB.near_lines(L.Key(pair["a"], 3, 0, 0)) == []  # (finer levels fade to their parents)


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

