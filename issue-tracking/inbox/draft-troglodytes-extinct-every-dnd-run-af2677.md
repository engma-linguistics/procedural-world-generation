---
title: Troglodytes die out ("no habitat left") in every dnd run on af2677, and drow end under 1 Mkm2 in every run
type: task
status: todo
parent: null
milestone: null
subsystem: peoples
effort: m
impact: med
found_by: lane269b
blocked_by: []
relates: [PW-1558, PW-1182, PW-1379]
refs: [tools/peoples_robust.py, "planet/lineages/samples/dnd.toml (saurian stem: tortle, lizardfolk, troglodyte)", planet/lineages/dens.py, planet/lineages/ladder.py, docs/review/peoples/origins-spread.md, "suite af2677 arm now, main 673436c0 (lane 269; scratch outputs deleted)", "world af2677"]
---
## In plain words
In the dnd tree on world af2677 the troglodytes are extinct by the present in all 17 dnd runs of the robustness suite, always
"no habitat left" (e.g. seed 7: died out 62 kyr ago). The drow hold 0.04-0.75 million km2 in every run. So a dnd world on af2677
never has troglodytes, and its drow sit far below the owner's 1 million km2 floor (D71). This is on main, not caused by lane 269.

## Description
Suite af2677, arm now, 22 runs, main 673436c0 (lane 269's branch leaves both unchanged): troglodyte area 0 in 17/17 dnd runs
(why_gone "dies out (no habitat left)"); drow min 0.04 (dnd-sites1-s7), median 0.75, 17/17 under 1 Mkm2. Founding is not the
cause for troglodytes: the probe of dnd-j4 shows them founded 1,488 kyr ago on a 3,760-cell habitat, the parent's patch 724 cells.
Find what removes their habitat (the den-ground layer, PW-1382, or a cave/karst habitat that shrinks with climate) and whether drow
are PW-1182's loser floor. D71 says no land people under 1 Mkm2 at the end of any run.
