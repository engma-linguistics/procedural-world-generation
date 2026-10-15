---
id: PW-179
title: Dipping caprock in a big zone measures its tilt from a far origin with a varying downhill
type: task
status: todo
parent: PW-005
subsystem: zoom
effort: s
impact: low
found_by: zoomland3
blocked_by: [PW-147]
relates: [PW-148]
refs: [planet/zoom_landforms.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-148 made the bench levels planet-fixed: caprock and lava anchor and
period are per zone (the class's connected cells on the whole grid), the
escarpment's level a smooth field of its zone. Tilted caprock beds
(cuestas) measure s = h + t (downhill . (p - o)) from the zone's reference
cell o, with the downhill direction per pixel from the coarse land. In a
zone ~1000 km across, o can be far from the zoom, and a downhill
direction turning by 0.5 rad over 100 km then adds ~t x |p - o| x 0.5 /
100 km of extra apparent tilt, contorting the cuestas. Rare today (PW-147:
caprock is recorded near-flat, so the tilt branch seldom runs).
Try: a per-zone dip direction (a plane fitted to the zone's cells), or the
tilt from a planet-fixed smooth field of bed height (as the coastal plain
does with the coast distance).

## Updates
- 2026-10-14: Created from inbox draft draft-tilted-caprock-zone-origin.md (found by zoomland3).
