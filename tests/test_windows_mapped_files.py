"""Windows will not rewrite or replace a file this process still memory-maps (PW-1760: the 3-OS install smoke test's
zoom step failed with "[Errno 22] Invalid argument: ...zooms/<id>/layers/barrier_island.bin": coast.add_to_zoom
loaded the zoom with its layers mapped, then rewrote barrier_island.bin). Linux allows it, so these tests play
Windows: `windows_maps` makes opening a layer file for writing raise OSError(EINVAL), and os.replace onto it raise
PermissionError, while a np.memmap of it from store.read_layer is alive in this process."""

import builtins
import errno
import gc
import json
import weakref
from pathlib import Path

import numpy as np
import pytest

from planet import osutil as OS
from planet import store as S
from planet import timeline as T
from planet import world as W
from planet.tectonics import Params
from planet.zoom import coast as ZC
from planet.zoom import regional as Z


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("winmaps")
    S.set_root(tmp)
    run = T.simulate(seed=1, level=4, myr=40.0, dt=2.0, every=20.0, name="tiny", params=Params())
    path = W.save(T.world_from_frame(S.find_run(run.name), 20.0), "tiny maps")
    yield path.stem
    S.set_root(None)


@pytest.fixture
def windows_maps(monkeypatch):
    """Windows' rule for this process's own maps: no writing, no replacing a file while a map of it is alive. Returns
    mapped(path) -> bool."""
    live: list[tuple[str, weakref.ref]] = []
    real_read, real_replace = S.read_layer, OS.replace

    def read_layer(base_dir, spec, mmap=True):
        a = real_read(base_dir, spec, mmap)
        if isinstance(a, np.memmap):
            live.append((str(Path(a.filename).resolve()), weakref.ref(a)))  # (views keep their base alive)
        return a

    def mapped(path) -> bool:
        p = str(Path(path).resolve())
        return any(q == p and r() is not None for q, r in live)

    def guarded_open(file, mode="r", *a, **k):
        if any(c in mode for c in "wa+") and mapped(file):
            raise OSError(errno.EINVAL, "Invalid argument", str(file))
        return builtins.open(file, mode, *a, **k)

    def guarded_replace(src, dst):
        if mapped(dst):
            raise PermissionError(errno.EACCES, "Access is denied", str(dst))
        return real_replace(src, dst)

    monkeypatch.setattr(S, "read_layer", read_layer)
    monkeypatch.setattr(S, "open", guarded_open, raising=False)
    monkeypatch.setattr(OS, "replace", guarded_replace)
    return mapped


def test_the_helper_refuses_a_rewrite_under_a_live_map(tiny, windows_maps):
    out = Z.zoom(tiny, 5.0, 30.0, 400.0, 20.0)
    meta, lay = Z.load(out, decode=True)  # (mapped: what coast.add_to_zoom used to do)
    f = out / "layers" / "barrier_island.bin"
    assert windows_maps(f)
    with pytest.raises(OSError) as ei:
        S.write_layers(out, {"barrier_island": np.asarray(lay["barrier_island"])}, {"barrier_island": ZC.LAYER_SPECS["barrier_island"]})
    assert ei.value.errno == errno.EINVAL
    del lay, ei  # (the caught exception's frames hold the array too: a cycle, so collect)
    gc.collect()
    assert not windows_maps(f)  # (the map goes with the last array on it)


def test_a_zoom_build_and_its_in_place_steps_rewrite_no_mapped_file(tiny, windows_maps):
    out = Z.zoom(tiny, -10.0, 60.0, 400.0, 20.0)  # (save, then coast.add_to_zoom and the deposits: the make's zoom step)
    m = json.loads((out / "zoom.json").read_text())
    assert "barrier_island" in m["layers"] and m["coast"]["stats"]["terrain"] is False
    before = {p.name: p.read_bytes() for p in (out / "layers").glob("*.bin")}
    ZC.add_to_zoom(out.name, terrain=True)  # (rewrites elevation and water too)
    Z.add_humanuse(out.name)
    Z.add_game(out.name)
    Z.add_satellite(out.name)
    after = {p.name: p.read_bytes() for p in (out / "layers").glob("*.bin")}
    assert after["barrier_island.bin"] == before["barrier_island.bin"]  # (the coast pass again: the same bytes)


def test_load_without_maps_reads_the_same_values(tiny):
    out = Z.zoom(tiny, 5.0, 30.0, 400.0, 20.0)
    m1, a = Z.load(out, decode=True)
    m2, b = Z.load(out, decode=True, mmap=False)
    assert m1 == m2 and a.keys() == b.keys()
    for k in a:
        assert not isinstance(b[k], np.memmap) and np.array_equal(np.asarray(a[k]), b[k]) and np.asarray(a[k]).dtype == b[k].dtype
