---
title: "Fennoscandia's winter still 8.9 C too cold after PW-575's winds: the Barents and the northern Greenland Sea freeze (no Atlantic water past the sinking site), and Iceland sits in their cold"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: climate
effort: l
impact: high
found_by: base-climate-laneA6
blocked_by: []
relates: [PW-575, PW-577, PW-458, PW-026]
refs: [planet/climate.py, planet/ocean.py, tools/climate_bias.py, docs/review/base-climate/stages.md, docs/review/base-climate/laneA6/]
---

## Description
Found closing PW-575 (lane A6, Earth L6). With the wind belts following the air masses and the winter air relaxing
in time (stages.md, "PW-575"), Fennoscandia's coldest month goes −11.9 → −8.9 C against NCEP. The bar is ±6. The
Norwegian coast is now right (−4.1 against −5.2), Sweden is −14.0 against −8.3, Finland −22.1 against −10.8, and Kola
−14.0 too cold.

**What is left is the sea north of 72N, not the winds.**
- The coldest-month bias map (`scratchpad` probe `grid2.py`, model − NCEP) is within ±3 C over the open Norwegian
  Sea up to 70N. North of 72N the whole Barents Sea and the Greenland Sea are frozen at −24 to −26 C, against NCEP's
  −5 to −10 (biases −15 to −23). The Barents box is −24.6 against −10.8.
- On Earth the Atlantic Water flows on past the Nordic Seas' sinking into the Barents (the North Cape current) and up
  West Spitsbergen, and keeps both open. In the model the overturning's inflow ends at its sinking site (69N 14W),
  and the wind-driven currents don't carry that heat north of it. Recomputing the currents with the new winds
  (tried) changes nothing there.
- The frozen Barents is a cold high, so the wind there stays north-easterly (front_shift sees no warm anomaly), and
  Finland and Kola take its air. That is the feedback that would open once the water is open.
- Iceland's coldest month gets worse, −7.8 → −12.4 C: the new winds bring it the frozen Denmark Strait's and Greenland
  Sea's air (−20 to −22 C too cold at 66–68N, 30–18W).

**What to try:** the Atlantic Water's path past the sinking site (a share of the inflow continuing poleward as the
Barents and Fram branches, which sink in the Arctic), in `ocean.solve`'s inflow, so the Barents' winter water is open
where the inflow reaches it. Check the Barents and the Greenland Sea's winter sea air, then Finland, Kola and
Iceland. Generated worlds with a polar sea beyond their sinking site have the same gap.

- [ ] the Barents Sea's coldest month within ~6 C of NCEP, the Norwegian Sea still open
- [ ] Fennoscandia's coldest month within ±6 C
