---
id: PW-383
title: Forearc islands still stand as ~600-900 m plateaus with steep edges after the sea share (PW-362 B)
type: task
status: todo
parent: null
milestone: later
subsystem: zoom
effort: s
impact: low
found_by: small-fixes-batch
blocked_by: []
relates: [PW-362, PW-649]
refs: [planet/zoom.py, docs/review/zoom-polish/batch6.md, docs/review/zoom-polish/pw362_sea_share.png, "world fac2af"]
created: 2026-10-16
updated: 2026-10-26
---

## Description
PW-362 B (zoom.SEA_SHARE_PASSES) took fac2af's forearc mesa (cell 52473, +194 m, zoom -1.467,36.085 500 km @
1 km seed 1) from land p50/p90 1,334/1,631 m to 607/902 m, its sea from -1,604 to -628 m. The island still
rises fairly evenly with steep sides, because the rest of the mean (the sea part can only rise to the
shore, and the fine coast keeps 62% of the cell land) is still put on the land evenly by the mean
correction. Also the cell's final mean is 124 m, not 194 (unchanged by B: the later passes). If it still
reads as a block, the coordinator's fallback A applies: put a mixed cell's remaining correction on its land
by distance from its coast (a dome rather than a lift), which moves every coast's mean keeping.
- [ ] look at the island in the 3D view; decide whether A is wanted

## Updates
- 2026-10-26: Parent PW-001 (done) -> none. (PW-900 backlog reorg).
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-16: Created from inbox draft draft-forearc-island-plateau-after-sea-share.md (found by small-fixes-batch).
