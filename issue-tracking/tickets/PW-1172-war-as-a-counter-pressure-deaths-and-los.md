---
id: PW-1172
title: "War as a counter-pressure: deaths and lost land where peoples are crowded, stateless or ringed by enemies, with a per-era dial"
type: task
status: done
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
updated: 2026-11-09
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
- 2026-11-09: Status todo -> done. Merged lane 259 (d6d0124e..73798d7f): level with main at default; two design bars not met (slow breeders, commonest) -> PW-1617.
- 2026-11-09: Lane 259b stress suite (4360a3, seeds 7/10/13, base+subset, 12 runs an arm, off/default/x2 and main 0289ade6): slow breeders NOT met (dnd 20.2% off, 19.1% default, 15.6% x2; seven_meals 10.8, 8.3, 7.1; default level with main_def 19.2 / 9.2, so the fall is mostly lane 97/101); commonest share does NOT fall (dnd median 28/28/30%) but D31 limits hold in all arms (max 43%, 5+ peoples all <=70%); no new brittle peoples vs main_def (goliath borderline on a 0.02% share, also brittle with war off); troubles 38-105 a run at default, 0 refugee events in all 36 war runs (draft-refugees-never-fire). Table in design.md as-built note. Recommend merge.
- 2026-11-09: Lane 259 (commits d6d0124e, 1e88e213): built meta.war_early/war_late (x meta.war, war-torn land), per-line war_x, aggressive x2, times of troubles sized from Turchin 2009 Table 1 (TROUBLE_SHARE 0.41, TROUBLE_KYR 0.107, x3), refugees on jumps (REFUGEE_Q 1), viewer controls. War deaths not built (D31). Stress suite (base+subset, 4360a3, war 0/1/2 and main) was running at hand-off: scratchpad l259/{br_def,main_def,br_off,br_x2}.
- 2026-11-03: Milestones 11-03: later -> v4: v4 must-have: war's land effect inside the history (polities v1)
- 2026-11-03: Triage 11-03: v2 -> later: war, plague, events and life-history belong with the v3 civilization epic (PW-661); not needed for a first culinary brief
- 2026-10-31: Lane 101 built the war deaths through the life tables (excess violent deaths over the life table, lane 82 stage weights) and measured them on the stress suite: 0-0.2% of any people, no change to the commonest share. Dropped on Daniel's D31 ruling; parked with the commonest-share question for the war and polities work (inbox draft draft-in-fighting-judgements-for-polities.md).
- 2026-10-30: Created from inbox draft draft-war-counterpressure.md (found by lane-82).
