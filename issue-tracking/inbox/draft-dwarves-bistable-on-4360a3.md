---
title: "The dnd dwarves are bistable on world 4360a3 seed 7 (about 4% or 16% of all people): a do-nothing nudge flips them"
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: m
impact: med
found_by: lane176
blocked_by: []
relates: [PW-1207]
refs: [docs/review/peoples/ledger/round1.md, tools/peoples_robust.py, "world 4360a3"]
---

## Description
**In plain words.** On one of the two test worlds, the dwarves end up at one of two sizes: about 4% of all people, or about 16%.
A change that should do nothing (one timescale, 1.0 -> 1.01 kyr) tips them from one to the other. So do six of the ledger's
switch-offs. The humans make up the difference (38% -> 27-30%).

**What breaks if it is never done.** Any one-try comparison on dnd-s7@4360a3, such as a lane judging a change on the robust suite,
reads the dwarf flip as the change's effect. Round 1 of the ledger had to discount it for war-torn land, hold lapse, crowding,
carry, den and LEARN_GAIN. A campaign world could also land on either outcome from a trivial nudge.

- Measured (lane 176, one try each, main b53ccd24): base 4.4% (3.15 Mkm2). `TAU_KYR` 1.01: 15.5% (10.6 Mkm2). `LAND_Q` 0: 16.6%.
  `HOLD_MIN` 0: 16.2%. Crowd exploration off: 16.3%. `CARRY` 0: 16.9%. Den 0: 15.7%. `LEARN_GAIN` x0.8: 14.0%.
- [ ] find the branch point: which step the two outcomes part at (the dwarves' first contact with the humans in the mountains?)
- [ ] say whether it is a real tipping point (fine, report it) or a threshold artefact (EST, HOLD_MIN, BRAKE_HOLD)
