---
id: PW-303
title: test_parallel's worker-process tests fail now and then in a full pytest run (three different tests so far)
type: task
status: in-progress
parent: null
subsystem: infra
effort: s
impact: low
found_by: climate-ocean
blocked_by: []
relates: [PW-250]
refs: [tests/test_parallel.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
In 2 of 6 full `uv run pytest` runs on the climate-ocean branch, these two tests failed while the machine was busy (load 15–25, other agents running):
- `test_parallel.py::test_jobs_in_worker_processes_match_sequential`
- `test_parallel.py::test_zoom_built_twice_at_once_is_built_once`

The second one failed with `assert sum("already exists" in m for m in msgs) == 1` (got 0). The other 4 full runs passed. Run on their own, with test_api and test_store, both passed every time.

The second one looks like a race: both processes may build the zoom before either sees the other's lock or file. The first one wasn't diagnosed. It may share a cause, such as a shared tiny run or store directory, or a timeout. Neither touches the climate code.

Later (main merged at 2968db4, load ~4): `test_run_in_workers` failed once in a full run with an `AssertionError: assert [...` (not captured). Its asserts include the progress messages arriving "every message, before run returns", which looks like a race between the progress queue and the results. It passed when run on its own. Three tests have now flaked, so the progress/result hand-off in `planet/parallel.py` may deliver late under contention: check that `run` drains the progress queue before it returns. These look like real ordering races, not timeouts, so I didn't paper over them with longer waits.

## Updates
- 2026-10-15: Status todo -> in-progress. Infra batch agent started 2026-10-15 night.
- 2026-10-15: PW-312 (test_run_in_workers flaky, found by pw308) folded in: failed twice in a row in full runs on 2026-10-15, passes alone.
- 2026-10-15: Created from inbox draft draft-climate-ocean-parallel-tests-flaky-under-load.md (found by climate-ocean).
