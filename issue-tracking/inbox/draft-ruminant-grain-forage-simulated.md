---
title: Ruminant peoples' forage-led diet is only described, not simulated (body.grain is a note; nothing weights their fields)
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: low
found_by: fun-lane-24
blocked_by: []
relates: [PW-850, PW-793, PW-800]
refs: [planet/lineages/spec.py, planet/lineages/crops.py, planet/lineages/samples/seven_meals.toml]
---

## Description
PW-850 shipped the owner-approved diet as data: `body.grain = "moderate"` on the ruminant stem (a body note: "take grain in moderation ... fields lead with legumes, roots and leafy fodder"), antelope-kin and cervid-kin mostly farmers, with the savanna antelope-kin horticulturalists and the boreal cervid-kin foragers (the "some gatherers"), and no dairy. Nothing in the simulation reads `grain`: crops.py weights every people's farm capacity by the same staple crops, so the ruminant peoples' cropland still counts wheat and rice as much as lentils, roots and greens, and the brief only says it in a body line.
Option: make a people's crop uptake (crops.Crops adoption or k_mult) scale grain staples by body.grain (normal 1, moderate ~0.5, none 0) and forage staples (pulses, roots, greens) up correspondingly, so a ruminant people's fields and straw come out forage-led. Needs a judgement on the numbers (owner defers geophysics but this is a lore number), and a check that the ruminant peoples do not starve out where only grain grows.
- [ ] a ruminant farming culture's staple mix reads forage-led in the brief's crops line
