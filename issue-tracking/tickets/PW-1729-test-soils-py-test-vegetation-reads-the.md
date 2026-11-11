---
id: PW-1729
title: test_soils.py::test_vegetation_reads_the_soil fails in the full not-slow run under load, passes alone
type: task
status: todo
parent: null
milestone: v1.0
subsystem: infra
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: []
refs: [tests/test_soils.py]
created: 2026-11-11
updated: 2026-11-11
---

## Description
**In plain words.** One soils test fails now and then when the whole quick test run is busy, and passes when run on its
own. A test that fails at random teaches everyone to ignore failures, and the v1.0 tag needs a clean full run.

Seen twice on 11-11: lane 300 (load 53 at start) and lane 308 (`-n 2`, 16G cap); both passed alone, and it passed in the
coordinator's area run after the lane 308 merge. Likely a timing, ordering or shared-state dependence (a cache written by
another test, or numba compile under load).
- [ ] cause found (order dependence, shared cache, or timeout)
- [ ] test fixed to be deterministic; 5 full not-slow runs in a row with no failure

## Updates
- 2026-11-11: Created from inbox draft draft-soils-test-flaky-under-load.md (found by coordinator).
