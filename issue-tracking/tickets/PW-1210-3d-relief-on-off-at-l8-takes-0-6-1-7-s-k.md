---
id: PW-1210
title: "3D relief on/off at L8 takes 0.6-1.7 s: keep the globe's mesh, swap only material and normals"
type: task
status: todo
parent: PW-1198
milestone: later
subsystem: viewer
effort: s
impact: low
found_by: lane91-viewer-l8
blocked_by: []
relates: [PW-1198]
refs: [viewer/globe/geometry.js, viewer/globe/map2d.js, docs/review/viewer-l8/diagnosis.md]
created: 2026-10-31
updated: 2026-11-03
---

## Description
**In plain words.** At L8, ticking 3D relief takes about a second, and going back from the flat map to
the globe takes about 0.6-1 s. Most of that is rebuilding and re-uploading a globe mesh that hasn't changed.

Measured on a synthetic L8 world (lane 91, after its fixes): 3D relief on 1.1-1.7 s, off 0.6-1.1 s, back to
the globe 0.6-1.0 s. The globe's topology (`buildTopology`) is the same with and without the relief. Only
the material (smooth vs flat shading), the normal attribute and the sea shell differ. Yet the relief's
change handler (`map2d.js`) calls `buildTopology()`, which makes a new BufferGeometry, so three.js uploads
fresh position, colour and index buffers (`bufferData` ~0.2 s at L8) on top of the ~0.3 s build. Try:
- keep the globe's arrays and geometry when the topology key (grid, globe, perTri) is unchanged; add or
  drop the normal attribute and swap the material in place;
- optionally keep the last globe topology while on the flat map, so going back costs only a paint
  (~0.2 GB of heap at L8: weigh it).
- [ ] L8: 3D relief on/off < 0.4 s; same pixels (tools/viewer_perf_globe.py --fingerprint --equirect)

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: L8/L9 whole-world work, post-v2 (see PW-1198 space-to-ground globe)
- 2026-10-31: Created from inbox draft draft-relief-toggle-keeps-globe-mesh.md (found by lane91-viewer-l8).
