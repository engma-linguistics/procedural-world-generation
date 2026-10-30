---
id: PW-1102
title: The subtropics' sinking-air belt is the same all round the latitude, so the oceans' western flanks (SE USA) are as suppressed as their eastern ones
type: task
status: todo
parent: PW-013
milestone: v2
subsystem: climate
effort: m
impact: low
found_by: lane58
blocked_by: []
relates: [PW-1097, PW-1093]
refs: [planet/climate.py, tools/moisture_regions.py, docs/review/base-climate/moisture-budget/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. The model makes the dry, sinking air of the subtropics a band at the same strength all the way round
each latitude (`_season_inputs`' sink: ~25 deg from the rain belt). In reality the sinking is strong on the eastern
sides of the oceans (California, Chile, Namibia) and weak on the western sides (Florida, southern Brazil, eastern
China), where the subtropical highs send moist air poleward. So the model holds the rain down on SE USA as hard as
on the Sahara's Atlantic coast.

Probe (lane 58, Earth L6, kernel re-run): take the sink off the boxes SE USA, Gulf, W Atlantic 25-40 N and Pampas,
S Brazil, SW Atlantic, in its three uses (ls's belt_dry, cv_sink, the storm-lift mask):
- SE USA summer 912 -> 1023 (GPCC 1323), annual 636 -> 707
- Pampas 401 -> 366 (its upwind sea rains more)
- B 25.2 -> 25.0; the north mid-latitude land unchanged

A small, sound gain for the humid subtropics' summers. It needs a rule for "western flank" that works on generated
worlds, e.g. sink weighted by the sea's east-west position in its basin, or by monsoon_wind's subtropical-high
warmth. It fits with the land-sea inflow drafts.
- [ ] a generic form, one Earth solve, then a paired judge

## Updates
- 2026-10-30: Created from inbox draft draft-subtropical-sink-belt-zonal.md (found by lane58).
