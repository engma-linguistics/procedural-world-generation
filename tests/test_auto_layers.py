"""Worlds from a stored run get the coast-form and resource layers (PW-620, PW-609), the history pass is kept
beside them, and every zoom sites deposits (PW-618); a fine zoom keeps its parent's deposits that lie inside it."""

import json

import numpy as np
import pytest

from planet import store as S
from planet import timeline as T
from planet import world as W
from planet import zoom as Z
from planet import zoom_resources as ZR
from planet.tectonics import Params


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("auto")
    S.set_root(tmp)
    run = T.simulate(seed=1, level=4, myr=40.0, dt=2.0, every=20.0, name="tiny", params=Params())
    yield tmp, run.name
    S.set_root(None)


def test_world_has_coast_and_resource_layers_and_its_history(tiny):
    _, run = tiny
    w = T.world_from_frame(S.find_run(run), 20.0)
    assert "coast_type" in w["layers"] and "barrier" in w["layers"]
    assert "resource" in w["layers"] and "res_coal" in w["layers"]
    assert w["meta"]["resources"]["history"] and w["meta"]["coast"]["created"]
    path = W.save(w, "tiny with")
    hist = S.read_history(path.stem)
    assert hist["column_depth"].shape[0] == w["grid"].n and hist["frames"] == w["meta"]["resources"]["keyframes"]
    assert S.delete("world", path.stem) and S.read_history(path.stem) is None  # (it goes with the world)


def test_no_resources_flag_leaves_the_resource_layers_out(tiny):
    _, run = tiny
    with W.resources_off():
        w = T.world_from_frame(S.find_run(run), 20.0)
    assert "resource" not in w["layers"] and "res_coal" not in w["layers"] and "history" not in w
    assert "coast_type" in w["layers"]  # (the coast layers are always made)


def test_zoom_sites_deposits(tiny):
    _, run = tiny
    path = W.save(T.world_from_frame(S.find_run(run), 20.0), "tiny zoom")
    out = Z.zoom(path.stem, 5.0, 30.0, 400.0, 20.0)
    m = json.loads((out / "zoom.json").read_text())
    assert m["resources"]["history"] and m["coast"]["stats"]["terrain"] is False
    assert "barrier_island" in m["layers"] and m["resources"]["summary"]["total"] == len(m["resources"]["deposits"])


def test_a_fine_zoom_keeps_its_parents_deposits_inside_it():
    parent = {"center": {"lat": 5.0, "lon": 30.0}, "nx": 20, "ny": 20, "res_km": 20.0}
    fine = {"center": {"lat": 5.0, "lon": 30.0}, "nx": 40, "ny": 40, "res_km": 5.0}  # 200 km across, same centre
    dep = [{"key": "coal", "form": "seam", "px": [10.0, 10.0]}, {"key": "coal", "form": "seam", "px": [1.5, 1.5]}]
    got = ZR._inherit(parent, {"deposits": dep}, fine, np.zeros((40, 40), bool))
    assert len(got) == 1 and np.allclose(got[0]["px"], [20.0, 20.0], atol=0.05)  # (the centre; the corner one is outside)
