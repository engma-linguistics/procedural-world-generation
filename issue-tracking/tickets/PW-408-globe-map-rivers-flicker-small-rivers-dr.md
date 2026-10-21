---
id: PW-408
title: "Globe/map rivers flicker: small rivers draw as shimmering dotted lines (new 2026-10-16)"
type: task
status: done
parent: null
milestone: null
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
- 2026-10-16: Status todo -> done; the owner should confirm on his screen (draft-pw408-confirm-on-screen.md).
  Cause: depth precision, not the overlays' heights. The camera's near plane was fixed at 0.01, so at the default
  distance the depth buffer's step is ~d^2/(near*2^bits): ~5e-5 radii at 24 bits, but ~0.014 at 16 bits. That is more
  than the rivers' lift over the relief (0.001-0.003; analytically all but 12 of 2,662 segments clear the surface) and
  about the marks' (~0.012), which matches the owner seeing rivers flicker most, marks ~1/10 as much, and the relief
  map worst. Headless Chrome here has a 24-bit buffer and showed nothing. With near 256x smaller to mimic 16 bits, 20%
  of the river pixels were lost on the relief globe and ~50% on the relief map, and the loss changed under 3e-5 camera
  nudges. No state is left behind by switching views: the load -> map -> relief -> globe sequence keeps the same scene
  objects and identical frames. Fix: `fitClip` sets near/far every frame from the camera's height over the highest
  thing drawn (near ~1.0 at the default globe distance, ~1.5 on the map), and the same 256x precision loss then changes
  no pixel. Rivers are also ribbons now (three's fat lines, 1.5 px, the biggest 2.5 px), the same on every GPU. The
  other overlays stay 1-px GL lines, protected by the same fix. Replay with the relief on run a1d3b9: 21.9
  keyframes/s (main 19.1, same run, noisy machine).
- 2026-10-16: Created from inbox draft draft-river-flicker-relief.md (found by daniel).
