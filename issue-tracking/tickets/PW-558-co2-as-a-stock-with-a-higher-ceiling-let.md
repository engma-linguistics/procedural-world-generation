---
id: PW-558
title: "CO2 as a stock with a higher ceiling: let volcanic CO2 pile up under the ice (snowball exits need 40-400x, the clip is 20x)"
type: task
status: needs-decision
parent: PW-470
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: ice-v2-stage0
blocked_by: []
relates: [PW-555, PW-438]
refs: [planet/tectonics/earth.py, docs/review/ice-v2-criteria.md]
created: 2026-10-22
updated: 2026-10-23
---

## Description
Base assumptions A3/A4 in docs/review/ice-v2-criteria.md. `earth.global_temperature` sets ln pCO2 =
ln(source / sink) / WEATHER_CO2 each step (a steady state, not a stock), and the forcing is clipped at CO2_MAX = 3
e-folds (~20x). Checkpoint 0: the clip is never reached on main (index -3.6..+1.8 over 12 runs); the binding problem today is that the thermostat barely answers a cold era (A3b: weathering only stops on iced land, the sink stays at or above its 1000 Myr baseline, the CO2 term is <= +0.1 C in 5 of 7 deep eras). Real snowballs ended when outgassing piled CO2 up for Myr while ice held weathering near zero, to
~0.01-0.1+ bar (~40-400x, 3.6-6 e-folds: Caldeira & Kasting 1992, Pierrehumbert 2004, Abbot & Pierrehumbert 2010,
Hoffman et al. 2017). Checkpoint 0 (docs/review/ice-v2/checkpoint-0.md) reports how often deep eras sit at the clip.
Options:
- A: a carbon stock C (dC/dt = source - sink(C, climate)), whose steady state is today's rule; no hard clip,
  log forcing to ~6 e-folds. The proper physics; changes every run.
- B: keep the steady-state rule, raise CO2_MAX to 6 e-folds. Cheap; no Myr build-up.
- C: leave it; rely on the recovery lever (draft-ice-recovery-lever).
Lean: A, in the serial run lane after PW-555 stage 3 (it interacts with the ice model's deglaciation; judging it
before B2 is fixed repeats PW-438's lesson: the thermostat can't undo a rigid fixed point). Measure with
tools/ice_diag.py on the 10 seeds against tools/ice_criteria.py's new bars.

## Updates
- 2026-10-23: PW-576 merged (mature start + set-once CO2 stock); re-judge against docs/review/health/2026-10-23-pw576.
- 2026-10-22: Created from inbox draft draft-co2-carbon-stock.md (found by ice-v2-stage0).
