---
id: PW-020
title: "Decision: which viewer layers draw lakes"
type: task
status: done
parent: null
subsystem: viewer
effort: s
impact: low
found_by: lakes
blocked_by: []
relates: [PW-082]
refs: ["morning_decisions@bdc967f item 1", "run 8dc2f2", viewer/index.html]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Lakes show on the run globe (demo run 8dc2f2, elevation layer, t≈180–360), drawn only on elevation and
biome, because on the Köppen and rainfall layers the map's blues and greens get confused with lakes.
- **A (current):** lakes on elevation and biome only.
- **B:** lakes on every layer with a dark outline.
- **C:** a "Lakes" overlay toggle, like Rivers, that works on any layer.

Coordinator's lean was C.

## Updates
- 2026-10-14: Owner's answer: the current implementation (A) is fine; don't chase B or C. Closed.
- 2026-10-14: Migrated from docs/morning_decisions.md item 1.
