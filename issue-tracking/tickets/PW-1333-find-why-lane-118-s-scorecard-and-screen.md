---
id: PW-1333
title: Find why lane 118's scorecard and screen gave different worlds for seed 1 (not the thread count)
type: task
status: todo
parent: null
milestone: null
subsystem: infra
effort: xs
impact: low
found_by: lane-124
blocked_by: []
relates: [PW-1324, PW-1297]
refs: [docs/review/speed/threads.md, "tools/scorecard.py::world_scores", "planet/parallel.py::set_default_threads", tests/test_thread_independence.py, docs/coordination.md]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: PW-1324 asked whether the thread count changes the world. It does not (docs/review/speed/threads.md: L5 up to 1 Gyr, L6 100 Myr, 1 to 16 threads, chunked or not, every snapshot field bit-identical). So the 33.5% vs 35.6% land difference lane 118 saw came from the two scripts differing. Likely suspects: `Params(run_end=myr)` left unset in the screen, a different commit, or OpenBLAS threads (changes outputs; pinned to 1 only when `planet` is imported before numpy). Low priority; worth doing only if a lane again has to compare "same seed" results across scripts. Cheap fix idea: a `tools/` helper that builds the standard Simulation so scripts cannot drift.
- [ ] diff the two setups and name the difference

## Updates
- 2026-11-02: Created from inbox draft draft-same-seed-two-scripts-differ.md (found by lane-124).
