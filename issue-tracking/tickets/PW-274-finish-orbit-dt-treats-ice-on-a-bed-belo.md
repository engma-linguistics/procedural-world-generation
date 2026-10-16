---
id: PW-274
title: finish.orbit_dt treats ice on a bed below sea level as sea (land = bed > 0, not surface > 0)
type: task
status: done
parent: PW-245
subsystem: timezoom
effort: xs
impact: low
found_by: audit-ice-veg
blocked_by: []
relates: [PW-198]
refs: [planet/finish.py, planet/timezoom.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`finish.orbit_dt` (finish.py:150) builds the orbital anomaly with `land = st["elevation"] > 0`, where elevation is
the bed. Grounded ice on a bed pressed below sea level then gets the sea's insolation response (x0.3, no snow
brightness), not the land's the time zoom used (timezoom.py: land = grounded surface > 0). It is small: it touches
only cells under thick ice.

Fix: `land = st["elevation"] + st["ice"] > 0`.

## Updates
- 2026-10-15: Status in-progress -> done. Done in the ice fix branch (merged 20684ed); docs/review/audit/fixes-ice.md.
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Created from inbox draft draft-audit-ice-veg-finish-orbit-land.md (found by audit-ice-veg).
