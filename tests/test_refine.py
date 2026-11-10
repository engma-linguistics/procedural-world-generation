"""A finished world refined onto a finer grid (planet/refine.py, `planet refine`; PW-490 first cut)."""

import numpy as np
import pytest

from planet import finish as F, refine as RF, store as S, timeline as T, timezoom as TZ, world as W
from planet.geo import is_land
from planet.grid import build_grid
from planet.tectonics import Params


@pytest.fixture(scope="module")
def made(tmp_path_factory):
    """A tiny L4 run, its keyframe world at 40 Myr, a finished world of a short time zoom, and the first refined
    to L5 through the store (as `planet refine` does)."""
    tmp = tmp_path_factory.mktemp("refine")
    S.set_root(tmp)
    run = T.simulate(seed=1, level=4, myr=40.0, dt=2.0, every=20.0, name="tiny", params=Params())
    src = W.save(T.world_from_frame(run, 40.0), "tiny @ 40 Myr")
    out = RF.refine_world(src.stem, 5, log=lambda *a: None)
    yield {"root": tmp, "run": run, "src": src, "out": out}
    S.set_root(None)


def test_refined_world_is_a_normal_world_on_the_finer_grid(made):
    a, b = W.load(made["src"]), W.load(made["out"])
    g5 = build_grid(5)
    assert b["meta"]["level"] == 5 and b["grid"].n == g5.n
    assert b["meta"]["refined_from"]["world"] == made["src"].stem
    assert b["meta"]["source_run"] == a["meta"]["source_run"] and b["meta"]["t_myr"] == a["meta"]["t_myr"]
    missing = set(a["layers"]) - set(b["layers"])
    assert not missing, missing
    for k, v in b["layers"].items():
        assert len(v) == g5.n, k
    # listed in the store like any world
    assert S.exists("world", made["out"].stem)


def test_coarse_cells_keep_their_land_and_means(made):
    a, b = W.load(made["src"]), W.load(made["out"])
    g4 = a["grid"]
    e4 = np.asarray(a["layers"]["elevation"], float)
    land4 = is_land(e4, np.asarray(a["layers"]["ice"], float), g4)
    st = b["meta"]["refined_from"]["terrain"]
    # every coarse cell is a fine cell (the grids nest) and keeps its land or sea before the finish
    assert abs(st["land_share"] - st["coarse_land_share"]) < 0.03
    # each inland coarse cell's height is its fine land's mean (the zoom's mean correction), within the noise's
    # last fill of hollows
    assert abs(st["inland_cell_mean_bias_m"]) < 25 and st["inland_cell_mean_rms_error_m"] < 80
    e5 = np.asarray(b["layers"]["elevation"], float)
    land5 = is_land(e5, np.asarray(b["layers"]["ice"], float), b["grid"])
    a4, a5 = g4.cell_area_km2, b["grid"].cell_area_km2
    assert abs((a5 * land5).sum() / a5.sum() - (a4 * land4).sum() / a4.sum()) < 0.04
    # the geology comes from the coarse cells (rock ids, plates)
    assert set(np.unique(b["layers"]["plate"])) <= set(np.unique(a["layers"]["plate"]))


def test_refined_climate_follows_the_coarse_one(made):
    a, b = W.load(made["src"]), W.load(made["out"])
    ga, gb = a["grid"], b["grid"]
    wa, wb = ga.cell_area_km2, gb.cell_area_km2
    for k, tol in (("temperature", 1.5), ("precipitation", 150.0)):
        ma = (wa * a["layers"][k]).sum() / wa.sum()
        mb = (wb * b["layers"][k]).sum() / wb.sum()
        assert abs(ma - mb) < tol, (k, ma, mb)
    # rivers and lakes are the fine grid's own: receivers are fine cells
    down = np.asarray(b["layers"]["downstream"])
    assert down.max() < gb.n and (down >= 0).any()


def test_nest_sums_and_kernel():
    g, G = build_grid(3), build_grid(5)
    n = RF.Nest(g, G)
    assert np.array_equal(n.own[:g.n], np.arange(g.n))
    m, share = n.mean(np.full(G.n, 3.0))
    assert np.allclose(m, 3.0) and np.allclose(share, 1.0)
    # the fine area's full-weighting sums are the coarse cells' areas
    assert np.allclose(n.total(n.area).sum(), g.cell_area_km2.sum())
    v = n.interp(np.full(g.n, 5.0), None, 0.5 * g.spacing * 6371)
    assert np.allclose(v, 5.0)
    pick = n.pick(G.centers)
    assert np.array_equal(pick[:g.n], np.arange(g.n))


def test_refine_refuses_a_coarser_level(made):
    w = W.load(made["src"])
    with pytest.raises(SystemExit):
        RF.refine(w, 4)


def test_refine_a_finished_time_zoom_world(made):
    """A finished time-zoom frame (its orbit anomaly, its held trees) refines too."""
    src = TZ.source_from_run(made["run"], 20.0)
    res = TZ.simulate(src, kyr=6, step=0.5, every=2.0)
    tz = TZ.save(res, src, kyr=6, step=0.5, every=2.0)
    p = F.finish_timezoom(tz.name, 6.0)
    w = W.load(p)
    w["id"] = p.stem
    out = RF.refine(w, 5, log=lambda *a: None)
    assert out["meta"]["timezoom"] == tz.name and out["grid"].n == build_grid(5).n
    assert np.isfinite(out["layers"]["temperature"]).all()
