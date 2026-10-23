"""The cold_moment fixture's seed scan, every seed: plausible? and its share under > 1 m of ice.
usage (from a tree's root): PYTHONPATH=.:tests uv run python coldscan.py SEED [SEED ...]"""
import sys

import planet  # noqa: F401  (first: its thread caps must precede numpy, or the run differs)
import numpy as np

from helpers import run_sim
from planet import timezoom as Z
from test_timezoom_consistency import POLAR_LAND, _cold, _plausible

for seed in map(int, sys.argv[1:]):
    sim = run_sim(level=5, seed=seed, myr=300)
    src0 = Z.source_from_sim(sim)
    src, c = _cold(src0)
    lat, land = src["grid"].lat, src["elev"] > 0
    sink = np.where(land, 0.0, c["overturning"])
    cap = max(land[lat > 60].mean(), land[lat < -60].mean())
    print(f"seed {seed}: plausible {_plausible(src, c)}  sheets {100 * (src['ice'] > 1).mean():.2f}%  "
          f"run ice {100 * (src0['ice'] > 1).mean():.2f}%  run dT {src0['dT']:+.2f}  sl {src['sea_level']:+.0f}  "
          f"moc N/S {sink[lat > 0].sum():.1f}/{sink[lat < 0].sum():.1f}  cap {cap:.2f} (>= {POLAR_LAND})", flush=True)
