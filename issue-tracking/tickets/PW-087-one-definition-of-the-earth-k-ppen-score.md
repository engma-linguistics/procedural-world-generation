---
id: PW-087
title: One definition of the Earth Köppen score (code review B5)
type: task
status: todo
parent: null
subsystem: infra
effort: s
impact: med
found_by: cleanup
blocked_by: []
relates: []
refs: [tests/test_envelopes.py, tools/scorecard.py, tools/earth_check.py, docs/review/code_review_2026-10-13.md]
created: 2026-10-14
updated: 2026-10-14
---

## Description
There are three "Earth Köppen group agreement" numbers: the test and scorecard count cells, unweighted,
lat > −60; `earth_check` is area-weighted and excludes cells with no observation. Calibration decisions
rest on a number with an unclear definition. Use one function everywhere.

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Infrastructure.
