---
id: PW-323
title: "Coastal life: turbidity only from rivers; shallow tidal shelves (Wadden, Yellow Sea, Gulf of Thailand) should be turbid from resuspension"
type: task
status: todo
parent: PW-184
subsystem: coast
effort: s
impact: low
found_by: coastal-life
blocked_by: []
relates: [PW-188]
refs: [planet/coastal.py, tools/coastal_check.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`coastal.turbidity` (PW-188) is the rivers' BQART mud spread over the sea and settled, over a clear-water background of 0.5 mg/L. Real shallow seas with strong tides or waves are turbid without big rivers: waves and tidal currents stir the bed's fine sediment up wherever the floor lies within the wave base (Wadden Sea, southern North Sea, Yellow Sea, Gulf of Thailand, the Bay of Bengal's shelf: tens to hundreds of mg/L). On the Earth world (L6, `tools/coastal_check.py`) the Wadden Sea is at 0.6 mg/L, so its sea cells get ~45% seagrass (observed: a few % of Zostera beds; the flats are bare mud) and such shelves would grow reefs if they were warm.

Sound simplest fix: a resuspension term on coastal sea cells, rising as the floor shallows within the wave base (~20-30 m) and with tidal range and wave power (bed stress), times a mud supply (the shelf's own sediment cover or the river mud already there). Check the Earth numbers move the right way (seagrass and reef totals, Wadden / Yellow Sea), without tuning to them.
- [ ] resuspension term in `coastal.turbidity`
- [ ] Earth check: Wadden and Yellow Sea turbid (> 10 mg/L), open clear coasts unchanged

## Updates
- 2026-10-15: Created from inbox draft draft-coastal-turbidity-resuspension.md (found by coastal-life).
