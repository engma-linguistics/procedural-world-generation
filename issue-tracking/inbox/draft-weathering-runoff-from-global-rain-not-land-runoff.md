---
title: "Weathering's runoff factor scales with the global-mean rain law, not the land runoff the climate computes"
type: task
status: todo
parent: null
milestone: v1
subsystem: climate
effort: s
impact: med
found_by: coupling-audit
blocked_by: []
relates: [PW-865]
refs: [planet/tectonics/earth.py, planet/climate.py, "runs 0ceebf 172922 343058 2b0b65", docs/review/coupling-audit/]
---

## Description
Coupling audit finding C3 (severity medium for the Earth-like v1 finish; docs/review/coupling-audit/README.md).

**Physics lane:** take third.

**One side:** planet/tectonics/earth.py (v1-finish-12) weathering() L227 warm *= exp(WEATHER_RUNOFF x climate.RAIN_PER_C x dT); climate_coef() L108-111, used by drift_source and balance_co2.

**Other side:** planet/climate.py compute L2278-2298: RAIN_PER_C renormalises the GLOBAL mean rain (sea included); the per-cell land runoff is computed (water_balance) and kept as sim.runoff (earth.py update_climate L414).

**Why they disagree:** The stand-in assumes weathering-land runoff grows like the global mean rain, 3%/C. The model's own land rain grows much less, and runoff = rain - AET grows differently again, while the real quantity sits in sim.runoff.

**Measured:** Across keyframes 50-1000 Myr of L6 runs 0ceebf, 172922, 343058, 2b0b65: global rain d ln P/dT = 0.030 (by construction); ice-free land rain 0.005, 0.019, 0.012, 0.023 per C. So the runoff term (0.0195/C in climate_coef) is 1.3-6x too strong on these planets, and climate_coef (0.0735) ~5-17% too strong.

**What to try:** Use the weathering land's own runoff against the reference, (runoff/runoff_ref)^WEATHER_RUNOFF per cell (GEOCARB's f_R on the model's water balance), learnt with the rest of the reference; size climate_coef from a measured land runoff slope.
