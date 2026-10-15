"""Finished worlds (planet/finish.py, PW-091): a world at any frame of a
glacial time zoom, and the API / queue around it, on a tiny level-4 run."""

import json

import numpy as np
import pytest

from planet import api, finish as F, store as S, timeline as T, timezoom as TZ, world as W
from planet.tectonics import Params


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    """A tiny run, and an 8 C colder time zoom of it (so the ice grows and the sea falls)."""
    tmp = tmp_path_factory.mktemp("finish")
    S.set_root(tmp)
    run = T.simulate(seed=1, level=4, myr=40.0, dt=2.0, every=20.0, name="tiny", params=Params())
    src = TZ.source_from_run(run, 20.0)
    src["dT"] -= 8.0
    res = TZ.simulate(src, kyr=30, step=0.5, every=2.0)
    tz = TZ.save(res, src, kyr=30, step=0.5, every=2.0)
    yield {"root": tmp, "run": run, "tz": tz, "res": res}
    S.set_root(None)


def test_frame_state_gives_back_the_bed(tiny):
    """Bed = surface - ice, to the metre, from every stored frame; frame 0's is the keyframe's."""
    tz, res = tiny["tz"], tiny["res"]
    run, arr = T.load_frames(tiny["run"], ("elevation",))
    st0 = F.frame_state(tz, 0)
    keep = st0["ice"] == 0
    assert np.array_equal(st0["elevation"][keep], T.frame(run, arr, "elevation", 1)[keep].astype(float))
    st = F.frame_state(tz, len(res["frames"]) - 1)
    s = res["state"]
    bed = s["bed"] - s["sl"]
    assert np.abs(st["elevation"] - bed).max() <= 1.0  # the true bed, also below sea level under grounded ice
    assert st["sea_level"] == res["frames"][-1]["stats"]["sea_level_m"]


def test_finish_at_any_kyr(tiny):
    tz = tiny["tz"]
    tzrun = json.loads((tz / "run.json").read_text())
    t_end = tzrun["frames"][-1]["t"]
    end = F.finish_timezoom(tz.name)  # default: the end
    mid = F.finish_timezoom(tz.name, 13.2)  # snaps to the frame at 14 kyr
    start = F.finish_timezoom(tz.name, 0)
    assert len({end, mid, start}) == 3
    w = W.load(end)
    m = w["meta"]
    s = tzrun["frames"][-1]["stats"]
    assert m["timezoom"] == tz.name and m["timezoom_kyr"] == t_end and m["finished"]
    assert m["source_run"] == tiny["run"].name and m["t_myr"] == 20 and m["from_keyframe"]
    assert m["sea_level_m"] == round(s["sea_level_m"], 1) and abs(m["global_temp_c"] - s["global_temp_c"]) <= 0.051  # (14.5 + (x - 14.5) may round the other way)
    assert W.load(mid)["meta"]["timezoom_kyr"] == 14
    # an ice age: more ice and (the sea having fallen) more land than at the start
    w0 = W.load(start)
    assert s["sea_level_change_m"] < -1
    assert w["layers"]["ice"].sum() > w0["layers"]["ice"].sum()
    assert (w["layers"]["elevation"] > 0).sum() >= (w0["layers"]["elevation"] > 0).sum()
    # a normal world: the usual layers, in the index with its provenance
    for k in ("biome", "flow", "lake", "temperature_jul", "rock", "landform"):
        assert k in w["layers"], k
    idx = {e["id"]: e for e in json.loads((tiny["root"] / "worlds" / "index.json").read_text())}
    assert idx[end.stem]["timezoom"] == tz.name and idx[end.stem]["timezoom_kyr"] == t_end
    # the same frame again: reused
    assert F.finish_timezoom(tz.name, t_end - 0.4) == end
    # frame 0 is the plain keyframe world (same bed, same texture; only the climate, 8 C colder here,
    # carves the valleys a little differently), and isn't taken for one
    plain = T.world_from_frame(tiny["run"], 20.0)
    diff = np.abs(plain["layers"]["elevation"] - w0["layers"]["elevation"])
    assert np.median(diff) == 0 and diff.max() < 30, diff.max()
    assert api.find_slice(tiny["run"], 20.0) is None
    with pytest.raises(SystemExit):
        F.finish_timezoom(tz.name, 99)
    with pytest.raises(SystemExit):
        F.finish_timezoom(tiny["run"].name, 0)


def test_finish_api(tiny):
    tz = tiny["tz"].name
    assert api.parse_finish_request({"timezoom": tz, "kyr": "5.2"}) == {"type": "finish", "timezoom": tz, "kyr": 6.0}
    assert api.parse_finish_request({"timezoom": tz})["kyr"] == 30
    assert api.parse_finish_request({"run": tiny["run"].name, "t": 19})["t"] == 20
    for bad in ({}, {"timezoom": tz, "run": tiny["run"].name}, {"timezoom": tz, "kyr": 500},
                {"timezoom": tiny["run"].name}, {"run": tz, "t": 0}, {"run": tiny["run"].name, "t": 900}):
        with pytest.raises(api.BadRequest):
            api.parse_finish_request(bad)
    with pytest.raises(SystemExit):
        api.parse_finish_request({"timezoom": "nope"})
    # through the shared queue, as the server does: the job carries the world's id
    jobs = api.Jobs(api.any_job)
    seen = []
    j = jobs.wait(jobs.submit(api.parse_finish_request({"timezoom": tz, "kyr": 8})))
    assert j["status"] == "done", j
    assert W.load(S.find_world(j["world"]))["meta"]["timezoom_kyr"] == 8
    # straight from the run time: the keyframe world (the Zoom button's), not a finished one
    res = api.finish_job({"run": tiny["run"].name, "t": 20}, lambda f, msg: seen.append(f))
    m = api.world_header(S.find_world(res["world"]))["meta"]
    assert m["t_myr"] == 20 and not m.get("timezoom") and seen[-1] == 1.0
    assert api.find_slice(tiny["run"], 20.0).stem == res["world"]
