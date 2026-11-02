---
id: PW-1335
title: Coldest month of warm semi-arid land is 1.6-2.7 C below NCEP on Earth itself (not a cloud effect)
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: lane125
blocked_by: []
relates: [PW-1330, PW-1261, PW-1279]
refs: [docs/review/base-climate/tropical-cloud/diagnosis.md, docs/review/base-climate/tropical-cloud/bands.py, "planet/climate.py::_summer_split", "planet/climate.py::compute", tools/earth_check.py, docs/review/base-climate/rain-inland/diagnosis.md, "world dba204", "world 899985", "world 1df1c3", "world 6909cb", "world 3e9e7d", docs/review/base-climate/tropical-cloud/round2-diagnosis.md, docs/review/base-climate/tropical-cloud/winter2.py, docs/review/base-climate/tropical-cloud/round2.patch, paper:He2016]
created: 2026-11-02
updated: 2026-11-02
---

## Description
PW-1330's cool coldest months (12.5-17 C vs Africa's 20) are in the Earth model too: warm land with rain in the 400-900 mm
band in both the model and GPCC has coldest month 13.7 C vs NCEP 16.4 (900-1500: 18.4 vs 20.0) and mean temperature
20.8 vs 22.6. Clouds don't enter the temperature except the summer split, so this is the winter/annual temperature.
Worlds at 400-900 mm: coldest month 14.2-19.6 C. Per region (observed-rain mask) Sahel 19.8 vs 22.5, S Africa savanna
12.7 vs 15.2, India 15.1 vs 19.2. Not diagnosed: winter-air advection, the temperature curve's seasonal range, or the rain
bias (model rain 2-3x too high in the Sahel/E Africa, which cools them). First: regress the miss on the model's rain error.
- [ ] decide the cause; Earth warm semi-arid coldest month within ~1 C of NCEP

## Updates
- 2026-11-02: Created from inbox draft draft-cool-coldest-month-warm-semiarid.md (found by lane125).
- 2026-11-02: Lane 131 (round2-diagnosis.md section 4): not the rain (r +0.28, wrong sign). ~1/3 is height (-1.5 C/km at all latitudes; mass elevation effect, He 2016). The rest is a lowland winter-range excess (dry sunny winters get no energy split). Three mass-elevation arms screened: 20-40 deg winters fixed, the ticket's cells only +0.5 C, 40-60 deg winters too mild. None to merge; inbox drafts mass-elevation-effect-highland-temperature and winter-energy-split-dry-season-warmth.
