---
title: Confirm the river flicker fix on the owner's screen; move the other 1-px line overlays to ribbons if they flicker too
type: task
status: todo
parent: null
subsystem: viewer
effort: s
impact: med
found_by: pw408-river-flicker
blocked_by: []
relates: [PW-408]
refs: [viewer/index.html, "world 0b77f1", "~/Screencasts/Screencast From 2026-10-16 17-30-26.mp4"]
---

## Description
PW-408 changed the rivers from 1-pixel GL lines (`THREE.LineSegments`) to triangle ribbons
(three's `LineSegments2` / `LineMaterial`, `ribbonObj` in viewer/index.html). The cause could not
be reproduced headless. In headless Chrome on the same RTX PRO 6000 (ANGLE Vulkan and GL, device
scale 0.9, 1 and 1.25, globe and map, relief on and off), the river pixels are identical over 60
frames and under 1e-4 camera nudges. Analytically the rivers sit 0.1–0.3% of the radius above the
relief, about 30–60x the depth buffer's precision at the default distance. Only 12 of 2,662
segments on the 3D-relief map dip under a cell edge.

The owner's screencast does show it. With the camera and ground identical to the pixel between
frames (a 0 difference away from the rivers), only the GL line pixels switch between solid and
dotted, in bursts that look like a per-frame alternation sampled by the recorder. So the 1-px GL
line path is unstable in the owner's browser (Chrome on Wayland, NVIDIA), while triangles are not.
Ribbons are triangles, so they should be immune.

Every other line overlay is still a 1-px GL line: plate outlines, highlight rings and courses,
volcano and atoll marks, hotspot circles, event markers, plate arrows, wind and current arrows,
streamlines, the zoom box and the tropics.
- [ ] The owner confirms the rivers no longer flicker (globe and flat map, relief on and off).
- [ ] If the other overlays shimmer the same way, move them to `ribbonObj` as well (all of them
      share `lineObj`/`lineMat`, so it is one change; check the replay speed with
      `planetViewer.bench()`: rivers as ribbons gave 27.6 keyframes/s on run a1d3b9).
