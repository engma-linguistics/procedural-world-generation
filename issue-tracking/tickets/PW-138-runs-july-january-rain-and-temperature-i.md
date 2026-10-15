---
id: PW-138
title: "Runs: July / January rain (and temperature) in keyframes, so the season picker works on runs"
type: task
status: done
parent: null
subsystem: store
effort: s
impact: low
found_by: viewerseason
blocked_by: []
relates: [PW-107, PW-126]
refs: [planet/timeline.py, planet/store.py, viewer/index.html]
created: 2026-10-14
updated: 2026-10-15
---

## Description
PW-126 stores July / January temperature and precipitation in worlds (store.LAYERS `temperature_jul/jan`,
`precipitation_jul/jan`) and the viewer's Temperature / Rain season picker shows on worlds only; on a run it is
hidden because keyframes store only the annual `temperature` and `precipitation`. The PW-126 ticket asked to add
seasonal rain to runs too "if the frame-size cost is acceptable", alongside PW-107 (seasonal winds in keyframes).

Cost: `precipitation_*` is uint16 (2 bytes x cells x frames: at L7, 250 frames, ~80 MB per layer) and
`temperature_*` int8 (~40 MB each), so all four add ~240 MB to an L7 1 Gyr run. Options: (A) all four;
(B) precipitation only, as uint8 with a log transform like flow (~40 MB each); (C) leave runs annual (worlds
are cheap to make from a keyframe: the viewer's Zoom/Highlights does it in seconds). Lean B, done together with PW-107.
The viewer side is ready: COLOUR_NEEDS for 'rainfall'/'temperature' would need the seasonal names added, and
seasonalData() already reads `<layer>_<season>` from V.layers when present.

## Updates
- 2026-10-15: Status todo -> done. Merged (smalls2).
- 2026-10-14: Created from inbox draft draft-run-seasonal-climate.md (found by viewerseason).
