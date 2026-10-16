---
title: tests/test_parallel.py::test_run_in_workers is flaky (failed twice in a row in full pytest runs, passes alone)
type: task
status: todo
parent: null
subsystem: infra
effort: s
impact: low
found_by: pw308
blocked_by: []
relates: []
refs: [tests/test_parallel.py, planet/parallel.py]
---

## Description
On the PW-308 branch after merging main (2026-10-15, load ~8-11), `test_run_in_workers` failed in a full
`uv run pytest -q` and again in `pytest tests/test_parallel.py`, with "AssertionError: assert [...". It then passed
alone and in three more runs of the module. The change under test only touched the climate, so this is likely a
race: either the progress messages (`seen`) arrive after `P.run` returns, or a worker's environment
(threads / blas / root) isn't what the test expects. Capture the failing assertion's values (e.g. run the
module in a loop until it fails) and make `parallel.run` drain every progress message before it returns.
