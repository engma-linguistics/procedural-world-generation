"""The meander train's easing (planet/zoom/fine_meander.py): bounded in memory whatever the reach's phase does."""

import numpy as np

from planet.zoom import fine_meander as ZFM


def test_ease_past_the_samples_is_their_minimum():
    """A half-window longer than the samples gives their minimum everywhere, the same as one the samples' length."""
    r = np.linspace(0.2, 1.0, 40) ** 2
    out = ZFM._ease(r, 10**9)  # (uncapped: a 16 GB pad)
    assert np.allclose(out, ZFM._ease(r, len(r))) and np.allclose(out, r.min())


def test_a_reach_whose_phase_does_not_advance_trains_in_bounded_memory():
    """dba204's level-4 tile py.1.1/4/7/151 (11-11): an edge block's reach with a constant valley phase made train()
    ask _ease for half ~1.6e9 samples (23 GB, then the OOM killer took the machine). It now trains as any reach."""
    n = 50
    psi = np.full(n, 3.0)
    x, y, st = ZFM.train(psi, np.full(n, 0.8), np.full(n, 2.0), np.full(n, 0.1), None, 0.025, 1.2, 7)
    assert x.shape == (n,) and np.isfinite(x).all() and np.isfinite(y).all()
