---
id: PW-438
title: Cold eras' depth is not set by the climate drift sd; look at the ice-albedo / CO2 feedback instead
type: task
status: needs-decision
parent: null
subsystem: climate
effort: m
impact: high
found_by: pw434
blocked_by: []
relates: [PW-434, PW-240, PW-366, PW-364]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py, planet/icemass.py, tools/sealevel.py]
created: 2026-10-19
updated: 2026-10-20
---

## Description
PW-434 option B (a smaller `climate_drift` sd) did not bring the 4 L6 seeds under the ~-430 m bar. L6, 1 Gyr,
`tools/sealevel.py`, sea level from ice on 4 Myr samples (mean / worst / share below -150 m / below -430 m):

| seed | sd 3.0 (PW-366) | sd 2.0 | sd 1.6 | sd 2.0, drift time 15 Myr |
|---|---|---|---|---|
| 3199 | -82 / -368 / 19% / 0% | -68 / -518 / 14% / 4% | -19 / -66 / 0% / 0% | -30 / -227 / 3% / 0% |
| 11 | -92 / -609 / 18% / 7% | -107 / -446 / 25% / 3% | -134 / -511 / 31% / 7% | -108 / -521 / 18% / 5% |
| 2 | -112 / -542 / 25% / 5% | -124 / -570 / 37% / 4% | -77 / -500 / 18% / 2% | -103 / -475 / 25% / 8% |
| 21 | -75 / -510 / 17% / 5% | -17 / -109 / 0% / 0% | -58 / -294 / 13% / 0% | -102 / -681 / 15% / 12% |

The result is chaotic per seed (a changed sd reshuffles which seed goes deep) and seed 11 is as deep at sd 1.6 as
at 3.0, so the deep eras are not driven by the drift's amplitude: once a planet dips, the ice-albedo feedback and
the thicker PW-366 sheets carry it to -450..-600 m regardless. A stronger thermostat would have to act on that
feedback: `ice_albedo` / `ice_albedo_max`, the weathering thermostat's strength (WEATHER_K), or option C
(`icemass.LOCAL` 0.3 -> 0.15). Lean: look at how far the albedo feedback drives dT below the drift's own
excursion in the deepest eras (seed 11 / 2), then pick between a smaller `ice_albedo_max` and option C.
- [ ] decide; re-run the 4-seed table after

## Updates
- 2026-10-20: Merged attempt 3 (base level, weathering mask, CO2-dependent weathering): (1) the weathering-to-base-level term counted height from the current sea, so a glacial lowstand lifted every plain (`base_rise` in `surface.erode`); (2) the weathering sink counted glacial erosion on ground the ice left during the update (`sim.weathered`, masked by the ice the erosion ran under); (3) GEOCARB f(CO2) ~ pCO2^0.4 (`WEATHER_CO2`, co2 = ln(source/sink)/0.4), forcing clip widened from +-1.5 to `CO2_MAX` = 3, rates and baselines start at the first real erosion. L6 1 Gyr, sea level from ice (worst / % of time below -430 m / % below -150 m):

  | seed | before | after |
  |---|---|---|
  | 3199 | -368 / 0% / 19% | -386 / 0% / 31% |
  | 11 | -609 / 7.2% / 18% | -569 / 5.2% / 37% |
  | 2 | -542 / 5.2% / 26% | -404 / 0% / 22% |
  | 21 | -510 / 5.2% / 17% | -393 / 0% / 11% |

  Net improvement, two parts are bug fixes. Stays open: seed 11 still spends 5.2% below -430 m, and the time below -150 m rose on 3199 and 11. Follow-ups: drafts draft-ice-extent-at-dt-4.md and draft-cold-era-weathering-sink-composition.md. Goldens updated for the changed sim.
- 2026-10-20: Owner/coordinator 2026-10-20: separate from the time zoom's cycle work. Idea to try here if it pans out in the time zoom (PW-440): CO2 headroom, i.e. CO2 must not sit at its floor in cold eras, so it can still rise and end them. A clipped CO2 leaves no feedback to recover with.
- 2026-10-19: Created from inbox draft draft-cold-eras-ice-albedo-feedback.md (found by pw434).
