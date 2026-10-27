---
id: PW-917
title: Life-history stats per people (lifespan, maturity, offspring) with counter-pressures on fast breeders
type: story
status: todo
parent: null
milestone: v2
subsystem: highlights
effort: l
impact: high
found_by: owner
blocked_by: []
relates: [PW-888, PW-904, PW-916]
refs: []
created: 2026-10-26
updated: 2026-10-26
---

## Description
Owner 2026-10-26. Peoples have only density, explore, sea_share, insularity and speed_kmyr (spec.DEMOGRAPHY). They have no lifespan, age at maturity or offspring rate. Add these per people, with defaults from traits and settable in the tree. Derive generation time and the intrinsic growth rate r from them, and use those for:
- how fast a frontier fills;
- how fast a people recovers from a bottleneck;
- the persistence-horizon founder MVP, if PW-888 needs it;
- how populations jump after the farming onset, when contact turns to displacement and mixing.

Fast breeders (goblins) must not simply take over. Pair r with counter-pressures that scale with density:
- carrying capacity per way of life;
- crowding disease and plague (plague is on every world);
- higher juvenile mortality, an r/K trade-off;
- predation, raiding and conflict with neighbours.

Long-lived, slow peoples (elves) should hold ground through low turnover and insularity, not through numbers.

Deep-time sanity check, to add to the peoples acceptance tests:
- Deep-time numbers must stay plausible against each other. No hundred million dragonborn unless humans were in the same range.
- Elves reaching a region long before humans is fine.
- Deep time, before ~20 kyr ago, only has to find reasonable places for each species.

## Updates
- 2026-10-26: Created from inbox draft draft-life-history-stats.md (found by owner).
