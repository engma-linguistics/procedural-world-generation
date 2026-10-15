---
id: PW-051
title: Oceans get older after the l7jumps fix; sea-level basin term on its clip
type: task
status: todo
parent: null
subsystem: tectonics
effort: m
impact: med
found_by: l7jumps
blocked_by: []
relates: [PW-024, PW-053]
refs: [planet/tectonics/events.py, planet/tectonics/earth.py, docs/review/health/2026-10-15/report.md]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Margin subduction now breaks off one basin (6000 km of the oldest passive margin) instead of the plate's
whole ocean. Mean ocean age is 83 Myr at L6 (70 before; Earth ~60). In stagnant 2–3-plate phases the L7
mean reaches 140–185 Myr, and the ocean-basin term of sea level sits on its −250 m clip. (Only that
term — half the change in mean ocean depth against a ~300 Myr running baseline — is clipped to ±250 m;
the hot-mantle and ice terms are added after the clip.) More plates (PW-024) may fix most of it.

## Updates
- 2026-10-15: Merged inbox draft draft-health-pw051-ocean-age.md ("PW-051 update: oceans no longer age at L6 or L7 (health sweep: seed medians 37-47 Myr, max 86); likely closable", found by health-sweep).
  Update for PW-051 (re-measure). PW-246 health sweep (2026-10-15, main 6926583, 1 Gyr): mean ocean-floor
  age per keyframe, seed medians 42-47 Myr at L6 (8 seeds; max over any run 86 Myr, seed 1) and 37-46
  Myr at L7 (seeds 3199, 21, 11; max 70 Myr). Earth ~64 Myr, the tests' envelope 25-120. No run reaches
  the 140-185 Myr of the ticket; plate counts at L7 stay at 5-17 (median 11-14), so the stagnant 2-3
  plate phases behind it are gone. If anything oceans are now a little young (more spreading than
  Earth), which also keeps the ocean-basin sea-level term positive-ish. Lowest total sea level at L7:
  -288 m (seed 3199 at 480 Myr, with ~-110 m of ice) -> the basin term no longer sits on its -250 m clip.
  - [ ] close PW-051, or keep it open only for the young-ocean side
- 2026-10-15: Tect2: mean ocean age now 41-57 Myr after PW-191's age fix; likely resolved, re-measure before closing.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Crust and continents.
