---
id: PW-1147
title: Let each people's growth rate set its spread speed, recovery and displacement
type: task
status: done
parent: PW-917
milestone: v2
subsystem: highlights
effort: m
impact: med
found_by: lane76
blocked_by: []
relates: [PW-917, PW-887, PW-920]
refs: [docs/review/peoples-demography/report.md, planet/lineages/history/dispersal.py, planet/lineages/history/competition.py, planet/lineages/history/pressure.py, planet/lineages/history/params.py]
created: 2026-10-30
updated: 2026-10-30
---

## In plain words
Fast-breeding peoples (kobolds, goblins, orcs) should spread a little faster, win back lost ground sooner and set out to new
land more often. Slow-breeding ones (elves, dwarves, gnomes) should do all of that more slowly. Today every people spreads,
recovers and gives way at the same rates, whatever its births and deaths. This mostly changes contests and recoveries, not the
final numbers, and it will make elves and dwarves somewhat rarer, not commoner.

## Description
Today there is no growth equation: a reached cell takes its room at once. `speed_kmyr` (default 0.5), `TAU_KYR` (1 kyr),
`MVP_TAU_KYR`, `JUMP_RATE` and lane 73's `SURGE_KYR` are the same for every people. With r_max from the life-history draft
(ratio x = r / r_human):
- spread: `speed_kmyr` × √x. The Fisher-KPP front speed is U = 2√(νγ), independent of carrying capacity (Baggaley et al. 2012,
  arXiv:1203.4471, eqs. 1–2): elves ×0.38, dwarves ×0.5, kobolds and goblins ×1.3–1.7;
- displacement: the TAU_KYR e-folding scaled by the r of the people taking the land (a winner grows into the room at its own rate);
- recovery from a refuge, and the small-patch fade `MVP_TAU_KYR`, by r;
- `JUMP_RATE` × x (founders of far colonies are surplus emigrants);
- `SURGE_KYR`: keep it in years (counting it in generations would give elves a ~28 kyr edge).

Steady losses (raids, predation, plague: N* = K(1 − h/r)) are PW-917's counter-pressures and stay out of this task.
- [ ] each rate above, behind one switch, measured on a few rolls (share of people and cells led per people, before and after)
- [ ] scorecard and lineages tests pass; golden updated on purpose

## Updates
- 2026-10-30: Status todo -> done. Merged lane 78/78b (e30f6092): life stages by way of life, growth-rate displacement (meta.growth_rates), share bands, portals in force + wandering. Follow-ups PW-1185-1191.
- 2026-10-30: Created from inbox draft draft-growth-rate-drives-spread-and-recovery.md (found by lane76).
