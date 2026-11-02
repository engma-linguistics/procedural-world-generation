---
id: PW-1300
title: "Choose practice sections for the land zoom: side-by-side 4000 km neighbours that cross a river, a range, a coast and a desert edge, and measure their seams"
type: task
status: done
parent: PW-1299
milestone: v2
subsystem: zoom
effort: s
impact: high
found_by: owner
blocked_by: []
relates: []
refs: ["planet/zoom/regional.py::zoom", "world 0af5ae", "world dba204", "world 9459ad"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
**In plain words.** The coordinator picks 3-4 pairs (and one 2x2 block) of adjacent 4000 km sections on a showcase world, chosen so each seam crosses something that shows a mismatch: a big river, a mountain range, a coastline, a desert or ice edge. Zoom each at ~1 km/px, then measure the seams: height and slope jumps, coast and river breaks, landform and biome mismatches, and per-section wall time and peak memory. Output: docs/review/land-zoom/practice.md with the sections' lat/lon (world:<id>(lat,lon) refs), pictures of each seam, and the numbers. No fixes yet.

## Updates
- 2026-11-02: Status todo -> done. Lane 116 merged: 10 sections on dba204 at 2 km (zooms 7b69a9 a33145 f6a9c7 c9ae66 2a4463 fde691 7fd990 e82f85 48489d 50d6af), one at 1 km (69b422: 2 h 48 m, 110 GB); docs/review/land-zoom/practice.md.
- 2026-11-02: Created.
