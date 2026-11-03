---
id: PW-899
title: PW-880's balance-CO2 plants for the weathering sink run vegetation.model twice per climate update; measure the cost and find a cheaper exact form
type: task
status: todo
parent: PW-470
milestone: later
subsystem: climate
effort: s
impact: low
found_by: v1-finish-13
blocked_by: []
relates: [PW-880]
refs: [planet/tectonics/earth.py]
created: 2026-10-26
updated: 2026-11-03
---

## Description
PW-880 (v1-finish-13, 1b52cdf): `earth.update_vegetation` grows the run's plants a second time at PCO2_BALANCE
(`sim.npp_w`, warm-started from its own last update). The weathering sink's plant factor then carries no CO2, and
GEOCARB's FERT carries all of it. This is a second `vegetation.model` call per climate update, on top of the
spin-up's potential-vegetation call before REF_FREEZE.

Seen on a loaded machine and not separated from the load: a 400 Myr L6 smoke run took 8.6 min, and pytest took 17:45
against 8:13 on the previous commit.
- [ ] Time one L6 1 Gyr run before and after 1b52cdf on a quiet machine.
- [ ] If it costs more than ~15%, look for a form that gives the same answer: the plants' CO2 response only enters
  through vegetation.potential's quantum yield and respiration (co2_doublings), so the balance-CO2 NPP could come
  from the same call's potential at a second CO2, without a second equilibrium pass.

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Ice-age epic PW-470 is parked post-v1 (owner 10-28 timebox); PW-467 is the one kept as the timeboxed item.
- 2026-10-26: Created from inbox draft draft-weathering-plants-second-vegetation-call-cost.md (found by v1-finish-13).
