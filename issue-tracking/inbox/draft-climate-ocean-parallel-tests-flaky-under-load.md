---
title: test_parallel's two worker-process tests fail now and then in a full pytest run under load
type: task
status: todo
parent: null
subsystem: infra
effort: s
impact: low
found_by: climate-ocean
blocked_by: []
relates: [PW-250]
refs: [tests/test_parallel.py]
---

## Description
In 2 of 6 full `uv run pytest` runs on the climate-ocean branch, these two tests failed while the machine was busy (load 15–25, other agents running):
- `test_parallel.py::test_jobs_in_worker_processes_match_sequential`
- `test_parallel.py::test_zoom_built_twice_at_once_is_built_once`

The second one failed with `assert sum("already exists" in m for m in msgs) == 1` (got 0). The other 4 full runs passed. Run on their own, with test_api and test_store, both passed every time.

The second one looks like a race: both processes may build the zoom before either sees the other's lock or file. The first one wasn't diagnosed. It may share a cause, such as a shared tiny run or store directory, or a timeout. Neither touches the climate code.
