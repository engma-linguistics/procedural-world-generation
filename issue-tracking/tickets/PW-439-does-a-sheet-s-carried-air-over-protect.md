---
id: PW-439
title: Does a sheet's carried air over-protect big glacial sheets' summer margins? (suspected PW-030 stabiliser)
type: task
status: todo
parent: PW-470
milestone: later
subsystem: climate
effort: m
impact: med
found_by: pw030
blocked_by: []
relates: [PW-030, PW-336]
refs: [planet/icemass.py, planet/climate.py, docs/review/audit/PW-030-handoff.md]
created: 2026-10-20
updated: 2026-11-03
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
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Ice-age epic PW-470 is parked post-v1 (owner 10-28 timebox); PW-467 is the one kept as the timeboxed item.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-20: Created from inbox draft draft-sheet-air-protects-glacial-margins.md (found by pw030).
