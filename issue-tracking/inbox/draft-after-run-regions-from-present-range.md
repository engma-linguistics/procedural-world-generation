---
title: "Tech tree: the after-run tree takes its region learners from today's range for all time, so kingship comes earlier than in the live tree"
type: task
status: todo
parent: PW-661
milestone: later
subsystem: culture
effort: m
impact: low
found_by: lane-200
blocked_by: []
relates: [PW-1471]
refs: ["planet/lineages/techtree.py::rebuild", "planet/lineages/history/tech_live.py", docs/review/culture/techtree/round2.md, docs/review/culture/techtree/round2/check_f72bf3.txt]
---

## Description
**In plain words.** Each region of a people is a learner (D55). The tree built inside the history (POLITIES_LIVE on) sees a people's
regions as its range was at each stored frame, so a people that is small early has few learners early. The tree built after the run
(the default while POLITIES_LIVE is off) has only today's range, and uses today's regions for all of history. So it gives a people
its full set of learners from the start, too early. On the switch-on check run f72bf3 (899985 L7, dnd, seed 7, lane 200b's
defaults), writing agrees: 12 of the 12 biggest peoples' live dates fall inside the after-run tree's 12-draw spread. Kingship does
not: only 8 of 12 do. In all 12 peoples the live kingship is later than the after-run tree's on the same draw (elves 243 against
1,099 years ago). Lane 196's run c19b5c (regions and arms off) had 12 of 12 for both.

**What breaks if never done.** With POLITIES_LIVE off, region learners make a people's urban techs a little early. The showcases'
first writing still sits inside main's range (round2.md), so this is a fidelity gap, not a failure. The fix is to save each frame's
regions (or their dated arrivals and shares) in meta and have `rebuild` read them, as the live tree does.
