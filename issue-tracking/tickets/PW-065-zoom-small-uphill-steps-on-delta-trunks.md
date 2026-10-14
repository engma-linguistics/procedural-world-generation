---
id: PW-065
title: "Zoom: small uphill steps on delta trunks"
type: task
status: done
parent: null
subsystem: zoom
effort: s
impact: low
found_by: falls
blocked_by: []
relates: []
refs: [planet/zoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Delta trunk channels have small uphill steps because their path is frozen early, before the land is
final. Predates `falls`.

## Updates
- 2026-10-14: Status todo -> done. zoomsmalls: final drainage evens out uphill steps <= 10 m along pinned courses (settle kernel) and unpins bigger ones; distributaries not laid over target ground > 250 m. 20 zooms: uphill receiver steps on land 671 -> 7 (rivers >= 100 m3/s 338 -> 4, delta channels 100 -> 1), max 244 -> 13 m.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Highlights (falls).
