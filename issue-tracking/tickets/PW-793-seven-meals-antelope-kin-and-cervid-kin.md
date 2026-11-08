---
id: PW-793
title: "seven_meals: antelope-kin and cervid-kin (all their cultures, tundra included) don't dairy by default (milks=false); cultural uptake left to civ work"
type: task
status: done
parent: PW-692
milestone: v2
subsystem: food
effort: xs
impact: med
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-10-24
updated: 2026-11-03
---

## Description
Owner 2026-10-24, reversing the earlier default after the dairy table: no dairying for the setting's 'tieflings'; differentiates them; maybe culturally picked up later (PW-661/PW-768).

## Updates
- 2026-11-03: Status todo -> done. Lane 164: confirmed in the cuisine sheet: dairy_of returns none for milks = false, so antelope-kin and cervid-kin sheets never list milk (3c1caf culture 475, docs/review/food/cuisine-sheet/round1.md); test_cuisine.py asserts the rule.
- 2026-10-24: Created.
- 2026-10-24: (fun lane 22) `milks = false` on antelope_folk and cervid_folk in seven_meals.toml (all nine cultures inherit it, tundra herders included; ways of life unchanged); briefs say "do not milk their animals". Preset test asserts it.
