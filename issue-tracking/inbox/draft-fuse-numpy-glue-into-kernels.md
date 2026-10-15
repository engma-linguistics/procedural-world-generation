---
title: "Fuse the run's single-threaded numpy glue into parallel numba kernels (~45% of an L6/L7 run's wall time)"
type: task
status: todo
parent: PW-247
subsystem: infra
effort: l
impact: high
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249, PW-215]
refs: [planet/climate.py, planet/tectonics/simulation.py, planet/tectonics/mantle.py, planet/noise.py, planet/vegetation.py, planet/landform.py, docs/review/gpu/profile.md]
---

## Description
The biggest serial bucket of a run is not Python and not the kernels: it is numpy C code on the
main thread (py-spy --native of an L6 run: 46% of main-thread samples in numpy, 4% in the
interpreter itself). Per 100 Myr at 16 threads: ~18 s of an L6 run's ~38 s and ~75 s of an L7
run's ~189 s are Python-side (numpy + interpreter) time. ~34k planet function calls, ~22k numpy C
calls (np.where, reductions, `np.add.at`, reduceat, astype) and ~13k numpy Python-wrapper calls
(1.3k `np.clip` alone) per step, plus the operators cProfile can't see: many full-grid temporaries,
each a single-threaded pass over memory.

Where it sits (exclusive Python-side seconds per 100 Myr, L6 / L7; docs/review/gpu/profile.md "CPU headroom"):
tectonics 6.6 / 21.9 (`Simulation._world_view`, `mantle.gradient`, `mantle.eddies`, `noise.fbm`
in rifts, `motion.forces`), climate 3.9 / 19.9 (`month_temps`, `months`, `koppen`, `_geom`, the
season/wind fields), ocean 3.0 / 7.6, vegetation 1.3 / 8.3, erosion 2.1 / 12.9 (minus ~2 / 11 s of
priority_flood_to hidden inside `hydrology.route`), output 1.9 / 7.1 (snapshot: `landform.classify`, koppen).

Approach: take the top ~10 functions by exclusive time, write each as one `parallel=True` kernel
(one pass, no temporaries), keep outputs bit-identical where the arithmetic order allows (they are
elementwise mostly) and check goldens. Rough gain: fusing half of this glue at ~4-6x gives ~1.3x on a run.
- [ ] rank functions by exclusive time on an L7 run (the scratch timer harness in the profile report)
- [ ] port the top 5; before/after per stage; goldens unchanged or regenerated with a stated reason
