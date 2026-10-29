---
id: PW-959
title: Dragon generation time is 200 yr; the approved age structure gives ~430 yr (more if fecundity grows with size)
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-937, PW-924]
refs: [planet/lineages/samples/dnd.toml, planet/lineages/samples/seven_meals.toml, docs/proposals/megafauna-scaling.md]
created: 2026-10-28
updated: 2026-10-28
---

## Description
Owner 2026-10-28: revisit the dragon generation time.

dnd.toml and seven_meals.toml give every dragon line generation_yr = 200. The base age structure (PW-958) gives a different figure:
- **~430 yr**, the mean age of mothers with breeding from age 100, flat fecundity and 0.25%/yr adult mortality;
- **~700 yr**, if fecundity rises with body mass, as in big reptiles where larger females lay more.

Generation time feeds History.line_mvp and the persistence-horizon founder rule (Lande 1993, PW-888). A longer generation means fewer generations elapse over a span, so small dragon populations persist more easily. Check the effect on dragon persistence and on PW-936 coverage before merging, and keep PW-937 (scale every people's viable number by generation time) consistent.

- [ ] generation_yr ~430 for dragon lines, derived from the stage schedule if that is cheap
- [ ] dragon persistence and coverage compared before and after on the usual worlds

## Updates
- 2026-10-29: fun-lane-43: dnd.toml and seven_meals.toml dragon lines now generation_yr = 430 with meta.dragon_generation = "line". Findings: the 200 was never read (the default was already "schedule", 433 yr at base), and the younger schedule's own figure is 427, not 460-520. Effect on 12 runs (6 worlds x 7000-7001, younger schedule, generation 427 -> 430): 11 of 12 identical; 1df1c3/7001 differs by chance (dragons 9659 -> 8521, coverage 10/14 both). No wobble. Draft filed on keeping line vs schedule.
- 2026-10-28: Owner 10-28: ~430 yr is the default for now (even under the younger schedule, whose own figure is ~460-520); flag if it wobbles or makes the numbers fall out badly.
- 2026-10-28: 10-28: under PW-958's proposed younger pyramid the generation time is ~460-520 yr (base case ~430).
- 2026-10-28: Created from inbox draft draft-megafauna-3-dragon-generation-time.md (found by daniel).
