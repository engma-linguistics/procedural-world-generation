---
title: "Coldest months near -95 C on 8+ km polar-ish peaks (bare or margin-thin ice) after PW-276"
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: low
found_by: ice-fix
blocked_by: []
relates: [PW-226, PW-276, PW-172]
refs: [planet/climate.py, planet/tectonics/earth.py, tests/test_invariants.py]
---

## Description
After PW-276 (ice surface from the margin's bed) and PW-277 (one ice-surface climate) the run's ice on high
ground is margin-thin (~350 m), so the remaining extreme surfaces are the peaks themselves. Probe over every
climate update (L5, 1000 Myr): seed 2 coldest month -93.5 C (1 cell below -90), seed 11 -97.4 C (8 cells); highest
iced surfaces 9.2 / 8.4 km, i.e. 8-9 km peaks at ~60-65 deg plus a margin's ice (L4 seed 4: -97.5 C on a 7-8 km
plateau at 66-74 N). test_values_sane's restored -95 C bound holds on the L4 seed-1 test run (-55 C) but would
not on these.
It is now the lapse rate on very high ground in a continental polar winter, not the ice. Worth checking:
- whether 8-9 km peaks at 60+ deg are expected (PW-172 is about > 9.5 km spikes);
- whether the climate's winter inversion (polar winters are colder at the ground than aloft, so a peak is not
  6.5 C/km colder than a frozen lowland in January) should cap the lapse rate's cooling in winter.
- [ ] coldest months above ~-90 C on L5/L6 seeds 2 and 11, or a stated physical reason for the colder ones
