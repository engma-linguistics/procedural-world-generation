---
id: PW-023
title: "Decision: wave and tide fitted constants"
type: task
status: done
parent: null
subsystem: coast
effort: xs
impact: low
found_by: deltas
blocked_by: []
relates: []
refs: ["morning_decisions@bdc967f item 4", planet/coast.py, tools/coast_check.py, "world 0f7abd"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The wave and tide formulas in `planet/coast.py` are physical (fetch-limited wind sea, swell decay,
shelf resonance, funnelling), but ~10 constants were fitted on Earth by grid search: wave power within
2× at 25 of 30 coasts, tides within 2× at 21 of 23 sites. Delta thresholds: lagoons above wave weight
0.3, fingers above river weight ~0.4, "mixed" below 0.5. Demo zooms 00975d (river), f81832 (wave),
ce4b72 (tide) on world 0f7abd. Question: are fitted constants OK?

## Updates
- 2026-10-14: Owner's answer: fine. Closed.
- 2026-10-14: Migrated from docs/morning_decisions.md item 4.
