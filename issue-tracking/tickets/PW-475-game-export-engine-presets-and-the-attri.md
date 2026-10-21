---
id: PW-475
title: "Game export: engine presets and the attributes of PW-099 and PW-206"
type: task
status: todo
parent: null
subsystem: store
effort: s
impact: low
found_by: export
blocked_by: []
relates: [PW-100, PW-099, PW-206]
refs: [planet/export.py, README.md]
created: 2026-10-20
updated: 2026-10-20
---

## Description
`planet export` (PW-100) is engine-neutral: 16-bit PNG or raw `.r16` tiles with `--tile` / `--overlap`,
a splat set derived by simple rules, GeoJSON features. Left out until a target engine is chosen:
presets (`--engine unity|unreal|godot`: power-of-two-plus-one sizes, `.r16`, import notes), a
documented import recipe, and a check of cube-face seams at the edges. The manifest leaves room for
PW-099 (passes, harbours, navigable rivers, fertility) and PW-206 (travel cost, forage, timber,
hazards): add them as `layouts.<name>.layers` entries and feature kinds (`pass`, `harbour`,
`resource`) when those tickets land; nothing in the store holds passes or resources yet, so the export
has none. The splat rules (`export.splat_weights`) are simple; PW-206's vegetation attributes would
replace them.

## Updates
- 2026-10-20: Created from inbox draft draft-export-engine-presets-fields.md (found by export).
