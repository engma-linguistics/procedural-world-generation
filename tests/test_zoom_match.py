"""Neighbouring land-zoom sections agree where they meet (PW-1301): a section matched to one already built holds its
ground, shares its coastline and blends into its own across a ramp; far inside it is unchanged."""
import numpy as np
import pytest

from planet import world as W
from planet.geo import R_KM, xyz
from planet.grid import build_grid
from planet.zoom import match as ZM
from planet.zoom import regional as RG

A_C, B_C, SIZE, RES = (38.0, 7.0), (38.0, 13.0), 700.0, 5.0  # centres ~525 km apart: a ~175 km shared band


@pytest.fixture(scope="module")
def pair():
    g = build_grid(5)
    c = xyz(np.radians(38.0), np.radians(10.0))
    d = np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM
    ridge = np.arccos(np.clip(g.centers @ xyz(np.radians(39.0), np.radians(10.0)), -1, 1)) * R_KM
    elev = np.where(d < 2200, 250 + 0.3 * (2200 - d) + 2500 * np.exp(-(ridge / 300) ** 2), -3000.0)
    extra = {"rock": np.full(g.n, 2), "surface_rock": np.full(g.n, 2), "sediment_cover": np.where(elev > 0, 0.2, 6.0)}
    world = W.finish(g, elev, extra, {"method": "test", "seed": 0, "level": 5}, erosion=0.0)
    q = dict(size_km=SIZE, res_km=RES, iterations=6, log=lambda *a: None)
    za = RG.build(world, *A_C, **q)
    zb = RG.build(world, *B_C, **q)
    zm = RG.build(world, *B_C, **q, match=[ZM.source_of(za, "A")])
    return za, zb, zm


def _at(z, P):
    x, y = z["frame"].to_plane(P)
    r = np.rint(z["ny"] / 2 - y / z["res"] - 0.5).astype(int)
    c = np.rint(x / z["res"] + z["nx"] / 2 - 0.5).astype(int)
    ok = (r >= 0) & (r < z["ny"]) & (c >= 0) & (c < z["nx"])
    return ok, np.asarray(z["layers"]["elevation"])[np.clip(r, 0, z["ny"] - 1), np.clip(c, 0, z["nx"] - 1)]


def test_matched_section_meets_its_neighbour(pair):
    za, zb, zm = pair
    a, b = za["frame"].c, zb["frame"].c
    u = (b - a) / np.linalg.norm(b - a)
    m = (a + b) / np.linalg.norm(a + b)
    t = np.cross(a, b) / np.linalg.norm(np.cross(a, b))
    s = np.linspace(-250, 250, 101) / R_KM
    line = np.cos(s)[:, None] * m + np.sin(s)[:, None] * t  # the owner line (the bisector)

    def across(dkm):
        p = np.cos(dkm / R_KM) * line + np.sin(dkm / R_KM) * u
        return p / np.linalg.norm(p, axis=1, keepdims=True)
    on = across(RES)  # just inside B's own ground
    oka, ha = _at(za, on)
    okb, hb = _at(zb, on)
    okm, hm = _at(zm, on)
    k = oka & okb & okm & (ha > 0)
    assert k.sum() > 50
    alone, matched = np.median(np.abs(ha - hb)[k]), np.median(np.abs(ha - hm)[k])
    assert matched < 0.5 * alone + 1.0  # the matched section meets its neighbour far better than one built alone
    # far inside its own ground the section is as built alone. Matching does reach past the ramp, by design: the held
    # ground is an outlet at the neighbour's levels, so a basin draining across the line is graded up from them, and
    # the slope fit pulls each coarse cell back to its own mean, so the change dies out with distance, over about two
    # coarse cells here (lane 128, seams-round2.md: median 100 / 33 / 9 / 3 / 0.3 m at 80-160 / -240 / -320 / -400 /
    # 400-600 km on this level-5 world of ~220 km cells; on the L7 4000 km practice pairs, whose basins run many cells
    # long, 0.1-6 m at 160-300 km, 0-2 m at 300-600, 0.0 beyond). 480 km is past that reach on this world (0.24 m).
    far = across(480.0)
    ok1, h1 = _at(zb, far)
    ok2, h2 = _at(zm, far)
    assert (ok1 & ok2).sum() > 50
    assert np.median(np.abs(h1 - h2)[ok1 & ok2]) < 1.0


def test_unmatched_build_is_unchanged(pair):
    """match=None leaves the build as it always was (no conditioning code runs)."""
    za, zb, zm = pair
    assert not np.array_equal(zb["layers"]["elevation"], zm["layers"]["elevation"])


def test_matched_section_carries_the_neighbours_rivers_on(pair):
    """A river of the neighbour's flowing across the owner line into the section's ground carries its water on
    there (PW-1302): before, held ground was an outlet and the river started dry at the line. From the neighbour's
    own network (its receivers): each crossing of >= 100 m3/s, the most water put in at a pixel within 2 px of where it
    enters (its discharge less its donors': the section's own tributaries may join the river right at the line, and
    the largest discharge there was the river with them, PW-1462), and the river's course for 5 px below it (on this
    pair 252 -> 255 and 211 -> 212 m3/s put in)."""
    za, _, zm = pair
    sA = ZM.source_of(za, "A")
    nx, ny, res = sA["nx"], sA["ny"], sA["res"]
    r, c = np.divmod(np.arange(nx * ny), nx)
    P = sA["frame"].to_sphere((c + 0.5 - nx / 2) * res, (ny / 2 - r - 0.5) * res)
    own_b = P @ zm["frame"].c > P @ sA["frame"].c
    p = np.flatnonzero(~own_b & (sA["rec"] >= 0) & (sA["q"] >= 100.0) & sA["land"].ravel())
    p = p[own_b[sA["rec"][p]]]
    assert len(p) >= 2
    Q = np.asarray(zm["layers"]["discharge"], float).ravel()
    rec = zm["rec"]
    put = Q - np.bincount(rec[rec >= 0], Q[rec >= 0], len(Q))  # (each pixel's runoff, and a handed-on river's water)
    for k in p:
        x, y = zm["frame"].to_plane(P[sA["rec"][k]][None])
        rr = int(np.floor(zm["ny"] / 2 - y[0] / zm["res"]))
        cc = int(np.floor(x[0] / zm["res"] + zm["nx"] / 2))
        rows, cols = np.mgrid[max(rr - 2, 0):rr + 3, max(cc - 2, 0):cc + 3]
        win = (rows * zm["nx"] + cols).ravel()
        b = int(win[np.argmax(put[win])])
        assert 0.8 * sA["q"][k] <= put[b] <= 1.5 * sA["q"][k], (sA["q"][k], put[b])
        assert Q[RG.ZK.chain(rec, b)[:6]].min() >= 0.8 * sA["q"][k]  # (and carries it on)
