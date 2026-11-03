---
id: PW-1390
title: "Checkpoints deep-copy the whole state before shrinking it: shrink first"
type: task
status: todo
parent: null
milestone: v2
subsystem: store
effort: s
impact: low
found_by: speed report 11-03
blocked_by: []
relates: [PW-801]
refs: [docs/review/speed/l9-memory.md, planet/tectonics/simulation.py]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: every 100 Myr the run copies its full state (simulation.py:199, called from store.py:945) and holds it while a thread pickles it: 1.35 GB at L7, ~22 GB at L9 (estimate), mostly empty plate slots. Shrinking first (store.shrink_state already knows which cells matter) keeps the checkpoint the same. See docs/review/speed/l9-memory.md.

## Updates
- 2026-11-03: Created.
