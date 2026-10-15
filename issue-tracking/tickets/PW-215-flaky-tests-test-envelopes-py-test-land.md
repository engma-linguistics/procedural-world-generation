---
id: PW-215
title: "Flaky: tests/test_envelopes.py::test_land_and_crust[1] failed once in the full suite after the veg merge, passes alone (3/3)"
type: task
status: in-progress
parent: null
subsystem: infra
effort: xs
impact: low
found_by: coordinator
blocked_by: []
relates: []
refs: [tests/test_invariants.py, tests/test_store.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Seen 2026-10-15 in the full suite right after merging veg (191 passed, 1 failed); re-runs of the file and the test pass. Possibly numba parallel nondeterminism or an order dependence between tests. Find out which, then make the test deterministic or loosen its bound.

## Updates
- 2026-10-15: Merged inbox draft draft-determinism-tests-flaky-under-load.md ("Determinism tests fail together on unmodified main under load: test_deterministic, checkpoint resume, simulate replay", found by vegzoom).
  On 2026-10-15 (laptop shared by four agents), `uv run pytest -q tests/test_invariants.py tests/test_store.py` on a clean checkout of main (5411877) failed 3 tests: `test_invariants.py::test_deterministic` (w_elev differs), `test_store.py::test_checkpoint_resume_bit_identical` (precip, temp, w_lith, budget hashes differ) and `test_store.py::test_simulate_checkpoints_and_replay`. Each passes when run alone, and `test_store.py::test_run_lakes` failed once in a full run and passed alone. `tests/test_golden.py::test_golden_sim` (alone, 4 s) failed then passed on the very same code twice in a row at load average ~15 (every output hash differed: budget, flow, precip, temp, w_elev...). Same family as PW-215: two runs of the same simulation in one process diverging, likely from a numba parallel reduction whose result depends on the thread schedule (load), or from state shared between tests (a cache keyed too loosely). These tests are what show refactors don't change results, so a flaky one hides real changes.
  - [ ] find the kernel or cache that makes two identical runs differ (run test_deterministic in a loop under `NUMBA_NUM_THREADS=8` with a CPU hog beside it)
  - [ ] make it deterministic (fixed-order reduction) or document the tolerance
- 2026-10-15: Status todo -> in-progress. Overnight agent, worktree smalls (with other small tickets).
- 2026-10-15: Created.
