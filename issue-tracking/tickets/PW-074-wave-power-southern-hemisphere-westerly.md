---
id: PW-074
title: "Wave power: Southern Hemisphere westerly coasts too weak, N Atlantic too strong"
type: task
status: todo
parent: null
subsystem: coast
effort: m
impact: med
found_by: deltas
blocked_by: []
relates: []
refs: [planet/coast.py, planet/climate.py, tools/coast_check.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Southern Hemisphere westerly coasts get ~half their observed wave power; the N Atlantic and NE Pacific
get ~1.5× too much. The storm tracks come mostly from land–sea contrast, so they're weak over the
Southern Ocean. Fix in the storm-track/wind model rather than by refitting constants.

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Coast.
