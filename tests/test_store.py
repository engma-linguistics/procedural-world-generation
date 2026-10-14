"""planet/store.py (paths, layer files and encodings, find/delete) and
simulation checkpoints, in a temporary data root."""

import json

import numpy as np
import pytest

from planet import server, store as S, timeline as T
from planet.tectonics import Params, Simulation

from helpers import run_sim
from test_golden import sim_digest


def test_root_from_env(monkeypatch, tmp_path):
    monkeypatch.setattr(S, "_root", None)
    monkeypatch.setenv("PLANET_DATA", str(tmp_path))
    assert S.root() == tmp_path.resolve() and S.runs_dir() == tmp_path.resolve() / "runs"
    monkeypatch.delenv("PLANET_DATA")
    assert S.root() == S.REPO


def test_encodings_round_trip(sim4):
    """Every layer a run stores decodes back to its value within the encoding's step."""
    snap = sim4.snapshot()
    g = sim4.grid
    vals = T.frame_values(g, snap, T.jet_of(g, snap))
    assert set(vals) == set(T.RUN_LAYERS) and set(T.RUN_LAYERS) <= set(S.LAYERS)
    for k, v in vals.items():
        spec = S.LAYERS[k]
        back = S.decode(S.encode(v, spec, g), spec, g)
        v = np.asarray(v, float)
        if k == "downstream":
            assert np.array_equal(back, v), k  # exact: the next cell down, -1 at the sea
        elif k == "flow":  # log scale: ~2% steps
            assert np.allclose(back, v, rtol=0.03, atol=0.05), k
        else:
            info = np.iinfo(np.dtype(spec["dtype"]))
            inside = (v / spec["scale"] >= info.min) & (v / spec["scale"] <= info.max)
            assert np.abs(back - v)[inside].max() <= spec["scale"] / 2 + 1e-9, k


def test_run_lakes(sim4):
    """Run frames keep the lakes of the last erosion step, as worlds name
    them: lake_kind (hydrology ids) and lake_depth (m) only on wet land."""
    from planet import hydrology as H
    snap = sim4.snapshot()
    k, d = snap.lake_kind, snap.lake_depth
    wet = (k == H.OPEN_LAKE) | (k == H.CLOSED_LAKE)
    assert set(np.unique(k)) <= {H.NO_LAKE, H.OPEN_LAKE, H.CLOSED_LAKE, H.SALT_PAN} and (k > 0).any()
    assert (d[wet] > 0).all() and (d[~wet] == 0).all()
    assert not (k > 0)[(snap.elevation <= 0) | (snap.ice > 0)].any()
    vals = T.frame_values(sim4.grid, snap, T.jet_of(sim4.grid, snap))
    assert np.array_equal(S.encode(vals["lake_kind"], S.LAYERS["lake_kind"]), k)


def test_layer_files(data_root):
    a = np.arange(12, dtype=np.int16).reshape(3, 4) * 7
    b = np.array([[0.5, 1.5]], np.float32)
    specs = {"elevation": S.LAYERS["elevation"], "x": {"units": "m", "description": "test"}}
    meta = S.write_layers(data_root / "r", {"elevation": a, "x": b}, specs)
    assert meta["elevation"] == {"file": "layers/elevation.bin", "dtype": "int16", "shape": [3, 4], "scale": 1,
                                 "offset": 0, "transform": None, "units": "m",
                                 "description": S.LAYERS["elevation"]["description"]}
    assert meta["x"]["dtype"] == "float32" and (data_root / "r" / "layers" / "x.bin").stat().st_size == 8
    got = S.read_layers(data_root / "r", json.loads(json.dumps(meta)))
    assert isinstance(got["elevation"], np.memmap)
    assert np.array_equal(got["elevation"], a) and np.array_equal(got["x"], b)
    assert np.array_equal(S.read_layer(data_root / "r", meta["elevation"], mmap=False)[2], a[2])


def test_json_header(data_root):
    p = data_root / "x.json"
    S.write_json(p, {"format": "f", "id": "abc", "meta": {"a": 1}, "frames": [1, 2], "name": "late"})
    assert json.loads(p.read_text())["frames"] == [1, 2]
    # stops at the first big key: "name" after "frames" isn't seen
    assert S.read_header(p, ("id", "meta", "name")) == {"id": "abc", "meta": {"a": 1}}
    p.write_text(json.dumps({"id": "x", "name": "y"}))  # one line: parsed whole
    assert S.read_header(p, ("id", "name")) == {"id": "x", "name": "y"}


def _fake(kind, item_id, world=None):
    """A minimal item of a kind, enough for find/index/delete."""
    if kind == "run":
        d = S.path_of("run", item_id)
        (d / "layers").mkdir(parents=True)
        S.write_json(d / "run.json", {"id": item_id, "name": f"run {item_id}", "meta": {
            "seed": 1, "level": 4, "myr": 10, "created": "now"}})
    elif kind == "world":
        S.worlds_dir().mkdir(parents=True, exist_ok=True)
        S.write_json(S.path_of("world", item_id), {"id": item_id, "name": f"world {item_id}",
                                                   "meta": {"created": "now"}, "layers": {}})
        S.path_of("world", item_id).with_suffix(".txt").write_text("report")
        S.highlights_path(item_id).parent.mkdir(parents=True, exist_ok=True)
        S.highlights_path(item_id).write_text("{}")
    else:
        d = S.path_of("zoom", item_id)
        d.mkdir(parents=True)
        (d / "zoom.json").write_text(json.dumps({
            "id": item_id, "name": f"zoom {item_id}", "created": "now", "source_world": {"id": world},
            "center": {"lat": 0, "lon": 0}, "size_km": 100, "res_km": 1}))


def test_find_and_delete(data_root):
    """A run and a world may share an id: deleting one leaves the other (bug
    B6). A world takes its zooms and highlights with it; zooms delete alone."""
    _fake("run", "abc123")
    _fake("world", "abc123")
    _fake("world", "w2")
    _fake("zoom", "z1", world="abc123")
    _fake("zoom", "z2", world="w2")
    _fake("zoom", "z3", world="w2")
    assert S.kinds_of("abc123") == ["run", "world"]
    assert S.find_run("abc123") == S.path_of("run", "abc123") == S.find_run(S.path_of("run", "abc123"))
    assert S.find_world("abc123.json") == S.find_world("abc123") == S.path_of("world", "abc123")
    with pytest.raises(SystemExit):
        S.find_zoom("abc123")
    assert [e["id"] for e in S.update_index("zoom")] and len(S.update_index("world")) == 2

    gone = S.delete("run", "abc123")
    assert gone == [S.path_of("run", "abc123")] and S.exists("world", "abc123") and S.exists("zoom", "z1")
    assert S.delete("run", "abc123") == []

    assert S.delete("zoom", "z3") == [S.path_of("zoom", "z3")] and S.exists("zoom", "z2")
    assert {e["id"] for e in json.loads((S.zooms_dir() / "index.json").read_text())} == {"z1", "z2"}

    gone = S.delete("world", "abc123")
    assert set(gone) == {S.path_of("world", "abc123"), S.path_of("world", "abc123").with_suffix(".txt"),
                         S.highlights_path("abc123"), S.path_of("zoom", "z1")}
    assert S.exists("world", "w2") and S.exists("zoom", "z2") and S.highlights_path("w2").exists()
    assert [e["id"] for e in json.loads((S.worlds_dir() / "index.json").read_text())] == ["w2"]

    # bad or reserved ids never reach the file system
    for bad in ("../runs", "index", "", "a/b"):
        assert S.delete("world", bad) == [] and not S.exists("run", bad)
    assert server.delete("/zooms/z2") == 204 and not S.exists("zoom", "z2")
    assert server.delete("/zooms/z2") == 404 and server.delete("/elsewhere/x") == 400


def test_orphans(data_root):
    _fake("world", "w1")
    _fake("zoom", "z1", world="w1")
    _fake("zoom", "z2", world="gone")
    S.highlights_path("gone").write_text("{}")
    (S.runs_dir() / "killed" / "state").mkdir(parents=True)
    assert S.orphans() == [S.runs_dir() / "killed", S.path_of("zoom", "z2"), S.highlights_path("gone")]
    S.delete_orphans()
    assert S.orphans() == [] and S.exists("zoom", "z1") and S.highlights_path("w1").exists()


def test_checkpoint_resume_bit_identical(sim4_60):
    """Restoring the state saved at t and running on to t' gives exactly the
    straight run's state at t' (all arrays, events, budget, scalars)."""
    states = {}
    sim = Simulation(sim4_60.grid, 1, Params(), 2.0)
    sim.run(60, lambda s: states.setdefault(s.t, s.state()) if s.t in (20, 40) else None)
    assert sim_digest(sim) == sim_digest(sim4_60)
    for t, st in states.items():
        r = Simulation.from_state(sim.grid, 1, Params(), 2.0, st)
        assert r.t == t
        r.run(60)
        assert sim_digest(r) == sim_digest(sim4_60), t


def test_simulate_checkpoints_and_replay(data_root, sim4_60):
    """simulate saves the state every checkpoint_every Myr; replay starts
    from the latest one at or before t, and the result is the same planet."""
    out = T.simulate(1, 4, 60.0, 2.0, 20.0, "ck", Params(), checkpoint_every=20.0)
    assert S.checkpoints(out) == [20.0, 40.0, 60.0]
    assert json.loads((out / "run.json").read_text())["meta"]["checkpoint_every"] == 20.0
    said = []
    sim = T.replay(out, 50.0, log=said.append)
    assert said == ["replaying from the checkpoint at t=40"] and sim.t == 50.0
    sim.run(60)
    assert sim_digest(sim) == sim_digest(sim4_60)
    assert sim_digest(T.replay(out, 60.0, use_checkpoints=False)) == sim_digest(sim4_60)
    # a world sliced through a checkpoint still matches the stored keyframe
    world = json.loads(T.slice_world(out, 40.0).read_text())
    assert world["meta"]["replay_matches_keyframe"] is True


def test_run_layout(data_root):
    """One file per layer, specs with the encoding, keyframes readable by frame()."""
    out = T.simulate(1, 4, 8.0, 2.0, 4.0, "t", Params(), checkpoint_every=0)
    run = json.loads((out / "run.json").read_text())
    assert list(run["layers"]) == list(T.RUN_LAYERS) and not (out / "state").exists()
    for k, spec in run["layers"].items():
        assert (out / spec["file"]).stat().st_size == np.dtype(spec["dtype"]).itemsize * np.prod(spec["shape"]), k
        assert spec["shape"] == [3, run["meta"]["cells"]]
    assert run["layers"]["ice"]["scale"] == 20 and run["layers"]["flow"]["transform"] == "log2p1"
    assert set(run["legend"]) == {"rocks", "koppen", "biomes"}
    run2, arr = T.load_frames(out, ("plate", "downstream"))
    sim = run_sim(myr=8)
    assert np.array_equal(T.frame(run2, arr, "plate", 2), sim.snapshot().plate)
    assert np.array_equal(T.frame(run2, arr, "downstream", 2, sim.grid), sim.snapshot().downstream)
    assert S.read_header(out / "run.json")["name"] == "t"
    assert S.update_index("run")[0]["id"] == run["id"]
