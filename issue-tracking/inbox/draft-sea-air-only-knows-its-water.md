---
title: "The sea's air only knows its own water: Hudson Bay, Baffin Bay and Okhotsk stay open in winter (Hudson Bay -5 vs -28 C), like the Antarctic pack (PW-346)"
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: base-climate-review
blocked_by: []
relates: [PW-346, PW-038, PW-457]
refs: [planet/climate.py, tools/climate_bias.py, docs/review/base-climate-review.md]
---

## Description
For PW-346 (probably `--merge-into PW-346`). It is the same cause as PW-346's, beyond the Southern Ocean.

**The mechanism.** In `climate._air_temps` a sea cell's air is pinned to its own water (the carry's k = 0 at sea). It
gets the sea-ice inversion only where the *latitude's* annual sea would freeze (`frozen`, from `sea_temperature`). So
leeward and enclosed seas never take the continent's winter air, and never freeze over.

**Earth L6** (`tools/climate_bias.py`), coldest month, model against NCEP:

| sea | model | NCEP |
|---|---|---|
| Hudson Bay | −5.2 (annual 0.0) | −28.2 (annual −8.3) |
| Sea of Okhotsk | −0.4 | −11.8 |
| Baffin Bay | −11.9 | −29.5 |
| Southern Ocean 60–70S | −5.8 | −14.5 |

- The winter sea-ice proxy (sea whose coldest month is below −5 C) is 15.0 Mkm2 in the north (NCEP 16.8) and 15.0 in
  the south (NCEP 20.2).
- On land, Labrador's winters are 3.6 C too warm and the Hudson Bay lowlands' 5.5 C. That is part of "North America
  too warm".

**Why it matters beyond Earth.** It's a mechanism error on any planet. Leeward seas, bays and seas beside ice sheets
run warm in winter, and the sea-ice edge is set by latitude.

**What to try.** PW-346's own proposal, on every sea:
- The air over the sea takes part in the carry.
- It relaxes toward the water's temperature in proportion to the open water, and is land-like where the sea is frozen.
- The freeze then follows the local air.

Do it after the overturning fix, because the brine reads the sea-ice share.

- [ ] Hudson Bay, Okhotsk and Baffin Bay freeze in winter, with their coldest month within 8 C; the Southern Ocean
  60–70S within 4 C
- [ ] the winter sea-ice proxy (or an observed set) within ±25% per hemisphere; the Arctic Ocean not worse
- [ ] at dT −6, the southern sea ice is 1.5–2.5× today's
