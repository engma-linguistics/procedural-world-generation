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
refs: [planet/tectonics/output.py, planet/surface.py, "run 4ddb5d", "run bad074", "run 6ff364", "run 01b0f7", tools/health.py, docs/review/health/2026-10-15/report.md, planet/tectonics/earth.py, "run cde55b", "run:aad3b9@88Myr(6.60,74.40)"]
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
- 2026-10-15: Merged inbox draft draft-health-pw239-downstream-stale.md ("PW-239 update: run frames' stale lakes show giant 2-7 Mkm2 salt lakes, and their `downstream` doubles inland drainage", found by health-sweep).
  Update for PW-239 (same cause: a run frame stores what `surface.erode` worked out on the terrain
  *before* the step's erosion, deposition and tectonics). Besides `lake_depth`/`lake_kind`, the
  frame's `downstream` layer is stale in the same way. PW-246 health sweep, 8 L6 seeds x 1 Gyr
  (2026-10-15): following each land cell's stored `downstream` to its end (as highlights'
  `_inland_basins` and the coordinator's quick world check do), 22-27% of ice-free land drains
  inland (median over 50-1000 Myr per seed). But most of those ends are not hollows on the frame's own
  elevation: of seed 21's (run 65e4c7) 206 inland ends at 400 Myr, 164 have a lower neighbour and 86
  touch the sea; counting only ends that are closed lakes, salt pans or real pits on the frame's
  elevation gives 7-11% (seed medians), which matches PW-243's 9.5-11% from `rivers_and_lakes` on
  `sim.bed()`. So anything reading a run frame's rivers (viewer river overlay on run frames, highlights
  on `world_from_frame` worlds, quick inland checks) sees routes that end in hollows the frame no
  longer has.
  Giant lakes: on the same sweep, every L6 seed has keyframes whose largest lake (connected land cells
  with `lake_depth` > 0) is over 1 million km2 (Caspian 0.37): seed 11 15.5% of keyframes, 42 14.7%,
  1 14.3%, 2 13.9%, 21 10.1%, 3199 7.6%, 505 6.7%, 77 3.4%. The biggest are closed salt lakes
  (`lake_kind` 2) ~50-70 m deep: seed 42 (run aad3b9) 7.25 Mkm2 at 88 Myr around (6.6, 74.4), 6.4 Mkm2
  at 368 Myr; seed 3199 (b8b494) 5.8 Mkm2 at 132-152 Myr; the other seeds 3.0-3.8 Mkm2 at worst. The
  world sliced at aad3b9 @ 88 Myr (world 3eaf9a, replay matches the keyframe) has no such lake: its
  largest is 0.09 Mkm2. So these are the hollows of the pre-deposition terrain, filled within the step
  (the run's erosion does see them for that step: sediment trapping, lake evaporation).
  - [ ] PW-239's option B (recompute lakes on the frame's final terrain) should recompute
    `downstream` (and `flow`) with them
  - [ ] then `inland_raw_pct` and `inland_pct` in tools/health.py should agree
- 2026-10-15: Status needs-decision -> todo. Coordinator decision (north star): B, recompute the frame's lakes on its final terrain (~+5% run time); a frame should describe itself.
- 2026-10-15: Created from inbox draft draft-run-frame-lakes-pre-step.md (found by hydro2).
