---
id: PW-035
title: "Time zoom: start-anchor cooling persists after the starting ice is gone"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: low
found_by: timezoom
blocked_by: []
relates: []
refs: [planet/timezoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
A fixed per-cell cooling keeps the starting ice stable; it persists after that ice has melted, so it's a
calibration crutch. Replace it with something tied to the ice actually present (or fade it out).

## Updates
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Glacial time zoom.
