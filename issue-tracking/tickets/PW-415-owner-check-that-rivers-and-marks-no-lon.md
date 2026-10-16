---
id: PW-415
title: Owner check that rivers and marks no longer flicker (PW-408 depth-precision fix)
type: task
status: in-progress
parent: null
subsystem: viewer
effort: xs
impact: med
found_by: pw408-river-flicker
blocked_by: []
relates: [PW-408]
refs: [viewer/index.html, "world 0b77f1"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
The PW-408 fix (`fitClip` in viewer/index.html: the near and far planes follow the view) was
verified only headless, by mimicking a 16-bit depth buffer with a near plane 256x smaller. The
headless buffer is 24-bit, so the original flicker never showed there. Whether the owner's
browser really has a low-precision depth buffer is inferred, not measured.

To find out, run `renderer.getContext().getParameter(renderer.getContext().DEPTH_BITS)` in the
console. `renderer` isn't global; `planetViewer` could expose it.
- [ ] The owner opens world 0b77f1 on the globe, then the flat map, 3D relief on and off,
      switching back and forth, and sees no shimmering rivers, volcano triangles or hotspot rings.
- [ ] If anything still shimmers, try `logarithmicDepthBuffer: true` on the renderer (zoom3d
      already uses it). The other suspect is the 1-px GL line path: the screencast showed only
      line pixels changing between frames. If so, move the remaining overlays to `ribbonObj`.
      Plate outlines are ~1 M segments, so check `planetViewer.bench()`.

## Updates
- 2026-10-16: Status todo -> in-progress. Owner (2026-10-16 night): Chrome still flickers after a full cache clear and restart. Firefox never flickered. No flicker while the mouse is dragging over the view. Back to in-progress.
- 2026-10-16: Created from inbox draft draft-pw408-confirm-on-screen.md (found by pw408-river-flicker).
