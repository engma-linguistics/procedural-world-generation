---
id: PW-091
title: "First step: time zoom from a chosen world, feeding a finished world"
type: story
status: todo
parent: PW-090
subsystem: timezoom
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: [PW-031]
refs: [planet/timezoom.py, planet/world.py, planet/store.py, planet/__main__.py, planet/api.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Run the time zoom from a world (or a run time) and feed its results back into a new "finished world":
today the time zoom is view-only and leaves no imprint. Output a world (same format as a sliced world,
with provenance: source run/world, time-zoom settings, which kyr is the "now") whose elevation, ice,
lakes and sea level reflect the time zoom's end state. CLI (e.g. `planet finish <world> [--kyr 1000]`)
and a viewer button. Highest impact; the epic's first step. Generated worlds currently glaciate too
hard (PW-031); fix or limit that so finished worlds aren't buried in ice.

## Updates
- 2026-10-14: Created from the owner's world-finishing epic (2026-10-14).
