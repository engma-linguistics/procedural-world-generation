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


def test_caprock_holds_the_lip():
    """PW-146: a hard cap over soft rock holds a lip (Niagara), a thin one
    is helped by what's under it, and soft rock under the lip lets the
    gorge retreat faster."""
    SS, SH, DOL, GRAN, CRATON = 7, 8, 14, 11, 5
    niagara = (DOL, CRATON, 2.0, 0.6, SH)  # dolomite cap over shale, 2 km of cover
    assert zoom.lip_resistance(*niagara) == zoom.KP_RESIST[DOL]
    # a sandstone veneer over granite: the granite holds it; a thick one doesn't
    assert zoom.lip_resistance(SS, CRATON, 2.0, 0.1, GRAN) == zoom.KP_RESIST[GRAN]
    assert zoom.lip_resistance(SS, CRATON, 2.0, 0.8, GRAN) == zoom.KP_RESIST[SS]
    # undercut: shale under the cap retreats faster than granite under it
    assert zoom.lip_undercut(*niagara) > 1.1 > 0.7 > zoom.lip_undercut(SS, CRATON, 2.0, 0.6, GRAN)
    # without strata layers: the old rule (basement under a thin cover)
    assert zoom.lip_resistance(SS, CRATON, 0.2) == zoom.KP_RESIST[CRATON]


# ---------------------------------------------------------------------------
# Batch 2 (PW-011): fold belt, rift, shield; and the fixes PW-149 / PW-150
# ---------------------------------------------------------------------------
def _plain_world(base, gx, gy, precip=1200.0, thick_gy=0.01):
    """A continent at `base` m rising gx, gy m/km east and north, its crust
    thickening northward by thick_gy km/km (a collision to the north)."""
    from planet import hydrology
    from planet.grid import build_grid
    from planet.geo import latlon
    from test_zoom_water import _dist_km
    g = build_grid(5)
    lat, lon = latlon(g.centers)
    xk, yk = lon * 111.2, lat * 111.2
    d0 = _dist_km(g, 0.0, 0.0)
    elev = np.where(d0 < 2500, base + gx * xk + gy * yk, -3000.0)
    pr = np.full(g.n, precip)
    c = {"runoff": 0.5 * pr, "aet": 0.5 * pr, "lake_evap": np.full(g.n, 300.0)}
    flow, down, lk = hydrology.rivers_and_lakes(g, elev, c)
    land = elev > 0
    layers = {
        "elevation": np.round(elev), "precipitation": pr, "temperature": np.full(g.n, 18.0),
        "warm_month": np.full(g.n, 24.0), "flow": flow, "downstream": down, "lake": lk["wet"].astype(int),
        "rock": np.full(g.n, 4), "surface_rock": np.full(g.n, 8), "climate": np.full(g.n, 14),
        "ice": np.zeros(g.n), "sediment_cover": np.where(land, 2.0, 6.0),
        "crust_thickness": 35.0 + thick_gy * yk, "plate_boundary": np.zeros(g.n),
    }
    return {"grid": g, "layers": layers, "meta": {"level": 5}}, land


def _build(world, **kw):
    kw = {"size_km": 300, "res_km": 1.0, "iterations": 6, "log": lambda *a: None, **kw}
    return zoom.build(world, 0.0, 0.0, **kw)


def _grad(z):
    h = z["layers"]["elevation"].astype(float)
    land = z["layers"]["water"] == 0
    gy, gx = np.gradient(h, z["res"])
    inner = np.zeros_like(land)
    inner[30:-30, 30:-30] = True
    return np.abs(gx)[land & inner], np.abs(gy)[land & inner], h, land & inner


@pytest.fixture(scope="module")
def fold_pair():
    w, land = _plain_world(1200.0, 0.0, 0.2)
    n = len(land)
    cls = np.where(land, LF.FOLD_BELT, LF.SEA)
    lay = {"fold_wavelength": np.full(n, 12.0), "strata_dip": np.full(n, 30.0), "strata_top": np.full(n, 8),
           "strata_next": np.full(n, 7), "strata_top_km": np.full(n, 1.5)}
    young = _with_landforms(w, cls, {**lay, "landform_age": np.full(n, 2.0)})
    old = _with_landforms(w, cls, {**lay, "landform_age": np.full(n, 80.0)})
    return _build(w), _build(young), _build(old)


def test_fold_belt_ridges_follow_the_strike(fold_pair):
    """The crust thickens northward (the shortening is north-south): the
    folds run east-west, so the land's slopes face north and south far more
    than east and west, as parallel ridges about a fold wavelength apart."""
    plain, young, old = fold_pair
    assert young["stats"]["landforms"].get("fold_belt", 0) > 50
    for z in (young, old):
        gx, gy, h, on = _grad(z)
        px, py, *_ = _grad(plain)
        assert gy.mean() > 1.5 * gx.mean() and gy.mean() / gx.mean() > 1.5 * py.mean() / px.mean(), \
            (gy.mean(), gx.mean(), py.mean(), px.mean())
    # young folds: ridges ~ a fold wavelength (12 km) apart down each column
    _, _, h, on = _grad(young)
    hc = h[30:-30, 30:-30] - h[30:-30, 30:-30].mean(0)
    spec = np.abs(np.fft.rfft(hc, axis=0)) ** 2
    f = np.fft.rfftfreq(hc.shape[0], d=young["res"])
    band = spec.mean(1)
    k = (f > 1 / 40.0) & (f < 1 / 3.0)
    lam = 1 / f[k][np.argmax(band[k])]
    assert 7.0 < lam < 20.0, lam


def test_fold_belt_rivers_cut_water_gaps(fold_pair):
    """Rivers crossing the ridges keep their graded beds (water gaps), not a
    staircase of falls."""
    plain, young, old = fold_pair
    for z in (young, old):
        assert z["stats"]["falls_count"]["100m"] <= plain["stats"]["falls_count"]["100m"] + 2


@pytest.fixture(scope="module")
def rift_pair():
    w, land = _plain_world(900.0, 0.0, 0.0, precip=1200.0, thick_gy=0.0)
    from planet.geo import latlon
    lat, lon = latlon(w["grid"].centers)
    n = len(land)
    # a rift band 250 km wide, running north-south
    cls = np.where(land, np.where(np.abs(lon * 111.2) < 125, LF.RIFT, LF.HILLS), LF.SEA)
    lay = {"rift_strain": np.full(n, 0.6), "landform_age": np.full(n, 2.0)}
    return _build(w), _build(_with_landforms(w, cls, lay))


def test_rift_has_fault_blocks_along_its_axis(rift_pair):
    """Fault scarps run along the rift (north-south): steep east- or
    west-facing steps; between them flat basin floors (sediment) and, in a
    wet climate, lakes in the half-grabens."""
    plain, rift = rift_pair
    assert rift["stats"]["landforms"].get("rift", 0) > 30
    gx, gy, h, on = _grad(rift)
    px, py, *_ = _grad(plain)
    steep_x, steep_y = (gx > 150).sum(), (gy > 150).sum()
    assert steep_x > 3 * max(steep_y, 10) and steep_x > 3 * max((px > 150).sum(), 10), (steep_x, steep_y)
    # the half-grabens: flat floors or lakes
    def low(z):
        h = z["layers"]["elevation"].astype(float)
        gy_, gx_ = np.gradient(h, z["res"])
        return np.mean((np.hypot(gx_, gy_) < 3.0) | (z["layers"]["water"] == 2))
    assert low(rift) > low(plain) + 0.1, (low(rift), low(plain))
    assert rift["stats"]["landform_lakes"] >= 1


@pytest.fixture(scope="module")
def shield_pair():
    w, land = _plain_world(200.0, 0.0, 0.0, precip=900.0, thick_gy=0.0)
    n = len(land)
    cls = np.where(land, LF.SHIELD, LF.SEA)
    base = {"strata_top": np.full(n, 11), "strata_next": np.full(n, 11), "strata_top_km": np.zeros(n),
            "landform_age": np.full(n, 2500.0)}
    warm = _with_landforms(w, cls, {**base, "glaciated_myr": np.full(n, LF.GLACIATED_NEVER)})
    ice = _with_landforms(w, cls, {**base, "glaciated_myr": np.full(n, 2.0)})
    return _build(w), _build(warm, res_km=0.5, size_km=200), _build(ice, res_km=0.5, size_km=200)


def _prominent_peaks(z, prom):
    """Local maxima (7 x 7) standing `prom` m above the 21 x 21 box's 20th percentile."""
    from numpy.lib.stride_tricks import sliding_window_view as win
    h = z["layers"]["elevation"].astype(float)
    pad = np.pad(h, 10, mode="edge")
    lo = np.percentile(win(pad, (21, 21)), 20, axis=(2, 3))
    mx = win(np.pad(h, 3, mode="edge"), (7, 7)).max(axis=(2, 3))
    return int(((h == mx) & (h - lo > prom) & (z["layers"]["water"] == 0)).sum())


def test_shield_has_domes_and_scoured_lakes(shield_pair):
    """An old shield: inselbergs rise from a low plain; where it was under
    ice lately, the domes are ground down and rock basins hold lakes."""
    plain, warm, ice = shield_pair
    assert warm["stats"]["landforms"].get("shield", 0) > 50
    assert _prominent_peaks(warm, 80) >= 5 + _prominent_peaks(plain, 80) / 2, (
        _prominent_peaks(warm, 80), _prominent_peaks(plain, 80))
    assert _prominent_peaks(ice, 200) < _prominent_peaks(warm, 200)
    assert ice["stats"]["landform_lakes"] >= 5 and warm["stats"]["landform_lakes"] == 0
    wet = np.mean(ice["layers"]["water"] == 2)
    assert 0.03 < wet < 0.3, wet  # lake-dotted, not drowned


def test_build_frames_reads_the_strike():
    """A patch's strike runs across the crust's thickness gradient (and along
    a narrow class's band of cells), the same whichever zoom asks."""
    from planet.grid import build_grid
    from planet.geo import latlon, R_KM
    g = build_grid(5)
    lat, lon = latlon(g.centers)
    xk, yk = lon * 111.2, lat * 111.2
    sp = g.spacing * R_KM
    near = np.flatnonzero(np.hypot(xk, yk) < 2000)
    cells = g.centers[near]
    Pk = np.ascontiguousarray(g.centers[near[:50]] * R_KM)
    cues = {"thick": 35 + 0.01 * yk[near], "elev": np.zeros(len(near)), "converging": np.zeros(len(near))}
    F = ZL.build_frames(Pk, 5, cells, np.ones(len(near)), {}, cues, sp, "gradient")
    ang = np.mod(F.patch["axis_deg"], 180)
    assert np.all(np.minimum(ang, 180 - ang) < 15), ang  # east-west
    # a band of cells running north-south: a rift along it
    band = (np.abs(xk[near]) < 150).astype(float)
    cues["thick"] = np.zeros(len(near))
    F = ZL.build_frames(Pk, 5, cells, band, {}, cues, sp, "band")
    ang = np.mod(F.patch["axis_deg"], 180)
    on = np.abs(np.degrees(np.arctan2(F.patch["centre"][:, 1], F.patch["centre"][:, 0])) * 111.2) < 300
    assert on.sum() >= 2 and np.all(np.abs(ang[on] - 90) < 20), ang[on]


def test_cut_widens_a_breach_into_a_gap():
    """A ridge across a river is cut through as a gap a few pixels wide,
    not a one-pixel slot (PW-149)."""
    nx = ny = 41
    res = 0.5
    r, c = np.mgrid[0:ny, 0:nx]
    h = (100.0 + 2.0 * (nx - c)).astype(float)  # sloping east
    h = np.where(np.abs(c - 20) <= 1, h + 300.0, h).ravel()  # a ridge across it
    rec = np.where(c.ravel() < nx - 1, np.arange(nx * ny) + 1, -1)  # every row flows east
    order = ZK_order(rec)
    keep = np.zeros(nx * ny, bool)
    z = ZL.cut(h.copy(), rec, order, keep, nx, ny, res).reshape(ny, nx)
    row = z[20]
    assert np.all(np.diff(row) <= 0)  # the river crosses
    # the walls of the gap: the rows beside the river (all rivers here) are cut too,
    # and next to a lone cut pixel the land is lowered over more than one pixel
    hh = h.reshape(ny, nx).copy()
    rec2 = np.full(nx * ny, -1)
    rec2[20 * nx:21 * nx - 1] = np.arange(20 * nx + 1, 21 * nx)
    z2 = ZL.cut(hh.ravel().copy(), rec2, ZK_order(rec2), keep, nx, ny, res).reshape(ny, nx)
    lowered = (hh - z2)[:, 20] > 5
    assert lowered.sum() >= 3, lowered.sum()


def ZK_order(rec):
    from planet import zoom_kernels as ZK
    return ZK.receiver_order(rec)


def test_landform_falls_are_listed_with_pools(esc_pair):
    """PW-150: every fall >= 30 m is listed (stats.falls, falls_count), the
    top 5 summary stays; falls over the escarpment are kind 'scarp' with a
    plunge pool at the foot."""
    _, esc = esc_pair
    st = esc["stats"]
    assert len(st["waterfalls"]) <= 5 and st["falls_count"]["30m"] == len(st["falls"])
    assert st["falls_count"]["30m"] >= len(st["waterfalls"])
    assert all(f["height_m"] >= 30 for f in st["falls"])
    kinds = {f["kind"] for f in st["falls"]}
    assert "scarp" in kinds, kinds
    scarp = [f for f in st["waterfalls"] if f["kind"] == "scarp"]
    assert all("plunge_pool_m" in f for f in scarp)
