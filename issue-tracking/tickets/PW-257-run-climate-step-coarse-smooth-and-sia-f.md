---
id: PW-257
title: Run climate_step, _coarse_smooth and sia_flow in parallel on the CPU (zoom ~2x, time zoom ~1.4-2x)
type: task
status: in-progress
parent: PW-247
subsystem: climate
effort: s
impact: high
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249, PW-215]
refs: [planet/timezoom_kernels.py, planet/climate.py, planet/icemass.py, docs/review/gpu/profile.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Found while profiling for the GPU exploration (docs/review/gpu/profile.md). Two of the hottest numba
kernels are compiled serial (`@njit(cache=True)`, no `parallel=True`):

- `timezoom_kernels.climate_step` (the yearly snow/melt mass balance, called by `icemass.balance`
  9x per climate update in the run, 36x in a zoom's glaciers, once per step in the time zoom). It is
  independent per cell. Share of wall time at 16 threads: 12% of an L6 run, 14% of an L7 run,
  18-19% of a time zoom, **55% of a regional zoom** (2 km and 1 km/px).
  Measured: copying the body with `for i in prange(n)` gives **bit-identical** outputs and
  13x (L6, 10.1 -> 0.78 ms), 15.6x (L7, 51.6 -> 3.3 ms), 15x (1M px zoom, 260 -> 17 ms) at 16 threads
  (2.6 ms at 48 threads, L7). No reductions, so determinism (PW-215) is unaffected.
- `climate._coarse_smooth` (wide blurs via the coarse grid; 4% of an L6 run, **18% of an L6 time
  zoom** via `icemass.sheet_cover` / `smooth_big`). The fine -> coarse scatter is a race if
  parallelised as is, but the coarse -> fine interpolation (the last loop) is a pure gather, and the
  scatter can be turned into a gather with a precomputed inverse map (fixed order: deterministic).

- `timezoom_kernels.sia_flow` (the time zoom's ice flow, explicit sub-steps): serial, 4% of the
  200 kyr L6 time zoom of run 2abe69 but **28%** (9 s of 32 s) of the one of run 6a8269 at the same
  moment (more ice, more sub-steps). Each sub-step's passes are per cell; the `dV[j] +=` scatter
  becomes a gather over each cell's incoming fluxes (deterministic, though not bit-identical to the
  scatter's summation order), and `dmax` is a max (order-free).

Expected (Amdahl from the measured shares): zoom ~2.1x faster, time zoom ~1.4-1.6x, run ~1.15-1.2x.
This is the first thing to do before any GPU port: it is most of what a GPU would buy for these
two kernels (a GPU climate_step with its inputs copied per call is no faster than the prange CPU
version: 3.6 ms vs 3.3 ms at L7).
- [ ] `climate_step`: `parallel=True` + `prange` over cells; check outputs bit-identical (goldens unchanged)
- [ ] `_coarse_smooth`: parallel gather back to the fine grid; deterministic scatter (inverse map)
- [ ] `sia_flow`: parallel sub-step passes with a gather for the flux update
- [ ] before/after timings for an L6 run, a 2 km zoom and a 200 kyr time zoom

## Updates
- 2026-10-15: Status todo -> in-progress. Agent started (CPU speed wins, owner go-ahead 2026-10-15).
- 2026-10-15: Created from inbox draft draft-parallel-climate-step-and-coarse-smooth.md (found by gpu-explore (PW-249)).
