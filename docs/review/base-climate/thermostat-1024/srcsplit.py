"""tools/ice_diag.py with the volcanic source's parts logged per step (read only: the run is unchanged):
src_newc (new ocean floor), src_arc (20 x arc growth), arc_gain (crust.thermostats' arc growth factor, the
continental-volume thermostat). Run from a tree's root: python srcsplit.py --seed N --out DIR [ice_diag args]"""
import os
import sys

sys.path[:0] = [os.getcwd()]
from tools import ice_diag as D  # noqa: E402
from planet.tectonics import crust, earth  # noqa: E402

_gt, _th = earth.global_temperature, crust.thermostats


def thermostats(sim):
    r = _th(sim)
    sim._gain_now = r
    return r


def global_temperature(sim, growth, newc, rng):
    _gt(sim, growth, newc, rng)
    d = getattr(sim, "diag", None)
    if d is not None and getattr(d, "_pending", None) is not None:
        d._pending.update(src_newc=newc / sim.scale**2, src_arc=20.0 * float(growth.sum()) / sim.scale**2,
                          arc_gain=float(sim._gain_now[0]), shrink=float(sim._gain_now[1]))


crust.thermostats = thermostats
earth.global_temperature = global_temperature
if __name__ == "__main__":
    D.main()
