---
id: PW-249
title: Explore an optional GPU backend (RTX PRO 6000, 96 GB) for the heaviest kernels
type: task
status: done
parent: PW-244
subsystem: infra
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: [PW-247, PW-215]
refs: [planet/kernels.py, planet/climate.py, planet/zoom_kernels.py, planet/timezoom_kernels.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Owner (2026-10-15): the new machine has an NVIDIA RTX PRO 6000 Blackwell (96 GB, CUDA 13.2). A GPU path is welcome only as an **optional** accelerator: the CPU (numba) path stays the default and the reference, so the code still ships to machines without a GPU.

Exploration, not implementation. Use the PW-247 profile to pick the 2-3 hottest stages (likely climate, the erosion/flow-routing kernels, zoom terrain synthesis at 1 km, the time-zoom ice loop) and, for each:
- Is it data-parallel enough to win on a GPU at L7 (164k cells) and L8 (655k)? Or do sequential parts (flow routing order, priority-flood lake filling, plate bookkeeping) and host-device transfers each step eat the gain? Zooms (millions of px) and L8 are the likeliest wins.
- Which route: CuPy (numpy-like, least code), numba-cuda (closest to the existing kernels), JAX, or warp. Weigh install weight (an optional `uv` extra, e.g. `procgen-world[gpu]`), Linux/CUDA-only vs portable, and maintenance cost of two code paths.
- Determinism and goldens: GPU float reductions and the math library differ from the CPU, so outputs won't be bit-identical to the CPU path. Decide whether the GPU path needs its own goldens plus tolerance checks against the CPU (PW-215 determinism must still hold run-to-run on one device).
- A prototype of one kernel with a timing comparison against the tuned CPU version at 48 threads (after PW-247, so the comparison is fair).

Output: a short report under docs/review/gpu/ with a go/no-go per stage, and inbox drafts for the stages worth porting. Raise the choice of backend (and whether it's worth a second code path at all) as a needs-decision ticket.

## Updates
- 2026-10-15: Status todo -> done. Exploration done: docs/review/gpu/profile.md (merged 459faff); decision in PW-253 (no GPU path).
- 2026-10-15: Created from inbox draft draft-gpu-backend-exploration.md (found by daniel).
