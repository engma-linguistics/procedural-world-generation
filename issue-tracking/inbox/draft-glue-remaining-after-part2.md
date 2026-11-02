---
title: Numpy glue still left after PW-252 part 2 (ice rings, route/settle, forces algebra, overturning, is_land labelling)
type: task
status: todo
parent: null
milestone: v2
subsystem: infra
effort: l
impact: low
found_by: lane-118 (PW-1297, PW-1298)
blocked_by: []
relates: [PW-252, PW-1298]
refs: ["planet/tectonics/earth.py::ablation_zone", "planet/tectonics/earth.py::_ice_pass", "planet/tectonics/earth.py::sheet_surface", "planet/hydrology.py::route", "planet/hydrology.py::_settle", "planet/tectonics/motion.py::forces", "planet/ocean.py::overturning", "planet/icemass.py::balance", "planet/geo.py::_land_k", "planet/kernels.py::components", docs/review/speed/pw252.md, docs/review/speed/pw252_ab.py, docs/review/speed/pw252_rank.py, docs/review/gpu/scripts/run_sim.py]
---

## Description
In plain words: part 2 of the speed pass ported the exp users and the cheap rest of PW-1298 (see "Part 2" in docs/review/speed/pw252.md).
What is left is spread thin: at L6 no single python-side function is above 2 s of ~33 s, at L7 the python side is ~105 s of ~290 s.
Largest remaining by exclusive python seconds at L6: `hydrology.route` 2.1 (mostly nested sequential kernels), `ocean.overturning` 2.0,
`hydrology._settle` 1.35, `motion.forces` 0.5 now (torque/plate algebra), `icemass.balance` 0.6, `earth.ablation_zone` 0.7, `_ice_pass` 0.6,
`sheet_surface` 0.4. `geo.is_land` is now one sequential kernel (8 ms at L7; the breadth-first labelling dominates).
Not worth chasing for L6/L7 wall unless a sorting/ring-loop kernel with the same tie order is wanted anyway; `overturning` is the one
unexamined item. Daniel ruled that L8/L9 speed is not being chased, so this is low priority.
- [ ] profile `ocean.overturning` and port if it is numpy glue
- [ ] ice ring loops as per-sheet sequential kernels with the same tie order (only if the ice pass shows up in a profile)
