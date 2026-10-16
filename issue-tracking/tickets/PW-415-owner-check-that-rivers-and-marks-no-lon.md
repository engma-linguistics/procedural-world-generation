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
- 2026-10-16: Owner test in Chrome (2026-10-16 night; ANGLE on OpenGL, NVIDIA RTX PRO 6000, 24-bit depth, 4 MSAA samples, dpr 1): ?noaa=1 alone cures the flicker; always/rehover/pdb don't matter. The flicker runs while the readout shows cam and renders at 60/s (the orbit-damping tail, 4-11 s after the globe stops) and stops at 0 renders. Light-blue rivers and the satellite view don't show it. The render-on-change default (890efce) shortens it but doesn't cure it. MSAA is now off by default (?aa=1 turns it back on). Awaiting the owner's look at line quality without MSAA.
- 2026-10-16: pw415 branch: three default changes and a set of URL switches for the owner's Chrome.
  Measured headless (SwiftShader, so the flicker itself can't show there): at rest nothing in the
  scene changes from frame to frame (camera, near/far, geometry, materials all fixed), yet the old
  loop redrew the identical scene 60 times a second. After a drag the orbit damping keeps moving the
  camera for ~640 frames (~10 s at 60 Hz), by less than 1e-7 radii after ~240. Each mouse move
  rewrote the info box even when its text didn't change (always, over empty space), and every panel
  had a `backdrop-filter: blur` over the WebGL canvas, so each rewrite made Chrome recomposite the
  canvas under it. That matches "a flicker per pixel of mouse movement over space" and points at
  Chrome's presentation of the canvas, not at our depth values.
  Defaults now: (1) the globe is drawn only when something drawn changes (a signature of the camera,
  every object's transform, visibility, geometry and attribute versions, materials, textures and
  lights; the same screenshots as drawing every frame in 9 states, replays draw every keyframe);
  (2) the info box is written only when its content changes; (3) no backdrop blur on the panels
  (they're 92% opaque, so it barely showed).
  Owner, in Chrome (server on 8765), in this order:
  1. `http://127.0.0.1:8765/viewer/?world=0b77f1.json&dbg=1`: the new defaults plus a readout in the
     bottom-left corner: GPU string, depth bits, MSAA samples, canvas and CSS size, near/far, and
     per-second counts. At rest "renders" should be 0. Flicker gone: the fix works, and steps 2-3
     tell which part did it. Flicker with renders 0: Chrome is flickering a canvas we no longer
     redraw, so it's the compositor: go to step 4. Renders above 0 at rest: something still changes
     every frame; send the readout.
  2. Add `&always=1` (redraw every frame, as before). If that brings the flicker back, the redraws
     at rest were the cause.
  3. Add `&blur=1` and/or `&rehover=1` (the blur back; the info box rewritten on every mouse move).
     If either brings back the mouse-over-space flicker, that was the trigger.
  4. Only if it still flickers, one at a time: `&pdb=1` (preserveDrawingBuffer: Chrome copies
     the frame instead of swapping buffers; fixed: a Chrome buffer swap bug), `&noaa=1` (no MSAA;
     fixed: MSAA resolve), `&dpr=1` (pixel ratio 1; fixed: canvas resampling, check whether the
     readout's canvas size is the CSS size times dpr), `&logdepth=1` (logarithmic depth; fixed:
     depth precision after all, though the readout's depth bits say how much we have),
     `&offset=1` (polygon offset pushes the ground back; fixed: z-fighting), `&nodamp=1` (no orbit
     damping), `&fixclip=1` (the old fixed near 0.01 / far 100; should make things worse).
  Also useful: chrome://gpu, the "Graphics Feature Status" and the GL/ANGLE backend lines.
- 2026-10-16: Status todo -> in-progress. Owner (2026-10-16 night): Chrome still flickers after a full cache clear and restart. Firefox never flickered. No flicker while the mouse is dragging over the view. Back to in-progress.
- 2026-10-16: Created from inbox draft draft-pw408-confirm-on-screen.md (found by pw408-river-flicker).
