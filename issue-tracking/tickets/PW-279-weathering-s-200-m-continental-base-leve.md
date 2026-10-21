---
id: PW-279
title: "Weathering's 200 m continental base level: a floor standing in for 'flat plains don't erode'"
type: task
status: done
parent: PW-245
milestone: v1
subsystem: surface
effort: s
impact: low
found_by: audit-surface-hydro
blocked_by: []
relates: []
refs: [planet/surface.py, docs/review/audit/surface-hydro.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
surface.py:247-250 wears continental ground toward 200 m, not toward sea level ("continental interiors settle
~200 m up"). Isostasy already puts a normal 35 km continent at 250 m. Here the floor stops the relief-independent
weathering term from planing old plains to the sea. Measured (L5 seed 1, 300 Myr): base 0 would remove 1.45x as
much by weathering. It props land area up a little (an envelope and scorecard metric). It has been there since
the first erosion commit (fe56a31); it was not added for a metric.
Options:
- A. Keep it; document it as a stand-in.
- B. Base 0, with the weathering rate scaled by local relief (e.g. x min(1, relief / R0)), so flat plains stop by
  themselves; retune `erosion_timescale` at L6 (scorecard land %).
Lean: A for now (low impact); B if the land fraction is retuned anyway.

## Updates
- 2026-10-15: Status in-progress -> done. A: kept and documented (merged 4d3b46f).
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Status needs-decision -> todo. Owner (2026-10-15): approved the lean.
- 2026-10-15: Created from inbox draft draft-audit-surface-hydro-base-level.md (found by audit-surface-hydro).
