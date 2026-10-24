"""thermostat-1024's srcsplit.py (the source's ridge / arc parts), plus what the weathering supply rides on, logged
per step (read only: the run is unchanged): land bed height mean / p90 (m), continental crust share, land runoff
mean (mm/yr), the erosion on bare land per unit land area (removed, km per step), and the mantle heat. Run from the
repository root: uv run python docs/review/base-climate/v1-finish-2/relief.py --seed N --out DIR [ice_diag args]"""
import os
import sys

sys.path[:0] = [os.getcwd(), os.path.join(os.getcwd(), "docs/review/base-climate/thermostat-1024")]
import srcsplit  # noqa: E402  (first: it imports planet, whose thread caps keep BLAS at one thread; patches
#                                  earth.global_temperature / crust.thermostats)
import numpy as np  # noqa: E402
from planet.tectonics import earth  # noqa: E402
from tools import ice_diag as D  # noqa: E402

_gt = earth.global_temperature


def global_temperature(sim, growth, newc, rng):
    _gt(sim, growth, newc, rng)
    d = getattr(sim, "diag", None)
    if d is not None and getattr(d, "_pending", None) is not None:
        land = sim.land()
        bed = sim.bed()
        bare = land & ~(sim.ice > 0)
        ro = sim.runoff if sim.runoff is not None else np.zeros_like(bed)
        d._pending.update(
            bed_mean=float(bed[land].mean()), bed_p90=float(np.percentile(bed[land], 90)),
            cont=float(np.mean(sim.w_cont)), runoff=float(ro[land].mean()),
            ero_bare=float(sim.removed[bare].sum() / max(land.sum(), 1)), bare=float(bare.mean()),
            heat=float(sim.heat()))


earth.global_temperature = global_temperature
if __name__ == "__main__":
    D.main()
