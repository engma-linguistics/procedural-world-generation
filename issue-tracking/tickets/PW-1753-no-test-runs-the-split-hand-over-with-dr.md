---
id: PW-1753
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
refs: [planet/lineages/history/handover.py, planet/lineages/history/polity_live.py, planet/lineages/history/tech_live.py, tests/test_lineages_split.py, "planet/lineages/history/handover.py::hand_over", "planet/lineages/history/polity_live.py::DragonCultures", "planet/lineages/history/polity_live.py::_Rings", "planet/lineages/history/polity_live.py::is_dragon", "tests/test_lineages.py::_raw", docs/review/catalogue/plan.md, "scratch world 20b777 (refined from 899985), /data/personal/scratch/lane307/logs/split-crash1.log"]
created: 2026-11-11
updated: 2026-11-11
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

## Updates
- 2026-11-11: Merged inbox draft draft-split-handover-test-has-no-dragons.md ("The split history's hand-over test has no dragon people, so a grid-bound object added to the live rule crashes the L8 split unseen", found by lane307).
  **In plain words.** The L8 split peoples run (deep time on L7, settled history on the refined L8 world) crashed on current
  main the first time a tree with dragons reached the hand-over: seven_meals on 20b777 (899985 refined to L8), at step ~350
  of 477, `ValueError: operands could not be broadcast together with shapes (655362,) (163842,)` in
  `DragonCultures.step`. The dragon cultures (merged 11-10, live dragon realms) and the realm rings `_ring_of` are objects,
  so `hand_over`'s carry-over (`R.auto`) kept them on the coarse grid. Lane 307 fixed both (handover.py makes them on the fine
  grid and carries the labels and dates by kind), but the split test (`test_split_history_hands_over...`) uses the small
  `_raw()` tree, which has no line `is_dragon` accepts ("dragon" in the id and the trait `flies`), so the dragon code never
  runs in it and the crash was invisible to the suite.
  
  **What breaks if never done.** The next object with per-cell state added to the live rule (or to `LiveTech`) is carried
  coarse again, and the December world's split run dies after ~35 min of L7 history, found only by whoever runs a real L8
  split (2+ h).
  
  **Do.**
  - [ ] give the split test's tree (or a second test) a dragon line that holds land inside the demes window before the cut,
    so `_dragon_cultures` runs on both sides of the hand-over
  - [ ] a generic check after the hand-over: every attribute of `h.rule` (and `h.rule.tech`) that holds a per-cell ndarray,
    directly or one object deep, has the fine grid's length
- 2026-11-11: Created from inbox draft draft-split-handover-live-state-test.md (found by lane305).
