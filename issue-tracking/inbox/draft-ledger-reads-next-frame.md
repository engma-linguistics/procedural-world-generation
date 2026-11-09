---
title: The settlement ledger reads density from the next stored frame, so its first towns (and the after-run calendar) come 0.2-0.5 kyr early
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lane258
blocked_by: []
relates: [PW-1597, PW-1596, PW-1608]
refs: ["planet/lineages/settlements.py::derive", "planet/lineages/history/polity_live.py::LivePolities.town_cells", "planet/lineages/history/polity_live.py::LivePolities.begin_step", "planet/lineages/techspread.py::town_footprint", "planet/lineages/techtree.py::Calendar.settled", docs/review/culture/polities/round20.md, docs/review/culture/polities/round20/rebuild_live_foot.py, docs/review/culture/polities/round19/footprint.py, docs/review/culture/polities/round19/live_run.py, "world 4360a3", "world 899985"]
---

## Description
**In plain words.** The settlement ledger is built after a run from the stored frames (every 0.5 kyr). For each century step it
draws the people per cell straight between the frame before and the frame *after* the step, and takes who leads each cell
from the nearer of the two, up to 0.25 kyr ahead. So it sees a little of its own future: a place reaches town size a few
centuries before the history itself had the people for it. With polities in the history (`POLITIES_LIVE`), the history now
counts towns exactly as the ledger does (PW-1608, lane 258), but can only see the present, and counts at the start of a step
(one more century behind). Measured on the same run (round20.md): totals agree within a few per cent, but each people's first
town comes 0.2-0.5 kyr later live (L6 world 4360a3 seed 3 on, 3a52d1bc: humans 10.3 against 10.8 kyr ago, elves 8.7 against 9.1,
triton 5.8 against 6.2), and that alone moves the 12 largest peoples' writing median 307 years on L6 seed 3 (the after-run tree on
the same history: 5,536 ya with the live count, 5,843 with the ledger's) and 106 on L6 seed 7.

Fix by mechanism, in one of two ways (or both): (A) the ledger reads each step from the frames at or before it only (no
look-ahead; the read-out loses an anachronism, as lane 254's ranges fix did, and the default calendar moves later), or (B)
the history counts its towns at the end of each step, after the peoples move, and the tree reads that count from the next step.
A changes the default (switch off) calendar and every settlement's founding date; B touches only the switch-on path.

**What misleads if never done.** The switch-off calendar and every settlement card date a people's first towns, and the
states and writing that follow from them, a few centuries earlier than the history had the people for them; and PW-1597's check
cannot pass, so the switch cannot be flipped (PW-1596): the two calendars stay one or two tree steps apart for a reason that is
the read-out's, not the history's.
