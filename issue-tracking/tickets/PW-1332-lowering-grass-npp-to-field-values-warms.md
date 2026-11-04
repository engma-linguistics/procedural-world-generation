---
id: PW-1332
title: Lowering grass NPP to field values warms L6 runs by 3-5 C through the weathering's NPP factor
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: tectonics
effort: m
impact: high
found_by: lane123
blocked_by: []
relates: [PW-1261, PW-646]
refs: ["planet/tectonics/earth.py::NPP_WEATHER", "planet/tectonics/earth.py::START_PLANTED", "planet/tectonics/earth.py::update_vegetation", "planet/vegetation.py::_year", docs/review/vegetation/npp-check/screens.md, docs/review/vegetation/npp-check/candidate1-herb-root-resp.patch, docs/review/vegetation/npp-check/diagnosis.md, "tools/health.py::measure_run"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
**In plain words.** Lane 123's plant fix (grass roots pay upkeep, so grassland grows what field plots measure) makes the
runs' planets warmer: L6 seeds 1 and 2 over 1 Gyr end 3.4 and 4.8 C warmer (late dT -2.2 -> +2.6, +1.8 -> +5.2), CO2
stock up 0.5-0.7 e-folds. In a run, land NPP sets how fast rock weathers (`earth.py`: fully planted at NPP_WEATHER =
500 g C/m2/yr, in proportion below), and weathering draws CO2 down; less grass growth reads as less weathering. The
weathering's plant factor was set while grass was ~1.4x too productive, so the climate's balance sits on that error.

Options:
- **A.** Re-anchor NPP_WEATHER (and START_PLANTED) so Earth-like runs keep their weathering after the plant fix (a
  calibration shift that follows the plants, not a new knob).
- **B.** Tie the weathering's plant factor to cover or root activity rather than NPP (grass roots weather rock whatever
  their carbon budget).
- **C.** Keep the warmer runs (the star brightening and thermostat already set the climate; would need the judge).
Lean: A, then two L6 seeds and the judge, as one change with PW-1261's plant patch and the fire fuel floor.

## Updates
- 2026-11-03: Owner 11-03: 'your call', with a north star: 'reasonably stable and not prone to exploding when nudged', here and elsewhere. Folded into the climate-stability diagnosis lane.
- 2026-11-02: Created from inbox draft draft-weathering-npp-reference-after-grass-cue.md (found by lane123).
