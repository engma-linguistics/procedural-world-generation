---
id: PW-1327
title: "Summer energy split reads the wet tropics' sky cover as their sunshine (0.12-0.17 vs CRU 0.4-0.5): wet tropical summers 1.5-4 C cool"
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: lane121
blocked_by: []
relates: [PW-1279]
refs: [docs/review/base-climate/summer-heat/diagnosis.md, docs/review/base-climate/summer-heat/diag.py, "planet/climate.py::_summer_split", "planet/climate.py::sunshine", "planet/climate.py::shade", "planet/climate.py::clouds", "tools/earth_data.py::earth_clouds", data/earth/clouds_L7.npz]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the wet tropics' summers are too cool on Earth, because the summer heating step thinks they get
almost no sun. planet/climate.py::_summer_split takes sunshine(cloud) from the sky's total cover (0.9 in the Amazon
summer), which gives 11-17% sunshine. CRU measures 38-66%. The plants already use the convective discount
(`shade`, PW-806/808), but this step doesn't.

Earth L7, lane 121 (diag.py base vs sun):
- Land 0-10 deg summer sunshine: model 0.12 vs CRU 0.46. Land 10-20 deg: 0.22 vs 0.57.
- Warmest month 0-20 deg: 24.6 vs NCEP 26.5. With CRU's sunshine swapped in it's 26.7. That's the whole cool bias.
- Regions: West Africa coast -3.5 C, Sahel -3.9, East Africa -3.2, NE Brazil -2.3, Pacific NW -5.0.
- The catch: the split's reference (cloud_ref 0.63, so sunshine 0.38) sits on the same sky-cover scale, and CRU's
  land 20-60 deg summer sunshine is 0.62. A fix has to move the cell and the reference onto one scale together.
  Swapping CRU in alone also warms 20-40 deg by +0.3 and 40-60 deg by +1.7.

Fix sketch: feed the split clouds()' sunshine share (with cloud_sun_conv) in place of sunshine(cloud_sum), and set
its reference from CRU's land 20-60 deg summer share (0.62). Then re-check 0-20 deg, 40-60 deg and Köppen A/C. It
interacts with the deep-boundary-layer candidate (PW-1279's lane 121 arm) through the reference.

## Updates
- 2026-11-02: Status in-progress -> todo. 11-02 lane 125: confirmed; fold with PW-1334 (cloud first, then the split's reading and cloud_ref) and PW-1335 (open water, inspector).
- 2026-11-02: Status todo -> in-progress. 11-02: lane 125, diagnosis only (Earth model vs CRU cloud/sunshine and coldest month, then worlds).
- 2026-11-02: Created from inbox draft draft-summer-split-overcast-tropics.md (found by lane121).
