---
title: No test runs the split hand-over with dragons and the live polities, so grid-sized state crashed it three ways unseen
type: task
status: todo
parent: null
milestone: v1.0
subsystem: peoples
effort: s
impact: med
found_by: lane305
blocked_by: []
relates: []
refs: [planet/lineages/history/handover.py, planet/lineages/history/polity_live.py, planet/lineages/history/tech_live.py, tests/test_lineages_split.py]
---

## Description
**In plain words.** Every split peoples run (a world refined to a finer grid) on main at 3085f020 stopped after the hand-over:
the dragon cultures, the live tech tree's goods and landmass caches and the live polities' ring table were carried from the
coarse grid (a shape error or an index past the end at the first stored frame or dragon realm). Lane 305 fixed them in
`hand_over`, and found the live polities' town and city ring counts carried silently at their coarse values. The unit test
(`test_split_history_hands_over_at_the_first_farming_and_keeps_the_coarse_past`) uses a fake tree without dragons and its window
ends before the live polities do anything, so none of this ran in tests; each crash showed up only after ~20 min of a real run.

**What breaks if never done.** The next field added to LivePolities, DragonCultures or LiveTech that holds a cell array crashes
the L8 December world again, or (worse) runs with coarse values, and only a full run finds out.

**Do.** A split test on the fake zoom with a dragon kind and a window long enough for a stored frame and a seated realm after
the cut; and a check in `hand_over` that no attribute of the new rule, its tech or its dragon cultures still holds an array of
the coarse cell count.
- [ ] the test fails on 3085f020 and passes now
