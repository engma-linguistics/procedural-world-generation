---
id: PW-139
title: "Regional zooms: July / January temperature and rain layers (season picker in zoom.html)"
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: viewerseason
blocked_by: []
relates: [PW-126]
refs: [planet/zoom.py, viewer/zoom.html, planet/world.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
PW-126 gave worlds `temperature_jul/jan` and `precipitation_jul/jan` (world.seasons, in world.finish) and the globe a
year / July / January picker for the Temperature and Rain layers (`?season=jul`). Regional zooms can't show them yet:
zoom.py interpolates only the annual `temperature` (reduced to sea level, then lapse-adjusted to the fine elevation,
around line 778) and `precipitation` from the coarse world, and writes only those two layers.

To add them: in zoom.py carry the four seasonal fields through the same coarse -> fine path as the annual ones
(temperatures with the same sea-level reduction and lapse rate; rain as precipitation, ideally with the same
orographic adjustment if any), write them as layers `temperature_jul` ... (uint16 / int8 like the world specs in
store.LAYERS), and in zoom.html add a season select next to the layer buttons, shown when the zoom has them, and
`?season=` like the globe. Old zooms without the layers just hide the select. About 4 extra 500x500 layers per zoom (~1 MB).
- [ ] zoom.py writes the four seasonal layers
- [ ] zoom.html Temperature/Rain follow a year/July/January picker and ?season=

## Updates
- 2026-10-15: Status in-progress -> done. Merged (vegzoom): temperature/precipitation jul/jan in zooms; season picker in zoom.html.
- 2026-10-15: Status todo -> in-progress. Overnight agent, worktree vegzoom.
- 2026-10-14: Created from inbox draft draft-zoom-seasonal-layers.md (found by viewerseason).
