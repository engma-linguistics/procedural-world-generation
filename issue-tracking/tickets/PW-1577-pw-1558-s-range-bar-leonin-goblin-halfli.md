---
id: PW-1577
title: PW-1558's range bar (leonin/goblin/halfling ranges on af2677 not below main's median) measures the teleport it was meant to remove
type: task
status: needs-decision
parent: null
milestone: v5
subsystem: peoples
effort: xs
impact: med
found_by: lane233
blocked_by: []
relates: [PW-1558, PW-1184]
refs: ["planet/lineages/history/dispersal.py::_refuge_cell", "planet/lineages/history/dispersal.py::_hold_out", tools/peoples_robust.py, docs/review/peoples/origins-spread.md, "lane 233 suite dirs (scratch, gone after reboot): out_main, out_br; compare.py"]
created: 2026-11-09
updated: 2026-11-09
---

## In plain words
Lane 233 made a stem left with no land hold out near its last land, in the nearest free country big enough for a split's founders,
instead of jumping to the world's best cell on another continent. On world af2677 the leonins, goblins and halflings now start where
their stem really lived and end with about 5, 4-6 and 5-8 Mkm2 (main: about 28, 10 and 33). The ticket asked for these ranges to stay
at or above main's median. Main's big ranges came from the jump to an empty continent, so that bar cannot be met without the jump.

## Description
Options:
- A: drop the range bar; judge PW-1558 on swing, brittle count and refuge distance (all improved: see origins-spread.md, lane 233).
- B: keep a range bar but against a non-teleport baseline (e.g. "no people of the four under 1 Mkm2 in any dnd run on af2677").
- C: keep the bar; then something else must give these peoples room (more sea crossings for pre-boat peoples, PW-888's across-sea
  founding weight), which is a separate mechanism, not the refuge.
Lean: B. If never decided, PW-1558 stays open on a bar measured against the teleport itself, and the next lane may put the jump back.

## Updates
- 2026-11-09: Created from inbox draft draft-stem-refuge-range-bar.md (found by lane233).
