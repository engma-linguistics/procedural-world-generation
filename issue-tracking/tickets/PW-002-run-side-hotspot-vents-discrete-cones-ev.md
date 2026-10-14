---
id: PW-002
title: "Run-side hotspot vents: discrete cones every 50-100 km of plate motion"
type: story
status: done
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
- 2026-10-14: Status in-progress -> done. Done. Demo: run 39d004 (seed 13 L7 500 Myr): equatorial chain from the plume at (-1.9, 35.4), islands 0-8 Myr, atolls beyond, youngest over the plume; at L7 ~half the >800 m islands are land cells (sub-cell cones), see inbox draft on coarse grids.
- 2026-10-14: Vents implemented (volcanism.hotspots/new_vent/tend): gap 1.5 x flexural wavelength (60-150 km, +-30%), 25 km Gaussian cones, Vogt height limit 2.5+0.8 sqrt(age) km (Mauna Kea summit cap), excess as an apron below -2 km; sink on own sea-floor clock + swell, erode, wave-planed, reefs. Crust budget test passes.
- 2026-10-14: Status todo -> in-progress. Started in worktree volcanoes.
- 2026-10-14: Created from the discrete-volcanoes epic (owner discussion 2026-10-14).
