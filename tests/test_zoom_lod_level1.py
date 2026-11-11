"""A cell's level 1 built on demand is matched to its neighbours already built (planet/zoom/lod_build.py, PW-1699;
docs/review/zoom/lod-plan-v2.md 2.3, step 3): which neighbours lod_build.tile matches to, and two neighbouring cells'
sections, built in either order, meeting at their shared cell edge. The sections are coarse (10 km/px, 400 px) on a
synthetic level-5 world so they build in seconds; the matching is match.py's, as at 4 km."""

import json

import numpy as np
import pytest

from planet import world as W
from planet.geo import R_KM, xyz
from planet.grid import build_grid
from planet.zoom import lod as L
from planet.zoom import lod_build as LB
from planet.zoom import match as ZM
from planet.zoom import regional as RG
from planet.zoom import tiling as T

CENTRE = (38.0, 10.0)
RES = 10.0


def _cell_at(lat, lon):
    return str(LB._cells_of(xyz(np.radians(lat), np.radians(lon))[None, :])[0])


# ---- which neighbours a level-1 build is matched to --------------------------------------------------------------

def test_level1_is_matched_to_the_neighbours_already_built(data_root, monkeypatch):
    """lod_build.tile on a level-1 key builds the cell's section matched to every neighbouring cell's level 1 already
    built (of this world and seed), none at first; a built one is found, not rebuilt."""
    (data_root / "worlds").mkdir()
    (data_root / "worlds" / "w0.json").write_text("{}")
    calls = []

    def fake_zoom(world_ref, lat, lon, size_km, res_km, seed, log=print, section=None, match=()):
        assert (lat, lon, size_km, res_km) == (None, None, L.SQUARE_KM, L.res_km(1))
        calls.append((section, tuple(match)))
        zid = f"z{len(calls):05d}"
        d = data_root / "zooms" / zid
        d.mkdir(parents=True)
        (d / "zoom.json").write_text(json.dumps({"id": zid, "section": section, "res_km": res_km, "seed": seed,
                                                 "source_world": {"id": "w0"}, "created": f"2026-11-11 00:00:{len(calls):02d}"}))
        return d

    monkeypatch.setattr(RG, "zoom", fake_zoom)
    a = "py.1.1"
    nb = T.section(a)["neighbours"]
    b, c = nb[0], nb[-1]
    far = next(s["id"] for s in T.sections() if s["id"] not in nb and s["id"] != a and a not in s["neighbours"])
    da = LB.tile("w0", f"{a}/1/0/0", log=lambda *_: None)
    assert calls[-1] == (a, ())
    db = LB.tile("w0", L.Key(b, 1, 0, 0), log=lambda *_: None)
    assert calls[-1] == (b, (da.name,))
    LB.tile("w0", L.Key(c, 1, 0, 0), log=lambda *_: None)
    assert calls[-1][0] == c and da.name in calls[-1][1]  # (b too, if b and c touch)
    assert set(calls[-1][1]) <= {da.name, db.name}
    n = len(calls)
    assert LB.tile("w0", L.Key(a, 1, 0, 0), log=lambda *_: None) == da and len(calls) == n  # (found)
    LB.tile("w0", L.Key(far, 1, 0, 0), log=lambda *_: None)
    assert calls[-1] == (far, ())
    # (another seed's sections are not this seed's neighbours)
    LB.tile("w0", L.Key(nb[1], 1, 0, 0), seed=2, log=lambda *_: None)
    assert calls[-1] == (nb[1], ())


# ---- two neighbouring cells meeting at their edge ----------------------------------------------------------------

@pytest.fixture(scope="module")
def world():
    """A continent round CENTRE with a range across it, on a level-5 grid."""
    g = build_grid(5)
    c = xyz(np.radians(CENTRE[0]), np.radians(CENTRE[1]))
    d = np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM
    ridge = np.arccos(np.clip(g.centers @ xyz(np.radians(44.0), np.radians(4.0)), -1, 1)) * R_KM
    elev = np.where(d < 3000, 250 + 0.3 * (3000 - d) + 2500 * np.exp(-(ridge / 400) ** 2), -3000.0)
    extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2), "sediment_cover": np.where(elev > 0, 0.2, 6.0)}
    return W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 5}, erosion=0.0)


def _pair():
    """The cell holding CENTRE and the neighbour sharing the edge with the most of the continent along it."""
    a = _cell_at(*CENTRE)
    best = None
    c = xyz(np.radians(CENTRE[0]), np.radians(CENTRE[1]))
    for b in T.section(a)["neighbours"]:
        P = LB.cell_line(a, b, 200)
        if len(P):
            on = (np.arccos(np.clip(P @ c, -1, 1)) * R_KM < 2800).sum()
            if best is None or on > best[0]:
                best = (on, b)
    return a, best[1]


def _section(world, cell, match=None):
    s = T.section(cell)
    z = RG.build(world, s["lat"], s["lon"], L.SQUARE_KM, RES, iterations=6, up=s["up"], section=cell,
                 match=match, log=lambda *_: None)
    return ZM.source_of(z, cell, section=cell)


@pytest.fixture(scope="module")
def sections(world):
    a, b = _pair()
    sa, sb = _section(world, a), _section(world, b)
    return a, b, {"a": sa, "b": sb, "b|a": _section(world, b, [sa]), "a|b": _section(world, a, [sb])}


@pytest.mark.parametrize("first, then", [("a", "b"), ("b", "a")])
def test_neighbours_meet_at_the_cell_edge_in_either_order(sections, first, then):
    """Built in either order, the later cell's section takes the earlier one's ground at every pixel of its own
    within a pixel of their shared edge (the owner line, where the viewer switches from one cell's tiles to the
    other's) and on the earlier one's side; along the line the two then differ only as much as the earlier section
    resampled onto the later one's lattice differs from itself (the floor for two lattices, LB.resampled), where the
    two built alone differ by several times that."""
    a, b, s = sections
    e, l = s[first], s[f"{then}|{first}"]
    P = LB.cell_line(a, b, 400)
    alone = LB.line_seam(s["a"], s["b"], P)
    matched = LB.line_seam(e, l, P)
    floor = LB.line_seam(e, LB.resampled(e, l), P)
    assert matched["n"] > 50 and alone["n"] > 50
    assert matched["median"] <= 1.1 * floor["median"] + 0.5 and matched["p90"] <= 1.1 * floor["p90"] + 0.5, (
        matched, floor)
    assert matched["median"] < 0.3 * alone["median"], (matched, alone)
    # at the later section's own pixels: its ground is the earlier one's, near the line and on the earlier's side
    nx, ny, res = l["nx"], l["ny"], l["res"]
    r, c = np.divmod(np.arange(nx * ny), nx)
    Q = l["frame"].to_sphere((c + 0.5 - nx / 2) * res, (ny / 2 - r - 0.5) * res)
    he, _, le, _, _, ins = ZM._sample(e, Q, e["res"])
    own = LB._cells_of(Q)
    d_line = np.min(np.linalg.norm(Q[:, None, :] - P[None, ::4, :], axis=2), axis=1) * R_KM
    on = le & l["land"].ravel() & (ins > 0) & ((own == (a if first == "a" else b)) | (d_line < res))
    d = np.abs(l["h"].ravel() - he)[on]
    assert on.sum() > 100 and np.median(d) < 0.5, (on.sum(), np.median(d))


def test_rivers_cross_the_cell_edge(sections):
    """A river of the earlier cell flowing over the line into the later one keeps its water there (match.inflows)."""
    a, b, s = sections
    got = []
    for first, then in (("a", "b"), ("b", "a")):
        cf, ct = (a, b) if first == "a" else (b, a)
        got += LB.line_rivers(s[first], cf, s[f"{then}|{first}"], ct, qmin=50.0)
    assert len(got) >= 2, got
    for qa, qb in got:
        assert qb >= 0.8 * qa, got
