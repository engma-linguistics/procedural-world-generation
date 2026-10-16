"""Shared setup for the PW-249 profiling scripts: repo on sys.path, outputs into a scratch data root
($PLANET_DATA, default $PROF_SCRATCH/data), 16 numba threads unless set. Not part of planet/."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SP = os.environ.get("PROF_SCRATCH", "/tmp/planet-prof")
os.environ.setdefault("PLANET_DATA", SP + "/data")
os.environ.setdefault("NUMBA_NUM_THREADS", "16")
sys.path.insert(0, REPO)
sys.path.insert(0, HERE)
