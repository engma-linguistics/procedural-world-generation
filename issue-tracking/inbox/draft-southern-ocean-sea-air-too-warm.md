---
title: "Southern Ocean air 4-8 C too warm (60-80S), worst over the seasonal pack ice: the sea's own air ignores winter ice and the continent's outflow"
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: med
found_by: polar-bundle
blocked_by: []
relates: [PW-335, PW-337, PW-017, PW-313]
refs: [planet/climate.py, tools/earth_check.py, docs/review/audit/polar-bundle.md]
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
