---
id: PW-252
title: Fuse the run's single-threaded numpy glue into parallel numba kernels (~45% of an L6/L7 run's wall time)
type: task
status: todo
parent: PW-247
subsystem: infra
effort: l
impact: high
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249, PW-215]
refs: [planet/climate.py, planet/tectonics/simulation.py, planet/tectonics/mantle.py, planet/noise.py, planet/vegetation.py, planet/landform.py, docs/review/gpu/profile.md, docs/review/gpu/scripts/]
created: 2026-10-15
updated: 2026-10-15
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

## Updates
- 2026-10-15: Merged inbox draft draft-speed-shares-after-pw257.md ("Where the time goes after PW-256/257 (for PW-252, PW-255, PW-259): zooms now mostly numpy glue", found by worktree-agent-abb4e9e7307244dd3 (PW-256/257)).
  Meant to be merged into PW-252 (`board.py intake --merge-into PW-252`), with a pointer from PW-255/259.
  Re-profiled with docs/review/gpu/scripts (`run_misc.py`, `run_sim.py`, `stages.py`; 16 threads, load
  ~7-11) after climate_step / sia_flow / _coarse_smooth went parallel and the ocean's coarse grid stopped
  evicting `_geom` (PW-256/257):
  
  - **Zoom L6 1000 km @ 2 km** (5.1 s in-process): `climate_step` is down to 8% (11.5 ms/call x 36);
    89% is now outside the stage roots: `flood_d8` 11% (sequential, PW-255 territory), vegetation
    `_potential` 7% + `_step` 4%, `zoom_landforms._axis_tensor` 6% (330 numpy calls),
    `zoom_vegetation.compute` 5%, `world.load` 4%, `zoom.build` 4%, `_radiation` 3.5%, satellite 4%.
    A zoom is now a numpy-glue problem: worth adding the zoom's `_axis_tensor`, `zoom_vegetation` and
    `satellite._mix` to PW-252's list.
  - **Time zoom L6 100 kyr** (11.5 s): `sia_flow` 23% (launch-bound, see
    draft-small-parallel-loops-launch-bound), `_coarse_smooth` 14% (611 calls, ~2.6 ms; its coarse blur
    of 22-66 steps dominates, not the scatter/gather), `_rain` 7.5%, `_smooth` 5.5%, `_stommel` 4%
    (PW-259), `_relax_along` 4%, `month_temps` 4%; `climate_step` 1.9%.
  - **Run L6 100 Myr** (34 s with timers): climate 31.5%, tectonics 23%, lakes 8.5%, ocean 7%,
    erosion/routing 7%, vegetation 7%, output 6%, setup 4%; ice 2.4% (was ~14%). Top kernels `_rain`
    5.6%, `_coarse_smooth` 4.7%, `_smooth` 4.2%, `lakes` 3.4%, `_stommel` 3.2%; top glue
    `hydrology.route` 5.3% (nested priority_flood_to/accumulate), `noise.fbm` 3.9%, `_world_view` 3.5%,
    `month_temps` 3.3%, `mantle.basis` 2.0%.
  - `climate._geom` is now computed 3 times per process (main grid + 2 coarse levels) instead of once
    per climate update (L6 time zoom: 3136 calls, 0.11 s total).
- 2026-10-15: Created from inbox draft draft-fuse-numpy-glue-into-kernels.md (found by gpu-explore (PW-249)).
