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
refs: []
created: 2026-10-15
updated: 2026-10-15
---

## Description
Seen 2026-10-15 in the full suite right after merging veg (191 passed, 1 failed); re-runs of the file and the test pass. Possibly numba parallel nondeterminism or an order dependence between tests. Find out which, then make the test deterministic or loosen its bound.

## Updates
- 2026-10-15: Status todo -> in-progress. Overnight agent, worktree smalls (with other small tickets).
- 2026-10-15: Created.
