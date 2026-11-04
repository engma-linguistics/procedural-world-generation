---
id: PW-1201
title: Pick one cell-size convention for the grid levels (README, world meta and CLAUDE.md disagree)
type: task
status: todo
parent: null
milestone: later
subsystem: docs
effort: xs
impact: low
found_by: lane88-docs
blocked_by: []
relates: [PW-816]
refs: [README.md, docs/overview.md, CLAUDE.md]
created: 2026-10-31
updated: 2026-11-03
---

## Description
The assumptions audit (finding on the stale overview) also asked to pick one cell-size convention. README.md says
L6 ~110 km and L7 ~55 km; docs/overview.md section 2.1 says ~110 km for L6; world meta `cell_size_km` says 60 and 120;
CLAUDE.md says ~60 km. They differ by centre spacing against sqrt(cell area). PW-816 did not touch it. Pick one (the
centre spacing or sqrt of the area), state which in section 2.1, and make README, CLAUDE.md and the meta agree.
- [ ] one convention, stated once in overview 2.1, used everywhere

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: docs/provenance work, not needed for the planet or the culinary goal
- 2026-10-31: Created from inbox draft draft-cell-size-convention.md (found by lane88-docs).
