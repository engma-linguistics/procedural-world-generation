"""Landform classes (landform.py): each rule on a made-up record, the class
layer of a simulated planet, and the layers' way into runs and worlds."""

import numpy as np
import pytest

from planet import landform as LF
from planet.grid import build_grid
from planet.surface import (ARC, CRATON, FLOOD_BASALT, HOTSPOT, LIMESTONE, OROGEN, SANDSTONE, SHALE)
from planet.tectonics import record as R
from planet.tectonics.volcanism import ARC as V_ARC, COLUMNS, VENT

T = 1000.0


@pytest.fixture(scope="module")
def g():
    return build_grid(5)


def planet(g, **kw):
    """A continent-covered planet of plain old hills, unless told otherwise."""
    n = g.n
    p = dict(elev=np.full(n, 500.0), cont=np.ones(n, bool), rock=np.full(n, OROGEN, np.uint8),
             cover=np.zeros(n), mix=np.zeros((n, 6)), precip=np.full(n, 600.0), temp=np.full(n, 12.0),
             crust_age=np.full(n, 200.0), volcanoes=[])
    p["rec"], p["lith"] = R.empty((n,))
    p.update(kw)
    return p


def strata(p, layers):
    """Give every cell the strata [(rock, km, last grew)], top first."""
    for j, (rock, km, t) in enumerate(layers):
        p["rec"][:, j] = km
        p["rec"][:, R.K + j] = t
        p["lith"][:, j] = rock
    p["cover"] = np.full(len(p["cover"]), sum(km for _, km, _ in layers))
    return p


def classify(g, p):
    return LF.classify(g, T, p["elev"], p["cont"], p["rock"], p["cover"], p["mix"], p["rec"], p["lith"],
                       p["crust_age"], p["precip"], p["temp"], p["volcanoes"])


def only(out, k):
    return np.all(out["landform"] == k)


def test_plain_land_is_hills_and_sea_is_sea(g):
    p = planet(g)
    p["elev"][: g.n // 2] = -3000
    out = classify(g, p)
    assert np.all(out["landform"][: g.n // 2] == LF.SEA)
    assert np.all(out["landform"][g.n // 2:] == LF.HILLS)


def test_shield_old_granite_basement_exposed(g):
    out = classify(g, planet(g, rock=np.full(g.n, CRATON, np.uint8), crust_age=np.full(g.n, 2500.0)))
    assert only(out, LF.SHIELD) and np.all(out["landform_age"] == 2500)
    # under a sediment blanket it's no longer exposed
    p = strata(planet(g, rock=np.full(g.n, CRATON, np.uint8), crust_age=np.full(g.n, 2500.0)), [(SHALE, 1.0, 0.0)])
    assert not np.any(classify(g, p)["landform"] == LF.SHIELD)


def test_lava_plateau_from_flood_basalt(g):
    out = classify(g, strata(planet(g), [(FLOOD_BASALT, 1.2, 940.0), (SHALE, 2.0, 500.0)]))
    assert only(out, LF.LAVA_PLATEAU) and np.all(out["landform_age"] == 60)
    assert np.all(out["strata_top"] == FLOOD_BASALT) and np.allclose(out["strata_top_km"], 1.2)


def test_caprock_hard_over_soft_flat_and_exposed(g):
    out = classify(g, strata(planet(g), [(LIMESTONE, 0.2, 700.0), (SHALE, 1.0, 650.0)]))
    assert only(out, LF.CAPROCK)
    assert np.all(out["strata_next"] == SHALE) and np.all(out["fold_wavelength"] == 0)
    # still being laid down: not exhumed yet
    assert not np.any(classify(g, strata(planet(g), [(LIMESTONE, 0.2, T), (SHALE, 1.0, 650.0)]))["landform"]
                      == LF.CAPROCK)
    # soft over soft: no cap
    assert not np.any(classify(g, strata(planet(g), [(SHALE, 0.2, 700.0), (SHALE, 1.0, 650.0)]))["landform"]
                      == LF.CAPROCK)


def test_karst_thick_carbonate_in_a_wet_climate(g):
    p = strata(planet(g, precip=np.full(g.n, 1500.0)), [(LIMESTONE, 0.8, 600.0), (SHALE, 1.0, 500.0)])
    assert only(classify(g, p), LF.KARST)
    p["precip"][:] = 300.0  # dry: a carbonate caprock instead (it's thin enough)
    p["rec"][:, 0] = 0.5
    assert only(classify(g, p), LF.CAPROCK)


def test_dunes_sand_in_a_hyperarid_lowland(g):
    p = strata(planet(g, precip=np.full(g.n, 40.0)), [(SANDSTONE, 0.5, 990.0), (SHALE, 1.0, 500.0)])
    assert only(classify(g, p), LF.DUNES)


def test_dunes_need_aridity_not_just_little_rain(g):
    """The erg rule is the aridity index P / PET (PW-176): a hot desert with
    150 mm/yr is hyper-arid, a cold one with 80 mm/yr and little
    evaporation is not."""
    sand = [(SANDSTONE, 0.5, 990.0), (SHALE, 1.0, 500.0)]
    lat = np.asarray(g.lat)

    def dunes(precip, temp, warm, cold):
        p = strata(planet(g, precip=np.full(g.n, precip), temp=np.full(g.n, temp)), sand)
        return LF.classify(g, T, p["elev"], p["cont"], p["rock"], p["cover"], p["mix"], p["rec"], p["lith"],
                           p["crust_age"], p["precip"], p["temp"], p["volcanoes"], t_warm=np.full(g.n, warm),
                           t_cold=np.full(g.n, cold))["landform"] == LF.DUNES
    assert np.all(dunes(150.0, 24.0, 32.0, 16.0)[np.abs(lat) < 25])
    assert not np.any(dunes(80.0, -6.0, 6.0, -18.0)[(np.abs(lat) > 50) & (np.abs(lat) < 65)])
    # ... but a polar desert dry enough still is one
    assert np.all(dunes(20.0, -6.0, 6.0, -18.0)[(np.abs(lat) > 50) & (np.abs(lat) < 65)])
    ai = LF.aridity(g, np.full(g.n, 100.0), np.full(g.n, -6.0), np.full(g.n, 6.0), np.full(g.n, -18.0))
    ai_mean = LF.aridity(g, np.full(g.n, 100.0), np.full(g.n, -6.0))
    band = (np.abs(lat) > 50) & (np.abs(lat) < 65)
    assert np.all(ai[band] < ai_mean[band])  # (a summer above freezing evaporates: the seasons count)


def test_fold_belt_strata_older_than_the_folding(g):
    p = strata(planet(g), [(SANDSTONE, 0.5, 600.0), (SHALE, 3.0, 500.0)])
    p["rec"][:, R.T_FOLD] = 800.0
    p["rec"][:, R.FOLD_KM] = 6.0
    p["rec"][:, R.FOLD_STRAIN] = 30.0
    out = classify(g, p)
    assert only(out, LF.FOLD_BELT) and np.all(out["landform_age"] == 200)
    assert np.allclose(out["fold_wavelength"], LF.fold_wavelength(6.0))
    assert np.all(out["strata_dip"] > 30)
    # strata laid down after the folding lie flat on it: no fold belt at the surface
    p2 = strata(planet(g), [(SHALE, 0.5, 900.0), (SANDSTONE, 0.5, 600.0), (SHALE, 3.0, 500.0)])
    p2["rec"][:, R.T_FOLD] = 800.0
    assert not np.any(classify(g, p2)["landform"] == LF.FOLD_BELT)


def test_young_rift_then_escarpment_retreating_from_the_coast(g):
    sea = g.centers[:, 0] < -0.3
    p = planet(g, elev=np.where(sea, -3000.0, 800.0), cont=~sea)
    p["rec"][:, R.T_RIFT] = T - 10
    assert not np.any(classify(g, p)["landform"] == LF.RIFT)  # barely stretched
    p["rec"][:, R.RIFT_STRAIN] = 0.3
    assert np.all(classify(g, p)["landform"][~sea] == LF.RIFT)
    p["rec"][:, R.T_RIFT] = T - 130
    out = classify(g, p)
    esc = out["landform"] == LF.ESCARPMENT
    assert esc.any() and np.all(out["landform_age"][esc] == 130)
    # it sits about retreat_km(130) inland of the rifted coast
    land = ~sea
    coast = land & (np.add.reduceat(sea[g.nbr_idx], g.nbr_off[:-1]) > 0)
    d = LF.coast_km(g, land, coast)
    assert np.all(np.abs(d[esc] - LF.retreat_km(130)) <= 0.75 * g.spacing * 6371)
    assert not esc[d > LF.retreat_km(130) + g.spacing * 6371].any()
    # an unrifted coast has none
    p["rec"][:, R.T_RIFT] = R.NEVER
    assert not np.any(classify(g, p)["landform"] == LF.ESCARPMENT)


def test_coastal_plain_young_low_sediment_near_the_coast(g):
    sea = g.centers[:, 0] < -0.3
    p = strata(planet(g, elev=np.where(sea, -3000.0, 100.0), cont=~sea), [(SHALE, 0.3, T - 4), (SANDSTONE, 2.0, 500.0)])
    out = classify(g, p)
    cp = out["landform"] == LF.COASTAL_PLAIN
    assert cp.any()
    land = ~sea
    d = LF.coast_km(g, land, land & (np.add.reduceat(sea[g.nbr_idx], g.nbr_off[:-1]) > 0))
    assert np.all(d[cp] <= LF.COASTAL_KM) and np.all(cp[land & (d <= LF.COASTAL_KM)])


def test_arcs_and_hotspots_from_the_volcano_table(g):
    from planet.geo import latlon
    p = planet(g)
    lat, lon = latlon(g.centers[100])
    row = dict(zip(COLUMNS, [0] * len(COLUMNS)))
    row.update(lat=float(lat), lon=float(lon), kind=V_ARC, age=3.0, active=1, top_m=2500)
    p["volcanoes"] = [[row[c] for c in COLUMNS]]
    out = classify(g, p)
    arc = np.flatnonzero(out["landform"] == LF.ARC_CLASS)
    assert 100 in arc and set(arc) <= {100, *g.neighbors[100]}
    assert out["landform_age"][100] == 3
    row.update(kind=VENT, top_m=1200)
    p["volcanoes"] = [[row[c] for c in COLUMNS]]
    assert classify(g, p)["landform"][100] == LF.HILLS  # on a continent: its lava makes the landform
    p["cont"][:] = False
    assert classify(g, p)["landform"][100] == LF.HOTSPOT_CLASS
    row.update(top_m=-900)  # a seamount isn't an island
    p["volcanoes"] = [[row[c] for c in COLUMNS]]
    assert classify(g, p)["landform"][100] == LF.HILLS
    # an ocean-island basalt pile standing above the sea
    q = planet(g, cont=np.zeros(g.n, bool), rock=np.full(g.n, HOTSPOT, np.uint8), crust_age=np.full(g.n, 50.0))
    assert only(classify(g, q), LF.HOTSPOT_CLASS)
    q["crust_age"][:] = 400.0  # an old, worn pile: just hills
    assert only(classify(g, q), LF.HILLS)


def test_priority_arc_beats_everything(g):
    from planet.geo import latlon
    p = strata(planet(g, rock=np.full(g.n, ARC, np.uint8)), [(FLOOD_BASALT, 1.0, 990.0)])
    lat, lon = latlon(g.centers[7])
    row = [float(lat), float(lon), V_ARC, 1.0, 1, 2000] + [0] * (len(COLUMNS) - 6)
    p["volcanoes"] = [row]
    out = classify(g, p)
    assert out["landform"][7] == LF.ARC_CLASS
    assert np.sum(out["landform"] == LF.LAVA_PLATEAU) > 0.9 * g.n


def test_simulated_planet_has_classes_from_its_history(sim4):
    """A 300 Myr level-4 run: several classes, all from the record."""
    s = sim4.snapshot()
    land = s.elevation > 0
    got = set(np.unique(s.landform[land]).tolist())
    assert LF.SEA not in got
    assert len(got) >= 4, got
    assert np.all(s.landform[~(sim4.w_elev > 0)] == LF.SEA)
    for k in LF.LAYERS:
        assert getattr(s, k).shape == (sim4.grid.n,)


def test_landforms_in_runs_and_worlds(data_root):
    """Keyframes store the class layers; worlds built from a keyframe or a
    replay carry them, with the legend."""
    from planet import store as S
    from planet import timeline as TL
    from planet.tectonics import Params
    out = TL.simulate(1, 4, 8.0, 2.0, 4.0, "lf", Params(), checkpoint_every=0)
    run, arr = TL.load_frames(out, LF.LAYERS)
    assert [f["id"] for f in run["legend"]["landforms"]] == list(range(len(LF.CLASSES)))
    w = TL.world_from_frame(out, 8.0)
    sim = TL.replay(out, 8.0, use_checkpoints=False)
    w2 = TL.world_from_sim(sim)
    for k in LF.LAYERS:
        assert k in w["layers"] and k in w2["layers"], k
    assert np.array_equal(np.asarray(w["layers"]["landform"]), TL.frame(run, arr, "landform", 2))
    assert np.array_equal(np.asarray(w2["layers"]["landform"]), sim.snapshot().landform)
    import json
    from planet import world as W
    saved = json.loads(W.save(w2, "lf world").read_text())
    assert "landform_pct" in saved["summary"] and saved["legend"]["landforms"][5]["key"] == "escarpment"


def test_smoothing_removes_speckle_but_keeps_narrow_classes(g):
    cls = np.full(g.n, LF.CAPROCK, np.uint8)
    cls[5] = LF.HILLS  # a lone speck
    cls[200] = LF.ESCARPMENT  # a narrow class: kept
    cls[300] = LF.SEA
    out = LF.smooth(g, cls)
    assert out[5] == LF.CAPROCK and out[200] == LF.ESCARPMENT and out[300] == LF.SEA
    cls2 = np.full(g.n, LF.HILLS, np.uint8)
    cls2[g.neighbors[7]] = LF.SHIELD
    cls2[7] = LF.SHIELD
    assert np.all(LF.smooth(g, cls2)[g.neighbors[7] + [7]] == LF.SHIELD)  # a patch survives
