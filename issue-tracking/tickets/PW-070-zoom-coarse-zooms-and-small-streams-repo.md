---
id: PW-070
title: "Zoom: coarse zooms and small streams report undesigned drops"
type: task
status: todo
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
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Highlights (falls2).
