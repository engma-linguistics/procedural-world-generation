---
id: PW-175
title: Coastal plain beds have no recorded seaward dip, so its cuestas follow the contours
type: task
status: todo
parent: PW-005
subsystem: surface
effort: m
impact: low
found_by: zoomland3
blocked_by: []
relates: [PW-012, PW-147]
refs: [planet/landform.py, planet/zoom_landforms.py, "zoom:dccb9c"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The record gives flat strata the regional slope as their dip (a few
hundredths of a degree), so the zoom's CoastalPlain assumes a seaward dip
of 2.5-8 m/km and measures it from the coarse coast. On a low plain the
valleys cut ~30 m into beds 60 m apart, so the outcrops follow the
contours (benches along the valley sides, V's up the valleys; zoom dccb9c)
more than they make the long inland-facing cuestas of the Gulf and
Atlantic coastal plains, whose wedge of young beds thickens seaward
(dips 0.1-0.5 deg, steeper the older the bed).
Try: record the deposit's thickness gradient (a seaward-thickening wedge)
when shelf sediment emerges, giving coastal-plain cells a dip and a
direction; the zoom then uses them instead of the assumption.
Same family as PW-147 (caprock recorded as near-flat).

## Updates
- 2026-10-14: Created from inbox draft draft-coastal-plain-seaward-dip.md (found by zoomland3).
