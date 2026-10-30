"""Zoom passes whose result shouldn't depend on the pixel size (PW-125): creep
is a diffusivity, and the landscape pass's summit taper is integrated along
each link, so a hill of a given size in km comes out alike on 2 and 4 km
pixels. Nor on where the region ends (PW-321): no rough rim at its edge."""

import numpy as np

from planet.zoom import regional as zoom
from planet.zoom import kernels as ZK


def _hill(res, n_km=400.0, sigma_km=40.0, top=1000.0):
    n = int(n_km / res)
    x = (np.arange(n) + 0.5 - n / 2) * res
    X, Y = np.meshgrid(x, x)
    return (top * np.exp(-(X**2 + Y**2) / (2 * sigma_km**2))).ravel(), n


def test_creep_share_falls_with_the_pixel_area():
    assert zoom.creep_kd(zoom.KD_RES_KM) == 1.0
    assert zoom.creep_kd(1.0) == zoom.creep_kd(0.5) == 1.0  # finer pixels keep the 2 km share
    for res in (2.5, 3.0, 4.0, 8.0):
        assert abs(zoom.creep_kd(res) - (zoom.KD_RES_KM / res) ** 2) < 1e-12


def test_creep_rounds_a_hill_alike_at_2_and_4_km():
    """The same hill (in km) loses the same height to a creep step on 2 km
    and 4 km pixels; at a fixed share per pixel the 4 km one lost ~4x as much."""
    lost = {}
    for res in (2.0, 4.0):
        h, n = _hill(res)
        active = np.ones(n * n, bool)
        mid = (n // 2) * n + n // 2
        for name, kd in (("scaled", zoom.KD * zoom.creep_kd(res)), ("fixed", zoom.KD)):
            out = ZK.diffuse(h, np.full(n * n, kd), active, n, n)
            lost[name, res] = h[mid] - out[mid]
    assert abs(lost["scaled", 4.0] / lost["scaled", 2.0] - 1) < 0.05
    assert lost["fixed", 4.0] / lost["fixed", 2.0] > 3.5


def _profile(res, s=200.0, soft=300.0, scale=400.0, length_km=48.0):
    """A stream climbing from 0 m at s m/km on res km links, tapering above
    soft: its height at each km of length_km."""
    n = int(round(length_km / res)) + 1
    h = np.zeros(n)
    rec = np.arange(n) - 1  # pixel i drains to i - 1; pixel 0 is the outlet
    fixed = np.zeros(n, bool)
    fixed[0] = True
    full = lambda v: np.full(n, float(v))
    ZK.integrate(h, rec, np.arange(n), full(s), full(res), fixed, full(-np.inf), full(soft), full(scale), full(1e9))
    return np.interp(np.arange(0, length_km + 1), np.arange(n) * res, h)


def test_summit_taper_does_not_depend_on_the_pixel_size():
    """A steep stream crossing the taper's level climbs the same profile on
    1, 2 and 4 km links (taken at each link's base, a 4 km link climbed
    800 m at the full slope and the links above it hardly rose: a one-link
    step)."""
    p1, p2, p4 = _profile(1.0), _profile(2.0), _profile(4.0)
    for p in (p2, p4):
        nodes = np.arange(0, 49, 4)  # (the 4 km nodes: between them interp is linear)
        assert np.max(np.abs(p[nodes] - p1[nodes])) < 1.0
    # ... the continuous profile: full slope up to `soft`, then u^3 = 1 + 3 s x' / scale
    x = 40.0 - 300.0 / 200.0
    assert abs(p4[40] - (300.0 + 400.0 * ((1 + 3 * 200.0 * x / 400.0) ** (1 / 3) - 1))) < 1.0


def _relief3(h):
    from numpy.lib.stride_tricks import sliding_window_view
    v = sliding_window_view(np.pad(h, 1, mode="edge"), (3, 3))
    return v.max((-1, -2)) - v.min((-1, -2))


def test_no_rough_rim_at_the_zoom_edge():
    """PW-321: the landscape goes on past the region's edge (a halo built and
    cropped off), so the relief next to the edge is like the relief a little
    further in. Held at the target surface, the edge pixels stepped into the
    graded land: 3x3 relief ~1.5-2x within 3 px of the edge."""
    from test_zoom_landforms import _plain_world
    w, _ = _plain_world(1500.0, 0.3, 0.0)
    z = zoom.build(w, 0.0, 0.0, size_km=300, res_km=1.0, iterations=6, log=lambda *a: None)
    h = z["layers"]["elevation"].astype(float)
    n = h.shape[0]
    r, c = np.mgrid[0:n, 0:n]
    d = np.minimum(np.minimum(r, n - 1 - r), np.minimum(c, n - 1 - c))
    rl = _relief3(h)
    rim, ring = rl[d < 3].mean(), rl[(d >= 8) & (d < 40)].mean()
    assert rim < 1.25 * ring, (rim, ring)


def _pk(lat, lon, n, res):
    fr = zoom.Frame(lat, lon)
    x = (np.arange(n) + 0.5 - n / 2) * res
    X, Y = np.meshgrid(x, -x)
    return np.ascontiguousarray(fr.to_sphere(X.ravel(), Y.ravel()) * zoom.R_KM), X.ravel(), Y.ravel()


def test_drainage_tie_breaks_are_planet_fixed():
    """PW-339: the flood's tie-break jitter is a function of the place on the
    planet, so zooms of another size or with another halo share it where
    they overlap (one random number per pixel index did not)."""
    Pa, xa, ya = _pk(10.0, 20.0, 200, 1.0)
    Pb, xb, yb = _pk(10.0, 20.0, 300, 1.0)  # (same centre, even sizes: the pixel centres coincide)
    ja, jb = zoom.tie_jitter(Pa, 1.0, 77), zoom.tie_jitter(Pb, 1.0, 77)
    ka = {(round(a, 3), round(b, 3)): v for a, b, v in zip(xa, ya, ja)}
    shared = [(ka[(round(a, 3), round(b, 3))], v) for a, b, v in zip(xb, yb, jb) if (round(a, 3), round(b, 3)) in ka]
    assert len(shared) == 200 * 200
    u, v = np.array(shared).T
    assert np.max(np.abs(u - v)) < 1e-9
    assert 0 <= ja.min() and ja.max() <= 1 and np.std(ja) > 0.15  # (a spread, varying from pixel to pixel)
    assert abs(np.corrcoef(ja.reshape(200, 200)[:, :-2].ravel(), ja.reshape(200, 200)[:, 2:].ravel())[0, 1]) < 0.5


def test_overlapping_zooms_drain_alike_on_flats():
    """PW-339: two zooms of one flat plain (200 and 300 km) give the same
    receivers in their shared middle more often with the planet-fixed
    tie-break than with one random number per pixel index (0.42 vs 0.31)."""
    from test_zoom_landforms import _plain_world
    w, _ = _plain_world(300.0, 0.0, 0.0)

    def agree():
        offs = []
        for s in (200, 300):
            z = zoom.build(w, 0.0, 0.0, size_km=s, res_km=1.0, iterations=6, log=lambda *a: None)
            n, r = z["nx"], z["rec"]
            i = np.arange(n * n)
            rr, cc = np.divmod(np.where(r >= 0, r, i), n)
            d = ((rr - i // n) * 3 + (cc - i % n)).reshape(n, n)
            offs.append(d[n // 2 - 60:n // 2 + 60, n // 2 - 60:n // 2 + 60])
        return float(np.mean(offs[0] == offs[1]))

    fixed = agree()
    old = zoom.tie_jitter
    try:
        zoom.tie_jitter = lambda Pk, res, seed: np.random.default_rng(seed).random(len(Pk))
        by_index = agree()
    finally:
        zoom.tie_jitter = old
    assert fixed > by_index + 0.05, (fixed, by_index)
