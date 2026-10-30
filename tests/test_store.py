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
        spec = S.run_spec(k)
        back = S.decode(S.encode(v, spec, g), spec, g)
        v = np.asarray(v, float)
        if k == "downstream":
            assert np.array_equal(back, v), k  # exact: the next cell down, -1 at the sea
        elif spec.get("transform") == "log2p1":  # log scale: ~2-4% steps
            assert np.allclose(back, v, rtol=0.03, atol=0.05), k
        else:
            info = np.iinfo(np.dtype(spec["dtype"]))
            inside = (v / spec["scale"] >= info.min) & (v / spec["scale"] <= info.max)
            assert np.abs(back - v)[inside].max() <= spec["scale"] / 2 + 1e-9, k


def test_run_lakes(sim4):
    """Run frames keep the lakes of the last erosion step, as worlds name
    them: lake_kind (hydrology ids) and lake_depth (m) only on wet land."""
    from planet import hydrology as H
    from planet.tectonics import Simulation
    sim = sim4
    for _ in range(60):  # (on 2.5k cells lakes come and go: step a copy on until there are some)
        if (sim.snapshot().lake_kind > 0).any():
            break
        if sim is sim4:
            sim = Simulation.from_state(sim4.grid, sim4.seed, sim4.params, sim4.dt, sim4.state())
        sim.step()
    snap = sim.snapshot()
    k, d = snap.lake_kind, snap.lake_depth
    wet = (k == H.OPEN_LAKE) | (k == H.CLOSED_LAKE)
    assert set(np.unique(k)) <= {H.NO_LAKE, H.OPEN_LAKE, H.CLOSED_LAKE, H.SALT_PAN} and (k > 0).any()
    assert (d[wet] > 0).all() and (d[~wet] == 0).all()
    assert not (k > 0)[(snap.elevation <= 0) | (snap.ice > 0)].any()
    vals = T.frame_values(sim.grid, snap, T.jet_of(sim.grid, snap))
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


def test_interrupted_run_keeps_its_folder(data_root):
    """PW-508: simulate writes a "running" header first; an error or Ctrl-C keeps the folder and its checkpoints
    (header "interrupted"). Unfinished runs aren't listed, found or reused; an interrupted one is an orphan and can be
    deleted, a running one is neither."""
    def stop(f):
        if f >= 0.5:
            raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        T.simulate(1, 3, 20.0, 2.0, 4.0, "cut short", Params(), checkpoint_every=4.0, progress=stop)
    (d,) = [p for p in S.runs_dir().iterdir() if p.is_dir() and not p.name.startswith(".")]
    head = S.read_header(d / "run.json", ("status", "meta"))
    assert head["status"] == "interrupted" and "KeyboardInterrupt" in head["meta"]["error"]
    assert S.checkpoints(d) and S.run_status(d) == "interrupted"
    assert not S.exists("run", d.name) and S.items("run") == [] and S.orphans() == [d]
    with pytest.raises(SystemExit, match="interrupted"):
        S.find_run(d.name)
    # a header whose process is alive is running: not an orphan, not deletable; once its process is gone, interrupted
    run = json.loads((d / "run.json").read_text())
    S.write_json(d / "run.json", {**run, "status": "running", "meta": {**run["meta"], **S.process_stamp()}})
    assert S.run_status(d) == "running" and S.orphans() == [] and S.delete("run", d.name) == []
    S.write_json(d / "run.json", {**run, "status": "running", "meta": {**run["meta"], "pid": 2 ** 22 + 1}})
    assert S.run_status(d) == "interrupted"
    assert S.delete("run", d.name) and not d.exists()


def test_checkpoint_resume_bit_identical(sim4_60):
    """Restoring the state saved at t and running on to t' gives exactly the
    straight run's state at t' (all arrays, events, budget, scalars)."""
    states = {}
    sim = Simulation(sim4_60.grid, 1, Params(run_end=60.0), 2.0)
    sim.run(60, lambda s: states.setdefault(s.t, s.state()) if s.t in (20, 40) else None)
    assert sim_digest(sim) == sim_digest(sim4_60)
    for t, st in states.items():
        r = Simulation.from_state(sim.grid, 1, Params(run_end=60.0), 2.0, st)
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
    # PW-1035: a run stamped by other code still replays from its checkpoint (the keyframe check judges the replay)
    run = json.loads((out / "run.json").read_text())
    run["meta"]["code"]["planet_src_sha"] = run["meta"]["code"]["sim_sha"] = "other code"
    S.write_json(out / "run.json", run)
    said = []
    assert T.replay(out, 50.0, log=said.append).t == 50.0 and said == ["replaying from the checkpoint at t=40"]
    # a checkpoint that won't load: from t=0
    S.checkpoint_path(out, 40.0).write_bytes(b"not a checkpoint")
    said = []
    sim = T.replay(out, 50.0, log=said.append)
    assert sim.t == 50.0 and len(said) == 1 and "won't load" in said[0] and "from t=0" in said[0]


def test_shrunk_checkpoint_resumes_bit_identical(sim4_60):
    """A checkpoint zeroes the crust of the plate cells nothing reads
    (S.shrink_state: most of them); a run resumed from it is still exactly
    the straight run, and the plates' owned crust is untouched (PW-131)."""
    states = {}
    sim = Simulation(sim4_60.grid, 1, Params(run_end=60.0), 2.0)
    sim.run(60, lambda s: states.setdefault(s.t, s.state()) if s.t in (10, 30) else None)
    for t, st in states.items():
        pl = st["plates"]
        before = [a[pl.owned].copy() for a in pl.crust()]
        S.shrink_state(st)
        assert all(np.array_equal(a[pl.owned], b) for a, b in zip(pl.crust(), before))
        assert (pl.thick[~pl.owned] == 0).mean() > 0.8  # (most cells are stale copies)
        r = Simulation.from_state(sim.grid, 1, Params(run_end=60.0), 2.0, st)
        r.run(60)
        assert sim_digest(r) == sim_digest(sim4_60), t


def test_checkpoint_keeps_world_view_records(tmp_path, sim4_60):
    """A checkpoint zeroes the geological record of plate cells that own no
    crust, but not of cells the world view samples: a plate's slot can be
    the view's without being owned, and the view (and its subsidence) reads
    its record (PW-291: zeroing them moved a replayed checkpoint's elevation
    by up to ~1 km, failing slices at checkpoint times)."""
    st = sim4_60.state()
    pl, owner = st["plates"], st["owner"]
    cells = np.arange(0, owner.size, 7)
    pl.owned[owner[cells], pl.idx[owner[cells], cells]] = False  # make some of the view's slots unowned
    live = Simulation.from_state(sim4_60.grid, 1, Params(run_end=60.0), 2.0, st)
    path = tmp_path / "c.ckpt"
    S._write_checkpoint(path, st, sim4_60.grid)
    back = Simulation.from_state(sim4_60.grid, 1, Params(run_end=60.0), 2.0, S.read_checkpoint(path, sim4_60.grid))
    assert np.array_equal(back.w_rec, live.w_rec) and np.array_equal(back.w_lith, live.w_lith)
    assert np.array_equal(back.dyn, live.dyn) and np.array_equal(back.w_elev, live.w_elev)


def test_checkpoint_plate_idx_round_trip(tmp_path, sim4_60):
    """The plates' cell map is stored as its difference from a fresh
    grid.locate (~all zeros, PW-306) and read back exactly."""
    st = sim4_60.state()
    idx = st["plates"].idx.copy()
    path = tmp_path / "c.ckpt"
    S._write_checkpoint(path, st, sim4_60.grid)
    assert (st["plates"].idx == 0).mean() > 0.99  # (what was pickled)
    assert np.array_equal(S.read_checkpoint(path, sim4_60.grid)["plates"].idx, idx)


def test_run_layout(data_root):
    """One file per layer, specs with the encoding, keyframes readable by frame()."""
    out = T.simulate(1, 4, 8.0, 2.0, 4.0, "t", Params(), checkpoint_every=0)
    run = json.loads((out / "run.json").read_text())
    assert list(run["layers"]) == list(T.RUN_LAYERS) and not (out / "state").exists()
    for k, spec in run["layers"].items():
        assert (out / spec["file"]).stat().st_size == np.dtype(spec["dtype"]).itemsize * np.prod(spec["shape"]), k
        assert spec["shape"] == [len(run["frames"]), run["meta"]["cells"]]
    assert run["layers"]["ice"]["scale"] == 20 and run["layers"]["flow"]["transform"] == "log2p1"
    assert set(run["legend"]) == {"rocks", "koppen", "biomes", "landforms", "vegetation", "coastal_life", "soils", "human_use", "game", "resources", "coast"}
    run2, arr = T.load_frames(out, ("plate", "downstream"))
    sim = run_sim(myr=8)
    assert np.array_equal(T.frame(run2, arr, "plate", len(run2["frames"]) - 1), sim.snapshot().plate)
    assert np.array_equal(T.frame(run2, arr, "downstream", len(run2["frames"]) - 1, sim.grid), sim.snapshot().downstream)
    assert S.read_header(out / "run.json")["name"] == "t"
    assert S.update_index("run")[0]["id"] == run["id"]


def test_world_seasons():
    """Worlds store July / January temperature and rain (PW-126): July is the
    warm month in the north and the cold one in the south, and the half-year
    rains average to the annual."""
    from planet import world as W
    w = W.generate("plates", seed=2, level=4)
    L, lat = w["layers"], w["grid"].lat
    for k in ("temperature_jul", "temperature_jan", "precipitation_jul", "precipitation_jan"):
        assert k in S.LAYERS and len(L[k]) == len(lat)
    n, s = lat > 30, lat < -30
    assert np.abs(L["temperature_jul"][n] - L["warm_month"][n]).max() <= 0.51
    assert np.abs(L["temperature_jul"][s] - L["cold_month"][s]).max() <= 0.51
    assert np.abs(L["temperature_jan"][n] - L["cold_month"][n]).max() <= 0.51
    assert np.abs(0.5 * (L["precipitation_jul"] + L["precipitation_jan"]) - L["precipitation"]).max() <= 1


def test_grid_file_rewritten_when_the_grid_changes(data_root):
    """PW-1039: the shared grid file carries its grid's digest and is rewritten when the grid's cells differ."""
    from planet.grid import build_grid
    g = build_grid(3)
    p = S.write_grid(g)
    d = json.loads(p.read_text())
    assert d["digest"] == S.grid_digest(g) and len(d["nbr"]) == g.n
    t0 = p.stat().st_mtime_ns
    assert S.write_grid(g) == p and p.stat().st_mtime_ns == t0  # (the same grid: left alone)
    p.write_text(json.dumps({**d, "digest": "0" * 16, "lat": d["lat"][::-1]}))  # (made by other grid code)
    S.write_grid(g)
    assert json.loads(p.read_text()) == d


def test_update_meta_keeps_concurrent_keys(data_root):
    """PW-1040: passes adding to the same run.json at once (threads here; processes share the flock) keep each
    other's keys: update_meta re-reads under the lock."""
    import threading
    d = S.runs_dir() / "abc123"
    d.mkdir(parents=True)
    S.write_json(d / "run.json", {"id": "abc123", "meta": {}})
    go = threading.Barrier(8)

    def add(k):
        go.wait()
        for j in range(5):
            S.update_meta(d, lambda run: run["meta"].__setitem__(f"{k}-{j}", j))

    ts = [threading.Thread(target=add, args=(k,)) for k in range(8)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert len(json.loads((d / "run.json").read_text())["meta"]) == 40


def test_new_id_skips_taken_ids(data_root, monkeypatch):
    """PW-1040: a new id never lands on an existing run (its folder is made at once) or world."""
    (S.runs_dir() / "aaaaaa").mkdir(parents=True)
    S.worlds_dir().mkdir(parents=True, exist_ok=True)
    (S.worlds_dir() / "bbbbbb.json").write_text("{}")
    draws = iter(["aaaaaa", "cccccc", "bbbbbb", "dddddd"])
    monkeypatch.setattr(S.secrets, "token_hex", lambda n: next(draws))
    assert S.new_id() == "cccccc" and (S.runs_dir() / "cccccc").is_dir()
    assert S.new_id("world") == "dddddd"


def test_atomic_path(tmp_path):
    """PW-1040: np.savez through atomic_path lands at the path; the temporary name is unique and goes on failure."""
    p = tmp_path / "goods.npz"
    with S.atomic_path(p) as tmp:
        assert tmp.name.startswith(".goods.") and tmp.suffix == ".npz"
        np.savez(tmp, a=np.arange(3))
    assert np.load(p)["a"].tolist() == [0, 1, 2] and sorted(x.name for x in tmp_path.iterdir()) == ["goods.npz"]
    with pytest.raises(RuntimeError), S.atomic_path(p) as tmp:
        np.savez(tmp, a=np.arange(4))
        raise RuntimeError
    assert np.load(p)["a"].tolist() == [0, 1, 2] and sorted(x.name for x in tmp_path.iterdir()) == ["goods.npz"]


def test_code_hash_scopes():
    """PW-1035: one hashing rule, each cache naming its scope (the import closure of entry modules): the server
    and the zoom are in no cache's scope; each scope holds the code its cache reads."""
    from planet import provenance as P
    names = {s: {p.relative_to(P.PLANET).as_posix() for p in P.scope_files(s)} for s in P.SCOPES}
    for s in ("sim", "finish", "lineages", "highlights"):
        assert not {"server.py", "api.py", "zoom.py", "zoom_fine.py", "__main__.py"} & names[s], s
    assert {"tectonics/simulation.py", "climate.py", "tectonics/earth.py"} <= names["sim"]
    assert {"world.py", "finish.py", "soils.py", "vegetation.py"} <= names["finish"]
    assert {"lineages/land.py", "lineages/seafood.py", "lineages/recent.py", "resources.py"} <= names["lineages"]
    assert "highlights.py" in names["highlights"] and "server.py" in names["all"]
    assert len({P.code_hash(s) for s in P.SCOPES}) == len(P.SCOPES)


def test_highlights_cache_follows_the_world_file(data_root, monkeypatch):
    """PW-1035: a world saved again in place (enriched, say) doesn't keep its old highlights."""
    import os
    from planet import highlights as H
    w = S.worlds_dir() / "abc123.json"
    w.parent.mkdir(parents=True, exist_ok=True)
    w.write_text("{}")
    H.cache_path(w).parent.mkdir(parents=True, exist_ok=True)
    H.cache_path(w).write_text(json.dumps({"version": H.version(w), "features": []}))
    assert H.cached(w) is not None
    st = w.stat()
    os.utime(w, ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))
    assert H.cached(w) is None
