---
title: "Arm S: 11-15% of settled D&D peoples still lack a state tech today; printing at 0.5 kyr ago drops to 7% on 0141d1"
type: task
status: todo
parent: PW-661
milestone: later
subsystem: culture
effort: s
impact: med
found_by: lane-207
blocked_by: []
relates: [PW-1490]
refs: [docs/review/culture/techtree/round3.md, docs/review/culture/techtree/round3/lag.py, docs/review/culture/techtree/round3/tables.py, "planet/lineages/techtree.py::Calendar.settled", "planet/lineages/techtree.py::Calendar.can", "planet/lineages/techspread.py::town_footprint", planet/lineages/samples/techtree.toml, "runs 0141d1 3e0eb4 07c755"]
---

## Description
**In plain words.** The new rule (D60 B, arm S) says only peoples with towns of their own take up writing, kingship, law, taxes and
coinage. It works: foragers and herders without towns no longer write, and the fast techs are unchanged. But a few peoples that do
have towns now miss a state tech they would have had before. Where that happens, the viewer shows a town-holding people without
law or coinage for no visible reason.

**Measured** (round3.md section 2; 8 draws on each run; the baseline is main at faa4fb8c):
- The share of settled admin cases that never take the tech rose from 7% to 15% on 0141d1, and is 11% on 3e0eb4 and 1% on 07c755.
- On 0141d1, 44 of those cases are peoples whose towns later shrank below one cell, so the gate rightly closed again; 109 still have
  towns now.
- On 3e0eb4 it is 88 who lost their towns and 36 who still have them.
- Likely cause for the rest: the downstream state techs (law, coinage) now have fewer givers, so their fronts are slower. A town
  count that flickers around 1 may also re-close the gate.
- Printing (downstream of writing) at 0.5 kyr ago fell from 72% to 7% of peoples (median of draws) on 0141d1. It is 62% on 3e0eb4
  and 28% on 07c755.

**What breaks if never done.** The viewer and briefs show settled peoples without law or coinage, and very little printing on
0141d1. That is a misleading "who knows what" for exactly the peoples that should have it.

**To try.**
- [ ] Split the "still has towns" cases by tech and by whether the town count stayed at 1 or more since the ready date.
- [ ] If they flicker: read "settled" as having had a town within the last few centuries. That is a mechanism, not a tuned threshold.
- [ ] Check printing's chain (libraries, paper) for a step that the gate starves.
