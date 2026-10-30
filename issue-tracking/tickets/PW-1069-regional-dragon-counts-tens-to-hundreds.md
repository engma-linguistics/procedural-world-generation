---
id: PW-1069
title: Regional dragon counts (tens to hundreds in a Sword Coast-sized peopled region) are far below the thousands a viable population needs
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: dragon-density-r2
blocked_by: []
relates: [PW-936, PW-977]
refs: [planet/lineages/history/megafauna.py, docs/review/megafauna/dragon-density/index.html]
created: 2026-10-30
updated: 2026-10-30
---

## Description
**In plain words.** A region the size of the Sword Coast holds only tens to hundreds of dragons of all kinds where peoples live, and one
kind only a fraction of that. Biologists put the smallest population that lasts at thousands. The model keeps such pockets alive by
treating pockets of a kind within 7,500 km as one population; nobody has checked whether that test is strict enough at these numbers.

Evidence (review round 2, sections 7, 9.2 item 7):
- Marshall et al. 2021: "the loose consensus that at least thousands of individuals are needed for long-term persistence" (p. 285);
- Burness et al. 2001: "frequent estimates are a few thousand to at least 10,000 individuals" (p. 14521);
- the model: `metapop_km` = SCATTER_LINKS x LINK_KM = 7,500 km; viable number lowered for long-lived kinds (History.line_mvp).
Direction: fewer dragons, locally none, if the test is tightened; or explicitly a planet-wide metapopulation.
- [ ] count each kind's linked population per run against its viable number
- [ ] decide whether a regional pocket should need a regional viable number

## Updates
- 2026-10-30: Created from inbox draft draft-dragon-viability-at-regional-counts.md (found by dragon-density-r2).
