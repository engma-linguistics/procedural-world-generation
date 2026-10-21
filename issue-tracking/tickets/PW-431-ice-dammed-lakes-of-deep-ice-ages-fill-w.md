---
id: PW-431
title: Ice-dammed lakes of deep ice ages fill whole basins (seed 2 L6 7 Mkm2 behind an ice sheet); no flotation limit on an ice dam
type: task
status: todo
parent: null
milestone: null
subsystem: hydrology
effort: s
impact: low
found_by: pw300
blocked_by: []
relates: [PW-300]
refs: [planet/hydrology.py, docs/review/health-pw300-after/, docs/review/health-pw300-after/diag/hollow_origin.py]
created: 2026-10-16
updated: 2026-10-16
---

## Description
After PW-300's valley memory, some remaining giant-lake frames are proglacial lakes of deep ice ages. Seed 2
L6 (health --quick after PW-300) at 462 -> 464 Myr: the sea drops 257 m in one step, the ice sheet covers
47% of the basin's rim cells (8% the step before), and a 7.0 Mkm2 open lake (median 291 m deep) appears
behind it; it stays 2.6-3.2 Mkm2 through 488 Myr (sea -300 to -460 m) and is gone when the ice goes.
`rivers_and_lakes` routes water over the ice surface (bed + ice) with no lakes on the ice, so a lake
against an ice sheet can rise to the ice surface's lowest point: a dam of 1-3 km of ice.
Real ice dams hold much less: a lake floats its dam once its depth at the dam reaches ~0.9 of the ice
thickness (rho_ice / rho_water) and drains under it (jokulhlaups; Lake Agassiz ~0.44 Mkm2 at its largest,
Missoula's floods), and they drain along the ice margin. Worth trying: the ice's height as a barrier to
water = bed + 0.917 x ice (or less, for warm-based margins), in the lake fill only (rivers still cross the
ice surface). Check seed 2 @ 464-488 and seed 11 @ 184-192 with `docs/review/health-pw300-after/diag/probe.py`.
Low priority: the deep ice ages recover, and the health sweep counts these frames under giant lakes.

## Updates
- 2026-10-16: Created from inbox draft draft-ice-dammed-giant-lakes.md (found by pw300).
