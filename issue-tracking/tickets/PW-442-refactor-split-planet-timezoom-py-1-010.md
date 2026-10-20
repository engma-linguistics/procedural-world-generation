---
id: PW-442
title: "Refactor: split planet/timezoom.py (1,010 lines; simulate() ~390) into a package before the three-mode ice-age cycle"
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: high
found_by: coordinator-2026-10-20
blocked_by: []
relates: [PW-030, PW-440]
refs: [planet/timezoom.py]
created: 2026-10-20
updated: 2026-10-20
---

## Description
Proposed split: params, orbit/insolation, shelf, sources, the stepping loop, glacial events/report/save, kernels. The new cycle/hysteresis code then gets its own module. Behaviour-preserving: goldens and tests unchanged. A Haiku pass first looks for helpers duplicated elsewhere in planet/ (orbit, insolation, ice helpers vs icemass and tectonics.earth) so they can be shared. Pending the owner's yes.

## Updates
- 2026-10-20: Created.
- 2026-10-20: Phase 1 done on worktree-agent-ac03cc792f682e8a6: planet/timezoom/ package, planet/orbit.py, Grid.nbr_src/edge_dir; phase 2 (shared ice helpers, after PW-438) in inbox draft-pw442-phase2-shared-ice-helpers.md.
