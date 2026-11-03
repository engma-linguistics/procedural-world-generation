---
id: PW-561
title: "Optional generation-time ice-age recovery lever: a push on real mechanisms that grows with a cold era's depth and length and eases as the planet recovers"
type: task
status: todo
parent: PW-470
milestone: later
subsystem: climate
effort: m
impact: med
found_by: ice-v2-stage0
blocked_by: []
relates: [PW-555]
refs: [docs/review/ice-v2-criteria.md, planet/tectonics/earth.py, planet/tectonics/diag.py]
created: 2026-10-22
updated: 2026-11-03
---

## Description
Owner, 2026-10-21: "the longer a deep ice age goes, the more the subsystems nudge real sim behavior until it's
guaranteed to spring out of it with the nudges eased off as it recovers". Design in docs/review/ice-v2-criteria.md
section 4:
- State: a cold-era debt D, dD/dt = depth - D / 20 Myr (depth = max(0, -sea_ice - 150) / 300 + max(0, iced land -
  0.25)); strength s = recovery x (1 - exp(-D / D0)).
- Pushes, most honest first: (1) CO2 piling up under the ice (the ceiling rises from 3 toward 6 e-folds, the stock
  grows at source - sink); (2) dusty ice (smaller ice-albedo term, more melt on the sheets); (3) basal heat (weak);
  (4) a volcanic pulse (world-builder); (5) a brighter star (world-builder unless the star is variable).
- `recovery` param: 0 off / 0.3 natural / 1 assisted / >1 guaranteed (scaled so s = 1 reaches the planet's exit dT
  from tools/ice_probe.py --stair). A mirror onset lever is optional.
- Display: a New-planet option with a one-line note on which parts are physics; a band under the viewer's
  temperature curve showing the push; run meta records it.
- Default off until the carbon stock (draft-co2-carbon-stock) and stages 1-3 of PW-555 land; then natural (0.3).
- [ ] lever built behind `recovery` (0 = bit-identical)
- [ ] 10-seed L6 check at 0.3 and 1: N1 passes on >= 9/10 at 1 without hothouse overshoot (N4)
- [ ] viewer band and New-planet option

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Ice-age epic PW-470 is parked post-v1 (owner 10-28 timebox); PW-467 is the one kept as the timeboxed item.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: Created from inbox draft draft-ice-recovery-lever.md (found by ice-v2-stage0).
