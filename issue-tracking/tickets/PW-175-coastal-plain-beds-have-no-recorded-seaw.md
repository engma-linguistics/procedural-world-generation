---
id: PW-175
title: Coastal plain beds have no recorded seaward dip, so its cuestas follow the contours
type: task
status: todo
parent: null
milestone: later
subsystem: surface
effort: m
impact: low
found_by: zoomland3
blocked_by: []
relates: [PW-012, PW-147, PW-649]
refs: [planet/landform.py, planet/zoom/landforms.py]
created: 2026-10-14
updated: 2026-10-26
---

## Description
The record gives flat strata the regional slope as their dip (a few
hundredths of a degree), so the zoom's CoastalPlain assumes a seaward dip
of 2.5-8 m/km and measures it from the coarse coast. On a low plain the
valleys cut ~30 m into beds 60 m apart, so the outcrops follow the
contours (benches along the valley sides, V's up the valleys; zoom dccb9c (deleted))
more than they make the long inland-facing cuestas of the Gulf and
Atlantic coastal plains, whose wedge of young beds thickens seaward
(dips 0.1-0.5 deg, steeper the older the bed).
Try: record the deposit's thickness gradient (a seaward-thickening wedge)
when shelf sediment emerges, giving coastal-plain cells a dip and a
direction; the zoom then uses them instead of the assumption.
Same family as PW-147 (caprock recorded as near-flat).

## Updates
- 2026-10-26: Parent PW-005 (done) -> none. (PW-900 backlog reorg).
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-14: Created from inbox draft draft-coastal-plain-seaward-dip.md (found by zoomland3).
- 2026-10-30: planet/zoom.py and planet/zoom_*.py moved into planet/zoom/ (regional.py, fine.py, ...) and zoom.build split into named stages (stage_*.py), lane 55; the file names here are the new ones, but the line numbers in the text are from before the move.
