---
id: PW-432
title: PW-300's valley memory lowers lake share and inland drainage a little (lakes 0.43 -> 0.34% of land, inland 3.8 -> 3.4%); evidence for PW-054
type: task
status: todo
parent: null
subsystem: hydrology
effort: xs
impact: low
found_by: pw300
blocked_by: []
relates: [PW-054, PW-300]
refs: [docs/review/health-pw358-after/, docs/review/health-pw300-after/]
created: 2026-10-16
updated: 2026-10-16
---

## Description
For PW-054 (coordinator: probably `--merge-into PW-054`). PW-300 gave the run a memory of the valleys rivers
to the sea cut (isostasy.EXTRA `valley`, hydrology.lakes' `valley`): a basin that stops spilling keeps its
outlet gap. Health --quick, 8 L6 seeds x 500 Myr, frames after 50 Myr, before (health-pw358-after) -> after
(health-pw300-after): lakes median 0.43 -> 0.34% of land (frames below the 0.2% envelope 17 -> 24%), inland
drainage median 3.8 -> 3.4%, p90 10.0 -> 7.9% (the >30% ice-age spike of seed 11 gone). So part of the
run's closed-basin area was basins that had lost their outlets, not tectonic basins. Earth's ~18% inland
needs basins that stay closed for real reasons (sinking, rain shadows, rims rising faster than rivers
cut); the run still makes few (PW-054). A variant that kept the deepest valley ever cut on active rivers
(not graded to the river now) lowered lakes to 0.25% and inland to 2.0%: not landed.

## Updates
- 2026-10-16: Created from inbox draft draft-pw300-lakes-inland-lower.md (found by pw300).
