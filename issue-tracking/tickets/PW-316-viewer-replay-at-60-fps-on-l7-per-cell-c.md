---
id: PW-316
title: Viewer replay at 60 fps on L7 - per-cell colour and height in data textures
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: m
impact: low
found_by: viewer-replay-speed
blocked_by: []
relates: []
refs: [viewer/index.html]
created: 2026-10-15
updated: 2026-10-16
---

## Description
After the replay speed-up (2026-10-15) an L7 keyframe costs ~25-30 ms of script and the replay reaches
~23-28 keyframes/s on "very fast" (40/s requested). What's left per frame: writing and uploading
~1.15 M vertex positions and colours (~28 MB) in `paint` (~10 ms), the colour ramps in `cellColors`
(~5-8 ms), the overlays (~5 ms), the summary's innerHTML (~1.5 ms).

To reach 60 fps: keep the mesh static and give each vertex its cell index (and corner index); upload a
per-cell colour texture (n texels, 0.6 MB) and a per-cell/per-corner height texture each frame, and
displace / colour in the vertex shader (`onBeforeCompile` on the Lambert material). Smooth colours and the
flat map's hill shading (per-triangle, `mapHillshade`) need care. Only worth it if 25 fps feels slow.

## Updates
- 2026-10-16: Coordinator 2026-10-16: deferred; replay is ~23-28 keyframes/s after the speed-up, revisit only if it feels slow.
- 2026-10-15: Created from inbox draft draft-viewer-replay-60fps.md (found by viewer-replay-speed).
