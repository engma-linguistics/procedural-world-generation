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

dnd.toml and seven_meals.toml give every dragon line generation_yr = 200. The base age structure (draft-megafauna-2) gives a different figure:
- **~430 yr**, the mean age of mothers with breeding from age 100, flat fecundity and 0.25%/yr adult mortality;
- **~700 yr**, if fecundity rises with body mass, as in big reptiles where larger females lay more.

Generation time feeds History.line_mvp and the persistence-horizon founder rule (Lande 1993, PW-888). A longer generation means fewer generations elapse over a span, so small dragon populations persist more easily. Check the effect on dragon persistence and on PW-936 coverage before merging, and keep PW-937 (scale every people's viable number by generation time) consistent.

- [ ] generation_yr ~430 for dragon lines, derived from the stage schedule if that is cheap
- [ ] dragon persistence and coverage compared before and after on the usual worlds

## Updates
- 2026-10-28: Created from inbox draft draft-megafauna-3-dragon-generation-time.md (found by daniel).
