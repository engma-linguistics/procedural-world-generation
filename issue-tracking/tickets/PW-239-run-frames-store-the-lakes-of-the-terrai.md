---
id: PW-239
title: Run frames store the lakes of the terrain before that step's erosion and sediment, so they disagree with the frame's own elevation
type: task
status: todo
parent: null
subsystem: hydrology
effort: s
impact: low
found_by: hydro2
blocked_by: []
relates: [PW-057, PW-054]
refs: [planet/tectonics/output.py, planet/surface.py, "run 4ddb5d", "run bad074", "run 6ff364", "run 01b0f7"]
created: 2026-10-15
updated: 2026-10-15
---

## Description
After PW-057 (B: slope-scaled texture, one-sided creep, lake-aware world erosion) a world keeps most of
the lakes that its keyframe's *elevation* holds under the world's climate (Jaccard 0.31-0.89 on five L6
runs, was 0.05-0.77). But the run frame's own `lake_depth` layer still agrees with that on few cells:
Jaccard 0.04-0.11 (runs bad074@500, 4ddb5d@500, 6ff364@500, 01b0f7@976), and run lakes turn over from
one 4-Myr frame to the next (Jaccard frame-to-frame 0.02-0.34). Cause: `output.lakes_now` stores the
lakes `surface.erode` worked out on the terrain *before* the step's erosion, deposition (which fills each
hollow to within 5 m of its spill level when the sediment is there), sea-level and tectonic changes,
while the frame's elevation is after them. So the viewer shows a run frame's lakes over terrain that no
longer holds them, and its slice shows others.
Options:
- A. Keep (the run's lakes are "the lakes during that step"); document it.
- B. Store lakes recomputed on the frame's final terrain (one more `hydrology.lakes` per stored frame,
  ~0.4 s at L7 every 4 Myr, ~+5% run time); the run frame and its world then share the terrain and
  differ only by climate and finishing.
- C. Snapshot the elevation before erosion instead (no: the elevation is the frame's state).
Lean: B (cheap, and what the viewer shows becomes consistent).

## Updates
- 2026-10-15: Status needs-decision -> todo. Coordinator decision (north star): B, recompute the frame's lakes on its final terrain (~+5% run time); a frame should describe itself.
- 2026-10-15: Created from inbox draft draft-run-frame-lakes-pre-step.md (found by hydro2).
