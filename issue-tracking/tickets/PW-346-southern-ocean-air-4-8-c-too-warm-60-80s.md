---
id: PW-346
title: "Southern Ocean air 4-8 C too warm (60-80S), worst over the seasonal pack ice: the sea's own air ignores winter ice and the continent's outflow"
type: task
status: todo
parent: null
milestone: null
subsystem: climate
effort: m
impact: med
found_by: polar-bundle
blocked_by: []
relates: [PW-335, PW-337, PW-017, PW-313]
refs: [planet/climate.py, tools/earth_check.py, docs/review/audit/polar-bundle.md, tools/climate_bias.py, docs/review/base-climate-review.md]
created: 2026-10-16
updated: 2026-10-22
---

## Description
Earth L6, dT 0, after the polar bundle. Sea air by band, model / NCEP 2 m (C):

| band | warmest month | coldest month | annual (earth_check) |
|---|---|---|---|
| 60-65S | 8.8 / 3.8 | -1.3 / -1.1 | |
| 65-70S | 6.1 / 1.4 | -4.5 / -10.2 | -70..-60: -0.2 / -6.1 |
| 70-75S | 4.1 / -0.4 | -7.7 / -20.4 | |
| 75-80S | 2.0 / -0.9 | -16.3 / -28.5 | -80..-70: -8.7 / -16.7 |

(The Arctic's sea air is within ~1-2 C at 70-85N in both months.) Two causes in `climate._air_temps`:
- Winter: a sea cell's own coldest month is `sst - sea_half` (+ the sea-ice inversion only where the
  latitude's *annual* sea would be below freezing). Around Antarctica the annual sea is above freezing, so the
  winter pack ice (open_w = 0 there) gets the water's winter, -4 to -8 C, not the -10 to -28 C air over the
  pack. The land's carry already treats a frozen winter sea as land air ("a frozen sea moderates nothing");
  the sea cells' own air doesn't.
- Summer: PW-335's `max(sst + frozen + sea_half, FREEZE)` gives the full seasonal swing on a sea that is
  ice-covered half the year and sits beside a continent whose cold air drains out over it (sea cells are
  pinned to the sea's air: the carry's k = 0 at sea). At the same annual sst (~0.5 C) NCEP has +7 C summers
  at 65N and +1.4 C at 65S. Before PW-335 the sea's summer was -1.9 / -6.6 C at 70-80S (closer by luck).

Consequences: coastal mixing warms Antarctica's margins in summer (the probe's losing margin cells sit at a
surface warmest month of 0 to +1.6 C, observed coasts -1 to -4), the winter sea ice grows too little
(ice_growth from the sea air: brine and the Antarctic overturning, PW-017), and the sea-ice share of the
year. Try: the sea's own winter air over frozen water as the carry's eq_w (land-like where open_w = 0), and
letting the air over (frozen) sea take part in the carry, so a continent's outflow cools the sea beside it.
- [ ] 60-80S sea air within ~2 C of NCEP in both months, the Arctic not worse
- [ ] re-run the PW-313 probe and earth_check's overturning (Ross/Weddell)

## Updates
- 2026-10-22: Merged inbox draft draft-sea-air-only-knows-its-water.md ("The sea's air only knows its own water: Hudson Bay, Baffin Bay and Okhotsk stay open in winter (Hudson Bay -5 vs -28 C), like the Antarctic pack (PW-346)", found by base-climate-review).
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
- 2026-10-16: Created from inbox draft draft-southern-ocean-sea-air-too-warm.md (found by polar-bundle).
