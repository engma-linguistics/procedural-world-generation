---
id: PW-1353
title: High ground is ~1.5 C/km too cold on Earth (all latitudes); a mass elevation effect candidate fixes 20-40 deg winters but over-warms 40-60 deg
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: m
impact: med
found_by: lane131
blocked_by: []
relates: [PW-1335]
refs: ["planet/climate.py::temperature", "planet/climate.py::compute", "tools/earth_data.py::earth_on_grid", docs/review/base-climate/tropical-cloud/round2-diagnosis.md, docs/review/base-climate/tropical-cloud/winter2.py, docs/review/base-climate/tropical-cloud/round2.patch, "paper:He2016"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
In plain words: on Earth the model's highlands are colder than observed, more so the higher they are. That is about
-1.5 C per km of height in the coldest month and -1.4 C/km in the annual mean, at every latitude band. NCEP is already
brought to each cell's height with the model's own 6.5 C/km, so the data's terrain doesn't cause it. Real raised ground
heats the air over it: plateaus are warmer than the free air at the same height. He et al. 2016 puts it at ~5 K at
3700 m on the Altiplano.

Lane 131's candidate (round2.patch, `mee_k` 1.35 C per km of 300 km-smoothed ice-free height, capped at the cell's own
height) on Earth L7:
- 20-40 deg coldest month -1.6 -> -0.6 C; Köppen E 11.7 -> 10.4% (Kottek 7.3); S Africa savanna winter -2.6 -> -1.3.
- But 40-60 deg winters +1.0 -> +1.9 C; Köppen B 24.5 -> 23.6 (Kottek 30.1, wrong way); exact Köppen -0.9 point.
- The Congo's rain 1735 -> 2596 mm (GPCC 1653).

Not checked: glaciers, ice caps and the runs' ice ages (Tibet, Andes, Rockies warm 1-3 C through temp0); L6 judge.
Open: whether the effect should fade poleward or in winter (He 2016: the winter difference "increased from high
latitudes to low latitudes"). Why 35-50 deg lowlands are already +3.4 C in winter is a separate question.
- [ ] decide whether to take the effect; if so, Earth highland miss within ~0.5 C/km without 40-60 deg winters past +1 C

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: calibration or second-order physics refinement, not needed for the planet to be stable or for the culinary goal
- 2026-11-02: Created from inbox draft draft-mass-elevation-effect-highland-temperature.md (found by lane131).
