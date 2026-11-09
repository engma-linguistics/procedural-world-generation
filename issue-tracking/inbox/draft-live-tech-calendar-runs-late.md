---
title: With polities in the history on, the tech calendar runs late, so states start up to 800 years later than off
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lane248
blocked_by: []
relates: [PW-1466, PW-1472]  # (and PW-1594, not yet on this branch)
refs: ["planet/lineages/history/tech_live.py::LiveTech", "planet/lineages/history/polity_live.py::LivePolities.town_cells", "planet/lineages/techspread.py::town_footprint", docs/review/culture/polities/round18.md, docs/review/culture/polities/round18/live_run.py, docs/review/culture/polities/round16/measure_v1.py, "world 4360a3", "world 899985"]
---

## Description
**In plain words.** With polities inside the history (the switch `POLITIES_LIVE`), the history runs its own tech calendar; with the
switch off, the calendar is built after the run. On the same code (lane 248, round18.md section 2) the live calendar is later: the
first state comes later than off on 3 of 5 pairs (L6 world 4360a3 seed 7: 3,300 against 3,700 years ago; seed 10: 4,900 against
5,300; L7 world 899985 seed 7: 3,300 against 4,100; earlier on L6 seed 3, 6,600 against 6,300, and L7 seed 10, 4,600 against 4,500),
and the 12 largest peoples' median first writing is 160-380 years later on 4 of 5 (L7 seed 7: 4,079 against 4,462 years ago; L7
seed 10: 4,544 against 4,795; L6 seed 7: 3,005 against 3,347; the same on L6 seed 3). The state count *now* matches off after PW-1594's fix, so this is about when states begin, not how many there are.

A likely part, not tested: the town footprint the live tree reads (D52's town arms B and E) is `LivePolities.town_cells`, which
counts only the lead people's best-of-ring places that are town-sized this step; the read-out's `techspread.town_footprint` counts
every ledger site of town size, the second peoples' own places and towns still shrinking included. Fewer town cells, later arms.
Round 14 found the live calendar about 170 years late too. Diagnose first (feed the live tree the read-out's footprint shape on one
seed and see whether writing moves back), then fix by mechanism.

**What misleads if never done.** If the switch is flipped on, every state's founding date on the cards and the Polities layer's
first states move a few centuries later than today's read-out shows, and the date writing arrives with them; a reader comparing
worlds made before and after would read a real change in history that is only the calendar's inputs.
- [ ] live and read-out first-state dates and writing medians within ~100 years on L6 seeds 7, 3, 10 and L7 seeds 7, 10, same code
