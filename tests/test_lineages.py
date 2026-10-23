"""Lineages lane (docs/proposals/lineages.md): the recent pass and the peoples' history,
on a small fake time zoom (level 3) in a temporary store."""

from __future__ import annotations

import json

import numpy as np
import pytest

from planet import store as S
from planet import timeline as T
from planet.grid import build_grid
from planet.lineages import recent as R

LEVEL = 3


def _fake_timezoom(root, kyr=40.0, every=2.0) -> str:
    """Two continents (lon -60..60 and 90..150) joined by a shelf (60..90, |lat| < 25, 40 m deep)
    that is dry while the glacial index is high (sea down 80 m), a polar ice cap that grows with it,
    and a small island (lon -120)."""
    S.set_root(root)
    g = build_grid(LEVEL)
    lat, lon = g.lat, g.lon
    ts = np.arange(0, kyr + every / 2, every)
    gi = np.clip(np.sin(np.pi * ts / kyr) * 1.2, 0, 1)  # glacial index: up, then down
    bed = np.full(g.n, -2000.0)
    bed[np.abs(lon) < 60] = 400
    bed[(lon > 90) & (lon < 150)] = 300
    bed[(lon > 60) & (lon < 90) & (np.abs(lat) < 25)] = -40
    d = np.degrees(np.arccos(np.clip(np.cos(np.radians(lat)) * np.cos(np.radians(lon + 120)), -1, 1)))
    bed[d < 9] = 200
    data = {k: [] for k in ("elevation", "ice", "temperature", "climate", "tree_cover")}
    frames = []
    for t, I in zip(ts, gi):
        ice = np.where((np.abs(lat) > 62 - 12 * I) & (bed > 0), 800.0 * (0.3 + I), 0.0)
        elev = bed + 80 * I + ice
        temp = 29 - 0.45 * np.abs(lat) - 6 * I
        land = (elev > 0) | (ice > 0)
        clim = np.where(temp > 22, 0, np.where(temp > 6, 14, 28))
        clim = np.where(land, clim, 30)
        data["elevation"].append(S.encode(np.round(elev), S.LAYERS["elevation"]))
        data["ice"].append(S.encode(np.round(ice), {**S.LAYERS["ice"], "dtype": "<u2", "scale": 1}))
        data["temperature"].append(S.encode(np.round(temp), S.LAYERS["temperature"]))
        data["climate"].append(S.encode(clim, S.LAYERS["climate"]))
        data["tree_cover"].append(S.encode(np.where(land & (temp > 0), 50, 0), S.LAYERS["tree_cover"]))
        frames.append({"t": float(t), "omega": {}, "hotspots": [], "volcanoes": [],
                       "stats": {"t": float(t), "sea_level_change_m": -80 * I, "ice_pct": float((ice > 0).mean() * 100),
                                 "ice_volume_mkm3": float(I), "glacial_index": float(I), "global_temp_c": 14 - 6 * I,
                                 "max_ice_m": float(ice.max()), "ice_age": "building"}})
    specs = {"elevation": S.LAYERS["elevation"], "ice": {**S.LAYERS["ice"], "dtype": "<u2", "scale": 1},
             "temperature": S.LAYERS["temperature"], "climate": S.LAYERS["climate"], "tree_cover": S.LAYERS["tree_cover"]}
    run_id = "faketz"
    out = S.path_of("run", run_id)
    layers = S.write_layers(out, {k: np.stack(v) for k, v in data.items()}, specs)
    S.write_grid(g)
    S.write_json(out / "run.json", {
        "format": "procgen-run/2", "kind": "timezoom", "id": run_id, "name": "fake time zoom",
        "meta": {"kind": "timezoom", "time_unit": "kyr", "source_run": "earth", "source_name": "fake", "at_myr": 0.0,
                 "kyr": kyr, "step_kyr": 0.5, "every": every, "myr": kyr / 1000, "frames": len(ts), "seed": 1,
                 "level": LEVEL, "cells": g.n, "cell_size_km": 900, "params": {}, "created": "now"},
        "grid": f"../../grids/L{LEVEL}.json", "legend": S.legends(), "layers": layers, "events": [], "frames": frames})
    return run_id


@pytest.fixture
def faketz(tmp_path):
    old = S.root()
    tz = _fake_timezoom(tmp_path)
    yield tz
    S.set_root(old)


def test_recent_interpolates_the_time_zoom(faketz):
    ps = R.Pass(faketz, now_kyr=40.0, params=R.RecentParams(kyr=10, seed=3))
    assert ps.start == pytest.approx(-10.0)
    a = ps.fields(-9.0, variability=False)  # time zoom 31 kyr: halfway between the 30 and 32 kyr frames
    run, arr = T.load_frames(S.find_run(faketz), ("temperature",))
    want = 0.5 * (T.frame(run, arr, "temperature", 15) + T.frame(run, arr, "temperature", 16))
    assert np.allclose(a["temperature"], want)
    assert len(ps.steps) == 101 and ps.frame_times()[0] == -10.0 and ps.frame_times()[-1] == 0.0


def test_recent_variability_is_seeded_and_bounded(faketz):
    p1 = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=5, episodes_per_kyr=0.5))
    p2 = R.Pass(faketz, 40.0, R.RecentParams(kyr=20, seed=5, episodes_per_kyr=0.5))
    assert np.array_equal(p1.noise, p2.noise) and [e.t0 for e in p1.episodes] == [e.t0 for e in p2.episodes]
    assert 0.1 < p1.noise.std() < 1.0
    dT, rf, _ = p1.anomaly(-5.0)
    assert np.all(rf > 0.4) and np.all(rf <= 1.0) and np.all(np.abs(dT) < 6)
    # the window holds the deglaciation (index 1 -> 0): one cold reversal
    assert sum(e.kind == "cold reversal" for e in p1.episodes) == 1


def test_recent_saved_as_a_viewable_time_zoom(faketz):
    ps = R.Pass(faketz, 40.0, R.RecentParams(kyr=10, every=1.0, seed=1))
    out = R.save(ps)
    run = json.loads((out / "run.json").read_text())
    assert run["kind"] == "timezoom" and run["meta"]["phase"] == "recent" and run["meta"]["timezoom"] == faketz
    assert [f["t"] for f in run["frames"]] == [float(t) for t in range(-10, 1)]
    assert set(run["layers"]) >= {"elevation", "ice", "temperature", "climate", "precipitation"}
    _, arr = T.load_frames(out, ("precipitation",))
    assert arr["precipitation"].shape == (11, build_grid(LEVEL).n)
    assert (out / "run.txt").is_file()
    assert R.resolve(faketz) == (faketz, None, None)
