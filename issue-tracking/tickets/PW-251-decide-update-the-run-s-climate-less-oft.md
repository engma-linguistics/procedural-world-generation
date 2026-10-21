---
id: PW-251
title: "Decide: update the run's climate less often (climate_every 4 -> 8 Myr) or cheaper (fewer orbit states in the ice balance)?"
type: task
status: wontdo
parent: PW-247
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: gpu-explore (PW-249)
blocked_by: []
relates: [PW-249]
refs: [planet/tectonics/earth.py, planet/icemass.py, planet/tectonics/params.py, docs/review/gpu/profile.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
The climate update (`earth.update_climate`: climate.compute + ice sheets + vegetation) runs every
`climate_every` = 4 Myr, i.e. every other 2 Myr step, and is ~60% of a run (L6: 0.87 s per update,
21.9 s per 100 Myr of ~36 s of steps; L7: ~4 s per update, 107 s of 176 s). Within it,
`ice_sheets` calls `icemass.balance` twice, each running `climate_step` for the mean orbit plus
8 orbit-cycle states (18 calls per update). Both are "work repeated more often than needed"
candidates, but both change outputs:
- A. Keep as is (reference behaviour).
- B. climate_every = 8 Myr: ~30% faster runs; keyframes every 4 Myr would show the climate of up
  to 4 Myr earlier between updates; erosion uses a climate up to 8 Myr old. Check scorecard/KPIs.
- C. Fewer orbit states in the ice balance (e.g. 4 instead of 8), or one balance call instead of
  two: after `climate_step` is made parallel (separate draft) this is worth only ~1-2%, so not worth it.
- D. Adaptive: update when the inputs moved (sea level, land mask, global temperature) by more than a threshold.

Lean: A until the parallel/fusion work (PW-247 drafts) is done; then measure B against the
scorecard. It's the only single knob with a >1.3x effect on CPU.

## Updates
- 2026-10-15: Status needs-decision -> wontdo. Owner (2026-10-15): pass, option A: keep climate_every = 4 Myr. A ~30 min L7 run is fine, and multi-seed checks get their speed by running seeds a few at a time (planet/parallel.py).
- 2026-10-15: Created from inbox draft draft-climate-cadence-decision.md (found by gpu-explore (PW-249)).
