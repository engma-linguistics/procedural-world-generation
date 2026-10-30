---
title: "Dragons jump about 3x at 30 kyr ago, where a peoples run changes from its glacial pass to its recent pass (2a7385 roll 7000: 22,800 to 76,100)"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: dragon-density-doc
blocked_by: []
relates: [PW-977, PW-990]
refs: [docs/review/megafauna/dragon-density/index.html, docs/review/megafauna/dragon-density/charts/time.png, planet/lineages/recent.py]
---

## Description
**In plain words.** On the dragon-density page's Figure 4, the number of dragons on one world triples in one step 30,000 years ago, exactly where the run switches from its coarse glacial pass to its fine last-30,000-year pass. Nothing in the world changes there, so the jump is probably the switch itself.

Fun lane 45b's probe (docs/review/megafauna/probe.py, world 2a7385 roll 7000, the default model) has dragons at 22,823 at 30.0 kyr ago
and 76,077 by the next frames (29.5 kyr: 70,971). With the pressure off (`--no-press`) the same step is 524,621 to 653,081 (+25%).
Before 30 kyr the run is in its `glacial` epoch (planet/lineages/history/steps.py), after it in `recent` (RecentParams.kyr = 30).
Not traced. Candidates: the prey field or the people's density read differently in the two passes (climate fields, ice), the
pressure computed on a different land mask, or the eras' presence values resetting.
- [ ] find which input to the dragon count changes at the pass boundary
- [ ] either make the passes agree or say on the review page why they differ
