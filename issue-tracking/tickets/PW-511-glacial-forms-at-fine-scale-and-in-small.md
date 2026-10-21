---
id: PW-511
title: Glacial forms at fine scale, and in small-glacier mountains (Alps, Patagonia) the imprint is ~0
type: story
status: todo
parent: null
milestone: v1
subsystem: zoom
effort: l
impact: med
found_by: pw092
blocked_by: []
relates: [PW-092, PW-499, PW-037]
refs: [planet/zoom_glacial.py, planet/zoom_fine.py, "zoom b03a2b", "zoom bf3c88", "world 577526"]
created: 2026-10-21
updated: 2026-10-21
---

## Description
Two gaps left by PW-092.
1. The Alps (zoom b03a2b) and Patagonia (bf3c88) get no troughs, cirques or fjords: at L6 the time zoom's cells there are a few ice cells with cell-mean erosion ~1 m (Alps) and 4 m (Patagonia), under the class's E > 3 m trunk rule. The parent's imprint is true to its own model, but real Alpine and Patagonian glaciation carved deep troughs (Patagonian fjords) that 110 km cells cannot hold. Options: (a) store per-cell glacier-valley erosion from a sub-cell scheme in the time zoom (mountain glaciers by elevation), (b) the zoom adds alpine carving wherever the zoom's own `glaciers()` ice reached during the glacial (needs a past-ice proxy from the climate: lowered snowline), (c) accept.
2. Fine zooms (zoom_fine, 25-100 m/px) get only the drumlin / kettle overlay through `Landforms.finish`; cirques, arêtes and troughs at that scale (and hanging valleys with real falls) are not drawn, and the zoom's trough floors are 2-4 px wide at 1-2 km/px.
- [ ] Alps and Patagonia zooms with troughs and cirques; a 100 m/px fjord zoom with cirques and a flat-floored U

## Updates
- 2026-10-21: Created from inbox draft draft-glacial-zoom-fine-and-alpine.md (found by pw092).
