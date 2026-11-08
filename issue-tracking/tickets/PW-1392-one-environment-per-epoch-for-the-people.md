---
id: PW-1392
title: "One environment per epoch for the peoples: an epoch-environment provider (NPP rescaled by each epoch's climate)"
type: story
status: todo
parent: null
milestone: later
subsystem: peoples
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-1077, PW-902]
refs: ["docs/review/fresh-eyes/2026-11-03.md#2-recommendations-ranked", "planet/lineages/history/habitat.py::_land_view", planet/lineages/ladder.py, planet/lineages/prey.py, planet/lineages/history/params.py]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: the peoples read the climate in more than one way. Habitats read each epoch's own climate (history/habitat.py::_land_view), but the density ladder reads the finished world's plant growth for every epoch, ice-age ones included (ladder.py:126-127, per the review), and the herds read the world's grazing growth (prey.py:3). PW-1077 measured 843 cells where the world has more than 600 mm of rain and the epoch has under 200 mm. So a glacial desert can carry an interglacial crowd.

Proposal (fresh-eyes R2): one epoch-environment provider that every peoples module asks for an epoch's climate and plant growth (even just the world's growth rescaled by the epoch's climate to start). Fold PW-1077 into it; link PW-902 (ranges follow the ice-age climate).
- [ ] one provider, used by habitat, ladder and prey
- [ ] a check that epoch rain and growth agree with the epoch's climate (PW-1077's 843 cells go to ~0)
Not decided here: how to rescale (judgement; measure against the time-zoom frames first).

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: peoples tuning or owner call that no milestone theme needs
- 2026-11-03: Created.
