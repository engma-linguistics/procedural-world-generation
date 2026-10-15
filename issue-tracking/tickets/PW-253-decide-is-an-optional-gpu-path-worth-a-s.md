---
id: PW-253
title: "Decide: is an optional GPU path worth a second code path, and with which backend (numba-cuda vs CuPy)?"
type: task
status: needs-decision
parent: PW-244
subsystem: infra
effort: xs
impact: med
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249, PW-247, PW-215]
refs: [docs/review/gpu/profile.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
PW-249's profile (docs/review/gpu/profile.md, 16 numba threads, machine shared with other jobs):
the climate stages (atmosphere, ocean, ice mass balance, vegetation) are ~55% of an L6/L7 run and
of a time zoom; the rest (tectonics bookkeeping ~17-22%, priority flood / lakes / flow routing
~15%, output ~5%) is sequential or Python glue and won't move to a GPU. So Amdahl caps a GPU run
at ~2.2-2.3x even if the climate became free.

Prototypes on the RTX PRO 6000 (fp64, outputs within 1e-10 relative of the CPU, bit-repeatable
run to run on the device):
- `climate._rain` as one persistent cooperative kernel: L6 66 -> 8.5 ms (7.8x), L7 398 -> 35 ms
  (11.4x), L8 3.78 s -> 0.23 s (16x) including the copies in and out.
- `climate_step`: 7-15x on the device, but with its inputs copied per call it only matches the CPU
  once that kernel is `prange` (a CPU fix, separate draft), so it buys nothing alone.

Estimated end-to-end (after the CPU fixes, which alone give run ~1.2x, zoom ~2x, time zoom ~1.4-1.6x):
B) GPU `_rain` + the graph-stencil smoothers/relaxers, copying per call: run ~1.45x total, time
zoom ~2.1-2.3x, zoom no gain. C) all of `climate.compute` + ice + vegetation resident on the GPU
(a CuPy port of ~2000 lines of numpy glue plus the kernels): run ~1.85-2x.

Options:
- A. No GPU path. Do the CPU fixes (PW-247) and stop. Zero maintenance. Gets the zoom win entirely.
- B. Optional numba-cuda kernels for `_rain` and the stencils behind `planet[gpu]` (numba-cuda[cu13],
  ~1 GB of CUDA wheels), selected at runtime, CPU path stays the reference; separate GPU goldens
  with a tolerance check against CPU goldens. ~+1.2x on runs, ~+1.4x on time zooms beyond A; two
  copies of ~6 kernels to keep in sync. numba-cuda reuses the kernel bodies almost verbatim.
- C. Port the whole climate to CuPy (array API on the device) plus numba-cuda/RawKernel for the
  loops. Biggest gain (~2x runs) but effectively a second climate model to maintain; every climate
  ticket (PW-013 etc.) then touches two paths.
- D. Revisit at L8: the GPU lift grows with size (rain 16x at L8), so if L8 showcases become routine, B pays more.

Lean: **A now, D later** (B only if L8 runs or many time zooms become the main workload). The CPU
fixes give most of the cheap wins; the GPU's 1.2-1.4x extra on top doesn't justify a second code
path and its own goldens yet. If B goes ahead: numba-cuda over CuPy (closest to the existing
kernels, cooperative launches available), fp64 kept.

## Updates
- 2026-10-15: Created from inbox draft draft-gpu-backend-decision.md (found by gpu-explore (PW-249)).
