"""C' measurement (PW-761, monkeypatched, not merged): a star as young as the planet brightening on Gough's (1981)
curve, L(t) / L_now = 1 / (1 + 0.4 (1 - t / 4570 Myr)), counted against the run's start (planet-relative), with the
model's own thermostat unchanged (its parameters are in the literature's range: README). Forcing
S0 / 4 (1 - 0.3) dL / L = 238 W/m2 x dL / L, at LAM C per W/m2 added to the global temperature's target (through
climate_offset, which only global_temperature reads).
LAM: the model's own sensitivity, co2_sensitivity / (5.35 ln 2) = 0.81 C per W/m2 (default; 3 C per doubling of
pCO2, Myhre et al. 1998's 5.35 ln ratio); LAM=0.6 is v1-finish-6's c_run.py value, for comparison.
RATE: a multiple of that brightening (the owner's lever, 2026-10-24: a slower star, within the plausible range).
usage (repo root): [LEVEL=7] [LAM=0.6] [RATE=0.5] c7_run.py SEED OUT_DIR k=v ..."""
import math
import os
import sys

sys.path[:0] = [os.getcwd()]
from pathlib import Path  # noqa: E402

from planet.tectonics import earth  # noqa: E402
from tools import ice_diag  # noqa: E402

STAR_AGE0 = 0.0  # Myr: the star's age at the run's start (the planet as young as its star)
LAM = float(os.environ.get("LAM", 3.0 / (5.35 * math.log(2.0))))
RATE = float(os.environ.get("RATE", 1.0))  # x Gough's brightening (a slower-evolving, lower-mass star: < 1)


def lum(t):
    return 1.0 / (1.0 + 0.4 * (1.0 - (STAR_AGE0 + t) / 4570.0))


def solar(t):
    return RATE * LAM * 238.0 * (lum(t) / lum(0.0) - 1.0)


_orig = earth.global_temperature
base = {}


def patched(sim, growth, newc, rng):
    p = sim.params
    b = base.setdefault(id(sim), p.climate_offset)
    object.__setattr__(p, "climate_offset", b + solar(sim.t))
    _orig(sim, growth, newc, rng)


earth.global_temperature = patched
seed, out = int(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
ice_diag.run(seed, 1000.0, int(os.environ.get("LEVEL", "6")), ice_diag.parse_sets(sys.argv[3:]), out)
