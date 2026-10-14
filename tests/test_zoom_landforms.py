"""Landform synthesis in the zoom (zoom_landforms): the bench map, cuestas
from dipping caprock, and a synthetic great escarpment that steps up to a
plateau with falls where its rivers cross it."""

import numpy as np
import pytest

from planet import landform as LF
from planet import zoom
from planet import zoom_landforms as ZL

from test_zoom_water import _escarpment_world


def test_bench_map_is_monotone_with_cliffs():
    s = np.linspace(0.0, 1000.0, 100001)
    z = ZL.bench_map(s, 800.0, 100.0, cliff=0.5, power=2.0, top_k=0.3)
    assert np.all(np.diff(z) >= -1e-9)  # monotone: the drainage survives
    # above the anchor: the top bed, relief scaled by top_k
    hi = s > 800
    assert np.allclose(np.diff(z[hi]), 0.3 * np.diff(s[hi]))
    # each band: a cliff of ~cliff x period over its top `face`
    k = (s > 690) & (s < 700)
    assert z[k][-1] - z[k][0] > 0.45 * 100
    # endless benches keep the land's level on average
    mid = (s > 100) & (s < 700)
    assert abs(np.mean(z[mid] - s[mid])) < 5
    # one band (an escarpment): below it the land is left alone, and the band
    # steps up to the anchor
    z1 = ZL.bench_map(s, 600.0, 300.0, bands=1, cliff=0.75, face=0.015)
    assert np.allclose(z1[s < 300], s[s < 300]) and np.allclose(z1[s > 600], s[s > 600])
    assert np.all(np.diff(z1) >= -1e-9)
    step = (s > 590) & (s < 600)
    assert z1[step][-1] - z1[step][0] > 0.6 * 300


def test_dipping_caprock_makes_cuestas():
    """Caprock dipping east over a plain sloping east more gently than the
    beds: asymmetric cuestas, their scarps facing west (up-dip), their dip
    slopes long and gentle."""
    x = np.linspace(0.0, 200.0, 2001)  # km east
    h = 600.0 - 1.0 * x  # the land: 1 m/km down to the east
    t = 4.0  # m/km: the beds dip east, more steeply than the land
    sv = h + t * x
    z = ZL.bench_map(sv, sv.max(), 80.0, cliff=0.45, power=2.0) - t * x
    g = np.diff(z) / np.diff(x)
    up = g > 20  # scarp faces: the land rising eastward (facing west)
    down = g < -20
    assert up.sum() > 10 and down.sum() == 0
    assert np.mean(g[~up] < 0) > 0.9  # the rest: dip slopes falling east


def _with_landforms(world, cls, layers=None):
    """A copy of the world with landform layers: class `cls` (per cell) and
    neutral strata."""
    L = dict(world["layers"])
    n = len(L["elevation"])
    L["landform"] = cls.astype(np.uint8)
    L["landform_age"] = np.where(cls > 1, 100.0, 0.0)
    L["strata_top"] = np.full(n, 7)
    L["strata_top_km"] = np.full(n, 0.2)
    L["strata_next"] = np.full(n, 8)
    L["strata_dip"] = np.zeros(n)
    L["fold_wavelength"] = np.zeros(n)
    L.update(layers or {})
    return {**world, "layers": L}


@pytest.fixture(scope="module")
def esc_pair():
    """The falls world (a continent sloping east to a 600 m scarp at
    longitude 0), with and without an escarpment class along the scarp."""
    w = _escarpment_world(0.3, 600)
    g = w["grid"]
    from planet.geo import latlon
    lat, lon = latlon(g.centers)
    land = w["layers"]["elevation"] > 0
    cls = np.where(land, np.where(np.abs(lon * 111.2) < 120, LF.ESCARPMENT, LF.HILLS), LF.SEA)
    kw = dict(size_km=800, res_km=2, iterations=6, log=lambda *a: None)
    return zoom.build(w, 0.5, 0.0, **kw), zoom.build(_with_landforms(w, cls), 0.5, 0.0, **kw)


def _falls(z):
    Lr = z["layers"]
    ws = np.where(Lr["water"] == 1, 0.0, Lr["elevation"] + Lr["lake_depth"]).ravel().astype(float)
    return zoom.waterfalls(ws, Lr["discharge"].ravel().astype(float), z["rec"], z["nx"], z["ny"], z["res"], top=200)


def test_escarpment_steps_up_to_a_plateau(esc_pair):
    plain, esc = esc_pair
    assert esc["stats"]["landforms"].get("escarpment", 0) > 5
    assert not plain["stats"]["landforms"]

    def cliffs(z):
        h = z["layers"]["elevation"].astype(float)
        land = z["layers"]["water"] == 0
        d = np.abs(np.diff(h, axis=1))
        return d[land[:, 1:] & land[:, :-1]]
    # many steep pixel steps (a cliff line), where the plain zoom has a ramp
    assert (cliffs(esc) > 120).sum() > 3 * max((cliffs(plain) > 120).sum(), 10)


def test_escarpment_rivers_fall_over_it(esc_pair):
    plain, esc = esc_pair
    f0, f1 = _falls(plain), _falls(esc)
    big = [f for f in f1 if f["height_m"] >= 100]
    assert len(big) >= 3 and len(big) > len([f for f in f0 if f["height_m"] >= 100])


def test_escarpment_keeps_cell_means(esc_pair):
    plain, esc = esc_pair
    for k, tol in (("cell_mean_rms_error_m", 20.0), ("cell_mean_bias_m", 10.0)):
        # (no worse than without the class: the synthetic world's coarse cells are big and its scarp steep)
        assert abs(esc["stats"][k]) < abs(plain["stats"][k]) + tol, (k, plain["stats"][k], esc["stats"][k])


def test_landform_zoom_is_deterministic(esc_pair):
    _, esc = esc_pair
    w = _escarpment_world(0.3, 600)
    from planet.geo import latlon
    lat, lon = latlon(w["grid"].centers)
    land = w["layers"]["elevation"] > 0
    cls = np.where(land, np.where(np.abs(lon * 111.2) < 120, LF.ESCARPMENT, LF.HILLS), LF.SEA)
    again = zoom.build(_with_landforms(w, cls), 0.5, 0.0, size_km=800, res_km=2, iterations=6, log=lambda *a: None)
    assert np.array_equal(again["layers"]["elevation"], esc["layers"]["elevation"])


def test_designed_falls_take_the_scarp(esc_pair):
    """The big rivers' designed falls (knickpoints) sit at the scarp, with
    the plateau above them: taller than without the class (falls2: they were
    scaled down to fit under the coarse ground)."""
    plain, esc = esc_pair
    def lips(z, scarp_only):
        return [st["height_m"] for kp in z["kps"] if kp.get("scarp") or not scarp_only
                for st in kp["steps"][:1] if st.get("height_m")]
    assert lips(esc, True) and max(lips(esc, True)) >= 250
    assert max(lips(esc, True)) > max(lips(plain, False)) + 100
