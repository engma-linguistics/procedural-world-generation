---
id: PW-1265
title: "Peoples (lineages) on a refined L8 world: the cheap L8 finishing state PW-1143 asks for"
type: task
status: todo
parent: PW-1198
milestone: v2
subsystem: infra
effort: m
impact: med
found_by: lane104-refine-l8
blocked_by: []
relates: [PW-1143, PW-490]
refs: [planet/refine.py, "world fb5e11", docs/review/refine-l8/design.md]
created: 2026-11-01
updated: 2026-11-01
---

## Description
**In plain words.** PW-1143 wants peoples placed on a finer (L8) finish of an L7 world. `planet refine` now makes
exactly that: a normal L8 world from a finished L7 one, in about 5-10 minutes instead of a 2-hour L8 simulation.
A regional zoom (49 s) and highlights (39 s) of the refined world fb5e11 work. A peoples run on it was not tried.

The peoples history starts from a glacial time zoom of the run (`lineages` reads the run's frames). A refined world
has no L8 run behind it: its source run is L7. So either the lineages step runs on the L7 time zoom and its result is
mapped onto the refined grid, or the time zoom's frames are refined too.
- [ ] find what `planet lineages` needs from the run's grid, and try one dnd try on a refined world (or say what blocks it)
- [ ] if it runs: cost against the L7 try (~66 min, 11 GB) and a side-by-side of the peoples map

## Updates
- 2026-11-01: Created from inbox draft draft-refine-peoples-on-a-refined-world.md (found by lane104-refine-l8).
