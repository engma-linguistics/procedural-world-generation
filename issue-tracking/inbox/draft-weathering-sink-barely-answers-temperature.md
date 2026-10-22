---
title: "The weathering sink barely answers temperature (0.02 per C against 0.09): the CO2 feedback is ~0.14 C per C of cooling, ~5x weaker than written"
type: task
status: needs-decision
parent: PW-470
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: base-climate-review
blocked_by: []
relates: [PW-558, PW-559, PW-438, PW-564, PW-368, PW-561]
refs: [planet/tectonics/earth.py, tools/ice_diag.py, docs/review/base-climate-review.md]
---

## Description
**Measured** on the 15 existing L6 1 Gyr `ice_diag` runs (checkpoint 0 and the new main; after the 300 Myr spin-up):

| measure | as the rule is written | measured, median (range) |
|---|---|---|
| d ln(sink)/dT | ~0.09 per C | 0.020 per C (−0.002..0.045) |
| CO2 warming per 1 C of cooling | ~0.7 C (3 C per e-fold × 0.09 / 0.4) | 0.14 C (−0.12..0.38) |
| dT per C of drift | | 0.82 (0.53–1.05) |

The CO2 term rises *with* dT on 12 of 15 runs. It follows the volcanic source (×0.6–1.5 against its baseline),
amplified 2.5× by 1/WEATHER_CO2, so it acts as a forcing, not a brake.

**Likely cause, not yet separated.** `sim.weathered` is physical erosion. Mountains, rain and a cold era's base-level
drop (`base_rise`) all raise it, and that swamps the exp(0.09 dT) factor.

PW-558's stock alone doesn't change the steady-state gain: the ratio rule is the stock's equilibrium.

**Options.**
- A: a weathering law with a kinetic ceiling (regolith residence, or weathering intensity: West et al. 2005; Maher &
  Chamberlain 2014). Extra erosion saturates, and temperature and runoff steer.
- B: keep supply-limited weathering, but don't count a cold era's extra incision and rock flour at full weight.
- C: leave it, and rely on the set point (PW-559) and the recovery lever (PW-561).

**Lean: A.** First split the sink in `ice_diag` into its area, erosion supply, temperature factor and plant factor.

**Done when** the feedback is 0.4–0.9 C per C and the CO2 term runs against dT on ≥ 7 of 10 seeds. Then PW-558,
PW-559 and PW-564, in that order.
