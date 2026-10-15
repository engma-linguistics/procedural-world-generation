---
title: "Weathering's 200 m continental base level: a floor standing in for 'flat plains don't erode'"
type: task
status: needs-decision
parent: PW-245
subsystem: surface
effort: s
impact: low
found_by: audit-surface-hydro
blocked_by: []
relates: []
refs: [planet/surface.py, docs/review/audit/surface-hydro.md]
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
