---
title: "Annual mean = midpoint of warmest and coldest month: the Antarctic plateau's annual is +9 C while its months are +2/+3 C (most of PW-039)"
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: s
impact: low
found_by: base-climate-review
blocked_by: []
relates: [PW-039]
refs: [planet/climate.py, tools/climate_bias.py]
---

## Description
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
