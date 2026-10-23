---
id: PW-104
title: Embedded ice-age episodes in the main run (default on, at most 3 per run)
type: story
status: todo
parent: PW-470
milestone: v2
subsystem: timezoom
effort: l
impact: med
found_by: daniel
blocked_by: []
relates: [PW-091, PW-037]
refs: []
created: 2026-10-14
updated: 2026-10-23
---

## Description
Owner idea (2026-10-14). Today the main run has no orbital ice-age cycles: ice is an equilibrium per 4 Myr climate step (earth.py), and the glacial time zoom is a separate view-only run. Proposal: during a run, detect the strongest icehouse intervals (cold era, large ice extent), and for up to 3 of them run a ~1 Myr time-zoom sub-simulation at that moment; feed its imprint back into the coarse state (glacial erosion depth, sediment moved, fjords/overdeepenings, sea-level history effects), then carry on. Optional, default on, max 3 per run; the cost should stay a modest fraction of the run. Shares the imprint machinery with PW-037/PW-091.

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-14: Created.
