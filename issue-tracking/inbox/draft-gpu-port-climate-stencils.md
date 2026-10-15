---
title: "If the GPU route is chosen: port climate._rain and the graph-stencil kernels to numba-cuda behind an optional extra"
type: story
status: todo
parent: PW-244
subsystem: climate
effort: l
impact: med
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249, PW-215]
refs: [planet/climate.py, planet/ocean.py, docs/review/gpu/profile.md]
---

## Description
Only do this if the backend decision (draft-gpu-backend-decision) picks option B. The stage worth
porting (go per docs/review/gpu/profile.md): the climate's iterative graph kernels, which are
data-parallel over cells and iterate hundreds of times on data that can stay on the device:
`climate._rain` (5-9% of runs and time zooms; prototype 11.4x at L7, 16x at L8 with copies),
`climate._smooth`, `climate._relax_along`, `ocean._relax_from` (together ~8-12%), and the coarse
grid blur `_coarse_smooth` (after it is made parallel on the CPU). No-go stages: priority flood,
lakes, flow accumulation, `_stommel` (Gauss-Seidel in a fixed east-to-west order), plate
bookkeeping, numpy glue.

Lessons from the prototype (scratch scripts are described in the profile report):
- Launch overhead dominates at L6/L7 when each iteration is a separate kernel launch (L7 _rain:
  ~1200 launches, 50 ms; one cooperative kernel with `grid.sync()` between phases: 29 ms).
- fp64 throughput is not the limit for these kernels (fp32 was no faster), so keep fp64.
- The CPU `_rain`'s one serial sum becomes a fixed-order block tree on the GPU: bit-repeatable on
  one device/grid size, not bit-identical to the CPU (rel. differences ~1e-10).
- [ ] `planet[gpu]` extra (numba-cuda[cu13]); `PLANET_GPU=1` or auto-detect; CPU stays the default/reference
- [ ] GPU goldens of their own + a test comparing GPU vs CPU fields within tolerance
- [ ] run-to-run determinism on the GPU (PW-215) checked in tests
