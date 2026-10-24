"""Option C measurement only (PW-564, not merged): a brightening star, luminosity +0.9% per 100 Myr from the run's
start (Gough 1981, Sun-like star now), forcing S0/4 (1 - 0.3) dL/L = 238 W/m2 dL/L at ~0.6 C per W/m2 (PW-564's
estimate of the model's sensitivity): +1.29 C per 100 Myr added to the global temperature's target (through
climate_offset, which only global_temperature reads). The thermostat absorbs it as it can.
YOUNG=1: the star is as young as the planet (the run starts at its formation), ~0.6-0.7% per 100 Myr over 0-1 Gyr.
usage (repo root): [YOUNG=1] c_run.py SEED OUT_DIR k=v ..."""
import os
import sys

sys.path[:0] = [os.getcwd()]
from pathlib import Path  # noqa: E402

from planet.tectonics import earth  # noqa: E402
from tools import ice_diag  # noqa: E402

RATE = 0.6 * 238.0 * 0.009 / 100.0  # C per Myr
YOUNG = os.environ.get("YOUNG") == "1"  # Gough 1981 for a star as young as the planet: L(t) = 1 / (1 + 0.4 (1 - t / 4570 Myr))


def solar(t):
    if YOUNG:
        L = lambda u: 1.0 / (1.0 + 0.4 * (1.0 - u / 4570.0))  # noqa: E731
        return 0.6 * 238.0 * (L(t) / L(0.0) - 1.0)
    return RATE * t
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
ice_diag.run(seed, 1000.0, 6, ice_diag.parse_sets(sys.argv[3:]), out)
