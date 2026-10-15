---
id: PW-285
title: Sediment on hotspot rock still floats at the volcano-pile rate (x1.75) beyond the PW-172 pile cap
type: task
status: in-progress
parent: PW-245
subsystem: tectonics
effort: xs
impact: low
found_by: audit-tectonics
blocked_by: []
relates: [PW-172]
refs: [planet/tectonics/isostasy.py, docs/review/audit/tectonics.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
PW-172 capped the flexural support of a hotspot pile at VOLCANO_PILE_KM
(20 km beyond ocean crust) in `isostasy.elevation`. Two places still use
the volcano rate for the whole column:
- `isostasy._k` scales K_SEA by ISO_VOLCANO / ISO_SEA = 1.75 for every
  HOTSPOT cell, so `sediment_lift` (the light-sediment uplift) and
  `sediment_iso` are 1.75x on hotspot cells, however thick the pile.
  These were the "4.2 km sediment lift" of PW-172's 11.5 km spike.
  Measured (audit probes): the extra lift on hotspot cells reaches 1.07
  km at L6 seed 21 over 1 Gyr (mean of the per-frame maximum 620 m), and
  410 m at L5.
- `iso_rate` returns ISO_VOLCANO for HOTSPOT basement even beyond the pile
  cap, where `elevation` changes at ISO_SEA. So erosion and deposition
  there are computed at the wrong m-per-km.

Fix: give sediment on hotspot cells the plain K_SEA (the flexural support
belongs to the volcanic pile, not to the mud on it). Make `iso_rate` return
ISO_SEA for hotspot cells whose pile is past VOLCANO_PILE_KM. Golden update
expected; no envelope change expected.

## Updates
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Created from inbox draft draft-audit-tectonics-hotspot-sediment-iso.md (found by audit-tectonics).
