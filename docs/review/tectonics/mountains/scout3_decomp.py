"""PW-1446 (b) scout 190: what lifts the cap cells above Airy? usage: scout3_decomp.py RUN_DIR T"""
import sys
from pathlib import Path
import numpy as np
from planet import store as S
from planet.grid import build_grid
from planet.tectonics import Params
from planet.tectonics.simulation import Simulation
from planet.tectonics import isostasy as I

run_dir, t = Path(sys.argv[1]), float(sys.argv[2])
run = S.read_header(run_dir / "run.json"); m = run["meta"]
g = build_grid(m["level"])
sim = Simulation.from_state(g, m["seed"], Params(**{k: v for k, v in m["params"].items() if k in Params.__dataclass_fields__}), m["dt"], S.load_checkpoint(run_dir, t, g))
th, cont, sed = sim.w_thick, sim.w_cont, I.sediment_km(sim.w_cover, sim.w_extra)
airy = np.where(cont, 250 + I.ISO_LAND * (th - I.CONT_KM), np.nan)
lift = I.sediment_lift(cont, sim.w_rock, sed)
sw, dyn, sl = sim.swell, sim.dyn, sim.sea_level
E = sim.w_elev
print(f"t {sim.t} sea level {sl:.0f}; check elev = airy+lift+swell+dyn-sl: max err "
      f"{np.nanmax(np.abs(np.where(cont, airy + lift + sw + dyn - sl - E, 0))):.2f} m")
for k in (5000, 6000, 7000):
    print(f"cells > {k} m: {(E > k).sum()}")
print(f"highest {E.max():.0f} m")
s = E > 6000
print(f"cells > 6 km: n {s.sum()}; thick median {np.median(th[s]):.1f}, at cap (>=79.5) {(th[s] >= 79.5).mean():.0%}")
for name, v in (("sed km", sed), ("sed lift m", lift), ("swell m", sw), ("dyn m", dyn), ("excess m", E - airy)):
    print(f"  {name:10s} p10 {np.percentile(v[s],10):7.1f} med {np.median(v[s]):7.1f} p90 {np.percentile(v[s],90):7.1f} max {v[s].max():7.1f}")
print("top 12: cell, elev, thick, sed, lift, swell, dyn, -sl")
for c in np.argsort(-E)[:12]:
    print(f"  {c:6d} {E[c]:6.0f} {th[c]:5.1f} {sed[c]:5.1f} {lift[c]:6.0f} {sw[c]:6.0f} {dyn[c]:6.0f} {-sl:5.0f}")
cap = cont & (th >= 79.5)
print(f"all cap cells {cap.sum()}: sed med {np.median(sed[cap]):.1f} km, lift med {np.median(lift[cap]):.0f}, swell med {np.median(sw[cap]):.0f}")
print(f"all continent: sed med {np.median(sed[cont]):.1f} p90 {np.percentile(sed[cont],90):.1f} km; "
      f"thick > 70 km: sed med {np.median(sed[cont & (th > 70)]):.1f}")
