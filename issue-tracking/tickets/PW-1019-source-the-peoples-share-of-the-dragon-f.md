---
id: PW-1019
title: "Source the peoples' share of the dragon food budget: a person's food, the share of it that is wild game, and the guild's size-class rule"
type: task
status: todo
parent: null
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: fun-lane-45b
blocked_by: []
relates: [PW-977, PW-991, PW-974]
refs: [planet/lineages/history/megafauna.py, docs/references/megafauna/README.md]
created: 2026-10-29
updated: 2026-11-03
---

## Description
PW-977 stage 2 (fun lanes 45/45b) lets the peoples' hunters and the rest of the predator guild draw on the wild offtake before
the dragons. Three of its inputs have no source on file:
- `megafauna.PERSON_KCAL_YR` = 2,200 kcal a day (a round number; the proposal's Kleiber x 1.7 figure for a 65 kg forager is ~1,900).
- `megafauna.WILD_MEAT` = (0.5, 0.05): the share of a forager's food that is wild game, and of any other way of life's. An
  ethnographic figure for hunter-gatherer diets (share of energy from animal food) is wanted; the 5% for herders, farmers and
  gardeners is a guess. An earlier comment cited a diet survey from memory; it was removed because the paper is not on file.
- `megafauna.guild_ratio()` (~5.0): the smaller carnivores' food is ~5 times the apex class's, from Carbone, Turvey & Bielby 2011's
  Table 1 size classes (checked 10-29, PDF p. 2683: 20.6 kg 79.9%, 58.3 kg 19.0%, 1,123 kg 0.9%, 5,347 kg 0.1% of the guild's
  individuals) times a Kleiber M^0.75 that is not from the paper. One Cretaceous guild stands in for every world's.

Cross-checks already on file: Farlow 1993 (p. 172) 7 kJ per g live mass puts a 0.5 t head at ~840,000 kcal, so HEAD_KCAL
625,000 is ~3/4 eaten; Farlow p. 176 gives prey:predator 100:1-200:1 in modern large-mammal faunas.
- [ ] a source (or a range) for the forager's game share
- [ ] a source for the daily food figure
- [ ] the guild rule checked against a living large-mammal guild (e.g. Serengeti carnivore biomass by species)

## Updates
- 2026-11-03: Parked 11-03 per fresh-eyes review (docs/review/fresh-eyes/2026-11-03.md s3): milestone v2 -> later. Dragon-density tail; PW-961 stays.
- 2026-10-31: Lane 90: the peoples' game take now uses the shared edible figure HEAD_KCAL (Carbone 2007 carcass use); WILD_MEAT still unsourced. docs/review/dragon-food-chain/report.md
- 2026-10-29: Created from inbox draft draft-food-budget-peoples-share-constants-unverified.md (found by fun-lane-45b).
