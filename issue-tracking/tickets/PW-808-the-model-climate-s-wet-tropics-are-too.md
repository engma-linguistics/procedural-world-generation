---
id: PW-808
title: The model climate's wet tropics are too dim for forest, so tropical forest NPP is a thin margin (NPP ~55% of MOD17 at the equator)
type: task
status: todo
parent: PW-470
milestone: later
subsystem: climate
effort: m
impact: med
found_by: v1-finish-9
blocked_by: []
relates: [PW-806, PW-228, PW-290]
refs: [planet/climate.py, planet/vegetation.py, tools/veg_check.py, docs/review/base-climate/v1-finish-9/]
created: 2026-10-24
updated: 2026-11-03
---

## Description
After PW-806's plant fix, what is left of the forests' sensitivity to warming on star-warmed worlds comes from the base
climate, not the plants. On the Earth world's model climate (577526, wet equatorial land: < 10 deg, > 2000 mm) the
tropical evergreen trees' potential GPP is ~1350 g C/m2/yr against their respiration ~1000 (CUE ~0.2; observed
tropical forest GPP 2300-3500, CUE ~0.3: Luyssaert et al. 2007, Malhi 2012). tools/veg_check.py shows the same:
equatorial NPP on the model climate is 390-410 g C/m2/yr against MOD17's 700-920, while on the observed climate the
same vegetation gives 780-810. The plants are fine on observed weather; the model climate's tropics are too
cloudy/dim (light = 0.48 Ra (0.25 + 0.5 sunshine), sunshine from climate.clouds).

Evidence that this is the remaining lever (offline, rain held, `docs/review/base-climate/v1-finish-9/`): with the
stored cloud scaled by 0.6, Earth's wet-equatorial tree cover is 86 / 83 / 75% at +0 / +3 / +6 C and 79% at 180 ppm;
on the stored cloud it is 61 / 45 / 28% and 38%.

Try: check the equatorial cloud cover and sunshine hours of the model climate against CRU/ISCCP (Amazon, Congo,
Borneo: ~40-50% of possible sunshine) before touching any plant parameter.
- [ ] equatorial land NPP on the model climate within ~25% of MOD17 (veg_check), without retuning the plants

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Ice-age epic PW-470 is parked post-v1 (owner 10-28 timebox); PW-467 is the one kept as the timeboxed item.
- 2026-10-25: v1-finish-12: first check done (eqsun.py, Earth world 506694, wet-eq land): cover 0.82 vs NCEP 0.64; climate's sunshine 0.31-0.33 vs CRU 0.50-0.52; the plants used 0.21-0.23 (raw cover; fixed in be00f07, climate.shade). Remaining gap 0.31 vs 0.51 is the cloud scheme's (cover and cloud_sun_conv).
- 2026-10-24: Created from inbox draft draft-dim-model-tropics-thin-forest-margin.md (found by v1-finish-9).
