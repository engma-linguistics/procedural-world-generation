"""The rain kernel's vapour transport in physical time (PW-015)."""

import numpy as np

from planet import climate
from planet.grid import build_grid


def test_transport_keeps_the_vapour():
    """One transport step in any wind and mixing keeps the vapour's mass (per m2 x the cell's area)
    and never makes it negative."""
    g = build_grid(4)
    rng = np.random.default_rng(1)
    F = climate._faces(g)
    un = rng.normal(0, 8, (2, len(F["ea"])))
    kd = rng.uniform(0, 4e5, (2, len(F["ea"])))
    c_self, c_in, nbr, dt = climate._transport(g, un, kd)
    assert dt > 0 and c_self.min() >= -1e-12 and c_in.min() >= 0
    m = rng.uniform(0, 3, (2, g.n))
    for k in range(2):
        q = c_self[k] * m[k] + np.add.reduceat(c_in[:, k] * m[k][nbr], F["off"][:-1])
        assert q.min() >= 0
        assert abs((q * F["A"]).sum() / (m[k] * F["A"]).sum() - 1) < 1e-12


def test_faces_close_each_cell():
    """Each cell's faces, by length along their outward normals, add up to nothing (a closed polygon),
    and its faces' total length is its perimeter: about 6 x the edge length for a hexagon."""
    g = build_grid(5)
    F = climate._faces(g)
    G = climate._geom(g)
    cell = np.repeat(np.arange(g.n), np.diff(F["off"]))
    # the outward normals in each cell's own tangent plane
    nrm = F["n"][F["eid"]] * F["sg"][:, None]
    p = g.centers[cell]
    nrm = nrm - (nrm * p).sum(1, keepdims=True) * p
    s = np.zeros((g.n, 3))
    np.add.at(s, cell, nrm * F["L"][F["eid"]][:, None])
    perim = np.bincount(cell, F["L"][F["eid"]], g.n)
    assert (np.linalg.norm(s, axis=1) / perim).max() < 0.01
    hexes = np.diff(F["off"]) == 6
    side = perim[hexes] / 6 / (G["h"] * 1000.0)
    assert 0.5 < side.mean() < 0.65  # (a regular hexagon's side is its centre spacing / sqrt(3))


def test_no_rain_from_a_dry_column():
    """No vapour and no source (a sea that gives nothing): no rain, no vapour, anywhere."""
    g = build_grid(4)
    elev = np.full(g.n, -3000.0)
    t = 15 + 10 * np.cos(np.radians(g.lat))
    v = 0.6 * climate._geom(g)["east"]
    s_in = [climate._season_inputs(g, elev, t, t, v, 0.0, t, climate.TUNE) for _ in range(2)]
    for d in s_in:
        d["src_q"] = np.zeros(g.n)
    a = list(climate._rain_args(g, elev, s_in, climate.TUNE, np.full((2, g.n), 1000.0)))
    a[-3] = np.zeros((2, g.n))  # (m0: dry air)
    r, r_ls, up, q, m, _ = climate._rain(*a)
    assert not r.any() and not up.any() and not q.any() and not m.any()


def test_same_planet_rains_the_same_at_two_levels():
    """The kernel's rates are per second, not per cell (PW-290): the same continent's land rain at L5 and
    L6 agrees within a few percent (the per-cell kernel rained out in half the distance per level)."""
    out = {}
    for level in (5, 6):
        g = build_grid(level)
        lat, lon = g.lat, g.lon
        land = (np.abs(lat - 15) < 35) & (np.abs(lon) < 50)
        elev = np.where(land, 300.0 + 10 * (lat + 20), -4000.0)
        c = climate.compute(g, elev)
        inland = land & (np.abs(lon) < 35) & (np.abs(lat - 15) < 25)
        out[level] = (c["precip"][land].mean(), c["precip"][inland].mean())
    for a, b in zip(out[5], out[6]):
        assert abs(a / b - 1) < 0.05, out
