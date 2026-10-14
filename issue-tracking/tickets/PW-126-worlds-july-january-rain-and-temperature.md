---
id: PW-126
title: "Worlds: July / January rain and temperature layers with a season picker"
type: task
status: done
parent: null
subsystem: viewer
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-044, PW-107]
refs: [planet/world.py, viewer/index.html]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner looked for July/January views of rain and temperature and found only the winds' season picker (PW-044). climate.compute already makes p_jul/p_jan (and seasonal temperatures internally); worlds store only the annual precipitation, temperature and warm_month/cold_month. Store July and January precipitation and temperature in worlds (store.LAYERS) and give the Rain and Temperature layers the same year/July/January picker as the winds, with ?season= deep links. Note that warm_month/cold_month are not July/January (they swap hemispheres). Runs: see PW-107 (seasonal winds in keyframes); add seasonal rain there too if the frame-size cost is acceptable.

## Updates
- 2026-10-14: Status todo -> done. Worlds store temperature_jul/jan and precipitation_jul/jan (world.seasons in world.finish: July = warmest month in the north, coldest in the south; rain = half-year rates); viewer Temperature/Rain get a year/July/January picker shared with the winds and ?season=; hover names the season. Demo world 67317b (run 428083 @ 1000 Myr, L7). Runs and zooms: inbox drafts.
- 2026-10-14: Created.
