---
id: PW-1070
title: "Food budget order: the dragons' share the pressure leaves uneaten goes to nobody, and the smaller predators are never pressed by peoples (they keep ~50% of the supply in farmers' country)"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: dragon-density-r2
blocked_by: []
relates: [PW-977]
refs: [planet/lineages/history/megafauna.py, docs/review/megafauna/dragon-density/index.html]
created: 2026-10-30
updated: 2026-10-30
---

## Description
**In plain words.** The model serves the peoples and giants first by how many of them there are, then gives the other hunters and the
dragons fixed shares of what is left, as if they were always at full strength. Where peoples hold the dragons down, the dragons' unused
share simply vanishes: the wolves and big cats do not take it and the herds do not grow. And those smaller hunters are never driven off
by the peoples at all. Neither changes the dragon numbers, but both make the food budget less like a real one.

Evidence: megafauna.budget (stage 2) takes peoples (density x need) and giants first, then the guild's fixed share guild_ratio/(1+guild_ratio)
of the rest, then the dragons' share; local_density then presses the dragons below it. Round-2 sweep: in farmers' country the dragons'
share is mostly uneaten (Figure 2's hatching) while the smaller predators keep their full share. STOCK_TOLERABLE is documented as the stock
herders tolerate losing "to dragons", but 83% of it goes to the smaller predators.

Direction and size on dragons: none directly. A mesopredator release would cut the herds in peopled country (fewer prey for dragons there).
- [ ] decide whether the smaller predators are pressed too, and where the uneaten share goes

## Updates
- 2026-10-30: Created from inbox draft draft-food-budget-uneaten-share-and-unpressed-small-predators.md (found by dragon-density-r2).
