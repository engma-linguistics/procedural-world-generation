---
title: "Boreal fire return: GFED4.1s gives a ~170-220 yr rotation on Earth's boreal forest, not 50-200 (update for PW-347)"
type: task
status: todo
parent: null
subsystem: surface
effort: xs
impact: low
found_by: pw204-vegdata
blocked_by: []
relates: [PW-347]
refs: [tools/veg_check.py, tools/earth_data.py]
---

## Description
For the coordinator to merge into PW-347 (`board.py intake --merge-into PW-347`). veg_check now measures boreal fire on gridded GFED4.1s burned area (2001-2015 mean, small fires included). L6 Earth world 7873f9, observed climate, fire rotation (area / area burned a year) and median cell interval:
- model's boreal types: rotation 294 yr, median 381 yr, 0.058 Mkm2/yr;
- GFED on the same cells: rotation 166 yr, median 510 yr;
- GFED on potential vegetation's boreal forest (Ramankutty & Foley classes 6-7): rotation 216 yr, median 561 yr, 0.04 Mkm2/yr.
So the observed target for PW-347 is a rotation of ~170-220 yr at this resolution (15 years of satellite data; fire concentrates in a few cells, which is why the median is longer than the rotation), and the model is ~1.4-1.8x too long, not 2-7x. PW-347's "50-200 yr" comes from stand-scale literature. Suggest changing its acceptance to "boreal rotation 150-250 yr (GFED 166-216)".
