---
id: PW-894
title: "2 Gyr runs stay icebox after PW-859: the bare-ground weathering thermostat returns only ~40% of the faint star's forcing"
type: task
status: needs-decision
parent: null
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: v1-finish-14
blocked_by: []
relates: [PW-859, PW-865]
refs: [planet/tectonics/earth.py, docs/review/base-climate/v1-finish-14/README.md]
created: 2026-10-26
updated: 2026-10-26
---

## Description
A 2 Gyr run starts at -29 C of star forcing, which is still -15 C at 1000 Myr. Before plants arrive (~470 Ma, run time
1530), the sink sits at x0.1-0.3 of its reference: bare ground weathers 1/PLANT_WEATHER, and the reference is
planted at the balance. The steady state is w X^0.5 = s, so ln X = 2 ln(s/w) - 2c dT. With c ~0.07/C (local
kinetics at 0.5-0.6 of dT, plus runoff) and G = 4.33 C per e-fold, the return is Gc/beta / (1 + Gc/beta) ~0.38. A
-25 C forcing leaves dT ~-10 C, and that is what the cpl runs show (957317: CO2 index ~3.5, dT -10 over 300-1000 Myr).

PW-859's deep-time methane (~4 W/m2) and the CO2 log-to-0.1-bar fix (v1-finish-14) raise the median dT by 1-3 C.
The runs stay icebox (icehouse 81-97% of the time).

Options, all literature-sized; the owner picks:
- (a) WHK 1981's beta of 0.3 on bare ground in place of GEOCARB's 0.5. Smaller beta gives a stronger return: ~0.5.
- (b) The weathering kinetics on global dT (GEOCARB's ACT 0.09 per C of the global dT) in place of the local land
  response of ~0.5-0.6: c ~0.115, return ~0.5.
- (c) Mantle heat dated by planet age (see draft-mantle-heat-by-age).
- (d) Accept that 2 Gyr Earth-likes are cold early and judge the bar on 1000-end. That is a threshold, so it is the
  owner's call.

## Updates
- 2026-10-26: Created from inbox draft draft-faint-sun-thermostat-return-bare-ground.md (found by v1-finish-14).
