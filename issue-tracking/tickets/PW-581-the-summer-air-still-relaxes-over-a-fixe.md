---
id: PW-581
title: The summer air still relaxes over a fixed 450 km while the winter's is now per time (PW-575); mountain cells' own winters run cold (Canadian Rockies −4.7 → −7.6 C)
type: task
status: todo
parent: PW-570
milestone: later
subsystem: climate
effort: m
impact: med
found_by: base-climate-laneA6
blocked_by: []
relates: [PW-575, PW-352, PW-573, PW-026]
refs: [planet/climate.py, tools/climate_bias.py, docs/review/base-climate/stages.md]
created: 2026-10-22
updated: 2026-11-03
---

## Description
PW-575 (lane A6) made the winter air over land relax toward the land's own winter in time: the air mass (`air_m`,
1000 m) against `ice_b`, ~4 days, so it reaches U × 4 days inland. Two follow-ups.

1. **The summer.** `_air_temps` still carries the summer air over a fixed `air_km_s` (450 km), whatever the wind. For
   stage 3 (PW-352 / PW-573), the summer's relaxation should be per time as well, with the summer's own exchange (the
   sensible heat of a sunlit, convective boundary layer is much faster than the winter's loss to space). Small lands in
   a strong westerly would then keep the sea's summer, which is PW-573's mechanism.
   - The winter's change alone already moved the southern coastal seasonal range 16.3 → 14.3 C (NCEP 9.6).
2. **Mountains.** Ground above `air_m` cuts the carried air off, so mountain cells relax fully to their own winter.
   This is what keeps the prairies' cold behind the Rockies (the Hudson Bay lowlands stay at +5.5 C), but the
   Canadian Rockies' own coldest month goes −4.7 → −7.6 C too cold and Tibet −5.4 → −4.1. On a mountain the air
   mass isn't cut off but lifted. A better form may cut off only the air downstream of a ridge, not on it.

`air_m` is a new constant. Its sensitivity on Earth L6 (Fennoscandia / Hudson Bay lowlands coldest-month bias):
800 m −11.2 / +5.0, 1000 m −8.9 / +5.5, 1250 m −7.3 / +6.7.

- [ ] the summer carry per time (stage 3), the SH coastal range within 1.3× NCEP
- [ ] mountain cells' winters within ±6 C without losing the prairies' cold pool

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: calibration or second-order physics refinement, not needed for the planet to be stable or for the culinary goal
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-22: Created from inbox draft draft-air-relaxation-in-time-summer-and-mountains.md (found by base-climate-laneA6).
