---
id: PW-1186
title: Draw the portals and the wandering thinnings on the peoples map
type: task
status: todo
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: low
found_by: lane78
blocked_by: []
relates: [PW-1150, PW-697]
refs: [planet/lineages/history/portals.py, planet/lineages/output.py, viewer/lineages.html]
created: 2026-10-30
updated: 2026-10-30
---

## In plain words
The arrivals' portals, and the drifting thinnings when wandering portals are on, are only listed in the run's text, with no marks on the map. They should show as marks on the map.
A wandering thinning would show as a short track, from where it opened to where it closed.

## Description
- What the run stores today:
  - `meta.portals`: fixed portals, as lat/lon;
  - `meta.thinnings`: per plane, each thinning's id with its opened_kyr and lat/lon, then a closed_kyr entry;
  - per line `waves`: each wave's time, portal count, people and carried.
- Wanted:
  - per frame, the open thinnings' cells (or a track per thinning) in the frame data;
  - a marker layer in the globe and in the peoples viewer.
- [ ] frame data for open thinnings
- [ ] viewer markers

## Updates
- 2026-10-30: Created from inbox draft draft-draw-portals-and-thinnings-on-the-map.md (found by lane78).
