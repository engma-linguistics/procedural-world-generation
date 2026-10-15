---
id: PW-198
title: "Finished worlds: climate ignores the frame's precession/eccentricity and the time zoom's anchor"
type: task
status: todo
parent: PW-090
subsystem: timezoom
effort: s
impact: low
found_by: finish
blocked_by: []
relates: [PW-091, PW-104]
refs: [planet/finish.py, planet/climate.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
A finished world (planet/finish.py) gets the frame's bed, ice, sea level, global temperature
and obliquity (as the tilt), then climate.compute. climate.compute has no eccentricity or
perihelion, so the frame's seasonal insolation anomaly (which the time zoom itself applies,
±10 C on summer land at 65 N) and its start_anchor cooling over the ice are not in the finished
world's temperature and seasons. So a finished glacial-maximum world is a little warmer in
summer than the time zoom frame it came from. Fix: give climate.compute an optional monthly
insolation anomaly (timezoom.insolation vs the reference orbit) and pass it from finish.py.

## Updates
- 2026-10-14: Created from inbox draft draft-finish-orbit-climate.md (found by finish).
