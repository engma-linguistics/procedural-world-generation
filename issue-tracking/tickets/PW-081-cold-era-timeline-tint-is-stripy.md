---
id: PW-081
title: Cold-era timeline tint is stripy
type: task
status: done
parent: null
subsystem: viewer
effort: xs
impact: low
found_by: viewer2
blocked_by: []
relates: []
refs: [viewer/index.html]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The run timeline's cold-era tint flickers frame to frame where temperature does (kept unsmoothed). Smooth
over a few frames or use hysteresis.

## Updates
- 2026-10-14: Status in-progress -> done. Two causes. (1) The main stripes were a drawing bug: each keyframe's translucent rect overlapped the next by a pixel, doubling the alpha in thin regular stripes even through steady eras; rects now abut. (2) Frame-to-frame wobble near the thresholds: coldness is now a 5-keyframe running mean, and the alpha ramps in from 0 instead of switching on at 0.05. Threshold flips on run 103c05 25 -> 15 (and faint where left). Checked with a headless-Chrome screenshot of run 103c05.
- 2026-10-14: Status todo -> in-progress. Started on branch quickwins.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Viewer / Earth world.
