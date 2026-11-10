---
id: PW-1631
title: The split history's settled window on L8 ends with 8% fewer people than the same world all on L7 (one draw; signal or chaos?)
type: task
status: todo
parent: PW-1198
milestone: v5
subsystem: peoples
effort: m
impact: med
found_by: lane267b-pw1265
blocked_by: []
relates: [PW-1265, PW-1627]
refs: [docs/review/refine-l8/split.md, "planet/lineages/history/handover.py::hand_over", "planet/lineages/history/handover.py::heads_split", "planet/lineages/recent.py::finer", "run 025b98 (split, scratch root l266/root, may be gone)", "run ebd83a (L7 baseline, scratch)", "world 5d09cc (scratch)"]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words
Moving the history onto the finer grid at the first farming keeps every person exactly (15,167,457 before and after the
move), but by the present the split run has 980 million people against 1,069 million when the same world's history runs all
on L7 (humans 564 M against 694 M, orcs 114 M against 148 M). One draw cannot say whether the fine grid grows fewer people
or the run simply went another way. If it is the grid, every L8 world understates its peoples' numbers, and the towns,
states and trade built on them.

## Description
Split run 025b98 (5d09cc, L7 to 12 kyr, then L8) against L7 run ebd83a (899985), same code, dnd tree, one try, seed 7;
totals summed from run.txt's per-line people. Candidates to check, cheapest first: (a) re-roll 2-3 tries of both and compare
the spread; (b) the prolonged L7 frames' coasts against the refined world's land (the last frame's land agrees with 5d09cc's
on 98.7% of cells; 227,424 against 233,563 land cells), so carrying capacity on the fine coast may be lost; (c) K and the
ladder's density remade on the fine land in the first step after the hand-over (handover.hand_over).
- [ ] pass rates/totals over re-rolled draws before calling it signal
- [ ] if signal: name the mechanism; do not rescale to match L7

## Updates
- 2026-11-10: Created from inbox draft draft-l8-settled-window-fewer-people.md (found by lane267b-pw1265).
