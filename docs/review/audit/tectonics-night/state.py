"""Global state of a run at a few times (temperature, land, ice, sea level)."""
import sys

sys.path.insert(0, sys.argv[1])
import planet  # noqa: E402,F401
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402

level, seed = int(sys.argv[2]), int(sys.argv[3])
sim = Simulation(build_grid(level), seed, Params(flora_end=320.0), 2.0)
for t in (300, 340, 380, 400):
    sim.run(t)
    st = sim.stats()
    print(t, {k: st.get(k) for k in ("global_temp_c", "land_pct", "ice_pct", "sea_level_m", "plates")}, flush=True)
