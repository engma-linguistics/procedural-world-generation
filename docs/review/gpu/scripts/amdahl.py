"""Amdahl estimates from a timer profile: per-kernel / per-stage speedup factors applied to the
measured times. python amdahl.py prof.json LEVEL_FACTOR_KEY"""
import json, sys
from collections import defaultdict
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from stages import load, stage_of

fn, key = sys.argv[1], sys.argv[2]
d, rows, excl = load(fn)
wall = d["wall"]
# measured kernel lifts (prototypes): climate_step serial -> prange16; _rain CPU16 -> GPU (with transfers)
CS_PRANGE = {"L6": 13.0, "L7": 15.6, "zoom": 15.0}[key]
RAIN_GPU = {"L6": 7.8, "L7": 11.4, "zoom": 1.0}[key]
SMOOTH_GPU = 4.0  # estimate (graph stencils like _rain, but fewer iterations per call and a copy per call)
COARSE_CPU = 3.0  # estimate: _coarse_smooth's interpolation back is a parallel gather
CLIMATE_DEVICE = 8.0  # estimate for climate/ocean/ice/vegetation ported whole (data resident)
TRANSFER_PER_UPDATE = {"L6": 0.006, "L7": 0.02, "zoom": 0.05}[key]  # s per climate update, both ways


def kern(name):
    return sum(rows[p][0] for p in rows if p[-1] == name)


def excl_of(name, under=None):
    return sum(e for p, e in excl.items() if p[-1] == name and (under is None or under in p))


T = {k: kern("K:" + k) for k in ("timezoom_kernels.climate_step", "climate._rain", "climate._smooth",
                                  "climate._coarse_smooth", "climate._relax_along", "ocean._relax_from",
                                  "climate._stommel")}
thrash = excl_of("climate._geom") + excl_of("ocean.cell_area_km2") + excl_of("grid.build_grid", "ocean._coarse")
updates = sum(rows[p][1] for p in rows if p[-1] in ("climate.compute",) and "climate.compute" not in p[:-1])
cs, rain = T["timezoom_kernels.climate_step"], T["climate._rain"]
smooth = T["climate._smooth"] + T["climate._relax_along"] + T["ocean._relax_from"]
coarse = T["climate._coarse_smooth"]

save_a = cs * (1 - 1 / CS_PRANGE) + coarse * (1 - 1 / COARSE_CPU) + 0.9 * thrash
a = wall - save_a
save_b = rain * (1 - 1 / RAIN_GPU) + (smooth + coarse / COARSE_CPU) * (1 - 1 / SMOOTH_GPU)
b = a - save_b
# C: everything in the climate stages on the device (after A), stommel kept on the CPU
st = defaultdict(float)
for p, e in excl.items():
    st[stage_of(p)] += e
clim = sum(st[s] for s in ("climate (atmosphere)", "ocean", "ice", "vegetation"))
clim_a = clim - save_a + 0.9 * thrash * 0  # (A's savings are all inside these stages)
c = (wall - clim) + (clim_a - T["climate._stommel"]) / CLIMATE_DEVICE + T["climate._stommel"] \
    + updates * TRANSFER_PER_UPDATE
inf = wall - clim
print(f"{fn}: wall {wall:.1f}s; climate_step {100*cs/wall:.1f}%, rain {100*rain/wall:.1f}%, stencils "
      f"{100*smooth/wall:.1f}%, coarse_smooth {100*coarse/wall:.1f}%, cache thrash {100*thrash/wall:.1f}%, "
      f"stommel {100*T['climate._stommel']/wall:.1f}%, climate stages {100*clim/wall:.1f}%, updates {updates}")
for nm, v in (("A  CPU fixes (prange climate_step, parallel coarse_smooth, cache)", a),
              ("B  A + GPU rain and graph stencils, copy per call", b),
              ("C  A + climate/ocean/ice/vegetation resident on the GPU", c),
              ("   bound: climate stages free", inf)):
    print(f"  {nm:<62s} {v:7.1f}s  x{wall / v:.2f}")
