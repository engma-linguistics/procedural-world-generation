---
title: Animals as stocks and as food goods for the culinary pass (separate stocks, dairy, meat animals, fowl and eggs)
type: story
status: todo
parent: PW-691
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun6
blocked_by: []
relates: [PW-691, PW-692, PW-694]
refs: [planet/lineages/animals.py, planet/lineages/animal_defs.py, docs/proposals/lineages.md]
---

## Description
The first pass (PW-691 animals: horse, dog, sheep and goat, cattle, fowl, two rare fantasy rows) keeps each animal as one
homogeneous stock, stored as two bit-flag layers (`animal_wild`, `animal_known`). What PW-692 will want and is not built:
- separate stocks per taming (the goblin dogs of continent 3 vs the human dogs of continent 2): `Stock.tamed` already lists
  each taming with its landmass and people, but `rd` merges them;
- `dairy` is a summary per people (`meta.animals.dairy`: milk share x the share of its land with a dairy animal), not a layer or
  a per-cell good; meat/eggs/draft uses are only the table's effect keys; a cell-level `animal_<id>` share per people would
  give the cuisine pass what each people herds where;
- peoples with `diet = carnivore` and `raw_meat`, and the dog-as-food taboo for canid peoples, are not consulted;
- no wild fauna that is not tamed (eland-like, owner ruling): wild ranges exist only for the table's animals; a hunting
  good from the same range functions would be cheap.
- [ ] decide the per-cell representation (bit flags per people, or a share layer per animal)
