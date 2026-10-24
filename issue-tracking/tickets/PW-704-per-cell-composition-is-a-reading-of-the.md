---
id: PW-704
title: Per-cell composition is a reading of the presence; should cohabitation also feed the competition (wish score, empty land)?
type: task
status: todo
parent: PW-689
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-composition
blocked_by: []
relates: [PW-689, PW-663, PW-682]
refs: [planet/lineages/compose.py, planet/lineages/history.py, docs/proposals/lineages.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
PW-689 as built does not change the dynamics: the composition (lead / second / other share per cell) is computed per frame from the presence (`Pw`), a short reach over land past each people's range (settlers, trade, neighbours; up to 10 cells x the late-mixing ramp, decaying 0.85/cell, slowed in closed country, only where the land suits the people) and a cohabitation matrix (each people's openness, wishes near/apart). So the wish score, the empty land and the ranges are unchanged (1df1c3 0.802, 3e9e7d 0.776 with horses on, same seeds as 1b969d / b53bf6).

Options:
- A (built): composition as a reading. Peoples that the competition keeps apart show as pockets only through the reach; nothing is pushed or pulled by it.
- B: let the cohabitation matrix also soften the competition late (the pair's `alpha` times (1 - MIX_DROP x mix x cohab)), so tolerant pairs actually hold the same cell at full presence. This would move ranges, the wish score and the empty land of every try, so it needs the usual multi-draw comparison (several re-rolled draws, not one pair of runs).
- C: leave it at A until the zooms place the pockets (the composition then sets how many settlements of each people a zoom draws).

Lean: A now, C next; B only if the owner finds the globe's mixing too weak after the zooms use it.

## Updates
- 2026-10-23: Status needs-decision -> todo. Coordinator's call: keep composition a reading for now; feeding it into competition belongs with PW-663/PW-661's coexist-or-press-away pass and needs re-rolled draws.
- 2026-10-23: Created from inbox draft draft-composition-feeds-competition.md (found by fun-composition).
