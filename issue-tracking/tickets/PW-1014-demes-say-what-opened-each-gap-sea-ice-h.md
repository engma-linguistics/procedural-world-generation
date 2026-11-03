---
id: PW-1014
title: "Demes: say what opened each gap (sea, ice, hard country, or a neighbour moving in); most are neighbours"
type: task
status: todo
parent: PW-981
milestone: v2
subsystem: peoples
effort: s
impact: med
found_by: fun46-demes
blocked_by: []
relates: [PW-981, PW-902]
refs: [planet/lineages/demes.py, "run b69f51", "run 2cb509"]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words: with the flicker gone (gap splits and fusions now have to hold 4 frames), the splits that remain are
real separations that last, but the sea, the ice or the hard country rarely causes them. On b69f51 about four in five
happen because another people holds the strip between the two halves of a population. That is a fair way for a population to
part: a wedge of newcomers. But the tree says only "split off along a gap", so a reader cannot tell a drowned land
bridge from a neighbour's advance.

Measured with the PW-981 follow-up (gap events of 60+ cells; the zone within ~3 cells of both sides; sea, ice or a
corridor change of 0.5 or more between the frame before the event began and the frame it was confirmed):
- b69f51: 114 events, 12 (11%) with a change in the gap (corridor 12, ice 9, sea 0). Of the other 102, the gap is held
  by another people in 90, by sea in 11, and empty in 1. The sea hardly moves on this world in 300 kyr: land runs from
  58,454 to 59,338 cells, and only 947 cells ever change.
- 2cb509: 125 events, 22 (18%) with a change (corridor 17, ice 11, sea 6). Three splits come from a gap drowning (e.g.
  brass dragon 2 on Shurul split from brass dragon 1 on Namo at 276 kyr). No fusion over newly emerged land.
- A wider neck (NECK_KM 240 instead of 120) cuts the count to 70 but not the share (4% with a change), so this is not a
  neck-width question.

What to do: tag each split_gap / fusion event with its cause (sea rose / fell, ice, corridor, "<people> moved in",
"<people> withdrew") and put it in the event text and the workbench hover. That makes land-bridge stories findable
when a world has them (PW-902: ranges following sea level).
- [ ] each gap event names its cause; b69f51's 114 and 2cb509's 125 events classified, counts in the review note

## Updates
- 2026-10-29: Created from inbox draft draft-demes-gap-cause.md (found by fun46-demes).
