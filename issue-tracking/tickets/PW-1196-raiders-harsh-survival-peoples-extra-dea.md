---
id: PW-1196
title: "Raiders: harsh-survival peoples' extra deaths rise on hostile frontiers, plus culling wars that cut a crowded raider border to 40% and let it bounce back"
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: lane-85
blocked_by: [PW-1165]
relates: [PW-1169, PW-1172, PW-1149, PW-1165]
refs: [docs/review/peoples-events/design.md, planet/lineages/life_history.py, planet/lineages/samples/dnd.toml]
created: 2026-10-31
updated: 2026-10-31
---

## Description
**In plain words.** The owner's view: kobolds and goblins breed fast *because* they die constantly, and "we're just not killing off
enough aggressive little monsters". They also want local culling wars ("way too many goblins, hunt 'em down") that thin them, after
which they bounce back. The life tables agree, if the deaths are the right ones. A flat extra death rate kills elves first: +1%/yr
leaves kobolds 92% and elves extinct. But kobolds' and goblins' high fecundity is already paid for by their "harsh" losses. So make
those losses depend on where they live:
- more on a border with peoples who hate them;
- fewer deep in their own country;
- fewer still in walled towns.

Slow peoples have no such losses and are untouched. Design: docs/review/peoples-events/design.md, section 2.

- **Raid factor.** The harsh excess (harsh schedule minus normal) × R, with R = R_SAFE + (R_FRONT − R_SAFE) × F × (1 − town). F is
  lane 82's hostile-frontier share. R_SAFE 0.7 and R_FRONT 2.0 are judgements to screen. Fecundity stays closed at R = 1. Computed on
  `life_history.table`: kobold kept 0.65 at R = 1.5 and 0.31 at R = 2; goblin 0.70 and 0.41. It enters as `kept` on K (PW-1165).
- **Culls.** A raiding people's frontier component becomes a cull site when it is crowded (p ≥ 0.8 K), borders enemies (F ≥ 0.3) and
  is outnumbered there. With chance 0.5 a step, d = 0.6, recovering as lane 82's `d ← d exp(−dt / (RECOVER_YR / x))`, and it can be
  struck again once d < 0.1.
  - The time-average is 0.28 for any growth rate (r-neutral sawtooth; arithmetic in the design).
  - Faster than a century step, the step applies the mean and logs one cull.
- **Spec.** `raids` (bool, default true where `survival = "harsh"`). The meta keys are `cull_early` / `cull_late` (0, 0.5, 1, 2).
- **Pushback, recorded.** Where kobolds hold a range alone, nobody raids or culls them, so their density (D20) stays the lever there.

- [ ] raid factor in the kept channel; a test that normal-survival lines are unchanged and kobold kept is 0.65 / 0.31 at R 1.5 / 2
- [ ] cull sawtooth; a test that its mean is 0.28 whatever x is
- [ ] events logged ("the hill folk hunted the goblins of X back to their warrens")
- [ ] lane 77 suite, arms off / default / ×2: kobold and goblin median share falls; elf, dwarf and gnome medians not below off

## Updates
- 2026-10-31: Created from inbox draft draft-raiders-raid-losses-and-culling-wars.md (found by lane-85).
