---
title: "History: no pigs, camelids, reindeer, yaks, buffalo or donkeys among the herd animals (and no soy or teff), so their tech rows were dropped"
type: task
status: todo
parent: null
milestone: null
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-69
blocked_by: []
relates: [PW-1122, PW-692]
refs: [planet/lineages/animal_defs.py, planet/lineages/crop_defs.py, planet/lineages/samples/techtree.toml, docs/references/tech-catalogue/food.toml]
---

## Description
In plain words: the tech tree now knows each of the history's own crops and herd animals as a tech (crop_wheat, animal_cattle...),
learned only when the history gives that people the stock. The catalogue also lists animals the history does not have: pigs,
donkeys, camels (both), llamas and alpacas, guinea pigs, reindeer, yaks, water buffalo, rabbits, cats; and crops: soybean, teff
and enset, the eastern North American seed crops, date palm. Those rows were dropped (PW-1122, list in
docs/references/tech-catalogue/README.md), with the techs that hung on them (llama and camel caravans, reindeer sleds, war
elephants). For the culinary goal pigs matter most (pork, lard, sausage, the forest-farming peoples), then the pack and milk
animals of deserts and mountains (camels, llamas, yaks) and reindeer for the far north.

What to do: add the missing stocks to animal_defs / crop_defs (anchor dates are in docs/references/tech-catalogue/hunt/food.toml,
several verified), then add their tech rows (stock = "animals:pig" etc.) and let riding, milking and pack animals take them in
`needs_any`.
- [ ] pigs, camelids, reindeer, yak, buffalo in the history's animals (with their ranges)
- [ ] the tech rows and needs_any entries
