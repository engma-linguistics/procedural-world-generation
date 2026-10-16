---
id: PW-310
title: "Zoom: round sea holes cut into land near a polar hotspot chain"
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: zoom-polish
blocked_by: []
relates: [PW-118]
refs: [planet/zoom.py, planet/zoom_volcanoes.py, "world:592f2a(73.6,121.0)", docs/review/zoom-polish/pw118_caldera_before.png]
created: 2026-10-15
updated: 2026-10-16
---

## Description
In a 500 km @ 1 km zoom at world:592f2a(73.6,121.0) (and the 250 km @ 0.5 km one at
73.58,124.18), several perfect circles of sea, ~80-120 km across, are cut into an
ice-covered landmass, with sharp round coastlines (visible in
docs/review/zoom-polish/pw118_caldera_before.png, top left; there before PW-118 too).
They look like the oceanic hotspot vents' province (`zoom_volcanoes.fields`: terrain
replaced by the vents' sea floor within `rin`, `wv = province x oceanic`) applied where
the coarse cells count as oceanic crust but stand above the sea (or under ice). Check
the vents there (floor_m < 0 but the coarse ground land?) and fade the province where
the coarse cells are land, or take the vent's floor from the current ground. Cell-mean
rms in that zoom is ~1,600 m, so something there fights the means.

## Updates
- 2026-10-16: Status in-progress -> done. Done (95f410d): zoom removes only the cones' own share of each cell's mean for vents recorded below their cells; 73.6,121 zoom bias -1879 -> +89 m, land/sea agreement 87 -> 96%.
- 2026-10-15: Status todo -> in-progress. Zoom batch 2 agent started.
- 2026-10-15: Created from inbox draft draft-zoom-round-sea-holes-73n.md (found by zoom-polish).
