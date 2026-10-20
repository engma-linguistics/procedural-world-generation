---
id: PW-439
title: Does a sheet's carried air over-protect big glacial sheets' summer margins? (suspected PW-030 stabiliser)
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: med
found_by: pw030
blocked_by: []
relates: [PW-030, PW-336]
refs: [planet/icemass.py, planet/climate.py, docs/review/audit/PW-030-handoff.md]
created: 2026-10-20
updated: 2026-10-20
---

## Description
PW-336 damps the summer warmth of the air over land ice by 0.6 x the iced share within ~1000 km
(`icemass.air_mass`, carried along the summer winds), calibrated on Antarctica's coasts. In the glacial time
zoom a big sheet's whole margin then sits in its own cold air, and the sheets "never go away"
(PW-030: interglacials of a cold run moment keep 17-25% of land iced; a cold branch never terminates).
Mid-latitude glacial margins (Laurentide's south: warm summers, proglacial outwash, summer westerlies
off bare land) likely felt much less of the sheet's air in summer than Antarctica's coast does.
Not tested in PW-030 (shared with the run, so it is the run lane's): measure how much of a big sheet's
margin summer the damping removes (L6 seed 11 @ 400 Myr in a 24%-of-land glacial state), and compare with
an Earth LGM margin estimate (southern Laurentide July ~10-15 C at the ice edge). If it over-protects, a
latitude or onshore-wind dependence of the carried air would be physics, not a fudge.
- [ ] numbers for the damping on glacial margins vs Antarctica's coast
- [ ] if changed: PW-030's metrics rerun (handoff's three L6 moments and Earth)

## Updates
- 2026-10-20: Created from inbox draft draft-sheet-air-protects-glacial-margins.md (found by pw030).
