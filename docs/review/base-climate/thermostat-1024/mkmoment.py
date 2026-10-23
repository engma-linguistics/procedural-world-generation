"""usage: mkmoment.py OUT.pkl SEED [LEVEL MYR] -- a sim moment (timezoom.source_from_sim, without its grid) for static.py."""
import os
import pickle
import sys

sys.path[:0] = [os.getcwd(), os.path.join(os.getcwd(), "tests")]
os.environ.setdefault("NUMBA_NUM_THREADS", "4")
from helpers import run_sim  # noqa: E402

from planet import timezoom as Z  # noqa: E402

seed, level, myr = int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 5, float(sys.argv[4]) if len(sys.argv) > 4 else 400.0
s = Z.source_from_sim(run_sim(level=level, seed=seed, myr=myr))
s = {k: v for k, v in s.items() if k != "grid"}
open(sys.argv[1], "wb").write(pickle.dumps(s))
