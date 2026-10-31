---
title: planet simulate prints no progress when stdout is redirected
type: task
status: todo
parent: null
subsystem: infra
effort: xs
impact: low
found_by: lane-86b
blocked_by: []
relates: [PW-535]
refs: [planet/make.py, planet/tectonics.py]
---

## Description
Run as a background job with stdout going to a file, `planet simulate` (and `planet make`, which logs only one line per 6 Myr of the run) showed nothing for
the first 40 minutes of an L8 run and then lines only every 6 Myr; the long finish window (~90 min for the last 12 Myr) looked like a hang. The stage after it
(the time zoom) prints only every 5% of the zoom. Print a line with the elapsed time at least every few minutes, with a flush, and name the phase
("finish window: climate 7 of 20"). Lane 86b could not tell a hang from slow work for ~90 minutes.
- [ ] a progress line at least every 5 min while redirected, flushed
- [ ] the finish window names its own progress
