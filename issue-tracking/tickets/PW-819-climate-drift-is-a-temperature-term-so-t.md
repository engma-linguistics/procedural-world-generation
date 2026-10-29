---
id: PW-819
title: "Climate drift is a temperature term, so the CO2 thermostat answers it with low CO2: move the drift onto the carbon source (outgassing noise)"
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: climate
effort: s
impact: high
found_by: assumptions-audit
blocked_by: []
relates: []
refs: []
created: 2026-10-24
updated: 2026-10-25
---

## Description
From the pre-v1 assumptions audit (docs/review/assumptions-audit/README.md, findings.json): Climate drift is a temperature term, so the CO2 thermostat answers it with low CO2: move the drift onto the carbon source (outgassing noise).

## Updates
- 2026-10-29: Lane 24 checked main b711afe6: the drift is on the carbon source (earth.drift_source, climate_drift 0.8 C), with no temperature term left in global_temperature's target. In the paired L6 set (36 draws, >= 300 Myr), corr(dT, ln CO2) has a median of +0.68 (range -0.02..+0.91, 1 of 36 below 0), so warm eras carry high CO2. Nothing left to change; ready to close.
- 2026-10-25: v1-finish-11: drift_source re-derived on the planted law at the balance (3 C = +-0.36 e-folds of the source). docs/review/base-climate/v1-finish-11/README.md
- 2026-10-24: v1-finish-10: done in the branch. The drift is noise on the carbon source (earth.drift_source: 3 C is +-0.44 e-folds), not a temperature term; corr(dT, ln pCO2) after 300 Myr is now +0.3..+0.85 (was negative-leaning: warm eras CO2-starved). docs/review/base-climate/v1-finish-10/README.md
- 2026-10-24: Created.
