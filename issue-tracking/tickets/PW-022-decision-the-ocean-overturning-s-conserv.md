---
id: PW-022
title: "Decision: the ocean overturning's conservative choices"
type: task
status: done
parent: null
subsystem: ocean
effort: s
impact: high
found_by: ocean
blocked_by: []
relates: [PW-013, PW-026]
refs: ["morning_decisions@bdc967f item 3", docs/proposals/ocean_overturning.md]
created: 2026-10-14
updated: 2026-10-14
---

## Description
The overturning (`planet/ocean.py`) shipped with: (a) a spin-up rule for the North Atlantic on-state,
because the rain has almost no Atlantic–Pacific evaporation contrast; (b) rain doesn't see the ocean's
warming (one extra temperature pass); (c) +0.17 s per climate step (~35%; ~15 s per 1 Gyr L6 run);
(d) the rest of W Europe's winter error (~4.8 °C too cold) is in the air model, not the ocean.
Question: is a spin-up rule acceptable as nudging? Full text in `docs/proposals/ocean_overturning.md`.

## Updates
- 2026-10-14: Owner's answer: spin up its own plan. Superseded by the rain/moisture-transport epic PW-013 (a, b) and the air-model ticket PW-026 (d); (c) accepted. Closed.
- 2026-10-14: Migrated from docs/morning_decisions.md item 3.
