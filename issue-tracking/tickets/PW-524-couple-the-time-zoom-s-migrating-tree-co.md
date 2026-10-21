---
id: PW-524
title: Couple the time zoom's migrating tree cover to the climate (albedo, Budyko w) once ice ages are unparked
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: timezoom
effort: m
impact: low
found_by: pw213
blocked_by: []
relates: [PW-213, PW-450, PW-471]
refs: [planet/timezoom/plants.py, planet/vegetation.py]
created: 2026-10-21
updated: 2026-10-21
---

## Description
PW-213 added a migrating tree cover to the time zoom (plants.py `migrate`, `veg_speed` 250 m/yr), but the
climate and the global albedo term still use the first, in-balance cover (PW-450), because ice ages are parked
and the feedback would change the ice. The real forest lags the climate by up to ~5 kyr at a deglaciation
(Earth 300 kyr: ~2 Mkm2 of 8-17 Mkm2 regrowth), so its albedo and rain recycling lag too. When PW-470 is
unparked: feed `feedback(mig cover)` into `Plants.raw` (the local correction and `measure`), re-check the
Kohler LGM albedo number and the ice volume, and decide whether the balance cover can go.
- [ ] ice volume and sea level of Earth 600 kyr compared before and after

## Updates
- 2026-10-21: Created from inbox draft draft-veg-migration-feedback.md (found by pw213).
