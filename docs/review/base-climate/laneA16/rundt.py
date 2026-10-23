"""The seed's L5 300 Myr run, its dT and ice: does the run depend on the process (hash seed, imports)?
usage: PYTHONPATH=.:tests uv run python rundt.py SEED"""
import os
import sys

import planet
from helpers import run_sim

s = run_sim(level=5, seed=int(sys.argv[1]), myr=300)
print("seed", sys.argv[1], "hashseed", os.environ.get("PYTHONHASHSEED"), "planet", planet.__file__,
      "dT", s.dT, "ice", float((s.snapshot().ice > 1).mean()), flush=True)
