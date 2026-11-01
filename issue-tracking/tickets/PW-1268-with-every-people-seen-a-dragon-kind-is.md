---
id: PW-1268
title: "With every people seen, a dragon kind is one to five living cultures, not one: keep that or fold it?"
type: task
status: todo
parent: PW-670
milestone: null
subsystem: timezoom
effort: s
impact: med
found_by: lane109
blocked_by: []
relates: [PW-1259, PW-670, PW-981]
refs: [planet/lineages/cultures.py, planet/lineages/demes.py]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words: now that the history stores every people's presence (PW-1259), a dragon kind no longer drops in and out
of the record. Its demes come from where it really lives, cut where gaps are wider than a dragon flies (1,500 km). On the
L6 test run each dragon kind came out as one to five living cultures (gold 3, brass 4, red 4, green 5, black 1), where
round 2 had hoped for one each. Giants: cloud 3, frost 4, hill 3, storm 5.

Round 2's "rejoin" rule (a cohesive kind's returning pockets join its first culture) is removed: with the full record it
changed nothing on the test run (one culture, fire giants, 1 vs 2), because the kinds no longer vanish and come back.

The choice for Daniel:
- (a) Keep it: dragons on continents more than 1,500 km apart drift into separate cultures, as the reach rule says.
  Cohesion still pulls their ways toward the kind's mean and makes sisters merge ten times faster when they touch.
- (b) Fold it: a kind with cohesion at or above some level (0.9: the dragons) is one culture wherever it lives, as if
  word travels between dragons over any distance. That is a special case in cultures.py, which round 2 tried to avoid.
- (c) Scale the time apart by cohesion: a dragon pocket needs t_apart / (1 - cohesion) apart (6 kyr in the stone age at
  0.9) before it counts as a culture of its own.

Also seen: with every cell counted, a giant culture on the coast "gains the sea craft" (hill giants 0.02 -> 0.69 on the test
run). Check whether giants should have sea craft at all (they wade straits), like fliers have none.

## Updates
- 2026-11-01: Status needs-decision -> todo. Owner 2026-11-01 (D36): B, keep the splits; a dragon kind may be several cultures.
- 2026-11-01: Created from inbox draft draft-dragon-kinds-several-cultures-with-full-presence.md (found by lane109).
