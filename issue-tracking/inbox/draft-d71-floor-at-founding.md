---
title: The 1 Mkm2 floor (D71) holds on the failing dnd seeds only if a new people is founded where its habitat patch can hold 1 Mkm2 (twice a founders' country) - decide whether the floor applies at founding
type: task
status: needs-decision
parent: null
milestone: v5
subsystem: peoples
effort: s
impact: high
found_by: lane269c
blocked_by: []
relates: [PW-1558, PW-1182]
refs: ["planet/lineages/history/origins.py::_founders_room", "planet/lineages/history/origins.py::_origin_split", "planet/lineages/history/dispersal.py::_jump", "planet/lineages/history/competition.py::_compete", docs/review/peoples/origins-spread.md, "lane 269c screens, af2677 arm now, dnd s7/j1/j2/j4 (scratch, deleted)"]
---
## In plain words
Daniel ruled (D71) that no land people may end a robustness-suite history under 1 million km2. The small peoples left are not being
pushed down. They are born on a small patch of the land that suits them, such as a cold highland on a tropical continent, and they
fill it. Goliaths and firbolgs are the worst cases. The model's founding size is a "founders' country" of about 0.5 million km2. A
patch that size lets a people be born, but it ends at 0.5-0.9 million km2. If new peoples are only born where the patch can hold 1
million km2, every failing dnd seed tried passes except one firbolg run (0.85). That uses the floor as a founding rule. It is a
design choice, not something the model works out, so it needs Daniel's yes.

## Description
Lane 269c, af2677, arm now, 4 dnd screens (s7, j1, j2, j4). Each arm is compared with lane 269b's branch on the same seeds
(c6907d5b with main 31c3b00d merged):
- 269b's branch: 9 people-runs under 1, not counting drow and troglodytes (goliath in all 4 runs, firbolg twice, kobold, leonin,
  halfling).
- G, patch of one founders' country, plus A, pinned jumps: 3 (goliath j2 and j4, firbolg j2).
- G plus A, with the patch required to hold 1 Mkm2: 1 (firbolg j2, 0.85). Goliath 8.8-33.5 Mkm2.
- A, where a line at the refuge floor may jump into country other peoples hold where it has room, barely fires: 0-2 jumps per
  small people. Dropped.
- At the present, the pinned losers have almost no room of their own on their landmass: 2-26 cells, all held by others.
Options:
- (A) The floor applies at founding: a split's habitat patch must hold max(a founders' country, 1 Mkm2). Otherwise it arises at
  the nearest free country that does, within 8,000 km. Not yet run on the full suite.
- (B) Keep one founders' country (the branch as committed, 32e9fb19). Sky-island endemics stay at 0.5-0.9 Mkm2. List goliath (and
  firbolg) with drow and troglodytes as known exceptions.
- (C) Lower the bar to the model's own refuge floor, 0.5 Mkm2.
Lean: A, because it is the owner's floor stated where it binds. Judge on the full suite against main before merging.
