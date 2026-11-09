---
id: PW-1608
title: With polities in the history on, the live tech tree counts a third more town cells than the ledger at L7, so writing comes early
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lane254b
blocked_by: []
relates: [PW-1597, PW-1596, PW-1472]
refs: ["planet/lineages/history/polity_live.py::LivePolities.town_cells", "planet/lineages/techspread.py::town_footprint", "planet/lineages/techtree.py::rebuild", docs/review/culture/polities/round19.md, docs/review/culture/polities/round19/footprint.py, docs/review/culture/polities/round19/replay.py, docs/review/culture/polities/round19/live_run.py, docs/review/culture/polities/round16/measure_v1.py, "world 899985", "world 4360a3"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** With polities inside the history (`POLITIES_LIVE`), the history runs its own tech calendar, and one of its
inputs is how many town-sized places each people has (the "town footprint"). Lane 254 made the history count these places the
way the settlement ledger does (81fc3851). At L6 that brought the two calendars together; at L7 the history now counts more town
cells than the ledger does, so its peoples learn writing earlier than the after-run calendar gives on the very same history.

Measured on 81fc3851 (lane 254b, round19.md section 4; scratch runs, deleted after the lane):
- L7 world 899985 seed 7, switch on (run 4d304e): live footprint against the same run's ledger footprint, 3 kyr ago 4,252 / 2,811
  town cells, 1 kyr ago 6,128 / 5,737. The live calendar's writing median (12 largest peoples) is 4,079 ya; `techtree.rebuild` on
  the same history gives 4,305 ya (the switch-off run's own calendar: 4,305 ya).
- L7 seed 10, switch on (00331e): live / ledger footprint 2 kyr ago 3,015 / 2,197, 1 kyr ago 5,859 / 4,734; writing 4,305 ya live
  against 4,795 ya rebuilt on the same history.
- Replays of the after-run tree on 4d304e (`round19/replay.py`: regions and goods on the range of the time, starts, tamings)
  give 4,305-4,462 ya, never the live 4,079: the residual is a live-only input, and the footprint is the one that is off.
- At L6 (world 4360a3 seed 7) the live count was also above the ledger mid-history (3 kyr ago 2,770 against 2,422) but writing
  matched (3,005 on both).

Likely place to look: `LivePolities.town_cells` counts every cell whose sized place reaches town size, while the ledger keeps
one site per place spacing; at L7 there are four cells to every L6 cell, so a per-cell count grows with resolution. Fix by
mechanism (count as the ledger places sites), then re-check the five pairs.

**What misleads if never done.** PW-1597's done-check fails at L7 (first state 400 years earlier with the switch on, L7 seed 7),
so the switch cannot be flipped on (PW-1596); if it were, every L7 world's first states and writing would read centuries earlier
than the same history gives with the switch off, for a counting reason, not a historical one.
- [ ] live and after-run town cells within ~10% at L6 and L7 on the same run; then PW-1597's five pairs within ~100 years

## Updates
- 2026-11-09: Created from inbox draft draft-live-town-cells-overcount-l7.md (found by lane254b).
