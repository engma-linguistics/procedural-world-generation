"""Record the CO2 source's parts per step: heat, ridge cells, arc nominal growth, trench cells, land."""
import sys, json
W = sys.argv[1]; sys.path.insert(0, W)
import planet  # noqa
from planet.grid import build_grid
from planet.tectonics import Params, Simulation
from planet.tectonics import earth
seed, myr, level, out = int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
sets = {}
for kv in sys.argv[6:]:
    k, v = kv.split("="); sets[k] = float(v)
sets = {"flora_end": myr, **sets}
sim = Simulation(build_grid(level), seed, Params(**sets), 2.0)
rows = []
orig = earth.global_temperature


def gt(s, growth, newc, rng):
    orig(s, growth, newc, rng)
    sc2 = s.scale ** 2
    rows.append([round(s.t, 2), round(s.heat(), 4), newc / sc2, 20 * float(growth.sum()) / sc2,
                 int((growth > 0).sum()), float(s.land().mean()), float(s.w_cont.mean()),
                 float(s.rates[1]) if s.rates is not None else 0.0, round(float(s.dT), 2)])


earth.global_temperature = gt
sim.run(myr, lambda s: None)
json.dump({"cols": ["t", "heat", "ridge", "arc", "arc_cells", "land", "cont", "sink", "dT"], "rows": rows}, open(out, "w"))
