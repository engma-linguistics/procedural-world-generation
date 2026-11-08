---
id: PW-1172
title: "War as a counter-pressure: deaths and lost land where peoples are crowded, stateless or ringed by enemies, with a per-era dial"
type: task
status: todo
parent: PW-917
milestone: v4
subsystem: peoples
effort: l
impact: high
found_by: lane-82
blocked_by: []
relates: [PW-917, PW-1108, PW-661, PW-1068]
refs: [docs/review/peoples-counterpressures/design.md, planet/lineages/history/competition.py, planet/lineages/compose.py]
created: 2026-10-30
updated: 2026-11-03
---

## Description
**In plain words.** Peoples fight more where their land is crowded and no state keeps the peace, and where they border peoples they
hate. Foragers fight least, tribal farmers and herders most; states are calmer. War kills some people, mostly young men, which hardly
slows a people's growth. Above all it empties land: fields go unworked and people pull back to strongholds. That second effect is what
holds down a dense people, kobolds included.

There are two dials in the viewer, "how warlike the peoples are" in the early and late eras, like the dragon-pressure pair. No share is
forced: a people loses only where it is crowded or hemmed in.

Design: docs/review/peoples-counterpressures/design.md, section (b). Depends on the counter-pressure plug draft
(draft-counterpressure-plug).

**The hazard.** `h_war = H_way x A x E(lev) x [(N / N0)^2 x G + X x F]`:
- H_way per way of life (forager 0.07, horticulturalist 0.5, pastoral 0.8, farmer 0.12 %/yr: medians of OWID's compilation of Keeley,
  Gat, Bowles and others; which rows count is a judgement);
- A: the `aggressive` trait x2, or a per-line `war_x`;
- E: `meta.war_early` / `war_late`, blended by tech level (lane 63's `tech_level`);
- G: state pacification, 1 / (1 + 3 lev x town share) (Gómez et al. 2016; Turchin 2009's -alpha S);
- F: the hostile frontier share;
- X: external weight, 0.5.

**Turning the hazard into a cut.**
- **Deaths.** Only the excess over the life table's own reference counts. It falls on the stages with weights (0.1, 0.3, 1, 0.3) and
  male deaths at 0.25 (judgements).
- **Land.** `K x (1 - 0.3 x min(1, h_war / 1%))`, Turchin's K(W) (judgement 0.3).
- **Troubles.** Seeded "times of troubles" pulses stand in for Turchin's ~200-year cycles, which the century step cannot resolve.

Settlements (PW-1108) read the war intensity for sacking and walls. PW-661 builds polities on top.

- [ ] h_war and the two kept factors in CounterMixin
- [ ] meta.war_early / war_late / war_external, per-line war_x, viewer controls
- [ ] lane 77 arms off / default / x2: slow breeders not lower than off; commonest people's share falls; no new brittle peoples

## Updates
- 2026-11-03: Milestones 11-03: later -> v4: v4 must-have: war's land effect inside the history (polities v1)
- 2026-11-03: Triage 11-03: v2 -> later: war, plague, events and life-history belong with the v3 civilization epic (PW-661); not needed for a first culinary brief
- 2026-10-31: Lane 101 built the war deaths through the life tables (excess violent deaths over the life table, lane 82 stage weights) and measured them on the stress suite: 0-0.2% of any people, no change to the commonest share. Dropped on Daniel's D31 ruling; parked with the commonest-share question for the war and polities work (inbox draft draft-in-fighting-judgements-for-polities.md).
- 2026-10-30: Created from inbox draft draft-war-counterpressure.md (found by lane-82).
