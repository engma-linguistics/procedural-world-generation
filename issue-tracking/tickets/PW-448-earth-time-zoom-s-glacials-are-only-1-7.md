---
id: PW-448
title: Earth time zoom's glacials are only ~1.7 C colder (real LGM ~5-6 C), so no Laurentide sheet south of ~60 N
type: task
status: todo
parent: null
subsystem: timezoom
effort: m
impact: high
found_by: owner-2026-10-20
blocked_by: []
relates: [PW-030, PW-435, PW-447]
refs: [planet/timezoom/forcing.py]
created: 2026-10-20
updated: 2026-10-20
---

## Description
Owner compared time zoom 755514's glacial maximum with an LGM map (Svendsen et al. 2004): the simulation has no Laurentide below ~60 N, no Hudson Bay ice, no Scandinavian sheet to northern Germany, no Barents sheet. run.txt: global_T 14.5 -> 12.8 C at the deepest glacial (-43 m, 5.9% of the surface iced) against the real ~-5 to -6 C, -125 m, ~8%. Investigate with measurements, not supposition: decompose the glacial cooling into orbit, CO2, ice albedo and any other terms, and compare each with Earth's LGM budget (CO2 ~ -90 ppm ~ -1.5 to -2 C with feedbacks; ice albedo ~ -3 C; dust and vegetation). Check whether the forcing-to-temperature chain lacks the water-vapour/lapse-rate amplification, whether CO2 is tied to the extra ice so small ice gives small CO2 (chicken and egg), whether Earth wrongly gets a run moment's halved CO2 cap, and what summer temperature and snow balance the Canadian interior (Keewatin/Labrador/Hudson Bay) sees at glacial orbits. Fix only what the measurements show is wrong. Planet-relative, no Earth fudges.

## Updates
- 2026-10-20: Created.
