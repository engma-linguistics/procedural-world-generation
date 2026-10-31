---
id: PW-1211
title: "Measured L8 costs (100 Myr world): the make estimates for L8 are far too low"
type: task
status: todo
parent: null
milestone: null
subsystem: infra
effort: s
impact: med
found_by: lane-86b
blocked_by: []
relates: [PW-535, PW-1143]
refs: [planet/make.py, docs/coordination.md, docs/review/l8-world/notes.md]
created: 2026-10-31
updated: 2026-10-31
---

## Description
Lane 86/86b built one L8 world (seed 11, 100 Myr, run 2c0c5d, world a16f5a, time zoom 37f146) on the Threadripper at load 20-55.
Measured: `simulate` 132 min for 100 Myr (9-25 s/Myr, then ~8 min/Myr over the last 10 Myr, where the finish window runs a
full L8 climate every 0.5 Myr: 88 -> 100 Myr took ~90 min); peak RSS 10.7-15 GB (the run-cost table said 3.5 GB). `slice` of the world: 13.8 min,
17.7 GB RSS, world file 440 MB. A 60 kyr time zoom: 39 min, 10.4 GB (10-20 s/kyr, `TZ_S_PER_KYR[8]` is 2.6). Highlights 86 s; four regional zooms 439 s.
`make`'s estimates (RUN_S_PER_GYR[8]=12000, FINISH_S[8]=155, TZ_S_PER_KYR[8]=2.6) are off by roughly x5 for the time zoom
and x5 for the finish. A 300 kyr time zoom at L8 would take ~4 h, not 13 min.
For PW-535: this is the L8 timing it asked for (use under-load figures with a note). For PW-1143: peoples at L8 will cost about 4x an L7 try (L7 try ~66 min wall, 11 GB), so 4-5 h per try; result in the notes when it lands.
- [ ] refit RUN_S_PER_GYR / FINISH_S / TZ_S_PER_KYR for L8 (and the finish window's share of short runs)
- [ ] the run-cost table's L8 memory (done in coordination.md for this world)

## Updates
- 2026-10-31: Created from inbox draft draft-l8-measured-costs.md (found by lane-86b).
