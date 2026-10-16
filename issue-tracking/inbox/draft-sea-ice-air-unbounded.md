---
title: "Sea-ice air in deep icehouses reaches -114 C: the 3x frozen-sea amplification has no floor"
type: task
status: todo
parent: null
subsystem: climate
effort: s
impact: low
found_by: pw313
blocked_by: []
relates: [PW-226, PW-240]
refs: [planet/climate.py, tests/test_invariants.py]
---

## Description
In `climate._air_temps` the air over sea ice is `temp = sst + 3 x frozen` and `t_cold = sst - sea_half + 4.5 x
frozen`, with `frozen = min(t_sea_air - t_sea, 0)`: how far below freezing the latitude's sea would be. On Earth
(frozen ~-5.7 at the pole) this gives the Arctic's -19 C annual and -33 C winter, which is right. But it grows
linearly as a planet cools. In the PW-226 sweep (L4, seed 3, 300 Myr, main 6392e18), a deep icehouse at 60 Myr
(global 2.5 C, 14% ice, sea level -513 m) gives a coldest month of -114 C over the open ocean (elevation
-3954 m), below test_values_sane's -95 C bound. That test only runs seed 1, which never gets that cold.

Real winter air over thick multi-year sea ice bottoms out near -40..-50 C (the ocean's heat through the ice and
leads, and the inversion). A sound shape would be a saturating amplification (the sea-ice air's cooling levelling
off as the ice thickens), not a clamp. The land's coldest months in the same sweep are -61..-83 C.
- [ ] the coldest sea-ice air in deep icehouses (L4 seeds 1-5, 300 Myr) above ~-60 C
