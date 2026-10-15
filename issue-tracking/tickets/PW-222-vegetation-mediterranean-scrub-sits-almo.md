---
id: PW-222
title: "Vegetation: Mediterranean scrub sits almost entirely outside Koppen Cs (34 of 2163 cells on world 351f32)"
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: low
found_by: smalls
blocked_by: []
relates: [PW-187, PW-208]
refs: [planet/vegetation.py, "world 351f32"]
created: 2026-10-15
updated: 2026-10-15
---

## Description
While adding vegetation highlights (PW-208) on the L7 vegetation demo world 351f32:
of 2163 land cells whose named type is 19-21 (Mediterranean scrub / evergreen
woodland / pine forest), only 34 are Koppen Cs (Csa 4, Csb 28, Csc 2); 750 are BSh, 749 BSk, 187 Cwb, 122 Cfb,
102 Cfa, 97 BWk, 67 Cwa. The Koppen Cs
regions themselves carry temperate woodland and parkland / mixed forest (the
"Wine country" highlight at 38.8, -130.1: woodland 45%, Mediterranean pine 25%,
mixed forest 22%; at 32.7, -179.7: woodland 96%). On Earth maquis, chaparral and
fynbos are mostly Cs, with some spill into BSk.
Check the classifier rule for types 19-21 (vegetation.classify): it probably keys on
sclerophyll-shrub dominance and dryness without asking for a summer-dry,
winter-wet regime, so semi-arid steppe climates get it and Cs gets parkland.
- [ ] most Mediterranean-type cells in Cs (or a documented reason they aren't)

## Updates
- 2026-10-15: Created from inbox draft draft-maquis-outside-cs.md (found by smalls).
