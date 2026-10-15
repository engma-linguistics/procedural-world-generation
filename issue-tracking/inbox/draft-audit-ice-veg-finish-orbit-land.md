---
title: "finish.orbit_dt treats ice on a bed below sea level as sea (land = bed > 0, not surface > 0)"
type: task
status: todo
parent: PW-245
subsystem: timezoom
effort: xs
impact: low
found_by: audit-ice-veg
blocked_by: []
relates: [PW-198]
refs: [planet/finish.py, planet/timezoom.py]
---

## Description
`finish.orbit_dt` (finish.py:150) builds the orbital anomaly with `land = st["elevation"] > 0`, where elevation is
the bed. Grounded ice on a bed pressed below sea level then gets the sea's insolation response (x0.3, no snow
brightness), not the land's the time zoom used (timezoom.py: land = grounded surface > 0). It is small: it touches
only cells under thick ice.

Fix: `land = st["elevation"] + st["ice"] > 0`.
