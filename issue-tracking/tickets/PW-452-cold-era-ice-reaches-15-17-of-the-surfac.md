---
id: PW-452
title: Cold-era ice reaches 15-17% of the surface at only dT -4, so the sea falls ~500 m
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: pw438b
blocked_by: []
relates: [PW-438, PW-439]
refs: [planet/icemass.py, tools/ice_diag.py, issue-tracking/tickets/PW-438-cold-eras-depth-is-not-set-by-the-climat.md]
created: 2026-10-20
updated: 2026-10-29
---

## Description
After PW-438's base-level, weathering-mask and CO2 changes, the deep eras on seeds 2 and 21 show land ice at 15-17% of the surface (Earth's LGM: ~7-8%) at a global dT of only about -4 C, with sea level from ice near -500 m. The climate side is no longer the main lever (CO2 now has room to rise); the ice side is: how much ice a given cooling builds, i.e. the local mass balance and sheet extent (`icemass.LOCAL`, PW-439). Check the ice area against dT in the deepest eras of seeds 2, 21, 11 (`tools/sealevel.py` diagnostics), compare to the LGM (dT about -5..-6, ice ~7-8%, sea -120 m), then pick between `icemass.LOCAL` and the sheets' thickness/extent rules.\n- [ ] ice % at dT -4 within ~2x of the LGM's\n- [ ] re-run the 4-seed L6 table of PW-438

## Updates
- 2026-10-29: Removed tools/sealevel.py in cleanup; last present at aae96637. Folded into tools/ice_diag.py: --tect records its per-step channels and --summary prints its sea-level line; --run <id> reads a stored run.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-20: Created from inbox draft draft-ice-extent-at-dt-4.md (found by pw438b).
