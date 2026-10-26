---
id: PW-914
title: Progress bars for runs, zooms and peoples runs in the viewer
type: task
status: todo
parent: PW-247
milestone: v2
subsystem: viewer
effort: m
impact: med
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-10-26
updated: 2026-10-26
---

## Description
The viewer gives no sign of how far a long job has got. Runs (`planet simulate`), regional zooms and peoples' runs (the lineages history) can take tens of minutes, and the only feedback is that the page or the terminal is quiet until the job ends. Show a progress bar for each, in the viewer, so the owner can see whether a job is moving, roughly how long it has left, and whether it has stalled.
- [ ] a run, a zoom and a peoples run each show a progress bar while they work
- [ ] the bar reads the job's own progress (completed steps or simulated time), not a guessed timer
- [ ] a finished or stopped job no longer shows a bar

## Updates
- 2026-10-26: Created from inbox draft draft-progress-bars.md (found by owner).
