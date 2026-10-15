---
id: PW-193
title: "Pipeline in the UI: run (pick a Myr) -> time zoom (pick a kyr) -> finished world, chained with provenance"
type: story
status: in-progress
parent: PW-090
subsystem: viewer
effort: m
impact: high
found_by: daniel
blocked_by: [PW-091]
relates: [PW-091, PW-128, PW-103]
refs: []
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner (2026-10-14, next thing to work on): chain the phases in the viewer. Phase 1: in a run, pick a time on the slider and start a ~1 Myr glacial time zoom from it (POST /api/timezoom exists: {run, t, kyr}). Phase 2: in the time zoom, scrub to a chosen kyr ('now') and press 'Finish world here', producing a finished world (PW-091's output: a world in the usual format whose elevation, ice, lakes, sea level and climate reflect that moment, with provenance run@Myr -> timezoom@kyr). Phase 3: the finished world opens in the world view, with zooms/highlights as usual. Also allow finishing straight from a run time (skipping the time zoom = today's slice). Provenance shows the whole chain (PW-128 tree gains time zooms -> finished worlds; slider ticks). Job progress UI for each step. Ties to the one-grand-timeline idea (PW-103).

## Updates
- 2026-10-14: Status todo -> in-progress. Agent started in worktree finish, after PW-091.
- 2026-10-14: Created.
