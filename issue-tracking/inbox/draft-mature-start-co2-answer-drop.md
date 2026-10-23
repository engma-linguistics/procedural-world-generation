---
title: "On the mature start the CO2 stock's answer falls (+0.34 -> +0.21 C/C for the reference set once): find out why before tuning anything"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: base-climate-laneB3
blocked_by: []
relates: [PW-576, PW-559]
refs: [tools/ice_diag.py, docs/review/base-climate/thermostat.md]
---

## Description
10 L6 seeds, 1 Gyr, main 5c4c0fd. With the reference set once (co2_relief_myr 0), the trends-out CO2 answer is a
median +0.34 C/C on the old start and +0.21 on the mature start, 3/10 in 0.35-0.9 on both. With the relief term:
+0.40 against +0.13. N1-N4 and the icehouse share improve on the mature start, so the brake on long eras works.
The weaker answer is on the drift's ~40 Myr time scale.
- One seed's answer is good to about ±0.1 (17 independent drift samples), so part of this may be noise.
- A possible cause: the mature start's erosion comes more from the high old belts, where the supply hardly answers
  rain, and less from the runoff over lowlands. Compare the sink's parts per seed (supply /C and temperature factor
  /C from `ice_diag --summary`) between laneB3/cmp_old_a1 and laneB3/cmp_mat_a1 in the session scratch.
- [ ] per-seed split of the answer into supply and temperature factor on both starts
- [ ] if it's real and mechanistic, a ticket on the cause; no gain tuning
