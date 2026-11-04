---
id: PW-1143
title: Experimental L8 / L9 finishing state for a world, to get finer peoples placement and mixes
type: task
status: todo
parent: null
milestone: later
subsystem: infra
effort: l
impact: med
found_by: owner
blocked_by: []
relates: [PW-1015]
refs: [planet/lineages/settlements.py, docs/review/owner-desk/]
created: 2026-10-30
updated: 2026-11-03
---

## Description
**In plain words.** The owner (10-30) looked at the settlement pictures. The "mix of peoples" circles are fine, but they suggest the
peoples layer needs more detail than L7 gives. The owner wants to try an experimental L8, and maybe an L9, *finishing state* for one
world. It need not line up exactly with the existing regional zoom. The aim is to see whether finer cells give better definition and
placement of peoples.

Facts to start from:
- The peoples runs on the owner's desk are on **L6** worlds (40,962 cells; e.g. 488d7e, 570701). Showcase worlds are L7 (163,842
  cells). L8 would be about 655k cells and L9 about 2.6M.
- So the cheapest first step is a peoples run on an **L7** world. Then try an L8 finishing state: refine the finished L7 world's
  fields to L8 and run only the peoples history on it. Run time, memory and the viewer's ability to draw it are the unknowns.

To do: measure the cost of the peoples history at L7, and estimate L8 and L9 (time, RAM, output size, and the viewer's frame
rate). Then propose the smallest experiment.
- [ ] a peoples run on an L7 world, with its cost
- [ ] a cost estimate for L8 and L9, and whether the globe viewer can draw 655k / 2.6M cells
- [ ] if feasible, one L8 finishing-state experiment, compared side by side with L7

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: L8/L9 whole-world work, post-v2 (see PW-1198 space-to-ground globe)
- 2026-10-30: Created from inbox draft draft-experimental-l8-l9-finish.md (found by owner).
