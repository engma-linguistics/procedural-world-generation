---
id: PW-376
title: "Zoom 3D at half / quarter detail: rivers in narrow valleys still cross ridges of the coarser mesh"
type: task
status: done
parent: null
milestone: null
subsystem: viewer
effort: s
impact: low
found_by: fall-jut (PW-375)
blocked_by: []
relates: [PW-375, PW-072]
refs: [viewer/zoom3d.js, viewer/zoom3d_mesh.js, "zoom:226c95"]
created: 2026-10-16
updated: 2026-10-16
---

## Description
PW-375 fixed the river "jutting up" below falls in the zoom 3D view at full detail (`detail=1`, the GPU
default): each quad is split along a river crossing it diagonally (`quadSplits`), and the painted river's
smoothed line is held on the valley floor (`hugChaikin`). At half and quarter detail (`&detail=2|4`, and the
default on a software renderer) the mesh's vertices skip pixels, so a river in a gorge one pixel wide lies
between vertices: the mesh there is the walls' interpolation and the painted river rides up and down it. The
coarse mesh only takes the diagonal through two river pixels at opposite corners of its quad, which helps little.
Options: lower the coarse mesh's vertices to the lowest pixel in their block along the drawn rivers (a
river-aware decimation), or keep full-detail rows/columns along the rivers (a non-uniform mesh).
- [ ] at `detail=4` on 226c95 the painted river below its 17 falls climbs < 20 m (measured as in PW-375)

## Updates
- 2026-10-16: Status in-progress -> done. Done (small fixes batch).
- 2026-10-16: Status todo -> in-progress. Small fixes batch agent started.
- 2026-10-16: Created from inbox draft draft-zoom3d-coarse-mesh-rivers.md (found by fall-jut (PW-375)).
