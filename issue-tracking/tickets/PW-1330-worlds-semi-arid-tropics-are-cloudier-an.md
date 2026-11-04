---
id: PW-1330
title: Worlds' semi-arid tropics are cloudier and cooler-wintered than Earth's at the same rain, cutting grass growth ~30-45%
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: m
impact: med
found_by: lane123
blocked_by: []
relates: [PW-1261, PW-1321, PW-1279]
refs: ["planet/climate.py::shade_from_hours", "planet/climate.py::months", "planet/vegetation.py::_ft", docs/review/vegetation/npp-check/diagnosis.md, docs/review/vegetation/npp-check/world_check.py, docs/review/vegetation/npp-check/inputs_cmp.py, "world 067778", "world 6909cb", "world dba204", "world 506694 (Earth L6)", docs/review/base-climate/rain-inland/diagnosis.md]
created: 2026-11-02
updated: 2026-11-03
---

## Description
**In plain words.** At the same yearly rain (550-700 mm, mean temperature over 18 C), the worlds' grassland grows
392-538 g C/m2/yr against 748 on Earth's observed African climate, so their herds are 1.5-2.3 t/km2 against Earth's 4.1.
The plants respond the same way to the same climate; the worlds' climate differs: more cloud (shade 0.40-0.44 against
0.29; 15-20% less light), cooler coldest months (12.5-17 C against 20 C: C4 grass grows at full rate only from 25 C), and on
067778 a low CO2 of 221 ppm (water-limited growth x221/350, sourced). Whether the cloud and winter temperatures of the
worlds' semi-arid tropics are plausible is a climate question (compare the Earth model-climate run against CRU sunshine
in the Sahel/E Africa band, lanes 120/121's tools).
- [ ] cloud and coldest-month temperature of warm 400-900 mm land: Earth model climate vs observed, then the worlds

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: calibration or second-order physics refinement, not needed for the planet to be stable or for the culinary goal
- 2026-11-02: Correction to the update above: the cool coldest month is PW-1335 (not 1336).
- 2026-11-02: Status in-progress -> todo. 11-02 lane 125: worlds' tropics match the Earth model's own shade; the Earth model is ~0.13 too shady vs CRU, from the humidity-layer cloud (cloud_rh) in warm air (PW-1334) plus over-rain; cool coldest month is separate (PW-1336). docs/review/base-climate/tropical-cloud/diagnosis.md
- 2026-11-02: Status todo -> in-progress. 11-02: lane 125, diagnosis only (Earth model vs CRU cloud/sunshine and coldest month, then worlds).
- 2026-11-02: Created from inbox draft draft-semiarid-tropics-cloudy-cool.md (found by lane123).
