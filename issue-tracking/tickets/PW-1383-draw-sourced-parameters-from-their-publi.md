---
id: PW-1383
title: Draw sourced parameters from their published ranges (optional, per world)
type: task
status: done
parent: null
milestone: v2
subsystem: peoples
effort: s
impact: low
found_by: Daniel 11-02
blocked_by: []
relates: [PW-1350]
refs: [planet/lineages/ladder.py, docs/review/peoples/density-ladder/ladder.md]
created: 2026-11-02
updated: 2026-11-03
---

## Description
In plain words: where a density-ladder or peoples number comes from a source that gives a range (e.g. Binford's forager densities, the plough and irrigation densities), let each world optionally draw its value from that range instead of the fixed central value, seeded by the world. Off by default; a setting turns it on. Needs the ranges written beside each constant (ladder.md has most) and one helper that draws them.

## Updates
- 2026-11-03: Status in-progress -> done. Merged cfd7d1cf (lane 145): planet/lineages/ranges.py, meta.draw_ranges off by default (identical densities when off), seeded by meta.seed, recorded in run.json; workbench tick box. 8 numbers drawn, the rest listed in ranges.FIXED with reasons. Full suite 958 passed. Write-up docs/review/peoples/ranges/round1.md. Follow-ups PW-1400 (rung order, needs-decision), PW-1401, PW-1402.
- 2026-11-03: Status todo -> in-progress. Lane 145 started 11-03.
- 2026-11-02: Created.
