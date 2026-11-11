"""PW-1684: the scorecard reports medians over the late window (the run's last 40%), not only its last moment."""
import numpy as np

from tools import scorecard as sc


def test_the_late_window_is_the_last_40_percent_sampled_every_20_myr():
    t0, ts = sc.late_window(1000)
    assert t0 == 600
    assert ts == [600 + 20 * k for k in range(21)]
    t0, ts = sc.late_window(500)
    assert t0 == 300 and ts[0] == 300 and ts[-1] == 500 and len(ts) == 11


def test_the_late_summary_is_the_median_and_mean_of_the_window_only():
    rows = [{"t": t, "gt4km": v, "masses": 3, "tag": "x"} for t, v in ((500, 99.0), (600, 1.0), (700, 5.0), (800, 2.0))]
    s = sc.late_summary(rows, 600)
    assert (s["t0"], s["t1"], s["n"]) == (600, 800, 3)
    assert s["median"]["gt4km"] == 2.0 and s["mean"]["gt4km"] == round((1 + 5 + 2) / 3, 2)
    assert "tag" not in s["median"] and s["median"]["masses"] == 3


def test_world_scores_keeps_the_100_myr_track_and_adds_the_late_one(monkeypatch):
    """The 100-Myr `track` (and the `final` row the old lines compare) is unchanged; the late samples come on top."""

    class FakeSim:
        def __init__(self, grid, seed, params, dt):
            self.t, self.w_thick, self.w_cont = 0.0, np.ones(4), np.array([True, True, False, False])
            self.w_age, self.flora = np.ones(4), [np.inf]

        def run(self, t):
            assert t > self.t  # (never asked to go back)
            self.t = t

    monkeypatch.setattr(sc, "Simulation", FakeSim)
    monkeypatch.setattr(sc, "build_grid", lambda level: None)
    monkeypatch.setattr(sc, "sample", lambda sim: {"t": sim.t, "land": sim.t / 10, "largest": 1, "plate_max": 1})
    w = sc.world_scores(1, 1000)
    assert [r["t"] for r in w["track"]] == [100.0 * k for k in range(1, 11)]
    assert w["final"]["t"] == 1000
    assert [r["t"] for r in w["late_track"]] == [600 + 20 * k for k in range(21)]
    assert w["late"]["n"] == 21 and w["late"]["median"]["land"] == 80.0
    assert w["land_min"] == 10 and w["land_max"] == 100  # (over the 100-Myr track, as before)
