---
title: "PW-051 update: oceans no longer age at L6 or L7 (health sweep: seed medians 37-47 Myr, max 86); likely closable"
type: task
status: todo
parent: null
subsystem: tectonics
effort: xs
impact: low
found_by: health-sweep
blocked_by: []
relates: [PW-051, PW-191, PW-288]
refs: [docs/review/health/2026-10-15/report.md]
---

## Description
Update for PW-051 (re-measure). PW-246 health sweep (2026-10-15, main 6926583, 1 Gyr): mean ocean-floor
age per keyframe, seed medians 42-47 Myr at L6 (8 seeds; max over any run 86 Myr, seed 1) and 37-46
Myr at L7 (seeds 3199, 21, 11; max 70 Myr). Earth ~64 Myr, the tests' envelope 25-120. No run reaches
the 140-185 Myr of the ticket; plate counts at L7 stay at 5-17 (median 11-14), so the stagnant 2-3
plate phases behind it are gone. If anything oceans are now a little young (more spreading than
Earth), which also keeps the ocean-basin sea-level term positive-ish. Lowest total sea level at L7:
-288 m (seed 3199 at 480 Myr, with ~-110 m of ice) -> the basin term no longer sits on its -250 m clip.
- [ ] close PW-051, or keep it open only for the young-ocean side
