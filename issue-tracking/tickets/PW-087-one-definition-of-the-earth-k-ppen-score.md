---
id: PW-087
title: One definition of the Earth Köppen score (code review B5)
type: task
status: done
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
- 2026-10-14: Status in-progress -> done. One function: tools/earth_data.koppen_agreement(grid, koppen, obs_koppen, elev) -> {group, exact, group_cells}: area-weighted share of model land outside Antarctica where Kottek has a land class (cell_areas moved to earth_data too). earth_check, scorecard (group_agree/exact_agree) and test_envelopes' 66% floor use it; definition stated in docs/overview.md. Measured at L6: the old definitions differed by only 0.06 points (cells 70.74%, area 70.69%; earth_check's mask was effectively identical), so no calibration conclusion changes. Scorecard's Earth part checked (70.7 / 38.4); the full 6-min scorecard wasn't run, nothing appended to scorecard.jsonl.
- 2026-10-14: Status todo -> in-progress. Started on branch quickwins.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Infrastructure.
