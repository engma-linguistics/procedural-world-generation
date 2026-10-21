---
id: PW-250
title: "Linux box uses numba's TBB threading layer: relax the API's one-computation lock (PW-084) and pin the layer"
type: task
status: done
parent: PW-247
milestone: v2
subsystem: infra
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-084, PW-215]
refs: [planet/api.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
On the new Ubuntu machine `numba.threading_layer()` is `tbb` (the Mac used `workqueue`, which aborts when two parallel kernels run at once; that is why `api.COMPUTE` serialises every computation, PW-084). TBB supports concurrent parallel kernels from several threads.

Measured 2026-10-15: the L4 60 Myr golden digest is bit-identical under tbb (twice), workqueue and NUMBA_NUM_THREADS=1, so determinism (PW-215) holds regardless of layer and thread count.

To do: make the layer explicit (`NUMBA_THREADING_LAYER` / `numba.config.THREADING_LAYER = "safe"` or `"tbb"` when available, falling back to the lock under workqueue), let the server run more than one compute job at a time when the layer allows it (a small pool, not unbounded: each job already uses all cores), and add `tbb` to the dependencies if it isn't reliably present (it appears to come from the system or a wheel here; check `uv pip list` / `ldconfig -p | grep tbb`). Test: two concurrent zoom builds through the API give the same outputs as sequential ones.

## Updates
- 2026-10-15: Status todo -> done. Done: process-level concurrency merged (de8e016, merge on main 2026-10-15).
- 2026-10-15: Created from inbox draft draft-tbb-concurrent-compute.md (found by coordinator).
