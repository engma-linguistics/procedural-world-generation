"""PW-950 experiment: water-loaded isostasy for submerged continental crust. Usage: wl.py LEVEL SEED MYR [water]
Prints every 50 Myr: shelf % of ocean, median submerged continent (m), land %, cont %, thickness, sea level.
With 'water': every continental cell whose air-loaded elevation is below sea level sinks by
rho_m / (rho_m - rho_w) of it (water fills the space, not air)."""
import sys
import planet  # noqa
import numpy as np
from planet.grid import build_grid
from planet.tectonics import isostasy, earth, simulation, volcanism
from planet.tectonics.params import Params

level, seed, end = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
if len(sys.argv) > 4 and sys.argv[4] == "water":
    base = isostasy.elevation
    F = isostasy.RHO_MANTLE / (isostasy.RHO_MANTLE - isostasy.RHO_WATER)

    def elevation(thick, age, cont, rock, swell, sed):
        e = base(thick, age, cont, rock, swell, sed)
        return np.where(cont & (e < 0), e * F, e)
    for m in (isostasy, earth, simulation, volcanism):
        m.elevation = elevation
    print("water-loaded, factor", round(F, 3), flush=True)
sim = simulation.Simulation(build_grid(level), seed, Params(run_end=end), 2.0)
for t in range(50, int(end) + 1, 50):
    sim.run(float(t))
    e, cont = sim.w_elev, sim.w_cont
    sea = e <= 0
    sub = sea & cont
    print(f"t={t} shelf={100 * (e[sea] > -200).mean():.2f} sub_med={np.median(e[sub]):.0f} land={100 * (e > 0).mean():.1f} "
          f"cont={100 * cont.mean():.1f} thick={sim.w_thick[cont].mean():.2f} sea_level={sim.sea_level:.0f}", flush=True)
