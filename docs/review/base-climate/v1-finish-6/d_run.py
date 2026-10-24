"""Option D measurement (not merged code): tools/ice_diag.run with the volcanic source's reference replaced, after
REF_FREEZE, by the source's running mean since 100 Myr (causal: past steps only, never frozen); the sink's reference
is kept frozen as in the model. usage (repo root): d_run.py SEED OUT_DIR k=v ..."""
import os
import sys

sys.path[:0] = [os.getcwd()]
from pathlib import Path  # noqa: E402

from planet.tectonics import earth  # noqa: E402
from tools import ice_diag  # noqa: E402

_orig = earth.global_temperature
acc = {}


def patched(sim, growth, newc, rng):
    st = acc.setdefault(id(sim), [0.0, 0.0])
    if sim.t >= earth.REF_FREEZE and sim.refs is not None and st[1] > 0:
        sim.refs[0] = st[0] / st[1]
    _orig(sim, growth, newc, rng)
    if sim.t >= 100 and sim.rates is not None:
        st[0] += float(sim.rates[0]) * sim.dt
        st[1] += sim.dt


earth.global_temperature = patched
seed, out = int(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
ice_diag.run(seed, 1000.0, 6, ice_diag.parse_sets(sys.argv[3:]), out)
