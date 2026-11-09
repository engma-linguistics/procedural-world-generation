---
id: PW-1606
title: The dry-hollow recheck reroutes rivers up to 25 times per lakes() call (+15% L7 run time)
type: task
status: todo
parent: null
milestone: later
subsystem: hydrology
effort: m
impact: low
found_by: scout251b
blocked_by: []
relates: [PW-054]
refs: ["planet/hydrology.py::lakes", "planet/hydrology.py::_settle", "planet/hydrology.py::_dry_hollows", "planet/hydrology.py::route", docs/review/basins/scout251.md, docs/review/basins/scout251/bench.sh, docs/review/basins/scout251/prof.py]
created: 2026-11-09
updated: 2026-11-09
---

## Description
PW-054 pass 3 (scout 251, merged) keeps closed hollows whose catchment is dryland. After the rivers settle,
`_settle` rechecks every kept hollow (catchment turned wet, or its lake spills) and reruns when one is dropped,
in every carve try. Profile of one erosion-step `lakes()` call on L7 seed 11 at ~200 Myr (`prof.py`): 0.50 s
against 0.25 s with the rule off; `route()` is about half of it (25 calls per `lakes()` call), `_dry_hollows`
only 0.03 s. Bench (`bench.sh 30`, L7, 4 threads): 30 Myr in 85.9 s against main's 74.6 s, +15% run time
(baseline: main 935ddd0e in the same bench).

If never done: every run stays ~15% slower at L7 than before the rule (about 5-6 more minutes per Gyr), with no
change in output. Nothing is wrong, it is cost only.

What to try: recheck only the basins downstream of a dropped hollow instead of rerouting the whole grid; or
reuse the first try's routing when the carve leaves the kept hollows' catchments unchanged.
- [ ] same `lakes()` outputs (golden unchanged), `lakes()` call <= ~0.35 s on the same profile state

## Updates
- 2026-11-09: Created from inbox draft draft-dry-hollow-recheck-cost.md (found by scout251b).
