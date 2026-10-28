---
id: PW-975
title: Prey field slope and intercept from McNaughton et al. 1989 / Coe et al. 1976 once the papers are on file
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-41
blocked_by: []
relates: [PW-966, PW-962, PW-957, PW-833]
refs: [planet/lineages/prey.py, docs/references/megafauna/README.md]
created: 2026-10-28
updated: 2026-10-28
---

## Description
PW-966 asked for wild herbivore biomass from absolute NPP "through a published fit (McNaughton et al. 1989; Coe, Cumming &
Phillipson 1976), verify the papers first". Both citations check out on Crossref (doi:10.1038/341142a0, doi:10.1007/BF00345312),
but neither paper is on file, and the agent could not read their regression coefficients (paywalled; a university-hosted copy
of McNaughton 1989 was bot-blocked). So prey.py does not use any published coefficient: wild herbivores are taken as
**proportional** to the grazing NPP (PREY_EXP = 1) through one anchor from PW-966's own table, ~10 t/km2 on rich savanna at
~470 g C/m2/yr (the model's savanna median on world 2a7385). The biome medians then give temperate forest ~0.3, boreal ~0.6,
tundra ~1.3, temperate grassland ~5.7 and savanna ~10 t/km2.

McNaughton's work is usually read as herbivore biomass rising faster than NPP (a slope above 1 on log-log). If so, the poor
lands would hold fewer dragons under meta.megafauna_natural = "prey" than now, and the rich ones about as many. The case that
shows it: the model's hot deserts have a median grazing NPP of ~90 g C/m2/yr (2a7385: mostly herb cover), so prey.py gives them
~1.9 t/km2, far above the ticket's ~0.1 t/km2 desert example; a steeper slope (or the open-month and drought weighting in
gameattrs) would bring that down.

- [ ] owner fetches McNaughton 1989 and Coe 1976 into docs/references/megafauna/ (added to the README's fetch list, PW-962)
- [ ] read the biomass regression (units: kJ/m2 in McNaughton; check the dry-matter and carbon conversions) and set
      PREY_EXP / PREY_T_REF from it, citing the table or figure
- [ ] re-run the PW-967 review page (docs/review/megafauna/age_of_dragons.py) so the owner sees the change

## Updates
- 2026-10-28: Created from inbox draft draft-prey-fit-from-papers.md (found by fun-lane-41).
