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
updated: 2026-10-31
---

## Description
megafauna.OFFTAKE (10% of the wild herds' standing biomass a year, kept by a predator) and megafauna.STOCK_TOLERABLE (10% of herders' stock a year lost before they leave a range) are both model assumptions with no source on file; the first is the PW-967 review's rough figure. They set the food supply of the PW-977 stage 1 cap and section 5 of the age-of-dragons review. Find sources (wild ungulate harvest rates; herder tolerance of livestock predation, e.g. large-carnivore depredation surveys) and put the checked figures, or ranges, in the code and docs/references/megafauna/README.md.
- [x] OFFTAKE sourced or marked as a range
- [ ] STOCK_TOLERABLE sourced

## Updates
- 2026-10-31: Lane 90: OFFTAKE now sourced (Farlow 1993, PW-1072). STOCK_TOLERABLE (10%) still unsourced. docs/review/dragon-food-chain/report.md
- 2026-10-29: Papers read 10-29: Farlow 1993 (Am J Sci 293:167, on file) bounds OFFTAKE. Prey biomass turnover = 0.94 M^-0.28 per yr (M kg; eq. 6, p. 172, from Farlow 1990): 0.26/0.17/0.14 per yr at 100/500/1000 kg prey, the most that all predators together can take; modern large-mammal faunas run prey:predator 100:1-200:1 against his 50:1 best case (p. 176), so one big-predator guild gets well under the turnover. 0.10 sits inside that range; the comment now cites it and calls the value a judgement. STOCK_TOLERABLE: no source in this batch (Farlow's eq. 6 gives 0.17/yr turnover for 500 kg stock, so the 15-25% in the comment holds; the herders' tolerance is still unsourced). First box: marked as a range.
- 2026-10-29: Created from inbox draft draft-dragon-food-shares-unverified.md (found by fun-lane-43).
