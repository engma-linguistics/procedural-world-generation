---
id: PW-144
title: Store humidity and sea-surface temperature per season on worlds
type: task
status: done
parent: null
subsystem: climate
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-142, PW-137]
refs: [planet/climate.py, planet/world.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner (2026-10-14) asked about humidity and sea temperature layers. Both are computed but thrown away: climate._season_inputs has the sea-surface temperature (sst, carried by the currents in climate.currents) and the air's moisture (qsat, rh); ocean.py has its own sst for density. Biomes and Koppen only reflect dryness indirectly (rain minus evaporation), not humidity. Store sst (annual + jul/jan) and humidity (e.g. relative humidity or dew point, jul/jan) as world layers with viewer layers and hover text, and use sst in the beach finder (PW-142). (The viewerocean agent may do the SST part as part of PW-137.)

## Updates
- 2026-10-14: Status todo -> done. viewerocean: worlds store sst, sst_jul, sst_jan (C, the sea's peak months; a smaller swing under near-perennial ice), dewpoint_jul/jan and humidity_jul/jan (climate.humidity, from the rain kernel's vapour; RH floor 15%, soft saturation). Viewer layers 'sea temperature' (year / July / January), 'humidity', 'dew point' with hover text. Beach finder uses the summer SST (PW-142). Earth world remade: 64fc00.
- 2026-10-14: Created.
