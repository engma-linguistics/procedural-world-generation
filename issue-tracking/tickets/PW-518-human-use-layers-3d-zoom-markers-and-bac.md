---
id: PW-518
title: "Human-use layers: 3D zoom markers, and backfill the stored worlds and zooms that predate them"
type: task
status: todo
parent: PW-099
milestone: null
subsystem: viewer
effort: s
impact: low
found_by: pw505
blocked_by: []
relates: [PW-505]
refs: [viewer/zoom.html, viewer/zoom3d.js, planet/__main__.py]
created: 2026-10-21
updated: 2026-10-21
---

## Description
PW-505 shows the five human-use layers on the globe, the 2D map and the 2D zoom tab. Two things were left out.
- The 3D zoom view (`viewer/zoom3d.js`) colours the ground from the layer picked (so farmland and fresh water show), but draws no harbour, pass or spring markers. The 2D zoom tab draws them from `state.marks.harb / passm / spring` (`huMarkers` in `viewer/zoom.html`); `zoom3d.js` takes only `falls` and `volc`.
- Stored items made before PW-099 have no human-use layers (the viewer shows nothing for them). `uv run python -m planet humanuse <id> ...` (new in PW-505) adds them in place to worlds and zooms. Run it on the showcases (world 577526 and its zooms 66c45e, 21703a, 4f65aa, 0de6eb, ...). A zoom's falls come from `stats.falls`; zooms without it get no fall mask, so rivers below a fall may read as navigable.
- [ ] harbour, pass and spring markers in the 3D zoom view
- [ ] humanuse backfill run on the showcase worlds and zooms

## Updates
- 2026-10-21: 2026-10-21: coordinator backfilled world 577526, 28442c and showcase/owner zooms (66c45e 0de6eb 21703a 4f65aa b03a2b bf3c88 85ba3f 9a2621 c9d1a9 91486c 7816f3). 3D zoom markers remain.
- 2026-10-21: Created from inbox draft draft-humanuse-3d-markers-backfill.md (found by pw505).
