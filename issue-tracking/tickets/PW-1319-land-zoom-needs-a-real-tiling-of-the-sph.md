---
id: PW-1319
title: "Land zoom needs a real tiling of the sphere: stepping 3800 km east or north does not give aligned, overlapping squares"
type: task
status: done
parent: PW-1299
milestone: v2
subsystem: zoom
effort: m
impact: high
found_by: lane116
blocked_by: []
relates: [PW-1301, PW-1296]
refs: ["planet/zoom/regional.py::Frame", "planet/zoom/regional.py::zoom", docs/review/land-zoom/practice.md, docs/review/land-zoom/seams.py, docs/review/land-zoom/seam-blockS.png, docs/review/land-zoom/seam-blockE.png, "world dba204", "zoom 7b69a9", "zoom a33145", "zoom c9ae66", "zoom f6a9c7"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** A regional zoom is a 4000 km square drawn around its centre in a projection that is true only at the centre. Two sections whose centres are 3800 km apart along a start bearing are not neighbouring squares: they are rotated against each other and the second centre drifts toward a pole. On dba204, SW (-25, 65) stepped east gave SE at lat -20.5 (4.5 degrees north), so the overlap with SW is a thin wedge, and SE to NE (NE = NW stepped east) overlap by 871 km instead of 200 km (`seam-blockE`). Any whole-planet tiling needs a rule first: e.g. fixed section centres (rings of constant latitude with a longitude step of 3800/cos(lat), or a cube-sphere or icosphere face layout), the overlap chosen, and seams measured along the bisector as `seams.py` does.
- [ ] a tiling function (centres for a world's land) with a guaranteed minimum and a stated maximum overlap
- [ ] re-measure the practice seams with it (`seams.py`)

## Updates
- 2026-11-02: Status in-progress -> done. Lane 122 (merged e89de6af): planet/zoom/tiling.py::sections, cube sphere 3x3 per face = 54 cells, overlap >=197 km; dba204 needs 47 land sections (~12 h at 1 km serial, ~6.5 h two at once). Orientation through zoom/save needed before a sweep (PW-1338); fewer sections PW-1339. Design docs/review/land-zoom/tiling.md.
- 2026-11-02: Status todo -> in-progress. 11-02: lane 122 (cost profile + fixes; tiling design and section lister).
- 2026-11-02: Created from inbox draft draft-land-zoom-tiling-geometry.md (found by lane116).
