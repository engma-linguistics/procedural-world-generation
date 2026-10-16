---
title: "Giant run-frame lakes doubled when sea level came down ~130 m (PW-293); evidence for PW-300"
type: task
status: todo
parent: null
subsystem: hydrology
effort: xs
impact: low
found_by: pw293
blocked_by: []
relates: [PW-300, PW-293]
refs: [docs/review/audit/pw293-sea-level.md, docs/review/health-pw293-before/, docs/review/health-pw293-after/]
---

## Description
Evidence for PW-300 (coordinator: probably `--merge-into PW-300`). PW-293 moved the run's median sea level
from +148 to +15 m (health --quick, 8 L6 seeds x 500 Myr, same seeds). Keyframes whose biggest lake is over
1 Mkm2 rose from a mean of 5.2% per run to 9.6% (per seed before -> after: 1: 2.7 -> 10.6, 2: 3.5 -> 1.8,
11: 4.4 -> 14.2, 21: 10.6 -> 18.6, 3199: 2.7 -> 11.5, 42: 2.7 -> 1.8, 77: 13.3 -> 10.6, 505: 1.8 -> 8.0), and
lake_max spells outside the envelope 34 -> 40. The lake share of land is unchanged (median 0.5%) and the land
share is unchanged (33.4 -> 33.5%), so this isn't more land. Likely mechanism: a sea ~130 m lower leaves
low continental interiors that a +150 m sea used to flood as epicontinental seas above the sea, as closed
basins that fill into giant lakes. If so, PW-300's giant lakes depend on how deep the low interiors are (the
erosion base level, sag, PW-054's closed basins), not on sea level, and a fix there should be checked at
today's sea level. Not checked cell by cell; the 8 seeds diverge chaotically, so part of it may be chance.
