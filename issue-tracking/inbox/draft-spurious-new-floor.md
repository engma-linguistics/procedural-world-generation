---
title: New ocean floor appears in sampling gaps where plates converge
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: low
found_by: tectchurn
blocked_by: []
relates: [PW-108, PW-053]
refs: [planet/tectonics/plate_kernels.py]
---

## Description
`plate_kernels.resolve` makes any world cell no plate covers new 7 km ocean
floor of age 0 (a ridge), unless one plate surrounds it and `_fill` can patch
it. At L6 s21 300 Myr, of ~1230 new-floor cells per step, ~71 sit amid floor
older than 20 Myr and ~47-89 were continental the step before (27-47 of them
with >= 3 continental neighbours); some of these are real rifts, some are
sampling gaps at converging or sliding boundaries. Tried on tectchurn (not
kept): fill a gap whose neighbouring plates don't pull apart across it
(relative velocity . separation <= 0) from the neighbours with last step's
crust type. No measurable churn gain (noise between runs is larger), so not
kept. Effect on sea level (young floor is shallow, PW-053) is likely small
(~6% of new floor). Decide whether worth doing for correctness.
