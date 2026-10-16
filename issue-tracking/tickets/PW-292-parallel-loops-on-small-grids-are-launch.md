---
id: PW-292
title: Parallel loops on small grids are launch-bound (sia_flow sub-steps, coarse blurs, _smooth at L6)
type: task
status: wontdo
parent: PW-247
subsystem: infra
effort: s
impact: low
found_by: worktree-agent-abb4e9e7307244dd3 (PW-256/257)
blocked_by: []
relates: [PW-257, PW-215]
refs: [planet/timezoom_kernels.py, planet/climate.py, planet/ocean.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Found while doing PW-257 (Threadripper 9960X, TBB layer, 16 numba threads, load ~6-10). Starting a
`prange` loop costs ~25-40 us at 16 threads, so loops over a few thousand cells gain little or lose:

| One blur step (`_smooth` body), us | serial | 1 thr | 2 | 4 | 8 | 16 |
|---|---|---|---|---|---|---|
| L3 (642 cells) | 3 | 3 | 8 | 4 | 14 | 28 |
| L4 (2.6k) | 13 | 11 | 18 | 11 | 19 | 33 |
| L5 (10k) | 49 | 42 | 38 | 30 | 32 | 40 |
| L6 (41k) | 200 | 170 | 88 | 71 | 64 | 65 |
| L7 (164k) | 942 | 898 | 434 | 319 | 181 | 159 |

What's done: `climate._coarse_smooth`'s blur on the coarse grid now runs on one thread per ~2500 coarse
cells (`BLUR_CELLS_PER_THREAD`, set from Python around the call; bit-identical). Calling
`numba.set_num_threads` *inside* a jitted function works but stops numba caching it ("dynamic
globals"), which costs a compile in every process, so do it from Python.

Still launch-bound:
- `timezoom_kernels.sia_flow`: 3 parallel loops per explicit sub-step; ~190 us per sub-step for 4.2k
  active cells at L6 (old serial kernel: ~440 us; new kernel on one thread ~520 us). It is still
  ~23% of an L6 100 kyr time zoom (2.7 s of 11.5 s, 200 calls). Ideas: pick the thread count from the
  active set's size the same way (from timezoom.py, around the call); or do several sub-steps per
  parallel region when the CFL step is known ahead (it isn't: dt depends on the step's max D, so a
  red-black/two-colour order or a fixed dt per call would be needed; output change).
- `climate._smooth` at L6 with 16 threads is no faster than at 8; `_relax_along`, `_rain` (doesn't
  scale past 16, PW-249) likely the same. A small per-kernel thread table measured at L6/L7 could save a
  few % of a run's climate; also frees cores for concurrent jobs (TBB workers spin, PW-250).
- [ ] sia_flow threads by active-set size (bit-identical; measure an L6 and L7 time zoom)
- [ ] measure _smooth/_relax_along/_rain per level and thread count; cap where it helps

## Updates
- 2026-10-15: Status in-progress -> wontdo. Measured, skipped: at 8 threads every run kernel is already fastest; a thread cap saves <0.1% of an L6 100 Myr run. sia_flow (time zoom) not measured.
- 2026-10-15: Infra batch: measured, skipped for runs. L6, NUMBA_NUM_THREADS=8, kernels replayed on args recorded in a run (ms per call at 1/2/4/8 threads): _smooth 2.50/1.50/0.99/0.94 (~1650 calls per 100 Myr, coarse blurs included), _relax_along 19.6/12.3/7.5/6.0 (~200), _rain 351/174/105/69 (~25), ocean._carry 2.7 at any count (serial). 8 threads is the fastest for every one, so a per-kernel cap saves ~0 s of a 27.5 s L6 100 Myr run (< 0.1%, well under the 3% bar). The sia_flow item (time zoom, not the run) was not measured.
- 2026-10-15: Status todo -> in-progress. Infra batch agent started 2026-10-15 night.
- 2026-10-15: Created from inbox draft draft-small-parallel-loops-launch-bound.md (found by worktree-agent-abb4e9e7307244dd3 (PW-256/257)).
