"""Glacial time zoom (planet/timezoom.py): bookkeeping and sanity, on the
session's level-4 simulation (fast)."""

import json
import numpy as np
import pytest

from planet import timeline as T, timezoom as Z

NO_ORBIT = dict(obliquity_amp=0.0, ecc_mean=0.0, ecc_100=0.0, ecc_400=0.0, orbit_ref="mean")


@pytest.fixture(scope="module")
def cold_src(sim4):
    """sim4's moment, made an icehouse (8 C colder) so there's ice to move."""
    src = Z.source_from_sim(sim4)
    src["dT"] = src["dT"] - 8.0
    return src


@pytest.fixture(scope="module")
def cold_run(cold_src):
    return Z.simulate(cold_src, kyr=40, step=0.5, every=2.0)


def test_insolation():
    """Global annual mean = S0/4; no tilt and a circular orbit: the poles get
    nothing; Earth today: 65N midsummer ~480-520 W/m2."""
    lat = Z.BAND_LAT
    w = np.cos(np.radians(lat))
    q = Z.insolation(23.44, 0.0167, 283.0)
    assert abs((q.mean(1) * w).sum() / w.sum() - Z.S0 / 4 * (1 / np.sqrt(1 - 0.0167**2))) < 2
    assert Z.insolation(0.0, 0.0, 0.0, np.array([90.0, -90.0])).max() < 1e-6
    assert 450 < Z.insolation(23.44, 0.0167, 283.0, np.array([65.0]))[0, 2:4].max() < 530


def test_ice_and_sea_level_bookkeeping(cold_src, cold_run):
    r = cold_run
    H = r["state"]["H"]
    assert np.isfinite(H).all() and (H >= 0).all()
    assert (r["data"]["ice"] >= 0).all()
    b = r["budget"]
    # flow conserves ice exactly; volume changes only by mass balance and calving
    assert abs((b["V_end"] - b["V0"]) - (b["smb"] - b["calved"])) < 1e-6 * max(b["V0"], 1e12)
    # sea level is the change of the sea water the ice holds, spread over the starting ocean
    assert b["Vaf0"] <= b["V0"]
    for f in r["frames"]:
        s = f["stats"]
        want = -(s["ice_sea_equiv_mkm3"] * 1e15 - b["Vaf0"]) / b["ocean_area"]
        # (sea level follows the ice one step late: timezoom's fixed point takes one pass per step)
        assert abs(s["sea_level_change_m"] - want) < 0.5 + 1e-3 * abs(want), f["t"]
        assert s["sea_level_m"] == pytest.approx(cold_src["sea_level"] + s["sea_level_change_m"], abs=0.11)
    # something happened (an 8 C colder world grows ice) and sea level followed
    assert r["frames"][-1]["stats"]["sea_level_change_m"] < -1


def test_deterministic(cold_src, cold_run):
    again = Z.simulate(cold_src, kyr=40, step=0.5, every=2.0)
    for k, v in cold_run["data"].items():
        assert np.array_equal(v, again["data"][k]), k
    assert np.array_equal(cold_run["series"], again["series"])


def test_warm_unforced_stays_ice_free(sim4):
    """A greenhouse era with no orbital forcing: no ice appears. High peaks
    are capped first: a 5 km mountain keeps glaciers even in a hothouse."""
    src = Z.source_from_sim(sim4)
    src["elev"] = np.minimum(src["elev"], 1500.0)
    src["dT"] = src["dT"] + 8.0
    src["ice"] = np.zeros_like(src["ice"])
    r = Z.simulate(src, kyr=30, step=0.5, every=10.0, params=Z.TZParams(**NO_ORBIT))
    assert all(f["stats"]["ice_volume_mkm3"] < 0.01 for f in r["frames"])
    assert abs(r["frames"][-1]["stats"]["sea_level_change_m"]) < 0.1


def test_orbit_moves_the_ice(cold_src):
    """Same world with and without orbital cycles: the cycles change the ice."""
    a = Z.simulate(cold_src, kyr=20, step=0.5, every=10.0, params=Z.TZParams(**NO_ORBIT))
    b = Z.simulate(cold_src, kyr=20, step=0.5, every=10.0, params=Z.TZParams(phases="zero", orbit_ref="mean"))
    assert not np.allclose(a["state"]["H"], b["state"]["H"])


def test_saved_run_format(cold_src, cold_run, data_root):
    """Written in the run format the viewer reads, marked as a time zoom."""
    out = Z.save(cold_run, cold_src, kyr=40, step=0.5, every=2.0)
    run, arr = T.load_frames(out)
    m = run["meta"]
    assert run["kind"] == m["kind"] == "timezoom" and m["time_unit"] == "kyr"
    assert m["source_run"] == "sim" and m["kyr"] == 40 and "code" in m
    nf, n = len(run["frames"]), cold_src["grid"].n
    for k in Z.LAYERS:
        assert arr[k].shape == (nf, n), k
    for k in Z.STATIC:
        assert arr[k].shape == (1, n), k
    assert [f["t"] for f in run["frames"]] == [2.0 * i for i in range(nf)]
    for k in ("plates", "land_pct", "landmasses", "largest_landmass_pct", "max_elev_m", "global_temp_c",
              "sea_level_m", "ice_pct", "mean_speed_cmyr", "max_speed_cmyr"):  # what the viewer shows
        assert k in run["frames"][0]["stats"], k
    assert (out / "run.txt").exists()
    idx = json.loads((data_root / "runs" / "index.json").read_text())
    assert idx[0]["kind"] == "timezoom" and idx[0]["at_myr"] == cold_src["at"]
    with pytest.raises(SystemExit):
        T.slice_world(out, 0.0)


def test_feedback_room(cold_src, cold_run):
    """A run's moment is the cycle average: only average_room of the CO2 and
    ice-albedo caps is left (PW-031); 'interglacial' gets them in full."""
    p = Z.TZParams()
    floor = -(p.co2_cool * p.co2_max + p.ice_albedo_max)
    dT = [f["stats"]["dT_global"] for f in cold_run["frames"]]
    assert min(dT) >= p.average_room * floor - 0.01
    full = Z.simulate(cold_src, kyr=40, step=0.5, every=2.0, params=Z.TZParams(start="interglacial"))
    assert min(f["stats"]["dT_global"] for f in full["frames"]) <= min(dT)
