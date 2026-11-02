---
title: Numpy glue still left after PW-252 (ice pass, route/settle, forces, gradient, is_land, face_winds)
type: task
status: todo
parent: null
milestone: v2
subsystem: infra
effort: l
impact: med
found_by: lane-114 (PW-252)
blocked_by: []
relates: [PW-252]
refs: [planet/tectonics/earth.py::ablation_zone, planet/tectonics/earth.py::_ice_pass, planet/tectonics/earth.py::sheet_surface, planet/hydrology.py::route, planet/hydrology.py::_settle, planet/tectonics/motion.py::forces, planet/tectonics/mantle.py::gradient, planet/geo.py::is_land, planet/climate.py::face_winds, docs/review/speed/pw252.md]
---

## Description
After PW-252 the python-side exclusive time at L7 is 108 s per 100 Myr (was 146). The functions below were
not ported (ranking and reasons in docs/review/speed/pw252.md):
- `earth.ablation_zone` 3.7 s, `_ice_pass` 2.7 s, `sheet_surface` 2.1 s: lexsort/bincount/maximum.at ring loops; need a per-sheet sequential kernel with the same tie order.
- `hydrology.route` 7.9 s (mostly the nested `priority_flood_to`/`accumulate_lakes` kernels, not glue) and `_settle` 4.2 s: sequential; see draft-lakes-settle-passes.
- `motion.forces` 2.2 s and `mantle.gradient` 2.1 s: `np.add.at` / `np.bincount` scatter-adds whose summation order is the edge order; a parallel version changes summation order (golden change) unless built as per-cell gathers in the same order.
- `geo.is_land` 2.5 s (1148 calls), `climate.face_winds` 1.6 s, `climate.open_water_evap` 1.6 s, `ocean.ice_growth` 1.9 s, `icemass.balance` 1.9 s.
Fusing these is another ~15 s at L7 (6%) if the order constraints hold.
