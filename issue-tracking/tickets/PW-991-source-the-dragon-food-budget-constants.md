---
id: PW-991
title: "Source the dragon food budget constants: the sustainable offtake of wild herds (10%/yr) and the herders' tolerable stock loss (10%/yr)"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun-lane-43
blocked_by: []
relates: [PW-977, PW-975]
refs: [planet/lineages/history/megafauna.py, planet/lineages/prey.py, docs/references/megafauna/README.md]
created: 2026-10-29
updated: 2026-10-29
---

## Description
megafauna.OFFTAKE (10% of the wild herds' standing biomass a year, kept by a predator) and megafauna.STOCK_TOLERABLE (10% of herders' stock a year lost before they leave a range) are both model assumptions with no source on file; the first is the PW-967 review's rough figure. They set the food supply of the PW-977 stage 1 cap and section 5 of the age-of-dragons review. Find sources (wild ungulate harvest rates; herder tolerance of livestock predation, e.g. large-carnivore depredation surveys) and put the checked figures, or ranges, in the code and docs/references/megafauna/README.md.
- [ ] OFFTAKE sourced or marked as a range
- [ ] STOCK_TOLERABLE sourced

## Updates
- 2026-10-29: Created from inbox draft draft-dragon-food-shares-unverified.md (found by fun-lane-43).
