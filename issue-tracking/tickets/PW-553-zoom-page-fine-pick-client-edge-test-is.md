---
id: PW-553
title: "Zoom page fine pick: client edge test is a square approximation; 3D hover ignores edge room"
type: task
status: todo
parent: PW-649
milestone: later
subsystem: viewer
effort: xs
impact: low
found_by: agent-a9583a91061f51486
blocked_by: []
relates: [PW-552]
refs: [viewer/zoom.html, planet/zoom/fine.py]
created: 2026-10-21
updated: 2026-10-23
---

## Description
PW-552 made the size menu follow the server (`GET /api/fine-rules?res_km=`). The pick's *position* test is still
client-side: `fineFitsIn()` in viewer/zoom.html uses a square (edge_px*res + halo) margin, while
`zoom_fine.check()` projects a 3x3 sample of the region into the parent's plane, so near a corner or a far-off-centre
zoom the server can still refuse ("refused: ... doesn't fit inside zoom ...") a point the page accepted. In 3D the
hint (`hoverHost3d`) takes the tile under the pointer as the host without the edge test; a click too near its edge
then falls back to a coarser host (or is refused).
- [ ] Either expose the position check (e.g. `GET /api/fine-rules?...&lat=&lon=&size_km=&res_km=` calling `check()`), or
      mirror the 3x3 projection in JS and cover it with a test against `check()`.
- [ ] 3D hover: show the same "too close to the edge" hint as the 2D map.

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-21: Created from inbox draft draft-fine-pick-fit-check.md (found by agent-a9583a91061f51486).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
