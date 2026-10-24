---
id: PW-770
title: "PW-729 marine habitat not started: where it would go and what the cost is"
type: task
status: wontdo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: l
impact: med
found_by: fun14
blocked_by: []
relates: [PW-729, PW-692]
refs: [planet/lineages/history.py, planet/lineages/spec.py, planet/lineages/spread.py, planet/lineages/crossing.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
Fun lane 14 spent its budget on PW-756 (derived incursions, herder press) and did not start PW-729. What a start needs, from reading the code:
- `History.capacity` / `_K` give habitat on land cells only (`land_any = env["land"]` in the spread, `is_land` in every tag); a sea line needs its own K on sea cells (depth band, SST, light,
  reef and kelp from the coast pass, vents from the tectonics' ridge/arc volcanism) and a spread over the sea graph (grid.nbr_* is shared; `spread.spread(..., land_any ...)` would take a `sea_any`).
- Every consumer assumes land presence: `Contacts.update` masks `& land`, `_frame` computes `whole` on land, `landuse`/`fuels`/`brief` read land goods, the viewer paints the peoples layer on land.
  The merfolk "coast" realm (tidal interface = sea cells next to land plus land coast cells) is the smaller step: K from `tags["coast"]` and the shelf, no new layers beyond a `sea` mask on the frame.
- Owner (2026-10-24, relayed): merfolk and storm giants are to be simulated at sea; deep folk stay written/authored. So option A for both, not the coast-only fallback.
- Lean unchanged from the intake: coast realm for merfolk and offshore for storm giants first (A), deep folk authored. Measure the cost at L7 and that land peoples' numbers do not move.

## Updates
- 2026-10-24: Status todo -> wontdo. Duplicate of PW-729; pointers folded there.
- 2026-10-24: Created from inbox draft draft-marine-habitat-not-started.md (found by fun14).
