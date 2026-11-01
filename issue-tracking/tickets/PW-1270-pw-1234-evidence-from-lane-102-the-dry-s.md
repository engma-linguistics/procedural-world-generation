---
id: PW-1270
title: PW-1234 evidence from lane 102, the dry shift is not in 36 re-rolled draws; trees and NPP still untested
type: task
status: todo
parent: null
milestone: null
subsystem: climate
effort: s
impact: low
found_by: lane102
blocked_by: []
relates: [PW-1234, PW-1229, PW-1223]
refs: [docs/review/v1-cut/final-tally.md, tools/hard_bar.py]
created: 2026-11-01
updated: 2026-11-01
---

## Description
In plain words: PW-1234 asked whether the drier scorecard (dry land 18.8 to 22.9%) after the inland-pits merge is a shift or
chaos. Lane 102 re-ran the 36 L6 re-rolled draws on today's code and compared them with lane 92's run on the older code:
arid land is 23.1% before and 23.2% now, a paired difference of +0.09 points (standard error 0.54), up in 20 of 36 draws.
The six scorecard seeds again read 23.0% dry (the same worlds as lane 98's 22.9%). So the dry rise is the old baseline's six
worlds being low, not a model shift. What is not settled: the scorecard's NPP (412 to 372) and tree cover (41.2 to 36.0%)
also fell, and the draws' tree column cannot test it (it is a median that includes the pre-vegetation updates).
- [ ] Either close PW-1234 on the dry evidence, or run scorecard seeds 7-12 and 13-18 on both codes for NPP and trees.
- [ ] The 8-fold-fall crash definition (D32 candidate) flags 25 of 42 draws as written, so it is not a rare-event line;
      if it is ever used as a bar it needs a depth or a late-window clause. Daniel has ruled option B, so this is only a note.

## Updates
- 2026-11-01: Created from inbox draft draft-pw1234-dry-shift-evidence.md (found by lane102).
