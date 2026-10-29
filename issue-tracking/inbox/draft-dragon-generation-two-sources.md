---
title: Dragon generation time: the younger schedule gives 427 yr itself, not 460-520, and generation_yr = 200 was never read under the old default
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun-lane-43
blocked_by: []
relates: [PW-959, PW-958]
refs: [planet/lineages/dragon_ages.py, planet/lineages/samples/dnd.toml, planet/lineages/samples/seven_meals.toml]
---

## Description
Fun lane 43 (PW-959). Two findings: (1) dragon_ages.structure("younger") gives a generation time of 427 yr (flat fecundity; 1152 with fecundity ~ mass), not the 460-520 the ticket quoted, so meta.dragon_generation = "schedule" and the owner's 430 differ by 3 yr under the default schedule; (2) the dnd.toml / seven_meals.toml generation_yr = 200 was never read: the default dragon_generation was already "schedule" (433 yr at base). The tomls now say generation_yr = 430 with dragon_generation = "line" (as the owner ruled), so a dragon line has its own number again. Decide whether to go back to "schedule" as the default (one source of truth, and the number follows the age schedule, 427 now) or keep "line" 430 until the owner wants fecundity ~ mass (~1,150 under younger).
