"""Cross-check of the cold_moment fixture: the run's ice rule (_cold: 4 C colder, 6 climate updates) on a fixed
source, with this tree's climate. usage (from a tree's root):
  PYTHONPATH=.:tests uv run python xcold.py dump SEED OUT.pkl     # the L5 300 Myr source of this tree
  PYTHONPATH=.:tests uv run python xcold.py cold SRC.pkl [belt1] [col1]
belt1 / col1: westerly_belt / low_column forced to 1 (A15's steps off) if this tree has them."""
import pickle
import sys

import planet  # noqa: F401  (first: its thread caps must precede numpy)
import numpy as np

from planet import climate, timezoom as Z

if sys.argv[1] == "dump":
    from helpers import run_sim
    pickle.dump(Z.source_from_sim(run_sim(level=5, seed=int(sys.argv[2]), myr=300)), open(sys.argv[3], "wb"))
    sys.exit()
if "belt1" in sys.argv and hasattr(climate, "westerly_belt"):
    climate.westerly_belt = lambda g, a, b: (np.ones(g.n), np.ones(g.n))
if "col1" in sys.argv and hasattr(climate, "low_column"):
    climate.low_column = lambda g, land, tune: np.ones(g.n)
from test_timezoom_consistency import _cold, _plausible  # noqa: E402

src0 = pickle.load(open(sys.argv[2], "rb"))
src, c = _cold(src0)
lat = src["grid"].lat
ice = src["ice"] > 1
print(f"{sys.argv[2].rsplit('/', 1)[-1]} {sys.argv[3:]}: plausible {_plausible(src, c)}  sheets {100 * ice.mean():.2f}% "
      f"(N {100 * ice[lat > 0].mean():.2f} / S {100 * ice[lat < 0].mean():.2f})  run dT {src0['dT']:+.2f}  "
      f"land t_warm >60N {float(np.mean(c['t_warm'][(lat > 60) & (src['elev'] > 0)])) if ((lat > 60) & (src['elev'] > 0)).any() else float('nan'):.2f}",
      flush=True)
