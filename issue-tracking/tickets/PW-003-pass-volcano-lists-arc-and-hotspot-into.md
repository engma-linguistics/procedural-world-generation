---
id: PW-003
title: Pass volcano lists (arc and hotspot) into worlds and zooms
type: story
status: done
parent: PW-001
subsystem: store
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: [PW-002]
refs: [planet/tectonics/volcanism.py, planet/store.py, planet/timeline.py, planet/world.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Arc volcanoes already exist as point objects in `planet/tectonics/volcanism.py` (`volcanoes()`), and
hotspot vents will (run-side story). Neither reaches a world or zoom today. Store them in keyframes /
checkpoints, slice them into the world (position, kind, age, height, active or not) and hand the
nearby ones to `zoom.zoom()`. Show them as a viewer overlay on worlds if cheap.

## Updates
- 2026-10-14: Status in-progress -> done. Done. Columns in volcanism.COLUMNS; world meta.volcanoes + meta.volcano_columns; runs/<id>/volcanoes.json.gz (~8 MB per 500 Myr at L7); run.json frames list only the active ones [lat, lon, kind] for the viewer.
- 2026-10-14: Volcano table (volcanism.COLUMNS) in snapshots, checkpoints (state), runs/<id>/volcanoes.json.gz per keyframe, world meta (slice and world_from_frame); zoom reads it. Viewer overlay on worlds: arcs, hotspot islands, atolls.
- 2026-10-14: Status todo -> in-progress. Started in worktree volcanoes.
- 2026-10-14: Created from the discrete-volcanoes epic (owner discussion 2026-10-14).
