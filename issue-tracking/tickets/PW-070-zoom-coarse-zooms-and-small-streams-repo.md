---
id: PW-070
title: "Zoom: coarse zooms and small streams report undesigned drops"
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: falls2
blocked_by: []
relates: []
refs: [planet/zoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Coarse zooms (2–4 km pixels) still report steep reaches as waterfall drops, and small streams
(<400 m³/s) show 100–200 m drops on steep slopes. Filter the falls list by pixel size and discharge, or
treat them as cascades.

## Updates
- 2026-10-14: Status todo -> done. zoomsmalls: cause was creep filling stream beds (0.4 under ice) then the pit fill leaving steps; creep no longer lifts stream beds (under ice only up to 50 m/km in from the edge). waterfalls() lists an undesigned drop only if >= 3x as steep as the river within ~6 km, not under ice, not within 8 px of the edge. 20 zooms: undesigned drops listed 830 -> 32 (>= 100 m 428 -> 14); raw steps 830 -> 301.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Highlights (falls2).
