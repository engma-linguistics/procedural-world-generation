---
title: "PW-239 update: run frames' stale lakes show giant 2-7 Mkm2 salt lakes, and their `downstream` doubles inland drainage"
type: task
status: todo
parent: null
subsystem: hydrology
effort: s
impact: med
found_by: health-sweep
blocked_by: []
relates: [PW-239, PW-054, PW-243]
refs: [tools/health.py, docs/review/health/2026-10-15/report.md, planet/tectonics/earth.py, "run cde55b", "run:aad3b9@88Myr(6.60,74.40)"]
---

## Description
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
