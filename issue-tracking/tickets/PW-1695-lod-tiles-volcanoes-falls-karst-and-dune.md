---
id: PW-1695
title: "LOD tiles: volcanoes, falls, karst and dune overlays and reef flats near a tile edge are drawn by one tile or none"
type: task
status: todo
parent: PW-1673
milestone: v1.0
subsystem: zoom
effort: m
impact: med
found_by: lane290
blocked_by: []
relates: [PW-1689]
refs: ["planet/zoom/fine.py::build", "planet/zoom/fine_forms.py::landform_overlay", "planet/zoom/fine_forms.py::coastal", planet/zoom/lod.py, planet/zoom/lod_build.py]
created: 2026-11-10
updated: 2026-11-10
---

## Description
**In plain words.** Some features a detail tile draws are decided by the tile alone, so where one sits near the edge
between two tiles it can stop at the edge (a volcano's cone or a waterfall's gorge drawn on one side only) or vanish from
both. On the globe that shows as a half-volcano or a cut-off gorge at a tile line, and a volcano dropped by a level-2
tile is lost for every finer level too (it leaves the tile's stats).

Where (fine.build with seam=True, lane 290):
- a volcano is skipped when its summit hold comes within `ramp + hold` of the tile edge, a fall when its chain comes within
  `ramp` of it; a volcano or fall wholly inside one tile can still reach over the edge with its edifice or gorge walls,
  which the neighbour does not draw. Skipped volcanoes are not passed on in the tile's stats.
- the karst and dune overlays (`fine_forms.landform_overlay`) and the reef flats and lagoons (`fine_forms.coastal`) keep
  means per parent pixel over the tile's own area, after the edge fade: their heights at an edge are the tile's own.
The seam numbers in docs/review/zoom/lod-plan-v2.md (State, lane 290) are for cell py.1.1 of dba204, where none of these
lie on the measured edges.

What to try: decide a feature's owner by place (the tile holding its vent or lip; the neighbour draws it too when its
reach crosses the edge, from the same parent data, so both sides agree), pass skipped volcanoes on in the stats, and
fade the overlays' and reef changes to zero at the edge like the carving.
- [ ] a volcano and a fall placed on a shared edge of two synthetic sibling tiles: heights across the edge within the
      inside steps; the volcano listed in both tiles' stats

## Updates
- 2026-11-10: Created from inbox draft draft-lod-features-at-tile-edges.md (found by lane290).
