---
id: PW-039
title: East Antarctic interior about 10 °C too warm
type: task
status: todo
parent: null
milestone: null
subsystem: climate
effort: m
impact: med
found_by: viewer2
blocked_by: []
relates: []
refs: [planet/climate.py, docs/overview/earth_temperature_diff.jpg, tools/climate_bias.py]
created: 2026-10-14
updated: 2026-10-22
---

## Description
The Earth world's temperature-difference view (model − observed) shows the East Antarctic interior
~10 °C too warm. Likely the lapse rate / inversion over high ice, or the polar temperature profile.
Check on world dc3732 (deleted) (`?obs=diff`).

## Updates
- 2026-10-22: Merged inbox draft draft-annual-mean-coreless-winter.md ("Annual mean = midpoint of warmest and coldest month: the Antarctic plateau's annual is +9 C while its months are +2/+3 C (most of PW-039)", found by base-climate-review).
  For PW-039 (probably `--merge-into PW-039`).
  
  **Measured** on Earth L6 (`tools/climate_bias.py`), the Antarctic plateau above 2500 m, model against NCEP:
  
  | | model | NCEP | bias |
  |---|---|---|---|
  | warmest month | −19.3 | −21.3 | +2.0 |
  | coldest month | −55.3 | −58.5 | +3.2 |
  | annual mean | −36.7 | −45.7 | +9.0 |
  
  **Why.** The model's annual mean on land is 0.5 (t_warm + t_cold), a sine year. Real polar interiors have a long, flat
  "coreless" winter: NCEP's annual mean there is ~6 C below its own midpoint.
  
  **Why it matters, a little.** Melt runs on the warm months, so the ice barely feels it. But permafrost, ice
  temperature, soils and the weathering factor all read the annual mean.
  
  **What to try.** Take the annual mean from a year shape that knows how long the polar night is (the insolation per
  month at the latitude).
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Climate (seen on the deleted Earth world 8e052d (deleted); still visible on 2f38e3 per docs/overview.md).
