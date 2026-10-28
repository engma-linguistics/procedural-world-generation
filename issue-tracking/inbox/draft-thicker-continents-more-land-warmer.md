---
title: "After the weld fix (PW-970) land is 31 -> 35% of the surface and finish moments run ~0.9 C warmer"
type: task
status: todo
parent: null
milestone: v1
subsystem: tectonics
effort: m
impact: med
found_by: lane23
blocked_by: []
relates: [PW-970, PW-950, PW-293, PW-865]
refs: [planet/tectonics/crust.py, docs/review/tectonics/crust/crust.md]
---

## Description
Lane 23's coherence fix (a607c614) takes thin welded margin crust out. In the paired L6 1 Gyr set (36 draws
each, 600-1000 Myr means, median over draws), continental crust goes 32.6 -> 34.2 km and continental area
41.8 -> 41.3%. But land goes 31.3 -> 34.8% (Earth 29). Drowned continent falls from ~10.5% to ~6.5% of the
surface (Earth ~12). Its median depth is -1519 -> -819 m, so less continent lies under the sea.

The pass rate went 31/36 -> 28/36 (both pass 25, main only 6, branch only 3). All 6 lost draws were too warm
at the finish moment (+4.8 to +11.1 C). The median end temperature is +0.85 against -0.05 C.

Not looked into: why more land runs warmer here, and whether the sea level's own steady ocean (PW-293,
SEA_TECT_MAX ~400 m) should now sit higher with less ocean basin taken by drowned margins. Candidates: the
weathering balance's land/area terms (PW-865's end-anchored GEOCARB frame), the land albedo/ice terms, and
sea level.
- [ ] find what warms the branch's finish moments (one warm draw, e.g. seed 639472 r0.001 l6fix: +11.1 C
  against main's -3.6 C, traced through ice_diag's CO2 source/sink and albedo terms)
- [ ] land back within ~29-33% at L6 without thinning the crust again
