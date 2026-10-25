---
id: PW-842
title: Peoples workbench Results tab lists runs but none load for the world on screen
type: task
status: todo
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: med
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: []
refs: []
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner feedback 2026-10-25 (feedback doc on world 2a7385): Owner expected the current world's runs (e.g. 57939b?) to show; looks broken. Investigation pending.

## Updates
- 2026-10-25: fun-lane-24: the workbench Results tab lists the current world's peoples runs (the world picker, or a time zoom's), opens the newest when none is open, and has an 'all worlds (N)' toggle; the open run is always listed. Also fixed: the run dropdown had no handler while no run was open. Checked with a headless screenshot of ?world=2a7385#results.
- 2026-10-25: Diagnosis: drawResults lists every peoples run, newest first, with no filter or selection by the current world (lineages.html:596-600, 647, 775-786); 57939b is on world 119973, not 2a7385 (2a7385's runs are b69f51 and 6b5d0e); 7 of 23 listed runs point to a deleted world or time zoom. Fix: filter or select by ?world= / the dropdown; prune stale runs.
- 2026-10-25: Created.
