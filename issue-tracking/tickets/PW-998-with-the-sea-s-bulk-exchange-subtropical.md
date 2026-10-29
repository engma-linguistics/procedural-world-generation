---
id: PW-998
title: "With the sea's bulk exchange, subtropical east coasts and winter-rain coasts dry out (SE USA 482 vs 1328 mm, Pampas 294 vs 943, Japan 524 vs 1672, E Australia 488 vs 743): the instant refill had masked their winds"
type: task
status: todo
parent: PW-013
milestone: v1
subsystem: climate
effort: l
impact: med
found_by: lane25
blocked_by: []
relates: [PW-015, PW-026, PW-352]
refs: [planet/climate.py, tools/earth_check.py, tools/moisture_budget.py, docs/review/base-climate/deserts/README.md]
created: 2026-10-29
updated: 2026-10-29
---

## Description
Lane 25 (PW-015) replaced the rain kernel's instant refill of the sea's air with a bulk exchange
(`climate.sea_uptake`, commit 5840dcc6). Earth improved overall (Koppen B 20 -> 27%, log-rain corr 0.648 -> 0.691,
exact 34 -> 36%), but coasts whose rain came from air that had crossed only a little sea lost a lot (Earth L6 earth_check,
main -> branch, GPCC):

| region | main | branch | GPCC |
|---|---|---|---|
| SE USA | 1109 | 482 | 1328 |
| Pampas | 548 | 294 | 943 |
| Japan | 1153 | 524 | 1672 |
| E Australia | 1055 | 488 | 743 |
| Mediterranean | 607 | 383 | 551 |
| Mexico N | 237 | 114 | 482 |
| India | 696 | 588 | 1109 |

Before, any strip of sea refilled the air at once, so these coasts were wet for the wrong reason. Their real moisture
comes with winds the model lacks: the winter subtropical highs' return flow and the cyclones that bring Gulf, South
Atlantic and Kuroshio air onshore (PW-026, the 2026-10-16 handoff's root cause 2: SE USA Oct-Mar PW 4.6 vs NCEP 17.4 mm).
Japan's winter (the NW monsoon over the Sea of Japan) should be wet under a bulk exchange; check whether its summer
southerlies or its winter fetch is what dried.

What to try: per region and half-year with `tools/moisture_budget.py` (kernel terms, wind), find which half lost the rain
and from where the vapour comes; then fix the winds (PW-026), not the sea's exchange.
- [ ] SE USA and Pampas each at least 60% of GPCC's annual rain without undoing the bulk exchange

## Updates
- 2026-10-29: Created from inbox draft draft-subtropical-coasts-dry-after-bulk-evap.md (found by lane25).
