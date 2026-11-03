---
title: Show the numbers a world drew in the peoples workbench
type: task
status: todo
parent: null
milestone: v2
subsystem: viewer
effort: xs
impact: low
found_by: lane 145
blocked_by: []
relates: [PW-1383]
refs: [viewer/lineages.html, planet/lineages/output.py, planet/lineages/ranges.py]
---

## Description
In plain words: the peoples workbench now has a "draw sourced numbers from their published ranges" checkbox (meta.draw_ranges), and a
run saves the numbers it drew in run.json under meta.range_draws (name -> value; the ranges are in ranges.py). The workbench does not
show them yet: list them beside the density ladder table (viewer/lineages.html, SCHEMA.ladder) with each one's range. The "New planet"
form is for worlds, not peoples, so it needs nothing.
