---
id: PW-880
title: Weathering sink counts CO2 twice on planted ground (GEOCARB FERT law and the NPP it multiplies)
type: task
status: done
parent: null
milestone: v1
subsystem: climate
effort: s
impact: high
found_by: coupling-audit
blocked_by: []
relates: [PW-865, PW-830, PW-646]
refs: [planet/tectonics/earth.py, planet/vegetation.py, "world 6909cb", docs/review/coupling-audit/]
created: 2026-10-25
updated: 2026-10-29
---

## Description
Coupling audit finding C1 (severity high for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**Physics lane:** take first.

**One side:** planet/tectonics/earth.py (v1-finish-12) co2_law L121-125 and co2_stock L234-267: planted ground ~ (2X/(1+X))^WEATHER_FERT, GEOCARB's plant-mediated CO2 response (log-slope 0.2 at the balance).

**Other side:** planet/tectonics/earth.py (v1-finish-12) plant_factor L209-212 x weathering() L229, with sim.npp from update_vegetation L482-491, which grows the plants at pco2=climate.pco2(sim.co2); vegetation.co2_doublings L236 raises NPP with CO2. On main the same pair is WEATHER_CO2 X^0.4 (earth.py:28) and plants = 1 + 0.5 clip(npp/800) (earth.py:109).

**Why they disagree:** GEOCARB's FERT term IS the plants' CO2 fertilisation acting on weathering. The model now also feeds the sink an NPP that already responds to CO2, and plant_factor is linear in NPP below NPP_WEATHER = 500, which covers 84-93% of vegetated land in worlds 2a7385, e71172, 6909cb.

**Measured:** vegetation.model (branch code, the run's cheap variant, crown off) on world 6909cb's climate at 350 and 700 ppm: land NPP 379 -> 452 g/m2/yr (x1.19 per doubling); the sum of plant_factor rises 8.2% per doubling, an extra sink log-slope of ~0.11 on top of FERT's 0.2 (planted, at the balance). The planted sink's CO2 sensitivity is ~55% too strong, so CO2 moves ~1/3 less than intended for a given source/sink imbalance (the faint-star compensation, cold-era recoveries, the drift's CO2 swing).

**What to try:** Evaluate plant_factor on NPP at the balance pCO2 (the run already grows npp_pot at PCO2_BALANCE during the spin-up; keep a balance-CO2 NPP after REF_FREEZE too, or divide out the model's own CO2 response), so CO2 reaches the sink only through co2_law. Alternative: drop FERT on planted ground and let NPP carry the CO2 dependence (then NPP_WEATHER's saturation sets the slope, not the literature).

## Updates
- 2026-10-29: Status todo -> done. Closed 10-29: lane 24 measured the fix already on main working (see the ticket's previous update).
- 2026-10-29: Lane 24 checked main b711afe6: the fix (1b52cdf, the sink reads sim.npp_w, the plants grown at PCO2_BALANCE) is merged and works. In the paired L6 set (36 draws, 600-1000 Myr) the planted sink's CO2 log-slope is 0.176 (diag w_a), with a bare share of 0.083: FERT's 0.2 at the balance, a little saturated above it, and no extra ~0.11. The spin-up reference reads npp_pot, also at the balance's CO2. Nothing left to change; ready to close.
- 2026-10-25: v1-finish-13 (1b52cdf): the sink's plant factor reads sim.npp_w, the run's plants grown at PCO2_BALANCE (a second vegetation.model call per update), so CO2 reaches planted ground only through FERT. Cost follow-up: draft-weathering-plants-second-vegetation-call-cost.md. Pass rates re-measuring (cpl set). docs/review/base-climate/v1-finish-13/README.md
- 2026-10-25: Created from inbox draft draft-weathering-co2-counted-twice-on-planted-ground.md (found by coupling-audit).
