---
id: PW-059
title: "earth_check: the Orinoco gauge picks up the Amazon"
type: task
status: done
parent: null
subsystem: infra
effort: xs
impact: low
found_by: water
blocked_by: []
relates: []
refs: [tools/earth_check.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
A coarse-routing artifact in `tools/earth_check.py`'s discharge check: the Orinoco gauge cell drains
Amazon water. Move the gauge or mask by basin.

## Updates
- 2026-10-14: Status in-progress -> done. Moving the gauge can't help: at L6 every cell within 150 km of Caicara routes through the Casiquiare gap into the Rio Negro and out the Amazon mouth (the Orinoco delta cells carry <800 m3/s). The Ob likewise ends at the Yenisei's mouth. earth_check now detects a river whose ends are shared with a bigger listed river and reports it as 'drains into the X' with no discharge (ratio -), separately for model and obs-P routing, instead of double counting. Fields model_captured_by/obs_rain_captured_by added to the JSON.
- 2026-10-14: Status todo -> in-progress. Started on branch quickwins.
- 2026-10-14: Migrated from plan_next@bdc967f: Known issues → Rivers, lakes, sediment.
