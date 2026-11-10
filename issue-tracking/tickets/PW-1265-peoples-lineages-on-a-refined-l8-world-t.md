---
id: PW-1265
title: "Peoples (lineages) on a refined L8 world: the cheap L8 finishing state PW-1143 asks for"
type: task
status: done
parent: PW-1198
milestone: v5
subsystem: infra
effort: m
impact: med
found_by: lane104-refine-l8
blocked_by: []
relates: [PW-1143, PW-490]
refs: [planet/refine.py, "world fb5e11", docs/review/refine-l8/design.md]
created: 2026-11-01
updated: 2026-11-10
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
- 2026-11-10: Status todo -> done. Merged 4bb45871 (lanes 266/267/267b): the split history runs L7 to the first farming (cut 12.0 kyr on seed 7 dnd, sugar cane), hands heads to the refined L8 world exactly (15,167,457.52 before and after), and finishes there. Cost vs L7 run ebd83a on the same code: history 2.7x time, peak memory 3x (35.5 GB). Towns on rivers 30.4% -> 36.0%, none in water; coast 7.0% -> 1.9%, cities 331 -> 119 (PW-1630, folded toward PW-1627); people -8% on one draw (PW-1631). Evidence: docs/review/refine-l8/.
- 2026-11-03: Milestones 11-03: later -> v5: v5 must-have: peoples on the refined world
- 2026-11-03: Triage 11-03: v2 -> later: L8/L9 whole-world work, post-v2 (see PW-1198 space-to-ground globe)
- 2026-11-01: Created from inbox draft draft-refine-peoples-on-a-refined-world.md (found by lane104-refine-l8).
