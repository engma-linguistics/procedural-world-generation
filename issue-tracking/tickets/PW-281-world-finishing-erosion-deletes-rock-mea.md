---
id: PW-281
title: World finishing erosion deletes rock (mean 46 m of land at strength 0.3) instead of depositing it
type: task
status: in-progress
parent: PW-245
subsystem: hydrology
effort: s
impact: low
found_by: audit-surface-hydro
blocked_by: []
relates: [PW-239]
refs: [planet/hydrology.py, planet/world.py, docs/review/audit/surface-hydro.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`hydrology.erode` (12 passes of stream power plus a creep that only lowers ground, PW-057) never deposits what it
removes. On an L5 run end (seed 1, 300 Myr): land lowered 46 m on average, p99 338 m, at strength 0.3 (slice and
Zoom worlds); 137 m at strength 1.0 (`generate`). Inland drainage 3.8% -> 3.2%. The one-sided creep was chosen so
finishing keeps the keyframe's lakes (Jaccard). It does that by not filling hollows, not by modelling where the
material goes.
Options:
- A. Keep it; document in overview §2.11 that finishing sharpens and lowers without depositing.
- B. Route the removed rock with the run's `surface._route` (pits and lakes keep what fits, the rest to the sea)
  once at the end of the passes, and add it to land and coast cells (cheap). Check the PW-057 Jaccard.
- C. Lower the default strength.
Lean: B (sound, and matches the run). A if B costs the Jaccard.

## Updates
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Status needs-decision -> todo. Owner (2026-10-15): approved the lean.
- 2026-10-15: Created from inbox draft draft-audit-surface-hydro-finish-erosion-mass.md (found by audit-surface-hydro).
