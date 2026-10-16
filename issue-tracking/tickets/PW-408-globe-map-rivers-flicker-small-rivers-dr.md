---
id: PW-408
title: "Globe/map rivers flicker: small rivers draw as shimmering dotted lines (new 2026-10-16)"
type: task
status: done
parent: null
subsystem: viewer
effort: s
impact: high
found_by: daniel
blocked_by: []
relates: []
refs: [viewer/index.html, viewer/relief.js, "world 0b77f1"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
Owner screencast (~/Screencasts/Screencast From 2026-10-16 17-30-26.mp4, map view of a run/world): every small river renders as a dotted line whose dots shimmer frame to frame, while the large highlighted river (white) stays solid. New today: most likely depth fighting between the river lines and the 3D relief surface (viewer/relief.js, landed 2026-10-16), or the rivers sitting on the old flat-sphere radius under the displaced surface. Fix the cause (draw rivers on the relief's displaced height with a small offset or polygonOffset, or depth-test off for the overlay layer); check globe and map, relief on and off, at several zoom levels.

## Updates
- 2026-10-16: Status todo -> done (the owner should confirm on his screen: draft-gl-line-overlays-unstable.md).
  Not depth fighting with the relief. The screencast's frames have the camera and ground identical to the pixel; only the
  GL line pixels switch between solid and dotted (all rivers, the big white one too), in bursts that look like a
  per-frame alternation sampled by the recorder. Headless Chrome on the same GPU (ANGLE Vulkan and GL, scale 0.9/1/1.25,
  globe and map, relief on and off) draws identical river pixels over 60 frames and under 1e-4 camera nudges. The rivers
  sit 0.1-0.3% of the radius above the surface, ~30-60x the depth precision (12 of 2,662 segments dip under a cell edge
  on the relief map). So the 1-px GL line path is unstable in the owner's browser (Chrome, Wayland, NVIDIA) and the
  triangles are not. Fix: rivers are now triangle ribbons (three's LineSegments2/LineMaterial, `ribbonObj`), 1.5 px (the
  biggest 0.5% 2.5 px), the same on the globe and the map. Replay on run a1d3b9 L7 27.6 keyframes/s (unchanged).
- 2026-10-16: Created from inbox draft draft-river-flicker-relief.md (found by daniel).
