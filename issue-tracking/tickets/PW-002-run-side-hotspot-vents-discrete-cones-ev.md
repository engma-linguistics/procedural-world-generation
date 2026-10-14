---
id: PW-002
title: "Run-side hotspot vents: discrete cones every 50-100 km of plate motion"
type: story
status: in-progress
parent: PW-001
subsystem: tectonics
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [planet/tectonics/volcanism.py, planet/tectonics/isostasy.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Replace the continuous ~150 km Gaussian hotspot smear (`volcanism.hotspots`, `r = 150 km`) with
discrete vents. When the plate has moved ~50–100 km over a plume since its last vent, start a new vent
on the plate (plate frame, so it rides along). Each vent has a height (from plume strength and crust
type), subsides with crust age and erodes; old vents drop below sea level (guyots).

- [ ] Vents stored as a per-run list (plate id, plate-frame position, birth time, height) in the state
      and checkpoints
- [ ] Elevation still conserves the crust budget (tests in `tests/test_invariants.py`)
- [ ] At L7 an ocean hotspot leaves a chain of separate islands/seamounts, youngest over the plume

## Updates
- 2026-10-14: Status todo -> in-progress. Started in worktree volcanoes.
- 2026-10-14: Created from the discrete-volcanoes epic (owner discussion 2026-10-14).
