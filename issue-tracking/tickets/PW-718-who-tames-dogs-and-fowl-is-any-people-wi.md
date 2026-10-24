---
id: PW-718
title: Who tames dogs and fowl is any people without a farm or herd use (dragonborn, kenku), not hunters by trait
type: task
status: todo
parent: PW-691
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun6
blocked_by: []
relates: [PW-691, PW-692, PW-695]
refs: [planet/lineages/animals.py, planet/lineages/animal_defs.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
`animal_defs.Animal.tame` weighs a people's shares {farm, herd, forage}; `forage` is "1 - farm - herd" for every
non-overlay people, so a people with no [[use]] row for fertile land or grazing counts as a forager. On run e9139f
(1df1c3, fantasy, all animals) dogs were first tamed 17.6 kyr ago by the dragonborn, and fowl by kenku / tabaxi
(dd02a0), where hunters (archaic humans, arctic hunters, goblinoids) would read better. Draws are in proportion to
presence x wild range, so the strongest early peoples win, whatever they are.
Options: (A) weight the draw by a `hunter` trait or the foraging use only (`LU.shares` wood share), (B) leave it as a
fantasy-world feature (any people may tame dogs), (C) per-animal `tame_traits`. Lean A with the tree's own traits.
Effects are small (dogs: speed x1.15, forage capacity +10%), so this is about the stories and the culinary goal.
- [ ] dogs are tamed by a foraging people in the real mode (humans), by the table's tamers in fantasy mode

## Updates
- 2026-10-24: Built on branch fun7: landuse.shares gains forage (the foraging use or the new hunter trait) and gather; a people with no use row is no longer a forager; dogs are tamed by hunters and forest foragers (arctic hunters in the real mode).
- 2026-10-23: Fold into the crops lane: tamers by trait (foraging/hunting use), not by absence of farm/herd.
- 2026-10-23: Created from inbox draft draft-animal-tamers-by-trait.md (found by fun6).
