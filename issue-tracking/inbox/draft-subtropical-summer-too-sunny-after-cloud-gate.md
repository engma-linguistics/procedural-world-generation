---
title: "Summer subtropical land too sunny after the stratus gate (20-40 deg 0.76 vs CRU 0.67), worst where the rain is too low"
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: low
found_by: lane126
blocked_by: []
relates: [PW-1334, PW-1326, PW-015, PW-228]
refs: ["planet/climate.py::_layer_gate", "planet/climate.py::clouds", "planet/climate.py::_summer_split", docs/review/base-climate/tropical-cloud/round1.md, docs/review/base-climate/tropical-cloud/screen.py, docs/review/base-climate/summer-heat/diagnosis.md, data/earth/clouds_L7.npz, "Eastman & Warren 2014 (J. Climate 27:2386)"]
---

## Description
In plain words: on Earth, summer land at 20-40 deg now gets more sunshine than CRU measures: 0.76 against 0.67 (main
0.67). The new stability gate removes the humidity layer cloud wherever summer land is warmer than the air aloft, and
at 20-40 deg in summer that is nearly everywhere.

Regions (summer sunshine, model / CRU, lane 126 vs main):
- India 0.71 / 0.49 (main 0.61); N Mexico 0.94 / 0.61 (main 0.87). Both were already too sunny on main, where the
  model's rain is too low (India 627 mm vs GPCC 1126, N Mexico 199 vs 482; summer-heat diagnosis).
- W Europe 0.56 / 0.45 (main 0.45, which matched).
- SE USA 0.66 / 0.64 is fine.

The 40-60 deg band is fine (0.52 vs 0.55). A 30% floor on the gate gives 0.73 at 20-40, but it leaves the tropical
bands 0.05-0.06 too shady. Eastman & Warren 2014 has summer land low cloud as cumulus-dominated, so most of the gap
should come back as cumulus (`cloud_cu`) and monsoon deep cloud, from the right rain, not as stratus.

Try: once PW-015 / PW-228's rain lands, re-measure. If W Europe's summer is still 0.1 too sunny, look at `cloud_cu`'s
instability threshold over midlatitude summer land.
- [ ] 20-40 deg summer sunshine within ~0.05 of CRU without losing the tropical shade bands
