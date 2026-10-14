---
id: PW-007
title: "New rock types: granite, quartzite, flood basalt, carbonate caprock, tuff"
type: story
status: done
parent: PW-005
subsystem: surface
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: [PW-006]
refs: [planet/surface.py, planet/zoom.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Add rock types the landform classes need: granite intrusions (domes, inselbergs), quartzite (ridges),
continental flood basalt (traps, distinct from ocean-island basalt), chalk/dolomite caprock (cuestas,
karst), tuff (arcs). Each with erodibility (`surface.ROCKS`, `ROCK_K`) and lip resistance for falls
(`zoom.py`). Produced by the events that make them (plumes under continents, arcs, shallow seas).

## Updates
- 2026-10-14: Status todo -> done. Granite (exhumed arc roots), quartzite (sandstone folded in >45 km crust), flood basalt (continental lava, K 1.0), dolomite (limestone under 1 km), tuff (10% of continental arc growth, new MIX column); KP_RESIST/RUGGED entries in zoom.py. Branch landform.
- 2026-10-14: Created from the landform-classes epic (owner discussion 2026-10-14).
